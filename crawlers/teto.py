import logging
import requests
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_float, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TetoCrawler:
    """
    Crawler para Teto Imóveis (https://www.teto-imoveis.com/).
    """

    def __init__(self):
        self.site_url = "https://www.teto-imoveis.com"

    def _extrair_features(self, card):
        specs = {"quartos": 0, "banheiros": 0, "vagas": 0, "area": 0.0, "suites": 0}
        for feat in card.select(".imovelcard__info__feature"):
            txt = feat.get_text(" ", strip=True).lower()
            if "área" in txt or "area" in txt or "m²" in txt:
                specs["area"] = specs["area"] or extrair_float(txt)
            elif "suíte" in txt or "suite" in txt:
                specs["suites"] = specs["suites"] or extrair_int(txt)
            elif "quarto" in txt or "dorm" in txt:
                specs["quartos"] = specs["quartos"] or extrair_int(txt)
            elif "banh" in txt:
                specs["banheiros"] = specs["banheiros"] or extrair_int(txt)
            elif "garag" in txt or "vaga" in txt:
                specs["vagas"] = specs["vagas"] or extrair_int(txt)
        return specs

    def _extrair_ref_e_tipo(self, card, href: str):
        ref_el = card.select_one(".imovelcard__info__ref")
        ref_txt = ref_el.get_text(" ", strip=True) if ref_el else ""
        if "-" in ref_txt:
            parte_ref, parte_tipo = ref_txt.split("-", 1)
            cod = str(extrair_int(parte_ref) or extrair_int(href))
            tipo = parte_tipo.strip() or "Imóvel"
        else:
            cod = str(extrair_int(ref_txt) or extrair_int(href))
            tipo = "Imóvel"
        return cod, tipo

    def _padronizar_card(self, card, modalidade: str):
        href = card.get("data-link") or ""
        a_img = card.select_one("a.imovelcard__img")
        if not href and a_img:
            href = a_img.get("href", "")

        cod, tipo = self._extrair_ref_e_tipo(card, href)
        if not cod or cod == "0":
            return None

        img_el = card.select_one("a.imovelcard__img img")
        foto = img_el.get("src", "") if img_el else ""
        titulo = (a_img.get("title") if a_img else None) or f"{tipo} {cod}"

        loc_el = card.select_one(".imovelcard__info__local")
        loc_txt = loc_el.get_text(" ", strip=True) if loc_el else ""
        if "," in loc_txt:
            bairro, cidade_uf = [p.strip() for p in loc_txt.split(",", 1)]
            cidade = cidade_uf.split("/")[0].strip()
        else:
            bairro, cidade = "Não Informado", loc_txt.split("/")[0].strip() or "São João del Rei"

        val_el = card.select_one(".imovelcard__valor__valor")
        preco = extrair_preco(val_el.get_text(" ", strip=True) if val_el else "")
        specs = self._extrair_features(card)
        link = f"{self.site_url}{href}" if href.startswith("/") else href

        return normalizar_imovel({
            "id_unico": f"Teto_{cod}",
            "imobiliaria": "Teto Imóveis",
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
                logging.exception("Erro ao padronizar card Teto Imóveis")
        return novos

    def _coletar_modalidade(self, fin_slug: str, modalidade: str, vistos: set):
        coletados = []
        logging.info(f"--- Teto Imóveis: {modalidade} ---")
        for page in range(1, 25):
            url = f"{self.site_url}/imovel/?finalidade={fin_slug}&pag={page}"
            try:
                resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.imovelcard")
                if not cards:
                    break
                if self._processar_cards(cards, modalidade, vistos, coletados) == 0:
                    break
            except Exception:
                logging.exception(f"Erro Teto Imóveis {modalidade} página {page}")
                break
        return coletados

    def buscar_imoveis(self):
        todos = []
        vistos = set()
        todos.extend(self._coletar_modalidade("venda", "VENDA", vistos))
        todos.extend(self._coletar_modalidade("locacao", "ALUGUEL", vistos))
        return todos


if __name__ == "__main__":
    c = TetoCrawler()
    res = c.buscar_imoveis()
    print(f"Total Teto Imóveis: {len(res)}")

