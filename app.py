from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import psycopg2
from copy import deepcopy
import os
from dotenv import load_dotenv
import re

# load_dotenv(): Carga las variables de entorno desde un archivo .env. En este caso, se asegura de que las variables se carguen desde el archivo especificado.
assert load_dotenv(f"{os.getcwd()}/medifacil_backend/.env", override=True)

app = Flask(__name__)
CORS(app)  # Esto habilita CORS para todas las rutas


# Configuración de la conexión a la base de datos PostgreSQL
hostname = os.environ["DB_HOSTNAME"]
username = os.environ["DB_USERNAME"]  # El usuario con el que te conectas
password = os.environ["DB_PASSWORD"]  # La contraseña del usuario
database = os.environ["DB_DATABASE"]  # La base de datos a la que te conectas
port = os.environ["DB_PORT"]  # Puerto de PostgreSQL (el valor por defecto es 5432)

def get_db_connection():
    """
    Establece una conexión a la base de datos PostgreSQL.

    Returns:
        conn (psycopg2.extensions.connection): Objeto de conexión a la base de datos.
    """
    conn = psycopg2.connect(
        host=hostname,
        user=username,
        password=password,
        dbname=database,
        port=port
    )
    return conn

@app.route('/search', methods=['GET'])
def search_medicine():
    """
    Ruta de la API para buscar medicamentos en la base de datos.

    Returns:
        json: Información sobre los medicamentos encontrados o un error.
    """

    token = request.args.get('token')
    if token != os.environ["SECRET_TOKEN"]:
        return jsonify({"error": "Unauthorized access"}), 401
    
    # Obtiene los nombres de los medicamentos desde los parámetros de la solicitud
    medicine_names = request.args.get('name').split(",")

    if not medicine_names:
        return jsonify({'error': 'No medicine name provided'}), 400

    if not isinstance(medicine_names, list):
        medicine_names = [medicine_names]

    # Esta instrucción SQL realiza una consulta para seleccionar medicamentos de la tabla public.medicines.
    # En alto nivel lo que hace es buscar por CADA farmacia CADA producto (son multiples consultas). Y elije
    # el producto que mejor match de TEXTO haga


    # Utiliza técnicas avanzadas de SQL como DISTINCT ON, subconsultas, funciones de texto completo (to_tsvector, to_tsquery), y 
    # la función de ventana ROW_NUMBER() para organizar y filtrar los resultados.
    # SELECT DISTINCT ON (pharma): Selecciona filas únicas basadas en la columna pharma. Para cada pharma, devuelve solo la primera fila encontrada en el orden especificado.
    #   FROM ( ... ) subquery: Utiliza una subconsulta para generar un conjunto de resultados intermedio que se referirá como subquery. La subconsulta contiene la lógica principal para calcular las filas y asignar números de fila.
    # ROW_NUMBER() OVER ( ... ) as rn:
    #   ROW_NUMBER(): Función de ventana que asigna un número único a cada fila en el conjunto de resultados.
    #   OVER ( ... ): Define la partición y el orden de las filas. PARTITION BY pharma: Divide las filas en particiones por el valor de pharma. 
    #      ORDER BY ts_rank_cd(to_tsvector('spanish', name), query) DESC: Ordena las filas dentro de cada partición según la relevancia calculada por ts_rank_cd. ts_rank_cd evalúa la similitud de to_tsvector('spanish', name) con query y devuelve un valor de relevancia en orden descendente (de más relevante a menos relevante).
    # as rn: Asigna el resultado de ROW_NUMBER() a la columna rn.


    query = """
    SELECT DISTINCT ON (pharma) pharma, name, price, url, url_image, availability, rn
    FROM (
        SELECT
            pharma, name, price, url, url_image, availability,
            ROW_NUMBER() OVER (
                PARTITION BY pharma ORDER BY ts_rank_cd(to_tsvector('spanish', name), query) DESC
            ) as rn 
        FROM public.medicines, to_tsquery('spanish', %s) query
        WHERE to_tsvector('spanish', name) @@ query
    ) subquery
    WHERE rn = 1;
    """

    try:
        medicines = []
        for medicine_name in medicine_names:
            # Convierte el nombre del medicamento en un formato adecuado para la consulta
            medicine_name_or = "|".join(medicine_name.split())

            # Establece una conexión con la base de datos y ejecuta la consulta
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(query, (medicine_name_or, ))
            results = cur.fetchall()
            cur.close()
            conn.close()

            # Almacena los resultados en la lista de medicamentos
            medicines.append([
                {
                    'pharma': row[0],
                    'name': row[1],
                    'price': row[2],
                    'url': row[3],
                    'url_image': row[4],
                    'availability': row[5]
                }
                for row in results
            ])

        pharmas = []
        pharmas_map_index = dict()
        index = 0

        products_default = []
                    
        for medicine_name in medicine_names:
            products_default.append({
                "name": medicine_name,
                "price": None,
                "found": False,
                "link": None,
            })

        for i, medicine_group in enumerate(medicines):
            
            for medicine in medicine_group:
                pharma = medicine['pharma']

                if pharma not in pharmas_map_index:
                    pharmas_map_index[pharma] = index
                    index += 1

                    # Obtiene información adicional sobre la farmacia desde la base de datos
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute(
                        """SELECT pharma, location, link_logo, link
                        FROM public.pharmas
                        WHERE pharma = %s
                        """,
                        (pharma, )
                    )
                    results_pharma = cur.fetchone()
                    cur.close()
                    conn.close()

                    # Agrega la farmacia a la lista de farmacias
                    pharmas.append({
                        "name": pharma,
                        "location": results_pharma[1],
                        "link_logo": results_pharma[2],
                        "link": results_pharma[3],
                        "products": deepcopy(products_default)
                    })

                index_pharma = pharmas_map_index[pharma]

                def parse_medication_prices(medications):
                    """
                    Analiza y ajusta los precios de los medicamentos en función de la cantidad.

                    Args:
                        medications (list): Lista de medicamentos y sus precios.

                    Returns:
                        list: Lista de medicamentos con precios ajustados por unidad.
                    """
                    parsed_medications = []
                    pattern = re.compile(r'(.+?)(?:\s*x(\d+)|\s*(\d+)\s*(?:unidad?e?s?))(.+)', re.IGNORECASE)

                    for med_name, price in medications:
                        match = pattern.search(med_name)
                        if match:
                            base_name = match.group(1).strip()
                            if 'unidad' in med_name.lower():
                                quantity = int(match.group(3))
                            else:
                                quantity = int(match.group(2))

                            if match.group(4):
                                base_name = f"{base_name} unidad {match.groups()[-1]}".strip()
                            else:
                                base_name = f"{base_name} x1 {match.groups()[-1]}".strip()

                            unit_price = price / quantity
                            parsed_medications.append((base_name, unit_price))
                        else:
                            parsed_medications.append((med_name, price))

                    return parsed_medications

                # Analiza y ajusta el precio del medicamento actual. Reemplazando los que tienen 'x 100' o 'n unidades' para tratar de obtener su precio unitario
                name_price_parsed = parse_medication_prices([[medicine["name"], float(medicine["price"])]])[0]
                name, price = name_price_parsed[0], name_price_parsed[1]

                # Actualiza la lista de productos de la farmacia con el medicamento encontrado
                pharmas[index_pharma]['products'][i] = {
                    "name": name,
                    "price": price,
                    "found": True,
                    "link": medicine["url"],
                }

        return jsonify(pharmas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scraper', methods=['POST'])
def run_spiders():
    """
    Ruta de la API para ejecutar spiders de scraping.

    La ruta espera una solicitud POST con un JSON que contiene una lista de nombres de spiders
    a ejecutar. Ejecuta un script externo que corre los spiders y devuelve la salida.

    Returns:
        json: Resultado de la ejecución del script incluyendo stdout, stderr y el código de retorno.
    """
    
    # Obtiene los datos JSON de la solicitud
    data = request.json
    # Obtiene la lista de nombres de spiders desde los datos JSON
    spider_names = data.get('spiders', [])

    token = data.get('token', None)
    if token != os.environ["SECRET_TOKEN"]:
        return jsonify({"error": "Unauthorized access"}), 401
    
    if not spider_names:
        # Devuelve un error si no se proporcionaron nombres de spiders
        return jsonify({'error': 'No spider names provided'}), 400

    try:
        # Convierte la lista de nombres de spiders a una cadena de argumentos para el script
        args = ['python', 'app_scraper.py'] + spider_names
        # Ejecuta el script en un nuevo proceso
        result = subprocess.run(args, capture_output=True, text=True)
        print(args, result)

        # Devuelve la salida del script, incluyendo stdout, stderr y el código de retorno
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
    except Exception as e:
        # Captura cualquier excepción y devuelve un mensaje de error
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
