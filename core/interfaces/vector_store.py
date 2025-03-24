"""
vector_store.py – Interfaz Avanzada para Almacenes Vectoriales en el sistema RAG.

Versión extremadamente avanzada y lista para entornos de producción.

Requisitos principales:
  - Heredar de BaseComponent para el ciclo de vida (CREATED, INITIALIZED, VALIDATED, SHUTDOWN).
  - Definir métodos abstractos para add(), remove(), search() y reindex().
  - Posibilidad de manejar concurrencia interna (locks) si se requiere.
  - Integrarse con service_detector para verificar disponibilidad del servicio vectorial (faiss_store, chroma_store, etc.).
  - Permitir hooks opcionales (post_add, post_remove, etc.) que faciliten la extensión.

Revisar 'vector_store_README.md' para conocer las pautas de implementación real.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional

from core.interfaces.base import BaseComponent, ComponentState
import logging

logger = logging.getLogger("VectorStoreLogger")
logger.setLevel(logging.DEBUG)

class VectorStore(BaseComponent):
    """
    Clase abstracta para adaptadores de almacén vectorial (FAISS, Chroma, etc.)
    en el sistema RAG.

    Cada implementación concreta debe:
      - Manejar un índice vectorial para la búsqueda semántica.
      - Mantener un mapeo (id -> documento) o su equivalente interno.
      - Proveer métodos de inserción, búsqueda, eliminación y/o reindexación de documentos.
      - Respetar el ciclo de vida: initialize() -> validate() -> uso -> shutdown().
    """

    @abstractmethod
    def add(self, document: Dict[str, Any], vector: List[float]) -> None:
        """
        Inserta o actualiza un documento y su vector en el índice.

        Args:
            document (dict): Debe incluir al menos la clave "id", y opcionalmente "texto", "metadata", etc.
            vector (List[float]): Vector de embeddings con la dimensión acordada.

        Raises:
            ValueError: Si la dimensión del vector es incorrecta.
            RuntimeError: Si ocurre un error en la operación interna.
        """
        pass

    @abstractmethod
    def remove(self, doc_id: str) -> None:
        """
        Elimina el documento (y su vector) asociado a la clave doc_id.

        Args:
            doc_id (str): Identificador del documento a eliminar.

        Raises:
            RuntimeError: Si no se encuentra o si ocurre algún problema interno.
        """
        pass

    @abstractmethod
    def search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda de los k documentos más cercanos a un vector de consulta.

        Args:
            query_vector (List[float]): Vector que representa la búsqueda.
            k (int): Número máximo de resultados a retornar.

        Returns:
            List[Dict[str, Any]]: Lista de documentos encontrados, cada uno con sus claves ("id", "texto", "metadata", etc.).
        """
        pass

    @abstractmethod
    def reindex(self) -> None:
        """
        Reconstituye o recrea el índice interno, en caso de que se necesite una reindexación completa.

        Raises:
            RuntimeError: Si ocurre un error en la recreación del índice.
        """
        pass

    # ======================
    # CICLO DE VIDA
    # ======================
    def _do_initialize(self) -> None:
        """
        Se encarga de inicializar recursos internos del vector store (conexiones, estructuras de datos, etc.).
        Debe implementarse en subclases concretas.
        """
        logger.debug(f"[{self.__class__.__name__}] _do_initialize() llamado (abstract).")

    def _do_validate(self) -> None:
        """
        Verifica que la configuración interna del vector store sea válida.
        Por ejemplo, se puede comprobar que la dimensión del embedding o
        la conexión a un servicio externo sea correcta.
        """
        logger.debug(f"[{self.__class__.__name__}] _do_validate() llamado (abstract).")

    def _do_shutdown(self) -> None:
        """
        Cierra recursos (conexiones, memoria compartida, etc.) si es necesario.
        """
        logger.debug(f"[{self.__class__.__name__}] _do_shutdown() llamado (abstract).")

    # ======================
    # METADATOS
    # ======================
    @property
    def version(self) -> str:
        """
        Retorna la versión de esta interfaz.
        En subclases, podría retornarse la versión real del adaptador (p.ej., '1.2.0').
        """
        return "0.0.1"

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Retorna un dict con información adicional, si se requiere.
        """
        return {
            "name": self.__class__.__name__,
            "description": "Interfaz abstracta para vector stores en el sistema RAG.",
            "dependencies": ["possibly_faiss_or_chroma", "core/service_detector"],
            "compatibility": ">=0.0.1"
        }
