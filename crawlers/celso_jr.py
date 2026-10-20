import logging
import requests
import urllib3
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_int

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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

    def _padronizar_card(self, block):
        info_el = block.select_one("ul.info")
        a_el = block.find("a", href=True)
        href = a_el.get("href", "") if a_el else ""
        cod = str(extrair_int(info_el.get_text(" ", strip=True) if info_el else "") or extrair_int(href))
        if not cod or cod == "0":
            return None

        fotos = []
        for img in block.select(".image-box img"):
            src = img.get("src", "")
            if src and src not in fotos:
                fotos.append(src)

        feat_el = block.select_one("span.featured") or block.select_one("span.for")
        mod_txt = (feat_el.get_text(" ", strip=True) if feat_el else "VENDA").upper()
        modalidade = "ALUGUEL" if "ALUG" in mod_txt else "VENDA"

        tag_el = block.select_one("ul.tags li")
        tipo = tag_el.get_text(" ", strip=True) if tag_el else "Imóvel"

        h3_el = block.select_one(".lower-content h3")
        bairro = h3_el.get_text(" ", strip=True) if h3_el else "Não Informado"

        loc_el = block.select_one(".lucation")
        loc_txt = loc_el.get_text(" ", strip=True) if loc_el else ""
        cidade, titulo = self._extrair_cidade_e_titulo(loc_txt, tipo, bairro)

        price_el = block.select_one(".property-price")
        preco = extrair_preco(price_el.get_text(" ", strip=True) if price_el else "")
        link = f"{self.site_url}{href}" if href.startswith("/") else (href or f"{self.site_url}/imovel/{cod}")

        return normalizar_imovel({
            "id_unico": f"CelsoJr_{cod}",
            "imobiliaria": "Celso Jr. Imóveis",
            "codigo_original": cod,
            "titulo": titulo,
            "modalidade": modalidade,
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
            "fotos": fotos,
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
                    verify=False,
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

