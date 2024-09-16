import scrapy
import json
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
import logging


from medifacil_backend.items import MedicineItem


# URL base para la farmacia Medicity
base_url_minimal = "https://www.farmaciasmedicity.com"


class CrawlMedicity(CrawlSpider):
    """
    Spider que rastrea y extrae información de productos de la farmacia Medicity.
    Utiliza reglas para seguir enlaces y procesar páginas específicas de productos.
    """

    name = "crawl_medicity"  # Nombre de la araña

    base_url = f"{base_url_minimal}/medicina"

    urls = [f"{base_url_minimal}/medicina?page={i}" for i in range(1, 50)] + [base_url_minimal]


    allowed_domains = [
        base_url_minimal.split("//")[-1]  # Dominio permitido para el rastreo
    ]

    # Reglas para seguir enlaces y llamar a callbacks específicos
    rules = (

        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow=(
                    r"^https://w?w?w?\.?farmaciasmedicity\.com/[a-zA-Z0-9\-.]+/p$"
                )
            ),
            callback='parse_item'  # Llama a parse_item para las URLs que coinciden
        ),
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow=(
                    r"^https?:\/\/w?w?w?\.?farmaciasmedicity\.com\/[a-zA-Z0-9\-.]+$"
                )
            ),
            callback='parse_page'  # Llama a parse_page para las URLs que coinciden
        ),

    )


    def __init__(self, *a, **kw):
        """
        Inicializa la araña y llama al constructor de la clase base.
        """
        super(CrawlMedicity, self).__init__(*a, **kw)


    def start_requests(self):
        """
        Inicia las solicitudes a las URLs especificadas en self.urls.
        """

        extra_urls = [
            '/especialidad',
            '/medicina?order=',
            '/dermocosmetica?order=',
            'cuidado-infantil-y-mama?order=',
            '/bienestar-y-nutricion/vitaminas-adultos?order=',
            '/belleza?order=',
            '/cuidado-personal?order=',
            '/cuidado-infantil-y-mama?order=OrderByBestDiscountDESC',
            '/bienestar-y-nutricion?order=OrderByBestDiscountDESC',
            '/dermocosmetica?order=OrderByBestDiscountDESC',
            '/medicina?order=OrderByBestDiscountDESC',
            '/139?map=productClusterIds&order=OrderByBestDiscountDESC',
            '/especialidad',
            '/piel%20grasa?_q=piel%20grasa&map=ft',
            '/antiedad?_q=antiedad&map=ft',
            '/pigmentos?_q=pigmentos&map=ft',
            '/eucerin?_q=eucerin&map=ft',
            '/la%20roche?_q=la%20roche&map=ft',
            '/bioderma?_q=bioderma&map=ft',
            '/redoxon?_q=redoxon&map=ft',
            '/pediasure?_q=pediasure&map=ft'
        ]

        for url in self.urls:
            yield scrapy.Request(url, callback=self.parse_page)

        for extra_url in extra_urls:
            base_url = f"{base_url_minimal}/{extra_url}"
            # print(base_url)
            urls_augmentation = [f"{base_url}&page={i}" for i in range(1, 50)] + [base_url]

            for url_augmented in urls_augmentation:
                yield scrapy.Request(url_augmented, callback=self.parse_page)


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
            # Extrae la información del producto utilizando selectores CSS
            
            name = response.css('div.vtex-flex-layout-0-x-flexCol--right-col h1.vtex-store-components-3-x-productNameContainer span.vtex-store-components-3-x-productBrand::text').get()

            currency_code = response.css('span.vtex-product-price-1-x-currencyCode::text').get()
            currency_integer = response.css('span.vtex-product-price-1-x-currencyInteger::text').get()
            currency_decimal = response.css('span.vtex-product-price-1-x-currencyDecimal::text').get()
            currency_fraction = response.css('span.vtex-product-price-1-x-currencyFraction::text').get()

            # Combina las partes del precio en una sola cadena
            price = f"{currency_integer}{currency_decimal}{currency_fraction}"

            url_image = response.css('img.vtex-store-components-3-x-imageElement::attr(src)').get()
            availability = response.css('div.vtex-product-availability-0-x-container span.vtex-product-availability-0-x-highStockText::text').get()


            if url_image is None:
                url_image = ''

            if availability is None:
                availability = ''

            data = {
                'url': url,
                'pharma': 'Medicity',
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
            logging.error(f"Error parsing item: {error}. URL: {url}")
            pass
