import os
import importlib
import logging
from pathlib import Path

# Configuración básica del logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def discover_adapters(root_dir: str = "adapters") -> dict:
    """
    Recorre recursivamente el directorio de adaptadores y descubre todos los módulos .py 
    (excluyendo __init__.py) organizados por categorías según su ruta.

    Retorna un diccionario con la siguiente estructura:
      {
         'Inputs': { 'json_loader': <module>, 'sql_loader': <module>, ... },
         'Embeddings': { 'openai_embedder': <module>, 'sentence_transformer_embedder': <module>, ... },
         'LLMs': { 'openai_generator': <module>, 'local_llm_generator': <module>, ... },
         'VectorStores': { 'faiss_store': <module>, 'chroma_store': <module>, ... }
      }
    
    La estructura de importación se basa en la carpeta raíz "adapters".
    """
    adapters = {}
    root_path = Path(root_dir)
    if not root_path.exists():
        logger.error(f"El directorio de adaptadores '{root_dir}' no existe.")
        return adapters

    # Recorre el directorio recursivamente
    for dirpath, _, filenames in os.walk(root_path):
        current_path = Path(dirpath)
        # La categoría se define como el primer directorio debajo de "adapters"
        try:
            category = current_path.relative_to(root_path).parts[0]
        except IndexError:
            # Si estamos en el directorio raíz "adapters", se ignora
            continue

        if category not in adapters:
            adapters[category] = {}

        for filename in filenames:
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]  # quita la extensión .py
                # Construye el nombre de importación basado en la estructura
                try:
                    # Extrae las partes de la ruta relativa a "adapters"
                    relative_parts = current_path.relative_to(root_path).parts
                    # El nombre completo del módulo se arma como: adapters.<Category>[.<subcat>...].<module_name>
                    module_import_path = "adapters." + ".".join(relative_parts + (module_name,))
                    module = importlib.import_module(module_import_path)
                    adapters[category][module_name] = module
                    logger.info(f"Descubierto módulo: {module_import_path}")
                except Exception as e:
                    logger.error(f"Error al importar el módulo '{module_import_path}': {e}")
    return adapters

# Función de conveniencia para inyectar o cargar los adaptadores
def load_all_adapters(root_dir: str = "adapters") -> dict:
    """
    Llama a discover_adapters() y retorna la estructura completa de adaptadores.
    Esta función puede extenderse para realizar tareas adicionales (por ejemplo, validación de interfaces)
    antes de retornar los módulos descubiertos.
    """
    adapters = discover_adapters(root_dir)
    # Aquí se pueden agregar comprobaciones adicionales (por ejemplo, verificar que cada módulo implemente una función "create")
    return adapters

# Ejemplo de uso cuando se ejecuta este script directamente
if __name__ == "__main__":
    adapters_found = load_all_adapters()
    for category, modules in adapters_found.items():
        print(f"Categoría: {category}")
        for name, mod in modules.items():
            print(f"  Módulo: {name} -> {mod}")
