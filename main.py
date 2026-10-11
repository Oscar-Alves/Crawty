import json
import logging
import time
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

# Configuração de Log para mostrar threads
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s')

def salvar_dados(nome_arquivo, dados):
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f"Dados salvos com sucesso em '{nome_arquivo}'")
    except IOError as e:
        print(f"Erro ao salvar arquivo: {e}")

def executar_crawler(crawler_class, source_name):
    """
    Função wrapper para instanciar e rodar um crawler específico.
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
        return imoveis
    except Exception as e:
        print(f"ERRO CRÍTICO no crawler {source_name}: {e}")
        return []

def main():
    start_global = time.time()
    banco_de_dados_temporario = []

    # Lista de crawlers para rodar
    tasks = [
        # Imobiliárias de São João del Rei
        (ZanferCrawler, 'Zanfer'),
        (ChavesCrawler, 'Chaves'),
        (FlavioCrawler, 'Flavio Vitor'),
        (DomiciliumCrawler, 'Domicilium'),
        (LiderCrawler, 'Líder'),
        (KrasisCrawler, 'Krasis'),
        (JFroesCrawler, 'JFróes'),
        (FocoCrawler, 'Foco'),
        (BaseGestaoCrawler, 'Base Gestão'),
        (ContinuaCrawler, 'Contínua'),
        # Imobiliárias da região (Barbacena, Barroso, etc.)
        (ResendeCrawler, 'Resende'),
        (MendoncaCrawler, 'Mendonça'),
        # (LongattiCrawler, 'Longatti'), # Desativado temporariamente devido a instabilidade no site da imobiliária
    ]

    print(f"--- Iniciando Captura Concorrente de {len(tasks)} Imobiliárias ---")

    with ThreadPoolExecutor(max_workers=6) as executor:
        # Submete todas as tarefas
        futures = [executor.submit(executar_crawler, cls, name) for cls, name in tasks]
        
        # Coleta os resultados conforme eles ficam prontos
        for future in as_completed(futures):
            resultado = future.result()
            if resultado:
                banco_de_dados_temporario.extend(resultado)

    total_time = time.time() - start_global
    print(f"\nTotal geral de imóveis capturados: {len(banco_de_dados_temporario)}")
    print(f"Tempo total de execução: {total_time:.2f}s")
    
    salvar_dados('imoveis_consolidados.json', banco_de_dados_temporario)

if __name__ == "__main__":
    main()