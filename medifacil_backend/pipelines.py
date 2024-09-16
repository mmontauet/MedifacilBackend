# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
assert load_dotenv(f"{os.getcwd()}/medifacil_backend/.env", override=True)


class PostgresPipeline:
    """
    Pipeline para guardar items en una base de datos PostgreSQL.

    Este pipeline se conecta a una base de datos PostgreSQL cuando se abre el spider
    y cierra la conexión cuando el spider se cierra. Procesa cada item insertándolo
    o actualizándolo en la base de datos.
    """

    def open_spider(self, spider):
        """
        Se llama cuando el spider se abre. Establece una conexión con la base de datos.

        Args:
            spider (scrapy.Spider): El spider que se está abriendo.
        """
        hostname = os.environ["DB_HOSTNAME"]
        username = os.environ["DB_USERNAME"]  # El usuario con el que te conectas
        password = os.environ["DB_PASSWORD"]  # La contraseña del usuario
        database = os.environ["DB_DATABASE"]  # La base de datos a la que te conectas
        port = os.environ["DB_PORT"]  # Puerto de PostgreSQL (el valor por defecto es 5432)

        try:
            # Establece la conexión con la base de datos
            self.connection = psycopg2.connect(
                host=hostname,
                user=username,
                password=password,
                dbname=database,
                port=port
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logging.info("Connected to the database successfully")
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")

    def close_spider(self, spider):
        """
        Se llama cuando el spider se cierra. Cierra la conexión con la base de datos.

        Args:
            spider (scrapy.Spider): El spider que se está cerrando.
        """
        self.cursor.close()
        self.connection.close()
        logging.info("Database connection closed")

    def process_item(self, item, spider):
        """
        Procesa cada item insertándolo o actualizándolo en la base de datos.

        Args:
            item (scrapy.Item): El item a procesar.
            spider (scrapy.Spider): El spider que está procesando el item.

        Returns:
            scrapy.Item: El item procesado.
        """
        try:
            # Inserta o actualiza el item en la base de datos: La instrucción SQL utiliza la cláusula INSERT INTO para insertar datos en una tabla llamada medicines.
            # Además, emplea la cláusula ON CONFLICT para manejar situaciones en las que se produce un conflicto (en este caso, una duplicación en la columna url). 
            # Si ocurre un conflicto, la instrucción no insertará un nuevo registro, 
            # sino que actualizará los campos específicos del registro existente con los nuevos valores proporcionados.
            # %s: Marcador de posición para cada uno de los valores que se insertarán en las columnas para evitar SQL INJECTION

            self.cursor.execute(
                """
                INSERT INTO medicines (url, pharma, name, price, url_image, availability, ingest_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) 
                DO UPDATE SET
                    name = EXCLUDED.name,
                    price = EXCLUDED.price,
                    url_image = EXCLUDED.url_image,
                    availability = EXCLUDED.availability,
                    ingest_date = EXCLUDED.ingest_date
                """,
                (
                    item['url'],
                    item['pharma'],
                    item['name'],
                    item['price'],
                    item.get('url_image', ''),
                    item['availability'],
                    item['ingest_date']
                )
            )
            self.connection.commit()
            # logging.info("Item inserted/updated successfully")
        except Exception as e:
            logging.error(f"Error processing item: {e} {str(item)}")
        return item