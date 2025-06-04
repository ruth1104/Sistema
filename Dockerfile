FROM python:3.13-alpine 
# Establecer el directorio de trabajo
WORKDIR /app
# Copiar requirements.txt e instalar dependencias
COPY requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt
# Copiar el resto del código
COPY . .
EXPOSE 8084

RUN mkdir -p /initial_static && cp -r /app/app/static/. /initial_static/

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

CMD [ "python", "run.py" ]
#CMD sh -c "gunicorn --bind 0.0.0.0:8081 --workers 4 --forwarded-allow-ips=*  wsgi:app"