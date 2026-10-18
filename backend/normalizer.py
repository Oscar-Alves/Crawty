import re
import unicodedata
from typing import Dict, Any, Tuple, Optional


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
    "sao joao del rei": "São João del Rei",
    "sao joao del-rei": "São João del Rei",
    "sjdr": "São João del Rei",
    "tiradentes": "Tiradentes",
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
    "tremembe": "Tremembé",
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
    "colinas del rey": "Colinas Del Rey",
    "colinas del rei": "Colinas Del Rey",
    "condominio colinas del rey": "Colinas Del Rey",
    "colinas": "Colinas Del Rey",
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
    "vila nossa senhora de fatima": "Vila Nossa Senhora de Fátima",
    "vila nossa senhora fatima": "Vila Nossa Senhora de Fátima",
    "vila jardim nossa senhora de fatima": "Vila Nossa Senhora de Fátima",
    "alto das aguas": "Alto das Águas",
    "senhor dos montes": "Senhor dos Montes",
    "rio das mortes": "Rio das Mortes",
    "vila sao paulo": "Vila São Paulo",
    "vila joao lombardi": "Vila João Lombardi",
    "vila joao lombard": "Vila João Lombardi",
    "jardim colonia": "Jardim Colônia",
    "jardim coloniais": "Jardim Colônia",
    "condominio jardins coloniais numero 44": "Jardim Colônia",
    "rio acima": "Rio Acima",
    "jardim paulo campos": "Jardim Paulo Campos",
    "corrego do andre": "Córrego do André",
    "vila jardim sao jose": "Vila Jardim São José",
    "jardins da serra": "Jardins da Serra",
    "alto das merces": "Alto das Mercês",
    "nascente do sol": "Nascente do Sol",
    "residencial lenheiro": "Residencial Lenheiro",
    "residencial lenheiros": "Residencial Lenheiro",
    "lenheiros": "Residencial Lenheiro",
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
    "monte verde": "Monte Verde",
    "condominio monte verde": "Monte Verde",
    "cond monte verde": "Monte Verde",
    "nova colonia": "Nova Colônia",
    "vila del rei": "Vila Del Rei",
    "villa del rei colonia do marcal": "Vila Del Rei",
    "aguas ferreas": "Águas Férreas",
    "agua limpa": "Água Limpa",
    "araca": "Araçá",
    "caquende": "Caquende",
    "zona rural": "Zona Rural",
    "area rural": "Zona Rural",
    "area rural de sao joao del rei": "Zona Rural",
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
    "recanto da serra": "Recanto da Serra",
    "condominio recanto da serra": "Recanto da Serra",
    "condominio recanto serra": "Recanto da Serra",
    "residencial recanto da serra": "Recanto da Serra",
    "elvas": "Elvas",
    "elvas emboabas": "Elvas",
    "candonga": "Candonga",
    "candonga da serra": "Candonga",
    "candonga da serrra": "Candonga",
    "cascalho": "Cascalho",
    "santissima trindade": "Santíssima Trindade",
    "santissima": "Santíssima Trindade",
    "caixa d agua": "Caixa D'Água",
    "caixa d agua z rural": "Caixa D'Água",
    "caixa d agua da esperanca": "Caixa D'Água",
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
    "bichinho": "Bichinho",
    "vitoriano veloso": "Bichinho",
    "vitoriano veloso bichinho": "Bichinho",
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
    "tremenbe": "Tremembé",
    "tremembe": "Tremembé",
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
        return "São João del Rei"
    texto = str(cidade).strip()
    chave = _chave_comparacao(texto)
    if chave in CIDADES_CANONICAS:
        return CIDADES_CANONICAS[chave]
    return _formatar_titulo_bairro(texto)


