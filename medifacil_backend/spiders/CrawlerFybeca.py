import scrapy
import json
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
import logging


from medifacil_backend.items import MedicineItem


# URL base para la farmacia Fybeca
base_url_minimal = "https://www.fybeca.com"


class CrawlFybeca(CrawlSpider):
    """
    Spider que rastrea y extrae información de productos de la farmacia Fybeca.
    Utiliza reglas para seguir enlaces y procesar páginas específicas de productos.
    """

    name = "crawl_fybeca"  # Nombre de la araña

    base_url = f"{base_url_minimal}"


    urls = [
        f"{base_url}"
    ]


    allowed_domains = [
        base_url_minimal.split("//")[-1]  # Dominio permitido para el rastreo
    ]

    # Reglas para seguir enlaces y llamar a callbacks específicos
    rules = (

        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow=(
                    r"^https?:\/\/www\.fybeca\.com\/[a-zA-Z0-9\-.]+$"
                )
            ),
            callback='parse_page'  # Llama a parse_page para las URLs que coinciden
        ),

        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow=(
                    r"^https://www\.fybeca\.com/[a-zA-Z0-9\-.]+/[A-Z]+_[0-9]+\.html$"
                )
            ),
            callback='parse_item'  # Llama a parse_item para las URLs que coinciden
        ),

    )


    def __init__(self, *a, **kw):
        """
        Inicializa la araña y llama al constructor de la clase base.
        """
        super(CrawlFybeca, self).__init__(*a, **kw)


    def start_requests(self):
        """
        Inicia las solicitudes a las URLs especificadas en self.urls.
        """
        for url in self.urls:
            yield scrapy.Request(url, callback=self.parse_page)


    def parse_page(self, response):
        """
        Procesa una página de la lista de productos, siguiendo enlaces a productos individuales.

        Args:
            response (scrapy.http.Response): La respuesta de la solicitud.
        """

        for u in response.css("a::attr(href)").getall():
            u = u.lower()

            if u.startswith("http"):
                yield response.follow(u)
            elif u.startswith("/"):
                yield response.follow(f"{base_url_minimal}{u}")


    def parse_item(self, response):
        """
        Procesa una página de producto individual, extrayendo la información relevante.

        Args:
            response (scrapy.http.Response): La respuesta de la solicitud.
        """

        url = response.request.url

        item_loader = ItemLoader(item=MedicineItem(), selector=response)
        item_loader.default_output_processor = TakeFirst()

        try:
            # Extrae datos del producto utilizando JSON-LD y selectores CSS/XPath
            product_data = response.xpath('//script[@type="application/ld+json"]/text()').get()
            product_json = json.loads(product_data) if product_data else {}
            name = product_json.get('name') or response.xpath('//h1/text()').get()
            price = product_json.get('offers', {}).get('price') or response.css('.price .value::attr(content)').get()  # first option

            url_image = (product_json.get('image', [])[0] if product_json.get('image') else response.css('img.product-image::attr(src)').get())

            availability = product_json.get('offers', {}).get('availability') or response.css('.availability::text').get()

            if url_image is None:
                url_image = ''

            if availability is None:
                availability = ''

            data = {
                'url': url,
                'pharma': 'Fybeca',
                'name': name,
                'price': price,
                'url_image': str(url_image),
                'availability': availability,
                'ingest_date': str(datetime.now().date())
            }

            for key, value in data.items():
                item_loader.add_value(key, value)

            item = item_loader.load_item()
            yield item

        except Exception as error:
            logging.error(f"Error parsing item: {error}")
            pass
