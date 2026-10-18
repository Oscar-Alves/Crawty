import os
import sys
import glob
import json
from pathlib import Path
from datetime import datetime, timezone
from pymongo import UpdateOne

from backend.database import imoveis_collection
from backend.normalizer import normalizar_imovel

DEFAULT_DIR = "dados_imoveis"


def listar_arquivos_disponiveis(diretorio=DEFAULT_DIR):
    """
    Lista todos os arquivos JSON de imóveis disponíveis para carga.
    Procura tanto na pasta especificada quanto na raiz do projeto.
    """
    arquivos = []

    if os.path.isdir(diretorio):
        for f in sorted(glob.glob(os.path.join(diretorio, "*.json"))):
            arquivos.append(os.path.normpath(f))

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
    Garante que documentos existentes no banco sem 'ativo', 'criado_em' ou 'historico_precos'
    sejam inicializados adequadamente.
    """
    if imoveis_collection is not None:
        try:
            agora = datetime.now(timezone.utc)
            res = imoveis_collection.update_many(
                {"ativo": {"$exists": False}},
                {"$set": {"ativo": True, "descontinuado_em": None}}
            )
            if res.modified_count > 0:
                print(f"-> Base inicializada: {res.modified_count} imóveis antigos atualizados com 'ativo=True'.")

            docs_sem_historico = list(
                imoveis_collection.find(
                    {"$or": [{"criado_em": {"$exists": False}}, {"historico_precos": {"$exists": False}}]},
                    {"_id": 1, "preco": 1, "last_updated": 1, "criado_em": 1, "historico_precos": 1, "preco_anterior": 1, "cliques": 1}
                )
            )
            if docs_sem_historico:
                ops_init = []
                for d in docs_sem_historico:
                    data_ref = d.get("criado_em") or d.get("last_updated") or agora
                    preco_atual = float(d.get("preco") or 0.0)
                    hist = d.get("historico_precos")
                    if not isinstance(hist, list) or len(hist) == 0:
                        hist = [{"preco": preco_atual, "data": data_ref}] if preco_atual > 0 else []
                    ops_init.append(
                        UpdateOne(
                            {"_id": d["_id"]},
                            {
                                "$set": {
                                    "criado_em": data_ref,
                                    "historico_precos": hist,
                                    "preco_anterior": d.get("preco_anterior"),
                                    "cliques": d.get("cliques", 0),
                                }
                            },
                        )
                    )
                for i in range(0, len(ops_init), 1000):
                    imoveis_collection.bulk_write(ops_init[i:i + 1000], ordered=False)
                print(f"-> Série histórica inicializada em {len(ops_init)} imóveis existentes.")
        except Exception as e:
            print(f"Aviso ao sincronizar base histórica: {e}")


def normalizar_base_existente():
    """
    Varre todos os documentos já salvos no MongoDB e aplica a normalização
    de cidade, bairro, tipo, subtipo e campos numéricos.
    """
    if imoveis_collection is None:
        print("Banco de dados não conectado.")
        return 0

    print("\n-> Normalizando registros existentes no MongoDB...")
    cursor = imoveis_collection.find({})
    ops = []
    total_lidos = 0

    for doc in cursor:
        total_lidos += 1
        doc_id = doc.get("_id")
        copia = {k: v for k, v in doc.items() if k != "_id"}
        normalizado = normalizar_imovel(copia)

        campos_atualizar = {
            "bairro": normalizado.get("bairro"),
            "cidade": normalizado.get("cidade"),
            "tipo": normalizado.get("tipo"),
            "titulo": normalizado.get("titulo"),
            "modalidade": normalizado.get("modalidade"),
            "quartos": normalizado.get("quartos"),
            "banheiros": normalizado.get("banheiros"),
            "vagas": normalizado.get("vagas"),
            "preco": normalizado.get("preco"),
            "area_util": normalizado.get("area_util"),
            "area_total": normalizado.get("area_total"),
            "extras": normalizado.get("extras", {}),
        }
        ops.append(UpdateOne({"_id": doc_id}, {"$set": campos_atualizar}))

    modificados = 0
    batch_size = 1000
    for i in range(0, len(ops), batch_size):
        res = imoveis_collection.bulk_write(ops[i:i + batch_size], ordered=False)
        modificados += res.modified_count

    print(f"-> Normalização concluída: {modificados} de {total_lidos} imóveis foram atualizados/padronizados.")
    return modificados


def desativar_imobiliaria(nome_imobiliaria: str):
    """
    Marca todos os anúncios ativos de uma determinada imobiliária como descontinuados (ativo=False),
    preservando os registros no histórico do MongoDB.
    """
    if imoveis_collection is None:
        print("Banco de dados não conectado.")
        return 0

    termo = nome_imobiliaria.strip()
    if not termo:
        print("Informe o nome da imobiliária para desativar.")
        return 0

    agora = datetime.now(timezone.utc)
    filtro = {
        "$or": [
            {"imobiliaria": {"$regex": termo, "$options": "i"}},
            {"crawler_source": {"$regex": termo, "$options": "i"}},
            {"id_unico": {"$regex": f"^{termo}_", "$options": "i"}},
        ],
        "ativo": {"$ne": False},
    }

    res = imoveis_collection.update_many(
        filtro,
        {"$set": {"ativo": False, "descontinuado_em": agora}},
    )
    print(f"-> Imobiliária '{termo}': {res.modified_count} imóveis marcados como descontinuados (inativos).")
    return res.modified_count


def carregar_arquivo(caminho_arquivo):
    """
    Carrega e faz upsert de um arquivo JSON no MongoDB, mantendo histórico:
    1. Marca todos os imóveis presentes no arquivo como ATIVOS (ativo=True, last_updated=agora, descontinuado_em=None).
    2. Registra criado_em e evolução de preços em historico_precos / preco_anterior quando houver alteração de valor.
    3. Identifica imóveis da MESMA imobiliária/fonte que já estavam no banco mas NÃO vieram nesta captura.
    4. Marca esses imóveis ausentes como DESCONTINUADOS (ativo=False, descontinuado_em=agora), sem deletá-los.
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

    agora = datetime.now(timezone.utc)
    ids_arquivo = [item["id_unico"] for item in dados if isinstance(item, dict) and "id_unico" in item]

    existentes_map = {}
    if ids_arquivo:
        cursor_existentes = imoveis_collection.find(
            {"id_unico": {"$in": ids_arquivo}},
            {
                "id_unico": 1,
                "preco": 1,
                "preco_anterior": 1,
                "historico_precos": 1,
                "criado_em": 1,
                "last_updated": 1,
                "cliques": 1,
                "_id": 0,
            },
        )
        for doc_ex in cursor_existentes:
            existentes_map[doc_ex["id_unico"]] = doc_ex

    ops = []
    ids_atuais = set()
    imobiliarias_arquivo = set()
    crawler_sources_arquivo = set()
    total_variacoes_preco = 0

    for item in dados:
        if not isinstance(item, dict) or "id_unico" not in item:
            continue

        normalizar_imovel(item)
        id_unico = item["id_unico"]
        ids_atuais.add(id_unico)

        if item.get("imobiliaria"):
            imobiliarias_arquivo.add(item["imobiliaria"])
        if item.get("crawler_source"):
            crawler_sources_arquivo.add(item["crawler_source"])

        preco_novo = float(item.get("preco") or 0.0)
        doc_antigo = existentes_map.get(id_unico)

        if doc_antigo is None:
            item["criado_em"] = agora
            item["preco_anterior"] = None
            item["historico_precos"] = [{"preco": preco_novo, "data": agora}] if preco_novo > 0 else []
            item["cliques"] = 0
        else:
            criado_em = doc_antigo.get("criado_em") or doc_antigo.get("last_updated") or agora
            item["criado_em"] = criado_em
            item["cliques"] = doc_antigo.get("cliques", 0)

            preco_antigo = float(doc_antigo.get("preco") or 0.0)
            hist = list(doc_antigo.get("historico_precos") or [])
            if not hist and preco_antigo > 0:
                hist = [{"preco": preco_antigo, "data": criado_em}]

            if preco_novo > 0 and preco_antigo > 0 and abs(preco_novo - preco_antigo) >= 1.0:
                item["preco_anterior"] = preco_antigo
                hist.append({"preco": preco_novo, "data": agora})
                total_variacoes_preco += 1
            else:
                item["preco_anterior"] = doc_antigo.get("preco_anterior")

            item["historico_precos"] = hist

        item["ativo"] = True
        item["descontinuado_em"] = None
        item["last_updated"] = agora

        ops.append(UpdateOne({"id_unico": id_unico}, {"$set": item}, upsert=True))

    if not ops:
        print("Nenhum imóvel válido com 'id_unico' encontrado para salvar.")
        return False

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

    total_descontinuados = 0
    if ids_atuais and (crawler_sources_arquivo or imobiliarias_arquivo):
        condicoes_origem = []
        if crawler_sources_arquivo:
            condicoes_origem.append({"crawler_source": {"$in": list(crawler_sources_arquivo)}})
        if imobiliarias_arquivo:
            condicoes_origem.append({"imobiliaria": {"$in": list(imobiliarias_arquivo)}})

        filtro_origem = {"$or": condicoes_origem} if condicoes_origem else {}

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
    print(f"  • Variações de preço:   {total_variacoes_preco:>5}")
    print(f"  • Descontinuados:        {total_descontinuados:>5} (marcados como inativos/histórico)")
    print(f"  • Total no arquivo:      {len(dados):>5}")
    return True


