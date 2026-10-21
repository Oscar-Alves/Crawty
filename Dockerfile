FROM python:3.11-slim

# Define a pasta de trabalho na raiz do container
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary :all: \
    fastapi==0.136.1 \
    uvicorn==0.46.0 \
    pymongo==4.17.0 \
    python-dotenv==1.2.2 \
    pydantic==2.13.4 \
    requests==2.34.1 \
    beautifulsoup4==4.14.3

# Copia a pasta backend para dentro de /app/backend
COPY backend/ ./backend/

# O PULO DO GATO: Adiciona a pasta /app/backend à lista de locais onde o Python busca arquivos
ENV PYTHONPATH=/app:/app/backend

# Garante que a saída do log apareça imediatamente (sem buffer)
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Agora podemos chamar o uvicorn apontando direto para o módulo "api", 
# pois o "api.py" está dentro do PYTHONPATH que definimos acima.
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]