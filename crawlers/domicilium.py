import requests
import time
import logging
import re
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DomiciliumCrawler:
    def __init__(self):
        self.endpoint = "https://www.domiciliumimoveis.com.br/fetch_pages.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.filtro_aluguel = "codigo=&id_modalidade%5B%5D=2&de_valor=10000&ate_valor=2000000&valor_de=100&valor_ate=100000&ordenacao=3"
        self.filtro_venda = "codigo=&id_modalidade%5B%5D=1&de_valor=10000&ate_valor=2000000&valor_de=10000&valor_ate=10000000&ordenacao=3"

    def _limpar_valor(self, valor_str):
        """Converte 'R$ 1.200,00' para 1200.00"""
        if not valor_str: return 0.0
        try:
            limpo = valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(limpo)
        except:
            return 0.0

    def _limpar_area(self, area_str):
        """Converte '135,92 m²' para 135.92"""
        if not area_str: return None
        try:
            # Pega apenas números, pontos e vírgulas iniciais
            limpo = re.sub(r'[^\d,.]', '', area_str).replace(",", ".")
            return float(limpo)
        except:
            return None

    def _limpar_numero(self, num_str):
        """Converte string numérica para int"""
        if not num_str: return 0
        try:
            return int(re.sub(r'\D', '', str(num_str)))
        except:
            return 0

    def _obter_detalhes_imovel(self, link_imovel):
        detalhes = {"caracteristicas": {}, "atributos": "", "fotos_extras": []}
        if not link_imovel or not link_imovel.startswith('http'): return detalhes

        try:
            time.sleep(0.3) 
            response = requests.get(link_imovel, headers=self.headers, timeout=10)
            if response.status_code != 200: return detalhes

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
                    if texto: lista_atributos.append(texto)
            detalhes["atributos"] = ", ".join(lista_atributos)

        except Exception as e:
            logging.error(f"Erro detalhes {link_imovel}: {e}")

        return detalhes

    def _extrair_dados_html(self, html_content, modalidade):
        soup = BeautifulSoup(html_content, 'html.parser')
        imoveis_padronizados = []
        cards = soup.find_all('div', class_='listing-item')

        for card in cards:
            try:
                # Extração Bruta
                titulo = card.find('h4', class_='titulo-limite').get_text(" ", strip=True) if card.find('h4', class_='titulo-limite') else ""
                codigo = card.find('span', class_='span-cod-lista').get_text(strip=True).replace('Cód.', '').strip() if card.find('span', class_='span-cod-lista') else ""
                valor_raw = card.find('span', class_='listing-price').get_text(strip=True) if card.find('span', class_='listing-price') else "0"
                
                # Localização: "Matosinhos São João Del Rei / MG"
                # Tenta separar Bairro de Cidade
                local_raw = card.find('h2', class_='neighborhood-and-city').get_text(" ", strip=True) if card.find('h2', class_='neighborhood-and-city') else ""
                bairro = "Desconhecido"
                cidade = "São João del Rei" # Default
                if "São João Del Rei" in local_raw:
                    partes = local_raw.split("São João Del Rei")
                    bairro = partes[0].strip()
                elif "Tiradentes" in local_raw:
                    cidade = "Tiradentes"
                    partes = local_raw.split("Tiradentes")
                    bairro = partes[0].strip()
                elif "Santa Cruz de Minas" in local_raw:
                    cidade = "Santa Cruz de Minas"
                    partes = local_raw.split("Santa Cruz de Minas")
                    bairro = partes[0].strip()
                else:
                    bairro = local_raw # Fallback

                link_tag = card.find('a', class_='listing-img-container')
                link = f"https://www.domiciliumimoveis.com.br{link_tag['href']}" if link_tag else ""

                fotos = []
                
                if link_tag:
                    link = f"https://www.domiciliumimoveis.com.br{link_tag['href']}"
                    img_capa = link_tag.find('img')
                    if img_capa and img_capa.get('src'):
                        src_capa = img_capa['src']
                        if not src_capa.startswith('http'):
                             src_capa = f"https://www.domiciliumimoveis.com.br{src_capa}"
                        fotos.append(src_capa)

                # Detalhes
                logging.info(f"Coletando detalhes: {codigo}")
                detalhes = self._obter_detalhes_imovel(link)
                feats = detalhes["caracteristicas"]

                if detalhes.get("fotos_extras"):
                    for f in detalhes["fotos_extras"]:
                        if f not in fotos:
                            fotos.append(f)

                # Padronização
                imovel_unificado = {
                    "id_unico": f"Domicilium_{codigo}",
                    "imobiliaria": "Domicilium",
                    "codigo_original": codigo,
                    "titulo": titulo,
                    "modalidade": modalidade, # Vem do argumento da função
                    "tipo": "Imovel", # Pode tentar inferir do título se contém "Lote", "Casa"
                    "preco": self._limpar_valor(valor_raw),
                    "bairro": bairro,
                    "cidade": cidade,
                    "quartos": self._limpar_numero(feats.get("Quartos", "0")),
                    "banheiros": self._limpar_numero(feats.get("Banheiros", "0")),
                    "vagas": self._limpar_numero(feats.get("Garagens", "0")),
                    "area_util": self._limpar_area(feats.get("Área construída")),
                    "area_total": self._limpar_area(feats.get("Área do terreno")),
                    "link": link,
                    "fotos": fotos, # Domicilium HTML é dificil pegar todas fotos sem entrar na galeria complexa
                    "extras": {
                        "atributos": detalhes["atributos"],
                        "suites": self._limpar_numero(feats.get("Suítes", "0")),
                        "salas": self._limpar_numero(feats.get("Salas", "0"))
                    }
                }
                
                # Refinamento de Tipo
                titulo_lower = titulo.lower()
                if "lote" in titulo_lower or "terreno" in titulo_lower: imovel_unificado["tipo"] = "Terreno"
                elif "casa" in titulo_lower: imovel_unificado["tipo"] = "Casa"
                elif "apartamento" in titulo_lower: imovel_unificado["tipo"] = "Apartamento"
                elif "comercial" in titulo_lower: imovel_unificado["tipo"] = "Comercial"

                imoveis_padronizados.append(imovel_unificado)

            except Exception as e:
                logging.error(f"Erro parse card: {e}")

        return imoveis_padronizados

    def _coletar_modalidade(self, nome_modalidade, filtro_string):
        imoveis = []
        page = 1
        continuar = True
        
        logging.info(f"--- Iniciando Domicilium: {nome_modalidade} ---")

        while continuar:
            # # TRAVA DE SEGURANÇA (REMOVER EM PROD)
            # if page > 1:
            #     logging.info("Limite de 1 páginas atingido (Teste). Parando.")
            #     break

            try:
                payload = {'page': str(page), 'FiltroBusca': filtro_string}
                response = requests.post(self.endpoint, data=payload, headers=self.headers, timeout=20)
                
                if not response.text.strip() or len(response.text) < 50: break
                
                # Passamos a modalidade aqui para ser incluída no objeto
                novos = self._extrair_dados_html(response.text, nome_modalidade)
                
                if not novos:
                    continuar = False
                else:
                    imoveis.extend(novos)
                    page += 1
                    time.sleep(1)
            except Exception as e:
                logging.error(f"Erro pag {page}: {e}")
                continuar = False

        return imoveis

    def buscar_imoveis(self):
        todos = []
        todos.extend(self._coletar_modalidade("VENDA", self.filtro_venda))
        todos.extend(self._coletar_modalidade("ALUGUEL", self.filtro_aluguel))
        return todos