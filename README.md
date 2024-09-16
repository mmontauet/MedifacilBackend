# Medifacil Backend

Medifacil Backend es una aplicación diseñada para rastrear y extraer información de medicamentos de diferentes farmacias en línea y proporcionar una API para buscar estos medicamentos en una base de datos centralizada. La aplicación utiliza el framework Flask para exponer endpoints de API y Scrapy para realizar el scraping de datos de las farmacias.

## Estructura del Proyecto

```markdown
medifacil_backend/
├── __init__.py
├── items.py
├── middlewares.py
├── pipelines.py
├── settings.py
├── spiders/
│   ├── __init__.py
│   ├── CrawlerCruzAzul.py
│   ├── CrawlerFybeca.py
│   ├── CrawlerMedicity.py
├── __pycache__/
├── temp/
├── .env
├── .env.example
├── .gitignore
├── app.py
├── app_scraper.py
├── dev.ipynb
├── gunicorn_config.py
├── README.md
├── requirements.txt
├── run_scraper.bat
├── run_scraper.sh
├── scrapy.cfg
```

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/tu_usuario/MedifacilBackend.git
    cd MedifacilBackend
    ```

2. Crea un entorno virtual e instala las dependencias:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. Configura las variables de entorno:
    - Crea un archivo `.env` basado en el `.env.example` y llena los valores necesarios (credenciales de la base de datos, etc.).

## Uso de forma LOCAL

### Ejecutar el Servidor Flask localmente

Para iniciar el servidor Flask, ejecuta:

```bash
python app.py
```

El servidor estará disponible en `http://127.0.0.1:5000/`.

### Endpoints Disponibles

#### `/search` (GET)

Busca medicamentos en la base de datos.

- **Parámetros de consulta**:
    - `name`: Nombres de los medicamentos separados por comas.

- **Ejemplo de solicitud**:
    ```bash
    curl "http://127.0.0.1:5000/search?name=ibuprofeno,paracetamol"
    ```

- **Ejemplo de respuesta**:
    ```json
    [
        {
            "name": "CruzAzul",
            "location": "Location A",
            "link_logo": "http://example.com/logo.png",
            "link": "http://example.com",
            "products": [
                {
                    "name": "Ibuprofeno",
                    "price": 10.0,
                    "found": true,
                    "link": "http://example.com/ibuprofeno"
                },
                {
                    "name": "Paracetamol",
                    "price": 5.0,
                    "found": true,
                    "link": "http://example.com/paracetamol"
                }
            ]
        }
    ]
    ```

#### `/scraper` (POST)

Ejecuta spiders de scraping.

- **Cuerpo de la solicitud**:
    ```json
    {
        "spiders": ["CrawlFybeca", "CrawlMedicity", "CrawlCruzAzul"],
        "token": "MySecretToken"
    }
    ```

- **Ejemplo de solicitud**:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"spiders": ["CrawlFybeca", "CrawlMedicity", "CrawlCruzAzul"], "token": "MySecretToken"}' http://127.0.0.1:5000/scraper
    ```

- **Ejemplo de respuesta**:
    ```json
    {
        "stdout": "Spider CrawlFybeca is started.\nSpider CrawlFybeca is closed.\n",
        "stderr": "",
        "returncode": 0
    }
    ```

### Ejecutar el Scraper Manualmente

Para ejecutar las spiders manualmente, utiliza el script `app_scraper.py`:

```bash
python app_scraper.py CrawlFybeca CrawlMedicity CrawlCruzAzul
```

## Descripción de los Archivos

### `app.py`

Archivo principal de la aplicación Flask que contiene la lógica del servidor web y los endpoints API.

### `app_scraper.py`

Script para ejecutar múltiples spiders de Scrapy de manera concurrente utilizando `asyncio` y `Twisted`.

### `items.py`

Define las clases de ítems que serán utilizados por las spiders para estructurar los datos extraídos.

### `middlewares.py`

Contiene middleware personalizado para Scrapy.

### `pipelines.py`

Define los pipelines de procesamiento de ítems que procesan los ítems extraídos antes de almacenarlos.

### `settings.py`

Archivo de configuración principal para Scrapy. Contiene todas las configuraciones y ajustes necesarios para el funcionamiento de Scrapy.

### `spiders/`

Contiene las spiders de Scrapy que se utilizan para rastrear y extraer datos de diferentes sitios web de farmacias:
- `CrawlerCruzAzul.py`
- `CrawlerFybeca.py`
- `CrawlerMedicity.py`

### `.env`

Archivo de configuración que contiene variables de entorno sensibles, como credenciales de bases de datos y configuraciones específicas de la aplicación.

### `.env.example`

Archivo de ejemplo que muestra las variables de entorno necesarias para la aplicación sin incluir los valores reales.

### `requirements.txt`

Lista de dependencias y paquetes necesarios para el proyecto. Utilizado por `pip` para instalar las dependencias.

### `run_scraper.sh`

Script para ejecutar el scraper en entorno Unix/Linux. Agregar permisos necesarios chmod +x run_scraper.sh

### `scrapy.cfg`

Archivo de configuración global para Scrapy, define la configuración del proyecto y los ajustes de las spiders.

Claro, aquí tienes la sección de la base de datos para el archivo `README.md`:

## Configuración de la Base de Datos

Para configurar la base de datos PostgreSQL utilizada por esta aplicación, debes crear las tablas necesarias y sus índices. A continuación se proporciona el script SQL para crear las tablas `pharmas` y `medicines`, así como el índice para la columna `name` de la tabla `medicines`.

### Crear Tablas

Ejecuta el siguiente script SQL en tu base de datos PostgreSQL para crear las tablas. Para las farmacias y medicinas que serán recolectadas del scrapping:

```sql
CREATE TABLE IF NOT EXISTS public.pharmas (
    pharma VARCHAR(200) PRIMARY KEY,
    location TEXT,
    link_logo TEXT,
    link TEXT
);