def normalizar_localizacao(
    bairro_raw: Optional[str],
    cidade_raw: Optional[str],
    logradouro_raw: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Normaliza o par (bairro, cidade), corrigindo casos em que:
    - O bairro contém o nome da cidade + '/ MG' (ex: 'Bonfim São João del rei / MG', 'Bichinho Prados / MG')
    - Cidade e bairro foram invertidos (ex: cidade='Cuiabá', bairro='São João Del Rei')
    - O bairro possui sub-bairro/loteamento entre parênteses (ex: 'Colônia do Marçal (Solar da Serra)')
    - Há variações de grafia/acentuação/caixa (ex: 'Matozinhos' -> 'Matosinhos', 'COHAB' -> 'Cohab')
    """
    cidade = normalizar_cidade(cidade_raw)
    bairro = str(bairro_raw or "").strip()

    # Caso especial da Chaves Corretora: cidade='Cuiabá' e bairro='São João Del Rei'
    if _chave_comparacao(cidade) == "cuiaba" and _chave_comparacao(bairro) == "sao joao del rei":
        cidade = "São João del Rei"
        log_key = _chave_comparacao(logradouro_raw or "")
        if "bonfim" in log_key:
            return "Bonfim", cidade
        return "Não Informado", cidade

    # 1. Verifica se o bairro contém sufixo '/ UF' ou '/' no final (padrão Domicilium)
    if "/" in bairro and re.search(r"/\s*([A-Za-z]{2})?\s*$", bairro):
        sem_uf = re.sub(r"\s*/\s*([A-Za-z]{2})?\s*$", "", bairro).strip()
        sem_uf_norm = _chave_comparacao(sem_uf)
        # Procura qual cidade conhecida está no final da string
        cidades_ordenadas = sorted(CIDADES_CANONICAS.keys(), key=len, reverse=True)
        for cid_key in cidades_ordenadas:
            # Regex para remover a cidade do final do texto original preservando acentos do bairro
            padrao_cid = r"\s+" + r"\s+".join(re.escape(p) for p in cid_key.split()) + r"\s*$"
            if re.search(padrao_cid, sem_uf_norm):
                cidade = CIDADES_CANONICAS[cid_key]
                # Remove os últimos N tokens correspondentes à cidade
                qtd_palavras_cid = len(cid_key.split())
                tokens_orig = sem_uf.replace("-", " ").split()
                if len(tokens_orig) > qtd_palavras_cid:
                    # Usa regex insensível a acento/caixa sobre sem_uf
                    partes = sem_uf.split()
                    bairro = " ".join(partes[:-qtd_palavras_cid]).strip()
                else:
                    bairro = "Não Informado"
                break
        else:
            bairro = sem_uf

    # 2. Limpeza básica de pontuação espúria
    bairro = re.sub(r"\s+", " ", bairro).strip(" ,.-")
    if not bairro:
        return "Não Informado", cidade

    # 3. Tratamento de parênteses: 'A (B)' -> extrair o loteamento/bairro específico
    m_paren = re.match(r"^(.+?)\s*\((.+?)\)\s*$", bairro)
    if m_paren:
        parte_a = m_paren.group(1).strip()
        parte_b = m_paren.group(2).strip()
        key_a = _chave_comparacao(parte_a)
        key_b = _chave_comparacao(parte_b)

        if key_a == "vitoriano veloso" or key_b == "bichinho":
            bairro = "Bichinho"
        elif key_a in BAIRROS_MACRO_KEYS:
            # Ex: 'Colônia do Marçal (Solar da Serra)' -> 'Solar da Serra'
            bairro = parte_b
        elif key_b in BAIRROS_MACRO_KEYS or key_b in {"alto das aguas", "ilha do governador", "venda nova"}:
            # Ex: 'Solar da Serra (Colônia do Marçal)' -> 'Solar da Serra'
            bairro = parte_a
        else:
            bairro = parte_b

    # 4. Verifica chave normalizada para mapeamentos diretos e valores vazios/inválidos
    chave_b = _chave_comparacao(bairro)
    chave_c = _chave_comparacao(cidade)

    if (
        not chave_b
        or chave_b in {"nao informado", "n i", "bairro", "fim comercial", "condominio", "undefined"}
        or chave_b == chave_c
    ):
        return "Não Informado", cidade

    # Casos onde 'Ritapolis' repetiu no bairro
    if chave_b == "ritapolis" and chave_c == "ritapolis":
        return "Não Informado", cidade

    if chave_b in BAIRROS_CANONICOS:
        bairro_final = BAIRROS_CANONICOS[chave_b]
    elif bairro.isupper() or bairro.islower():
        bairro_final = _formatar_titulo_bairro(bairro)
    else:
        # Garante primeira letra maiúscula
        bairro_final = bairro[0].upper() + bairro[1:]

    # Se o bairro é claramente de Tiradentes mas cidade veio vazia
    if not cidade_raw and bairro_final in {"César de Pina", "Águas Santas", "Candonga"}:
        cidade = "Tiradentes"

    return bairro_final, cidade


def normalizar_tipo_e_subtipo(
    tipo_raw: Optional[str],
    subtipo_raw: Optional[str] = None,
    titulo_raw: Optional[str] = None,
) -> Tuple[str, Optional[str]]:
    """
    Normaliza `tipo` nas categorias principais:
      - Casa
      - Apartamento
      - Terreno
      - Comercial
      - Rural
      - Kitnet
    Preservando e enriquecendo o detalhe em `subtipo`.
    """
    tipo_str = str(tipo_raw or "").strip()
    subtipo_str = str(subtipo_raw or "").strip() if subtipo_raw else None
    titulo_str = str(titulo_raw or "").strip()

    tk = _chave_comparacao(tipo_str)
    sk = _chave_comparacao(subtipo_str or "")
    tit_k = _chave_comparacao(titulo_str)

    # Normaliza subtipo se estiver todo maiúsculo ou vazio
    if subtipo_str and subtipo_str.lower() in {"none", "null", ""}:
        subtipo_str = None
    elif subtipo_str == "Casa de condomínio":
        subtipo_str = "Casa de Condomínio"
    elif subtipo_str == "Casa de vila":
        subtipo_str = "Casa de Vila"
    elif subtipo_str == "Duplex/triplex":
        subtipo_str = "Duplex/Triplex"
    elif subtipo_str == "Sítios e chácaras":
        subtipo_str = "Sítio"

    # 1. Prioridade por subtipo específico quando o tipo é agrupado (ex: 'Terrenos, sítios e fazendas' ou 'Apartamento' com 'Kitnet')
    if sk == "kitnet" or tk == "kitnet":
        return "Kitnet", "Kitnet"

    if sk in {"sitio", "chacara", "fazenda", "sitios e chacaras"}:
        sub_map = {"sitio": "Sítio", "chacara": "Chácara", "fazenda": "Fazenda", "sitios e chacaras": "Sítio"}
        return "Rural", sub_map.get(sk, subtipo_str)

    if sk in {"lote", "lote de condominio", "terreno"}:
        return "Terreno", subtipo_str or ("Lote" if tk == "lote" else "Terreno")

    # 2. Mapeamento pelo tipo principal
    if tk in {"casa", "chale"}:
        if tk == "chale" and (not subtipo_str or subtipo_str == "Padrão"):
            subtipo_str = "Chalé"
        return "Casa", subtipo_str

    if tk == "apartamento":
        if subtipo_str == "Apartamento":
            subtipo_str = "Padrão"
        return "Apartamento", subtipo_str

    if tk in {"lote", "terreno", "terrenos sitios e fazendas"}:
        if tk == "lote" and (not subtipo_str or subtipo_str == "Padrão"):
            subtipo_str = "Lote"
        elif not subtipo_str:
            subtipo_str = "Terreno"
        return "Terreno", subtipo_str

    if tk in {
        "comercio",
        "comercial",
        "comercio e industria",
        "ponto comercial",
        "sala comercial",
        "galpao",
        "pousada",
        "temporada",
    }:
        if tk == "ponto comercial" and not subtipo_str:
            subtipo_str = "Ponto Comercial"
        elif tk == "sala comercial" and not subtipo_str:
            subtipo_str = "Sala Comercial"
        elif tk == "galpao" and not subtipo_str:
            subtipo_str = "Galpão/Depósito"
        elif tk in {"pousada", "temporada"} and (not subtipo_str or subtipo_str == "Padrão"):
            subtipo_str = "Pousada"
        return "Comercial", subtipo_str

    if tk in {"rural", "sitio", "chacara", "fazenda"}:
        if tk == "sitio" and not subtipo_str:
            subtipo_str = "Sítio"
        return "Rural", subtipo_str or "Sítio"

    # 3. Quando o tipo é genérico ('Imovel', 'Imóvel', 'IMÓVEL PARA ACABAMENTO', etc.), inferimos pelo título
    if "kitnet" in tit_k or "conjugado" in tit_k:
        return "Kitnet", "Kitnet"
    if "cobertura" in tit_k:
        return "Apartamento", "Cobertura"
    if "loft" in tit_k:
        return "Apartamento", "Loft"
    if "studio" in tit_k or "flat" in tit_k:
        return "Apartamento", "Studio"
    if "apartamento" in tit_k or "apto" in tit_k:
        return "Apartamento", subtipo_str or "Padrão"
    if "sitio" in tit_k:
        return "Rural", "Sítio"
    if "fazenda" in tit_k:
        return "Rural", "Fazenda"
    if "chacara" in tit_k:
        return "Rural", "Chácara"
    if "galpao" in tit_k or "deposito" in tit_k:
        return "Comercial", "Galpão/Depósito"
    if "pousada" in tit_k:
        return "Comercial", "Pousada"
    if "hotel" in tit_k:
        return "Comercial", "Hotel"
    if "loja" in tit_k:
        return "Comercial", "Loja"
    if "sala" in tit_k or "escritorio" in tit_k or "consultorio" in tit_k:
        return "Comercial", "Sala Comercial"
    if "ponto comercial" in tit_k or "comercial" in tit_k or "predio" in tit_k:
        return "Comercial", subtipo_str or "Ponto Comercial"
    if "lote" in tit_k or "terreno" in tit_k:
        return "Terreno", "Lote" if "lote" in tit_k else "Terreno"

    return "Casa", subtipo_str or "Padrão"


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

    logradouro = extras.get("logradouro")
    bairro_norm, cidade_norm = normalizar_localizacao(
        item.get("bairro"),
        item.get("cidade"),
        logradouro,
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

    # Modalidade sempre em UPPERCASE ('VENDA' ou 'ALUGUEL')
    if item.get("modalidade"):
        item["modalidade"] = str(item["modalidade"]).strip().upper()

    # Garante numéricos limpos
    for campo_int in ("quartos", "banheiros", "vagas"):
        try:
            item[campo_int] = max(0, int(item.get(campo_int) or 0))
        except (ValueError, TypeError):
            item[campo_int] = 0

    for campo_ext_int in ("suites", "salas"):
        try:
            extras[campo_ext_int] = max(0, int(extras.get(campo_ext_int) or 0))
        except (ValueError, TypeError):
            extras[campo_ext_int] = 0

    for campo_float in ("preco", "area_util", "area_total"):
        try:
            item[campo_float] = max(0.0, float(item.get(campo_float) or 0.0))
        except (ValueError, TypeError):
            item[campo_float] = 0.0

    # Corrige título com 'undefined'
    titulo = str(item.get("titulo") or "").strip()
    if not titulo or "undefined" in titulo.lower():
        partes_loc = [p for p in [bairro_norm if bairro_norm != "Não Informado" else None, cidade_norm] if p]
        loc_str = " - ".join(partes_loc)
        item["titulo"] = f"{tipo_norm} em {loc_str}" if loc_str else tipo_norm

    return item
