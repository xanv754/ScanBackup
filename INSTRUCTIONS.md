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

## Configuración: qué se edita y dónde

Toda la configuración vive en **tres lugares**, y ningún dato se repite entre ellos:

| Archivo | Qué configura |
| --- | --- |
| `docker-compose.yml` (bloque `x-database`) | Base de datos (MongoDB). |
| `DataBackup/config.yml` | Capas a respaldar, credenciales de SCAN, logs y reportes. |
| `SourceScrapper/config.yml` | URLs de SCAN por capa y credenciales de scrapping. |

No hay `.env` ni otros archivos de configuración.

---

## 1. Base de datos (`docker-compose.yml`)

Abre `docker-compose.yml` y edita el bloque `x-database` del inicio del archivo, más la contraseña root del servicio `mongodb`:

```yaml
x-database: &database
  SCANBACKUP_DB_NAME: scanbackup_db
  SCANBACKUP_DB_USER: scanner
  SCANBACKUP_DB_PASSWORD: change-me      # ← cambiar

services:
  mongodb:
    environment:
      <<: *database
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: change-me-root   # ← cambiar
```

| Valor | Descripción |
| --- | --- |
| `SCANBACKUP_DB_NAME` | Nombre de la base de datos de la aplicación. |
| `SCANBACKUP_DB_USER` / `SCANBACKUP_DB_PASSWORD` | Usuario de aplicación. MongoDB lo crea automáticamente en su primer arranque, con permisos `readWrite` solo sobre `SCANBACKUP_DB_NAME`. DataBackup usa estos mismos valores para conectarse, así que no hay que escribirlos en ningún otro lugar. |
| `MONGO_INITDB_ROOT_PASSWORD` | Contraseña del usuario root de MongoDB. Solo se usa para inicializar la base y activar la autenticación. |

> ⚠️ `docker-compose.yml` está versionado en git. Para no subir tus contraseñas por error, después de editarlo ejecuta:
>
> ```bash
> git update-index --skip-worktree docker-compose.yml
> ```
>
> (Para volver a seguir sus cambios: `git update-index --no-skip-worktree docker-compose.yml`.)

> ⚠️ El usuario de aplicación solo se crea cuando el volumen de MongoDB está vacío (primer arranque). Si después cambias estos valores, MongoDB **no** los actualiza: ejecuta `make clean` (borra todos los datos) o cambia la contraseña a mano desde MongoDB.

---

## 2. Configuración de DataBackup (`DataBackup/config.yml`)

```bash
cp DataBackup/config.example.yml DataBackup/config.yml
```

Edita `DataBackup/config.yml`:

- **`layers`**: capas del BackBoneIP a respaldar (`borde`, `dint`, `dist`, `caching`, `rai`, `bras`, `ixp`, `ip_bras`, etc.), agrupadas bajo `bbip` e `ip`.
- **`metadata.scanner.scan_credentials`**: credenciales de acceso a la plataforma SCAN.

Este archivo **no** lleva datos de la base de datos: DataBackup los recibe del paso 1. El mismo `config.yml` sirve tanto en Docker como en ejecución nativa.

Referencia completa de cada campo en [`DataBackup/CONFIGURATION.md`](./DataBackup/CONFIGURATION.md).

---

## 3. Configuración de SourceScrapper (`SourceScrapper/config.yml`)

`SourceScrapper/config.yml` **no** viene en el repositorio (está en `.gitignore`); hay que crearlo siguiendo la estructura documentada en [`SourceScrapper/README.md`](./SourceScrapper/README.md#estructura):

- **`scan_credentials`**: credenciales de acceso a SCAN.
- **`layers`**: cada entrada define una URL de SCAN por capa/fabricante (`layer`, `url`, `type`, `locked` y, si `locked: true`, `credentials`).
- **`exporter.dir`**: carpeta donde se escriben los CSV generados (por defecto `data`, montada como volumen).

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

Con MongoDB ya corriendo, crea las colecciones definidas en `DataBackup/config.yml`:

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

> ⚠️ **Importante**: el subcomando `sources` depende del paquete `scrapper_scanbackup` (SourceScrapper), que **no** está instalado en la imagen Docker de `databackup` (ver nota en [`DataBackup/README.md`](./DataBackup/README.md#docker)). Por lo tanto este paso **no se puede ejecutar con `make databackup`**; requiere una instalación nativa de DataBackup con ambos paquetes (`scanbackup` y `scrapper_scanbackup`) en el mismo entorno virtual, exportando antes las variables de la base de datos con los valores del paso 1 (ver [Base de datos](./DataBackup/CONFIGURATION.md#base-de-datos)):

```bash
# entorno nativo, con ambos paquetes instalados
export SCANBACKUP_DB_HOST=localhost
export SCANBACKUP_DB_PORT=27018
export SCANBACKUP_DB_NAME=scanbackup_db
export SCANBACKUP_DB_USER=scanner
export SCANBACKUP_DB_PASSWORD=change-me

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

1. Editar `x-database` y `MONGO_INITDB_ROOT_PASSWORD` en `docker-compose.yml` (y `git update-index --skip-worktree docker-compose.yml`).
2. `cp DataBackup/config.example.yml DataBackup/config.yml` y ajustar capas y credenciales de SCAN.
3. Crear/ajustar `SourceScrapper/config.yml` (URLs, credenciales, capas).
4. `make build` (la primera vez) o `make up`.
5. `make databackup CMD="database setup"`.
6. `make scrape`.
7. Importar los CSV generados con `sources traffic_upload` / `sources ip_upload` (instalación nativa).
8. Uso diario: `make databackup CMD="history upload"` → `make databackup CMD="summaries traffic-generate"` (y sus equivalentes `ip-*`).
