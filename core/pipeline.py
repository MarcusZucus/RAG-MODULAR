import logging
import os
import json
import glob
from typing import List, Dict, Any

from core.config import get_config
from core.loader import load_all_adapters
from core.service_detector import check_service_availability
from utils.cache_manager import get_cache, set_cache
# Se asume que utils/logger.py expone un logger configurado
from utils.logger import logger

class RAGPipeline:
    """
    Clase que implementa el pipeline principal del sistema RAG.

    Este pipeline:
      - Carga y preprocesa documentos (asegurando que cada uno tenga 'id', 'texto' y 'metadata').
      - Calcula embeddings de manera optimizada con caching.
      - Indexa documentos en el vector store configurado.
      - Realiza búsquedas vectoriales y utiliza un LLM para generar respuestas.
      - Integra el módulo pre-RAG (los “vagones”) para consolidar la información del proyecto,
        permitiendo que el usuario pueda trabajar con el RAG por defecto de Synapcode o uno personalizado.
      - Verifica la disponibilidad de servicios externos y de recursos locales (incluyendo modelos gguf locales)
        antes de realizar operaciones críticas.
    """

    def __init__(self):
        self.config = get_config()
        self.adapters = load_all_adapters()  # Diccionario con adaptadores por categorías.
        self.logger = logger  # Se utiliza el logger centralizado.
        self.pre_rag_json = None  # Aquí se guardará el JSON consolidado del pre-RAG.

    def preprocess(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normaliza y valida los documentos.
        Se asegura de que cada documento contenga las claves 'id', 'texto' y 'metadata'.
        """
        preprocessed = []
        for doc in documents:
            try:
                if not all(k in doc for k in ("id", "texto", "metadata")):
                    raise ValueError(f"Documento incompleto: {doc}")
                # Normalización: quitar espacios en blanco
                doc["texto"] = doc["texto"].strip()
                preprocessed.append(doc)
            except Exception as e:
                self.logger.error(f"Error preprocesando documento {doc.get('id', 'N/A')}: {e}")
        return preprocessed

    def load_data(self) -> List[Dict[str, Any]]:
        """
        Invoca al adaptador de inputs configurado para cargar documentos.
        Se espera que el adaptador (por ejemplo, json_loader) implemente un método load().
        """
        input_adapter_name = self.config.input  # Ej.: "json_loader"
        category = "Inputs"
        try:
            adapter_module = self.adapters.get(category, {}).get(input_adapter_name)
            if not adapter_module or not hasattr(adapter_module, "load"):
                raise RuntimeError(f"Adaptador de inputs '{input_adapter_name}' no encontrado o sin método load()")
            documents = adapter_module.load()
            return self.preprocess(documents)
        except Exception as e:
            self.logger.error(f"Error en load_data: {e}")
            raise

    def compute_embeddings(self, texts: List[str]) -> List[Any]:
        """
        Calcula los embeddings para una lista de textos usando el adaptador de embeddings configurado.
        Se implementa caching para evitar reprocesamientos innecesarios.
        """
        embedder_name = self.config.embedder  # Ej.: "openai_embedder"
        category = "Embeddings"
        try:
            adapter_module = self.adapters.get(category, {}).get(embedder_name)
            if not adapter_module or not hasattr(adapter_module, "embed"):
                raise RuntimeError(f"Adaptador de embeddings '{embedder_name}' no encontrado o sin método embed()")
            cache_key = f"embeddings:{hash(tuple(texts))}"
            cached = get_cache(cache_key)
            if cached:
                self.logger.info("Embeddings recuperados de cache.")
                return cached
            embeddings = adapter_module.embed(texts)
            set_cache(cache_key, embeddings)
            return embeddings
        except Exception as e:
            self.logger.error(f"Error en compute_embeddings: {e}")
            raise

    def store_vectors(self, documents: List[Dict[str, Any]], embeddings: List[Any]) -> None:
        """
        Inserta cada documento junto a su vector en el adaptador de vector store configurado.
        """
        vs_name = self.config.vector_store  # Ej.: "faiss_store"
        category = "VectorStores"
        try:
            adapter_module = self.adapters.get(category, {}).get(vs_name)
            if not adapter_module or not hasattr(adapter_module, "add"):
                raise RuntimeError(f"Adaptador de vector store '{vs_name}' no encontrado o sin método add()")
            for doc, emb in zip(documents, embeddings):
                adapter_module.add(doc, emb)
            self.logger.info("Documentos indexados correctamente.")
        except Exception as e:
            self.logger.error(f"Error en store_vectors: {e}")
            raise

    def retrieve_and_generate(self, query: str) -> str:
        """
        Realiza la búsqueda vectorial y genera una respuesta utilizando el LLM configurado.
        Verifica previamente la disponibilidad de los servicios requeridos.
        """
        vs_name = self.config.vector_store
        llm_name = self.config.llm
        category_vs = "VectorStores"
        category_llm = "LLMs"

        try:
            if not check_service_availability(vs_name):
                raise RuntimeError(f"Servicio vector store '{vs_name}' no disponible.")
            if not check_service_availability(llm_name):
                raise RuntimeError(f"Servicio LLM '{llm_name}' no disponible.")

            adapter_vs = self.adapters.get(category_vs, {}).get(vs_name)
            if not adapter_vs or not hasattr(adapter_vs, "search"):
                raise RuntimeError(f"Adaptador de vector store '{vs_name}' no encontrado o sin método search()")
            # Calcular embedding del query
            query_embedding = self.compute_embeddings([query])[0]
            results = adapter_vs.search(query_embedding, self.config.search_k)
            context = " ".join([doc.get("texto", "") for doc in results])
            prompt = f"Contexto: {context}\nConsulta: {query}"

            adapter_llm = self.adapters.get(category_llm, {}).get(llm_name)
            if not adapter_llm or not hasattr(adapter_llm, "generate"):
                raise RuntimeError(f"Adaptador LLM '{llm_name}' no encontrado o sin método generate()")
            response = adapter_llm.generate(prompt)
            return response
        except Exception as e:
            self.logger.error(f"Error en retrieve_and_generate: {e}")
            raise

    def process_pre_rag(self, project_path: str) -> Dict[str, Any]:
        """
        Procesa el pre‑RAG extrayendo información del proyecto mediante los “vagones” que generan JSON.
        Busca en la carpeta 'pre_rag' (dentro del directorio de trabajo) y consolida todos los JSON en uno final.
        """
        pre_rag_dir = os.path.join(os.getcwd(), "pre_rag")
        consolidated = {}
        try:
            if self.config.pre_rag_enabled and os.path.exists(pre_rag_dir):
                json_files = glob.glob(os.path.join(pre_rag_dir, "*.json"))
                for jf in json_files:
                    with open(jf, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Aquí se realiza una fusión simple; esta lógica puede extenderse
                        consolidated.update(data)
                self.pre_rag_json = consolidated
                self.logger.info("Pre-RAG procesado y consolidado.")
            else:
                self.logger.info("Pre-RAG deshabilitado o directorio no encontrado.")
        except Exception as e:
            self.logger.error(f"Error procesando pre-RAG: {e}")
            raise
        return consolidated

    def run(self, query: str, project_path: str = None) -> str:
        """
        Ejecuta el pipeline completo.
        
        Opcionalmente, si se proporciona un project_path y el modo pre-RAG está habilitado,
        se procesa la información del proyecto mediante los módulos pre‑RAG.
        
        Retorna la respuesta generada por el sistema RAG.
        """
        try:
            if project_path:
                self.process_pre_rag(project_path)
            documents = self.load_data()
            if not documents:
                raise RuntimeError("No se cargaron documentos para procesar.")
            texts = [doc.get("texto", "") for doc in documents]
            embeddings = self.compute_embeddings(texts)
            self.store_vectors(documents, embeddings)
            response = self.retrieve_and_generate(query)
            return response
        except Exception as e:
            self.logger.error(f"Error en la ejecución del pipeline: {e}")
            raise

# Ejecución cuando se invoque este script directamente.
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python pipeline.py <consulta> [<project_path>]")
        sys.exit(1)
    query = sys.argv[1]
    project_path = sys.argv[2] if len(sys.argv) > 2 else None
    pipeline = RAGPipeline()
    result = pipeline.run(query, project_path)
    print("Respuesta generada:")
    print(result)
