# ScanBackup

Sistema para recolectar, importar, exportar y gestionar los datos de tráfico de red provenientes del sistema de monitoreo **SCAN** de CANTV.

## Objetivo

SCAN es un sistema de monitoreo que muestra los valores de tráfico de todas las interfaces de red cada 5 minutos, pero no conserva histórico. **ScanBackup** consulta esa información diariamente y la respalda para permitir visualizar y analizar datos de días, meses o incluso años anteriores.

## Arquitectura

El proyecto sigue Clean Architecture, con la dirección de dependencias `domain ← application ← infrastructure`:

- **`domain/`**: entidades, repositorios y servicios de negocio, sin dependencias externas ni conocimiento de infraestructura.
- **`application/`**: casos de uso y capas de entrega (CLI con Click, API con FastAPI).
- **`infrastructure/`**: implementaciones concretas (MongoDB, lectores/escritores de archivos, recolectores de datos de SCAN).
- **`shared/`**: utilidades transversales (configuración, constantes, errores, salidas por terminal, tipos de datos).

## Requerimientos

- Python `>= 3.10`
- Una instancia de MongoDB accesible
- Dependencias declaradas en `pyproject.toml`: `click`, `fastapi`, `pandas`, `pydantic`, `pymongo`, `pyyaml`, `rich`, entre otras.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

## Configuración

ScanBackup se configura mediante un archivo `config.yml` ubicado en la raíz del proyecto, validado con Pydantic. Puede partir de `config.example.yml` como plantilla:

```bash
cp config.example.yml config.yml
```

El archivo define, entre otros:

- **`layers`**: las capas del BBIP a respaldar y las colecciones donde se almacenan.
- **`database`**: los datos de conexión a MongoDB.
- **`metadata`**: rutas de almacenamiento, configuración de logs, del recolector (scanner) y de reportes.

La descripción detallada de cada parámetro se encuentra en [`CONFIGURATION.md`](./CONFIGURATION.md).

## CLI

ScanBackup expone su funcionalidad mediante una CLI construida con Click:

```bash
python -m scanbackup --help
```

Los comandos están agrupados en cuatro módulos:

### `database` — administrador de la base de datos

```bash
python -m scanbackup database setup                                       # Crea las colecciones definidas en la configuración
python -m scanbackup database inspect                                     # Lista las colecciones existentes
python -m scanbackup database import --collection <nombre> --filepath <archivo.csv> [--delimiter ";"]
python -m scanbackup database export --collection <nombre> --dirpath <carpeta> [--delimiter ";"] [--id]
```

### `history` — administrador del historial

```bash
python -m scanbackup history upload [--date YYYY-MM-DD]
```

Recolecta de SCAN el tráfico del día indicado (por defecto, el día anterior) para todas las fuentes con estatus `ACTIVO` en la base de datos, sin importar su capa, y lo almacena en el sistema.

```bash
python -m scanbackup history ip-upload [--date YYYY-MM-DD]
```

Recolecta de SCAN las IP activas del día indicado (por defecto, el día anterior) para todas las fuentes con estatus `ACTIVO` en la base de datos, sin importar su capa, y lo almacena en el sistema.

### `summaries` — administrador de los resúmenes

```bash
python -m scanbackup summaries traffic-generate [--date YYYY-MM-DD]
```

Genera el resumen diario de tráfico del día indicado (por defecto, el día anterior), leyendo el histórico ya almacenado de todas las capas configuradas. Por cada interfaz, promedia sus muestras de 5 minutos (`In Prom`, `In Max`, `Out Prom`, `Out Max`), calcula el porcentaje de uso (el mayor entre `In Max` y `Out Max`, dividido entre la capacidad de la interfaz) y guarda el resultado asociado al `device` de la fuente.

```bash
python -m scanbackup summaries ip-generate [--date YYYY-MM-DD]
```

Genera el resumen diario de IP activas del día indicado (por defecto, el día anterior), leyendo el histórico ya almacenado de todas las capas IP configuradas. Por cada interfaz, promedia sus muestras de 5 minutos (`In Prom`, `In Max`) y guarda el resultado asociado al `device` de la fuente.

## Pruebas unitarias

El proyecto usa `unittest` junto con `unittest.mock`, mockeando el filesystem y las llamadas a la base de datos.

Ejecutar toda la suite:

```bash
make test
```

o directamente:

```bash
python -m unittest discover -s tests -t . -v
```

Para ejecutar un módulo puntual:

```bash
python -m unittest tests.shared.config.test_config -v
```
