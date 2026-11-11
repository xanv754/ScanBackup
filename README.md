# SCAN-Backup

Histórico de tráfico de interfaces de red del BackboneIP de CANTV. Recolecta diariamente, vía SCAN, los valores de tráfico (periodos de 5 minutos) del día anterior, los almacena en MongoDB y genera reportes `.xlsx`. No consulta equipos de red ni modifica datos de SCAN.

## Tabla de contenido

- [Servicios](#servicios)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Inicio rápido](#inicio-rápido)
- [Variables de entorno](#variables-de-entorno)
- [Uso con Make](#uso-con-make)
- [Códigos de salida](#códigos-de-salida)
- [Logs y exportaciones](#logs-y-exportaciones)
- [Documentación](#documentación)

## Servicios

Tres paquetes Python independientes (Python 3.13, CLI con `click`). No se comunican entre sí; MongoDB es el único punto de integración. El fallo de uno no impide la ejecución de los demás.

| Servicio | Responsabilidad | Ejecución | Detalle |
|---|---|---|---|
| `interface-sync` | Scraping de interfaces en SCAN; sincroniza la BD con su estatus (activa/desincorporada) | Manual | [README](./services/interface-sync/README.md) |
| `traffic-collector` | Consulta en SCAN el tráfico del día anterior de las interfaces activas y lo almacena | Automática, `crontab`, 1 vez/día | [README](./services/traffic-collector/README.md) |
| `reports` | Genera reportes `.xlsx` por rango de fechas desde la BD | Manual | [README](./services/reports/README.md) |

El `crontab` es responsabilidad del usuario de operatividad, no del sistema.

## Arquitectura

```
SCAN ──► interface-sync ──► ┌─────────┐ ◄── traffic-collector ◄── SCAN
                            │ MongoDB │
         exports/*.xlsx ◄── └─────────┘ ──► reports
```

- Servicios como contenedores efímeros (`docker compose run --rm`), lanzados desde el `Makefile`.
- Dependencia crítica: SCAN. Un cambio o caída de SCAN afecta o impide el sistema.
- Exportación sobre una abstracción que permite agregar formatos sin tocar la lógica de reportes.

## Requisitos

Git, Docker con Docker Compose v2 y Make. Python y MongoDB corren dentro de contenedores. Se requiere acceso de red a SCAN y un usuario de SCAN con permiso de lectura.

## Inicio rápido

1. Copiar y completar las variables de entorno (ver [siguiente sección](#variables-de-entorno)).
2. Crear el `config.yml` de cada servicio desde su `config.yml.example`.
3. Crear `logs/` y `exports/` con el usuario dueño de `APP_UID`/`APP_GID`.
4. Construir imágenes, levantar la base de datos y ejecutar los servicios.

Pasos completos: [Producción](./docs/production.md) · [Desarrollo](./docs/setup.md).

## Variables de entorno

```bash
cp .env.production.example .env.production   # producción (docker-compose.yml)
cp .env.development.example .env.development # desarrollo (docker-compose.dev.yml)
```

El archivo resultante contiene credenciales: no debe versionarse. Los secretos solo se leen del entorno, nunca de archivos de configuración.

| Variable | Obligatoria | Descripción |
|---|---|---|
| `MONGO_USERNAME` / `MONGO_PASSWORD` | Sí | Usuario administrador de MongoDB, usado por los tres servicios |
| `MONGO_DATABASE` | Sí | Base de datos del sistema (recomendado `scan_backup`) |
| `MONGO_AUTH_SOURCE` | Sí | Base donde se validan las credenciales (`admin`) |
| `MONGO_HOST_PORT` | No | Puerto expuesto en `127.0.0.1` (`27017`) |
| `SCAN_USERNAME` / `SCAN_PASSWORD` | Sí | Acceso de lectura a SCAN (`interface-sync` y `traffic-collector`) |
| `APP_UID` / `APP_GID` | No | Dueño de logs y `exports/` (`id -u` / `id -g`, defecto `1000`). Requieren reconstruir imágenes si cambian |

> **Importante:** `MONGO_USERNAME`, `MONGO_PASSWORD` y `MONGO_DATABASE` solo se aplican cuando MongoDB inicializa su volumen por primera vez. Cambiarlos después rompe la conexión de los servicios salvo que se modifiquen dentro de MongoDB o se elimine el volumen (borra el histórico).

> **Importante:** `logs/` y `exports/` deben existir antes de la primera ejecución y pertenecer a `APP_UID`/`APP_GID`; de lo contrario Docker las crea como `root` y los servicios no podrán escribir.

## Uso con Make

Cada regla existe con prefijo `dev-` (desarrollo) y `prod-` (producción).

| Regla | Acción |
|---|---|
| `make init` | Prepara el entorno |
| `make prod-build` / `prod-up` / `prod-down` | Construir imágenes, levantar y detener MongoDB |
| `make prod-sync ARGS="run"` | Sincroniza interfaces (`check-scan` solo verifica SCAN) |
| `make prod-collect [ARGS="--force"]` | Recolecta el tráfico del día anterior |
| `make prod-report ARGS="--start YYYY-MM-DD --end YYYY-MM-DD"` | Genera el reporte `.xlsx` del rango |
| `make dev-test` | Pruebas de los tres servicios |
| `make dev-sim-up` | Simulador de SCAN (solo desarrollo) |

Todas las reglas y variables: [makefile.md](./docs/makefile.md).

## Códigos de salida

`0` solo ante éxito. Cualquier otro valor indica fallo:

| Código | Significado |
|---|---|
| `1` | Resultado fallido (capas/páginas/interfaces fallidas, ausencia de datos requeridos) |
| `2` | Error general del proceso (configuración inválida, credenciales ausentes, BD o SCAN no disponibles) |

El detalle por servicio está en su README.

## Logs y exportaciones

- `logs/<servicio>/`: logs rotativos con `logging` estándar, un directorio por servicio (bind mount del host).
- `exports/`: bind mount del host; solo `reports` escribe ahí (`<prefix_name>_<fecha>.xlsx`).

## Documentación

| Documento | Contenido |
|---|---|
| [docs/setup.md](./docs/setup.md) | Entorno de desarrollo y simulador de SCAN |
| [docs/production.md](./docs/production.md) | Instalación, `crontab`, operación, respaldo y problemas comunes |
| [docs/makefile.md](./docs/makefile.md) | Guía de todas las reglas del `Makefile` |
| [services/*/README.md](./services) | Funcionamiento, configuración y códigos de salida de cada servicio |
