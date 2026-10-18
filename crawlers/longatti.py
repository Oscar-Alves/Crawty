import requests
import logging
from backend.normalizer import normalizar_imovel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# OBSERVAÇÃO: A Longatti encerrou as atividades. Mantido apenas para referência histórica.
class LongattiCrawler:
    def __init__(self):
        self.base_url = "https://homeclixlongatti.dataclix.com.br:3331/website/imovel/filtrar/skip/{}/take/{}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json'
        }

    def _converter_para_float(self, valor):
        if valor is None:
            return 0.0
        try:
            return float(valor)
        except (ValueError, TypeError):
            return 0.0

    def _padronizar_item(self, item, modalidade_nome):
        cod = item.get('idInterno')
        return normalizar_imovel({
            "id_unico": f"Longatti_{cod}",
            "imobiliaria": "Longatti",
            "codigo_original": str(cod),
            "titulo": item.get('titulo'),
            "modalidade": modalidade_nome,
            "tipo": item.get('tipo'),
            "preco": self._converter_para_float(item.get('valor')),
            "bairro": item.get('bairro'),
            "cidade": item.get('cidade'),
            "quartos": int(item.get('quartos') or 0),
            "banheiros": int(item.get('banheiros') or 0),
            "vagas": int(item.get('garagens') or 0),
            "area_util": self._converter_para_float(item.get('areaConstruida')),
            "area_total": self._converter_para_float(item.get('areaTerreno')),
            "link": f"https://www.longattiimoveis.com.br/{cod}",
            "fotos": item.get('fotos', []),
            "extras": {
                "subtipo": item.get('subtipo'),
                "logradouro": item.get('logradouro'),
                "numero": item.get('numero')
            }
        })

    def _processar_lote(self, lista_imoveis, modalidade_nome, destino):
        for item in lista_imoveis:
            try:
                destino.append(self._padronizar_item(item, modalidade_nome))
            except Exception:
                logging.exception("Erro ao padronizar item Longatti")

    def _coletar_modalidade(self, modalidade_nome):
        imoveis_padronizados = []
        skip = 0
        take = 20

        logging.info(f"--- Longatti: {modalidade_nome} ---")

        while True:
            url_atual = self.base_url.format(skip, take)
            try:
                response = requests.post(
                    url_atual,
                    json={"modalidade": [modalidade_nome]},
                    headers=self.headers,
                    timeout=15,
                )
                dados = response.json()
                total_disponivel = dados.get('total', 0)
                lista_imoveis = dados.get('imoveis', [])
                qtd_encontrada = len(lista_imoveis)
                logging.info(f"Retornados {qtd_encontrada} imóveis de {modalidade_nome}. (Total na base: {total_disponivel})")

                if not lista_imoveis:
                    break

                self._processar_lote(lista_imoveis, modalidade_nome, imoveis_padronizados)
                skip += take

            except Exception:
                logging.exception("Erro Longatti")
                break

        return imoveis_padronizados

    def buscar_imoveis(self):
        todos = []
        todos.extend(self._coletar_modalidade("VENDA"))
        todos.extend(self._coletar_modalidade("ALUGUEL"))
        return todos


if __name__ == "__main__":
    crawler = LongattiCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(res[0])