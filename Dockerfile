FROM python:3.13-slim

# Instalar dependencias necesarias del sistema, incluyendo zbar
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libzbar-dev \
    libjpeg-dev \
    zlib1g-dev \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

EXPOSE 8084

# Crear copia de archivos estáticos
RUN mkdir -p /initial_static && cp -r /app/app/static/. /initial_static/

# Dar permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "run.py"]