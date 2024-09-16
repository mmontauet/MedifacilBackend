# Scrapy settings for medifacil_backend project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "medifacil_backend"

SPIDER_MODULES = ["medifacil_backend.spiders"]
NEWSPIDER_MODULE = "medifacil_backend.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "medifacil_backend (+http://www.yourdomain.com)"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS = 4

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY = 0  # Retraso mínimo de 1 segundo
DOWNLOAD_DELAY_MAX = 2  # Retraso máximo de 3 segundos

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 4
CONCURRENT_REQUESTS_PER_IP = 4

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "medifacil_backend.middlewares.MedifacilBackendSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "medifacil_backend.middlewares.MedifacilBackendDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "medifacil_backend.pipelines.MedifacilBackendPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value

# Versión de la implementación de Request Fingerprinter a utilizar.
# "2.7" indica que se está utilizando la implementación más reciente compatible con Scrapy 2.7.
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

# Configuración del reactor Twisted para usar con asyncio.
# "twisted.internet.asyncioreactor.AsyncioSelectorReactor" permite que Scrapy funcione con el loop de eventos asyncio.
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Codificación a utilizar al exportar feeds (archivos de salida).
# "utf-8" asegura que los datos exportados se codifiquen en formato UTF-8, compatible con la mayoría de los sistemas y aplicaciones.
FEED_EXPORT_ENCODING = "utf-8"

# Definición de los pipelines de items a utilizar en el proyecto.
# 'medifacil_backend.pipelines.PostgresPipeline' es la ruta al pipeline personalizado que se utilizará.
# El valor '300' es la prioridad del pipeline (menor valor significa mayor prioridad).
ITEM_PIPELINES = {
    'medifacil_backend.pipelines.PostgresPipeline': 300,
}

LOG_LEVEL = 'DEBUG'