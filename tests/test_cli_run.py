"""
test_run.py – Pruebas para el script run.py del pipeline RAG

Estas pruebas simulan la ejecución de run.py mediante la inyección de argumentos en sys.argv.
Se verifican dos escenarios:
  1. Ejecución exitosa del pipeline con respuesta simulada.
  2. Ejecución que provoca fallo en pipeline.run() y finaliza con código de error.
Utilizamos monkeypatch para modificar sys.argv y sustituir la clase RAGPipeline por versiones dummy.
"""

import sys
import pytest
from cli import run

# Dummy pipeline que simula una ejecución exitosa
class DummyPipeline:
    def run(self, query, project_path=None):
        return f"Respuesta simulada para: {query}"

# Dummy pipeline que simula un fallo en la ejecución
class FailingPipeline:
    def run(self, query, project_path=None):
        raise Exception("Fallo simulado en el pipeline")

@pytest.fixture(autouse=True)
def dummy_pipeline(monkeypatch):
    # Por defecto, sustituye RAGPipeline por DummyPipeline para los tests de éxito
    monkeypatch.setattr("core.pipeline.RAGPipeline", lambda: DummyPipeline())

def test_run_success(monkeypatch, capsys):
    # Simula argumentos de línea de comandos para una ejecución exitosa
    test_args = [
        "run.py",
        "--query", "Hola, ¿qué tal?",
        "--input", "json_loader",
        "--embedder", "openai_embedder",
        "--vector_store", "faiss_store",
        "--llm", "openai_generator"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    
    # Ejecuta el main() de run.py
    run.main()
    
    captured = capsys.readouterr().out
    # Verifica que se muestre la respuesta simulada
    assert "Respuesta generada:" in captured
    assert "Respuesta simulada para: Hola, ¿qué tal?" in captured

def test_run_failure(monkeypatch, capsys):
    # Sustituye RAGPipeline por FailingPipeline para simular un fallo
    monkeypatch.setattr("core.pipeline.RAGPipeline", lambda: FailingPipeline())
    
    test_args = [
        "run.py",
        "--query", "Consulta de error"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    
    with pytest.raises(SystemExit) as exit_info:
        run.main()
    captured = capsys.readouterr().out
    # Verifica que se muestre el mensaje de error y se finalice con código de error
    assert "Error:" in captured
    assert "Fallo simulado en el pipeline" in captured
    assert exit_info.value.code == 1
