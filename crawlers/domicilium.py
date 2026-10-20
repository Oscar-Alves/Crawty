from crawlers.base_homeclix import BaseHomeclixCrawler


class DomiciliumCrawler(BaseHomeclixCrawler):
    """
    Crawler para Domicilium Imóveis.
    O site migrou para a plataforma Homeclix (tenant 49) com frontend Next.js.
    """

    def __init__(self):
        super().__init__(
            tenant_id=49,
            imobiliaria_nome="Domicilium",
            prefixo_id="Domicilium",
            site_url="https://www.domiciliumimoveis.com.br"
        )


if __name__ == "__main__":
    crawler = DomiciliumCrawler()
    res = crawler.buscar_imoveis()
    if res:
        print(f"Total Domicilium: {len(res)}")
        print(res[0])
