import json
from crawlers.longatti import LongattiCrawler
from crawlers.domicilium import DomiciliumCrawler

def salvar_dados(nome_arquivo, dados):
    """Função auxiliar para salvar os dados em JSON"""
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f"Dados salvos com sucesso em '{nome_arquivo}'")
    except IOError as e:
        print(f"Erro ao salvar arquivo: {e}")

def main():
    print("--- INICIANDO SISTEMA CRAWLER IMOBILIÁRIO ---")
    
    # Lista para acumular todos os dados de todas as imobiliárias
    banco_de_dados_temporario = []

    # # --- IMOBILIÁRIA 1: LONGATTI ---
    print("\n> Iniciando Crawler: Longatti Imóveis")
    crawler_longatti = LongattiCrawler()
    imoveis_longatti = crawler_longatti.buscar_imoveis()

    for imovel in imoveis_longatti:
        imovel['crawler_source'] = 'Longatti'
        
    banco_de_dados_temporario.extend(imoveis_longatti)
    print(f"> Finalizado Longatti. Imóveis capturados: {len(imoveis_longatti)}")

    # --- IMOBILIÁRIA 2: Domicilium ---
    print("\n> Iniciando Crawler: Domicilium Imóveis")
    crawler_domicilium = DomiciliumCrawler()
    imoveis_domicilium = crawler_domicilium.buscar_imoveis()
    
    for imovel in imoveis_domicilium:
        imovel['crawler_source'] = 'Domicilium'
        
    banco_de_dados_temporario.extend(imoveis_domicilium)
    print(f"> Finalizado Domicilium. Imóveis capturados: {len(imoveis_domicilium)}")

    # --- FUTURAS IMOBILIÁRIAS ---
    # Aqui você chamaria crawler_outra = OutraImobiliaria()...

    # --- FINALIZAÇÃO ---
    print(f"\nTotal geral de imóveis capturados: {len(banco_de_dados_temporario)}")
    
    # Salvar em um JSON único para análise (ou futuramente enviar pro BD)
    salvar_dados('imoveis_consolidados.json', banco_de_dados_temporario)

if __name__ == "__main__":
    main()