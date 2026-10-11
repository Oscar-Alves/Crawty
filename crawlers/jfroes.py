from crawlers.base_homeclix import BaseHomeclixCrawler

class JFroesCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=9,
            imobiliaria_nome="JFróes Imóveis",
            prefixo_id="JFroes",
            site_url="https://www.jfroesimoveis.com.br"
        )

if __name__ == "__main__":
    crawler = JFroesCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total JFróes: {len(res)}")
        print(res[0])
