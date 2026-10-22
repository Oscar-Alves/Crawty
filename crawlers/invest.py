import logging
import requests
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_float, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class InvestCrawler:
    """
    Crawler para Invest Imóveis (https://www.investimoveissjdr.com.br/).
    """

    def __init__(self):
        self.site_url = "https://www.investimoveissjdr.com.br"
        self.page_url = f"{self.site_url}/imoveis/pagina-{{}}/"

    def _extrair_detalhes(self, card):
        specs = {"quartos": 0, "banheiros": 0, "vagas": 0, "area": 0.0, "ref": ""}
        for div in card.select(".detalhes div"):
            title = (div.get("title") or "").lower()
            txt = div.get_text(" ", strip=True)
            if "dormit" in title:
                specs["quartos"] = extrair_int(txt)
            elif "banheiro" in title:
                specs["banheiros"] = extrair_int(txt)
            elif "vaga" in title:
                specs["vagas"] = extrair_int(txt)
            elif "área" in title or "area" in title:
                specs["area"] = extrair_float(txt)
            elif "ref" in txt.lower():
                specs["ref"] = str(extrair_int(txt))
        return specs

    @staticmethod
    def _obter_texto(card, seletor: str, padrao: str = "") -> str:
        el = card.select_one(seletor)
        return el.get_text(strip=True) if el else padrao

    @staticmethod
    def _determinar_modalidade(card) -> str:
        mod_el = card.select_one(".valor small")
        mod_raw = mod_el.get_text(strip=True).upper() if mod_el else "VENDA"
        return "ALUGUEL" if ("LOCA" in mod_raw or "ALUG" in mod_raw) else "VENDA"

    def _padronizar_card(self, card):
        card_id = card.get("id") or ""
        a_el = card.select_one(".foto a")
        href = a_el.get("href", "") if a_el else ""
        img_el = card.select_one(".foto img")
        foto = img_el.get("src", "") if img_el else ""

        specs = self._extrair_detalhes(card)
        cod = specs["ref"] or str(card_id).strip()
        if not cod:
            return None

        tipo = self._obter_texto(card, "h3.tipo", "Imóvel")
        cidade_raw = self._obter_texto(card, "h4.cidade", "São João del Rei")
        cidade = cidade_raw.split("-")[0].strip()
        bairro = self._obter_texto(card, "h4.bairro", "Não Informado")
        modalidade = self._determinar_modalidade(card)
        preco = extrair_preco(self._obter_texto(card, ".valor h5"))
        link = f"{self.site_url}{href}" if href.startswith("/") else href
        titulo = (img_el.get("title") if img_el else None) or f"{tipo} em {bairro}"

        return normalizar_imovel({
            "id_unico": f"Invest_{cod}",
            "imobiliaria": "Invest Imóveis",
            "codigo_original": cod,
            "titulo": titulo.capitalize(),
            "modalidade": modalidade,
            "tipo": tipo,
            "preco": preco,
            "bairro": bairro,
            "cidade": cidade,
            "quartos": specs["quartos"],
            "banheiros": specs["banheiros"],
            "vagas": specs["vagas"],
            "area_util": specs["area"],
            "area_total": specs["area"],
            "link": link,
            "fotos": [foto] if foto else [],
            "extras": {}
        })

    def _processar_pagina(self, cards, vistos, imoveis) -> int:
        novos = 0
        for card in cards:
            try:
                item = self._padronizar_card(card)
                if item and item["id_unico"] not in vistos:
                    vistos.add(item["id_unico"])
                    imoveis.append(item)
                    novos += 1
            except Exception:
                logging.exception("Erro ao padronizar card Invest Imóveis")
        return novos

    def buscar_imoveis(self):
        imoveis = []
        vistos = set()
        logging.info("--- Invest Imóveis: Coletando imóveis ---")
        for page in range(1, 50):
            try:
                resp = requests.get(self.page_url.format(page), headers=DEFAULT_HEADERS, timeout=20)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.resultado")
                if not cards:
                    break
                novos = self._processar_pagina(cards, vistos, imoveis)
                if novos == 0:
                    break
            except Exception:
                logging.exception(f"Erro na página {page} de Invest Imóveis")
                break
        return imoveis


if __name__ == "__main__":
    c = InvestCrawler()
    res = c.buscar_imoveis()
    print(f"Total Invest Imóveis: {len(res)}")

