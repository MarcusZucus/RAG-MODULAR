"""
llm_model.py – Interfaz Extrema y Lista para Producción de Modelos LLM en el Sistema RAG.

Requisitos principales:
  - Heredar de BaseComponent (control de ciclo de vida y metadatos).
  - Definir un método abstracto generate() para generar respuestas (con o sin streaming).
  - Integrarse con service_detector para chequear disponibilidad de la LLM (p.ej., "openai_generator", "local_llm_generator").
  - Soportar opciones avanzadas: reintentos, streaming, corte de tokens, etc.

Esta versión "hiper-extrema" contiene:
  - Hooks opcionales para post_generate() en caso de necesitar modificar la respuesta.
  - Manejo de estados para evitar que generate() se invoque antes de validate().
  - Estructura ideal para subclases que implementen la lógica de LLM (OpenAI, Local, etc.).

Consultar 'llm_model_README.md' para más detalles de diseño.
"""

from abc import abstractmethod
from typing import Any, Dict, Optional, Generator
from core.interfaces.base import BaseComponent, ComponentState
import logging

logger = logging.getLogger("LLMModelLogger")
logger.setLevel(logging.DEBUG)

class LLMModel(BaseComponent):
    """
    Clase abstracta para generadores de texto (LLMs) en el sistema RAG.

    Cada implementación concreta (ej.: OpenAIGenerator, LocalLLMGenerator) debe:
      - Controlar la conexión o carga de un modelo de lenguaje (servicio local o externo).
      - Proveer un método generate() para producir la respuesta.
      - Opcionalmente, soportar streaming de tokens (generator) y reintentos automáticos.
      - Validarse frente a service_detector antes de usarse en producción.
    """

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Genera una respuesta a partir de un prompt, retornándola como string.
        
        Args:
            prompt (str): El contenido de la consulta o pregunta.
            **kwargs: Argumentos adicionales para controlar la generación 
                      (por ejemplo, max_tokens, temperature, streaming, etc.).

        Returns:
            str: Respuesta generada por el modelo.
        
        Raises:
            RuntimeError: Si el servicio no está disponible o si ocurre un error crítico.
            ValueError: Si el prompt es inválido.
        """
        pass

    def generate_stream(self, prompt: str, **kwargs) -> Optional[Generator[str, None, None]]:
        """
        Modo alternativo (opcional) para subclases que quieran producir la respuesta en forma de streaming de tokens.
        
        Args:
            prompt (str): El contenido de la consulta.
            **kwargs: Parámetros para la generación (por ejemplo, max_tokens).

        Returns:
            Generator[str, None, None] | None: Un generador que produce fragmentos 
                                               de texto (tokens o subcadenas), 
                                               o None si la subclase no soporta streaming.

        Raises:
            RuntimeError, ValueError: Igual que en generate() si algo falla.
        """
        logger.debug(f"[{self.__class__.__name__}] generate_stream() invocado, subclase puede sobrescribirlo.")
        return None

    def post_generate(self, response: str) -> str:
        """
        Hook opcional para subclases que quieran procesar el texto devuelto por generate(),
        por ejemplo para filtrar o normalizar la salida. Por defecto, retorna el mismo texto.
        
        Args:
            response (str): Respuesta generada.

        Returns:
            str: Respuesta final tras post-procesamiento.
        """
        return response

    # =====================
    # CICLO DE VIDA
    # =====================
    def _do_initialize(self) -> None:
        """
        Implementación interna requerida por BaseComponent.
        La subclase concreta debe sobrescribir si necesita cargar el modelo, abrir conexiones, etc.
        """
        logger.debug(f"[{self.__class__.__name__}] _do_initialize() base abstracto.")

    def _do_validate(self) -> None:
        """
        Verifica la disponibilidad del modelo, la validez de credenciales, etc.
        """
        logger.debug(f"[{self.__class__.__name__}] _do_validate() base abstracto.")

    def _do_shutdown(self) -> None:
        """
        Libera recursos (conexiones, handles de archivos, etc.).
        """
        logger.debug(f"[{self.__class__.__name__}] _do_shutdown() base abstracto.")

    # =====================
    # METADATOS
    # =====================
    @property
    def version(self) -> str:
        """
        Retorna la versión de esta interfaz base. 
        Las subclases pueden sobrescribir con la versión real implementada (ej.: "1.0.0").
        """
        return "0.0.1"

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Retorna información adicional si se requiere.
        """
        return {
            "name": self.__class__.__name__,
            "description": "Interfaz base para modelos de lenguaje (LLM) en el sistema RAG.",
            "dependencies": ["core/service_detector", "utils/logger"],
            "compatibility": ">=0.0.1"
        }
