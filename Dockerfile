# Dockerfile – Imagen de Contenedor para el Proyecto RAG

###############################################################################
# Etapa 1: Construcción
###############################################################################
FROM python:3.9-slim as builder

# Evita prompts en instalación de paquetes
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema necesarias para compilar libs nativas:
#  - build-essential: para compilar extensiones Python (psycopg2, etc.)
#  - git (opcional si vas a clonar repos; útil para sentence_transformers en modo local).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos requirements
COPY requirements.txt .

# Actualizamos pip y luego instalamos todas las dependencias
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

###############################################################################
# Etapa 2: Imagen Final
###############################################################################
FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive

# Instalamos librerías de sistema mínimas para torch, faiss, etc.
# libgomp1 se usa a menudo para Torch y FAISS.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos los paquetes ya instalados desde la etapa builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copiamos el resto del código del proyecto
COPY . .

# Exponemos el puerto 8000 (FastAPI/Uvicorn)
EXPOSE 8000

# Cambiamos el usuario a 'nobody' para no correr como root
USER nobody

# Configuramos el comando de arranque para FastAPI
# (Si prefieres CMD en vez de ENTRYPOINT, puedes cambiarlo sin problema)
ENTRYPOINT ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
