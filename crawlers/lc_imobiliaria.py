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

    @staticmethod
    def _obter_texto(el, seletor: str, padrao: str = "") -> str:
        if not el:
            return padrao
        target = el.select_one(seletor)
        return target.get_text(" ", strip=True) if target else padrao

    @staticmethod
    def _extrair_codigo(art, href: str) -> str:
        for h3 in art.select("h3.attribute-title"):
            txt = h3.get_text(" ", strip=True)
            if "Cód" in txt or "Cod" in txt:
                return str(extrair_int(txt))
        return str(extrair_int(href) or "")

    def _padronizar_card(self, art):
        img_a = art.select_one(".property-images a")
        href = img_a.get("href", "") if img_a else ""
        img_el = art.select_one(".property-images img")
        foto = img_el.get("src", "") if img_el else ""

        cod = self._extrair_codigo(art, href)
        if not cod or cod == "0":
            return None

        title_a = art.select_one(".property-attribute h3.attribute-title a")
        bold_txt = self._obter_texto(title_a, "b")
        modalidade, tipo = self._extrair_modalidade_e_tipo(bold_txt)
        bairro = self._extrair_bairro_card(title_a)
        titulo = (title_a.get("title") if title_a else None) or f"{tipo} em {bairro}"

        cidade = self._obter_texto(art, ".attribute-city", "São João del Rei")
        preco = extrair_preco(self._obter_texto(art, ".attr-pricing"))

        area = extrair_float(self._obter_texto(art, ".meta-size .meta-text"))
        quartos = extrair_int(self._obter_texto(art, ".meta-bedroom .meta-text"))
        banheiros = extrair_int(self._obter_texto(art, ".meta-bathroom .meta-text"))
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
            "quartos": quartos,
            "banheiros": banheiros,
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

