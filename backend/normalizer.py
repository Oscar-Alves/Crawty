import re
import unicodedata
from typing import Dict, Any, Tuple, Optional

CIDADE_SJDR = "São João del Rei"
CIDADE_TREMEMBE = "Tremembé"
CIDADE_TIRADENTES = "Tiradentes"
BAIRRO_NAO_INFORMADO = "Não Informado"
BAIRRO_COLINAS_DEL_REY = "Colinas Del Rey"
BAIRRO_VILA_NS_FATIMA = "Vila Nossa Senhora de Fátima"
BAIRRO_JARDIM_COLONIA = "Jardim Colônia"
BAIRRO_RESIDENCIAL_LENHEIRO = "Residencial Lenheiro"
BAIRRO_MONTE_VERDE = "Monte Verde"
BAIRRO_ZONA_RURAL = "Zona Rural"
BAIRRO_RECANTO_DA_SERRA = "Recanto da Serra"
BAIRRO_CAIXA_DAGUA = "Caixa D'Água"
BAIRRO_BICHINHO = "Bichinho"

SUBTIPO_SITIO = "Sítio"
SUBTIPO_PADRAO = "Padrão"
SUBTIPO_PONTO_COMERCIAL = "Ponto Comercial"
SUBTIPO_SALA_COMERCIAL = "Sala Comercial"
SUBTIPO_GALPAO = "Galpão/Depósito"
CHAVE_PONTO_COMERCIAL = "ponto comercial"


def _remover_acentos(texto: str) -> str:
    if not texto:
        return ""
    normalizado = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in normalizado if not unicodedata.combining(c))


def _chave_comparacao(texto: str) -> str:
    limpo = _remover_acentos(texto).lower().strip()
    limpo = re.sub(r"[^a-z0-9\s]", " ", limpo)
    return re.sub(r"\s+", " ", limpo).strip()


# Mapeamento canônico de cidades (chave sem acento/minúscula -> Nome Canônico)
CIDADES_CANONICAS = {
    "sao joao del rei": CIDADE_SJDR,
    "sao joao del-rei": CIDADE_SJDR,
    "sjdr": CIDADE_SJDR,
    "tiradentes": CIDADE_TIRADENTES,
    "santa cruz de minas": "Santa Cruz de Minas",
    "barbacena": "Barbacena",
    "barroso": "Barroso",
    "prados": "Prados",
    "resende costa": "Resende Costa",
    "coronel xavier chaves": "Coronel Xavier Chaves",
    "ritapolis": "Ritápolis",
    "antonio carlos": "Antônio Carlos",
    "nazareno": "Nazareno",
    "itutinga": "Itutinga",
    "carrancas": "Carrancas",
    "dores de campos": "Dores de Campos",
    "madre de deus de minas": "Madre de Deus de Minas",
    "madre de deus": "Madre de Deus de Minas",
    "conceicao da barra de minas": "Conceição da Barra de Minas",
    "lagoa dourada": "Lagoa Dourada",
    "piedade do rio grande": "Piedade do Rio Grande",
    "sao tiago": "São Tiago",
    "sao vicente de minas": "São Vicente de Minas",
    "alfredo vasconcelos": "Alfredo Vasconcelos",
    "ibertioga": "Ibertioga",
    "carandai": "Carandaí",
    "santa barbara do tugurio": "Santa Bárbara do Tugúrio",
    "alto rio doce": "Alto Rio Doce",
    "santos dumont": "Santos Dumont",
    "conselheiro lafaiete": "Conselheiro Lafaiete",
    "juiz de fora": "Juiz de Fora",
    "lavras": "Lavras",
    "belo horizonte": "Belo Horizonte",
    "bom sucesso": "Bom Sucesso",
    "itabirito": "Itabirito",
    "ribeirao das neves": "Ribeirão das Neves",
    "visconde do rio branco": "Visconde do Rio Branco",
    "porto firme": "Porto Firme",
    "ituiutaba": "Ituiutaba",
    "araxa": "Araxá",
    "tremembe": CIDADE_TREMEMBE,
    "rio de janeiro": "Rio de Janeiro",
    "niteroi": "Niterói",
    "cabo frio": "Cabo Frio",
    "itaguai": "Itaguaí",
    "sao pedro da aldeia": "São Pedro da Aldeia",
    "braganca paulista": "Bragança Paulista",
    "caldas novas": "Caldas Novas",
    "salvador": "Salvador",
    "ilheus": "Ilhéus",
    "souto soares": "Souto Soares",
    "centenario do sul": "Centenário do Sul",
    "taguatinga": "Taguatinga",
}

