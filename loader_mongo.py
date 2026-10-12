import os
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

def obter_resumo_banco():
    """Retorna contagem de ativos e descontinuados no MongoDB."""
    if imoveis_collection is None:
        return None
    try:
        total_ativos = imoveis_collection.count_documents({"ativo": {"$ne": False}})
        total_descontinuados = imoveis_collection.count_documents({"ativo": False})
        return {
            "ativos": total_ativos,
            "descontinuados": total_descontinuados,
            "total": total_ativos + total_descontinuados
        }
    except Exception:
        return None

def sincronizar_base_historica():
    """
    Garante que documentos existentes no banco sem o campo 'ativo'
    sejam inicializados como ativos (ativo=True, descontinuado_em=None).
    """
    if imoveis_collection is not None:
        try:
            res = imoveis_collection.update_many(
                {"ativo": {"$exists": False}},
                {"$set": {"ativo": True, "descontinuado_em": None}}
            )
            if res.modified_count > 0:
                print(f"-> Base inicializada: {res.modified_count} imóveis antigos atualizados com 'ativo=True'.")
        except Exception as e:
            print(f"Aviso ao sincronizar base histórica: {e}")

def carregar_arquivo(caminho_arquivo):
    """
    Carrega e faz upsert de um arquivo JSON no MongoDB, mantendo histórico:
    1. Marca todos os imóveis presentes no arquivo como ATIVOS (ativo=True, last_updated=agora, descontinuado_em=None).
    2. Identifica imóveis da MESMA imobiliária/fonte que já estavam no banco mas NÃO vieram nesta captura.
    3. Marca esses imóveis ausentes como DESCONTINUADOS (ativo=False, descontinuado_em=agora), sem deletá-los.
    """
    print(f"\n-> Processando: '{caminho_arquivo}'...")
    
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return False

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except Exception as e:
        print(f"Erro ao abrir/decodificar '{caminho_arquivo}': {e}")
        return False

    if not isinstance(dados, list) or len(dados) == 0:
        print(f"Aviso: '{caminho_arquivo}' está vazio ou não contém uma lista de imóveis. Operação cancelada.")
        return False

    if imoveis_collection is None:
        print(f"Banco de dados não conectado. Verifique 'credentials.env'. ({len(dados)} imóveis lidos no arquivo).")
        return False

    ops = []
    agora = datetime.now(timezone.utc)
    ids_atuais = set()
    imobiliarias_arquivo = set()
    crawler_sources_arquivo = set()

    for item in dados:
        if not isinstance(item, dict) or "id_unico" not in item:
            continue
        
        id_unico = item["id_unico"]
        ids_atuais.add(id_unico)

        if item.get("imobiliaria"):
            imobiliarias_arquivo.add(item["imobiliaria"])
        if item.get("crawler_source"):
            crawler_sources_arquivo.add(item["crawler_source"])

        # Garante que imóveis na captura atual fiquem ativos
        item["ativo"] = True
        item["descontinuado_em"] = None
        item["last_updated"] = agora
        
        ops.append(UpdateOne({"id_unico": id_unico}, {"$set": item}, upsert=True))

    if not ops:
        print("Nenhum imóvel válido com 'id_unico' encontrado para salvar.")
        return False

    # 1. Executa o upsert dos imóveis atuais em lotes de até 1.000
    batch_size = 1000
    total_inseridos = 0
    total_atualizados = 0

    try:
        for i in range(0, len(ops), batch_size):
            lote = ops[i:i + batch_size]
            res = imoveis_collection.bulk_write(lote, ordered=False)
            total_inseridos += res.upserted_count
            total_atualizados += res.modified_count
    except Exception as e:
        print(f"Erro durante o bulk_write no MongoDB: {e}")
        return False

    # 2. Descontinuação de imóveis ausentes (da mesma imobiliária/fonte)
    total_descontinuados = 0
    if ids_atuais and (crawler_sources_arquivo or imobiliarias_arquivo):
        condicoes_origem = []
        if crawler_sources_arquivo:
            condicoes_origem.append({"crawler_source": {"$in": list(crawler_sources_arquivo)}})
        if imobiliarias_arquivo:
            condicoes_origem.append({"imobiliaria": {"$in": list(imobiliarias_arquivo)}})

        filtro_origem = {"$or": condicoes_origem} if condicoes_origem else {}

        # Imóveis da mesma fonte que estavam ativos mas não constam na nova captura
        query_descontinuar = {
            **filtro_origem,
            "ativo": {"$ne": False},
            "id_unico": {"$nin": list(ids_atuais)}
        }

        try:
            res_desc = imoveis_collection.update_many(
                query_descontinuar,
                {
                    "$set": {
                        "ativo": False,
                        "descontinuado_em": agora
                    }
                }
            )
            total_descontinuados = res_desc.modified_count
        except Exception as e:
            print(f"Aviso ao marcar imóveis descontinuados: {e}")

    nome_arquivo = os.path.basename(caminho_arquivo)
    print(f"Sucesso [{nome_arquivo}]!")
    print(f"  • Novos inseridos:      {total_inseridos:>5}")
    print(f"  • Atualizados (ativos): {total_atualizados:>5}")
    print(f"  • Descontinuados:        {total_descontinuados:>5} (marcados como inativos/histórico)")
    print(f"  • Total no arquivo:      {len(dados):>5}")
    return True