def resolver_argumento(arg, arquivos_disponiveis):
    """
    Tenta resolver um argumento da linha de comando para um arquivo real.
    Aceita caminho completo, nome de arquivo ou parte do nome (ex: 'zanfer').
    """
    if os.path.exists(arg):
        return [os.path.normpath(arg)]

    caminho_pasta = os.path.join(DEFAULT_DIR, arg)
    if os.path.exists(caminho_pasta):
        return [os.path.normpath(caminho_pasta)]
    if os.path.exists(f"{caminho_pasta}.json"):
        return [os.path.normpath(f"{caminho_pasta}.json")]
    if os.path.exists(os.path.join(DEFAULT_DIR, f"imoveis_{arg}.json")):
        return [os.path.normpath(os.path.join(DEFAULT_DIR, f"imoveis_{arg}.json"))]

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
    print(" [ N] Apenas NORMALIZAR toda a base já existente no MongoDB")
    print(" [ D] DESATIVAR todos os anúncios de uma imobiliária")
    print(" [ 0] Cancelar / Sair")
    print("=" * 65)

    escolha = input("\nEscolha o número do arquivo (ou múltiplos ex: 1,3, 'T', 'N' ou 'D'): ").strip()

    if not escolha or escolha in ['0', 'q', 'Q', 'sair']:
        print("Operação cancelada.")
        return []

    if escolha.upper() in ['N', 'NORMALIZAR']:
        normalizar_base_existente()
        return []

    if escolha.upper() in ['D', 'DESATIVAR']:
        nome_imob = input("Digite o nome da imobiliária a desativar (ex: Longatti): ").strip()
        if nome_imob:
            desativar_imobiliaria(nome_imob)
        return []

    if escolha.upper() in ['T', 'TODOS', 'ALL']:
        return arquivos

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
    sincronizar_base_historica()

    arquivos_disponiveis = listar_arquivos_disponiveis()

    args = sys.argv[1:]
    arquivos_para_processar = []

    if args:
        if '--desativar' in args or '-d' in args:
            flag = '--desativar' if '--desativar' in args else '-d'
            idx = args.index(flag)
            if idx + 1 < len(args):
                desativar_imobiliaria(args[idx + 1])
            else:
                print("Uso: python loader_mongo.py --desativar <nome_imobiliaria>")
            return

        if any(a in ['--normalizar', '-n'] for a in args):
            normalizar_base_existente()
            args = [a for a in args if a not in ['--normalizar', '-n']]
            if not args:
                return

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