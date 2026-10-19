import os
import json
import hmac
import base64
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Annotated, Dict, Any
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from database import corretores_collection
except ImportError:
    from backend.database import corretores_collection

ITERACOES_PBKDF2 = 200_000
VALIDADE_TOKEN_HORAS = 168  # 7 dias
ERRO_NAO_AUTENTICADO = "Sessão inválida ou expirada. Faça login novamente na Área do Corretor."

security_bearer = HTTPBearer(auto_error=False)


def _obter_chave_secreta() -> bytes:
    segredo_env = os.getenv("JWT_SECRET_KEY") or os.getenv("MONGODB_URL") or "crawty-chave-padrao-b2b"
    return hashlib.sha256(segredo_env.encode("utf-8")).digest()


def _codificar_b64url(dados: bytes) -> str:
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode("ascii")


def _decodificar_b64url(texto: str) -> bytes:
    padding = "=" * (-len(texto) % 4)
    return base64.urlsafe_b64decode((texto + padding).encode("ascii"))


def gerar_hash_senha(senha: str) -> str:
    sal = secrets.token_hex(16)
    derivado = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        sal.encode("utf-8"),
        ITERACOES_PBKDF2,
    )
    return f"pbkdf2_sha256${ITERACOES_PBKDF2}${sal}${derivado.hex()}"


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    if not senha or not hash_salvo:
        return False
    partes = hash_salvo.split("$")
    if len(partes) != 4 or partes[0] != "pbkdf2_sha256":
        return False
    try:
        iteracoes = int(partes[1])
        sal = partes[2]
        hash_esperado = partes[3]
        derivado = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            sal.encode("utf-8"),
            iteracoes,
        ).hex()
        return hmac.compare_digest(derivado, hash_esperado)
    except (ValueError, TypeError):
        return False


def gerar_token_acesso(doc_corretor: Dict[str, Any], validade_horas: int = VALIDADE_TOKEN_HORAS) -> str:
    agora = datetime.now(timezone.utc)
    expiracao = agora + timedelta(hours=validade_horas)
    payload = {
        "sub": doc_corretor.get("usuario"),
        "nome": doc_corretor.get("nome"),
        "imobiliaria": doc_corretor.get("imobiliaria"),
        "role": doc_corretor.get("role", "corretor"),
        "iat": int(agora.timestamp()),
        "exp": int(expiracao.timestamp()),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = _codificar_b64url(payload_bytes)
    assinatura = hmac.new(
        _obter_chave_secreta(),
        payload_b64.encode("ascii"),
        hashlib.sha256,
    ).digest()
    assinatura_b64 = _codificar_b64url(assinatura)
    return f"{payload_b64}.{assinatura_b64}"


def validar_token_acesso(token: str) -> Optional[Dict[str, Any]]:
    if not token or "." not in token:
        return None
    partes = token.split(".")
    if len(partes) != 2:
        return None
    payload_b64, assinatura_recebida = partes
    assinatura_esperada_bytes = hmac.new(
        _obter_chave_secreta(),
        payload_b64.encode("ascii"),
        hashlib.sha256,
    ).digest()
    assinatura_esperada = _codificar_b64url(assinatura_esperada_bytes)
    if not hmac.compare_digest(assinatura_recebida, assinatura_esperada):
        return None
    try:
        payload = json.loads(_decodificar_b64url(payload_b64).decode("utf-8"))
        exp = int(payload.get("exp", 0))
        agora_ts = int(datetime.now(timezone.utc).timestamp())
        if exp < agora_ts:
            return None
        return payload
    except Exception:
        return None


def serializar_corretor_publico(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "usuario": doc.get("usuario", ""),
        "nome": doc.get("nome", ""),
        "imobiliaria": doc.get("imobiliaria", ""),
        "role": doc.get("role", "corretor"),
        "creci": doc.get("creci", ""),
        "telefone": doc.get("telefone", ""),
        "whatsapp": doc.get("whatsapp", ""),
        "email": doc.get("email", ""),
        "site_externo": doc.get("site_externo", ""),
        "ativo": doc.get("ativo", True) is not False,
        "criado_em": doc.get("criado_em"),
        "ultimo_login": doc.get("ultimo_login"),
    }


def obter_corretor_atual(
    credenciais: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security_bearer)],
) -> Dict[str, Any]:
    if not credenciais or not credenciais.credentials:
        raise HTTPException(status_code=401, detail=ERRO_NAO_AUTENTICADO)

    payload = validar_token_acesso(credenciais.credentials)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail=ERRO_NAO_AUTENTICADO)

    if corretores_collection is None:
        raise HTTPException(status_code=500, detail="Banco não conectado")

    usuario = str(payload["sub"]).strip().lower()
    doc = corretores_collection.find_one({"usuario": usuario})
    if not doc or doc.get("ativo") is False:
        raise HTTPException(
            status_code=401,
            detail="Conta de corretor inativa ou não encontrada.",
        )

    return doc

