import logging
import re
import requests
import urllib3
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_int

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class CarazzaCrawler:
    """
    Crawler para Carazza Imóveis (https://www.carazzaimoveis.com.br/).
    """

    def __init__(self):
        self.site_url = "https://www.carazzaimoveis.com.br"
        self.destaques_url = f"{self.site_url}/ImoveisDestaques.php"
        self.busca_url = f"{self.site_url}/busca"

    def _extrair_tipo_e_quartos(self, h3_txt: str):
        quartos = 0
        match_q = re.search(r"\((\d+)\s*Qts?\)", h3_txt, re.I)
        if match_q:
            quartos = int(match_q.group(1))
        tipo = re.sub(r"\(.*?\)", "", h3_txt).strip() or "Imóvel"
        return tipo, quartos

    def _padronizar_card(self, prop, modalidade_padrao="VENDA"):
        a_el = prop.select_one("a.ModalImovel") or prop.find("a")
        cod = (a_el.get("id_imovel") if a_el else None) or ""
        if not cod:
            hdr = prop.select_one(".additional-info header")
            cod = str(extrair_int(hdr.get_text(" ", strip=True) if hdr else ""))
        cod = str(cod).strip()
        if not cod or cod == "0":
            return None

        img_el = prop.select_one(".property-image img")
        foto = img_el.get("src", "") if img_el else ""

        price_el = prop.select_one(".info .tag.price")
        preco = extrair_preco(price_el.get_text(" ", strip=True) if price_el else "")

        h3s = prop.select(".info h3")
        tipo_txt = h3s[0].get_text(" ", strip=True) if h3s else "Imóvel"
        tipo, quartos = self._extrair_tipo_e_quartos(tipo_txt)
        bairro = h3s[1].get_text(" ", strip=True) if len(h3s) > 1 else "Não Informado"

        fig_el = prop.select_one(".info figure")
        cidade = fig_el.get_text(" ", strip=True) if fig_el else "São João del Rei"

        return normalizar_imovel({
            "id_unico": f"Carazza_{cod}",
            "imobiliaria": "Carazza Imóveis",
            "codigo_original": cod,
            "titulo": f"{tipo} em {bairro}",
            "modalidade": modalidade_padrao,
            "tipo": tipo,
            "preco": preco,
            "bairro": bairro,
            "cidade": cidade,
            "quartos": quartos,
            "banheiros": 0,
            "vagas": 0,
            "area_util": 0.0,
            "area_total": 0.0,
            "link": f"{self.site_url}/imovel/{cod}",
            "fotos": [foto] if foto else [],
            "extras": {}
        })

    def _processar_html(self, html: str, modalidade: str, vistos: set, destino: list):
        soup = BeautifulSoup(html, "html.parser")
        for prop in soup.select("div.property"):
            try:
                item = self._padronizar_card(prop, modalidade)
                if item and item["id_unico"] not in vistos:
                    vistos.add(item["id_unico"])
                    destino.append(item)
            except Exception:
                logging.exception("Erro ao padronizar card Carazza Imóveis")

    def buscar_imoveis(self):
        imoveis = []
        vistos = set()
        logging.info("--- Carazza Imóveis: Coletando imóveis ---")
        session = requests.Session()
        for dest_id in ("1", "2", "3"):
            try:
                resp = session.post(
                    self.destaques_url,
                    data={"FiltroBusca": dest_id},
                    headers=DEFAULT_HEADERS,
                    verify=False,
                    timeout=20,
                )
                if resp.status_code == 200:
                    self._processar_html(resp.text, "VENDA", vistos, imoveis)
            except Exception:
                logging.exception(f"Erro Carazza destaques {dest_id}")

        for id_mod, mod_nome in (("1", "VENDA"), ("2", "ALUGUEL")):
            try:
                resp = session.post(
                    self.busca_url,
                    data={"id_modalidade": id_mod, "codigo": ""},
                    headers=DEFAULT_HEADERS,
                    verify=False,
                    timeout=20,
                )
                if resp.status_code == 200:
                    self._processar_html(resp.text, mod_nome, vistos, imoveis)
            except Exception:
                logging.exception(f"Erro Carazza busca {mod_nome}")

        return imoveis


if __name__ == "__main__":
    c = CarazzaCrawler()
    res = c.buscar_imoveis()
    print(f"Total Carazza Imóveis: {len(res)}")

