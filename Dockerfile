FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema (necessárias pro chromadb-client)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema (necessárias pro chromadb-client compilar o hnswlib)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Atualiza o pip e instala as dependências Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn==0.30.0 \
    mem0ai==0.1.29 \
    chromadb==0.5.3 \
    pydantic==2.7.0

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]
