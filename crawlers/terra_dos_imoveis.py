import logging
import requests
from backend.normalizer import normalizar_imovel
from crawlers.html_utils import extrair_float, extrair_int

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TERRA_TOKEN = (
    "AKGYqUJzBDIXWXFZtxVBprRofZsRZHxlcamUMdEVKdczvQHseTupRmPjgXyApcRHEeet"
    "FVMroPpjxjcNTydMkSgTbdazGXJTVdoEqQDODYYNFNkwMPDgWRUFwApnxAJx"
)


class TerraDosImoveisCrawler:
    """
    Crawler para Terra dos Imóveis (https://www.terradosimoveis.com.br/).
    Consome a API dedicada Homeclix/DataClix na porta 3332 filtrando pelas cidades da região.
    """

    def __init__(self):
        self.site_url = "https://www.terradosimoveis.com.br"
        self.api_base = "https://homeclix.dataclix.com.br:3332/terra-dos-imoveis"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TERRA_TOKEN}",
        }

    def _extrair_nome_campo(self, val, padrao=""):
        if isinstance(val, dict):
            return val.get("nome") or padrao
        return str(val).strip() if val else padrao

    def _padronizar_item(self, item: dict, modalidade_nome: str):
        cod = str(item.get("idInterno") or item.get("id") or "").strip()
        if not cod:
            return None

        tipo = self._extrair_nome_campo(item.get("tipo"), "Imóvel")
        subtipo = self._extrair_nome_campo(item.get("subtipo"), "")
        bairro = item.get("bairro") or "Não Informado"
        cidade = item.get("cidade") or "São João del Rei"
        titulo = item.get("titulo") or f"{tipo} em {bairro}"

        return normalizar_imovel({
            "id_unico": f"Terra_{cod}",
            "imobiliaria": "Terra dos Imóveis",
            "codigo_original": cod,
            "titulo": titulo,
            "modalidade": modalidade_nome,
            "tipo": tipo,
            "preco": extrair_float(item.get("valor")),
            "bairro": bairro,
            "cidade": cidade,
            "quartos": extrair_int(item.get("quartos")),
            "banheiros": extrair_int(item.get("banheiros")),
            "vagas": extrair_int(item.get("garagens")),
            "area_util": extrair_float(item.get("areaConstruida")),
            "area_total": extrair_float(item.get("areaTerreno")),
            "link": f"{self.site_url}/imovel/{cod}",
            "fotos": item.get("fotos") or [],
            "extras": {
                "subtipo": subtipo or None,
                "logradouro": item.get("logradouro"),
                "numero": item.get("numero"),
                "suites": extrair_int(item.get("suites")),
            }
        })

    def _obter_total_modalidade(self, modalidade_nome: str) -> int:
        try:
            r = requests.post(
                f"{self.api_base}/cidades/filtrar/tem-imovel",
                json={"modalidade": modalidade_nome},
                headers=self.headers,
                timeout=15,
            )
            if r.status_code in (200, 201) and isinstance(r.json(), list):
                return sum(int(c.get("imoveis") or 0) for c in r.json())
        except Exception:
            logging.exception(f"Erro ao obter total de cidades Terra dos Imóveis ({modalidade_nome})")
        return 1500

    def _processar_lote(self, lista: list, modalidade_nome: str, vistos: set, destino: list) -> int:
        novos = 0
        for raw in lista:
            try:
                item = self._padronizar_item(raw, modalidade_nome)
                if item and item["id_unico"] not in vistos:
                    vistos.add(item["id_unico"])
                    destino.append(item)
                    novos += 1
            except Exception:
                logging.exception("Erro ao padronizar item Terra dos Imóveis")
        return novos

    def _coletar_modalidade(self, modalidade_nome: str, vistos: set):
        coletados = []
        limite = max(200, self._obter_total_modalidade(modalidade_nome) + 100)
        skip = 0
        take = 100
        logging.info(f"--- Terra dos Imóveis: {modalidade_nome} (limite estimado={limite}) ---")

        while skip < limite:
            url = f"{self.api_base}/imovel/filtrar/skip/{skip}/take/{take}"
            try:
                resp = requests.post(
                    url,
                    json={"modalidade": [modalidade_nome]},
                    headers=self.headers,
                    timeout=20,
                )
                if resp.status_code not in (200, 201):
                    break
                dados = resp.json()
                lista = dados.get("imoveis") or []
                if not lista:
                    break
                if self._processar_lote(lista, modalidade_nome, vistos, coletados) == 0:
                    break
                skip += take
            except Exception:
                logging.exception(f"Erro Terra dos Imóveis {modalidade_nome} skip={skip}")
                break

        return coletados

    def buscar_imoveis(self):
        todos = []
        vistos = set()
        todos.extend(self._coletar_modalidade("VENDA", vistos))
        todos.extend(self._coletar_modalidade("ALUGUEL", vistos))
        return todos


if __name__ == "__main__":
    c = TerraDosImoveisCrawler()
    res = c.buscar_imoveis()
    print(f"Total Terra dos Imóveis: {len(res)}")

