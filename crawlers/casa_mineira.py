import json
import logging
import re
import requests
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_float, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class CasaMineiraCrawler:
    """
    Crawler para Casa Mineira em São João del Rei (https://www.casamineira.com.br/imoveis/sao-joao-del-rei_mg).
    """

    def __init__(self):
        self.site_url = "https://www.casamineira.com.br"
        self.list_url = f"{self.site_url}/imoveis/sao-joao-del-rei_mg"

    def _extrair_preco_e_modalidade(self, post: dict):
        ops = post.get("priceOperationTypes") or []
        if not ops:
            return 0.0, "VENDA"
        op = ops[0]
        op_name = ((op.get("operationType") or {}).get("name") or "Venda").upper()
        modalidade = "ALUGUEL" if "ALUG" in op_name or "LOCA" in op_name else "VENDA"
        prices = op.get("prices") or []
        preco = float(prices[0].get("amount") or 0.0) if prices else 0.0
        return preco, modalidade

    def _extrair_features(self, post: dict):
        feats = post.get("mainFeatures") or {}
        specs = {"area_total": 0.0, "area_util": 0.0, "quartos": 0, "banheiros": 0, "vagas": 0, "suites": 0}
        for f in feats.values():
            label = (f.get("label") or "").lower()
            val = f.get("value")
            if "total" in label:
                specs["area_total"] = extrair_float(val)
            elif "útil" in label or "util" in label:
                specs["area_util"] = extrair_float(val)
            elif "quarto" in label or "dorm" in label:
                specs["quartos"] = extrair_int(val)
            elif "banheiro" in label:
                specs["banheiros"] = extrair_int(val)
            elif "vaga" in label or "garag" in label:
                specs["vagas"] = extrair_int(val)
            elif "suíte" in label or "suite" in label:
                specs["suites"] = extrair_int(val)
        if not specs["area_util"]:
            specs["area_util"] = specs["area_total"]
        if not specs["area_total"]:
            specs["area_total"] = specs["area_util"]
        return specs

    def _extrair_fotos(self, post: dict):
        pics = (post.get("visiblePictures") or {}).get("pictures") or []
        fotos = []
        for p in pics:
            url = p.get("url730x532") or p.get("url360x266") or p.get("url")
            if url:
                fotos.append(url)
        return fotos

    def _padronizar_post(self, post: dict):
        cod = str(post.get("postingId") or post.get("postingCode") or "").strip()
        if not cod:
            return None

        preco, modalidade = self._extrair_preco_e_modalidade(post)
        specs = self._extrair_features(post)

        gen_title = post.get("generatedTitle") or ""
        tipo = gen_title.split("·")[0].strip() if "·" in gen_title else "Imóvel"
        titulo = post.get("title") or gen_title or f"{tipo} {cod}"

        loc = post.get("postingLocation") or {}
        zone = (loc.get("location") or {}).get("name") or "Não Informado"
        parent_loc = ((loc.get("location") or {}).get("parent") or {}).get("name") or "São João del Rei"
        url_rel = post.get("url") or ""
        link = f"{self.site_url}{url_rel}" if url_rel.startswith("/") else url_rel

        return normalizar_imovel({
            "id_unico": f"CasaMineira_{cod}",
            "imobiliaria": "Casa Mineira",
            "codigo_original": cod,
            "titulo": titulo,
            "modalidade": modalidade,
            "tipo": tipo,
            "preco": preco,
            "bairro": zone,
            "cidade": parent_loc,
            "quartos": specs["quartos"],
            "banheiros": specs["banheiros"],
            "vagas": specs["vagas"],
            "area_util": specs["area_util"],
            "area_total": specs["area_total"],
            "link": link,
            "fotos": self._extrair_fotos(post),
            "extras": {"suites": specs["suites"]}
        })

    def buscar_imoveis(self):
        imoveis = []
        vistos = set()
        logging.info("--- Casa Mineira: Coletando imóveis ---")
        try:
            resp = requests.get(self.list_url, headers=DEFAULT_HEADERS, timeout=25)
            if resp.status_code != 200:
                return imoveis
            match = re.search(
                r"window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});\s*(?:window\.|</script>)",
                resp.text,
                re.DOTALL,
            )
            if not match:
                return imoveis
            state = json.loads(match.group(1))
            postings = (state.get("listStore") or {}).get("listPostings") or []
            for post in postings:
                try:
                    item = self._padronizar_post(post)
                    if item and item["id_unico"] not in vistos:
                        vistos.add(item["id_unico"])
                        imoveis.append(item)
                except Exception:
                    logging.exception("Erro ao padronizar item Casa Mineira")
        except Exception:
            logging.exception("Erro ao buscar Casa Mineira")
        return imoveis


if __name__ == "__main__":
    c = CasaMineiraCrawler()
    res = c.buscar_imoveis()
    print(f"Total Casa Mineira: {len(res)}")