CREATE TABLE IF NOT EXISTS public.medicines (
    id SERIAL PRIMARY KEY,
    pharma VARCHAR(200),
    url TEXT UNIQUE,
    name TEXT,
    price DECIMAL,
    url_image TEXT,
    availability TEXT,
    ingest_date DATE
);
```

### Insertar Datos Iniciales

Inserta algunos datos iniciales en la tabla `pharmas`:

```sql
INSERT INTO public.pharmas(pharma, location, link_logo, link) VALUES
('Fybeca', 'Amazonas y Pereira 1', 'https://www.fybeca.com/on/demandware.static/-/Sites-FybecaEcuador-Library/default/dwf1c417d9/images/header/site-logo.png', 'https://www.fybeca.com/'),
('Medicity', 'Amazonas y Pereira 3', 'https://www.fybeca.com/on/demandware.static/-/Sites-FybecaEcuador-Library/default/dwf1c417d9/images/header/site-logo.png', 'https://www.Medicity.com/'),
('CruzAzul', 'Amazonas y Pereira 3', 'https://www.fybeca.com/on/demandware.static/-/Sites-FybecaEcuador-Library/default/dwf1c417d9/images/header/site-logo.png', 'https://www.farmaciascruzazul.ec/');
```

### Crear Índices

Crea un índice para mejorar el rendimiento de las búsquedas en la columna `name` de la tabla `medicines`:

```sql
CREATE INDEX idx_medicines_name ON public.medicines USING GIN(to_tsvector('spanish', name));
```

Asegúrate de que las tablas y los índices estén configurados correctamente antes de ejecutar la aplicación.

## Despliegue a PRODUCCIÓN en un Entorno Unix (Debian/Ubuntu)

Sigue los pasos a continuación para desplegar la aplicación `MedifacilBackend` en un entorno Linux.

#### Elige un recurso adecuado
Si es en EC2, puede ser una computadora con mínimo 2GB de RAM y discoduro de 20 GB. No se requiere un CPU especial. Menos de 2GB de RAM puede producir que el scrapping no se realice y ocurra 'kills' por parte del sistema operativo

#### Actualizar los Paquetes del Sistema

Actualiza la lista de paquetes disponibles e instala los paquetes esenciales:

```bash
sudo apt update -y
sudo apt install build-essential
sudo apt install python3-dev libffi-dev libssl-dev
sudo apt install git -y 
sudo apt install nginx -y
```

#### Configurar Git

Configura tu nombre de usuario y correo electrónico para Git:

```bash
git config --global user.name "<user>"
git config --global user.email "<email>@gmail.com"
```

#### Clonar el Repositorio

Clona el repositorio de `MedifacilBackend` utilizando tu token personal de acceso:

```bash
git clone https://github.com/tu_usuario/MedifacilBackend.git  # Usar token personal de acceso al repo si te pide contraseña
cd MedifacilBackend
```

#### Instalar Python y Configurar el Entorno Virtual

Instala Python y las herramientas necesarias para crear un entorno virtual:

```bash
sudo apt install python3 python3-pip -y
sudo apt install python3.12-venv
python3 -m venv ~/myenv
source ~/myenv/bin/activate
pip install -r requirements.txt
```

Cada vez que se ingrese a la instancia por terminal es necesario activar el entorno con los requerimientos y dependencias ya instaladas:

```bash
source ~/myenv/bin/activate
```

#### IMPORTANTE
Agregar el archivo .env, basarse en el archivo .env.example para llenar las credenciales. El token secreto debe ser el mismo configurado en el frontend


#### Ejecutar la Aplicación con Gunicorn

Para producción, utiliza Gunicorn para servir la aplicación. No se recomienda usar flask => 'python app.py', sino un WSGI:

```bash
gunicorn -c gunicorn_config.py app:app
```

Para desarrollo, SI puedes ejecutar directamente el archivo `app.py`:

```bash
python app.py
```

#### Desactivar el Entorno Virtual

Cuando hayas terminado de usar el entorno virtual, desactívalo con:

```bash
deactivate
```

### Configuración Adicional de Nginx

Configura Nginx para servir la aplicación. Abre el archivo de configuración de Nginx:

```bash
sudo nano /etc/nginx/sites-available/medifacil
```

Agrega la siguiente configuración para redirigir el tráfico a Gunicorn:

```nginx
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Habilita la configuración del sitio y reinicia Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/medifacil /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

Una vez enrutado con nginx, la petición de prueba puede ser:
http://IP-SERVER/search?token=mysecrettoken&name=gel

## CRON JOB del scraping

Permisos y configuración de hora
```bash
timedatectl set-timezone America/Guayaquil
chmod +x /home/ubuntu/MedifacilBackend/run_scraper.sh
```

Agregar al CRON
```bash
crontab -e
0 6 * * * /bin/bash /home/ubuntu/MedifacilBackend/run_scraper.sh >> /home/ubuntu/MedifacilBackend/scraper.log 2>&1
0 6 * * *: Esto especifica que el trabajo se ejecutará todos los días a las 6:00 AM
```

Verifica que el cron job se haya añadido correctamente ejecutando:
crontab -l


## Contribuir

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Sube los cambios a tu rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está licenciado bajo los términos de la [Licencia MIT](LICENSE).
