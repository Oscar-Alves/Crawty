import re

PADRAO_HOMECLIX_S3 = re.compile(
    r"^https?://(?:(?:homeclix|crmdataclix)\.s3(?:\.[a-z0-9-]+)?\.amazonaws\.com/homeclix/|"
    r"s3(?:\.[a-z0-9-]+)?\.amazonaws\.com/(?:homeclix|crmdataclix)/homeclix/)",
    re.IGNORECASE,
)
BUNNY_CDN_HOMECLIX = "https://homeclix.b-cdn.net/"


def normalizar_url_foto(url: str) -> str:
    """
    Substitui endpoints privados/bloqueados do S3 da Homeclix/DataClix
    pelo endereço público oficial BunnyCDN (https://homeclix.b-cdn.net/).
    """
    if not url or not isinstance(url, str):
        return ""
    limpa = url.strip()
    if PADRAO_HOMECLIX_S3.search(limpa):
        return PADRAO_HOMECLIX_S3.sub(BUNNY_CDN_HOMECLIX, limpa)
    return limpa

