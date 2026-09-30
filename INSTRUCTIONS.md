# INSTRUCTIONS.md — Guía de arranque de ScanBackup

Guía paso a paso para levantar el sistema completo (**DataBackup** + **SourceScrapper** + **MongoDB**) usando Docker Compose, que es la forma recomendada según el [`README.md`](./README.md).

Sigue los pasos **en este orden exacto**: cada uno depende del anterior.

---

## 0. Requisitos previos

Antes de empezar, asegúrate de tener instalado:

- **Docker** y el plugin **Docker Compose** (`docker compose version`)
- **make** (opcional, pero recomendado — simplifica todos los comandos)

No necesitas Python ni MongoDB instalados localmente: todo corre dentro de contenedores.

---

## 1. Variables de entorno (`.env`)

El `.env` en la raíz del repositorio define las credenciales con las que arranca el contenedor de MongoDB.

```bash
cp .env.example .env
```

Edita `.env` y completa los valores (evita dejar los `change-me` por defecto):

| Variable | Descripción |
| --- | --- |
| `MONGO_ROOT_USER` / `MONGO_ROOT_PASSWORD` | Credenciales root de arranque de MongoDB (habilitan `--auth`). |
| `MONGO_APP_DB` | Nombre de la base de datos de la aplicación. |
| `MONGO_APP_USER` / `MONGO_APP_PASSWORD` | Usuario de aplicación, creado automáticamente en el primer arranque por `mongo-init/init-mongo.js`, con permisos `readWrite` solo sobre `MONGO_APP_DB`. |

> ⚠️ Estas variables (`MONGO_APP_*`) deben coincidir exactamente con el bloque `database` de `DataBackup/config.docker.yml` (ver paso 2). Si no coinciden, DataBackup no podrá autenticarse contra MongoDB.

---

## 2. Configuración de DataBackup (`config.docker.yml`)

DataBackup necesita un archivo de configuración propio para saber qué capas respaldar, cómo conectarse a Mongo y con qué credenciales consultar SCAN.

```bash
cp DataBackup/config.example.yml DataBackup/config.docker.yml
```

Edita `DataBackup/config.docker.yml`:

- **`database.host`**: debe quedar en `"mongodb"` (nombre del servicio en la red interna de Docker, **no** `localhost`).
- **`database.name` / `database.user` / `database.password`**: deben coincidir con `MONGO_APP_DB` / `MONGO_APP_USER` / `MONGO_APP_PASSWORD` del `.env`.
- **`layers`**: capas del BackBoneIP a respaldar (`borde`, `dint`, `dist`, `caching`, `rai`, `bras`, `ixp`, `ip_bras`, etc.) agrupadas bajo `bbip` e `ip`.
- **`metadata.scanner.scan_credentials`**: credenciales de acceso a la plataforma SCAN.

Referencia completa de cada campo en [`DataBackup/CONFIGURATION.md`](./DataBackup/CONFIGURATION.md).

