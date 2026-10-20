import logging
import re
import requests
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_float, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class LCImobiliariaCrawler:
    """
    Crawler para LC Imobiliária (https://www.lcimobiliaria.com.br/imoveis).
    """

    def __init__(self):
        self.site_url = "https://www.lcimobiliaria.com.br"
        self.list_url = f"{self.site_url}/imoveis"

    def _extrair_modalidade_e_tipo(self, bold_text: str):
        partes = bold_text.strip().split(None, 1)
        if not partes:
            return "VENDA", "Imóvel"
        mod = "ALUGUEL" if "ALUG" in partes[0].upper() else "VENDA"
        tipo = partes[1].strip() if len(partes) > 1 else "Imóvel"
        return mod, tipo

    def _extrair_bairro_card(self, link_el):
        if not link_el:
            return "Não Informado"
        textos = [t.strip() for t in link_el.stripped_strings]
        return textos[-1] if len(textos) > 1 else "Não Informado"

    def _padronizar_card(self, art):
        img_a = art.select_one(".property-images a")
        href = img_a.get("href", "") if img_a else ""
        img_el = art.select_one(".property-images img")
        foto = img_el.get("src", "") if img_el else ""

        cod_text = ""
        for h3 in art.select("h3.attribute-title"):
            txt = h3.get_text(" ", strip=True)
            if "Cód" in txt or "Cod" in txt:
                cod_text = txt
                break
        cod = str(extrair_int(cod_text) or extrair_int(href))
        if not cod or cod == "0":
            return None

        title_a = art.select_one(".property-attribute h3.attribute-title a")
        bold_el = title_a.find("b") if title_a else None
        modalidade, tipo = self._extrair_modalidade_e_tipo(bold_el.get_text(" ", strip=True) if bold_el else "")
        bairro = self._extrair_bairro_card(title_a)
        titulo = (title_a.get("title") if title_a else None) or f"{tipo} em {bairro}"

        cidade_el = art.select_one(".attribute-city")
        cidade = cidade_el.get_text(strip=True) if cidade_el else "São João del Rei"

        preco_el = art.select_one(".attr-pricing")
        preco = extrair_preco(preco_el.get_text(" ", strip=True) if preco_el else "")

        area_el = art.select_one(".meta-size .meta-text")
        quartos_el = art.select_one(".meta-bedroom .meta-text")
        banheiros_el = art.select_one(".meta-bathroom .meta-text")

        area = extrair_float(area_el.get_text(strip=True) if area_el else "")
        link_completo = f"{self.site_url}{href}" if href.startswith("/") else href

        return normalizar_imovel({
            "id_unico": f"LC_{cod}",
            "imobiliaria": "LC Imobiliária",
            "codigo_original": cod,
            "titulo": titulo,
            "modalidade": modalidade,
            "tipo": tipo,
            "preco": preco,
            "bairro": bairro,
            "cidade": cidade,
            "quartos": extrair_int(quartos_el.get_text(strip=True) if quartos_el else ""),
            "banheiros": extrair_int(banheiros_el.get_text(strip=True) if banheiros_el else ""),
            "vagas": 0,
            "area_util": area,
            "area_total": area,
            "link": link_completo,
            "fotos": [foto] if foto else [],
            "extras": {}
        })

    def buscar_imoveis(self):
        imoveis = []
        vistos = set()
        logging.info("--- LC Imobiliária: Coletando imóveis ---")
        try:
            resp = requests.get(self.list_url, headers=DEFAULT_HEADERS, timeout=25)
            if resp.status_code != 200:
                logging.error(f"Erro HTTP {resp.status_code} em LC Imobiliária")
                return imoveis
            soup = BeautifulSoup(resp.text, "html.parser")
            for art in soup.select("article.property-item"):
                try:
                    item = self._padronizar_card(art)
                    if item and item["id_unico"] not in vistos:
                        vistos.add(item["id_unico"])
                        imoveis.append(item)
                except Exception:
                    logging.exception("Erro ao padronizar card LC Imobiliária")
        except Exception:
            logging.exception("Erro ao buscar imóveis LC Imobiliária")
        return imoveis


if __name__ == "__main__":
    c = LCImobiliariaCrawler()
    res = c.buscar_imoveis()
    print(f"Total LC Imobiliária: {len(res)}")

