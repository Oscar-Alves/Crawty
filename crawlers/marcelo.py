import json
import logging
import re
import requests
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_float, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MarceloCrawler:
    """
    Crawler para Marcelo Corretor de Imóveis (https://marcelocorretordeimoveis.com/).
    """

    def __init__(self):
        self.site_url = "https://marcelocorretordeimoveis.com"
        self.ajax_url = f"{self.site_url}/wp-admin/admin-ajax.php"

    def _flatten_dict(self, d, parent_key=""):
        items = []
        if isinstance(d, dict):
            for k, v in d.items():
                new_key = f"{parent_key}[{k}]" if parent_key else k
                items.extend(self._flatten_dict(v, new_key))
        elif isinstance(d, list):
            for i, v in enumerate(d):
                items.extend(self._flatten_dict(v, f"{parent_key}[{i}]"))
        else:
            items.append((parent_key, "" if d is None else str(d)))
        return items

    def _extrair_campos_texto(self, tokens: list):
        dados = {"cod": "", "titulo": "", "bairro": "Não Informado", "cidade": "São João del Rei", "preco": 0.0, "nums": []}
        for idx, tok in enumerate(tokens):
            if tok.lower().startswith("ref") and idx + 1 < len(tokens):
                dados["cod"] = str(extrair_int(tokens[idx + 1]))
                if idx + 2 < len(tokens):
                    dados["titulo"] = tokens[idx + 2]
            elif tok == "-" and idx >= 2 and len(tokens[idx + 1] if idx + 1 < len(tokens) else "") == 2:
                dados["cidade"] = tokens[idx - 1]
                dados["bairro"] = tokens[idx - 2].lstrip(",").strip()
            elif "R$" in tok:
                dados["preco"] = extrair_preco(tok)
            elif re.fullmatch(r"\d+(?:[.,]\d+)?", tok) and tok != dados["cod"]:
                dados["nums"].append(tok)
        return dados

    @staticmethod
    def _determinar_tipo(terms: list) -> str:
        if len(terms) > 1:
            return terms[1]
        if terms:
            return terms[0]
        return "Imóvel"

    @staticmethod
    def _determinar_area(nums: list) -> float:
        if len(nums) == 1:
            return extrair_float(nums[0])
        if len(nums) >= 4:
            return extrair_float(nums[-1])
        return 0.0

    def _padronizar_card(self, card, modalidade: str):
        for s in card.find_all("style"):
            s.decompose()

        post_id = str(card.get("data-post-id") or "").strip()
        a_el = card.find("a", href=True)
        link = a_el.get("href", "") if a_el else ""
        img_el = card.find("img")
        foto = img_el.get("src", "") if img_el else ""

        terms = [t.get_text(strip=True) for t in card.select(".jet-listing-dynamic-terms__link")]
        tipo = self._determinar_tipo(terms)

        tokens = [t.strip() for t in card.get_text("|", strip=True).split("|") if t.strip()]
        dados = self._extrair_campos_texto(tokens)
        cod = dados["cod"] or post_id
        if not cod:
            return None

        nums = dados["nums"]
        area = self._determinar_area(nums)
        quartos = extrair_int(nums[0]) if len(nums) >= 2 else 0
        banheiros = extrair_int(nums[1]) if len(nums) >= 2 else 0
        vagas = extrair_int(nums[2]) if len(nums) >= 3 else 0

        return normalizar_imovel({
            "id_unico": f"Marcelo_{cod}",
            "imobiliaria": "Marcelo Corretor",
            "codigo_original": cod,
            "titulo": dados["titulo"] or f"{tipo} em {dados['bairro']}",
            "modalidade": modalidade,
            "tipo": tipo,
            "preco": dados["preco"],
            "bairro": dados["bairro"],
            "cidade": dados["cidade"],
            "quartos": quartos,
            "banheiros": banheiros,
            "vagas": vagas,
            "area_util": area,
            "area_total": area,
            "link": link,
            "fotos": [foto] if foto else [],
            "extras": {}
        })

    def _processar_soup(self, soup, modalidade: str, vistos: set, destino: list) -> int:
        novos = 0
        for card in soup.select(".jet-listing-grid__item"):
            try:
                item = self._padronizar_card(card, modalidade)
                if item and item["id_unico"] not in vistos:
                    vistos.add(item["id_unico"])
                    destino.append(item)
                    novos += 1
            except Exception:
                logging.exception("Erro ao padronizar card Marcelo Corretor")
        return novos

    def _coletar_modalidade(self, slug_path: str, modalidade: str, vistos: set):
        coletados = []
        logging.info(f"--- Marcelo Corretor: {modalidade} ---")
        try:
            resp = requests.get(f"{self.site_url}/{slug_path}/", headers=DEFAULT_HEADERS, timeout=20)
            if resp.status_code != 200:
                return coletados
            soup = BeautifulSoup(resp.text, "html.parser")
            self._processar_soup(soup, modalidade, vistos, coletados)

            script = soup.find("script", id="jet-smart-filters-js-extra")
            if not script or not script.string:
                return coletados
            match = re.search(r"\{.*\}", script.string, re.DOTALL)
            if not match:
                return coletados
            jsf = json.loads(match.group(0))
            query = jsf["queries"]["jet-engine"]["result"]
            settings = jsf["settings"]["jet-engine"]["result"]
            max_pages = int((jsf.get("props", {}).get("jet-engine", {}).get("result", {}).get("max_num_pages")) or 1)

            for page in range(2, max_pages + 1):
                payload = {
                    "action": "jet_smart_filters",
                    "provider": "jet-engine/result",
                    "paged": page,
                    "query": query,
                    "settings": settings,
                }
                r_ajax = requests.post(self.ajax_url, data=self._flatten_dict(payload), headers=DEFAULT_HEADERS, timeout=20)
                if r_ajax.status_code != 200:
                    break
                content_html = r_ajax.json().get("content") or ""
                if self._processar_soup(BeautifulSoup(content_html, "html.parser"), modalidade, vistos, coletados) == 0:
                    break
        except Exception:
            logging.exception(f"Erro Marcelo Corretor {modalidade}")
        return coletados

    def buscar_imoveis(self):
        todos = []
        vistos = set()
        todos.extend(self._coletar_modalidade("comprar", "VENDA", vistos))
        todos.extend(self._coletar_modalidade("alugar", "ALUGUEL", vistos))
        return todos


if __name__ == "__main__":
    c = MarceloCrawler()
    res = c.buscar_imoveis()
    print(f"Total Marcelo Corretor: {len(res)}")