> Nota: `config.docker.yml` es el que se monta dentro del contenedor (`docker-compose.yml` lo mapea a `/app/config.yml`). Si además quieres correr DataBackup de forma nativa (sin Docker), necesitas un `DataBackup/config.yml` aparte con `database.host: "localhost"` — ver [`DataBackup/README.md`](./DataBackup/README.md#configuración).

---

## 3. Configuración de SourceScrapper (`config.yml`)

SourceScrapper ya trae un `SourceScrapper/config.yml` en este repositorio, pero revísalo/ajústalo antes de levantar el sistema:

- **`scan_credentials`**: credenciales de acceso a SCAN (pueden ser las mismas del paso 2).
- **`layers`**: cada entrada define una URL de SCAN por capa/fabricante (`layer`, `url`, `type`, `locked`, y `credentials` si `locked: true`).
- **`exporter.dir`**: carpeta donde se escriben los CSV generados (por defecto `data`, montada como volumen).

Detalle completo de la estructura en [`SourceScrapper/README.md`](./SourceScrapper/README.md#estructura).

---

## 4. Levantar los servicios

Desde la raíz del repositorio:

```bash
make up
```

Esto construye (si hace falta) y levanta en segundo plano:

- `mongodb` — con el usuario de aplicación creado automáticamente en su primer arranque.
- `databackup` y `sourcescrapper` — imágenes de tipo CLI, **no quedan corriendo**; se invocan puntualmente con `make databackup` y `make scrape`.

Si es la primera vez, o cambiaste código/dependencias, usa en su lugar:

```bash
make build
```

Verifica que todo esté arriba (MongoDB debe quedar `healthy`):

```bash
make ps
```

---

## 5. Inicializar la base de datos

Con MongoDB ya corriendo, crea las colecciones definidas en `config.docker.yml`:

```bash
make databackup CMD="database setup"
```

Verifica que se hayan creado correctamente:

```bash
make databackup CMD="database inspect"
```

---

## 6. Obtener las fuentes de red desde SCAN

Ejecuta el scrapper para generar los CSV con las interfaces disponibles (uno por capa, en `SourceScrapper/data/`):

```bash
make scrape
```

Para una sola capa en vez de todas:

```bash
make scrape LAYER=borde
```

---

## 7. Importar las fuentes al sistema

Los CSV generados en el paso 6 deben cargarse a MongoDB con el CLI de DataBackup (comandos `sources traffic_upload` / `sources ip_upload`).

> ⚠️ **Importante**: el subcomando `sources` depende del paquete `scrapper_scanbackup` (SourceScrapper), que **no** está instalado en la imagen Docker de `databackup` (ver nota en [`DataBackup/README.md`](./DataBackup/README.md#docker)). Por lo tanto este paso **no se puede ejecutar con `make databackup`**; requiere una instalación nativa de DataBackup con ambos paquetes (`scanbackup` y `scrapper_scanbackup`) en el mismo entorno virtual:

```bash
# entorno nativo, con ambos paquetes instalados
python -m scanbackup sources traffic_upload --filepath SourceScrapper/data/BORDE.csv
python -m scanbackup sources ip_upload --filepath SourceScrapper/data/IP_BRAS.csv
```

Repite por cada CSV/capa generado.

---

## 8. Uso normal del sistema

Con las fuentes ya cargadas (estatus `ACTIVO`), el flujo diario habitual es:

```bash
# Recolecta el tráfico del día anterior (o --date YYYY-MM-DD) de todas las fuentes activas
make databackup CMD="history upload"

# Recolecta las IP activas del día anterior
make databackup CMD="history ip-upload"

# Genera el resumen diario de tráfico
make databackup CMD="summaries traffic-generate"

# Genera el resumen diario de IP activas
make databackup CMD="summaries ip-generate"
```

---

## Comandos útiles adicionales

| Comando | Qué hace |
| --- | --- |
| `make logs` | Sigue los logs de todos los servicios (`make logs SERVICE=mongodb` para uno solo). |
| `make mongo-shell` | Abre `mongosh` autenticado como el usuario de aplicación. |
| `make stop` | Detiene los contenedores sin eliminarlos. |
| `make start` | Reinicia contenedores ya creados. |
| `make restart` | `down` + `up`. |
| `make down` | Detiene y elimina contenedores (conserva volúmenes/datos de Mongo). |
| `make clean` | Elimina contenedores + volúmenes (**borra los datos de MongoDB**). |
| `make fclean` | `clean` + elimina las imágenes construidas. |
| `make re` | `fclean` + `build` (reconstrucción total desde cero). |

---

## Resumen del orden completo

1. `cp .env.example .env` y completar credenciales.
2. `cp DataBackup/config.example.yml DataBackup/config.docker.yml` y ajustar (`host: "mongodb"`, credenciales igual al `.env`, capas, credenciales SCAN).
3. Ajustar `SourceScrapper/config.yml` (URLs, credenciales, capas).
4. `make up` (o `make build` la primera vez).
5. `make databackup CMD="database setup"`.
6. `make scrape`.
7. Importar los CSV generados con `sources traffic_upload` / `sources ip_upload` (instalación nativa).
8. Uso diario: `make databackup CMD="history upload"` → `make databackup CMD="summaries traffic-generate"` (y sus equivalentes `ip-*`).
