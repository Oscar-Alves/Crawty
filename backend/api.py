import re
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import pymongo

try:
    from database import imoveis_collection, cliques_collection
    from models import Imovel, CliqueLeadRequest
except ImportError:
    from backend.database import imoveis_collection, cliques_collection
    from backend.models import Imovel, CliqueLeadRequest

Error = "Banco não conectado"

app = FastAPI(title="API Imóveis Unificada", version="1.4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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
        "version": "1.4",
        "endpoints": {
            "Listagem": "/imoveis",
            "Opções de Filtro": "/filtros",
            "Detalhe": "/imoveis/{id_unico}",
            "Estatísticas de Mercado": "/estatisticas",
            "Registrar Clique (Lead)": "/leads/clique",
            "Resumo de Leads B2B": "/leads/resumo",
        },
    }


@app.get("/filtros")
def obter_opcoes_filtro(
    status: str = Query("ativos", pattern="^(ativos|descontinuados|todos)$")
):
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=Error)

    filtro_base = {}
    if status == "descontinuados":
        filtro_base = {"ativo": False}
    elif status != "todos":
        filtro_base = {"ativo": {"$ne": False}}

    try:
        docs = imoveis_collection.find(
            filtro_base,
            {
                "cidade": 1,
                "bairro": 1,
                "tipo": 1,
                "extras.subtipo": 1,
                "imobiliaria": 1,
                "_id": 0,
            },
        )

        cidades_set = set()
        bairros_set = set()
        bairros_por_cidade = {}
        tipos_set = set()
        subtipos_set = set()
        subtipos_por_tipo = {}
        imobiliarias_set = set()

        for d in docs:
            cid = d.get("cidade")
            bai = d.get("bairro")
            tip = d.get("tipo")
            sub = (d.get("extras") or {}).get("subtipo")
            imo = d.get("imobiliaria")

            if cid:
                cidades_set.add(cid)
                if bai and bai != "Não Informado":
                    bairros_por_cidade.setdefault(cid, set()).add(bai)

            if bai and bai != "Não Informado":
                bairros_set.add(bai)

            if tip:
                tipos_set.add(tip)
                if sub and sub != "Padrão":
                    subtipos_por_tipo.setdefault(tip, set()).add(sub)

            if sub and sub != "Padrão":
                subtipos_set.add(sub)

            if imo:
                imobiliarias_set.add(imo)

        return {
            "cidades": sorted(cidades_set),
            "bairros": sorted(bairros_set),
            "bairros_por_cidade": {
                k: sorted(v) for k, v in sorted(bairros_por_cidade.items())
            },
            "tipos": sorted(tipos_set),
            "subtipos": sorted(subtipos_set),
            "subtipos_por_tipo": {
                k: sorted(v) for k, v in sorted(subtipos_por_tipo.items())
            },
            "imobiliarias": sorted(imobiliarias_set),
            "modalidades": ["VENDA", "ALUGUEL"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao agregar filtros: {str(e)}"
        )


@app.get("/imoveis")
def listar_imoveis(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    busca: Optional[str] = None,
    cidade: Optional[str] = None,
    bairro: Optional[str] = None,
    modalidade: Optional[str] = None,
    tipo: Optional[str] = None,
    subtipo: Optional[str] = None,
    imobiliaria: Optional[str] = None,
    quartos_min: Optional[int] = None,
    suites_min: Optional[int] = None,
    banheiros_min: Optional[int] = None,
    vagas_min: Optional[int] = None,
    preco_min: Optional[float] = None,
    preco_max: Optional[float] = None,
    area_min: Optional[float] = None,
    area_max: Optional[float] = None,
    apenas_com_foto: Optional[bool] = None,
    apenas_queda_preco: Optional[bool] = None,
    ordenar_por: Optional[str] = Query(
        None,
        pattern="^(menor_preco|maior_preco|maior_area|menor_area|recentes?)$",
    ),
    status: str = Query("ativos", pattern="^(ativos|descontinuados|todos)$"),
):
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=Error)

    skip = (page - 1) * limit
    and_conditions = []

    if status == "descontinuados":
        and_conditions.append({"ativo": False})
    elif status != "todos":
        and_conditions.append({"ativo": {"$ne": False}})

    if busca and busca.strip():
        termo = re.escape(busca.strip())
        and_conditions.append(
            {
                "$or": [
                    {"codigo_original": {"$regex": termo, "$options": "i"}},
                    {"id_unico": {"$regex": termo, "$options": "i"}},
                    {"titulo": {"$regex": termo, "$options": "i"}},
                    {"bairro": {"$regex": termo, "$options": "i"}},
                    {"extras.logradouro": {"$regex": termo, "$options": "i"}},
                    {"extras.atributos": {"$regex": termo, "$options": "i"}},
                ]
            }
        )

    if cidade:
        and_conditions.append(
            {"cidade": {"$regex": f"^{re.escape(cidade.strip())}$", "$options": "i"}}
        )
    if bairro:
        and_conditions.append(
            {"bairro": {"$regex": f"^{re.escape(bairro.strip())}$", "$options": "i"}}
        )
    if tipo:
        and_conditions.append(
            {"tipo": {"$regex": f"^{re.escape(tipo.strip())}$", "$options": "i"}}
        )
    if subtipo:
        and_conditions.append(
            {
                "extras.subtipo": {
                    "$regex": f"^{re.escape(subtipo.strip())}$",
                    "$options": "i",
                }
            }
        )
    if imobiliaria:
        and_conditions.append(
            {
                "imobiliaria": {
                    "$regex": f"^{re.escape(imobiliaria.strip())}$",
                    "$options": "i",
                }
            }
        )
    if modalidade:
        and_conditions.append({"modalidade": modalidade.strip().upper()})

    if quartos_min is not None and quartos_min > 0:
        and_conditions.append({"quartos": {"$gte": quartos_min}})
    if suites_min is not None and suites_min > 0:
        and_conditions.append({"extras.suites": {"$gte": suites_min}})
    if banheiros_min is not None and banheiros_min > 0:
        and_conditions.append({"banheiros": {"$gte": banheiros_min}})
    if vagas_min is not None and vagas_min > 0:
        and_conditions.append({"vagas": {"$gte": vagas_min}})

    if preco_min is not None or preco_max is not None:
        preco_cond = {}
        if preco_min is not None and preco_min > 0:
            preco_cond["$gte"] = preco_min
        if preco_max is not None and preco_max > 0:
            preco_cond["$lte"] = preco_max
            if "$gte" not in preco_cond:
                preco_cond["$gt"] = 0
        if preco_cond:
            and_conditions.append({"preco": preco_cond})
    elif ordenar_por == "menor_preco":
        and_conditions.append({"preco": {"$gt": 0}})

    if (area_min is not None and area_min > 0) or (area_max is not None and area_max > 0):
        cond_util = {}
        cond_total = {}
        if area_min is not None and area_min > 0:
            cond_util["$gte"] = area_min
            cond_total["$gte"] = area_min
        if area_max is not None and area_max > 0:
            cond_util["$lte"] = area_max
            cond_total["$lte"] = area_max
            if "$gte" not in cond_util:
                cond_util["$gt"] = 0
                cond_total["$gt"] = 0
        and_conditions.append(
            {"$or": [{"area_util": cond_util}, {"area_total": cond_total}]}
        )

    if apenas_com_foto:
        and_conditions.append({"fotos.0": {"$exists": True}})

    if apenas_queda_preco:
        and_conditions.append(
            {
                "preco_anterior": {"$gt": 0},
                "preco": {"$gt": 0},
                "$expr": {"$gt": ["$preco_anterior", "$preco"]},
            }
        )

    query = {"$and": and_conditions} if and_conditions else {}

    total_registros = imoveis_collection.count_documents(query)

    sort_criteria = [("id_unico", pymongo.ASCENDING)]
    if ordenar_por == "menor_preco":
        sort_criteria = [("preco", pymongo.ASCENDING)]
    elif ordenar_por == "maior_preco":
        sort_criteria = [("preco", pymongo.DESCENDING)]
    elif ordenar_por == "maior_area":
        sort_criteria = [("area_util", pymongo.DESCENDING), ("area_total", pymongo.DESCENDING)]
    elif ordenar_por == "menor_area":
        sort_criteria = [("area_util", pymongo.ASCENDING), ("area_total", pymongo.ASCENDING)]
    elif ordenar_por in ("recente", "recentes"):
        sort_criteria = [("criado_em", pymongo.DESCENDING), ("last_updated", pymongo.DESCENDING)]

    cursor = imoveis_collection.find(query).sort(sort_criteria).skip(skip).limit(limit)
    dados = [converter_mongo_para_dict(doc) for doc in cursor]

    return {
        "meta": {
            "total": total_registros,
            "page": page,
            "limit": limit,
            "pages": (total_registros // limit)
            + (1 if total_registros % limit > 0 else 0),
        },
        "data": dados,
    }


@app.get("/imoveis/{id_unico}", response_model=Imovel)
def obter_detalhe_imovel(id_unico: str):
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=Error)

    imovel = imoveis_collection.find_one({"id_unico": id_unico})
    if imovel:
        return converter_mongo_para_dict(imovel)
    raise HTTPException(status_code=404, detail="Imóvel não encontrado")