# Bairros macro que, quando aparecem junto de um loteamento/sub-bairro entre parênteses,
# cedem lugar ao nome específico do loteamento/sub-bairro.
BAIRROS_MACRO_KEYS = {
    "colonia do marcal",
    "fabricas",
    "centro",
    "bonfim",
    "matosinhos",
    "matozinhos",
    "tejuco",
    "caieiras",
}

# Mapeamento direto de variações de bairro (chave normalizada -> Nome Canônico)
BAIRROS_CANONICOS = {
    # São João del Rei e Região
    "matozinhos": "Matosinhos",
    "matosinhos": "Matosinhos",
    "colonia do marcal": "Colônia do Marçal",
    "fabricas": "Fábricas",
    "fabrica": "Fábricas",
    "bonfim": "Bonfim",
    "centro": "Centro",
    "tejuco": "Tejuco",
    "pio xii": "Pio XII",
    "dom bosco": "Dom Bosco",
    "dom bosco vila dom helvecio": "Dom Bosco",
    "vila belizario": "Vila Belizário",
    "vila belisario": "Vila Belizário",
    "cidade verde": "Cidade Verde",
    "solar da serra": "Solar da Serra",
    "bom pastor": "Bom Pastor",
    "jardim das acacias": "Jardim das Acácias",
    "novo horizonte": "Novo Horizonte",
    "sao caetano": "São Caetano",
    "residencial sao caetano": "São Caetano",
    "parque real": "Parque Real",
    "vila marchetti": "Vila Marchetti",
    "portal vila rica": "Portal Vila Rica",
    "vila rica": "Portal Vila Rica",
    "sao judas tadeu": "São Judas Tadeu",
    "vila tiradentes": "Vila Tiradentes",
    "vila tiradentes agua limpa": "Vila Tiradentes",
    "cidade universitaria": "Cidade Universitária",
    "vila brasil": "Vila Brasil",
    "caieiras": "Caieiras",
    "caieira": "Caieiras",
    "guarda mor": "Guarda-Mor",
    "gurdar mor": "Guarda-Mor",
    "colinas del rey": BAIRRO_COLINAS_DEL_REY,
    "colinas del rei": BAIRRO_COLINAS_DEL_REY,
    "condominio colinas del rey": BAIRRO_COLINAS_DEL_REY,
    "colinas": BAIRRO_COLINAS_DEL_REY,
    "colinas dos inconfidentes": "Colinas dos Inconfidentes",
    "bela vista": "Bela Vista",
    "vista da serra": "Vista da Serra",
    "campana del vento": "Campana Del Vento",
    "condominio campana del vento": "Campana Del Vento",
    "segredo": "Segredo",
    "sao jose operario": "São José Operário",
    "vila santa terezinha": "Vila Santa Terezinha",
    "cidade nova": "Cidade Nova",
    "carmindo": "Carmindo",
    "loteamento do carmindo": "Carmindo",
    "recreio das alterosas": "Recreio das Alterosas",
    "vila nossa senhora de fatima": BAIRRO_VILA_NS_FATIMA,
    "vila nossa senhora fatima": BAIRRO_VILA_NS_FATIMA,
    "vila jardim nossa senhora de fatima": BAIRRO_VILA_NS_FATIMA,
    "alto das aguas": "Alto das Águas",
    "senhor dos montes": "Senhor dos Montes",
    "rio das mortes": "Rio das Mortes",
    "vila sao paulo": "Vila São Paulo",
    "vila joao lombardi": "Vila João Lombardi",
    "vila joao lombard": "Vila João Lombardi",
    "jardim colonia": BAIRRO_JARDIM_COLONIA,
    "jardim coloniais": BAIRRO_JARDIM_COLONIA,
    "condominio jardins coloniais numero 44": BAIRRO_JARDIM_COLONIA,
    "rio acima": "Rio Acima",
    "jardim paulo campos": "Jardim Paulo Campos",
    "corrego do andre": "Córrego do André",
    "vila jardim sao jose": "Vila Jardim São José",
    "jardins da serra": "Jardins da Serra",
    "alto das merces": "Alto das Mercês",
    "nascente do sol": "Nascente do Sol",
    "residencial lenheiro": BAIRRO_RESIDENCIAL_LENHEIRO,
    "residencial lenheiros": BAIRRO_RESIDENCIAL_LENHEIRO,
    "lenheiros": BAIRRO_RESIDENCIAL_LENHEIRO,
    "jardim aeroporto": "Jardim Aeroporto",
    "residencial jardim aeroporto": "Jardim Aeroporto",
    "parque sao joao del rey": "Parque São João del Rei",
    "parque sao joao del rei": "Parque São João del Rei",
    "vila santo antonio": "Vila Santo Antônio",
    "parque bela vista": "Parque Bela Vista",
    "jardim central": "Jardim Central",
    "alto do maquine": "Alto do Maquiné",
    "residencial maquine": "Alto do Maquiné",
    "colonia do bengo": "Colônia do Bengo",
    "cohab": "Cohab",
    "coahbe": "Cohab",
    "girassol": "Girassol",
    "girasol": "Girassol",
    "residencial girassol": "Girassol",
    "sao francisco": "São Francisco",
    "vila sao vicente": "Vila São Vicente",
    "vila maria": "Vila Maria",
    "colonia do giarola": "Colônia do Giarola",
    "varzea do faria": "Várzea do Faria",
    "vila do carmo": "Vila do Carmo",
    "monte verde": BAIRRO_MONTE_VERDE,
    "condominio monte verde": BAIRRO_MONTE_VERDE,
    "cond monte verde": BAIRRO_MONTE_VERDE,
    "nova colonia": "Nova Colônia",
    "vila del rei": "Vila Del Rei",
    "villa del rei colonia do marcal": "Vila Del Rei",
    "aguas ferreas": "Águas Férreas",
    "agua limpa": "Água Limpa",
    "araca": "Araçá",
    "caquende": "Caquende",
    "zona rural": BAIRRO_ZONA_RURAL,
    "area rural": BAIRRO_ZONA_RURAL,
    "area rural de sao joao del rei": BAIRRO_ZONA_RURAL,
    "br 265": "BR 265",
    "br 494": "BR 494",
    "br 383": "BR 383",
    "rosa mistica": "Rosa Mística",
    "bom clima": "Bom Clima",
    "porto real": "Porto Real",
    # Tiradentes / Prados / Região
    "aguas santas": "Águas Santas",
    "cesar de pina": "César de Pina",
    "cuiaba": "Cuiabá",
    "cuiba": "Cuiabá",
    "terra dos cuiabas": "Terra dos Cuiabás",
    "condominio terra dos cuiabas": "Terra dos Cuiabás",
    "alto dos cuiabas": "Alto dos Cuiabás",
    "condominio alto dos cuiabas": "Alto dos Cuiabás",
    "condominio tiradentes ville": "Condomínio Tiradentes Ville",
    "recanto da serra": BAIRRO_RECANTO_DA_SERRA,
    "condominio recanto da serra": BAIRRO_RECANTO_DA_SERRA,
    "condominio recanto serra": BAIRRO_RECANTO_DA_SERRA,
    "residencial recanto da serra": BAIRRO_RECANTO_DA_SERRA,
    "elvas": "Elvas",
    "elvas emboabas": "Elvas",
    "candonga": "Candonga",
    "candonga da serra": "Candonga",
    "candonga da serrra": "Candonga",
    "cascalho": "Cascalho",
    "santissima trindade": "Santíssima Trindade",
    "santissima": "Santíssima Trindade",
    "caixa d agua": BAIRRO_CAIXA_DAGUA,
    "caixa d agua z rural": BAIRRO_CAIXA_DAGUA,
    "caixa d agua da esperanca": BAIRRO_CAIXA_DAGUA,
    "mococa": "Mococa",
    "capote": "Capote",
    "estacao": "Estação",
    "estacao de": "Estação",
    "varzea de baixo": "Várzea de Baixo",
    "alto da torre": "Alto da Torre",
    "pau de angu": "Pau de Angu",
    "pau de oleo": "Pau de Óleo",
    "guiaba": "Guiaba",
    "pacu": "Pacu",
    "trevo de tiradentes": "Trevo de Tiradentes",
    "trevo de": "Trevo de Tiradentes",
    "bichinho": BAIRRO_BICHINHO,
    "vitoriano veloso": BAIRRO_BICHINHO,
    "vitoriano veloso bichinho": BAIRRO_BICHINHO,
    "pinheiro chagas": "Pinheiro Chagas",
    "pitangueiras": "Pitangueiras",
    "jardim dos arvoredos": "Jardim dos Arvoredos",
    "jardim dos arvoreiros": "Jardim dos Arvoredos",
    # Outros locais da região
    "colonia rodrigo silva": "Colônia Rodrigo Silva",
    "santa tereza i": "Santa Tereza I",
    "santa tereza ii": "Santa Tereza II",
    "boa morte": "Boa Morte",
    "sao jose": "São José",
    "sao sebastiao": "São Sebastião",
    "campolide": "Campolide",
    "caicaras": "Caiçaras",
    "funcionarios": "Funcionários",
    "grogoto": "Grogotó",
    "ipanema": "Ipanema",
    "santa cecilia": "Santa Cecília",
    "chacaras marino ceolin": "Chácaras Marino Ceolin",
    "sao geraldo": "São Geraldo",
    "monte mario": "Monte Mário",
    "serra verde": "Serra Verde",
    "sao jorge": "São Jorge",
    "caminho novo": "Caminho Novo",
    "chacaras das andorinhas": "Chácaras das Andorinhas",
    "diniz ii": "Diniz II",
    "pontilhao": "Pontilhão",
    "fatima": "Fátima",
    "ibiapaba": "Ibiapaba",
    "santo antonio": "Santo Antônio",
    "mansoes": "Mansões",
    "faria": "Faria",
    "jardim": "Jardim",
    "nova cidade": "Nova Cidade",
    "belvedere": "Belvedere",
    "roman": "Roman",
    "boa vista": "Boa Vista",
    "carmo": "Carmo",
    "passarinhos": "Passarinhos",
    "pinheiro grosso": "Pinheiro Grosso",
    "vilela": "Vilela",
    "dr sa fortes": "Dr. Sá Fortes",
    "sa fortes": "Dr. Sá Fortes",
    "dr jose guimaraes": "Dr. José Guimarães",
    "irmaos pinto": "Irmãos Pinto",
    "jardim bandeirantes": "Jardim Bandeirantes",
    "joaquim gabriel de souza": "Joaquim Gabriel de Souza",
    "nova barroso": "Nova Barroso",
    "rosario": "Rosário",
    "genesio gracano": "Genésio Graçano",
    "eldorado": "Eldorado",
    "el dourado": "Eldorado",
    "balneario riviera real": "Balneário Riviera Real",
    "represa de camargos": "Represa de Camargos",
    "repressa de camargos": "Represa de Camargos",
    "engenho de serra": "Engenho de Serra",
    "engenho de serra sao sebastiao da vitoria": "Engenho de Serra",
    "varzea": "Várzea",
    "sao dimas": "São Dimas",
    "bananal": "Bananal",
    "estiva": "Estiva",
    "invejosa": "Invejosa",
    "tremenbe": CIDADE_TREMEMBE,
    "tremembe": CIDADE_TREMEMBE,
    "parque dos bandeirantes 2": "Parque dos Bandeirantes II",
    "residencial parque dos bandeirantes ii": "Parque dos Bandeirantes II",
    "residencial parque dos bandeirantes": "Parque dos Bandeirantes",
    "povoado sao caetano": "Povoado de São Caetano",
    "nossa senhora da penha": "Nossa Senhora da Penha",
    "terras de oyama": "Terras de Oyama",
    "condominio morada do sol": "Condomínio Morada do Sol",
    "loteamento balneario da capela": "Loteamento Balneário da Capela",
    "loteamento residencial colinas": "Loteamento Residencial Colinas",
}

