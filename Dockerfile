FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/
COPY scripts/ ./scripts/

# Crear directorio para outputs
RUN mkdir -p /app/outputs

# Variables de entorno por defecto
ENV DATABASE_URL=""
ENV OUTPUT_DIR="/app/outputs"
ENV PYTHONUNBUFFERED=1

# Exponer puerto para SSE transport (opcional)
EXPOSE 8000

# Comando por defecto - stdio transport
CMD ["python", "-m", "src.server"]
