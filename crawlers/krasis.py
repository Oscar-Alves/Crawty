from crawlers.base_homeclix import BaseHomeclixCrawler

class KrasisCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=10,
            imobiliaria_nome="Imobiliária Krasis",
            prefixo_id="Krasis",
            site_url="https://imobiliariakrasis.com.br"
        )

if __name__ == "__main__":
    crawler = KrasisCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Krasis: {len(res)}")
        print(res[0])
