import requests
import time
import logging
import re
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FlavioCrawler:
    def __init__(self):
        self.base_url = "https://flaviovitorimoveis.com.br"
        self.search_url = "https://flaviovitorimoveis.com.br/imoveis"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def _limpar_valor(self, valor_str):
        if not valor_str or "Consulte" in valor_str: return 0.0
        try:
            limpo = valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(limpo)
        except:
            return 0.0

    def _limpar_numero(self, num_str):
        if not num_str: return 0
        try:
            return int(re.sub(r'\D', '', str(num_str)))
        except:
            return 0

    def _limpar_area(self, area_str):
        if not area_str: return 0.0
        try:
            # Remove m² e outros caracteres, mantendo numeros e virgula/ponto
            limpo = re.sub(r'[^\d,.]', '', area_str).replace(",", ".")
            return float(limpo)
        except:
            return 0.0

    def _obter_detalhes_imovel(self, link_imovel):
        """
        Acessa a página individual para pegar fotos do Swiper e características.
        """
        detalhes = {
            "fotos_extras": [],
            "quartos": 0,
            "banheiros": 0,
            "vagas": 0,
            "extras": {}
        }

        if not link_imovel or not link_imovel.startswith('http'):
            return detalhes

        try:
            # Delay para não derrubar o site, já que faremos muitos requests seguidos
            time.sleep(0.2) 
            response = requests.get(link_imovel, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return detalhes

            soup = BeautifulSoup(response.text, 'html.parser')

            # --- 1. FOTOS (Swiper Gallery) ---
            # As fotos estão em: <div class="swiper-slide img-gallery" data-src="...">
            slides = soup.find_all('div', class_='img-gallery')
            
            for slide in slides:
                img_url = slide.get('data-src')
                if img_url:
                    # Garante protocolo https
                    if img_url.startswith('//'):
                        img_url = f"https:{img_url}"
                    elif not img_url.startswith('http'):
                        # Se for caminho relativo, tenta montar a URL (raro nesse site, mas preventivo)
                        if "homeclix" in img_url:
                             img_url = f"https://www.homeclix.com.br{img_url}" if img_url.startswith('/') else img_url
                        else:
                             img_url = f"{self.base_url}{img_url}"
                    
                    if img_url not in detalhes["fotos_extras"]:
                        detalhes["fotos_extras"].append(img_url)

            # --- 2. CARACTERÍSTICAS ---
            # Estão em lista: <li><span class="font-weight-bold">Chave:</span> <span class="det">Valor</span></li>
            lista_detalhes = soup.find_all('ul', class_='homes-list')
            
            for ul in lista_detalhes:
                itens = ul.find_all('li')
                for item in itens:
                    key_span = item.find('span', class_='font-weight-bold')
                    val_span = item.find('span', class_='det')
                    
                    if key_span and val_span:
                        chave = key_span.get_text(strip=True).replace(':', '').lower()
                        valor = val_span.get_text(strip=True)
                        valor_num = self._limpar_numero(valor)
                        
                        if 'quartos' in chave: detalhes['quartos'] = valor_num
                        elif 'banheiro' in chave: detalhes['banheiros'] = valor_num
                        elif 'garagens' in chave or 'vagas' in chave: detalhes['vagas'] = valor_num
                        # Extras
                        elif 'suítes' in chave: detalhes['extras']['suites'] = valor_num
                        elif 'salas' in chave: detalhes['extras']['salas'] = valor_num
                        elif 'cozinhas' in chave: detalhes['extras']['cozinhas'] = valor_num
                        elif 'pavimentos' in chave: detalhes['extras']['pavimentos'] = valor_num

        except Exception as e:
            logging.error(f"Erro ao ler detalhes {link_imovel}: {e}")

        return detalhes

    def _extrair_dados_html(self, html_content, modalidade):
        soup = BeautifulSoup(html_content, 'html.parser')
        imoveis_encontrados = []
        
        # Pega todos os cards de uma vez
        cards = soup.find_all('div', class_='item')
        total_cards = len(cards)
        
        logging.info(f"Processando lista completa de {total_cards} imóveis ({modalidade})...")

        for i, card in enumerate(cards):
            try:
                # --- Link ---
                project_single = card.find('div', class_='project-single')
                if not project_single: continue

                link_tag = project_single.find('a', class_='homes-img')
                link = ""
                if link_tag and link_tag.get('href'):
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = f"{self.base_url}{link}"

                # --- Código ---
                codigo = ""
                div_price = card.find('div', class_='homes-price')
                if div_price:
                    codigo = div_price.get_text(strip=True).replace("Código", "").strip()

                if not codigo: continue 

                # --- Título ---
                titulo = ""
                h3_tag = card.find('h3')
                if h3_tag: titulo = h3_tag.get_text(strip=True)

                # --- Endereço (Bairro e Cidade) ---
                # Ex: <span><b>Bairro</b><br>Cidade</span>
                bairro = "Não Informado"
                cidade = "São João del Rei"
                
                address_p = card.find('p', class_='homes-address')
                if address_p:
                    span_addr = address_p.find('span')
                    if span_addr:
                        # Pega o HTML interno para separar pelo <br>
                        # decode_contents() retorna a string HTML interna (ex: "<b>Centro</b><br>Cidade")
                        # Se não funcionar em versoes antigas do BS4, usamos encode_contents().decode()
                        texto_html = span_addr.decode_contents() 
                        partes = texto_html.split('<br') # Split no <br> ou <br/>
                        
                        if len(partes) >= 1:
                            # Limpa tags do bairro (ex: <b>Centro</b> -> Centro)
                            bairro = BeautifulSoup(partes[0], 'html.parser').get_text(strip=True)
                        if len(partes) >= 2:
                            # Limpa tags da cidade (geralmente texto puro ou >Cidade)
                            cidade_raw = partes[1].replace('/>', '').replace('>', '') # Limpeza basica de sobra de tag
                            cidade = BeautifulSoup(cidade_raw, 'html.parser').get_text(strip=True)

                # --- Preço ---
                preco = 0.0
                div_valor = card.find('div', class_='price-properties')
                if div_valor:
                    preco_txt = div_valor.get_text(strip=True)
                    preco = self._limpar_valor(preco_txt)

                # --- Área (Tentativa no card) ---
                area_util = 0.0
                ul_list = card.find('ul', class_='homes-list')
                if ul_list:
                    lis = ul_list.find_all('li')
                    for li in lis:
                        texto = li.get_text(strip=True)
                        icone = li.find('i')
                        classe_icone = str(icone.get('class')) if icone else ""
                        if 'object-group' in classe_icone or 'ruler' in classe_icone:
                            area_util = self._limpar_area(texto)

                # --- BUSCA DETALHADA ---
                # Aqui vamos em cada página pegar as fotos e dados reais
                logging.info(f"[{i+1}/{total_cards}] Detalhes: {codigo} - {titulo}")
                detalhes = self._obter_detalhes_imovel(link)
                
                # Foto de Capa (Thumbnail) - Caso o detalhe falhe ou não tenha fotos
                fotos = detalhes["fotos_extras"]
                if not fotos:
                    img_tag = card.find('img', class_='img-responsive')
                    if img_tag and img_tag.get('src'):
                        src = img_tag.get('src')
                        if "semimagem" not in src: # Evita imagem padrão de 'sem foto'
                            if not src.startswith('http'): src = f"{self.base_url}{src}"
                            fotos.append(src)

                # Montagem final
                imovel = {
                    "id_unico": f"Flavio_{codigo}",
                    "imobiliaria": "Flávio Vitor",
                    "codigo_original": codigo,
                    "titulo": titulo,
                    "modalidade": modalidade,
                    "tipo": self._inferir_tipo(titulo),
                    "preco": preco,
                    "bairro": bairro,
                    "cidade": cidade,
                    "quartos": detalhes.get('quartos', 0),
                    "banheiros": detalhes.get('banheiros', 0),
                    "vagas": detalhes.get('vagas', 0),
                    "area_util": area_util,
                    "area_total": 0.0,
                    "link": link,
                    "fotos": fotos,
                    "extras": detalhes.get('extras', {})
                }
                
                # Fallback: Se o detalhe vier zerado, tenta pegar quartos do card
                if imovel['quartos'] == 0 and ul_list:
                     for li in ul_list.find_all('li'):
                        if 'fa-bed' in str(li):
                            imovel['quartos'] = self._limpar_numero(li.get_text())

                imoveis_encontrados.append(imovel)

            except Exception as e:
                logging.error(f"Erro card {i}: {e}")

        return imoveis_encontrados

    def _inferir_tipo(self, titulo):
        titulo_lower = titulo.lower()
        if "lote" in titulo_lower or "terreno" in titulo_lower: return "Terreno"
        if "casa" in titulo_lower: return "Casa"
        if "apartamento" in titulo_lower: return "Apartamento"
        if "comercial" in titulo_lower or "loja" in titulo_lower or "galpao" in titulo_lower: return "Comercial"
        if "sitio" in titulo_lower or "chácara" in titulo_lower or "fazenda" in titulo_lower: return "Rural"
        return "Imovel"

    def _coletar_modalidade(self, modalidade_nome, payload):
        logging.info(f"--- Iniciando Flavio Vitor: {modalidade_nome} ---")
        try:
            # POST ÚNICO QUE TRAZ TUDO
            response = requests.post(self.search_url, data=payload, headers=self.headers, timeout=60)
            
            if response.status_code == 200:
                # O HTML retornado contém a lista completa
                return self._extrair_dados_html(response.text, modalidade_nome)
            else:
                logging.error(f"Erro request Flavio {modalidade_nome}: {response.status_code}")
                return []

        except Exception as e:
            logging.error(f"Erro fatal Flavio {modalidade_nome}: {e}")
            return []

    def buscar_imoveis(self):
        todos = []
        
        # Venda
        payload_venda = {
            'codigo': '',
            'imovel_para': '1', 
            'valor_de': '0,00',
            'valor_ate': '0,00',
            'bairro[]': [], 'cidades[]': [], 'quartos[]': [],
        }
        todos.extend(self._coletar_modalidade("VENDA", payload_venda))

        # Aluguel
        payload_aluguel = {
            'codigo': '',
            'imovel_para': '2',
            'valor_de': '0,00',
            'valor_ate': '0,00'
        }
        todos.extend(self._coletar_modalidade("ALUGUEL", payload_aluguel))
        
        return todos

if __name__ == "__main__":
    c = FlavioCrawler()
    res = c.buscar_imoveis()
    print(f"Total: {len(res)}")