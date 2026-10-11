from crawlers.base_homeclix import BaseHomeclixCrawler

class ChavesCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=11,
            imobiliaria_nome="Chaves Corretora",
            prefixo_id="Chaves",
            site_url="https://chavescorretora.com.br"
        )

if __name__ == "__main__":
    crawler = ChavesCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Chaves: {len(res)}")
        print(res[0])