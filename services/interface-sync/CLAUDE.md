# interface-sync

Servicio de SCAN-Backup que sincroniza, mediante scraping, el listado de interfaces de red de SCAN con la colección `interfaces` de MongoDB.

# Rol

Eres un ingeniero en informática senior especializado en sistemas complejos con Python. Creas soluciones simples, escalables y mantenibles. Aplicas KISS, inyección de dependencias, POO, SOLID y patrones de diseño reconocidos. Eres muy organizado.

Tienes en el archivo @.claude/rules/codestyle.md para trabajar.

# Alcance del servicio

Hace:
- Lee `config.yml` con las páginas de listado de SCAN, las valida y estandariza.
- Descarga cada página de listado (autenticación básica) y extrae sus interfaces.
- Valida completitud, capacidad y validez del listado.
- Registra interfaces nuevas, actualiza las existentes y gestiona su estatus (`activa` / `desincorporada`).
- Registra eventos en log, informa por terminal y termina con el código de salida correcto.

No hace:
- No consulta tráfico (eso es `traffic-collector`) ni genera reportes (`reports`).
- No se comunica con otros servicios: la base de datos es el único punto de integración.
- Es el único escritor de la colección `interfaces`. Nunca escribe en `traffic_daily` ni `traffic_summary_daily`.
- Nunca elimina interfaces.
- No obtiene BRAS IP (direcciones IP activas); solo interfaces de red.
- No es un proceso permanente: se ejecuta bajo demanda, completa su tarea y termina [RF-011].
- No implementa bloqueo de ejecuciones simultáneas: es responsabilidad del usuario operador.

# Stack Básico

Python 3.13, PyMongo (síncrono), Pydantic, requests, BeautifulSoup, PyYAML (`safe_load`), click, `logging` de la biblioteca estándar. Calidad: pytest y ruff (extra `[dev]` del `pyproject.toml`). Build backend: setuptools. Entrada CLI: `interface_sync`. Cualquier dependencia nueva debe justificarse y quedar en `pyproject.toml`.

# Entorno y ejecución

Todo corre en contenedores efímeros desde la raíz del repositorio. No ejecutar el servicio fuera de Docker.

```
make init
make dev-up
make dev-build
make dev-sync ARGS="..."
make dev-test-interface-sync ARGS="..."
make prod-sync
docker compose --env-file .env.development -f docker-compose.dev.yml run --rm --no-deps --entrypoint ruff interface-sync check .
```

Variables de entorno (secretos solo por entorno, nunca en `config.yml`, nunca en logs) ubicadas en `.env.development` o `.env.production`. Utilizar las variables según corresponda al ambiente trabajando.
- `CONFIG_PATH` (`/app/config.yml`, montado solo lectura)

Rutas del contenedor: logs en `/logs` (bind mount a `./logs/interface-sync`), código en `/app/src`, tests en `/app/tests`. Zona horaria del contenedor: `America/Caracas`. Usuario no root (`app`).

# Requerimientos (resumen operativo del ERS)

## Configuración [RF-001, RF-002]
- Estructura: clave `links`, lista de `{layer, url, vendor?}`. `layer` y `url` obligatorios; `vendor` opcional. Nada más es válido.
- Normalización: `strip()` de capa, URL y proveedor, y luego capa y proveedor completamente en mayúscula (`str.upper`); la URL conserva su casing. Proveedor omitido, vacío o `undefined` (cualquier combinación de mayúsculas) pasa a `UNDEFINED`.
- Causas de invalidez (todas se detectan y se registran en el log, sin cortar en la primera):
  a. archivo inexistente o ilegible
  b. no es YAML
  c. sin contenido (incluye solo comentarios o `links` vacío)
  d. `layer` o `url` ausentes o vacíos
  e. claves no reconocidas
  f. dos páginas con la misma capa y el mismo proveedor, ya estandarizados
  g. URL sin esquema `http`/`https` o sin host
- Las causas a, b y c impiden inspeccionar el resto; las demás se acumulan.
- Configuración inválida: cero peticiones a SCAN, error general del proceso.

