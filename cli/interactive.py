#!/usr/bin/env python
"""
interactive.py – Interfaz Interactiva REPL para el Sistema RAG

Esta versión state-of-the-art permite a los usuarios:
  - Configurar y ejecutar el pipeline RAG de forma guiada.
  - Seleccionar dinámicamente adaptadores disponibles (inputs, embeddings, vector stores y LLMs).
  - Ver información de configuración y resultados en tiempo real.
  - Generar logs detallados y capturar métricas de ejecución.

Utiliza prompt_toolkit para una experiencia de usuario enriquecida.
"""

import asyncio
import sys
import json
import os
import logging
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

# Importamos la configuración y el pipeline
from core.config import get_config, update_config
from core.loader import load_all_adapters
from core.pipeline import RAGPipeline

logger = logging.getLogger("RAGLogger")
logger.setLevel(logging.DEBUG)

# Cargar adaptadores disponibles dinámicamente
adapters = load_all_adapters()

# Crear un estilo para el prompt
prompt_style = Style.from_dict({
    'prompt': 'ansicyan bold',
    'option': 'ansiblue',
})

# Opciones dinámicas basadas en la metadata (se asume que los módulos tienen un método "create")
def get_options(category: str) -> list:
    if category in adapters:
        return list(adapters[category].keys())
    return []

# Definir los completers para cada categoría
input_completer = WordCompleter(get_options("Inputs"), ignore_case=True)
embedder_completer = WordCompleter(get_options("Embeddings"), ignore_case=True)
vectorstore_completer = WordCompleter(get_options("VectorStores"), ignore_case=True)
llm_completer = WordCompleter(get_options("LLMs"), ignore_case=True)

async def main():
    session = PromptSession()
    print("Bienvenido al REPL interactivo del Sistema RAG.")
    print("Configura los componentes del pipeline y ejecuta consultas.")
    print("Escribe 'exit' para salir.\n")

    # Leer o actualizar la configuración inicial
    config = get_config()
    print("Configuración actual:")
    print(json.dumps(config.model_dump(), indent=2))
    print("\n--- Seleccione los adaptadores a utilizar ---")

    # Seleccionar adaptador de Inputs
    input_adapter = await session.prompt_async(
        "[Input Adapter] (opciones: {}): ".format(", ".join(get_options("Inputs"))),
        completer=input_completer,
        style=prompt_style
    )
    # Seleccionar adaptador de Embeddings
    embedder = await session.prompt_async(
        "[Embedder] (opciones: {}): ".format(", ".join(get_options("Embeddings"))),
        completer=embedder_completer,
        style=prompt_style
    )
    # Seleccionar adaptador de Vector Store
    vector_store = await session.prompt_async(
        "[Vector Store] (opciones: {}): ".format(", ".join(get_options("VectorStores"))),
        completer=vectorstore_completer,
        style=prompt_style
    )
    # Seleccionar adaptador de LLM
    llm = await session.prompt_async(
        "[LLM] (opciones: {}): ".format(", ".join(get_options("LLMs"))),
        completer=llm_completer,
        style=prompt_style
    )

    # Actualizar la configuración global
    update_config({
        "input": input_adapter.strip() or config.input,
        "embedder": embedder.strip() or config.embedder,
        "vector_store": vector_store.strip() or config.vector_store,
        "llm": llm.strip() or config.llm,
    })
    config = get_config()  # Actualizamos la instancia

    print("\nConfiguración actualizada:")
    print(json.dumps(config.model_dump(), indent=2))
    print("\nIngrese consultas para el pipeline RAG. Escriba 'exit' para terminar.\n")

    pipeline = RAGPipeline()
    while True:
        query = await session.prompt_async("[Consulta] > ", style=prompt_style)
        if query.strip().lower() in {"exit", "quit"}:
            print("Saliendo del REPL interactivo. ¡Hasta luego!")
            break
        try:
            # Ejecutar el pipeline con la consulta ingresada
            result = pipeline.run(query)
            print("Respuesta generada:")
            print(result)
        except Exception as e:
            logger.error(f"Error durante la ejecución del pipeline: {e}")
            print(f"Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupción detectada. Saliendo del REPL interactivo.")
        sys.exit(0)
