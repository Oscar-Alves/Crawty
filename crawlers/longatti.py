import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LongattiCrawler:
    def __init__(self):
        self.base_url = "https://homeclixlongatti.dataclix.com.br:3331/website/imovel/filtrar/skip/{}/take/{}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json'
        }

    def _converter_para_float(self, valor):
        if valor is None: return 0.0
        try:
            return float(valor)
        except:
            return 0.0

    def _coletar_modalidade(self, modalidade_nome):
        imoveis_padronizados = []
        skip = 0
        take = 20
        continuar_buscando = True
        page_count = 1

        logging.info(f"--- Longatti: {modalidade_nome} ---")

        while continuar_buscando:

            # if page_count > 2:
            #     logging.info(f"Limite de teste atingido para {modalidade_nome} (2 páginas). Parando.")
            #     break

            url_atual = self.base_url.format(skip, take)
            try:
                response = requests.post(url_atual, json={"modalidade": [modalidade_nome]}, headers=self.headers, timeout=15)
                dados = response.json()
                total_disponivel = dados.get('total', 0)
                qtd_encontrada = len(dados.get('imoveis', []))
                logging.info(f"Retornados {qtd_encontrada} imóveis de {modalidade_nome}. (Total na base: {total_disponivel})")
                lista_imoveis = dados.get('imoveis', [])

                if len(lista_imoveis) > 0:
                    for item in lista_imoveis:
                        # --- PADRONIZAÇÃO AQUI ---
                        try:
                            imovel_unificado = {
                                "id_unico": f"Longatti_{item.get('idInterno')}",
                                "imobiliaria": "Longatti",
                                "codigo_original": str(item.get('idInterno')),
                                "titulo": item.get('titulo'),
                                "modalidade": modalidade_nome, # VENDA ou ALUGUEL
                                "tipo": item.get('tipo'),
                                "preco": self._converter_para_float(item.get('valor')),
                                "bairro": item.get('bairro'),
                                "cidade": item.get('cidade'),
                                "quartos": int(item.get('quartos') or 0),
                                "banheiros": int(item.get('banheiros') or 0),
                                "vagas": int(item.get('garagens') or 0),
                                "area_util": self._converter_para_float(item.get('areaConstruida')),
                                "area_total": self._converter_para_float(item.get('areaTerreno')),
                                # Link manual pois a API não retorna, baseado no padrão do site
                                "link": f"https://www.longattiimoveis.com.br/{item.get('idInterno')}",
                                "fotos": item.get('fotos', []),
                                "extras": {
                                    "subtipo": item.get('subtipo'),
                                    "logradouro": item.get('logradouro'),
                                    "numero": item.get('numero')
                                }
                            }
                            imoveis_padronizados.append(imovel_unificado)
                        except Exception as e:
                            logging.error(f"Erro ao padronizar item Longatti: {e}")

                    skip += take
                    page_count += 1
                    time.sleep(1)
                else:
                    continuar_buscando = False

            except Exception as e:
                logging.error(f"Erro Longatti: {e}")
                continuar_buscando = False
        
        return imoveis_padronizados

    def buscar_imoveis(self):
        todos = []
        todos.extend(self._coletar_modalidade("VENDA"))
        todos.extend(self._coletar_modalidade("ALUGUEL"))
        return todos

if __name__ == "__main__":
    crawler = LongattiCrawler()
    res = crawler.buscar_imoveis()
    if res: print(res[0])