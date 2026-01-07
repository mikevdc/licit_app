# 1. Usamos una imagen base de Python ligera (Slim)
FROM python:3.11-slim

# 2. Evitamos que Python genere archivos .pyc y buffer de salida
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /code

# 4. Instalamos dependencias del sistema necesarias para compilar (opcional pero recomendado)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 5. Copiamos PRIMERO los requirements (Truco de caché de Docker)
# Si no cambias dependencias, Docker se salta este paso y va rápido.
COPY requirements.txt .

# 6. Instalamos las librerías
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copiamos el resto del código
COPY ./src /code

# 8. Exponemos el puerto
EXPOSE 8000

# 9. Comando de arranque
# IMPORTANTE: host 0.0.0.0 para que sea accesible desde fuera del contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]