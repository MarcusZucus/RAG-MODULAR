"""
input_source.py – Interfaz Avanzada para Cargadores de Datos en el sistema RAG.

Versión extrema, avanzada y lista para producción.

Cumple con:
  - Heredar de BaseComponent para el ciclo de vida (CREATED, INITIALIZED, VALIDATED, SHUTDOWN).
  - Definir un método abstracto load_data(*args, **kwargs) -> List[Dict[str, Any]].
  - Integrar hooks y chequear la disponibilidad de servicios externos si aplica (service_detector).

Revisar 'input_source_README.md' para conocer las pautas de implementación.
"""

from abc import abstractmethod
from typing import List, Dict, Any
from core.interfaces.base import BaseComponent
import logging

logger = logging.getLogger("InputSourceLogger")
logger.setLevel(logging.DEBUG)

class InputSource(BaseComponent):
    """
    Clase abstracta para adaptadores de entrada de datos en el RAG.
    Cada adaptador (por ejemplo, JSONLoader, APILoader, SQLLoader) debe heredar
    de esta clase y proveer la lógica concreta de 'load_data'.

    Hereda de BaseComponent, lo cual significa que:
      - Debe exponer 'version' y 'metadata'.
      - Dispondrá de un ciclo de vida: initialize() -> validate() -> load_data() -> shutdown().
      - load_data() se invoca típicamente tras validate().
    """

    @abstractmethod
    def load_data(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Carga documentos desde la fuente (archivos, APIs, DB, etc.) y retorna una lista
        de dicts con al menos:
          [
            {
              "id": str,       # identificador único
              "texto": str,    # contenido principal
              "metadata": dict # información adicional
            },
            ...
          ]

        Puede lanzar excepciones si la fuente no está disponible o el formato es inválido.
        Es recomendable chequear la disponibilidad del servicio externo
        (por ejemplo, base de datos, endpoint) antes de procesar, usando service_detector.
        """
        pass

    def post_load_data(self, documents: List[Dict[str, Any]]) -> None:
        """
        Hook opcional que se ejecuta luego de 'load_data' exitoso, para transformaciones
        o validaciones adicionales. Por defecto, no hace nada.
        Sobrescribir en subclases si se requiere procesamiento extra.
        """
        logger.debug(f"[{self.__class__.__name__}] post_load_data hook con {len(documents)} documentos.")
        pass
