import requests
import time
import logging
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DomiciliumCrawler:
    def __init__(self):
        self.endpoint = "https://www.domiciliumimoveis.com.br/fetch_pages.php"
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

    def _obter_detalhes_imovel(self, link_imovel):
        detalhes = {"caracteristicas": {}, "atributos": "", "fotos_extras": []}
        if not link_imovel or not link_imovel.startswith('http'):
            return detalhes

        try:
            response = self.session.get(link_imovel, timeout=12)
            if response.status_code != 200:
                return detalhes

            soup = BeautifulSoup(response.text, 'html.parser')

            # Fotos Extras
            slides = soup.find_all('div', class_='sp-slide')
            for slide in slides:
                img_url = slide.get('data-src')
                if not img_url:
                    img_tag = slide.find('img', class_='sp-image')
                    if img_tag:
                        img_url = img_tag.get('src')

                if img_url:
                    if not img_url.startswith('http'):
                        if img_url.startswith('//'):
                            img_url = f"https:{img_url}"
                        else:
                            img_url = f"https://www.domiciliumimoveis.com.br{img_url}"

                    if img_url not in detalhes["fotos_extras"]:
                        detalhes["fotos_extras"].append(img_url)

            # Características
            tab_caracteristicas = soup.select_one('#tab-0 ul.property-features')
            if tab_caracteristicas:
                for item in tab_caracteristicas.find_all('li'):
                    valor_tag = item.find('b')
                    if valor_tag:
                        valor = valor_tag.get_text(strip=True)
                        chave = item.get_text(" ", strip=True).replace(valor, "").replace(":", "").strip()
                        detalhes["caracteristicas"][chave] = valor

            # Atributos
            lista_atributos = []
            ul_atributos = soup.select_one('ul.checkboxes')
            if ul_atributos:
                for item in ul_atributos.find_all('li'):
                    texto = item.get_text(strip=True)
                    if texto:
                        lista_atributos.append(texto)
            detalhes["atributos"] = ", ".join(lista_atributos)

        except Exception as e:
            logging.error(f"Erro detalhes {link_imovel}: {e}")

        return detalhes

    def _processar_card(self, card, modalidade):
        try:
            titulo_tag = card.find('h4', class_='titulo-limite')
            titulo = titulo_tag.get_text(" ", strip=True) if titulo_tag else ""
            codigo = card.find('span', class_='span-cod-lista').get_text(strip=True).replace('Cód.', '').strip() if card.find('span', class_='span-cod-lista') else ""
            valor_raw = card.find('span', class_='listing-price').get_text(strip=True) if card.find('span', class_='listing-price') else "0"

            if not codigo:
                return None

            # Localização: "Matosinhos São João Del Rei / MG"
            local_raw = card.find('h2', class_='neighborhood-and-city').get_text(" ", strip=True) if card.find('h2', class_='neighborhood-and-city') else ""
            bairro = "Não Informado"
            cidade = "São João del Rei"
            if "São João Del Rei" in local_raw:
                partes = local_raw.split("São João Del Rei")
                bairro = partes[0].strip() or "Não Informado"
            elif "Tiradentes" in local_raw:
                cidade = "Tiradentes"
                partes = local_raw.split("Tiradentes")
                bairro = partes[0].strip() or "Não Informado"
            elif "Santa Cruz de Minas" in local_raw:
                cidade = "Santa Cruz de Minas"
                partes = local_raw.split("Santa Cruz de Minas")
                bairro = partes[0].strip() or "Não Informado"
            elif local_raw:
                bairro = local_raw

            link_tag = card.find('a', class_='listing-img-container')
            link = ""
            fotos = []

            if link_tag:
                href = link_tag.get('href', '')
                link = f"https://www.domiciliumimoveis.com.br{href}" if href.startswith('/') else href
                img_capa = link_tag.find('div', class_='imgAnuncio')
                if img_capa and 'style' in img_capa.attrs:
                    m = re.search(r'url\((.*?)\)', img_capa['style'])
                    if m:
                        src_capa = m.group(1).replace('&amp;', '&').strip('\'"')
                        if not src_capa.startswith('http'):
                            src_capa = f"https://www.domiciliumimoveis.com.br{src_capa}"
                        fotos.append(src_capa)

            # Tenta pegar área informada no card como fallback
            area_card = 0.0
            if titulo_tag:
                partes_h4 = titulo_tag.decode_contents().split('<br')
                if len(partes_h4) > 1:
                    area_card = self._limpar_area(partes_h4[1])

            # Coleta detalhes da página individual
            detalhes = self._obter_detalhes_imovel(link) if link else {}
            feats = detalhes.get("caracteristicas", {})

            for f in detalhes.get("fotos_extras", []):
                if f not in fotos:
                    fotos.append(f)

            area_util = self._limpar_area(feats.get("Área construída"))
            if area_util == 0.0 and area_card > 0.0:
                area_util = area_card

            tipo = "Imóvel"
            titulo_lower = titulo.lower()
            if "lote" in titulo_lower or "terreno" in titulo_lower:
                tipo = "Terreno"
            elif "casa" in titulo_lower:
                tipo = "Casa"
            elif "apartamento" in titulo_lower:
                tipo = "Apartamento"
            elif "comercial" in titulo_lower:
                tipo = "Comercial"

            imovel = {
                "id_unico": f"Domicilium_{codigo}",
                "imobiliaria": "Domicilium",
                "codigo_original": codigo,
                "titulo": titulo,
                "modalidade": modalidade,
                "tipo": tipo,
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
            return imovel
        except Exception as e:
            logging.error(f"Erro ao processar card Domicilium: {e}")
            return None

    def _extrair_dados_html(self, html_content, modalidade):
        soup = BeautifulSoup(html_content, 'html.parser')
        cards = soup.find_all('div', class_='listing-item')

        if not cards:
            return []

        imoveis_padronizados = []
        # Processa cards com concorrência para obter detalhes mais rapidamente
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
        continuar = True

        logging.info(f"--- Iniciando Domicilium: {nome_modalidade} ---")

        while continuar:
            try:
                payload = {'page': str(page), 'FiltroBusca': filtro_string}
                response = self.session.post(self.endpoint, data=payload, timeout=20)

                if not response.text.strip() or len(response.text) < 50:
                    break

                novos = self._extrair_dados_html(response.text, nome_modalidade)

                if not novos:
                    continuar = False
                else:
                    logging.info(f"Domicilium {nome_modalidade} pág {page}: {len(novos)} imóveis processados")
                    imoveis.extend(novos)
                    page += 1
                    time.sleep(0.5)
            except Exception as e:
                logging.error(f"Erro Domicilium pag {page}: {e}")
                continuar = False

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