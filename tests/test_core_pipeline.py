import pytest
from core.pipeline import RAGPipeline
from unittest.mock import MagicMock

@pytest.fixture
def sample_documents():
    return [
        {"id": "doc1", "texto": "Texto de ejemplo 1", "metadata": {"origen": "test", "fecha": "2025-03-22"}},
        {"id": "doc2", "texto": "Texto de ejemplo 2", "metadata": {"origen": "test", "fecha": "2025-03-22"}}
    ]

@pytest.fixture
def pipeline_instance(sample_documents):
    # Se crea una instancia de RAGPipeline y se parchean (mock) los métodos críticos para pruebas.
    pipeline = RAGPipeline()
    pipeline.load_data = MagicMock(return_value=sample_documents)
    pipeline.compute_embeddings = MagicMock(return_value=[[0.1, 0.2], [0.3, 0.4]])
    pipeline.store_vectors = MagicMock()
    pipeline.retrieve_and_generate = MagicMock(return_value="Respuesta de prueba")
    pipeline.process_pre_rag = MagicMock(return_value={"pre": "data"})
    return pipeline

def test_pipeline_run_success(pipeline_instance):
    query = "Consulta de prueba"
    result = pipeline_instance.run(query)
    assert result == "Respuesta de prueba"
    pipeline_instance.load_data.assert_called_once()
    pipeline_instance.compute_embeddings.assert_called_once_with(
        [doc["texto"] for doc in pipeline_instance.load_data.return_value]
    )
    pipeline_instance.store_vectors.assert_called_once()
    pipeline_instance.retrieve_and_generate.assert_called_once_with(query)

def test_pipeline_run_no_documents(pipeline_instance):
    pipeline_instance.load_data = MagicMock(return_value=[])
    query = "Consulta sin documentos"
    with pytest.raises(RuntimeError, match="No se cargaron documentos"):
        pipeline_instance.run(query)

def test_pre_rag_integration(pipeline_instance):
    # Verificar que si se pasa un project_path se invoque process_pre_rag.
    query = "Consulta con pre-RAG"
    project_path = "/ruta/proyecto"
    pipeline_instance.run(query, project_path)
    pipeline_instance.process_pre_rag.assert_called_once_with(project_path)
