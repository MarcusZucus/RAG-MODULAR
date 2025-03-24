"""
embedding_model.py – Interfaz para Modelos de Embeddings en el sistema RAG.

Versión avanzada y lista para producción.

Esta interfaz define un contrato para componentes que convierten textos en vectores.
Se asume que el adaptador hereda de BaseComponent, a fin de garantizar su ciclo de vida
y exponer metadatos (versión, etc.).
"""

from abc import abstractmethod
from typing import List, Any
from core.interfaces.base import BaseComponent

class EmbeddingModel(BaseComponent):
    """
    Clase abstracta para adaptadores que generan embeddings a partir de textos.
    """

    @abstractmethod
    def embed(self, texts: List[str], *args, **kwargs) -> List[Any]:
        """
        Convierte una lista de textos en una lista de vectores (list[list[float]] o similar).
        Puede incluir parámetros de configuración (modelo, batch_size, etc.) en args/kwargs.
        """
        pass
