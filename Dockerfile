FROM python:3.13-alpine

# Instalar dependencias necesarias del sistema, incluyendo zbar
RUN apk add --no-cache \
    zbar \
    build-base \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    tiff-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    harfbuzz-dev \
    fribidi-dev \
    libxcb-dev \
    libx11-dev

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias de Python
COPY requirements.txt .
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