def resolver_argumento(arg, arquivos_disponiveis):
    """
    Tenta resolver um argumento da linha de comando para um arquivo real.
    Aceita caminho completo, nome de arquivo ou parte do nome (ex: 'zanfer').
    """
    # 1. Caminho exato
    if os.path.exists(arg):
        return [os.path.normpath(arg)]
    
    # 2. Na pasta dados_imoveis
    caminho_pasta = os.path.join(DEFAULT_DIR, arg)
    if os.path.exists(caminho_pasta):
        return [os.path.normpath(caminho_pasta)]
    if os.path.exists(f"{caminho_pasta}.json"):
        return [os.path.normpath(f"{caminho_pasta}.json")]
    if os.path.exists(os.path.join(DEFAULT_DIR, f"imoveis_{arg}.json")):
        return [os.path.normpath(os.path.join(DEFAULT_DIR, f"imoveis_{arg}.json"))]

    # 3. Match por substring
    termo = arg.lower()
    matches = [a for a in arquivos_disponiveis if termo in os.path.basename(a).lower()]
    return matches

def menu_interativo(arquivos):
    """
    Exibe um menu interativo para o usuário selecionar quais arquivos deseja enviar.
    """
    if not arquivos:
        print(f"Nenhum arquivo JSON encontrado em '{DEFAULT_DIR}/' ou na raiz.")
        print("Execute o 'main.py' primeiro para gerar os arquivos dos crawlers.")
        return []

    resumo = obter_resumo_banco()
    print("\n" + "=" * 65)
    print("ARQUIVOS DISPONÍVEIS PARA ENVIO AO MONGODB")
    if resumo:
        print(f"Base Atual: {resumo['ativos']} ativos | {resumo['descontinuados']} descontinuados (total: {resumo['total']})")
    print("=" * 65)
    
    for idx, arq in enumerate(arquivos, 1):
        qtd = contar_imoveis_arquivo(arq)
        nome = os.path.basename(arq)
        pasta = os.path.dirname(arq) or "."
        print(f" [{idx:>2}] {nome:<30} ({qtd:>4} imóveis) [pasta: {pasta}]")

    print("-" * 65)
    print(" [ T] Enviar TODOS os arquivos listados acima")
    print(" [ 0] Cancelar / Sair")
    print("=" * 65)

    escolha = input("\nEscolha o número do arquivo (ou múltiplos ex: 1,3 ou 'T'): ").strip()
    
    if not escolha or escolha in ['0', 'q', 'Q', 'sair']:
        print("Operação cancelada.")
        return []

    if escolha.upper() in ['T', 'TODOS', 'ALL']:
        return arquivos

    # Interpreta seleções numéricas
    selecionados = []
    partes = [p.strip() for p in escolha.replace(';', ',').split(',') if p.strip()]
    for p in partes:
        if '-' in p:
            try:
                ini, fim = map(int, p.split('-'))
                for n in range(ini, fim + 1):
                    if 1 <= n <= len(arquivos) and arquivos[n - 1] not in selecionados:
                        selecionados.append(arquivos[n - 1])
            except ValueError:
                pass
        else:
            try:
                n = int(p)
                if 1 <= n <= len(arquivos) and arquivos[n - 1] not in selecionados:
                    selecionados.append(arquivos[n - 1])
            except ValueError:
                pass

    return selecionados

def main():
    # Inicializa campos históricos caso ainda não existam
    sincronizar_base_historica()

    arquivos_disponiveis = listar_arquivos_disponiveis()
    
    # Se passou argumentos pela linha de comando
    args = sys.argv[1:]
    arquivos_para_processar = []

    if args:
        if any(a in ['--todos', '-t', '--all', '-a'] for a in args):
            arquivos_para_processar = arquivos_disponiveis
        else:
            for arg in args:
                resolvidos = resolver_argumento(arg, arquivos_disponiveis)
                if resolvidos:
                    for r in resolvidos:
                        if r not in arquivos_para_processar:
                            arquivos_para_processar.append(r)
                else:
                    print(f"Aviso: Nenhum arquivo correspondente a '{arg}' foi encontrado.")
    else:
        # Modo interativo
        arquivos_para_processar = menu_interativo(arquivos_disponiveis)

    if not arquivos_para_processar:
        print("Nenhum arquivo selecionado para envio.")
        return

    print(f"\nIniciando carga de {len(arquivos_para_processar)} arquivo(s) selecionado(s)...")
    sucessos = 0
    for arq in arquivos_para_processar:
        if carregar_arquivo(arq):
            sucessos += 1

    print("\n" + "=" * 50)
    print(f"Finalizado: {sucessos}/{len(arquivos_para_processar)} arquivo(s) processados com sucesso.")
    
    resumo_final = obter_resumo_banco()
    if resumo_final:
        print(f"Status Atual do Banco: {resumo_final['ativos']} ativos | {resumo_final['descontinuados']} históricos/descontinuados (Total: {resumo_final['total']})")
    print("=" * 50)

if __name__ == "__main__":
    main()