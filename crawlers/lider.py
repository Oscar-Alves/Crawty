from crawlers.base_homeclix import BaseHomeclixCrawler

class LiderCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=7,
            imobiliaria_nome="Imobiliária Líder",
            prefixo_id="Lider",
            site_url="https://www.imobiliarialider.imb.br"
        )

if __name__ == "__main__":
    crawler = LiderCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Líder: {len(res)}")
        print(res[0])
