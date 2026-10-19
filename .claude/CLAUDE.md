# SCAN-Backup

Histórico de tráfico de interfaces de red del BackboneIP de CANTV. Recolecta diariamente, vía SCAN, los valores de tráfico (periodos de 5 min) del día anterior y genera reportes `.xlsx`. No consulta equipos de red ni modifica datos de SCAN.

Contexto completo: `context.md`. No leer salvo que el usuario lo solicite explícitamente.

- Reglas de código: `codestyle.md`
- Reglas de commits: `commits.md`

## Servicios
Tres paquetes Python independientes, cada uno con su `pyproject.toml` (setuptools) y CLI con click. No se comunican entre sí; MongoDB es el único punto de integración.

| Servicio | Responsabilidad | Ejecución |
|---|---|---|
| `interface-sync` | Scraping de interfaces en SCAN; sincroniza la BD con su estatus (activa/desincorporada) | Manual |
| `traffic-collector` | Toma interfaces activas de la BD, consulta tráfico en SCAN y lo almacena | Automática, `crontab`, 1 vez/día (obligatorio) |
| `reports` | Genera reportes desde la BD y los exporta a `exports/` | Manual |

El fallo de un servicio no debe impedir la ejecución de los demás. El `crontab` es responsabilidad del usuario de operatividad, no del sistema.

## Stack
Python 3.13, pip, MongoDB + PyMongo (síncrono), requests, BeautifulSoup (solo `interface-sync`), PyYAML (`safe_load`), click, openpyxl (solo `reports`), pytest, ruff, Docker, Docker Compose, Make.

- Servicios como contenedores efímeros: `docker compose run --rm`, lanzados desde el `Makefile`.
- Secretos (BD y SCAN) solo por variables de entorno, nunca en archivos de configuración.
- Exportación sobre una abstracción que permita agregar formatos sin tocar la lógica de reportes (inicial: `.xlsx`).

## Reglas operativas
- Código de salida `0` solo ante éxito. Todo lo demás es distinto de cero: errores de ejecución o conexión, y ausencia de datos requeridos (ej. `traffic-collector` sin interfaces activas).
- Logs: módulo `logging` estándar, rotativos, un directorio propio por servicio, en bind mount del host.
- `exports/`: bind mount del host; solo `reports` escribe ahí.
- Dependencia crítica: SCAN. Un cambio o caída de SCAN afecta o impide el sistema.