import logging
import re
import requests
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_float, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class SigmaCrawler:
    """
    Crawler para Sigma Corretora (https://sigmacorretora.com.br/).
    """

    def __init__(self):
        self.site_url = "https://sigmacorretora.com.br"

    def _extrair_local_titulo(self, titulo: str):
        partes = [p.strip() for p in titulo.split(",") if p.strip()]
        if len(partes) >= 3:
            return partes[-2], partes[-1]
        if len(partes) == 2:
            return partes[-1], "São João del Rei"
        return "Não Informado", "São João del Rei"

    def _extrair_features(self, card):
        specs = {"quartos": 0, "banheiros": 0, "vagas": 0, "area": 0.0}
        for feat in card.select(".property-features-grid .feature-item, .property-features-grid span, .property-features-grid div"):
            txt = feat.get_text(" ", strip=True).lower()
            html_f = str(feat).lower()
            if "m²" in txt or "area" in html_f or "ruler" in html_f or "expand" in html_f:
                specs["area"] = specs["area"] or extrair_float(txt)
            elif "bed" in html_f or "quarto" in txt or "dorm" in txt:
                specs["quartos"] = specs["quartos"] or extrair_int(txt)
            elif "bath" in html_f or "banh" in txt:
                specs["banheiros"] = specs["banheiros"] or extrair_int(txt)
            elif "car" in html_f or "vaga" in txt or "garag" in txt:
                specs["vagas"] = specs["vagas"] or extrair_int(txt)
        return specs

    def _padronizar_card(self, card, modalidade_padrao: str):
        ref_el = card.select_one(".ref-modern")
        ref_txt = ref_el.get_text(" ", strip=True) if ref_el else ""
        cod = re.sub(r"(?i)^ref[:\s]*", "", ref_txt).strip()

        a_el = card.select_one(".property-content a")
        href = a_el.get("href", "") if a_el else ""
        if not cod:
            cod = str(extrair_int(href))
        if not cod or cod == "0":
            return None

        tipo_el = card.select_one(".property-type")
        tipo = tipo_el.get_text(" ", strip=True) if tipo_el else "Imóvel"

        titulo_el = card.select_one(".property-title-modern")
        titulo = titulo_el.get_text(" ", strip=True) if titulo_el else f"{tipo} {cod}"
        bairro, cidade = self._extrair_local_titulo(titulo)

        preco_el = card.select_one(".price-value")
        preco = extrair_preco(preco_el.get_text(" ", strip=True) if preco_el else "")

        fotos = []
        for img in card.select(".property-image-wrapper img"):
            src = img.get("src", "")
            if src:
                full_src = f"{self.site_url}{src}" if src.startswith("/") else src
                if full_src not in fotos:
                    fotos.append(full_src)

        specs = self._extrair_features(card)
        link = f"{self.site_url}{href}" if href.startswith("/") else href

        return normalizar_imovel({
            "id_unico": f"Sigma_{cod}",
            "imobiliaria": "Sigma Corretora",
            "codigo_original": cod,
            "titulo": titulo,
            "modalidade": modalidade_padrao,
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
            "fotos": fotos,
            "extras": {}
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
                logging.exception("Erro ao padronizar card Sigma Corretora")
        return novos

    def _coletar_modalidade(self, path: str, modalidade: str, vistos: set):
        coletados = []
        logging.info(f"--- Sigma Corretora: {modalidade} ---")
        offset = 0
        while offset < 500:
            url = f"{self.site_url}/{path}" if offset == 0 else f"{self.site_url}/{path}?start={offset}"
            try:
                resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.property-card-modern")
                if not cards:
                    break
                novos = self._processar_cards(cards, modalidade, vistos, coletados)
                if novos == 0:
                    break
                offset += len(cards)
            except Exception:
                logging.exception(f"Erro Sigma Corretora {modalidade} offset={offset}")
                break
        return coletados

    def buscar_imoveis(self):
        todos = []
        vistos = set()
        todos.extend(self._coletar_modalidade("imoveis-venda", "VENDA", vistos))
        todos.extend(self._coletar_modalidade("imoveis-locacao", "ALUGUEL", vistos))
        return todos


if __name__ == "__main__":
    c = SigmaCrawler()
    res = c.buscar_imoveis()
    print(f"Total Sigma Corretora: {len(res)}")

