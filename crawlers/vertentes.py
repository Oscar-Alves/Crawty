import logging
import requests
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_float, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class VertentesCrawler:
    """
    Crawler para Vertentes Imóveis (https://vertentesimoveis.com.br/).
    """

    def __init__(self):
        self.site_url = "https://vertentesimoveis.com.br"

    def _extrair_specs(self, card):
        specs = {"area": 0.0, "suites": 0, "quartos": 0, "banheiros": 0, "vagas": 0}
        for span in card.select("span[data-tooltip]"):
            tip = (span.get("data-tooltip") or "").lower()
            txt = span.get_text(" ", strip=True)
            if "área" in tip or "area" in tip:
                specs["area"] = extrair_float(txt)
            elif "suite" in tip:
                specs["suites"] = extrair_int(txt)
            elif "quarto" in tip:
                specs["quartos"] = extrair_int(txt)
            elif "banheiro" in tip:
                specs["banheiros"] = extrair_int(txt)
            elif "vaga" in tip:
                specs["vagas"] = extrair_int(txt)
        return specs

    def _extrair_tipo_e_cod(self, card, href: str):
        tipo = card.get("data-gtm-name") or "Imóvel"
        cod = ""
        for p in card.select(".content .row p"):
            txt = p.get_text(" ", strip=True)
            if "cod" in txt.lower():
                cod = str(extrair_int(txt))
            elif txt and not tipo:
                tipo = txt
        if not cod:
            cod = str(extrair_int(href))
        return tipo, cod

    def _padronizar_card(self, card, modalidade: str):
        href = card.get("href", "")
        tipo, cod = self._extrair_tipo_e_cod(card, href)
        if not cod or cod == "0":
            return None

        img_el = card.select_one("img.img-cover")
        foto = img_el.get("src", "") if img_el else ""

        titulo_el = card.select_one("h2")
        titulo = titulo_el.get_text(" ", strip=True) if titulo_el else f"{tipo} {cod}"

        loc_el = card.select_one("p.text-muted.small")
        loc_txt = loc_el.get_text(" ", strip=True) if loc_el else ""
        if "," in loc_txt:
            bairro, cidade = [p.strip() for p in loc_txt.split(",", 1)]
        else:
            bairro, cidade = loc_txt or "Não Informado", "São João del Rei"

        preco_el = card.select_one("h3")
        preco = extrair_preco(preco_el.get_text(" ", strip=True) if preco_el else "")
        specs = self._extrair_specs(card)
        link = f"{self.site_url}{href}" if href.startswith("/") else href

        return normalizar_imovel({
            "id_unico": f"Vertentes_{cod}",
            "imobiliaria": "Vertentes Imóveis",
            "codigo_original": cod,
            "titulo": titulo,
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
            "extras": {"suites": specs["suites"]}
        })

    def _processar_cards(self, cards, modalidade: str, vistos: set, destino: list) -> int:
        novos = 0
        for card in cards:
            try:
                item = self._padronizar_card(card, modalidade)
                if item and item["id_unico"] not in vistos:
                    vistos.add(item["id_unico"])
                    destino.append(item)
                    novos += 1
            except Exception:
                logging.exception("Erro ao padronizar card Vertentes Imóveis")
        return novos

    def _coletar_modalidade(self, slug: str, modalidade: str, vistos: set):
        coletados = []
        logging.info(f"--- Vertentes Imóveis: {modalidade} ---")
        for page in range(1, 40):
            url = f"{self.site_url}/imoveis/{slug}?page={page}"
            try:
                resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select('a[data-gtm-clicktype="card"]')
                if not cards:
                    break
                if self._processar_cards(cards, modalidade, vistos, coletados) == 0:
                    break
            except Exception:
                logging.exception(f"Erro Vertentes Imóveis {modalidade} página {page}")
                break
        return coletados

    def buscar_imoveis(self):
        todos = []
        vistos = set()
        todos.extend(self._coletar_modalidade("compra", "VENDA", vistos))
        todos.extend(self._coletar_modalidade("aluguel", "ALUGUEL", vistos))
        return todos


if __name__ == "__main__":
    c = VertentesCrawler()
    res = c.buscar_imoveis()
    print(f"Total Vertentes Imóveis: {len(res)}")

