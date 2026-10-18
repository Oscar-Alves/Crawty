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
    extras: Optional[ExtrasImovel] = {}
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