@app.post("/leads/clique")
def registrar_clique_lead(req: CliqueLeadRequest):
    """
    Registra um clique/redirecionamento para o site da imobiliária,
    incrementando o contador no imóvel e salvando o evento para relatórios B2B.
    """
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=Error)

    imovel = imoveis_collection.find_one(
        {"id_unico": req.id_unico},
        {
            "id_unico": 1,
            "imobiliaria": 1,
            "codigo_original": 1,
            "titulo": 1,
            "modalidade": 1,
            "tipo": 1,
            "preco": 1,
            "cidade": 1,
            "bairro": 1,
            "_id": 0,
        },
    )
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")

    agora = datetime.now(timezone.utc)
    imoveis_collection.update_one(
        {"id_unico": req.id_unico},
        {"$inc": {"cliques": 1}},
    )

    if cliques_collection is not None:
        cliques_collection.insert_one(
            {
                **imovel,
                "origem": req.origem or "detalhes",
                "timestamp": agora,
            }
        )

    return {"status": "ok", "id_unico": req.id_unico, "imobiliaria": imovel.get("imobiliaria")}


@app.get("/leads/resumo")
def obter_resumo_leads():
    """
    Retorna o consolidado de cliques/leads gerados por imobiliária e os imóveis mais clicados.
    Ideal para comprovar geração de valor B2B para as imobiliárias parceiras.
    """
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=Error)

    por_imobiliaria = []
    total_cliques = 0

    if cliques_collection is not None:
        pipeline = [
            {
                "$group": {
                    "_id": "$imobiliaria",
                    "cliques": {"$sum": 1},
                    "ultimo_clique": {"$max": "$timestamp"},
                }
            },
            {"$sort": {"cliques": -1}},
        ]
        for row in cliques_collection.aggregate(pipeline):
            qtd = row.get("cliques", 0)
            total_cliques += qtd
            por_imobiliaria.append(
                {
                    "imobiliaria": row.get("_id") or "Não Informada",
                    "cliques": qtd,
                    "ultimo_clique": row.get("ultimo_clique"),
                }
            )

    top_imoveis = [
        converter_mongo_para_dict(doc)
        for doc in imoveis_collection.find(
            {"cliques": {"$gt": 0}},
            {
                "id_unico": 1,
                "imobiliaria": 1,
                "codigo_original": 1,
                "titulo": 1,
                "cidade": 1,
                "bairro": 1,
                "preco": 1,
                "cliques": 1,
                "_id": 0,
            },
        )
        .sort("cliques", pymongo.DESCENDING)
        .limit(15)
    ]

    return {
        "total_cliques": total_cliques,
        "por_imobiliaria": por_imobiliaria,
        "top_imoveis": top_imoveis,
    }


