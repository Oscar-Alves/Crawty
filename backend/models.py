from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class ExtrasImovel(BaseModel):
    atributos: Optional[str] = None
    subtipo: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[Any] = None
    suites: Optional[int] = 0
    salas: Optional[int] = 0


class RegistroPreco(BaseModel):
    preco: float
    data: datetime


class Imovel(BaseModel):
    id_unico: str = Field(..., description="ID composto: Imobiliaria_Codigo")
    imobiliaria: str
    codigo_original: str
    titulo: str
    modalidade: str
    tipo: Optional[str] = "Indefinido"
    preco: float
    preco_anterior: Optional[float] = None
    historico_precos: Optional[List[RegistroPreco]] = []
    bairro: Optional[str] = "Não Informado"
    cidade: Optional[str] = "São João del Rei"
    quartos: int = 0
    banheiros: int = 0
    vagas: int = 0
    area_util: Optional[float] = 0.0
    area_total: Optional[float] = 0.0
    link: str
    fotos: List[str] = []
    extras: Optional[ExtrasImovel] = Field(default_factory=ExtrasImovel)
    criado_em: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    ativo: bool = True
    descontinuado_em: Optional[datetime] = None
    cliques: Optional[int] = 0

    class Config:
        populate_by_name = True


class CliqueLeadRequest(BaseModel):
    id_unico: str
    origem: Optional[str] = "detalhes"


class LoginCorretorRequest(BaseModel):
    usuario: str = Field(..., min_length=2, max_length=60)
    senha: str = Field(..., min_length=4, max_length=128)


class AtualizarPerfilCorretorRequest(BaseModel):
    nome: Optional[str] = Field(default=None, max_length=100)
    telefone: Optional[str] = Field(default=None, max_length=30)
    whatsapp: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=120)
    creci: Optional[str] = Field(default=None, max_length=40)
    site_externo: Optional[str] = Field(default=None, max_length=200)
    senha_atual: Optional[str] = Field(default=None, max_length=128)
    nova_senha: Optional[str] = Field(default=None, min_length=6, max_length=128)