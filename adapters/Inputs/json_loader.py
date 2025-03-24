"""
json_loader.py – Adaptador para carga de datos desde archivos JSON.

Este módulo implementa la función create() para registrar el adaptador y load() para cargar documentos.
En un entorno real, load() leería un archivo JSON, validaría y normalizaría la data.
Aquí se implementa una versión mínima para fines de test y desarrollo.
"""

def create():
    """
    Función de registro que permite identificar este adaptador.
    
    Returns:
        str: Una cadena indicando que el adaptador fue creado exitosamente.
    """
    return "json_loader_creado"

def load():
    """
    Simula la carga de documentos desde un archivo JSON.
    
    Returns:
        list: Lista de diccionarios representando documentos.
    """
    # Ejemplo simple: se retorna una lista con un documento de prueba.
    return [
        {
            "id": "doc1",
            "texto": "Documento de prueba para JSON loader.",
            "metadata": {"origen": "ejemplo", "fecha": "2025-03-22"}
        }
    ]
