from fastapi import FastAPI, HTTPException
from typing import List, Optional
from database import imoveis_collection
from models import Imovel
import uvicorn  # Adicionado para permitir execução direta

app = FastAPI(title="API Imóveis Unificada", version="1.0")

def converter_mongo_para_dict(imovel):
    if "_id" in imovel:
        del imovel["_id"]
    return imovel

@app.get("/")
def home():
    return {"msg": "API Online. Acesse /docs para documentação."}

@app.get("/imoveis", response_model=List[Imovel])
def listar_imoveis(
    page: int = 1,
    limit: int = 50,
    cidade: Optional[str] = None,
    bairro: Optional[str] = None,
    modalidade: Optional[str] = None,
    quartos_min: Optional[int] = None,
    preco_max: Optional[float] = None
):
    # CORREÇÃO AQUI: Verifica explicitamente se é None
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail="Banco de dados não conectado")

    skip = (page - 1) * limit
    query = {}

    if cidade:
        query["cidade"] = {"$regex": cidade, "$options": "i"}
    if bairro:
        query["bairro"] = {"$regex": bairro, "$options": "i"}
    if modalidade:
        query["modalidade"] = modalidade.upper()
    if quartos_min:
        query["quartos"] = {"$gte": quartos_min}
    if preco_max:
        query["preco"] = {"$lte": preco_max}

    cursor = imoveis_collection.find(query).skip(skip).limit(limit)
    return [converter_mongo_para_dict(doc) for doc in cursor]

# --- Bloco para rodar diretamente via 'python backend/api.py' ---
if __name__ == "__main__":
    # Isso permite rodar o arquivo como um script comum
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)