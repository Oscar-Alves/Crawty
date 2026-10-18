FROM python:3.11-slim

# Define a pasta de trabalho na raiz do container
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt

# Copia a pasta backend para dentro de /app/backend
COPY backend/ ./backend/

# O PULO DO GATO: Adiciona a pasta /app/backend à lista de locais onde o Python busca arquivos
ENV PYTHONPATH=/app/backend

# Garante que a saída do log apareça imediatamente (sem buffer)
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Agora podemos chamar o uvicorn apontando direto para o módulo "api", 
# pois o "api.py" está dentro do PYTHONPATH que definimos acima.
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]