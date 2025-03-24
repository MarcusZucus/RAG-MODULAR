#!/usr/bin/env python
"""
run.py – Ejecución del Pipeline RAG desde la Línea de Comandos

Este script permite ejecutar el pipeline RAG de forma no interactiva,
aceptando argumentos para configurar los adaptadores y la consulta a procesar.
Utiliza argparse para el parsing de argumentos y actualiza la configuración global
mediante update_config(). Luego, inicializa RAGPipeline y ejecuta el flujo completo,
mostrando la respuesta o los errores en la consola.
"""

import argparse
import sys
import json
import logging
from core.config import get_config, update_config
from core.pipeline import RAGPipeline

logger = logging.getLogger("RAGLogger")
logger.setLevel(logging.DEBUG)

def main():
    parser = argparse.ArgumentParser(
        description="Ejecuta el pipeline RAG con parámetros de configuración personalizados."
    )
    parser.add_argument("--query", type=str, required=True, help="Consulta para el pipeline RAG")
    parser.add_argument("--input", type=str, default=None, help="Adaptador de Inputs a utilizar")
    parser.add_argument("--embedder", type=str, default=None, help="Adaptador de Embeddings a utilizar")
    parser.add_argument("--vector_store", type=str, default=None, help="Adaptador de Vector Store a utilizar")
    parser.add_argument("--llm", type=str, default=None, help="Adaptador de LLM a utilizar")
    parser.add_argument("--project_path", type=str, default=None, help="Ruta del proyecto para el pre-RAG (opcional)")
    args = parser.parse_args()
    
    # Actualizar la configuración si se proporcionan nuevos adaptadores
    config_update = {}
    if args.input:
        config_update["input"] = args.input
    if args.embedder:
        config_update["embedder"] = args.embedder
    if args.vector_store:
        config_update["vector_store"] = args.vector_store
    if args.llm:
        config_update["llm"] = args.llm
    
    if config_update:
        update_config(config_update)
    
    config = get_config()
    logger.info("Configuración actualizada:\n" + json.dumps(config.model_dump(), indent=2))
    
    pipeline = RAGPipeline()
    try:
        result = pipeline.run(args.query, args.project_path)
        print("Respuesta generada:")
        print(result)
    except Exception as e:
        logger.error(f"Error al ejecutar el pipeline: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
