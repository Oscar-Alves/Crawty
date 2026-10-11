from crawlers.base_homeclix import BaseHomeclixCrawler

class ResendeCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=16,
            imobiliaria_nome="Imobiliária Resende",
            prefixo_id="Resende",
            site_url="https://imobiliariaresende.imb.br"
        )

if __name__ == "__main__":
    crawler = ResendeCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Resende: {len(res)}")
        print(res[0])