def _calcular_media(valores):
    return round(sum(valores) / len(valores), 2) if valores else 0.0


def _calcular_mediana(valores):
    if not valores:
        return 0.0
    ordenados = sorted(valores)
    n = len(ordenados)
    meio = n // 2
    if n % 2 == 1:
        return round(ordenados[meio], 2)
    return round((ordenados[meio - 1] + ordenados[meio]) / 2.0, 2)


@app.get("/estatisticas")
def obter_estatisticas_mercado(cidade: Optional[str] = None):
    """
    Agrega indicadores de inteligência de mercado (estoque ativo vs. absorvido,
    ticket médio, R$/m² por bairro e tipo, distribuição por faixa de preço e
    market share por imobiliária).
    """
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=Error)

    projecao = {
        "ativo": 1,
        "modalidade": 1,
        "tipo": 1,
        "preco": 1,
        "preco_anterior": 1,
        "area_util": 1,
        "area_total": 1,
        "cidade": 1,
        "bairro": 1,
        "imobiliaria": 1,
        "cliques": 1,
        "_id": 0,
    }

    todos_docs = list(imoveis_collection.find({}, projecao))

    # Contagem de imóveis ativos por cidade para popular o seletor de cidades do dashboard
    contagem_cidades = {}
    for d in todos_docs:
        if d.get("ativo") is not False:
            cid = d.get("cidade") or "São João del Rei"
            contagem_cidades[cid] = contagem_cidades.get(cid, 0) + 1

    cidades_disponiveis = [
        {"cidade": c, "ativos": qtd}
        for c, qtd in sorted(contagem_cidades.items(), key=lambda x: (-x[1], x[0]))
    ]

    # Filtra pela cidade selecionada (se informada)
    if cidade and cidade.strip():
        cid_alvo = cidade.strip().lower()
        docs = [
            d for d in todos_docs if (d.get("cidade") or "").strip().lower() == cid_alvo
        ]
    else:
        docs = todos_docs

    # Contagem de cliques por imobiliária na coleção de leads
    cliques_por_imob = {}
    if cliques_collection is not None:
        filtro_cliques = (
            {"cidade": {"$regex": f"^{re.escape(cidade.strip())}$", "$options": "i"}}
            if cidade and cidade.strip()
            else {}
        )
        for row in cliques_collection.aggregate(
            [
                {"$match": filtro_cliques},
                {"$group": {"_id": "$imobiliaria", "total": {"$sum": 1}}},
            ]
        ):
            if row.get("_id"):
                cliques_por_imob[row["_id"]] = row.get("total", 0)

    total_ativos = 0
    total_descontinuados = 0
    ativos_venda = 0
    ativos_aluguel = 0
    total_com_queda = 0
    total_cliques = sum(cliques_por_imob.values())

    precos_venda = []
    precos_aluguel = []
    m2_venda = []
    m2_aluguel = []

    tipos_agg = {}
    bairros_agg = {}
    imob_agg = {}

    faixas_venda = [
        {"faixa": "Até R$ 250 mil", "min": 0, "max": 250000, "quantidade": 0},
        {"faixa": "R$ 250 mil a 500 mil", "min": 250000, "max": 500000, "quantidade": 0},
        {"faixa": "R$ 500 mil a 1 milhão", "min": 500000, "max": 1000000, "quantidade": 0},
        {"faixa": "Acima de R$ 1 milhão", "min": 1000000, "max": float("inf"), "quantidade": 0},
    ]

    faixas_aluguel = [
        {"faixa": "Até R$ 1.200", "min": 0, "max": 1200, "quantidade": 0},
        {"faixa": "R$ 1.200 a 2.500", "min": 1200, "max": 2500, "quantidade": 0},
        {"faixa": "R$ 2.500 a 5.000", "min": 2500, "max": 5000, "quantidade": 0},
        {"faixa": "Acima de R$ 5.000", "min": 5000, "max": float("inf"), "quantidade": 0},
    ]

    for d in docs:
        ativo = d.get("ativo") is not False
        mod = (d.get("modalidade") or "VENDA").upper()
        tipo = d.get("tipo") or "Casa"
        bairro = d.get("bairro") or "Não Informado"
        cid_doc = d.get("cidade") or "São João del Rei"
        imob = d.get("imobiliaria") or "Não Informada"
        preco = float(d.get("preco") or 0.0)
        preco_ant = float(d.get("preco_anterior") or 0.0)
        area = float(d.get("area_util") or d.get("area_total") or 0.0)

        # Agregação por imobiliária (considera ativos e histórico)
        im_entry = imob_agg.setdefault(
            imob,
            {
                "imobiliaria": imob,
                "ativos": 0,
                "descontinuados": 0,
                "venda": 0,
                "aluguel": 0,
                "precos_venda": [],
                "precos_aluguel": [],
                "cliques": cliques_por_imob.get(imob, 0),
            },
        )

        # Agregação por bairro
        chave_bairro = (bairro, cid_doc)
        if bairro != "Não Informado":
            b_entry = bairros_agg.setdefault(
                chave_bairro,
                {
                    "bairro": bairro,
                    "cidade": cid_doc,
                    "ativos": 0,
                    "descontinuados": 0,
                    "venda": 0,
                    "aluguel": 0,
                    "precos_venda": [],
                    "precos_aluguel": [],
                    "m2_venda": [],
                    "m2_aluguel": [],
                },
            )
        else:
            b_entry = None

        if not ativo:
            total_descontinuados += 1
            im_entry["descontinuados"] += 1
            if b_entry:
                b_entry["descontinuados"] += 1
            continue

        # A partir daqui: apenas imóveis ATIVOS
        total_ativos += 1
        im_entry["ativos"] += 1
        if b_entry:
            b_entry["ativos"] += 1

        if preco_ant > 0 and preco > 0 and preco_ant > preco:
            total_com_queda += 1

        t_entry = tipos_agg.setdefault(
            tipo,
            {
                "tipo": tipo,
                "ativos": 0,
                "venda": 0,
                "aluguel": 0,
                "precos_venda": [],
                "precos_aluguel": [],
                "m2_venda": [],
            },
        )
        t_entry["ativos"] += 1

        if mod == "VENDA":
            ativos_venda += 1
            im_entry["venda"] += 1
            t_entry["venda"] += 1
            if b_entry:
                b_entry["venda"] += 1

            # Filtra valores realistas de venda para não distorcer médias com erros de digitação
            if 15000 <= preco <= 30000000:
                precos_venda.append(preco)
                im_entry["precos_venda"].append(preco)
                t_entry["precos_venda"].append(preco)
                if b_entry:
                    b_entry["precos_venda"].append(preco)

                for fx in faixas_venda:
                    if fx["min"] < preco <= fx["max"] or (fx["min"] == 0 and preco <= fx["max"]):
                        fx["quantidade"] += 1
                        break

                if area >= 15:
                    valor_m2 = preco / area
                    if 150 <= valor_m2 <= 25000:
                        m2_venda.append(valor_m2)
                        t_entry["m2_venda"].append(valor_m2)
                        if b_entry:
                            b_entry["m2_venda"].append(valor_m2)
        else:
            ativos_aluguel += 1
            im_entry["aluguel"] += 1
            t_entry["aluguel"] += 1
            if b_entry:
                b_entry["aluguel"] += 1

            if 150 <= preco <= 50000:
                precos_aluguel.append(preco)
                im_entry["precos_aluguel"].append(preco)
                t_entry["precos_aluguel"].append(preco)
                if b_entry:
                    b_entry["precos_aluguel"].append(preco)

                for fx in faixas_aluguel:
                    if fx["min"] < preco <= fx["max"] or (fx["min"] == 0 and preco <= fx["max"]):
                        fx["quantidade"] += 1
                        break

                if area >= 12:
                    valor_m2 = preco / area
                    if 3 <= valor_m2 <= 150:
                        m2_aluguel.append(valor_m2)
                        if b_entry:
                            b_entry["m2_aluguel"].append(valor_m2)

    # Formata lista por tipo
    lista_tipos = []
    for t in sorted(tipos_agg.values(), key=lambda x: -x["ativos"]):
        lista_tipos.append(
            {
                "tipo": t["tipo"],
                "ativos": t["ativos"],
                "venda": t["venda"],
                "aluguel": t["aluguel"],
                "percentual": round((t["ativos"] / total_ativos) * 100, 1) if total_ativos > 0 else 0.0,
                "ticket_medio_venda": _calcular_media(t["precos_venda"]),
                "ticket_medio_aluguel": _calcular_media(t["precos_aluguel"]),
                "preco_m2_venda": _calcular_media(t["m2_venda"]),
            }
        )

    # Formata lista de bairros (top 25 com pelo menos 2 imóveis ativos)
    lista_bairros = []
    for b in sorted(bairros_agg.values(), key=lambda x: -x["ativos"]):
        if b["ativos"] < 2:
            continue
        lista_bairros.append(
            {
                "bairro": b["bairro"],
                "cidade": b["cidade"],
                "ativos": b["ativos"],
                "descontinuados": b["descontinuados"],
                "venda": b["venda"],
                "aluguel": b["aluguel"],
                "ticket_medio_venda": _calcular_media(b["precos_venda"]),
                "ticket_medio_aluguel": _calcular_media(b["precos_aluguel"]),
                "preco_m2_venda": _calcular_media(b["m2_venda"]),
                "preco_m2_aluguel": _calcular_media(b["m2_aluguel"]),
            }
        )

    # Formata lista de imobiliárias (apenas as que possuem anúncios ativos)
    lista_imobiliarias = []
    for im in sorted(imob_agg.values(), key=lambda x: -x["ativos"]):
        if im["ativos"] == 0:
            continue
        lista_imobiliarias.append(
            {
                "imobiliaria": im["imobiliaria"],
                "ativos": im["ativos"],
                "descontinuados": im["descontinuados"],
                "venda": im["venda"],
                "aluguel": im["aluguel"],
                "market_share_pct": round((im["ativos"] / total_ativos) * 100, 1)
                if total_ativos > 0
                else 0.0,
                "ticket_medio_venda": _calcular_media(im["precos_venda"]),
                "ticket_medio_aluguel": _calcular_media(im["precos_aluguel"]),
                "cliques": im["cliques"],
            }
        )

    total_geral = total_ativos + total_descontinuados

    return {
        "cidade_selecionada": cidade or "Todas",
        "cidades_disponiveis": cidades_disponiveis,
        "resumo_geral": {
            "total_ativos": total_ativos,
            "total_descontinuados": total_descontinuados,
            "total_geral": total_geral,
            "taxa_absorcao_pct": round((total_descontinuados / total_geral) * 100, 1)
            if total_geral > 0
            else 0.0,
            "ativos_venda": ativos_venda,
            "ativos_aluguel": ativos_aluguel,
            "ticket_medio_venda": _calcular_media(precos_venda),
            "mediana_venda": _calcular_mediana(precos_venda),
            "ticket_medio_aluguel": _calcular_media(precos_aluguel),
            "mediana_aluguel": _calcular_mediana(precos_aluguel),
            "preco_m2_venda": _calcular_media(m2_venda),
            "preco_m2_aluguel": _calcular_media(m2_aluguel),
            "total_imobiliarias_ativas": len(lista_imobiliarias),
            "total_cliques": total_cliques,
            "total_com_queda_preco": total_com_queda,
        },
        "por_tipo": lista_tipos,
        "por_bairro": lista_bairros[:30],
        "por_imobiliaria": lista_imobiliarias,
        "faixas_venda": [
            {"faixa": f["faixa"], "quantidade": f["quantidade"]} for f in faixas_venda
        ],
        "faixas_aluguel": [
            {"faixa": f["faixa"], "quantidade": f["quantidade"]} for f in faixas_aluguel
        ],
    }


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)