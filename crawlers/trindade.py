import logging
import requests
import urllib3
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_int

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TrindadeCrawler:
    """
    Crawler para Imobiliária Trindade (https://imobiliariatrindadesjdr.com.br/imoveis).
    """

    def __init__(self):
        self.site_url = "https://imobiliariatrindadesjdr.com.br"
        self.ajax_url = f"{self.site_url}/fetch_pages.php"

    def _padronizar_card(self, card):
        a_el = card.find("a", href=True)
        href = a_el.get("href", "") if a_el else ""
        cod = str(extrair_int(card.get_text(" ", strip=True)) or extrair_int(href))
        if not cod or cod == "0":
            return None

        img_el = card.find("img")
        foto = img_el.get("src", "") if img_el else ""
        preco = extrair_preco(card.get_text(" ", strip=True))
        link = f"{self.site_url}{href}" if href.startswith("/") else (href or f"{self.site_url}/imovel/{cod}")

        return normalizar_imovel({
            "id_unico": f"Trindade_{cod}",
            "imobiliaria": "Imobiliária Trindade",
            "codigo_original": cod,
            "titulo": f"Imóvel {cod}",
            "modalidade": "VENDA",
            "tipo": "Imóvel",
            "preco": preco,
            "bairro": "Não Informado",
            "cidade": "São João del Rei",
            "quartos": 0,
            "banheiros": 0,
            "vagas": 0,
            "area_util": 0.0,
            "area_total": 0.0,
            "link": link,
            "fotos": [foto] if foto else [],
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
                logging.exception("Erro ao padronizar card Imobiliária Trindade")
        return novos

    def buscar_imoveis(self):
        imoveis = []
        vistos = set()
        logging.info("--- Imobiliária Trindade: Coletando imóveis ---")
        for page in range(1, 10):
            try:
                resp = requests.post(
                    self.ajax_url,
                    data={"page": page, "PrimeiraBusca": "S" if page == 1 else "N"},
                    headers=DEFAULT_HEADERS,
                    verify=False,
                    timeout=15,
                )
                if resp.status_code != 200 or not resp.text.strip():
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.property, div.property-block, article.property-item")
                if not cards:
                    break
                if self._processar_cards(cards, vistos, imoveis) == 0:
                    break
            except Exception:
                logging.exception(f"Erro Imobiliária Trindade página {page}")
                break
        return imoveis


if __name__ == "__main__":
    c = TrindadeCrawler()
    res = c.buscar_imoveis()
    print(f"Total Imobiliária Trindade: {len(res)}")

