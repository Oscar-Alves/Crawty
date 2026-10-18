import requests
import logging
from backend.normalizer import normalizar_imovel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BaseHomeclixCrawler:
    """
    Crawler base para imobiliárias hospedadas na plataforma Homeclix.
    Consome a API centralizada /website/imovel/filtrar utilizando o cabeçalho x-tenant-id.
    """
    def __init__(self, tenant_id: int, imobiliaria_nome: str, prefixo_id: str, site_url: str):
        self.tenant_id = str(tenant_id)
        self.imobiliaria_nome = imobiliaria_nome
        self.prefixo_id = prefixo_id
        self.site_url = site_url.rstrip('/') if site_url else ""
        self.base_url = "https://api.homeclix.com.br/website/imovel/filtrar/skip/{}/take/{}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'x-tenant-id': self.tenant_id
        }

    def _converter_para_float(self, valor):
        if valor is None:
            return 0.0
        try:
            return float(str(valor).replace(',', '.').strip())
        except (ValueError, TypeError):
            return 0.0

    def _converter_para_int(self, valor):
        if valor is None:
            return 0
        try:
            return int(valor)
        except (ValueError, TypeError):
            return 0

    def _coletar_modalidade(self, modalidade_nome):
        imoveis_padronizados = []
        skip = 0
        take = 50
        continuar_buscando = True

        logging.info(f"--- {self.imobiliaria_nome}: {modalidade_nome} ---")

        while continuar_buscando:
            url_atual = self.base_url.format(skip, take)
            try:
                response = requests.post(
                    url_atual,
                    json={"modalidade": [modalidade_nome]},
                    headers=self.headers,
                    timeout=20
                )

                if response.status_code not in [200, 201]:
                    logging.error(f"Erro request {self.imobiliaria_nome} {modalidade_nome}: HTTP {response.status_code}")
                    break

                dados = response.json()
                total_disponivel = dados.get('total', 0)
                lista_imoveis = dados.get('imoveis', [])
                qtd_encontrada = len(lista_imoveis)

                logging.info(f"Retornados {qtd_encontrada} imóveis de {modalidade_nome} (skip={skip}, total na base={total_disponivel})")

                if qtd_encontrada > 0:
                    for item in lista_imoveis:
                        try:
                            cod = str(item.get('idInterno', '')).strip()
                            imovel_unificado = normalizar_imovel({
                                "id_unico": f"{self.prefixo_id}_{cod}",
                                "imobiliaria": self.imobiliaria_nome,
                                "codigo_original": cod,
                                "titulo": item.get('titulo') or "Sem título",
                                "modalidade": modalidade_nome,
                                "tipo": item.get('tipo') or "Imóvel",
                                "preco": self._converter_para_float(item.get('valor')),
                                "bairro": item.get('bairro') or "Não Informado",
                                "cidade": item.get('cidade') or "São João del Rei",
                                "quartos": self._converter_para_int(item.get('quartos')),
                                "banheiros": self._converter_para_int(item.get('banheiros')),
                                "vagas": self._converter_para_int(item.get('garagens')),
                                "area_util": self._converter_para_float(item.get('areaConstruida')),
                                "area_total": self._converter_para_float(item.get('areaTerreno')),
                                "link": f"{self.site_url}/imovel/{cod}" if self.site_url else "",
                                "fotos": item.get('fotos', []) or [],
                                "extras": {
                                    "subtipo": item.get('subtipo'),
                                    "logradouro": item.get('logradouro'),
                                    "numero": item.get('numero'),
                                    "suites": self._converter_para_int(item.get('suites')),
                                    "salas": self._converter_para_int(item.get('salas'))
                                }
                            })
                            imoveis_padronizados.append(imovel_unificado)
                        except Exception as e:
                            logging.error(f"Erro ao padronizar item {self.imobiliaria_nome}: {e}")

                    skip += take
                    if skip >= total_disponivel:
                        continuar_buscando = False
                else:
                    continuar_buscando = False

            except Exception as e:
                logging.error(f"Erro {self.imobiliaria_nome}: {e}")
                continuar_buscando = False

        return imoveis_padronizados

    def buscar_imoveis(self):
        todos = []
        todos.extend(self._coletar_modalidade("VENDA"))
        todos.extend(self._coletar_modalidade("ALUGUEL"))
        return todos
