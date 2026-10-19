import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / 'credentials.env'

load_dotenv(dotenv_path=env_path)

MONGO_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME", "imobiliaria_db")

if not MONGO_URL:
    print(f"ERRO CRÍTICO: Não foi possível encontrar o .env no caminho: {env_path}")
    print("Verifique se o arquivo .env existe e contém a variável MONGODB_URL.")
    client = None
    db = None
    imoveis_collection = None
    cliques_collection = None
    corretores_collection = None
else:
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        imoveis_collection = db["imoveis"]
        cliques_collection = db["cliques_leads"]
        corretores_collection = db["corretores"]
        client.admin.command('ping')
    except Exception as e:
        print(f"Erro ao conectar no MongoDB: {e}")
        imoveis_collection = None
        cliques_collection = None
        corretores_collection = None

def criar_indices():
    if imoveis_collection is not None:
        try:
            imoveis_collection.create_index("id_unico", unique=True)
            imoveis_collection.create_index("ativo")
            imoveis_collection.create_index([("ativo", 1), ("cidade", 1), ("bairro", 1)])
            imoveis_collection.create_index([("ativo", 1), ("preco", 1)])
            imoveis_collection.create_index([("ativo", 1), ("modalidade", 1)])
            imoveis_collection.create_index([("ativo", 1), ("tipo", 1)])
            if cliques_collection is not None:
                cliques_collection.create_index([("imobiliaria", 1), ("timestamp", -1)])
                cliques_collection.create_index([("id_unico", 1), ("timestamp", -1)])
            if corretores_collection is not None:
                corretores_collection.create_index("usuario", unique=True)
            print("Índices do MongoDB verificados.")
        except Exception as e:
            print(f"Erro ao criar índices: {e}")

if imoveis_collection is not None:
    criar_indices()