import re
from datetime import datetime, timezone
from typing import Optional, Annotated, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import pymongo

try:
    from database import imoveis_collection, cliques_collection, corretores_collection
    from models import (
        Imovel,
        CliqueLeadRequest,
        LoginCorretorRequest,
        AtualizarPerfilCorretorRequest,
        SalvarImovelCorretorRequest,
        StatusImovelCorretorRequest,
        ImpulsionarImovelRequest,
    )
    from auth import (
        gerar_hash_senha,
        verificar_senha,
        gerar_token_acesso,
        serializar_corretor_publico,
        obter_corretor_atual,
    )
    from foto_utils import normalizar_url_foto
    from corretor_service import (
        construir_filtro_carteira_corretor,
        verificar_permissao_imovel,
        montar_documento_novo_imovel,
        montar_atualizacao_imovel,
        aplicar_impulsionamento_imovel,
        remover_impulsionamento_imovel,
        calcular_metricas_carteira,
    )
except ImportError:
    from backend.database import imoveis_collection, cliques_collection, corretores_collection
    from backend.models import (
        Imovel,
        CliqueLeadRequest,
        LoginCorretorRequest,
        AtualizarPerfilCorretorRequest,
        SalvarImovelCorretorRequest,
        StatusImovelCorretorRequest,
        ImpulsionarImovelRequest,
    )
    from backend.auth import (
        gerar_hash_senha,
        verificar_senha,
        gerar_token_acesso,
        serializar_corretor_publico,
        obter_corretor_atual,
    )
    from backend.foto_utils import normalizar_url_foto
    from backend.corretor_service import (
        construir_filtro_carteira_corretor,
        verificar_permissao_imovel,
        montar_documento_novo_imovel,
        montar_atualizacao_imovel,
        aplicar_impulsionamento_imovel,
        remover_impulsionamento_imovel,
        calcular_metricas_carteira,
    )

ERROR_DB = "Banco não conectado"
ERRO_IMOVEL_NAO_ENCONTRADO = "Imóvel não encontrado"
BAIRRO_NAO_INFORMADO = "Não Informado"
CIDADE_PADRAO = "São João del Rei"
SUBTIPO_PADRAO = "Padrão"
MONGO_REGEX = "$regex"
MONGO_OPTIONS = "$options"
MONGO_EXISTS = "$exists"

DESC_ERRO_500 = "Erro interno no servidor ou banco desconectado"
RESPONSES_500 = {500: {"description": DESC_ERRO_500}}
RESPONSES_401_500 = {
    401: {"description": "Não autenticado ou credenciais inválidas"},
    500: {"description": DESC_ERRO_500},
}
RESPONSES_400_401_500 = {
    400: {"description": "Dados de entrada inválidos"},
    401: {"description": "Não autenticado ou senha atual incorreta"},
    500: {"description": DESC_ERRO_500},
}
RESPONSES_404_500 = {
    404: {"description": ERRO_IMOVEL_NAO_ENCONTRADO},
    500: {"description": DESC_ERRO_500},
}

