# Resumen
Source Scrapper es un módulo extra (los pulmónes) para el sistema ScanBackup, que permite obtener la lista de interfaces de red a consultar, existentes en la plataforma de monitoreo SCAN de la empresa CANTV.

La página de monitoreo SCAN no tiene una API para consultar la información de las existentes interfaces que permite la visualización, es por ello que este proyecto se encarga de realizar un scrapping a la página para obtener directamente del HTML la información necesaria para que el sistema ScanBackup pueda solicitar la información de tráfico de las interfaces.

# Objetivos
## Peticiones
- Obtener un archivo con el listado todas las interfaces de red existentes en SCAN.

# Estructura
## General
- `data/`: Carpeta base en donde se encuentran todos los archivos de texto plano creados o necesarios para el sistema.
- `scrapper_scanbackup/`: Código fuente.
- `tests/`: Pruebas unitarias del sistema.

## Código Fuente
La arquitectura del sistema se basa en las distintas capas de SCAN:

- "BORDE", también llamado "Enlaces Internacionales", son las interfaces que se conectan con el mundo.
- "BRAS", también llamado "Agregación", son las interfaces principales que van directamente a la MetroEthernet.
    - "BRAS IP", es la información de las IP activas llegadas a los agregadores.
- "CACHING", son las interfaces de los servidores de Caching.
- "RAI", también llamado "Clientes Dedicados", son las interfaces especializadas para las empresas.
- "DINT", también llamado "Distribución Internet".
- "DIST", también llamado "Distribución Regional".
- "IXP", son interfaces para servicios especiales.

Cada capa cuenta con su scrapper para la página. Algunas capas cuentan con distintas tecnologías, ya que la página en SCAN hace ligeras variaciones que afectan el scraping.

```bash
SourceScrapper/scrapper_scanbackup
├── borde # tipo de capa de red
├── bras # tipo de capa de red
├── caching # tipo de capa de red
├── dint # tipo de capa de red
├── distr # tipo de capa de red
├── __init__.py
├── ixp # tipo de capa de red
├── __main__.py  # CLI.
├── model.py # Modelo de información a obtener para ScanBackup.
├── rai # tipo de capa de red
├── updater.py # Constructor de la clase scrapping.
└── utils # Clases variadas con utilidades tranversales.
```

# Stack
Lenguaje: Python
Librería Scrapper: BeautifulSoup
Archivo configuración: YAML, utilizando la librería PyYAML. Archivo de configuración llamado `config.yml`.

# CLI

Construido con Click. Comando de entrada:

```bash
python -m scrapper_scanbackup --help
```

Todo el sistema debe contener con un CLI sólido que permita realizar las operaciones necesarias para su uso.