# Backend Dockerfile - FastAPI + Python
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para compilar algumas bibliotecas Python
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o código do backend
COPY . .

# Expor a porta do FastAPI
EXPOSE 8000

# Comando para rodar o servidor FastAPI com uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]