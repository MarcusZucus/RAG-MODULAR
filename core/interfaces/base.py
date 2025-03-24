"""
base.py – Interfaz Base Abstracta para los componentes principales del sistema RAG.

Versión extrema, avanzada y lista para producción.

Este archivo define la clase abstracta BaseComponent, que sirve como contrato mínimo para
cualquier módulo o adaptador que se integre al sistema RAG. Además, incluye un control
de ciclo de vida (estado interno), logging avanzado y verificación de consistencia.

Características principales:
- Provee un atributo 'state' para gestionar el ciclo de vida del componente (CREATED, INITIALIZED, VALIDATED, SHUTDOWN).
- Define métodos abstractos initialize(), validate(), shutdown() y propiedades version, metadata.
- Permite hooks opcionales post_initialize() y post_validate() para extender la lógica de setup/validación.
- Integra un logger y un control estricto para evitar re-inicializaciones o validaciones múltiples.
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any

# Logger global (puedes reutilizar tu logger "RAGLogger" o un logger local)
logger = logging.getLogger("BaseComponentLogger")
logger.setLevel(logging.DEBUG)

# Estados de ciclo de vida posibles
class ComponentState(Enum):
    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    VALIDATED = "VALIDATED"
    SHUTDOWN = "SHUTDOWN"

class BaseComponent(ABC):
    """
    Clase abstracta base para todos los componentes del sistema RAG.
    Garantiza un ciclo de vida y metadatos básicos. Cualquier componente
    (adaptador, servicio, plugin) debe heredar de esta clase y proveer
    sus métodos concretos.
    """

    def __init__(self):
        """
        Inicializa el estado del componente en CREATED.
        """
        self._state = ComponentState.CREATED
        logger.debug(f"[{self.__class__.__name__}] Componente en estado CREATED.")

    @property
    @abstractmethod
    def version(self) -> str:
        """
        Retorna la versión actual del componente. Útil para control de compatibilidad
        y auditoría de despliegues.
        """
        pass

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """
        Retorna un dict con información adicional sobre el componente, por ejemplo:
          {
            "name": "NombreDelComponente",
            "description": "Breve descripción",
            "dependencies": ["otra_lib", "un_servicio_externo"],
            "compatibility": ">=1.0.0",
            ...
          }
        """
        pass

    @property
    def state(self) -> ComponentState:
        """
        Retorna el estado actual del ciclo de vida del componente.
        """
        return self._state

    def initialize(self) -> None:
        """
        Se invoca al crear o inyectar el componente para preparar recursos
        (conexiones, hilos, buffers, etc.). Cambia el estado a INITIALIZED.
        """
        if self._state != ComponentState.CREATED:
            logger.error(f"No se puede inicializar: estado actual={self._state.value}. Esperado=CREATED.")
            raise RuntimeError(f"Initialize inválido. El componente ya se encuentra en estado {self._state.value}.")

        self._do_initialize()
        self._state = ComponentState.INITIALIZED
        logger.debug(f"[{self.__class__.__name__}] Componente en estado INITIALIZED.")
        # Hook opcional para extender
        self.post_initialize()

    @abstractmethod
    def _do_initialize(self) -> None:
        """
        Implementación interna de la inicialización, obligatoria en cada subclase.
        Por ejemplo, abrir un pool de conexiones, levantar un hilo, etc.
        """
        pass

    def post_initialize(self) -> None:
        """
        Hook opcional que se invoca tras la inicialización exitosa. Se puede
        sobrescribir en subclases si se requiere lógica adicional (no obligatorio).
        """
        pass

    def validate(self) -> None:
        """
        Verifica la coherencia interna del componente, su configuración
        y la disponibilidad de recursos externos. Debe lanzar excepción
        si algo no está correcto. Cambia el estado a VALIDATED si todo está OK.
        """
        if self._state != ComponentState.INITIALIZED:
            logger.error(f"No se puede validar: estado actual={self._state.value}. Esperado=INITIALIZED.")
            raise RuntimeError(f"Validate inválido. El componente debe estar en estado INITIALIZED antes de validar.")

        self._do_validate()
        self._state = ComponentState.VALIDATED
        logger.debug(f"[{self.__class__.__name__}] Componente en estado VALIDATED.")
        # Hook opcional post-validación
        self.post_validate()

    @abstractmethod
    def _do_validate(self) -> None:
        """
        Implementación interna de la validación, obligatoria en cada subclase.
        Se espera verificación de recursos, configuraciones, etc.
        """
        pass

    def post_validate(self) -> None:
        """
        Hook opcional que se invoca tras la validación exitosa.
        Sobrescribir si se necesita lógica adicional.
        """
        pass

    def shutdown(self) -> None:
        """
        Libera recursos (conexiones, hilos, etc.) al terminar. Asume
        que el componente ya no se utilizará tras invocar este método.
        Cambia el estado a SHUTDOWN.
        """
        if self._state not in [ComponentState.VALIDATED, ComponentState.INITIALIZED]:
            logger.error(f"No se puede hacer shutdown: estado actual={self._state.value}.")
            raise RuntimeError(f"Shutdown inválido. El componente está en estado {self._state.value}, esperado VALIDATED o INITIALIZED.")

        self._do_shutdown()
        self._state = ComponentState.SHUTDOWN
        logger.debug(f"[{self.__class__.__name__}] Componente en estado SHUTDOWN.")

    @abstractmethod
    def _do_shutdown(self) -> None:
        """
        Implementación interna del apagado, obligatoria en cada subclase.
        Por ejemplo: cerrar conexiones, matar hilos, eliminar buffers, etc.
        """
        pass
