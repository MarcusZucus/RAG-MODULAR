"""
test_cli_interactive.py – Pruebas para la interfaz interactiva (CLI REPL) del sistema RAG

Esta suite simula una sesión interactiva completa utilizando prompt_toolkit, inyectando entradas
de forma automatizada para:
  - Configurar los adaptadores disponibles.
  - Ejecutar una consulta.
  - Finalizar la sesión con el comando de salida ("exit").
  
Se utiliza un PipeInput y DummyOutput de prompt_toolkit para evitar la intervención manual.
"""

import asyncio
import json
import pytest
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

# Importamos el módulo interactivo
from cli import interactive

@pytest.fixture
def pipe_input():
    # Creamos una entrada de tubería para simular el input interactivo
    pi = create_pipe_input()
    yield pi
    pi.close()

@pytest.mark.asyncio
async def test_interactive_session(monkeypatch, pipe_input, capsys):
    """
    Simula una sesión interactiva completa:
      1. Configuración de adaptadores (Input, Embedder, Vector Store y LLM)
      2. Ejecución de una consulta al pipeline RAG
      3. Comando de salida ("exit")
    """
    # Simulamos las entradas que el usuario proporcionaría:
    simulated_inputs = [
        "json_loader\n",              # Seleccionar adaptador de Inputs
        "openai_embedder\n",          # Seleccionar adaptador de Embeddings
        "faiss_store\n",              # Seleccionar adaptador de Vector Store
        "openai_generator\n",         # Seleccionar adaptador de LLM
        "Hola, ¿cómo funciona el sistema RAG?\n",  # Consulta al pipeline
        "exit\n"                      # Comando de salida
    ]
    # Enviar cada entrada al pipe
    for text in simulated_inputs:
        pipe_input.send_text(text)

    # Configuramos el PromptSession de interactive.py para usar nuestro pipe_input y un DummyOutput
    monkeypatch.setattr(
        interactive,
        "PromptSession",
        lambda: interactive.PromptSession(input=pipe_input, output=DummyOutput())
    )

    # Ejecutamos el main interactivo
    await interactive.main()

    # Capturamos la salida para verificar ciertos mensajes clave
    captured = capsys.readouterr().out
    assert "Bienvenido al REPL interactivo del Sistema RAG" in captured
    assert "Configuración actualizada:" in captured
    assert ("Respuesta generada:" in captured) or ("Error:" in captured)
    assert "Saliendo del REPL interactivo" in captured
