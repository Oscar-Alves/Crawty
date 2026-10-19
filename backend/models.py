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


class ContatoCorretorImovel(BaseModel):
    nome: Optional[str] = ""
    creci: Optional[str] = ""
    whatsapp: Optional[str] = ""
    telefone: Optional[str] = ""
    email: Optional[str] = ""


class Imovel(BaseModel):
    id_unico: str = Field(..., description="ID composto: Imobiliaria_Codigo")
    imobiliaria: str
    codigo_original: str
    titulo: str
    descricao: Optional[str] = None
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
    corretor_usuario: Optional[str] = None
    contato_corretor: Optional[ContatoCorretorImovel] = None
    criado_em: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    ativo: bool = True
    descontinuado_em: Optional[datetime] = None
    cliques: Optional[int] = 0
    destaque: Optional[bool] = False
    destaque_ate: Optional[datetime] = None
    destaque_plano: Optional[str] = None

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


class SalvarImovelCorretorRequest(BaseModel):
    codigo_original: Optional[str] = Field(default="", max_length=40)
    titulo: str = Field(..., min_length=3, max_length=180)
    descricao: Optional[str] = Field(default="", max_length=4000)
    modalidade: str = Field(default="VENDA", pattern="^(VENDA|ALUGUEL)$")
    tipo: str = Field(default="Casa", max_length=50)
    subtipo: Optional[str] = Field(default="Padrão", max_length=60)
    preco: float = Field(..., ge=0)
    cidade: str = Field(default="São João del Rei", max_length=80)
    bairro: str = Field(default="Centro", max_length=100)
    logradouro: Optional[str] = Field(default="", max_length=160)
    numero: Optional[str] = Field(default="", max_length=30)
    quartos: int = Field(default=0, ge=0)
    suites: int = Field(default=0, ge=0)
    banheiros: int = Field(default=0, ge=0)
    vagas: int = Field(default=0, ge=0)
    salas: int = Field(default=0, ge=0)
    area_util: float = Field(default=0.0, ge=0)
    area_total: float = Field(default=0.0, ge=0)
    atributos: Optional[str] = Field(default="", max_length=500)
    fotos: List[str] = Field(default_factory=list)
    link_externo: Optional[str] = Field(default="", max_length=500)
    whatsapp_contato: Optional[str] = Field(default="", max_length=30)
    telefone_contato: Optional[str] = Field(default="", max_length=30)
    ativo: bool = True


class StatusImovelCorretorRequest(BaseModel):
    ativo: bool


class ImpulsionarImovelRequest(BaseModel):
    dias: int = Field(default=15, ge=1, le=365)
    plano: Optional[str] = Field(default="15dias", max_length=50)