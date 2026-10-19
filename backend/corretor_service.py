import re
import secrets
from datetime import datetime, timezone
from urllib.parse import quote
from typing import Dict, Any, List

try:
    from models import SalvarImovelCorretorRequest
    from normalizer import normalizar_cidade, normalizar_bairro
except ImportError:
    from backend.models import SalvarImovelCorretorRequest
    from backend.normalizer import normalizar_cidade, normalizar_bairro


def construir_filtro_carteira_corretor(corretor: Dict[str, Any]) -> Dict[str, Any]:
    usuario = (corretor.get("usuario") or "").strip().lower()
    imob = (corretor.get("imobiliaria") or "").strip()

    condicoes: List[Dict[str, Any]] = []
    if usuario:
        condicoes.append({"corretor_usuario": usuario})
    if imob:
        padrao = f"^{re.escape(imob)}$"
        condicoes.append({"imobiliaria": {"$regex": padrao, "$options": "i"}})

    if not condicoes:
        return {"corretor_usuario": "__nenhum__"}
    if len(condicoes) == 1:
        return condicoes[0]
    return {"$or": condicoes}


def verificar_permissao_imovel(doc_imovel: Dict[str, Any], corretor: Dict[str, Any]) -> bool:
    if corretor.get("role") == "admin":
        return True
    usuario = (corretor.get("usuario") or "").strip().lower()
    if usuario and (doc_imovel.get("corretor_usuario") or "").strip().lower() == usuario:
        return True
    imob_corretor = (corretor.get("imobiliaria") or "").strip().lower()
    imob_imovel = (doc_imovel.get("imobiliaria") or "").strip().lower()
    return bool(imob_corretor and imob_corretor == imob_imovel)


def _limpar_lista_fotos(fotos: List[str]) -> List[str]:
    limpas: List[str] = []
    vistas = set()
    for url in fotos or []:
        texto = (url or "").strip()
        if texto.startswith(("http://", "https://")) and texto not in vistas:
            vistas.add(texto)
            limpas.append(texto)
    return limpas


def _montar_contato_corretor(
    dados: SalvarImovelCorretorRequest,
    corretor: Dict[str, Any],
) -> Dict[str, str]:
    whatsapp = (dados.whatsapp_contato or corretor.get("whatsapp") or "").strip()
    telefone = (dados.telefone_contato or corretor.get("telefone") or "").strip()
    return {
        "nome": (corretor.get("nome") or "").strip(),
        "creci": (corretor.get("creci") or "").strip(),
        "whatsapp": whatsapp,
        "telefone": telefone,
        "email": (corretor.get("email") or "").strip(),
    }


def gerar_link_anuncio_corretor(
    dados: SalvarImovelCorretorRequest,
    corretor: Dict[str, Any],
    codigo_original: str,
) -> str:
    link_ext = (dados.link_externo or "").strip()
    if link_ext.startswith(("http://", "https://")):
        return link_ext

    whatsapp_bruto = (
        dados.whatsapp_contato
        or corretor.get("whatsapp")
        or dados.telefone_contato
        or corretor.get("telefone")
        or ""
    )
    digitos = re.sub(r"\D", "", whatsapp_bruto)
    if len(digitos) in (10, 11):
        digitos = f"55{digitos}"
    if len(digitos) >= 12:
        mensagem = (
            f"Olá! Vi o imóvel '{dados.titulo.strip()}' "
            f"(Cód. {codigo_original}) no HubImóveis e gostaria de mais informações."
        )
        return f"https://wa.me/{digitos}?text={quote(mensagem)}"

    site_corretor = (corretor.get("site_externo") or "").strip()
    if site_corretor.startswith(("http://", "https://")):
        return site_corretor

    return "#contato-direto"


