import logging
import threading
import time
import requests
from backend.normalizer import normalizar_imovel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BaseHomeclixCrawler:
    """
    Crawler base para imobiliárias hospedadas na plataforma Homeclix.
    Consome a API centralizada /website/imovel/filtrar utilizando o cabeçalho x-tenant-id.
    """
    # Limita requisições concorrentes ao domínio central api.homeclix.com.br
    _api_semaphore = threading.Semaphore(2)

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
        self.session = requests.Session()
        self.session.headers.update(self.headers)

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

    def _padronizar_item(self, item, modalidade_nome):
        cod = str(item.get('idInterno', '')).strip()
        return normalizar_imovel({
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

    def _processar_lote(self, lista_imoveis, modalidade_nome, destino):
        for item in lista_imoveis:
            try:
                destino.append(self._padronizar_item(item, modalidade_nome))
            except Exception:
                logging.exception("[%s] Erro ao padronizar item", self.imobiliaria_nome)

    def _requisicao_com_retry(self, url: str, payload: dict, max_tentativas: int = 3, timeout: int = 45):
        """
        Executa requisição POST com controle de concorrência e tentativas automáticas em caso de timeout.
        """
        for tentativa in range(1, max_tentativas + 1):
            try:
                with self._api_semaphore:
                    time.sleep(0.3)
                    response = self.session.post(
                        url,
                        json=payload,
                        timeout=timeout
                    )

                if response.status_code in (200, 201):
                    return response.json()

                if response.status_code == 429 or response.status_code >= 500:
                    logging.warning(
                        "[%s] HTTP %s na tentativa %d/%d. Aguardando retentativa...",
                        self.imobiliaria_nome,
                        response.status_code,
                        tentativa,
                        max_tentativas
                    )
                else:
                    logging.error(
                        "[%s] Falha na requisição HTTP %s: %s",
                        self.imobiliaria_nome,
                        response.status_code,
                        response.text[:200]
                    )
                    return None
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                logging.warning(
                    "[%s] Conexão/Timeout (%s) na tentativa %d/%d para %s",
                    self.imobiliaria_nome,
                    type(exc).__name__,
                    tentativa,
                    max_tentativas,
                    url
                )
            except Exception as exc:
                logging.warning(
                    "[%s] Erro inesperado na requisição (tentativa %d/%d): %s",
                    self.imobiliaria_nome,
                    tentativa,
                    max_tentativas,
                    exc
                )

            if tentativa < max_tentativas:
                time.sleep(tentativa * 2)

        logging.error("[%s] Esgotadas todas as %d tentativas para %s", self.imobiliaria_nome, max_tentativas, url)
        return None

    def _coletar_modalidade(self, modalidade_nome):
        imoveis_padronizados = []
        skip = 0
        take = 50

        logging.info("--- %s: %s ---", self.imobiliaria_nome, modalidade_nome)

        while True:
            url_atual = self.base_url.format(skip, take)
            dados = self._requisicao_com_retry(
                url_atual,
                payload={"modalidade": [modalidade_nome]}
            )

            if not dados or not isinstance(dados, dict):
                break

            total_disponivel = dados.get('total', 0)
            lista_imoveis = dados.get('imoveis', [])
            qtd_encontrada = len(lista_imoveis)

            logging.info(
                "[%s] Retornados %d imóveis de %s (skip=%d, total na base=%d)",
                self.imobiliaria_nome,
                qtd_encontrada,
                modalidade_nome,
                skip,
                total_disponivel
            )

            if qtd_encontrada == 0:
                break

            self._processar_lote(lista_imoveis, modalidade_nome, imoveis_padronizados)
            skip += take
            if skip >= total_disponivel:
                break

        return imoveis_padronizados

    def buscar_imoveis(self):
        todos = []
        try:
            todos.extend(self._coletar_modalidade("VENDA"))
            todos.extend(self._coletar_modalidade("ALUGUEL"))
        finally:
            self.session.close()
        return todos
