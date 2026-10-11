from crawlers.base_homeclix import BaseHomeclixCrawler

class BaseGestaoCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=14,
            imobiliaria_nome="Base Gestão Imobiliária",
            prefixo_id="BaseGestao",
            site_url="https://www.basegestaoimobiliaria.com.br"
        )

if __name__ == "__main__":
    crawler = BaseGestaoCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Base Gestão: {len(res)}")
        print(res[0])
