mport os
import sys
import glob
import json
from pathlib import Path
from datetime import datetime, timezone
from pymongo import UpdateOne
from backend.database import imoveis_collection
DEFAULT_DIR = "dados_imoveis"
def listar_arquivos_disponiveis(diretorio=DEFAULT_DIR):
    """
    Lista todos os arquivos JSON de imóveis disponíveis para carga.
    Procura tanto na pasta especificada quanto na raiz do projeto.
    """
    arquivos = []
    
    # Busca na pasta dados_imoveis
    if os.path.isdir(diretorio):
        for f in sorted(glob.glob(os.path.join(diretorio, "*.json"))):
            arquivos.append(os.path.normpath(f))
            
    # Busca também arquivos 'imoveis_*.json' na raiz (para compatibilidade)
    for f in sorted(glob.glob("imoveis_*.json")):
        caminho_norm = os.path.normpath(f)
        if caminho_norm not in arquivos:
            arquivos.append(caminho_norm)
            
    return arquivos
def contar_imoveis_arquivo(caminho):
    """Retorna a contagem de itens em um arquivo JSON de forma segura."""
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return len(dados) if isinstance(dados, list) else 0
    except Exception:
        return 0
def carregar_arquivo(caminho_arquivo):
    """
    Carrega e faz upsert de um arquivo JSON específico no MongoDB.
    """