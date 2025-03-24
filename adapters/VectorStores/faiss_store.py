"""
faiss_store.py – Adaptador FAISS para Búsqueda Vectorial

Este módulo implementa la indexación y búsqueda de documentos utilizando FAISS.
Utiliza un índice de tipo IndexFlatL2 (para búsqueda por distancia euclidiana) y 
mantiene un mapeo interno entre el ID de cada documento y su posición en el índice.

Características:
- Inicialización dinámica del índice basado en la dimensión de los vectores.
- Inserción de documentos junto con sus embeddings.
- Búsqueda semántica para retornar los k documentos más cercanos a un vector de consulta.
- Manejo de errores, logging y verificación de servicios mediante core/service_detector.py.
- Soporte para operaciones concurrentes mediante locking.
"""

import faiss
import numpy as np
import threading
import logging
from core.service_detector import check_service_availability

logger = logging.getLogger("RAGLogger")
logger.setLevel(logging.DEBUG)

class FaissStore:
    def __init__(self, dim: int):
        """
        Inicializa el adaptador FAISS.
        
        Args:
            dim (int): Dimensión de los vectores.
        
        Raises:
            RuntimeError: Si la disponibilidad del servicio FAISS falla.
        """
        # Verificar disponibilidad del servicio FAISS (se asume local)
        if not check_service_availability("faiss_store"):
            logger.error("Servicio FAISS no disponible.")
            raise RuntimeError("Servicio FAISS no disponible.")
        
        self.dim = dim
        try:
            self.index = faiss.IndexFlatL2(dim)
            logger.info(f"Índice FAISS inicializado con dimensión {dim}.")
        except Exception as e:
            logger.error(f"Error al inicializar el índice FAISS: {e}")
            raise RuntimeError(f"Error al inicializar el índice FAISS: {e}") from e
        
        # Mapeo de posición de índice a documento (almacena el documento completo)
        self.doc_mapping = {}
        self.lock = threading.Lock()
    
    def add(self, document: dict, vector: list):
        """
        Agrega un documento y su vector al índice.
        
        Args:
            document (dict): Documento con al menos la clave "id".
            vector (list): Vector numérico (lista o numpy array) del documento.
        
        Raises:
            ValueError: Si el vector no tiene la dimensión correcta.
        """
        if len(vector) != self.dim:
            logger.error("La dimensión del vector no coincide con la dimensión del índice.")
            raise ValueError("La dimensión del vector no coincide con la dimensión del índice.")
        
        with self.lock:
            # Convertir vector a numpy array float32
            np_vector = np.array(vector, dtype='float32').reshape(1, self.dim)
            try:
                self.index.add(np_vector)
                pos = self.index.ntotal - 1
                self.doc_mapping[pos] = document
                logger.info(f"Documento '{document.get('id')}' agregado en la posición {pos}.")
            except Exception as e:
                logger.error(f"Error al agregar el documento: {e}")
                raise RuntimeError(f"Error al agregar el documento: {e}") from e
    
    def search(self, query_vector: list, k: int):
        """
        Realiza una búsqueda vectorial y retorna los k documentos más cercanos.
        
        Args:
            query_vector (list): Vector de consulta.
            k (int): Número de documentos a recuperar.
        
        Returns:
            list: Lista de documentos ordenados de mayor a menor similitud.
        
        Raises:
            ValueError: Si el vector de consulta no tiene la dimensión correcta.
        """
        if len(query_vector) != self.dim:
            logger.error("La dimensión del vector de consulta no coincide con la dimensión del índice.")
            raise ValueError("La dimensión del vector de consulta no coincide con la dimensión del índice.")
        
        # Convertir vector de consulta a numpy array float32
        np_query = np.array(query_vector, dtype='float32').reshape(1, self.dim)
        try:
            distances, indices = self.index.search(np_query, k)
            results = []
            with self.lock:
                for idx in indices[0]:
                    doc = self.doc_mapping.get(idx)
                    if doc:
                        results.append(doc)
            logger.info(f"Búsqueda completada: {len(results)} documentos recuperados.")
            return results
        except Exception as e:
            logger.error(f"Error en la búsqueda vectorial: {e}")
            raise RuntimeError(f"Error en la búsqueda vectorial: {e}") from e
