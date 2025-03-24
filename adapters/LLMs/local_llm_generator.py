import os
import logging
from transformers import pipeline, Pipeline
from typing import Optional

# Se reutiliza el logger central definido en utils/logger.py
logger = logging.getLogger("RAGLogger")

# Variable global para cachear el modelo local cargado
_local_model: Optional[Pipeline] = None

def load_local_model() -> Pipeline:
    """
    Carga el modelo local utilizando la variable de entorno 'LOCAL_LLM_MODEL_PATH'.
    Se utiliza el pipeline de HuggingFace para la generación de texto.
    
    Returns:
        Pipeline: Un objeto pipeline para generación de texto.
        
    Raises:
        RuntimeError: Si la variable de entorno no está definida o falla la carga.
    """
    global _local_model
    if _local_model is not None:
        return _local_model

    model_path = os.getenv("LOCAL_LLM_MODEL_PATH")
    if not model_path:
        logger.error("LOCAL_LLM_MODEL_PATH no está configurado.")
        raise RuntimeError("LOCAL_LLM_MODEL_PATH no está configurado.")

    try:
        logger.info(f"Cargando modelo local desde {model_path}...")
        # En producción, se podría adaptar para cargar modelos en formato gguf
        _local_model = pipeline("text-generation", model=model_path)
        logger.info("Modelo local cargado exitosamente.")
        return _local_model
    except Exception as e:
        logger.error(f"Error cargando el modelo local desde {model_path}: {e}")
        raise RuntimeError(f"Error cargando el modelo local: {e}")

def generate(prompt: str) -> str:
    """
    Genera una respuesta a partir del prompt utilizando el modelo local.
    
    Args:
        prompt (str): El prompt de entrada.
    
    Returns:
        str: La respuesta generada.
        
    Raises:
        RuntimeError: Si ocurre algún error durante la generación.
    """
    try:
        model = load_local_model()
        logger.info(f"Generando respuesta para el prompt: {prompt}")
        # Se define un max_length de 50 tokens (ajustable según necesidades)
        result = model(prompt, max_length=50, do_sample=True)
        if isinstance(result, list) and result:
            text = result[0].get("generated_text", "")
            logger.info("Respuesta generada exitosamente.")
            return text
        else:
            logger.error("Resultado inesperado del modelo local.")
            raise RuntimeError("Resultado inesperado del modelo local.")
    except Exception as e:
        logger.error(f"Error en la generación local: {e}")
        raise RuntimeError(f"Error en la generación local: {e}")
