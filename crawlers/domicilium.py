import requests
import time
import logging
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.normalizer import normalizar_imovel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BAIRRO_NAO_INFORMADO = "Não Informado"
CIDADE_PADRAO = "São João del Rei"
CIDADE_SANTA_CRUZ = "Santa Cruz de Minas"
CIDADE_TIRADENTES = "Tiradentes"
DOMICILIUM_BASE_URL = "https://www.domiciliumimoveis.com.br"


class DomiciliumCrawler:
    def __init__(self):
        self.endpoint = f"{DOMICILIUM_BASE_URL}/fetch_pages.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        self.filtro_aluguel = "codigo=&id_modalidade%5B%5D=2&de_valor=10000&ate_valor=2000000&valor_de=100&valor_ate=100000&ordenacao=3"
        self.filtro_venda = "codigo=&id_modalidade%5B%5D=1&de_valor=10000&ate_valor=2000000&valor_de=10000&valor_ate=10000000&ordenacao=3"

    def _limpar_valor(self, valor_str):
        """Converte 'R$ 1.200,00' para 1200.00"""
        if not valor_str:
            return 0.0
        try:
            limpo = valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(limpo)
        except (ValueError, TypeError):
            return 0.0

    def _limpar_area(self, area_str):
        """Converte '135,92 m²' para 135.92"""
        if not area_str:
            return 0.0
        try:
            limpo = re.sub(r'[^\d,.]', '', str(area_str)).replace(",", ".").strip()
            return float(limpo) if limpo else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _limpar_numero(self, num_str):
        """Converte string numérica para int"""
        if not num_str:
            return 0
        try:
            return int(re.sub(r'\D', '', str(num_str)))
        except (ValueError, TypeError):
            return 0

    def _normalizar_url_imagem(self, img_url):
        if not img_url:
            return ""
        if img_url.startswith('http'):
            return img_url
        if img_url.startswith('//'):
            return f"https:{img_url}"
        return f"{DOMICILIUM_BASE_URL}{img_url}"

    def _extrair_fotos_slides(self, soup):
        fotos_extras = []
        for slide in soup.find_all('div', class_='sp-slide'):
            img_url = slide.get('data-src')
            if not img_url:
                img_tag = slide.find('img', class_='sp-image')
                img_url = img_tag.get('src') if img_tag else None
            url_completa = self._normalizar_url_imagem(img_url)
            if url_completa and url_completa not in fotos_extras:
                fotos_extras.append(url_completa)
        return fotos_extras

    def _extrair_caracteristicas(self, soup):
        caracteristicas = {}
        tab_caracteristicas = soup.select_one('#tab-0 ul.property-features')
        if not tab_caracteristicas:
            return caracteristicas
        for item in tab_caracteristicas.find_all('li'):
            valor_tag = item.find('b')
            if valor_tag:
                valor = valor_tag.get_text(strip=True)
                chave = item.get_text(" ", strip=True).replace(valor, "").replace(":", "").strip()
                caracteristicas[chave] = valor
        return caracteristicas

    def _extrair_atributos(self, soup):
        ul_atributos = soup.select_one('ul.checkboxes')
        if not ul_atributos:
            return ""
        lista_atributos = [
            item.get_text(strip=True)
            for item in ul_atributos.find_all('li')
            if item.get_text(strip=True)
        ]
        return ", ".join(lista_atributos)

    def _obter_detalhes_imovel(self, link_imovel):
        detalhes = {"caracteristicas": {}, "atributos": "", "fotos_extras": []}
        if not link_imovel or not link_imovel.startswith('http'):
            return detalhes

        try:
            response = self.session.get(link_imovel, timeout=12)
            if response.status_code != 200:
                return detalhes

            soup = BeautifulSoup(response.text, 'html.parser')
            detalhes["fotos_extras"] = self._extrair_fotos_slides(soup)
            detalhes["caracteristicas"] = self._extrair_caracteristicas(soup)
            detalhes["atributos"] = self._extrair_atributos(soup)

        except Exception:
            logging.exception(f"Erro detalhes {link_imovel}")

        return detalhes

    def _extrair_localizacao_card(self, card):
        h2_tag = card.find('h2', class_='neighborhood-and-city')
        local_raw = h2_tag.get_text(" ", strip=True) if h2_tag else ""
        if "São João Del Rei" in local_raw:
            bairro = local_raw.split("São João Del Rei")[0].strip() or BAIRRO_NAO_INFORMADO
            return bairro, CIDADE_PADRAO
        if CIDADE_TIRADENTES in local_raw:
            bairro = local_raw.split(CIDADE_TIRADENTES)[0].strip() or BAIRRO_NAO_INFORMADO
            return bairro, CIDADE_TIRADENTES
        if CIDADE_SANTA_CRUZ in local_raw:
            bairro = local_raw.split(CIDADE_SANTA_CRUZ)[0].strip() or BAIRRO_NAO_INFORMADO
            return bairro, CIDADE_SANTA_CRUZ
        return (local_raw or BAIRRO_NAO_INFORMADO), CIDADE_PADRAO

    def _extrair_capa_e_link(self, card):
        link_tag = card.find('a', class_='listing-img-container')
        if not link_tag:
            return "", []

        href = link_tag.get('href', '')
        link = f"{DOMICILIUM_BASE_URL}{href}" if href.startswith('/') else href
        fotos = []

        img_capa = link_tag.find('div', class_='imgAnuncio')
        if img_capa and 'style' in img_capa.attrs:
            m = re.search(r'url\((.*?)\)', img_capa['style'])
            if m:
                src_capa = m.group(1).replace('&amp;', '&').strip('\'"')
                fotos.append(self._normalizar_url_imagem(src_capa))

        return link, fotos

    def _extrair_area_card(self, titulo_tag):
        if not titulo_tag:
            return 0.0
        partes_h4 = titulo_tag.decode_contents().split('<br')
        return self._limpar_area(partes_h4[1]) if len(partes_h4) > 1 else 0.0

    def _inferir_tipo_por_titulo(self, titulo):
        titulo_lower = titulo.lower()
        if "lote" in titulo_lower or "terreno" in titulo_lower:
            return "Terreno"
        if "casa" in titulo_lower:
            return "Casa"
        if "apartamento" in titulo_lower:
            return "Apartamento"
        if "comercial" in titulo_lower:
            return "Comercial"
        return "Imóvel"

    def _processar_card(self, card, modalidade):
        try:
            cod_tag = card.find('span', class_='span-cod-lista')
            codigo = cod_tag.get_text(strip=True).replace('Cód.', '').strip() if cod_tag else ""
            if not codigo:
                return None

            titulo_tag = card.find('h4', class_='titulo-limite')
            titulo = titulo_tag.get_text(" ", strip=True) if titulo_tag else ""
            preco_tag = card.find('span', class_='listing-price')
            valor_raw = preco_tag.get_text(strip=True) if preco_tag else "0"

            bairro, cidade = self._extrair_localizacao_card(card)
            link, fotos = self._extrair_capa_e_link(card)
            area_card = self._extrair_area_card(titulo_tag)

            detalhes = self._obter_detalhes_imovel(link) if link else {}
            feats = detalhes.get("caracteristicas", {})

            for f in detalhes.get("fotos_extras", []):
                if f not in fotos:
                    fotos.append(f)

            area_util = self._limpar_area(feats.get("Área construída"))
            if area_util <= 0.0 and area_card > 0.0:
                area_util = area_card

            imovel = {
                "id_unico": f"Domicilium_{codigo}",
                "imobiliaria": "Domicilium",
                "codigo_original": codigo,
                "titulo": titulo,
                "modalidade": modalidade,
                "tipo": self._inferir_tipo_por_titulo(titulo),
                "preco": self._limpar_valor(valor_raw),
                "bairro": bairro,
                "cidade": cidade,
                "quartos": self._limpar_numero(feats.get("Quartos", "0")),
                "banheiros": self._limpar_numero(feats.get("Banheiros", "0")),
                "vagas": self._limpar_numero(feats.get("Garagens", "0")),
                "area_util": area_util,
                "area_total": self._limpar_area(feats.get("Área do terreno")),
                "link": link,
                "fotos": fotos,
                "extras": {
                    "atributos": detalhes.get("atributos", ""),
                    "suites": self._limpar_numero(feats.get("Suítes", "0")),
                    "salas": self._limpar_numero(feats.get("Salas", "0"))
                }
            }
            return normalizar_imovel(imovel)
        except Exception:
            logging.exception("Erro ao processar card Domicilium")
            return None

    def _extrair_dados_html(self, html_content, modalidade):
        soup = BeautifulSoup(html_content, 'html.parser')
        cards = soup.find_all('div', class_='listing-item')

        if not cards:
            return []

        imoveis_padronizados = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self._processar_card, card, modalidade) for card in cards]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    imoveis_padronizados.append(res)

        return imoveis_padronizados

    def _coletar_modalidade(self, nome_modalidade, filtro_string):
        imoveis = []
        page = 1

        logging.info(f"--- Iniciando Domicilium: {nome_modalidade} ---")

        while True:
            try:
                payload = {'page': str(page), 'FiltroBusca': filtro_string}
                response = self.session.post(self.endpoint, data=payload, timeout=20)

                if not response.text.strip() or len(response.text) < 50:
                    break

                novos = self._extrair_dados_html(response.text, nome_modalidade)
                if not novos:
                    break

                logging.info(f"Domicilium {nome_modalidade} pág {page}: {len(novos)} imóveis processados")
                imoveis.extend(novos)
                page += 1
                time.sleep(0.5)
            except Exception:
                logging.exception(f"Erro Domicilium pag {page}")
                break

        return imoveis

    def buscar_imoveis(self):
        todos = []
        todos.extend(self._coletar_modalidade("VENDA", self.filtro_venda))
        todos.extend(self._coletar_modalidade("ALUGUEL", self.filtro_aluguel))
        return todos


if __name__ == "__main__":
    crawler = DomiciliumCrawler()
    res = crawler.buscar_imoveis()
    print(f"Total Domicilium: {len(res)}")