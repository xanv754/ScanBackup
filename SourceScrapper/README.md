# Source Scrapper

Módulo extra para el sistema **ScanBackup** que obtiene, mediante *web scrapping*, el listado de interfaces de red disponibles en la plataforma de monitoreo **SCAN** de CANTV.

SCAN no expone una API para consultar sus interfaces, por lo que este proyecto navega el HTML de cada capa de red (borde, dint, dist, bras, rai, ixp, caching, ip_bras) y extrae la información necesaria (enlace, URL del `.log`, capacidad y modelo del equipo) para que ScanBackup pueda luego solicitar el tráfico de cada interfaz.

## Requisitos

- Python >= 3.10

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

Esto instala el paquete `scrapper_scanbackup` junto con el script `scanbackup` (definido en `pyproject.toml`).

## Archivo de configuración

El módulo espera un archivo `config.yml` dentro de un *directorio base*, resuelto así:

1. Si la variable de entorno `SCANBACKUP_HOME` está definida, se usa esa ruta como directorio base.
2. En caso contrario, se usa el directorio de trabajo actual (`cwd`) desde el que se ejecuta `scanbackup`.

Esto permite ejecutar `scanbackup` desde la raíz del proyecto sin configuración adicional (el directorio base termina siendo esa misma raíz), y también apuntar a una ubicación distinta —por ejemplo dentro de un contenedor— fijando `SCANBACKUP_HOME`:

```bash
SCANBACKUP_HOME=/ruta/a/mi/config scanbackup run
```

### Estructura

```yaml
exporter:
  dir: "data"
  delimiter: ";"

header:
  link: "link"           # Encabezado de la columna con la URL del .log
  interface: "interface"  # Encabezado de la columna con el nombre del enlace
  capacity: "capacity"    # Encabezado de la columna con la capacidad
  type: "model"           # Encabezado de la columna con el modelo del equipo

scan_credentials:
  username: "usuario_scan"
  password: "clave_scan"

layers:
  - layer: "borde"
    url: "https://example.com"
    type: "cisco"
    locked: false

  - layer: "borde"
    url: "https://example.com"
    type: "huawei"
    locked: false

  - layer: "bras"
    url: "https://example.com"
    type: ""
    locked: true
    credentials:
      username: "usuario"
      password: "clave"
```

### Campos

| Campo | Descripción |
| --- | --- |
| `exporter.dir` | Carpeta donde se escriben los CSV exportados, resuelta contra el directorio base (ver [Archivo de configuración](#archivo-de-configuración)) si es relativa. Se crea automáticamente si no existe. |
| `exporter.delimiter` | Delimitador de columnas usado al exportar los CSV. |
| `header.*` | Encabezados de columna usados en los CSV exportados. |
| `scan_credentials` | Credenciales por defecto para autenticarse en SCAN. |
| `layers` | Lista de fuentes a scrappear. Cada entrada representa una URL de SCAN asociada a una capa de red. |
| `layers[].layer` | Capa de red a la que pertenece la URL: `borde`, `dint`, `dist`, `bras`, `ip_bras`, `rai`, `ixp` o `caching`. |
| `layers[].url` | URL de SCAN desde la cual se hace el scrapping del HTML. |
| `layers[].type` | Fabricante del equipo (`cisco`, `huawei`, `juniper`, `zte`, etc.), usado para elegir la lógica de parseo correspondiente. Puede ir vacío si la capa no distingue por fabricante. |
| `layers[].locked` | Indica si la URL requiere autenticación propia (`true`) o usa acceso por defecto (`false`). |
| `layers[].credentials` | Credenciales específicas para esa URL. Solo se usa cuando `locked: true`; si se omite, no aplica autenticación. |

Pueden existir varias entradas con el mismo `layer` (por ejemplo, `borde` con `cisco`, `huawei` y `juniper`); el módulo las procesa todas y consolida el resultado en un único CSV por capa.

## CLI

```bash
python -m scrapper_scanbackup --help
```

### Comando `run`

Ejecuta el scrapping y exporta el resultado a CSV en la carpeta indicada por `exporter.dir` del `config.yml`.

```bash
python -m scrapper_scanbackup run
```

| Opciones | Requerido | Descripción | Valores válidos |
| --- | --- | --- | --- |
| `--layer [LAYER]` | No. Por defecto `all` | Ejecuta el procesamiento para una única capa. | `borde`, `dint`, `dist`, `bras`, `ip`, `rai`, `ixp`, `caching`. |

Ejemplo:

```bash
# Procesa únicamente la capa borde
python -m scrapper_scanbackup run --layer borde
```

Cada capa procesada genera su propio archivo CSV (por ejemplo `data/BORDE.csv`, `data/BRAS.csv`) con las columnas definidas en `header` del `config.yml`.

## Docker

El `Dockerfile` fija `SCANBACKUP_HOME=/app` (ver [Archivo de configuración](#archivo-de-configuración)), por lo que `config.yml` y el directorio de `exporter.dir` deben montarse dentro de `/app`.

### Construir la imagen

```bash
docker build -t scanbackup-sources .
```

### Ejecutar el contenedor

El `ENTRYPOINT` es `scanbackup` y el `CMD` por defecto es `run`, así que basta con montar `config.yml` y la carpeta de datos:

```bash
docker run --rm \
  -v "$(pwd)/config.yml:/app/config.yml:ro" \
  -v "$(pwd)/data:/app/data" \
  scanbackup-sources
```

Cualquier argumento adicional se pasa después del nombre de la imagen y sobrescribe el `CMD` (por ejemplo, para procesar solo una capa):

```bash
docker run --rm \
  -v "$(pwd)/config.yml:/app/config.yml:ro" \
  -v "$(pwd)/data:/app/data" \
  scanbackup-sources run --layer borde
```

## Pruebas unitarias

Las pruebas están en la carpeta `tests/` y usan `unittest` con mocks sobre el scrapping HTML (no requieren red).

```bash
python -m unittest discover -s tests -v
```
