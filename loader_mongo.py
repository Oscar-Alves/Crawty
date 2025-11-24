import json
from pymongo import UpdateOne
from datetime import datetime, timezone
from backend.database import imoveis_collection

def carregar():
    if imoveis_collection is None:
        print("Banco não conectado. Verifique o .env")
        return

    try:
        with open('imoveis_consolidados.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except:
        print("JSON não encontrado. Rode o main.py primeiro.")
        return

    ops = []
    agora = datetime.now(timezone.utc)
    for item in dados:
        item["last_updated"] = agora
        # Upsert: Se existe ID, atualiza. Se não, cria.
        ops.append(UpdateOne({"id_unico": item["id_unico"]}, {"$set": item}, upsert=True))

    if ops:
        res = imoveis_collection.bulk_write(ops)
        print(f"Sucesso! Inseridos: {res.upserted_count}, Atualizados: {res.modified_count}")
    else:
        print("Nenhum dado para salvar.")

if __name__ == "__main__":
    carregar()