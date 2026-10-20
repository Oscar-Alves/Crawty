import logging
import requests
import urllib3
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_int

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class SavioCrawler:
    """
    Crawler para Sávio Corretor de Imóveis (https://www.saviocorretor.com.br/).
    """

    def __init__(self):
        self.site_url = "https://www.saviocorretor.com.br"
        self.ajax_url = f"{self.site_url}/fetch_pages.php"

    def _padronizar_card(self, card):
        a_img = card.select_one("a.property-img")
        link = a_img.get("href", "") if a_img else ""

        status_el = card.select_one(".property-tag.status")
        cod = str(extrair_int(status_el.get_text(" ", strip=True) if status_el else "") or extrair_int(link))
        if not cod or cod == "0":
            return None

        price_el = card.select_one(".property-price")
        preco = extrair_preco(price_el.get_text(" ", strip=True) if price_el else "")

        img_el = card.select_one("a.property-img img")
        foto = img_el.get("src", "") if img_el else ""

        tipo_el = card.select_one(".property-title h4")
        tipo = tipo_el.get_text(" ", strip=True) if tipo_el else "Imóvel"

        addrs = [p.get_text(" ", strip=True) for p in card.select("p.property-address") if p.get_text(" ", strip=True)]
        if len(addrs) >= 2:
            bairro, cidade = addrs[0], addrs[1]
        elif len(addrs) == 1:
            bairro, cidade = addrs[0], "São João del Rei"
        else:
            bairro, cidade = "Não Informado", "São João del Rei"

        footer_el = card.select_one(".property-footer")
        mod_txt = (footer_el.get_text(" ", strip=True) if footer_el else "VENDA").upper()
        modalidade = "ALUGUEL" if "ALUG" in mod_txt else "VENDA"

        return normalizar_imovel({
            "id_unico": f"Savio_{cod}",
            "imobiliaria": "Sávio Corretor",
            "codigo_original": cod,
            "titulo": f"{tipo} em {bairro}",
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
            "link": link or f"{self.site_url}/imovel/{cod}/1",
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
                logging.exception("Erro ao padronizar card Sávio Corretor")
        return novos

    def buscar_imoveis(self):
        imoveis = []
        vistos = set()
        logging.info("--- Sávio Corretor: Coletando imóveis ---")
        for page in range(1, 30):
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
                cards = soup.select("div.property")
                if not cards:
                    break
                if self._processar_cards(cards, vistos, imoveis) == 0:
                    break
            except Exception:
                logging.exception(f"Erro Sávio Corretor página {page}")
                break
        return imoveis


if __name__ == "__main__":
    c = SavioCrawler()
    res = c.buscar_imoveis()
    print(f"Total Sávio Corretor: {len(res)}")

