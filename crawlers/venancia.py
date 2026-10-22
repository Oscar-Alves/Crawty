import logging
import requests
from bs4 import BeautifulSoup
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import DEFAULT_HEADERS, extrair_preco, extrair_float, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class VenanciaCrawler:
    """
    Crawler para Venância Imóveis (https://www.venanciaimoveis.com.br/).
    """

    def __init__(self):
        self.site_url = "https://www.venanciaimoveis.com.br"
        self.ajax_url = f"{self.site_url}/acoes.php?acao=busca_imoveis"

    def _extrair_icones(self, card):
        specs = {"quartos": 0, "banheiros": 0, "vagas": 0, "suites": 0, "cod": ""}
        icones = card.select_one(".icones")
        if not icones:
            return specs

        font_el = icones.find("font")
        if font_el:
            specs["cod"] = str(extrair_int(font_el.get_text(" ", strip=True)))

        for img in icones.find_all("img"):
            title = (img.get("title") or "").lower()
            nxt = img.next_sibling
            val = extrair_int(str(nxt) if nxt else "")
            if "quarto" in title or "dorm" in title:
                specs["quartos"] = val
            elif "banheiro" in title:
                specs["banheiros"] = val
            elif "vaga" in title or "garagem" in title:
                specs["vagas"] = val
            elif "suíte" in title or "suite" in title:
                specs["suites"] = val
        return specs

    def _extrair_area(self, span_txt: str) -> float:
        if not span_txt:
            return 0.0
        val = extrair_float(span_txt)
        if "ha" in span_txt.lower():
            return round(val * 10000.0, 2)
        return val

    @staticmethod
    def _obter_texto(el, seletor: str, padrao: str = "") -> str:
        if not el:
            return padrao
        target = el.select_one(seletor)
        return target.get_text(strip=True) if target else padrao

    def _extrair_foto_url(self, card) -> list:
        foto_el = card.select_one(".foto-imovel img")
        foto_src = foto_el.get("src", "") if foto_el else ""
        if not foto_src:
            return []
        if foto_src.startswith("http"):
            return [foto_src]
        return [f"{self.site_url}/{foto_src.lstrip('/')}"]

    def _padronizar_card(self, card, modalidade_padrao: str):
        a_el = card.find("a")
        id_attr = a_el.get("id", "") if a_el else ""
        specs = self._extrair_icones(card)
        cod = specs["cod"] or str(extrair_int(id_attr))
        if not cod or cod == "0":
            return None

        ico_img = card.select_one(".ico-tipo img")
        tipo_raw = (ico_img.get("title") if ico_img else None) or "Imóvel"
        tipo = tipo_raw.split("(")[0].strip()

        ico_span_txt = self._obter_texto(card, ".ico-tipo span")
        area = self._extrair_area(ico_span_txt)

        mod_txt = self._obter_texto(card, ".texto_imo1", modalidade_padrao).upper()
        modalidade = "ALUGUEL" if "ALUG" in mod_txt else "VENDA"

        textos2 = card.select(".texto_imo2")
        preco_txt = textos2[0].get_text(strip=True) if textos2 else ""
        preco = extrair_preco(preco_txt)

        bairro = self._obter_texto(card, ".nome-imovel", "Não Informado")
        cidade_raw = self._obter_texto(card, ".texto_imo3", "São João del Rei")
        cidade = cidade_raw.split("-")[0].strip()
        fotos = self._extrair_foto_url(card)

        return normalizar_imovel({
            "id_unico": f"Venancia_{cod}",
            "imobiliaria": "Venância Imóveis",
            "codigo_original": cod,
            "titulo": f"{tipo} em {bairro}",
            "modalidade": modalidade,
            "tipo": tipo,
            "preco": preco,
            "bairro": bairro,
            "cidade": cidade,
            "quartos": specs["quartos"],
            "banheiros": specs["banheiros"],
            "vagas": specs["vagas"],
            "area_util": area,
            "area_total": area,
            "link": f"{self.site_url}/?cod={cod}",
            "fotos": fotos,
            "extras": {"suites": specs["suites"]}
        })

    def _coletar_modalidade(self, id_mod: str, mod_nome: str, vistos: set):
        coletados = []
        logging.info(f"--- Venância Imóveis: {mod_nome} ---")
        try:
            resp = requests.post(
                self.ajax_url,
                data={"id_modalidade": id_mod, "palavra": "", "bairro": "", "cidade": "", "estado": "mg"},
                headers=DEFAULT_HEADERS,
                timeout=25,
            )
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            for card in soup.select("div.item-imovel"):
                try:
                    item = self._padronizar_card(card, mod_nome)
                    if item and item["id_unico"] not in vistos:
                        vistos.add(item["id_unico"])
                        coletados.append(item)
                except Exception:
                    logging.exception("Erro ao padronizar item Venância Imóveis")
        except Exception:
            logging.exception(f"Erro Venância Imóveis {mod_nome}")
        return coletados

    def buscar_imoveis(self):
        todos = []
        vistos = set()
        todos.extend(self._coletar_modalidade("1", "VENDA", vistos))
        todos.extend(self._coletar_modalidade("2", "ALUGUEL", vistos))
        return todos


if __name__ == "__main__":
    c = VenanciaCrawler()
    res = c.buscar_imoveis()
    print(f"Total Venância Imóveis: {len(res)}")

