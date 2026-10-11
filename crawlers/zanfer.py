from crawlers.base_homeclix import BaseHomeclixCrawler

class ZanferCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=8,
            imobiliaria_nome="Zanfer",
            prefixo_id="Zanfer",
            site_url="https://www.zanferimoveis.com.br"
        )

if __name__ == "__main__":
    crawler = ZanferCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Zanfer: {len(res)}")
        print(res[0])