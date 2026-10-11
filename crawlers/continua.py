from crawlers.base_homeclix import BaseHomeclixCrawler

class ContinuaCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=19,
            imobiliaria_nome="Contínua Imóveis",
            prefixo_id="Continua",
            site_url=""
        )

if __name__ == "__main__":
    crawler = ContinuaCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Contínua: {len(res)}")
        print(res[0])