PALAVRAS_MINUSCULAS = {"de", "da", "do", "das", "dos", "e", "em", "no", "na", "nos", "nas", "del"}
ALGARISMOS_ROMANOS = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"}
BAIRROS_INVALIDOS = {"nao informado", "n i", "bairro", "fim comercial", "condominio", "undefined"}


def _formatar_titulo_bairro(nome: str) -> str:
    palavras = nome.strip().split()
    resultado = []
    for idx, p in enumerate(palavras):
        p_lower = p.lower()
        if p_lower in ALGARISMOS_ROMANOS:
            resultado.append(p.upper())
        elif p_lower == "br":
            resultado.append("BR")
        elif idx > 0 and p_lower in PALAVRAS_MINUSCULAS:
            resultado.append(p_lower)
        else:
            resultado.append(p.capitalize())
    return " ".join(resultado)


def normalizar_cidade(cidade: Optional[str]) -> str:
    if not cidade or not str(cidade).strip():
        return CIDADE_SJDR
    texto = str(cidade).strip()
    chave = _chave_comparacao(texto)
    if chave in CIDADES_CANONICAS:
        return CIDADES_CANONICAS[chave]
    return _formatar_titulo_bairro(texto)


def _separar_sufixo_cidade_uf(bairro: str, cidade_atual: str) -> Tuple[str, str]:
    if "/" not in bairro:
        return bairro, cidade_atual

    antes_barra, depois_barra = bairro.rsplit("/", 1)
    uf_limpa = depois_barra.strip()
    if uf_limpa and (len(uf_limpa) != 2 or not uf_limpa.isalpha()):
        return bairro, cidade_atual

    sem_uf = antes_barra.strip()
    sem_uf_norm = _chave_comparacao(sem_uf)
    cidades_ordenadas = sorted(CIDADES_CANONICAS.keys(), key=len, reverse=True)

    for cid_key in cidades_ordenadas:
        if sem_uf_norm == cid_key or sem_uf_norm.endswith(f" {cid_key}"):
            nova_cidade = CIDADES_CANONICAS[cid_key]
            qtd_palavras_cid = len(cid_key.split())
            tokens_orig = sem_uf.replace("-", " ").split()
            if len(tokens_orig) > qtd_palavras_cid:
                partes = sem_uf.split()
                novo_bairro = " ".join(partes[:-qtd_palavras_cid]).strip()
            else:
                novo_bairro = BAIRRO_NAO_INFORMADO
            return novo_bairro, nova_cidade

    return sem_uf, cidade_atual


