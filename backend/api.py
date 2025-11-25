from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional, Dict, Any
from database import imoveis_collection
from models import Imovel
import uvicorn
import pymongo

app = FastAPI(title="API Imóveis Unificada", version="1.1")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que qualquer site acesse (ok para desenvolvimento)
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, etc.
    allow_headers=["*"],
)

def converter_mongo_para_dict(imovel):
    if "_id" in imovel:
        del imovel["_id"]
    return imovel

@app.get("/")
def home():
    return {
        "status": "online",
        "endpoints": {
            "Listagem": "/imoveis",
            "Opções de Filtro": "/filtros",
            "Detalhe": "/imoveis/{id_unico}"
        }
    }

# Endpoint auxiliar para preencher os Selects do Frontend
@app.get("/filtros")
def obter_opcoes_filtro():
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail="Banco não conectado")

    # Busca valores únicos no banco para montar os dropdowns
    # Isso é muito rápido no Mongo
    try:
        cidades = imoveis_collection.distinct("cidade")
        bairros = imoveis_collection.distinct("bairro")
        tipos = imoveis_collection.distinct("tipo")
        # Remove valores nulos ou vazios e ordena
        cidades = sorted([c for c in cidades if c])
        bairros = sorted([b for b in bairros if b])
        tipos = sorted([t for t in tipos if t])
        
        return {
            "cidades": cidades,
            "bairros": bairros,
            "tipos": tipos,
            "modalidades": ["VENDA", "ALUGUEL"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao agregar filtros: {str(e)}")

@app.get("/imoveis")
def listar_imoveis(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    cidade: Optional[str] = None,
    bairro: Optional[str] = None,
    modalidade: Optional[str] = None,
    tipo: Optional[str] = None,
    quartos_min: Optional[int] = None,
    preco_min: Optional[float] = None,
    preco_max: Optional[float] = None,
    ordenar_por: Optional[str] = Query(None, pattern="^(menor_preco|maior_preco|recente)$")
):
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail="Banco não conectado")

    skip = (page - 1) * limit
    query = {}

    # Filtros (Case Insensitive para texto)
    if cidade:
        query["cidade"] = {"$regex": f"^{cidade}$", "$options": "i"} # Busca exata mas case-insensitive
    if bairro:
        query["bairro"] = {"$regex": bairro, "$options": "i"}
    if tipo:
        query["tipo"] = {"$regex": tipo, "$options": "i"}
    if modalidade:
        query["modalidade"] = modalidade.upper()
    
    # Filtros Numéricos
    if quartos_min:
        query["quartos"] = {"$gte": quartos_min}
    
    # Filtro de Preço (Range)
    if preco_min or preco_max:
        query["preco"] = {}
        if preco_min: query["preco"]["$gte"] = preco_min
        if preco_max: query["preco"]["$lte"] = preco_max

    # Contagem total para paginação (antes de aplicar limit/skip)
    total_registros = imoveis_collection.count_documents(query)

    # Ordenação
    sort_criteria = [("id_unico", pymongo.ASCENDING)] # Padrão
    if ordenar_por == "menor_preco":
        sort_criteria = [("preco", pymongo.ASCENDING)]
    elif ordenar_por == "maior_preco":
        sort_criteria = [("preco", pymongo.DESCENDING)]
    elif ordenar_por == "recente":
        sort_criteria = [("last_updated", pymongo.DESCENDING)]

    # Executa Query
    cursor = imoveis_collection.find(query).sort(sort_criteria).skip(skip).limit(limit)
    
    dados = [converter_mongo_para_dict(doc) for doc in cursor]

    # Retorno "Envelope" (Melhor prática para APIs)
    return {
        "meta": {
            "total": total_registros,
            "page": page,
            "limit": limit,
            "pages": (total_registros // limit) + (1 if total_registros % limit > 0 else 0)
        },
        "data": dados
    }

@app.get("/imoveis/{id_unico}", response_model=Imovel)
def obter_detalhe_imovel(id_unico: str):
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail="Banco não conectado")
        
    imovel = imoveis_collection.find_one({"id_unico": id_unico})
    if imovel:
        return converter_mongo_para_dict(imovel)
    raise HTTPException(status_code=404, detail="Imóvel não encontrado")

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)