"""
chroma_store.py – Adaptador ChromaDB para Búsqueda Vectorial en el Sistema RAG

Implementación “ultra-extendida” con características de:
  - Concurrencia (threading.Lock).
  - Detección de servicio (core/service_detector.py).
  - Configuración flexible (persistencia vs modo en memoria).
  - Manejo de excepciones avanzado y logging detallado.
  - Integración con los metadatos y la estructura del pipeline RAG.

Requisitos:
  1. pip install chromadb
  2. Asegurarse de que core/service_detector.py retorne True para 'chroma_store'.
  3. Validar que se usan los embeddings coherentes (embed_dim coincide con la dimensión usada).
"""

import logging
import os
import threading
from typing import List, Dict, Any, Optional

from core.service_detector import check_service_availability
from utils.logger import logger

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.client import Client
except ImportError:
    logger.error("No se encuentra la librería 'chromadb'. Instálala con: pip install chromadb")
    # Podemos lanzar una excepción para forzar el despliegue a detenerse
    raise RuntimeError("Librería 'chromadb' requerida no instalada.")

class ChromaStore:
    def __init__(
        self,
        collection_name: str = "rag_collection",
        embed_dim: int = 768,
        persist_directory: Optional[str] = None,
        client_settings: Optional[Settings] = None
    ):
        """
        Inicializa un adaptador ChromaDB. Puede trabajar en modo memoria o persistente.

        Args:
            collection_name (str): Nombre de la colección donde se guardarán los documentos.
            embed_dim (int): Dimensión esperada de los vectores de embeddings.
            persist_directory (str, opcional): Carpeta donde ChromaDB persistirá la colección.
                                               Si es None, se usará un modo en memoria efímero.
            client_settings (Settings, opcional): Configuración avanzada para el cliente de Chroma.
        Raises:
            RuntimeError: Si el servicio 'chroma_store' no está disponible según service_detector.
        """
        if not check_service_availability("chroma_store"):
            msg = "Servicio 'chroma_store' no disponible. Revisa service_detector."
            logger.error(msg)
            raise RuntimeError(msg)

        self.collection_name = collection_name
        self.embed_dim = embed_dim
        self.lock = threading.Lock()

        if not client_settings:
            # Definir configuración por defecto
            #   - telemetry desactivado
            #   - persistencia en persist_directory si se proporcionó
            client_settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory or "",
                anonymized_telemetry=False
            )

        try:
            logger.info(f"Iniciando ChromaStore con collection='{collection_name}', "
                        f"persist_dir='{persist_directory or 'mem'}', dim={embed_dim}")
            self.chroma_client = Client(settings=client_settings)
            self.collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Colección RAG principal con embeddings y documentos."}
            )
            logger.info("ChromaStore inicializado correctamente.")
        except Exception as e:
            logger.error(f"Error al inicializar ChromaStore: {e}")
            raise RuntimeError(f"Error al inicializar ChromaStore: {e}") from e

    def add(self, document: Dict[str, Any], vector: List[float]):
        """
        Agrega (o actualiza) un documento y su vector al índice ChromaDB.

        Args:
            document (dict): Diccionario con al menos las claves "id", "texto", "metadata".
            vector (list[float]): Vector de embeddings para este documento.

        Raises:
            ValueError: Si el vector no coincide con la dimensión esperada.
            RuntimeError: Si ocurre un problema al insertar en la colección.
        """
        if len(vector) != self.embed_dim:
            msg = f"La dimensión del vector ({len(vector)}) no coincide con la esperada ({self.embed_dim})."
            logger.error(msg)
            raise ValueError(msg)

        doc_id = document.get("id")
        if not doc_id:
            raise ValueError("El documento carece de 'id'.")

        texto = document.get("texto", "")
        metadata = document.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        with self.lock:
            try:
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[vector],
                    metadatas=[metadata],
                    documents=[texto]
                )
                logger.info(f"Documento '{doc_id}' agregado/actualizado en ChromaDB.")
            except Exception as e:
                logger.error(f"Error al agregar documento '{doc_id}': {e}")
                raise RuntimeError(f"Error al agregar documento '{doc_id}': {e}") from e

    def remove(self, doc_id: str):
        """
        Elimina un documento del índice ChromaDB.

        Args:
            doc_id (str): Identificador del documento a eliminar.
        """
        with self.lock:
            try:
                self.collection.delete(ids=[doc_id])
                logger.info(f"Documento '{doc_id}' eliminado de la colección '{self.collection_name}'.")
            except Exception as e:
                logger.error(f"Error al eliminar documento '{doc_id}': {e}")
                raise RuntimeError(f"Error al eliminar documento '{doc_id}': {e}") from e

    def search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda de los k documentos más cercanos a un vector de consulta.

        Args:
            query_vector (list[float]): Vector de embeddings para la consulta.
            k (int): Número de resultados a retornar.

        Returns:
            list[dict]: Lista de documentos, donde cada elemento incluye 'id', 'texto', 'metadata'
                        y, opcionalmente, un 'distance' o 'similarity' devuelto por ChromaDB.

        Raises:
            ValueError: Si la dimensión del vector de consulta no coincide con la esperada.
            RuntimeError: Si ocurre algún problema en la búsqueda.
        """
        if len(query_vector) != self.embed_dim:
            msg = f"Dimensión inválida para vector de consulta. Esperada={self.embed_dim}, actual={len(query_vector)}"
            logger.error(msg)
            raise ValueError(msg)

        with self.lock:
            try:
                results = self.collection.query(
                    query_embeddings=[query_vector],
                    n_results=k
                )
                # ChromaDB retorna un dict con "ids", "metadatas", "documents", "embeddings" (opcional), etc.
                # Estructura: {"ids": [["doc1", "doc2"]], "metadatas": [[{}, {}]], "documents": [["texto1", "texto2"]]}
                found_docs = []
                if results and "ids" in results and results["ids"]:
                    # results["ids"][0] -> lista de IDs, etc.
                    ids_batch = results["ids"][0]
                    meta_batch = results["metadatas"][0] if results.get("metadatas") else [{} for _ in ids_batch]
                    text_batch = results["documents"][0] if results.get("documents") else ["" for _ in ids_batch]
                    # Chroma 0.3.21 no retorna distancias por defecto, a menos que se activen
                    #   "include=["embeddings", "distances"]" en query(). Si se desea, se podría habilitar.
                    # Ejemplo:
                    # distances = results["distances"][0] if "distances" in results else None

                    for idx, doc_id in enumerate(ids_batch):
                        doc_obj = {
                            "id": doc_id,
                            "texto": text_batch[idx],
                            "metadata": meta_batch[idx]
                        }
                        found_docs.append(doc_obj)

                logger.info(f"Búsqueda con ChromaDB completada. Encontrados {len(found_docs)} documentos.")
                return found_docs

            except Exception as e:
                logger.error(f"Error en la búsqueda ChromaDB: {e}")
                raise RuntimeError(f"Error en la búsqueda ChromaDB: {e}") from e

    def reindex_collection(self):
        """
        Método opcional avanzado que puede recrear la colección, por si la necesitamos “reindexar”.
        ¡Tener cuidado con esta operación destructiva!
        """
        with self.lock:
            try:
                # Podríamos eliminar y recrear la colección, o usar un approach distinto:
                self.chroma_client.delete_collection(name=self.collection_name)
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"reindex": "true"}
                )
                logger.warning(f"Colección '{self.collection_name}' ha sido recreada (reindex).")
            except Exception as e:
                logger.error(f"Error al reindexar la colección '{self.collection_name}': {e}")
                raise RuntimeError(f"Error en reindex_collection: {e}")

    def list_documents(self) -> List[str]:
        """
        Retorna la lista de IDs disponibles en la colección.

        Returns:
            list[str]: Lista de IDs de los documentos indexados.
        """
        with self.lock:
            try:
                # A falta de un método más directo, podemos hacer un query con embeddings vacíos
                # o un "get all" (cada versión de Chroma puede variar).
                result = self.collection.query(query_texts=[""], n_results=9999999)
                if result and result["ids"]:
                    return list(result["ids"][0])
                return []
            except Exception as e:
                logger.error(f"Error al listar documentos de ChromaDB: {e}")
                return []