def _extrair_bairro_parenteses(bairro: str) -> str:
    if "(" not in bairro or not bairro.endswith(")"):
        return bairro

    parte_a, parte_b = bairro[:-1].split("(", 1)
    parte_a = parte_a.strip()
    parte_b = parte_b.strip()
    if not parte_a or not parte_b:
        return bairro

    key_a = _chave_comparacao(parte_a)
    key_b = _chave_comparacao(parte_b)

    if key_a == "vitoriano veloso" or key_b == "bichinho":
        return BAIRRO_BICHINHO
    if key_a in BAIRROS_MACRO_KEYS:
        return parte_b
    if key_b in BAIRROS_MACRO_KEYS or key_b in {"alto das aguas", "ilha do governador", "venda nova"}:
        return parte_a
    return parte_b


def _finalizar_nome_bairro(bairro: str, chave_b: str) -> str:
    if chave_b in BAIRROS_CANONICOS:
        return BAIRROS_CANONICOS[chave_b]
    if bairro.isupper() or bairro.islower():
        return _formatar_titulo_bairro(bairro)
    return bairro[0].upper() + bairro[1:]


def normalizar_localizacao(
    bairro_raw: Optional[str],
    cidade_raw: Optional[str],
    logradouro_raw: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Normaliza o par (bairro, cidade), corrigindo sufixos '/ MG', inversões cidade/bairro,
    sub-bairros entre parênteses e variações de grafia/acentuação.
    """
    cidade = normalizar_cidade(cidade_raw)
    bairro = str(bairro_raw or "").strip()

    if _chave_comparacao(cidade) == "cuiaba" and _chave_comparacao(bairro) == "sao joao del rei":
        log_key = _chave_comparacao(logradouro_raw or "")
        bairro_corr = "Bonfim" if "bonfim" in log_key else BAIRRO_NAO_INFORMADO
        return bairro_corr, CIDADE_SJDR

    bairro, cidade = _separar_sufixo_cidade_uf(bairro, cidade)
    bairro = re.sub(r"\s+", " ", bairro).strip(" ,.-")
    if not bairro:
        return BAIRRO_NAO_INFORMADO, cidade

    bairro = _extrair_bairro_parenteses(bairro)
    chave_b = _chave_comparacao(bairro)
    chave_c = _chave_comparacao(cidade)

    if not chave_b or chave_b in BAIRROS_INVALIDOS or chave_b == chave_c:
        return BAIRRO_NAO_INFORMADO, cidade

    bairro_final = _finalizar_nome_bairro(bairro, chave_b)
    if not cidade_raw and bairro_final in {"César de Pina", "Águas Santas", "Candonga"}:
        cidade = CIDADE_TIRADENTES

    return bairro_final, cidade


SUBTIPOS_PADRONIZADOS = {
    "Casa de condomínio": "Casa de Condomínio",
    "Casa de vila": "Casa de Vila",
    "Duplex/triplex": "Duplex/Triplex",
    "Sítios e chácaras": SUBTIPO_SITIO,
}

SUBTIPOS_RURAIS_MAP = {
    "sitio": SUBTIPO_SITIO,
    "chacara": "Chácara",
    "fazenda": "Fazenda",
    "sitios e chacaras": SUBTIPO_SITIO,
}

TIPOS_COMERCIAIS_KEYS = {
    "comercio",
    "comercial",
    "comercio e industria",
    CHAVE_PONTO_COMERCIAL,
    "sala comercial",
    "galpao",
    "pousada",
    "temporada",
}

REGRAS_TITULO_EXATAS = [
    (("kitnet", "conjugado"), "Kitnet", "Kitnet"),
    (("cobertura",), "Apartamento", "Cobertura"),
    (("loft",), "Apartamento", "Loft"),
    (("studio", "flat"), "Apartamento", "Studio"),
    (("sitio",), "Rural", SUBTIPO_SITIO),
    (("fazenda",), "Rural", "Fazenda"),
    (("chacara",), "Rural", "Chácara"),
    (("galpao", "deposito"), "Comercial", SUBTIPO_GALPAO),
    (("pousada",), "Comercial", "Pousada"),
    (("hotel",), "Comercial", "Hotel"),
    (("loja",), "Comercial", "Loja"),
    (("sala", "escritorio", "consultorio"), "Comercial", SUBTIPO_SALA_COMERCIAL),
]


def _normalizar_subtipo_inicial(subtipo_raw: Optional[str]) -> Optional[str]:
    if not subtipo_raw:
        return None
    subtipo_str = str(subtipo_raw).strip()
    if subtipo_str.lower() in {"none", "null", ""}:
        return None
    return SUBTIPOS_PADRONIZADOS.get(subtipo_str, subtipo_str)


def _classificar_comercial(tk: str, subtipo_str: Optional[str]) -> Tuple[str, Optional[str]]:
    defaults = {
        CHAVE_PONTO_COMERCIAL: SUBTIPO_PONTO_COMERCIAL,
        "sala comercial": SUBTIPO_SALA_COMERCIAL,
        "galpao": SUBTIPO_GALPAO,
    }
    if not subtipo_str and tk in defaults:
        return "Comercial", defaults[tk]
    if tk in {"pousada", "temporada"} and (not subtipo_str or subtipo_str == SUBTIPO_PADRAO):
        return "Comercial", "Pousada"
    return "Comercial", subtipo_str


def _classificar_por_tipo_direto(
    tk: str, sk: str, subtipo_str: Optional[str]
) -> Optional[Tuple[str, Optional[str]]]:
    if sk == "kitnet" or tk == "kitnet":
        return "Kitnet", "Kitnet"
    if sk in SUBTIPOS_RURAIS_MAP:
        return "Rural", SUBTIPOS_RURAIS_MAP[sk]
    if sk in {"lote", "lote de condominio", "terreno"}:
        return "Terreno", subtipo_str or ("Lote" if tk == "lote" else "Terreno")
    if tk in {"casa", "chale"}:
        sub = "Chalé" if tk == "chale" and (not subtipo_str or subtipo_str == SUBTIPO_PADRAO) else subtipo_str
        return "Casa", sub
    if tk == "apartamento":
        sub = SUBTIPO_PADRAO if subtipo_str == "Apartamento" else subtipo_str
        return "Apartamento", sub
    if tk in {"lote", "terreno", "terrenos sitios e fazendas"}:
        sub = "Lote" if tk == "lote" and (not subtipo_str or subtipo_str == SUBTIPO_PADRAO) else (subtipo_str or "Terreno")
        return "Terreno", sub
    if tk in TIPOS_COMERCIAIS_KEYS:
        return _classificar_comercial(tk, subtipo_str)
    if tk in {"rural", "sitio", "chacara", "fazenda"}:
        return "Rural", subtipo_str or SUBTIPO_SITIO
    return None


def _inferir_por_titulo(tit_k: str, subtipo_str: Optional[str]) -> Tuple[str, Optional[str]]:
    for termos, tipo_dest, subtipo_dest in REGRAS_TITULO_EXATAS:
        if any(t in tit_k for t in termos):
            return tipo_dest, subtipo_dest

    if "apartamento" in tit_k or "apto" in tit_k:
        return "Apartamento", subtipo_str or SUBTIPO_PADRAO
    if any(t in tit_k for t in (CHAVE_PONTO_COMERCIAL, "comercial", "predio")):
        return "Comercial", subtipo_str or SUBTIPO_PONTO_COMERCIAL
    if "lote" in tit_k or "terreno" in tit_k:
        return "Terreno", "Lote" if "lote" in tit_k else "Terreno"

    return "Casa", subtipo_str or SUBTIPO_PADRAO


def normalizar_tipo_e_subtipo(
    tipo_raw: Optional[str],
    subtipo_raw: Optional[str] = None,
    titulo_raw: Optional[str] = None,
) -> Tuple[str, Optional[str]]:
    """
    Normaliza `tipo` nas categorias principais (Casa, Apartamento, Terreno, Comercial, Rural, Kitnet)
    preservando e enriquecendo o detalhe em `subtipo`.
    """
    subtipo_str = _normalizar_subtipo_inicial(subtipo_raw)
    tk = _chave_comparacao(str(tipo_raw or "").strip())
    sk = _chave_comparacao(subtipo_str or "")
    tit_k = _chave_comparacao(str(titulo_raw or "").strip())

    direto = _classificar_por_tipo_direto(tk, sk, subtipo_str)
    if direto is not None:
        return direto

    return _inferir_por_titulo(tit_k, subtipo_str)


def _converter_int_positivo(valor: Any) -> int:
    try:
        return max(0, int(valor or 0))
    except (ValueError, TypeError):
        return 0


def _converter_float_positivo(valor: Any) -> float:
    try:
        return max(0.0, float(valor or 0.0))
    except (ValueError, TypeError):
        return 0.0


def _sanitizar_campos_numericos(item: Dict[str, Any], extras: Dict[str, Any]) -> None:
    for campo_int in ("quartos", "banheiros", "vagas"):
        item[campo_int] = _converter_int_positivo(item.get(campo_int))
    for campo_ext_int in ("suites", "salas"):
        extras[campo_ext_int] = _converter_int_positivo(extras.get(campo_ext_int))
    for campo_float in ("preco", "area_util", "area_total"):
        item[campo_float] = _converter_float_positivo(item.get(campo_float))


def normalizar_imovel(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza um dicionário de imóvel in-place e o retorna.
    """
    if not isinstance(item, dict):
        return item

    extras = item.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        item["extras"] = extras

    bairro_norm, cidade_norm = normalizar_localizacao(
        item.get("bairro"),
        item.get("cidade"),
        extras.get("logradouro"),
    )
    item["bairro"] = bairro_norm
    item["cidade"] = cidade_norm

    tipo_norm, subtipo_norm = normalizar_tipo_e_subtipo(
        item.get("tipo"),
        extras.get("subtipo"),
        item.get("titulo"),
    )
    item["tipo"] = tipo_norm
    if subtipo_norm:
        extras["subtipo"] = subtipo_norm

    if item.get("modalidade"):
        item["modalidade"] = str(item["modalidade"]).strip().upper()

    _sanitizar_campos_numericos(item, extras)

    titulo = str(item.get("titulo") or "").strip()
    if not titulo or "undefined" in titulo.lower():
        partes_loc = [p for p in [bairro_norm if bairro_norm != BAIRRO_NAO_INFORMADO else None, cidade_norm] if p]
        loc_str = " - ".join(partes_loc)
        item["titulo"] = f"{tipo_norm} em {loc_str}" if loc_str else tipo_norm

    return item
