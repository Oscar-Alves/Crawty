import requests
import time
import logging
import re
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChavesCrawler:
    def __init__(self):
        self.endpoint = "https://chavescorretora.com.br/fetch_pages.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        # Payloads de filtro
        self.filtro_venda = {
            'FiltroBusca[id_modalidade]': '1',
            'FiltroBusca[valor_de]': '',
            'FiltroBusca[valor_ate]': '',
            'FiltroBusca[codigo]': ''
        }
        self.filtro_aluguel = {
            'FiltroBusca[id_modalidade]': '2',
            'FiltroBusca[valor_de]': '',
            'FiltroBusca[valor_ate]': '',
            'FiltroBusca[codigo]': ''
        }

    def _limpar_valor(self, valor_str):
        if not valor_str: return 0.0
        try:
            return float(valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip())
        except:
            return 0.0

    def _limpar_numero(self, num_str):
        if not num_str: return 0
        try:
            # Remove tudo que não é dígito
            return int(re.sub(r'\D', '', str(num_str)))
        except:
            return 0

    def _limpar_area(self, area_str):
        if not area_str: return 0.0
        try:
            # Pega "300 m²", remove texto, ajusta vírgula
            limpo = re.sub(r'[^\d,.]', '', area_str).replace(",", ".")
            return float(limpo)
        except:
            return 0.0

    def _obter_detalhes_imovel(self, link_imovel):
        """
        Acessa a página do imóvel para pegar: Suítes, Salas, Cozinhas e Atributos.
        """
        detalhes = {
            "quartos": 0,
            "banheiros": 0, 
            "vagas": 0,
            "extras": {},
            "atributos_lista": [], # Para guardar "Portão Eletrônico", etc.
            "fotos_extras": []
        }

        if not link_imovel or not link_imovel.startswith('http'):
            return detalhes

        try:
            time.sleep(0.3) # Delay para não bloquear
            response = requests.get(link_imovel, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return detalhes

            soup = BeautifulSoup(response.text, 'html.parser')

            # --- CAPTURA DE FOTOS (Baseado no snippet fornecido) ---
            # Procura pelo container do slider (pelo ID ou Classe)
            slider_container = soup.select_one('#owl-demo') or soup.select_one('.listing_single_property_slider')

            if slider_container:
                # Busca os itens da galeria (tags <a> com classe 'img-gallery')
                galeria_items = slider_container.find_all('a', class_='img-gallery')
                
                for item in galeria_items:
                    # Prioridade: atributo 'data-src' (imagem full)
                    img_url = item.get('data-src')
                    
                    # Fallback: atributo 'href' se for um link de imagem
                    if not img_url:
                        img_url = item.get('href')
                    
                    # Fallback 2: tag <img> filha
                    if not img_url:
                        img_tag = item.find('img')
                        if img_tag:
                            img_url = img_tag.get('src')

                    # Adiciona se encontrou uma URL válida
                    if img_url:
                        # Garante URL absoluta (embora o snippet mostre que já vem absoluta)
                        if not img_url.startswith('http'):
                            if img_url.startswith('//'):
                                img_url = f"https:{img_url}"
                            else:
                                img_url = f"https://chavescorretora.com.br{img_url}"
                        
                        detalhes['fotos_extras'].append(img_url)

            # --- 1. Extração das "Características" (Chave: Valor) ---
            # No HTML enviado: <div class="property-features"> ... <div class="row col-lg-4 ..."> <div>Quartos: 5</div>
            features_container = soup.find('div', class_='property-features')
            if features_container:
                # Pega todas as divs que parecem ser itens da lista
                itens = features_container.find_all('div', class_=lambda x: x and 'col-lg-4' in x)
                
                for item in itens:
                    # O texto está na última div filha. Ex: <div>Quartos: 5</div>
                    divs_internas = item.find_all('div')
                    if divs_internas:
                        texto_completo = divs_internas[-1].get_text(strip=True) # "Quartos: 5"
                        
                        if ':' in texto_completo:
                            chave, valor = texto_completo.split(':', 1)
                            chave = chave.lower().strip()
                            valor_limpo = self._limpar_numero(valor)
                            
                            # Mapeia para o padrão unificado
                            if 'quartos' in chave: detalhes['quartos'] = valor_limpo
                            elif 'banheiros' in chave: detalhes['banheiros'] = valor_limpo
                            elif 'garagens' in chave or 'vagas' in chave: detalhes['vagas'] = valor_limpo
                            elif 'suítes' in chave or 'suites' in chave: detalhes['extras']['suites'] = valor_limpo
                            elif 'salas' in chave: detalhes['extras']['salas'] = valor_limpo
                            elif 'cozinhas' in chave: detalhes['extras']['cozinhas'] = valor_limpo
                            elif 'serviços' in chave: detalhes['extras']['area_servico'] = valor_limpo
            
            # --- 2. Extração de "Atributos" (Checklist) ---
            # Geralmente ficam em listas <ul> com classes como 'list-style-one' ou dentro de property-features também
            # Vou buscar listas genéricas dentro da área de detalhes caso existam
            ul_listas = soup.find_all('ul', class_='list-style-one')
            for ul in ul_listas:
                lis = ul.find_all('li')
                for li in lis:
                    attr = li.get_text(strip=True)
                    if attr:
                        detalhes['atributos_lista'].append(attr)

        except Exception as e:
            logging.error(f"Erro ao ler detalhes {link_imovel}: {e}")

        return detalhes

    def _extrair_dados_html(self, html_content, modalidade):
        soup = BeautifulSoup(html_content, 'html.parser')
        imoveis_encontrados = []
        cards = soup.find_all('div', class_='property-block')

        for card in cards:
            try:
                # --- DADOS DO CARD (Listagem) ---
                image_box = card.find('div', class_='image-box')
                link_tag = image_box.find('a') if image_box else None
                link = f"https://chavescorretora.com.br{link_tag['href']}" if link_tag else ""

                # FOTO DE CAPA (Thumbnail do Card)
                fotos = []
                if image_box:
                    img_tag = image_box.find('img')
                    if img_tag and img_tag.get('src'):
                        src = img_tag['src']
                        if not src.startswith('http'):
                             src = f"https://chavescorretora.com.br{src}"
                        fotos.append(src)
                
                # Stickers (Código e Preço)
                stickers = card.find_all('div', class_='card-sticker')
                codigo = ""
                valor_raw = "0"
                for s in stickers:
                    txt = s.get_text(strip=True)
                    if "Cód." in txt: codigo = txt.replace("Cód.", "").strip()
                    elif "R$" in txt: valor_raw = txt
                
                # Localização e Tipo
                lower = card.find('div', class_='lower-content')
                h3 = lower.find('h3') if lower else None
                tipo = "Indefinido"
                bairro = "Indefinido"
                titulo = ""
                
                if h3:
                    titulo = h3.get_text(" ", strip=True) # Ex: "Casa / Centro"
                    if "/" in titulo:
                        partes = titulo.split("/")
                        tipo = partes[0].strip()
                        bairro = partes[1].strip()
                
                # Área (Tenta pegar do card se tiver, geralmente é um ícone flaticon-dimension)
                area = 0.0
                icone_area = card.find('i', class_='flaticon-dimension')
                if icone_area:
                    # O texto costuma estar no pai ou irmão do ícone
                    area_txt = icone_area.parent.get_text(strip=True)
                    area = self._limpar_area(area_txt)

                # --- DADOS DETALHADOS (GET na Página) ---
                logging.info(f"Coletando detalhes: {codigo}")
                detalhes = self._obter_detalhes_imovel(link)

                if detalhes.get('fotos_extras'):
                    for f in detalhes['fotos_extras']:
                        if f not in fotos:
                            fotos.append(f)
                
                # Merge de dados (Prioriza o detalhe, se for 0 usa o do card)
                quartos = detalhes['quartos']
                banheiros = detalhes['banheiros']
                vagas = detalhes['vagas']

                # Monta Objeto Unificado
                imovel = {
                    "id_unico": f"Chaves_{codigo}",
                    "imobiliaria": "Chaves Corretora",
                    "codigo_original": codigo,
                    "titulo": f"{tipo} em {bairro}",
                    "modalidade": modalidade,
                    "tipo": tipo,
                    "preco": self._limpar_valor(valor_raw),
                    "bairro": bairro,
                    "cidade": "São João del Rei", # Chaves é focada nesta cidade
                    "quartos": quartos,
                    "banheiros": banheiros,
                    "vagas": vagas,
                    "area_util": area,
                    "area_total": 0.0,
                    "link": link,
                    "fotos": fotos,
                    "extras": {
                        **detalhes['extras'], # Desempacota suites, salas, cozinhas
                        "atributos": ", ".join(detalhes['atributos_lista'])
                    }
                }
                imoveis_encontrados.append(imovel)

            except Exception as e:
                logging.error(f"Erro ao processar card Chaves: {e}")

        return imoveis_encontrados

    def _coletar_modalidade(self, modalidade_nome, payload_base):
        imoveis = []
        page = 1
        continuar = True
        
        logging.info(f"--- Iniciando Chaves: {modalidade_nome} ---")

        while continuar:
            # TRAVA DE SEGURANÇA
            if page > 1:
                logging.info("Limite de 1 páginas atingido (Teste). Parando.")
                break

            try:
                payload = payload_base.copy()
                payload['page'] = str(page)
                
                logging.info(f"Requisitando pág {page}...")
                response = requests.post(self.endpoint, data=payload, headers=self.headers, timeout=20)
                
                if not response.text.strip() or len(response.text) < 50: break
                
                novos = self._extrair_dados_html(response.text, modalidade_nome)
                if not novos:
                    continuar = False
                else:
                    imoveis.extend(novos)
                    page += 1
                    time.sleep(1)

            except Exception as e:
                logging.error(f"Erro pág {page}: {e}")
                continuar = False

        return imoveis

    def buscar_imoveis(self):
        todos = []
        todos.extend(self._coletar_modalidade("VENDA", self.filtro_venda))
        todos.extend(self._coletar_modalidade("ALUGUEL", self.filtro_aluguel))
        return todos

if __name__ == "__main__":
    c = ChavesCrawler()
    res = c.buscar_imoveis()
    print(f"Coletados: {len(res)}")