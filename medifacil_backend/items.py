import scrapy
import re
from itemloaders.processors import MapCompose

def transform_price(text):
    """
    Transforma el texto del precio en un valor float limpio.

    Args:
        text (str): El texto del precio a transformar.

    Returns:
        float: El precio transformado en float, o None si hay un error.
    """
    # Limpia el texto eliminando caracteres no numéricos, excepto puntos
    text_clean = re.sub(r'[^\d\.]', '', text.replace(",", "."))

    price = None
    try:
        # Intenta convertir el texto limpio a un valor float
        price = float(text_clean)
    except Exception as error:
        # Manejo de excepciones y registro del error
        print(f"Error al transformar precio: {error}")
    return price

class MedicineItem(scrapy.Item):
    """
    Define el esquema de un ítem de medicina para Scrapy.

    Atributos:
        url (scrapy.Field): URL de la página del producto.
        pharma (scrapy.Field): Nombre de la farmacia.
        name (scrapy.Field): Nombre del medicamento.
        price (scrapy.Field): Precio del medicamento, procesado con una función personalizada.
        url_image (scrapy.Field): URL de la imagen del producto.
        availability (scrapy.Field): Disponibilidad del producto.
        ingest_date (scrapy.Field): Fecha de ingesta de los datos.
    """
    url = scrapy.Field()
    pharma = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field(
        input_processor=MapCompose(
            transform_price
        )
    )
    url_image = scrapy.Field()
    availability = scrapy.Field()
    ingest_date = scrapy.Field()

    def __str__(self):
        return ""