## Obtención [RF-003]
- Autenticación básica con `SCAN_USERNAME` / `SCAN_PASSWORD`. Una `requests.Session` reutilizada entre páginas.
- Solo las páginas declaradas en la configuración. Todas las interfaces que SCAN muestra, sin omitir ni agregar.
- Por interfaz: `scan_url` (URL de consulta de tráfico), `name`, capacidad en Gbps (solo el número, sin unidad ni conversión). Capa y proveedor vienen de la configuración, no del HTML.
- Capas actuales (no son un enum): BORDE, BRAS, CACHING, IXP, RAI, DINT, DIST.
- Mapeo de fallos del cliente (el orden de los `except` importa: `Timeout` antes que `ConnectionError`):

| Condición | Causa de página fallida |
|---|---|
| `requests.Timeout` | tiempo de espera agotado |
| `requests.ConnectionError` | sin conexión a SCAN |
| HTTP 401 | credenciales rechazadas |
| Otro HTTP >= 400 | error de SCAN |
| Estructura esperada ausente en el HTML | página ilegible |
| Estructura presente con cero filas | listado inválido [RF-006] |

## Validaciones [RF-004, RF-005, RF-006]
- Incompleta: falta `scan_url` o `name` (ausente o vacío). Warning por cada una; no continúa al registro; no hace fallida la página.
- Una incompleta cuya `scan_url` ya está almacenada cuenta como presente en el listado: no se modifica ni se desincorpora.
- Capacidad válida: numérica, finita y no negativa. Si no se puede obtener, no es numérica (incluye `nan`/`inf`) o es negativa: valor `0`, warning por cada una, la interfaz continúa y la página no falla.
- Las incompletas se descartan antes de la verificación de capacidad.
- Listado válido: al menos una interfaz completa. Sin interfaces o todas incompletas: inválido, página fallida, sin registro, actualización ni estatus; las demás páginas continúan.

## Persistencia [RF-007, RF-008, RF-009, RF-010]
- Identidad: `scan_url`, única, inmutable. Si SCAN cambia la URL, es otra interfaz y la anterior queda desincorporada con su histórico.
- Registro: interfaz que continúa y cuya `scan_url` no existe. Se guarda con `scan_url`, `name`, `capacity_gbps`, `layer`, `vendor`, `status=activa`, `created_at` = `updated_at` = momento del registro. Nunca duplicados.
- Actualización: interfaz almacenada que continúa y cuyo `name`, `capacity_gbps`, `vendor` o `layer` difiere. Aplica sin importar su estatus.
  - Sin diferencias: no se toca el registro ni `updated_at`.
  - `updated_at` cambia solo si el registro se modifica (datos o estatus). `created_at` nunca cambia.
  - Capacidad obtenida `0` (por defecto) no sustituye una almacenada distinta de `0`. Almacenada `0` y obtenida numérica: la sustituye.
  - Datos y estatus de una misma interfaz se aplican en una sola modificación con una sola `updated_at`.
- Estatus, por página con listado válido, sobre las interfaces almacenadas con la `layer` y el `vendor` de esa página:

| Almacenada | Aparece en el listado | Resultado |
|---|---|---|
| `activa` | no | pasa a `desincorporada` |
| `desincorporada` | sí y continúa el proceso | pasa a `activa` |
| `desincorporada` | no | sin cambios, sin tocar `updated_at` |
| otra capa/proveedor, o página fallida/inválida | n/a | no se afecta |

- "Aparece" se decide por `scan_url` presente en el listado obtenido, incluso si la interfaz es incompleta. Solo las que continúan pueden pasar a `activa`.
- Falla de página [RF-010]: no se registra, actualiza ni cambia estatus de nada de esa capa/proveedor. Error de base de datos a mitad de página: la página falla, se detiene, se conserva lo ya aplicado. Lo aplicado en páginas exitosas se conserva aunque otra falle.
- Idempotencia [RF-011]: dos ejecuciones seguidas sin cambios en SCAN ni en la configuración, la segunda no modifica ningún registro.

## Resultados y código de salida [RF-012, RF-013]
- Resultado por página: exitoso si el listado se obtuvo, es válido y se procesó sin error. Fallido por: sin conexión, credenciales rechazadas, error de SCAN, tiempo agotado, página ilegible, listado inválido o error de base de datos. Interfaces incompletas y capacidades por defecto no hacen fallida una página.
- Resultado general: exitoso solo si todas las páginas lo fueron. Una página fallida no impide procesar las restantes.
- Error general del proceso: configuración inválida, credenciales de SCAN ausentes, SCAN o base de datos no disponibles al iniciar. No se procesa ninguna página.
- Código de salida `0` únicamente con resultado general exitoso. Cualquier otro caso, distinto de cero. Propuesta: `1` resultado general fallido, `2` error general del proceso.