def _gerar_codigo_e_id_unico(
    codigo_informado: str,
    corretor: Dict[str, Any],
) -> tuple[str, str]:
    usuario_slug = re.sub(r"[^a-zA-Z0-9]", "", corretor.get("usuario") or "corretor").lower()
    codigo_limpo = re.sub(r"[^a-zA-Z0-9_-]", "", (codigo_informado or "").strip())
    if not codigo_limpo:
        codigo_limpo = f"P{secrets.randbelow(90000) + 10000}"
    id_unico = f"Parceiro_{usuario_slug}_{codigo_limpo}"
    return codigo_limpo, id_unico


def _extrair_campos_comuns_imovel(
    dados: SalvarImovelCorretorRequest,
    corretor: Dict[str, Any],
    codigo_original: str,
) -> Dict[str, Any]:
    cidade_norm = normalizar_cidade(dados.cidade) or "São João del Rei"
    bairro_norm = normalizar_bairro(dados.bairro) or "Centro"
    subtipo_limpo = (dados.subtipo or "Padrão").strip() or "Padrão"
    nome_imob = (corretor.get("imobiliaria") or corretor.get("nome") or "Corretor Parceiro").strip()

    return {
        "imobiliaria": nome_imob,
        "codigo_original": codigo_original,
        "titulo": dados.titulo.strip(),
        "descricao": (dados.descricao or "").strip(),
        "modalidade": dados.modalidade.strip().upper(),
        "tipo": (dados.tipo or "Casa").strip(),
        "preco": float(dados.preco),
        "cidade": cidade_norm,
        "bairro": bairro_norm,
        "quartos": int(dados.quartos or 0),
        "banheiros": int(dados.banheiros or 0),
        "vagas": int(dados.vagas or 0),
        "area_util": float(dados.area_util or 0.0),
        "area_total": float(dados.area_total or 0.0),
        "fotos": _limpar_lista_fotos(dados.fotos),
        "link": gerar_link_anuncio_corretor(dados, corretor, codigo_original),
        "extras": {
            "subtipo": subtipo_limpo,
            "logradouro": (dados.logradouro or "").strip(),
            "numero": (dados.numero or "").strip(),
            "suites": int(dados.suites or 0),
            "salas": int(dados.salas or 0),
            "atributos": (dados.atributos or "").strip(),
        },
        "contato_corretor": _montar_contato_corretor(dados, corretor),
        "ativo": bool(dados.ativo),
    }


def montar_documento_novo_imovel(
    dados: SalvarImovelCorretorRequest,
    corretor: Dict[str, Any],
) -> Dict[str, Any]:
    agora = datetime.now(timezone.utc)
    codigo_original, id_unico = _gerar_codigo_e_id_unico(dados.codigo_original or "", corretor)
    campos = _extrair_campos_comuns_imovel(dados, corretor, codigo_original)

    return {
        **campos,
        "id_unico": id_unico,
        "corretor_usuario": (corretor.get("usuario") or "").strip().lower(),
        "preco_anterior": None,
        "historico_precos": [{"preco": float(dados.preco), "data": agora}],
        "criado_em": agora,
        "last_updated": agora,
        "descontinuado_em": None if dados.ativo else agora,
        "cliques": 0,
    }


def montar_atualizacao_imovel(
    doc_existente: Dict[str, Any],
    dados: SalvarImovelCorretorRequest,
    corretor: Dict[str, Any],
) -> Dict[str, Any]:
    agora = datetime.now(timezone.utc)
    codigo_original = (
        (dados.codigo_original or "").strip()
        or doc_existente.get("codigo_original")
        or "P001"
    )
    campos = _extrair_campos_comuns_imovel(dados, corretor, codigo_original)
    campos["last_updated"] = agora
    campos["descontinuado_em"] = None if dados.ativo else (doc_existente.get("descontinuado_em") or agora)

    preco_antigo = float(doc_existente.get("preco") or 0.0)
    preco_novo = float(dados.preco or 0.0)
    historico = list(doc_existente.get("historico_precos") or [])

    if preco_antigo > 0 and preco_novo > 0 and abs(preco_novo - preco_antigo) >= 0.01:
        campos["preco_anterior"] = preco_antigo
        historico.append({"preco": preco_novo, "data": agora})
        campos["historico_precos"] = historico

    return campos

