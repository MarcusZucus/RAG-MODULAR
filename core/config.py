from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Config(BaseSettings):
    # Se usa "openai_api_key" como campo real para la clave API.
    openai_api_key: str = Field(..., description="Clave de API para servicios externos, típicamente OpenAI.")
    db_connection: str = Field(..., description="Cadena de conexión a la base de datos.")
    input: str = Field(..., description="Identificador del adaptador de inputs a utilizar.")
    embedder: str = Field(..., description="Identificador del modelo de embeddings a utilizar.")
    vector_store: str = Field(..., description="Tipo de índice vectorial (faiss_store, chroma_store, etc.).")
    llm: str = Field(..., description="Identificador del generador de respuestas a utilizar.")
    search_k: int = Field(5, description="Número de documentos a recuperar en la búsqueda vectorial.")

    # Campos adicionales para la integración con Synapcode.
    synapcode_mode: bool = Field(
        False,
        description="Si es True, el sistema operará en el modo Synapcode por defecto, activando funcionalidades específicas."
    )
    pre_rag_enabled: bool = Field(
        True,
        description="Habilita el módulo pre-RAG que consolida la información del proyecto a través de 'vagones'."
    )

    # Configuración para leer el archivo .env y poblar los campos por su nombre.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # Propiedad para que config.api_key sea accesible, devolviendo el valor de openai_api_key.
    @property
    def api_key(self) -> str:
        return self.openai_api_key

    # Valida que los campos de texto no estén vacíos.
    @field_validator("openai_api_key", "db_connection", "input", "embedder", "vector_store", "llm", check_fields=False)
    def must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v

    # Valida que search_k sea un entero mayor que cero.
    @field_validator("search_k", mode="before")
    def validate_search_k(cls, v):
        try:
            value = int(v)
        except (TypeError, ValueError):
            raise ValueError("search_k debe ser un entero")
        if value <= 0:
            raise ValueError("search_k debe ser mayor que cero")
        return value

    # Valida el campo synapcode_mode, permitiendo también valores string (por ejemplo, "true").
    @field_validator("synapcode_mode", mode="before")
    def validate_synapcode_mode(cls, v):
        if isinstance(v, str):
            lowered = v.lower()
            if lowered in {"true", "1", "yes"}:
                return True
            elif lowered in {"false", "0", "no"}:
                return False
            else:
                raise ValueError("synapcode_mode debe ser convertible a booleano ('true'/'false')")
        return bool(v)

# Patrón Singleton para la configuración global.
_global_config: Config | None = None

def get_config() -> Config:
    """
    Retorna una instancia singleton de Config. Si aún no ha sido creada, se inicializa a partir
    de las variables de entorno (usando el archivo .env).

    Esta configuración centralizada incluye parámetros críticos para el sistema RAG, junto con
    opciones específicas para la integración con Synapcode (por ejemplo, la activación del modo pre-RAG).
    """
    global _global_config
    if _global_config is None:
        try:
            _global_config = Config()
        except Exception as e:
            raise RuntimeError(f"Error al inicializar la configuración: {e}") from e
    return _global_config

def update_config(new_config: dict):
    """
    Actualiza la configuración global con los nuevos valores suministrados en new_config.
    Se recrea la instancia singleton de Config, fusionando la configuración actual con los nuevos valores.

    Nota: Si se proporciona la clave "api_key" en new_config, se remapea a "openai_api_key" para mantener la coherencia.
    Esto permite actualizar dinámicamente la configuración del sistema sin necesidad de reiniciar la aplicación.
    """
    global _global_config
    # Remapea "api_key" a "openai_api_key" si está presente.
    if "api_key" in new_config:
        new_config["openai_api_key"] = new_config.pop("api_key")
    try:
        if _global_config is None:
            _global_config = Config(**new_config)
        else:
            updated = _global_config.model_dump()
            updated.update(new_config)
            _global_config = Config(**updated)
    except Exception as e:
        raise RuntimeError(f"Error al actualizar la configuración: {e}") from e
