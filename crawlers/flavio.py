from crawlers.base_homeclix import BaseHomeclixCrawler

class FlavioCrawler(BaseHomeclixCrawler):
    def __init__(self):
        super().__init__(
            tenant_id=13,
            imobiliaria_nome="Flávio Vitor",
            prefixo_id="Flavio",
            site_url="https://flaviovitorimoveis.com.br"
        )

if __name__ == "__main__":
    crawler = FlavioCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Flavio: {len(res)}")
        print(res[0])