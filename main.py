import os
import json
import logging
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

from crawlers import (
    ZanferCrawler,
    ChavesCrawler,
    FlavioCrawler,
    DomiciliumCrawler,
    LiderCrawler,
    KrasisCrawler,
    JFroesCrawler,
    FocoCrawler,
    BaseGestaoCrawler,
    ResendeCrawler,
    ContinuaCrawler,
    MendoncaCrawler,
    LongattiCrawler
)

# Diretório padrão para salvar os arquivos individuais de cada crawler
OUTPUT_DIR = "dados_imoveis"

# Configuração de Log para mostrar threads
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s')

def gerar_slug(texto):
    """
    Normaliza o nome da imobiliária para gerar nomes de arquivos seguros.
    Exemplo: 'Flávio Vitor' -> 'flavio_vitor', 'Líder' -> 'lider'
    """
    normalizado = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    slug = ''.join(c if c.isalnum() else '_' for c in normalizado.lower()).strip('_')
    while '__' in slug:
        slug = slug.replace('__', '_')
    return slug

def salvar_dados(nome_arquivo, dados):
    """
    Salva os dados coletados de um crawler em um arquivo JSON individual.
    """
    try:
        os.makedirs(os.path.dirname(nome_arquivo), exist_ok=True)
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f"-> Arquivo salvo com sucesso: '{nome_arquivo}' ({len(dados)} imóveis)")
    except IOError as e:
        print(f"Erro ao salvar arquivo '{nome_arquivo}': {e}")

def executar_crawler(crawler_class, source_name, output_dir=OUTPUT_DIR):
    """
    Função wrapper para instanciar, rodar e salvar imediatamente o JSON individual do crawler.
    """
    try:
        print(f"> Iniciando Crawler: {source_name}...")
        start_time = time.time()
        
        crawler = crawler_class()
        imoveis = crawler.buscar_imoveis()
        
        # Marca a fonte em cada imóvel
        for imovel in imoveis:
            imovel['crawler_source'] = source_name
            
        duration = time.time() - start_time
        print(f"> Finalizado {source_name}. Capturados: {len(imoveis)} em {duration:.2f}s")
        
        # Salva o arquivo individual imediatamente após o processamento
        slug = gerar_slug(source_name)
        caminho_arquivo = os.path.join(output_dir, f"imoveis_{slug}.json")
        salvar_dados(caminho_arquivo, imoveis)
        
        return {
            "source": source_name,
            "arquivo": caminho_arquivo,
            "total": len(imoveis),
            "tempo": duration,
            "sucesso": True
        }
    except Exception as e:
        print(f"ERRO CRÍTICO no crawler {source_name}: {e}")
        return {
            "source": source_name,
            "arquivo": None,
            "total": 0,
            "tempo": 0.0,
            "sucesso": False,
            "erro": str(e)
        }

def main():
    start_global = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Lista de crawlers para rodar
    tasks = [
        # Imobiliárias de São João del Rei
        (ZanferCrawler, 'Zanfer'),
        (ChavesCrawler, 'Chaves'),
        (FlavioCrawler, 'Flavio Vitor'),
        # (DomiciliumCrawler, 'Domicilium'),
        (LiderCrawler, 'Líder'),
        (KrasisCrawler, 'Krasis'),
        (JFroesCrawler, 'JFróes'),
        (FocoCrawler, 'Foco'),
        # (BaseGestaoCrawler, 'Base Gestão'),
        (ContinuaCrawler, 'Contínua'),
        # Imobiliárias da região (Barbacena, Barroso, etc.)
        (ResendeCrawler, 'Resende'),
        (MendoncaCrawler, 'Mendonça'),
        # (LongattiCrawler, 'Longatti'), # Desativado temporariamente devido a instabilidade no site oficial
    ]

    print(f"--- Iniciando Captura Concorrente de {len(tasks)} Imobiliárias ---")
    print(f"Arquivos individuais serão gerados em: '{OUTPUT_DIR}/'\n")

    resumos = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(executar_crawler, cls, name, OUTPUT_DIR) for cls, name in tasks]
        
        for future in as_completed(futures):
            resumo = future.result()
            resumos.append(resumo)

    total_time = time.time() - start_global
    total_imoveis = sum(r["total"] for r in resumos)

    print("\n" + "=" * 70)
    print("RESUMO DA EXECUÇÃO")
    print("=" * 70)
    for r in sorted(resumos, key=lambda x: x["source"]):
        status = "OK" if r["sucesso"] else "FALHA"
        arquivo = r["arquivo"] or "Nenhum"
        print(f"[{status}] {r['source']:<22} | {r['total']:>5} imóveis | {r['tempo']:>6.2f}s | {arquivo}")
    print("=" * 70)
    print(f"Total geral capturado: {total_imoveis} imóveis em {total_time:.2f}s")
    print(f"Todos os arquivos individuais foram salvos no diretório '{OUTPUT_DIR}/'.")
    print("Utilize 'python loader_mongo.py' para selecionar quais arquivos enviar ao MongoDB.")

if __name__ == "__main__":
    main()