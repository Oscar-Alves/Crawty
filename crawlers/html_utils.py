import re

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}


def extrair_preco(texto) -> float:
    if not texto:
        return 0.0
    texto_str = str(texto)
    match = re.search(r"(\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+(?:,\d{1,2})?)", texto_str)
    if not match:
        return 0.0
    limpo = match.group(1).replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return 0.0


def extrair_float(texto) -> float:
    if not texto:
        return 0.0
    texto_str = str(texto)
    match = re.search(r"(\d+(?:[.,]\d+)?)", texto_str)
    if not match:
        return 0.0
    val = match.group(1)
    if "," in val and "." in val:
        val = val.replace(".", "").replace(",", ".")
    else:
        val = val.replace(",", ".")
    try:
        return float(val)
    except ValueError:
        return 0.0


def extrair_int(texto) -> int:
    if not texto:
        return 0
    match = re.search(r"(\d+)", str(texto))
    if not match:
        return 0
    try:
        return int(match.group(1))
    except ValueError:
        return 0

