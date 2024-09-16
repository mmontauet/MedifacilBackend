import asyncio
import logging
from twisted.internet import asyncioreactor
import os
import sys
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from medifacil_backend.spiders.CrawlerFybeca import CrawlFybeca
from medifacil_backend.spiders.CrawlerMedicity import CrawlMedicity
from medifacil_backend.spiders.CrawlerCruzAzul import CrawlCruzAzul
import threading
import argparse

# python app_scraper.py CrawlFybeca CrawlMedicity CrawlCruzAzul

# Configura el bucle de eventos a SelectorEventLoop antes de instalar el reactor
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncioreactor.install()

# Inicializa el proceso del crawler con la configuración del proyecto
settings = get_project_settings()
settings.set('LOG_LEVEL', 'WARNING')  # Ajusta el nivel de logging a WARNING

# Configura el nivel de logging
logging.getLogger('scrapy').setLevel(logging.WARNING)

# Diccionario de spiders disponibles
SPIDERS = {
    'CrawlFybeca': CrawlFybeca,
    'CrawlMedicity': CrawlMedicity,
    'CrawlCruzAzul': CrawlCruzAzul,
    # Añade otros spiders aquí
    # 'OtroSpider': OtroSpider
}

def run_spiders_in_thread(spider_names):
    """
    Ejecuta las spiders especificadas en un hilo separado.

    Args:
        spider_names (list): Lista de nombres de spiders a ejecutar.
    """
    process = CrawlerProcess(settings)

    def handle_spider_opened(spider):
        """
        Maneja la señal de apertura de una spider.

        Args:
            spider (Spider): La spider que se ha abierto.
        """
        print(f"Spider {spider.name} is started.")

    def handle_item_scraped(item):
        """
        Maneja la señal de item raspado.

        Args:
            item (dict): El item que se ha raspado.
        """
        pass

    def handle_spider_closed(spider):
        """
        Maneja la señal de cierre de una spider.

        Args:
            spider (Spider): La spider que se ha cerrado.
        """
        print(f"Spider {spider.name} is closed.")

    for spider_name in spider_names:
        if spider_name in SPIDERS:
            # Crea un crawler para la spider especificada
            crawler = process.create_crawler(SPIDERS[spider_name])
            # Conecta las señales a los manejadores correspondientes
            crawler.signals.connect(handle_spider_opened, signal=signals.spider_opened)
            crawler.signals.connect(handle_item_scraped, signal=signals.item_scraped)
            crawler.signals.connect(handle_spider_closed, signal=signals.spider_closed)
            # Inicia el proceso de rastreo
            process.crawl(crawler, tag=spider_name)
        else:
            print(f"Spider {spider_name} not found")

    process.start(install_signal_handlers=False, stop_after_crawl=True)

# Configuración del parser de argumentos para recibir nombres de spiders desde la línea de comandos
parser = argparse.ArgumentParser(description="Run Scrapy spiders.")
parser.add_argument(
    'spider_names',
    metavar='N',
    type=str,
    nargs='+',
    help='Names of the spiders to run'
)

# Parseo de los argumentos proporcionados
args = parser.parse_args()
spider_names = args.spider_names

# Agrega el directorio actual al path de búsqueda de módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Crea y comienza un hilo para ejecutar las spiders
spider_thread = threading.Thread(target=run_spiders_in_thread, args=(spider_names,))
spider_thread.start()
