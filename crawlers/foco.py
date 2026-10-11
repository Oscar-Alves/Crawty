from crawlers.base_homeclix import BaseHomeclixCrawler

class FocoCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=3,
            imobiliaria_nome="Foco Imóveis",
            prefixo_id="Foco",
            site_url="https://www.focoimoveissjdr.com.br"
        )

if __name__ == "__main__":
    crawler = FocoCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Foco: {len(res)}")
        print(res[0])
