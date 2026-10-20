import base64
import json
import logging
import requests
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_float, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class GuilhermeAugustoCrawler:
    """
    Crawler para Guilherme Augusto Imóveis (https://www.guilhermeaugustoimoveis.com.br/).
    """

    def __init__(self):
        self.site_url = "https://www.guilhermeaugustoimoveis.com.br"
        self.search_url = f"{self.site_url}/php/search-base64.php"

    def _extrair_features(self, card):
        specs = {"quartos": 0, "banheiros": 0, "vagas": 0, "area_total": 0.0, "area_util": 0.0, "suites": 0}
        for wrap in card.select(".c49-property-number-wrap"):
            title = (wrap.get("title") or wrap.get("data-original-title") or "").lower()
            num_el = wrap.select_one(".c49-property-number")
            txt = num_el.get_text(" ", strip=True) if num_el else ""
            if "total" in title:
                specs["area_total"] = extrair_float(txt)
            elif "útil" in title or "util" in title or "constru" in title or "área" in title or "area" in title:
                specs["area_util"] = extrair_float(txt)
            elif "suíte" in title or "suite" in title:
                specs["suites"] = extrair_int(txt)
            elif "quarto" in title or "dorm" in title:
                specs["quartos"] = extrair_int(txt)
            elif "banh" in title:
                specs["banheiros"] = extrair_int(txt)
            elif "vaga" in title or "garag" in title:
                specs["vagas"] = extrair_int(txt)
        if not specs["area_util"]:
            specs["area_util"] = specs["area_total"]
        if not specs["area_total"]:
            specs["area_total"] = specs["area_util"]
        return specs

    def _extrair_local(self, card):
        addr_el = card.select_one(".c49-property-card_address")
        txt = addr_el.get_text(" ", strip=True) if addr_el else ""
        if "," in txt:
            bairro, cid_uf = [p.strip() for p in txt.split(",", 1)]
            cidade = cid_uf.split("-")[0].strip()
        else:
            bairro, cidade = "Não Informado", txt.split("-")[0].strip() or "São João del Rei"
        return bairro, cidade

    def _padronizar_card(self, card, modalidade: str):
        code_el = card.select_one(".c49-property-card_code")
        cod = str(extrair_int(code_el.get_text(strip=True) if code_el else "") or extrair_int(card.get("id", "")))
        if not cod or cod == "0":
            return None

        title_el = card.select_one(".c49-property-card_title")
        titulo = title_el.get_text(" ", strip=True) if title_el else f"Imóvel {cod}"

        type_el = card.select_one(".c49-property-card_type")
        tipo = type_el.get_text(" ", strip=True) if type_el else "Imóvel"

        bairro, cidade = self._extrair_local(card)

        price_el = card.select_one(".c49-property-card_price")
        preco = extrair_preco(price_el.get_text(" ", strip=True) if price_el else "")

        fotos = []
        for img in card.select(".c49-carousel-photo-wrap img"):
            src = img.get("src", "")
            if src and src not in fotos:
                fotos.append(src)

        a_det = card.select_one("a.c49btn-details") or card.select_one(".c49-carousel-photo-wrap a")
        link = a_det.get("href", "") if a_det else f"{self.site_url}/imobiliaria/imoveis"
        specs = self._extrair_features(card)

        return normalizar_imovel({
            "id_unico": f"GuilhermeAugusto_{cod}",
            "imobiliaria": "Guilherme Augusto Imóveis",
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
            "area_util": specs["area_util"],
            "area_total": specs["area_total"],
            "link": link,
            "fotos": fotos,
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
                logging.exception("Erro ao padronizar card Guilherme Augusto")
        return novos

    def _coletar_modalidade(self, tipo_val: str, modalidade: str, vistos: set):
        coletados = []
        logging.info(f"--- Guilherme Augusto Imóveis: {modalidade} ---")
        try:
            filtro = [{"input": "tipo", "value": tipo_val, "table": "t_i"}]
            b64 = base64.b64encode(json.dumps(filtro).encode("utf-8")).decode("utf-8")
            r_sb = requests.post(self.search_url, data={"searches": b64}, headers=DEFAULT_HEADERS, timeout=20)
            dados_busca = r_sb.json()
            id_busca = dados_busca.get("id_busca")
            path = (dados_busca.get("path") or "imobiliaria/").strip("/")
            if not id_busca:
                return coletados

            for page in range(1, 25):
                url = f"{self.site_url}/{path}/imoveis/{id_busca}" if page == 1 else f"{self.site_url}/{path}/imoveis/{id_busca}/{page}"
                resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("article.c49-property-card")
                if not cards:
                    break
                if self._processar_cards(cards, modalidade, vistos, coletados) == 0:
                    break
        except Exception:
            logging.exception(f"Erro Guilherme Augusto {modalidade}")
        return coletados

    def buscar_imoveis(self):
        todos = []
        vistos = set()
        todos.extend(self._coletar_modalidade("1", "VENDA", vistos))
        todos.extend(self._coletar_modalidade("2", "ALUGUEL", vistos))
        return todos


if __name__ == "__main__":
    c = GuilhermeAugustoCrawler()
    res = c.buscar_imoveis()
    print(f"Total Guilherme Augusto: {len(res)}")

