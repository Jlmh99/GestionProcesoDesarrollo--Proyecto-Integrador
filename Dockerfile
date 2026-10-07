# Imagen base de Python
FROM python:3.12-slim

# Directorio de trabajo
WORKDIR /app

# Configuración de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY app/ ./app/

# Copiar servidor Flask + Socket
COPY run.py .
COPY socket_server.py .

# Crear directorios de SQLite y respaldos
RUN mkdir -p /app/instance/backups

# Puertos utilizados
EXPOSE 80
EXPOSE 6061

# Iniciar Flask + Socket TCP
CMD ["python", "run.py"]