app = FastAPI(title="API Imóveis Unificada", version="1.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _converter_destaque_ate(ate: Any) -> Optional[datetime]:
    if isinstance(ate, str):
        try:
            return datetime.fromisoformat(ate.replace("Z", "+00:00"))
        except ValueError:
            return None
    if isinstance(ate, datetime):
        return ate.replace(tzinfo=timezone.utc) if ate.tzinfo is None else ate
    return None


def converter_mongo_para_dict(imovel: Dict[str, Any]) -> Dict[str, Any]:
    if "_id" in imovel:
        del imovel["_id"]
    if imovel.get("destaque") and imovel.get("destaque_ate"):
        ate_dt = _converter_destaque_ate(imovel["destaque_ate"])
        if ate_dt and ate_dt < datetime.now(timezone.utc):
            imovel["destaque"] = False
    fotos = imovel.get("fotos")
    if isinstance(fotos, list):
        imovel["fotos"] = [normalizar_url_foto(f) for f in fotos if f]
    return imovel


def _obter_filtro_status(status: str) -> Dict[str, Any]:
    if status == "descontinuados":
        return {"ativo": False}
    if status != "todos":
        return {"ativo": {"$ne": False}}
    return {}


def _acumular_item_filtro(
    d: Dict[str, Any],
    cidades_set: set,
    bairros_set: set,
    bairros_por_cidade: Dict[str, set],
    tipos_set: set,
    subtipos_set: set,
    subtipos_por_tipo: Dict[str, set],
    imobiliarias_set: set,
) -> None:
    cid = d.get("cidade")
    bai = d.get("bairro")
    tip = d.get("tipo")
    sub = (d.get("extras") or {}).get("subtipo")
    imo = d.get("imobiliaria")

    bai_valido = bool(bai and bai != BAIRRO_NAO_INFORMADO)
    sub_valido = bool(sub and sub != SUBTIPO_PADRAO)

    if cid:
        cidades_set.add(cid)
        if bai_valido:
            bairros_por_cidade.setdefault(cid, set()).add(bai)
    if bai_valido:
        bairros_set.add(bai)
    if tip:
        tipos_set.add(tip)
        if sub_valido:
            subtipos_por_tipo.setdefault(tip, set()).add(sub)
    if sub_valido:
        subtipos_set.add(sub)
    if imo:
        imobiliarias_set.add(imo)


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


@app.get("/filtros", responses=RESPONSES_500)
def obter_opcoes_filtro(
    status: Annotated[str, Query(pattern="^(ativos|descontinuados|todos)$")] = "ativos",
):
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

    filtro_base = _obter_filtro_status(status)

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

        cidades_set, bairros_set, tipos_set, subtipos_set, imobiliarias_set = (
            set(),
            set(),
            set(),
            set(),
            set(),
        )
        bairros_por_cidade: Dict[str, set] = {}
        subtipos_por_tipo: Dict[str, set] = {}

        for d in docs:
            _acumular_item_filtro(
                d,
                cidades_set,
                bairros_set,
                bairros_por_cidade,
                tipos_set,
                subtipos_set,
                subtipos_por_tipo,
                imobiliarias_set,
            )

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


class FiltrosImoveisQuery(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, le=100)
    busca: Optional[str] = None
    cidade: Optional[str] = None
    bairro: Optional[str] = None
    modalidade: Optional[str] = None
    tipo: Optional[str] = None
    subtipo: Optional[str] = None
    imobiliaria: Optional[str] = None
    quartos_min: Optional[int] = None
    suites_min: Optional[int] = None
    banheiros_min: Optional[int] = None
    vagas_min: Optional[int] = None
    preco_min: Optional[float] = None
    preco_max: Optional[float] = None
    area_min: Optional[float] = None
    area_max: Optional[float] = None
    apenas_com_foto: Optional[bool] = None
    apenas_queda_preco: Optional[bool] = None
    apenas_destaque: Optional[bool] = None
    ordenar_por: Optional[str] = Field(
        None,
        pattern="^(relevancia|mais_relevantes|relevantes|menor_preco|maior_preco|maior_area|menor_area|recentes?|preco_asc|area_desc)?$",
    )
    status: str = Field("ativos", pattern="^(ativos|descontinuados|todos)$")


def _regex_exato(valor: str) -> Dict[str, str]:
    return {MONGO_REGEX: f"^{re.escape(valor.strip())}$", MONGO_OPTIONS: "i"}


def _regex_lista_exata(valor: str) -> Dict[str, str]:
    itens = [re.escape(item.strip()) for item in valor.split(",") if item.strip()]
    if not itens:
        return _regex_exato(valor)
    padrao = "|".join(itens)
    return {MONGO_REGEX: f"^({padrao})$", MONGO_OPTIONS: "i"}


def _adicionar_filtros_texto(params: FiltrosImoveisQuery, conds: List[Dict[str, Any]]) -> None:
    if params.busca and params.busca.strip():
        termo = re.escape(params.busca.strip())
        campos_busca = (
            "codigo_original",
            "id_unico",
            "titulo",
            "bairro",
            "extras.logradouro",
            "extras.atributos",
        )
        conds.append(
            {"$or": [{c: {MONGO_REGEX: termo, MONGO_OPTIONS: "i"}} for c in campos_busca]}
        )

    mapeamento_exato = (
        ("cidade", params.cidade),
        ("bairro", params.bairro),
        ("imobiliaria", params.imobiliaria),
    )
    for campo, valor in mapeamento_exato:
        if valor:
            conds.append({campo: _regex_exato(valor)})

    mapeamento_multiplo = (
        ("tipo", params.tipo),
        ("extras.subtipo", params.subtipo),
    )
    for campo, valor in mapeamento_multiplo:
        if valor:
            conds.append({campo: _regex_lista_exata(valor)})

    if params.modalidade:
        conds.append({"modalidade": params.modalidade.strip().upper()})


def _adicionar_filtros_quantitativos(
    params: FiltrosImoveisQuery, conds: List[Dict[str, Any]]
) -> None:
    mapeamento_min = (
        ("quartos", params.quartos_min),
        ("extras.suites", params.suites_min),
        ("banheiros", params.banheiros_min),
        ("vagas", params.vagas_min),
    )
    for campo, valor in mapeamento_min:
        if valor is not None and valor > 0:
            conds.append({campo: {"$gte": valor}})


def _adicionar_filtro_preco(params: FiltrosImoveisQuery, conds: List[Dict[str, Any]]) -> None:
    if params.preco_min is None and params.preco_max is None:
        if params.ordenar_por in ("menor_preco", "preco_asc"):
            conds.append({"preco": {"$gt": 0}})
        return

    preco_cond: Dict[str, Any] = {}
    if params.preco_min is not None and params.preco_min > 0:
        preco_cond["$gte"] = params.preco_min
    if params.preco_max is not None and params.preco_max > 0:
        preco_cond["$lte"] = params.preco_max
        if "$gte" not in preco_cond:
            preco_cond["$gt"] = 0
    if preco_cond:
        conds.append({"preco": preco_cond})


def _adicionar_filtro_area(params: FiltrosImoveisQuery, conds: List[Dict[str, Any]]) -> None:
    tem_min = params.area_min is not None and params.area_min > 0
    tem_max = params.area_max is not None and params.area_max > 0
    if not tem_min and not tem_max:
        return

    cond_area: Dict[str, Any] = {}
    if tem_min:
        cond_area["$gte"] = params.area_min
    if tem_max:
        cond_area["$lte"] = params.area_max
        if not tem_min:
            cond_area["$gt"] = 0

    conds.append({"$or": [{"area_util": dict(cond_area)}, {"area_total": dict(cond_area)}]})


def _construir_query_imoveis(params: FiltrosImoveisQuery) -> Dict[str, Any]:
    conds: List[Dict[str, Any]] = []
    filtro_status = _obter_filtro_status(params.status)
    if filtro_status:
        conds.append(filtro_status)

    _adicionar_filtros_texto(params, conds)
    _adicionar_filtros_quantitativos(params, conds)
    _adicionar_filtro_preco(params, conds)
    _adicionar_filtro_area(params, conds)

    if params.apenas_com_foto:
        conds.append({"fotos.0": {MONGO_EXISTS: True}})

    if params.apenas_queda_preco:
        conds.append(
            {
                "preco_anterior": {"$gt": 0},
                "preco": {"$gt": 0},
                "$expr": {"$gt": ["$preco_anterior", "$preco"]},
            }
        )

    if params.apenas_destaque:
        agora = datetime.now(timezone.utc)
        conds.append(
            {
                "destaque": True,
                "$or": [
                    {"destaque_ate": None},
                    {"destaque_ate": {"$gte": agora}},
                ],
            }
        )

    conds.append({"excluido": {"$ne": True}})

    return {"$and": conds} if conds else {}


CRITERIO_RELEVANCIA = [
    ("destaque", pymongo.DESCENDING),
    ("cliques", pymongo.DESCENDING),
    ("criado_em", pymongo.DESCENDING),
    ("last_updated", pymongo.DESCENDING),
]

SORT_CRITERIA_MAP = {
    "": CRITERIO_RELEVANCIA,
    "relevancia": CRITERIO_RELEVANCIA,
    "mais_relevantes": CRITERIO_RELEVANCIA,
    "relevantes": CRITERIO_RELEVANCIA,
    "menor_preco": [("preco", pymongo.ASCENDING)],
    "preco_asc": [("preco", pymongo.ASCENDING)],
    "maior_preco": [("preco", pymongo.DESCENDING)],
    "maior_area": [("area_util", pymongo.DESCENDING), ("area_total", pymongo.DESCENDING)],
    "area_desc": [("area_util", pymongo.DESCENDING), ("area_total", pymongo.DESCENDING)],
    "menor_area": [("area_util", pymongo.ASCENDING), ("area_total", pymongo.ASCENDING)],
    "recente": [("criado_em", pymongo.DESCENDING), ("last_updated", pymongo.DESCENDING)],
    "recentes": [("criado_em", pymongo.DESCENDING), ("last_updated", pymongo.DESCENDING)],
}


@app.get("/imoveis", responses=RESPONSES_500)
def listar_imoveis(params: Annotated[FiltrosImoveisQuery, Query()]):
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

    skip = (params.page - 1) * params.limit
    query = _construir_query_imoveis(params)
    total_registros = imoveis_collection.count_documents(query)

    sort_criteria = SORT_CRITERIA_MAP.get(params.ordenar_por or "", CRITERIO_RELEVANCIA)
    cursor = imoveis_collection.find(query).sort(sort_criteria).skip(skip).limit(params.limit)
    dados = [converter_mongo_para_dict(doc) for doc in cursor]

    return {
        "meta": {
            "total": total_registros,
            "page": params.page,
            "limit": params.limit,
            "pages": (total_registros // params.limit)
            + (1 if total_registros % params.limit > 0 else 0),
        },
        "data": dados,
    }


@app.get("/imoveis/{id_unico}", response_model=Imovel, responses=RESPONSES_404_500)
def obter_detalhe_imovel(id_unico: str):
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

    imovel = imoveis_collection.find_one({"id_unico": id_unico})
    if imovel:
        return converter_mongo_para_dict(imovel)
    raise HTTPException(status_code=404, detail=ERRO_IMOVEL_NAO_ENCONTRADO)


@app.post("/leads/clique", responses=RESPONSES_404_500)
def registrar_clique_lead(req: CliqueLeadRequest):
    """
    Registra um clique/redirecionamento para o site da imobiliária,
    incrementando o contador no imóvel e salvando o evento para relatórios B2B.
    """
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

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
        raise HTTPException(status_code=404, detail=ERRO_IMOVEL_NAO_ENCONTRADO)

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


@app.get("/leads/resumo", responses=RESPONSES_500)
def obter_resumo_leads():
    """
    Retorna o consolidado de cliques/leads gerados por imobiliária e os imóveis mais clicados.
    """
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

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


def _incrementar_faixa_preco(faixas: List[Dict[str, Any]], preco: float) -> None:
    for fx in faixas:
        if fx["min"] < preco <= fx["max"] or (fx["min"] == 0 and preco <= fx["max"]):
            fx["quantidade"] += 1
            return


def _obter_cidades_disponiveis(todos_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    contagem_cidades: Dict[str, int] = {}
    for d in todos_docs:
        if d.get("ativo") is not False:
            cid = d.get("cidade") or CIDADE_PADRAO
            contagem_cidades[cid] = contagem_cidades.get(cid, 0) + 1
    return [
        {"cidade": c, "ativos": qtd}
        for c, qtd in sorted(contagem_cidades.items(), key=lambda x: (-x[1], x[0]))
    ]


def _obter_cliques_por_imobiliaria(cidade: Optional[str]) -> Dict[str, int]:
    if cliques_collection is None:
        return {}
    filtro_cliques = (
        {"cidade": _regex_exato(cidade)}
        if cidade and cidade.strip()
        else {}
    )
    resultado: Dict[str, int] = {}
    for row in cliques_collection.aggregate(
        [
            {"$match": filtro_cliques},
            {"$group": {"_id": "$imobiliaria", "total": {"$sum": 1}}},
        ]
    ):
        if row.get("_id"):
            resultado[row["_id"]] = row.get("total", 0)
    return resultado


def _registrar_metricas_venda(
    preco: float,
    area: float,
    im_entry: Dict[str, Any],
    t_entry: Dict[str, Any],
    b_entry: Optional[Dict[str, Any]],
    estado: Dict[str, Any],
) -> None:
    estado["ativos_venda"] += 1
    im_entry["venda"] += 1
    t_entry["venda"] += 1
    if b_entry:
        b_entry["venda"] += 1

    if not (15000 <= preco <= 30000000):
        return

    estado["precos_venda"].append(preco)
    im_entry["precos_venda"].append(preco)
    t_entry["precos_venda"].append(preco)
    if b_entry:
        b_entry["precos_venda"].append(preco)

    _incrementar_faixa_preco(estado["faixas_venda"], preco)

    if area >= 15:
        valor_m2 = preco / area
        if 150 <= valor_m2 <= 25000:
            estado["m2_venda"].append(valor_m2)
            t_entry["m2_venda"].append(valor_m2)
            if b_entry:
                b_entry["m2_venda"].append(valor_m2)


def _registrar_metricas_aluguel(
    preco: float,
    area: float,
    im_entry: Dict[str, Any],
    t_entry: Dict[str, Any],
    b_entry: Optional[Dict[str, Any]],
    estado: Dict[str, Any],
) -> None:
    estado["ativos_aluguel"] += 1
    im_entry["aluguel"] += 1
    t_entry["aluguel"] += 1
    if b_entry:
        b_entry["aluguel"] += 1

    if not (150 <= preco <= 50000):
        return

    estado["precos_aluguel"].append(preco)
    im_entry["precos_aluguel"].append(preco)
    t_entry["precos_aluguel"].append(preco)
    if b_entry:
        b_entry["precos_aluguel"].append(preco)

    _incrementar_faixa_preco(estado["faixas_aluguel"], preco)

    if area >= 12:
        valor_m2 = preco / area
        if 3 <= valor_m2 <= 150:
            estado["m2_aluguel"].append(valor_m2)
            if b_entry:
                b_entry["m2_aluguel"].append(valor_m2)


def _obter_ou_criar_entradas_agregacao(
    imob: str,
    bairro: str,
    cid_doc: str,
    cliques_por_imob: Dict[str, int],
    estado: Dict[str, Any],
):
    im_entry = estado["imob_agg"].setdefault(
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

    b_entry = None
    if bairro != BAIRRO_NAO_INFORMADO:
        b_entry = estado["bairros_agg"].setdefault(
            (bairro, cid_doc),
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
    return im_entry, b_entry


def _extrair_campos_doc_estatistica(d: Dict[str, Any]):
    ativo = d.get("ativo") is not False
    mod = (d.get("modalidade") or "VENDA").upper()
    tipo = d.get("tipo") or "Casa"
    bairro = d.get("bairro") or BAIRRO_NAO_INFORMADO
    cid_doc = d.get("cidade") or CIDADE_PADRAO
    imob = d.get("imobiliaria") or "Não Informada"
    preco = float(d.get("preco") or 0.0)
    preco_ant = float(d.get("preco_anterior") or 0.0)
    area = float(d.get("area_util") or d.get("area_total") or 0.0)
    return ativo, mod, tipo, bairro, cid_doc, imob, preco, preco_ant, area


def _processar_documento_estatistica(
    d: Dict[str, Any],
    cliques_por_imob: Dict[str, int],
    estado: Dict[str, Any],
) -> None:
    ativo, mod, tipo, bairro, cid_doc, imob, preco, preco_ant, area = (
        _extrair_campos_doc_estatistica(d)
    )

    im_entry, b_entry = _obter_ou_criar_entradas_agregacao(
        imob, bairro, cid_doc, cliques_por_imob, estado
    )

    if not ativo:
        estado["total_descontinuados"] += 1
        im_entry["descontinuados"] += 1
        if b_entry:
            b_entry["descontinuados"] += 1
        return

    estado["total_ativos"] += 1
    im_entry["ativos"] += 1
    if b_entry:
        b_entry["ativos"] += 1

    if 0 < preco < preco_ant:
        estado["total_com_queda"] += 1

    t_entry = estado["tipos_agg"].setdefault(
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
        _registrar_metricas_venda(preco, area, im_entry, t_entry, b_entry, estado)
    else:
        _registrar_metricas_aluguel(preco, area, im_entry, t_entry, b_entry, estado)


def _formatar_listas_estatisticas(estado: Dict[str, Any]):
    total_ativos = estado["total_ativos"]

    lista_tipos = [
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
        for t in sorted(estado["tipos_agg"].values(), key=lambda x: -x["ativos"])
    ]

    lista_bairros = [
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
        for b in sorted(estado["bairros_agg"].values(), key=lambda x: -x["ativos"])
        if b["ativos"] >= 2
    ]

    lista_imobiliarias = [
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
        for im in sorted(estado["imob_agg"].values(), key=lambda x: -x["ativos"])
        if im["ativos"] > 0
    ]

    return lista_tipos, lista_bairros, lista_imobiliarias


@app.get("/estatisticas", responses=RESPONSES_401_500)
def obter_estatisticas_mercado(
    _corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
    cidade: Optional[str] = None,
):
    """
    Agrega indicadores de inteligência de mercado (estoque ativo vs. absorvido,
    ticket médio, R$/m² por bairro e tipo, distribuição por faixa de preço e
    market share por imobiliária). Uso exclusivo para corretores autenticados.
    """
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

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
    cidades_disponiveis = _obter_cidades_disponiveis(todos_docs)

    if cidade and cidade.strip():
        cid_alvo = cidade.strip().lower()
        docs = [d for d in todos_docs if (d.get("cidade") or "").strip().lower() == cid_alvo]
    else:
        docs = todos_docs

    cliques_por_imob = _obter_cliques_por_imobiliaria(cidade)

    estado: Dict[str, Any] = {
        "total_ativos": 0,
        "total_descontinuados": 0,
        "ativos_venda": 0,
        "ativos_aluguel": 0,
        "total_com_queda": 0,
        "precos_venda": [],
        "precos_aluguel": [],
        "m2_venda": [],
        "m2_aluguel": [],
        "tipos_agg": {},
        "bairros_agg": {},
        "imob_agg": {},
        "faixas_venda": [
            {"faixa": "Até R$ 250 mil", "min": 0, "max": 250000, "quantidade": 0},
            {"faixa": "R$ 250 mil a 500 mil", "min": 250000, "max": 500000, "quantidade": 0},
            {"faixa": "R$ 500 mil a 1 milhão", "min": 500000, "max": 1000000, "quantidade": 0},
            {"faixa": "Acima de R$ 1 milhão", "min": 1000000, "max": float("inf"), "quantidade": 0},
        ],
        "faixas_aluguel": [
            {"faixa": "Até R$ 1.200", "min": 0, "max": 1200, "quantidade": 0},
            {"faixa": "R$ 1.200 a 2.500", "min": 1200, "max": 2500, "quantidade": 0},
            {"faixa": "R$ 2.500 a 5.000", "min": 2500, "max": 5000, "quantidade": 0},
            {"faixa": "Acima de R$ 5.000", "min": 5000, "max": float("inf"), "quantidade": 0},
        ],
    }

    for d in docs:
        _processar_documento_estatistica(d, cliques_por_imob, estado)

    lista_tipos, lista_bairros, lista_imobiliarias = _formatar_listas_estatisticas(estado)
    total_ativos = estado["total_ativos"]
    total_descontinuados = estado["total_descontinuados"]
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
            "ativos_venda": estado["ativos_venda"],
            "ativos_aluguel": estado["ativos_aluguel"],
            "ticket_medio_venda": _calcular_media(estado["precos_venda"]),
            "mediana_venda": _calcular_mediana(estado["precos_venda"]),
            "ticket_medio_aluguel": _calcular_media(estado["precos_aluguel"]),
            "mediana_aluguel": _calcular_mediana(estado["precos_aluguel"]),
            "preco_m2_venda": _calcular_media(estado["m2_venda"]),
            "preco_m2_aluguel": _calcular_media(estado["m2_aluguel"]),
            "total_imobiliarias_ativas": len(lista_imobiliarias),
            "total_cliques": sum(cliques_por_imob.values()),
            "total_com_queda_preco": estado["total_com_queda"],
        },
        "por_tipo": lista_tipos,
        "por_bairro": lista_bairros[:30],
        "por_imobiliaria": lista_imobiliarias,
        "faixas_venda": [
            {"faixa": f["faixa"], "quantidade": f["quantidade"]}
            for f in estado["faixas_venda"]
        ],
        "faixas_aluguel": [
            {"faixa": f["faixa"], "quantidade": f["quantidade"]}
            for f in estado["faixas_aluguel"]
        ],
    }


def _calcular_resumo_parceiro(nome_imobiliaria: str) -> Dict[str, int]:
    if imoveis_collection is None or not nome_imobiliaria:
        return {"imoveis_ativos": 0, "imoveis_inativos": 0, "cliques_totais": 0}

    padrao_imob = f"^{re.escape(nome_imobiliaria.strip())}$"
    docs = list(
        imoveis_collection.find(
            {"imobiliaria": {MONGO_REGEX: padrao_imob, MONGO_OPTIONS: "i"}},
            {"ativo": 1, "cliques": 1, "_id": 0},
        )
    )
    ativos = sum(1 for d in docs if d.get("ativo") is not False)
    inativos = len(docs) - ativos
    cliques_imoveis = sum(int(d.get("cliques") or 0) for d in docs)

    cliques_log = 0
    if cliques_collection is not None:
        cliques_log = cliques_collection.count_documents(
            {"imobiliaria": {MONGO_REGEX: padrao_imob, MONGO_OPTIONS: "i"}}
        )

    return {
        "imoveis_ativos": ativos,
        "imoveis_inativos": inativos,
        "cliques_totais": max(cliques_imoveis, cliques_log),
    }


@app.post("/auth/login", responses=RESPONSES_401_500)
def login_corretor(credenciais: LoginCorretorRequest):
    if corretores_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

    usuario_limpo = credenciais.usuario.strip().lower()
    doc = corretores_collection.find_one({"usuario": usuario_limpo})

    if not doc or not verificar_senha(credenciais.senha, doc.get("senha_hash", "")):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos.",
        )

    if doc.get("ativo") is False:
        raise HTTPException(
            status_code=401,
            detail="Sua conta está temporariamente suspensa. Entre em contato com o suporte.",
        )

    agora = datetime.now(timezone.utc)
    corretores_collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"ultimo_login": agora}},
    )
    doc["ultimo_login"] = agora

    token = gerar_token_acesso(doc)
    perfil = serializar_corretor_publico(doc)
    resumo = _calcular_resumo_parceiro(perfil["imobiliaria"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "corretor": perfil,
        "resumo_conta": resumo,
    }


@app.get("/auth/me", responses=RESPONSES_401_500)
def obter_meu_perfil(
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    perfil = serializar_corretor_publico(corretor_atual)
    resumo = _calcular_resumo_parceiro(perfil["imobiliaria"])
    return {
        "corretor": perfil,
        "resumo_conta": resumo,
    }


def _montar_campos_atualizacao_perfil(
    dados: AtualizarPerfilCorretorRequest,
    corretor_atual: Dict[str, Any],
) -> Dict[str, Any]:
    campos_set: Dict[str, Any] = {}
    for nome_campo in ("nome", "telefone", "whatsapp", "email", "creci", "site_externo"):
        valor = getattr(dados, nome_campo, None)
        if valor is not None:
            campos_set[nome_campo] = valor.strip()

    if dados.nova_senha:
        if not dados.senha_atual or not verificar_senha(
            dados.senha_atual, corretor_atual.get("senha_hash", "")
        ):
            raise HTTPException(
                status_code=401,
                detail="A senha atual informada está incorreta.",
            )
        campos_set["senha_hash"] = gerar_hash_senha(dados.nova_senha)

    return campos_set


@app.put("/auth/perfil", responses=RESPONSES_400_401_500)
def atualizar_perfil_corretor(
    dados: AtualizarPerfilCorretorRequest,
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    if corretores_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

    campos_set = _montar_campos_atualizacao_perfil(dados, corretor_atual)
    if not campos_set:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    campos_set["atualizado_em"] = datetime.now(timezone.utc)
    corretores_collection.update_one(
        {"_id": corretor_atual["_id"]},
        {"$set": campos_set},
    )

    doc_atualizado = corretores_collection.find_one({"_id": corretor_atual["_id"]}) or corretor_atual
    return {
        "mensagem": "Perfil atualizado com sucesso.",
        "corretor": serializar_corretor_publico(doc_atualizado),
    }


RESPONSES_CORRETOR_IMOVEL = {
    400: {"description": "Dados inválidos ou código já existente"},
    401: {"description": "Não autenticado"},
    403: {"description": "Sem permissão para alterar este imóvel"},
    404: {"description": ERRO_IMOVEL_NAO_ENCONTRADO},
    500: {"description": DESC_ERRO_500},
}


def _obter_imovel_do_corretor_ou_erro(id_unico: str, corretor_atual: Dict[str, Any]) -> Dict[str, Any]:
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)
    doc = imoveis_collection.find_one({"id_unico": id_unico})
    if not doc:
        raise HTTPException(status_code=404, detail=ERRO_IMOVEL_NAO_ENCONTRADO)
    if not verificar_permissao_imovel(doc, corretor_atual):
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para modificar este imóvel.",
        )
    return doc


@app.get("/corretor/imoveis", responses=RESPONSES_401_500)
def listar_meus_imoveis(
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

    filtro = construir_filtro_carteira_corretor(corretor_atual)
    cursor = imoveis_collection.find(filtro, {"_id": 0}).sort(
        [("ativo", pymongo.DESCENDING), ("last_updated", pymongo.DESCENDING)]
    )
    lista = list(cursor)
    return {
        "total": len(lista),
        "data": lista,
    }


@app.post("/corretor/imoveis", responses=RESPONSES_CORRETOR_IMOVEL)
def cadastrar_imovel_corretor(
    dados: SalvarImovelCorretorRequest,
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

    novo_doc = montar_documento_novo_imovel(dados, corretor_atual)
    if imoveis_collection.find_one({"id_unico": novo_doc["id_unico"]}):
        raise HTTPException(
            status_code=400,
            detail=f"Já existe um imóvel cadastrado com o código '{novo_doc['codigo_original']}'.",
        )

    imoveis_collection.insert_one(novo_doc)
    converter_mongo_para_dict(novo_doc)
    return {
        "mensagem": "Imóvel cadastrado com sucesso!",
        "imovel": novo_doc,
    }


@app.put("/corretor/imoveis/{id_unico}", responses=RESPONSES_CORRETOR_IMOVEL)
def editar_imovel_corretor(
    id_unico: str,
    dados: SalvarImovelCorretorRequest,
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    doc_existente = _obter_imovel_do_corretor_ou_erro(id_unico, corretor_atual)
    campos_atualizados = montar_atualizacao_imovel(doc_existente, dados, corretor_atual)

    imoveis_collection.update_one(
        {"id_unico": id_unico},
        {"$set": campos_atualizados},
    )
    doc_final = imoveis_collection.find_one({"id_unico": id_unico}, {"_id": 0})
    return {
        "mensagem": "Imóvel atualizado com sucesso!",
        "imovel": doc_final,
    }


@app.patch("/corretor/imoveis/{id_unico}/status", responses=RESPONSES_CORRETOR_IMOVEL)
def alterar_status_imovel_corretor(
    id_unico: str,
    dados: StatusImovelCorretorRequest,
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    _obter_imovel_do_corretor_ou_erro(id_unico, corretor_atual)
    agora = datetime.now(timezone.utc)
    campos_set: Dict[str, Any] = {
        "ativo": bool(dados.ativo),
        "last_updated": agora,
        "descontinuado_em": None if dados.ativo else agora,
    }
    if dados.ativo:
        campos_set["excluido"] = False
        campos_set["removido_em"] = None
    imoveis_collection.update_one(
        {"id_unico": id_unico},
        {"$set": campos_set},
    )
    doc_final = imoveis_collection.find_one({"id_unico": id_unico}, {"_id": 0})
    if doc_final:
        converter_mongo_para_dict(doc_final)
    return {
        "mensagem": "Status do imóvel atualizado com sucesso!",
        "imovel": doc_final,
    }


@app.post("/corretor/imoveis/{id_unico}/reativar", responses=RESPONSES_CORRETOR_IMOVEL)
def reativar_imovel_corretor(
    id_unico: str,
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    """
    Reativa um imóvel arquivado ou pausado para a vitrine pública,
    permitindo que aluguéis que voltaram a ficar vagos ou imóveis relistados fiquem ativos.
    """
    _obter_imovel_do_corretor_ou_erro(id_unico, corretor_atual)
    agora = datetime.now(timezone.utc)
    campos_reativar = {
        "ativo": True,
        "excluido": False,
        "removido_em": None,
        "descontinuado_em": None,
        "last_updated": agora,
    }
    imoveis_collection.update_one(
        {"id_unico": id_unico},
        {"$set": campos_reativar},
    )
    doc_final = imoveis_collection.find_one({"id_unico": id_unico}, {"_id": 0})
    if doc_final:
        converter_mongo_para_dict(doc_final)
    return {
        "mensagem": "Imóvel reativado com sucesso na vitrine pública!",
        "imovel": doc_final,
    }


@app.delete("/corretor/imoveis/{id_unico}", responses=RESPONSES_CORRETOR_IMOVEL)
def excluir_imovel_corretor(
    id_unico: str,
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    """
    Exclusão lógica (Soft Delete): move o imóvel para o histórico de arquivados,
    preservando permanentemente a contagem de cliques/leads e permitindo reativação futura.
    """
    _obter_imovel_do_corretor_ou_erro(id_unico, corretor_atual)
    agora = datetime.now(timezone.utc)
    campos_arquivar = {
        "ativo": False,
        "excluido": True,
        "destaque": False,
        "destaque_ate": None,
        "removido_em": agora,
        "descontinuado_em": agora,
        "last_updated": agora,
    }
    imoveis_collection.update_one(
        {"id_unico": id_unico},
        {"$set": campos_arquivar},
    )
    doc_final = imoveis_collection.find_one({"id_unico": id_unico}, {"_id": 0})
    if doc_final:
        converter_mongo_para_dict(doc_final)
    return {
        "mensagem": "Imóvel movido para o histórico de arquivados. O histórico de cliques e leads foi preservado e você pode reativá-lo a qualquer momento.",
        "imovel": doc_final,
    }


@app.get("/corretor/metricas", responses=RESPONSES_401_500)
def obter_metricas_carteira_corretor(
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    """
    Retorna métricas consolidadas da carteira do corretor:
    total de imóveis, ativos, pausados, impulsionados, total de cliques acumulados e top imóveis.
    """
    if imoveis_collection is None:
        raise HTTPException(status_code=500, detail=ERROR_DB)

    filtro = construir_filtro_carteira_corretor(corretor_atual)
    cursor = imoveis_collection.find(filtro, {"_id": 0})
    imoveis = list(cursor)
    return calcular_metricas_carteira(imoveis)


@app.post("/corretor/imoveis/{id_unico}/impulsionar", responses=RESPONSES_CORRETOR_IMOVEL)
def impulsionar_imovel_corretor(
    id_unico: str,
    req: ImpulsionarImovelRequest,
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    """
    Ativa o destaque/impulsionamento do imóvel do corretor por determinado número de dias.
    Imóveis em destaque aparecem prioritariamente no topo das buscas por relevância e na vitrine.
    """
    _obter_imovel_do_corretor_ou_erro(id_unico, corretor_atual)
    atualizacao = aplicar_impulsionamento_imovel(req.dias, req.plano or "15dias")
    imoveis_collection.update_one({"id_unico": id_unico}, {"$set": atualizacao})
    doc_final = imoveis_collection.find_one({"id_unico": id_unico}, {"_id": 0})
    if doc_final:
        converter_mongo_para_dict(doc_final)
    return {
        "mensagem": f"Imóvel impulsionado com sucesso por {req.dias} dias!",
        "imovel": doc_final,
    }


@app.delete("/corretor/imoveis/{id_unico}/impulsionar", responses=RESPONSES_CORRETOR_IMOVEL)
def cancelar_impulsionamento_imovel_corretor(
    id_unico: str,
    corretor_atual: Annotated[Dict[str, Any], Depends(obter_corretor_atual)],
):
    """
    Cancela o impulsionamento ativo de um imóvel.
    """
    _obter_imovel_do_corretor_ou_erro(id_unico, corretor_atual)
    atualizacao = remover_impulsionamento_imovel()
    imoveis_collection.update_one({"id_unico": id_unico}, {"$set": atualizacao})
    doc_final = imoveis_collection.find_one({"id_unico": id_unico}, {"_id": 0})
    if doc_final:
        converter_mongo_para_dict(doc_final)
    return {
        "mensagem": "Impulsionamento cancelado com sucesso.",
        "imovel": doc_final,
    }


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)