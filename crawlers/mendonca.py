from crawlers.base_homeclix import BaseHomeclixCrawler

class MendoncaCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=20,
            imobiliaria_nome="Mendonça Imobiliária",
            prefixo_id="Mendonca",
            site_url=""
        )

if __name__ == "__main__":
    crawler = MendoncaCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Mendonça: {len(res)}")
        print(res[0])
