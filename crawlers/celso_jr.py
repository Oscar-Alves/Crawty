import logging
import requests
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class CelsoJrCrawler:
    """
    Crawler para Celso Jr. Imóveis (https://celsojrimoveis.com.br/).
    """

    def __init__(self):
        self.site_url = "https://celsojrimoveis.com.br"
        self.ajax_url = f"{self.site_url}/fetch_pages.php"

    def _extrair_cidade_e_titulo(self, loc_txt: str, tipo: str, bairro: str):
        partes = [p.strip() for p in loc_txt.split("-") if p.strip()]
        if len(partes) >= 3:
            return partes[0], partes[1]
        if len(partes) == 2:
            return partes[0], f"{tipo} em {bairro}"
        return loc_txt or "São João del Rei", f"{tipo} em {bairro}"

    @staticmethod
    def _obter_texto(element, seletor: str, padrao: str = "") -> str:
        if not element:
            return padrao
        el = element.select_one(seletor)
        return el.get_text(" ", strip=True) if el else padrao

    @staticmethod
    def _extrair_fotos(block) -> list:
        fotos = []
        for img in block.select(".image-box img"):
            src = img.get("src", "")
            if src and src not in fotos:
                fotos.append(src)
        return fotos

    @staticmethod
    def _extrair_modalidade(block) -> str:
        feat_el = block.select_one("span.featured") or block.select_one("span.for")
        mod_txt = (feat_el.get_text(" ", strip=True) if feat_el else "VENDA").upper()
        return "ALUGUEL" if "ALUG" in mod_txt else "VENDA"

    def _determinar_link(self, href: str, cod: str) -> str:
        if href.startswith("/"):
            return f"{self.site_url}{href}"
        return href or f"{self.site_url}/imovel/{cod}"

    def _padronizar_card(self, block):
        info_txt = self._obter_texto(block, "ul.info")
        a_el = block.find("a", href=True)
        href = a_el.get("href", "") if a_el else ""
        cod = str(extrair_int(info_txt) or extrair_int(href))
        if not cod or cod == "0":
            return None

        tipo = self._obter_texto(block, "ul.tags li", "Imóvel")
        bairro = self._obter_texto(block, ".lower-content h3", "Não Informado")
        loc_txt = self._obter_texto(block, ".lucation")
        cidade, titulo = self._extrair_cidade_e_titulo(loc_txt, tipo, bairro)

        preco_txt = self._obter_texto(block, ".property-price")
        preco = extrair_preco(preco_txt)
        link = self._determinar_link(href, cod)

        return normalizar_imovel({
            "id_unico": f"CelsoJr_{cod}",
            "imobiliaria": "Celso Jr. Imóveis",
            "codigo_original": cod,
            "titulo": titulo,
            "modalidade": self._extrair_modalidade(block),
            "tipo": tipo,
            "preco": preco,
            "bairro": bairro,
            "cidade": cidade,
            "quartos": 0,
            "banheiros": 0,
            "vagas": 0,
            "area_util": 0.0,
            "area_total": 0.0,
            "link": link,
            "fotos": self._extrair_fotos(block),
            "extras": {}
        })

    def _processar_cards(self, cards, vistos: set, destino: list) -> int:
        novos = 0
        for card in cards:
            try:
                item = self._padronizar_card(card)
                if item and item["id_unico"] not in vistos:
                    vistos.add(item["id_unico"])
                    destino.append(item)
                    novos += 1
            except Exception:
                logging.exception("Erro ao padronizar card Celso Jr.")
        return novos

    def buscar_imoveis(self):
        imoveis = []
        vistos = set()
        logging.info("--- Celso Jr. Imóveis: Coletando imóveis ---")
        for page in range(1, 20):
            try:
                resp = requests.post(
                    self.ajax_url,
                    data={"page": page},
                    headers=DEFAULT_HEADERS,
                    timeout=20,
                )
                if resp.status_code != 200 or not resp.text.strip():
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.property-block")
                if not cards:
                    break
                if self._processar_cards(cards, vistos, imoveis) == 0:
                    break
            except Exception:
                logging.exception(f"Erro Celso Jr. página {page}")
                break
        return imoveis


if __name__ == "__main__":
    c = CelsoJrCrawler()
    res = c.buscar_imoveis()
    print(f"Total Celso Jr.: {len(res)}")

