FROM python:3.11

WORKDIR /app

RUN pip install --upgrade pip && pip install --no-cache-dir fastapi==0.115.0 uvicorn==0.30.0 mem0ai==0.1.29 chromadb==0.5.3 pydantic==2.7.0

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]