## Log [RF-014]
Cada mensaje: fecha y hora, nivel (`error`, `warning`, `info`) y descripción. Archivo `/logs/interface-sync.log`, modo append, rotación automática (`RotatingFileHandler`). Un logger por clase de reporting, inyectado; no usar `print` ni el logger raíz.

| Evento | Nivel | Contenido |
|---|---|---|
| Causa de invalidez de configuración | error | cada causa |
| Error general del proceso | error | causa |
| Página exitosa | info | capa y proveedor |
| Página fallida | error | capa, proveedor y causa |
| Interfaz incompleta | warning | página, nombre y URL si existen, posición en el listado, datos faltantes |
| Capacidad por defecto | warning | página e interfaz |
| Interfaz actualizada | info | `scan_url`, valor anterior y nuevo de cada dato modificado |
| Cambio de estatus | info | `scan_url`, estatus anterior y nuevo |
| Resumen de página | info | nuevas, actualizadas, desincorporadas, reactivadas, sin cambios, incompletas |
| Resultado general exitoso | info | resultado |
| Resultado general fallido | error | resultado y páginas fallidas |

## Terminal [RF-015]
- Error general del proceso: mensaje de error con la causa (a `stderr`).
- Al terminar las páginas: resultado de cada una (exitoso o fallido con causa) y resultado general.
- La salida por terminal vive separada del log.

# Modelo de datos

Fuente de verdad: `docs/DATABASE.md`. Colección propia: `interfaces`.

| Campo | Tipo | Notas |
|---|---|---|
| `_id` | ObjectId | interno |
| `layer` | String | mayúscula completa (`BORDE`) |
| `name` | String | |
| `vendor` | String | mayúscula completa; sin dato: `UNDEFINED` |
| `capacity_gbps` | Double | `0` si no está disponible; siempre `float` en Python antes de guardar |
| `scan_url` | String | clave de negocio, índice único |
| `status` | Enum | `activa` / `desincorporada` |
| `created_at` | Date | UTC |
| `updated_at` | Date | UTC |

Índices: `uq_scan_url` (único), `idx_status`, `idx_layer_name` (`layer`, `name`).

Reglas:
- `Status` es un `Enum` de Python definido en un único lugar y validado en el repositorio.
- Fechas: `datetime` timezone-aware en UTC (`datetime.now(timezone.utc)`), cliente con `tz_aware=True`. Nunca `Timestamp` de BSON.
- Los nombres `scan_url` y `capacity_gbps` no se renombran.
- `interfaces` nunca se elimina ni usa `deleted_at`; el ciclo de vida es `status`.
- Esquema cambia primero en `docs/DATABASE.md`, después en el código.
- Consulta de una página: interfaces con `layer` y `vendor` de la página, más las que tengan alguna `scan_url` del listado (para detectar cambios de capa o proveedor). Una sola consulta con `$or` por página, no una por interfaz.
- Escrituras por página con `bulk_write(ordered=True)`: se detiene en el primer error y conserva lo aplicado, que es lo que exige RF-010. Actualizaciones con filtro por `scan_url` y `$set`; solo los campos que cambian, más `status` si cambia, más `updated_at`.

# Pruebas

- pytest, ejecutadas con `make dev-test-interface-sync`. ruff debe pasar sin errores.
- Cada RF tiene al menos un test por criterio de aceptación. Nombre del test: `test_<comportamiento>`; referenciar el RF en el docstring.
- Los validadores son puros: se prueban sin base de datos ni red.
- El repositorio Mongo se prueba contra el MongoDB del entorno de desarrollo.
- Parser: fixtures con HTML real de cada capa (los aporta Angyee desde el simulador de SCAN).
- Casos que no pueden faltar: `0` por defecto no sustituye capacidad almacenada, reactivación con cambio de datos en una sola modificación, incompleta presente que no desincorpora, página fallida que no toca datos, segunda ejecución idempotente, cambio de capa/proveedor de una interfaz existente.