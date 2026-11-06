# traffic-collector

Servicio de SCAN-Backup que respalda, a partir de SCAN, los valores de tráfico del día anterior de las interfaces activas de la colección `interfaces` de MongoDB y los almacena en `traffic_daily`, y genera su resumen diario en `traffic_summary_daily`.

# Rol

Eres un ingeniero en informática senior especializado en sistemas complejos con Python. Creas soluciones simples, escalables y mantenibles. Aplicas KISS, inyección de dependencias, POO, SOLID y patrones de diseño reconocidos. Eres muy organizado.

Tienes en el archivo @.claude/rules/codestyle.md para trabajar.

# Alcance del servicio

Hace:
- Lee de MongoDB las capas existentes y, capa por capa, sus interfaces `activa`.
- Omite las interfaces que ya tienen valores crudos del día anterior (salvo con `--force`).
- Consulta a SCAN (autenticación básica, consultas en paralelo con máximo configurable) el `.log` de tráfico de cada interfaz.
- Filtra las muestras del día anterior, las valida y las almacena en `traffic_daily`.
- Al terminar todas las capas, calcula y almacena el resumen diario en `traffic_summary_daily`.
- Registra eventos en log, informa por terminal y termina con el código de salida correcto.

No hace:
- No obtiene el listado de interfaces (eso es `interface-sync`) ni genera reportes (`reports`).
- No se comunica con otros servicios: la base de datos es el único punto de integración.
- Nunca escribe en `interfaces`: solo la lee.
- Es el único escritor de `traffic_daily` y `traffic_summary_daily`.
- No modifica ni convierte los valores de tráfico (bps tal cual los entrega SCAN).
- No reintenta consultas fallidas.
- No es un proceso permanente: se ejecuta, completa su tarea y termina [RF-017].
- No programa su propia ejecución: el `crontab` es responsabilidad del usuario operador, igual que evitar ejecuciones simultáneas (no hay bloqueo).
- No conserva en disco los `.log` recibidos de SCAN: viven en memoria solo mientras se procesa su interfaz [RF-016].

# Stack Básico

Python 3.13, PyMongo (síncrono), Pydantic, requests, PyYAML (`safe_load`), click, `logging` de la biblioteca estándar. Concurrencia con la biblioteca estándar (`concurrent.futures`), sin dependencias nuevas. Calidad: pytest y ruff (extra `[dev]` del `pyproject.toml`). Build backend: setuptools. Entrada CLI: `traffic_collector`. Cualquier dependencia nueva debe justificarse y quedar en `pyproject.toml`.

# Entorno y ejecución

Todo corre en contenedores efímeros desde la raíz del repositorio. No ejecutar el servicio fuera de Docker.

```
make init
make dev-up
make dev-build
make dev-collect ARGS="..."
make dev-test-traffic-collector ARGS="..."
make prod-collect
docker compose --env-file .env.development -f docker-compose.dev.yml run --rm --no-deps --entrypoint ruff traffic-collector check .
```

(Los nombres de los targets son propuestos: ajustar al `Makefile` real.)

Variables de entorno (secretos solo por entorno, nunca en archivos de configuración, nunca en logs) en `.env.development` o `.env.production`:
- `SCAN_USERNAME` / `SCAN_PASSWORD`
- Variables de conexión a MongoDB (las mismas de los demás servicios)
- `CONFIG_PATH` (`/app/config.yml`, montado solo lectura)

Rutas del contenedor: logs en `/logs` (bind mount a `./logs/traffic-collector`), código en `/app/src`, tests en `/app/tests`. Zona horaria del contenedor: `America/Caracas`. Usuario no root (`app`).

## Configuración (`config.yml`)

El ERS exige que estos valores sean configurables [RF-016, RF-022, RF-027]. Claves propuestas:

| Clave | Por defecto | Uso |
|---|---|---|
| `max_concurrent_requests` | `5` | Máximo de consultas simultáneas a SCAN |
| `request_timeout_seconds` | el de la plantilla | Tiempo de espera de la respuesta de SCAN |
| `max_consecutive_failures` | `5` | Fallas consecutivas que cortan una capa |

Pendiente: el ERS no define un requerimiento de lectura y validación de este archivo (valores ausentes, no numéricos, menores o iguales a cero). Hasta definirlo, validar al iniciar y tratarlo como error general del proceso.

# Requerimientos (resumen operativo del ERS)

Los números RF son provisionales hasta la numeración final del ERS.

## Ejecución [RF-017]
- Comando `traffic_collector` con la opción `--force` (única opción). Una (1) ejecución programada por día vía `crontab`; el usuario operador puede reejecutar el mismo día.
- Cada ejecución procesa todas las capas y termina. No queda ningún proceso.

## Día anterior [RF-016]
- Fecha actual en `America/Caracas` menos un día. Se calcula una sola vez al inicio y se inyecta a todo el servicio (cruzar la medianoche no lo cambia).
- Formato de la fecha de negocio: `YYYY-MM-DD`.

## Capas y lectura de interfaces [RF-018]
- Capas = valores distintos de `layer` en `interfaces`, sin importar el estatus, en orden alfabético ascendente (actualmente: BORDE, BRAS, CACHING, DINT, DIST, IXP, RAI).
- Por capa, una sola lectura de las interfaces `activa` de la capa (solo `_id` y `scan_url`). La lista no se actualiza durante la capa. Nunca una consulta por interfaz.
- Capa sin interfaces activas: warning en log, aviso por terminal y continúa. Falla de lectura de una capa: capa fallida, log, continúa.
- Error general del proceso: BD no disponible o falla al obtener las capas, o no existe ninguna capa. Cero peticiones a SCAN.
- Si ninguna capa tuvo interfaces activas: código de salida distinto de cero.

## Procesamiento por capa [RF-019]
Capas en secuencia; una no empieza hasta terminar la anterior. Por capa: leer interfaces → omitir → consultar → filtrar y validar → almacenar. Por interfaz el flujo es continuo: cada una se almacena apenas se obtiene y valida, sin esperar a las demás de la capa. Al terminar todas las capas: resumen diario [RF-026] y resultado general [RF-028]. Una capa fallida no impide las siguientes.

## Omisión [RF-020]
- Por defecto, antes de consultar una capa: una sola consulta a `traffic_daily` (`date` + `layer`, usa `idx_date_layer`) de las que tienen el día con al menos una muestra. Esas interfaces no se consultan ni se tocan.
- La omisión depende solo de los valores crudos; el resumen no influye.
- Una interfaz omitida no es fallida. Capa con todas omitidas: exitosa.
- No aplica con `--force`.

## Recolección forzada [RF-021]
- Con `--force` se consultan todas las interfaces activas.
- Por interfaz: primero obtener, filtrar y validar. Solo si es exitoso: eliminar su documento de `traffic_summary_daily` del día, luego el de `traffic_daily`, y almacenar el nuevo. Si no se obtiene, no se elimina nada.
- Riesgo asumido por el operador: si falla entre eliminar y almacenar, la interfaz queda sin datos del día.
- Sin `--force` el servicio nunca elimina datos.

## Obtención [RF-016, RF-022]
- Autenticación básica con `SCAN_USERNAME` / `SCAN_PASSWORD`. Una `requests.Session` reutilizada (cuidar la seguridad entre hilos: una sesión por hilo de trabajo).
- Una consulta por `scan_url`, tal cual, sin modificar la respuesta. Hasta `max_concurrent_requests` consultas simultáneas.
- Formato del `.log`: una línea por muestra: `<fecha UNIX> <In Prom> <Out Prom> <In Max> <Out Max>`. Contiene el día anterior completo más muestras parciales de otros días.
- Sin reintentos. Mapeo de fallos (el orden de los `except` importa: `Timeout` antes que `ConnectionError`):

| Condición | Causa de interfaz fallida |
|---|---|
| `requests.Timeout` | tiempo de espera agotado |
| `requests.ConnectionError` | sin conexión a SCAN |
| HTTP 401 | credenciales rechazadas |
| Otro HTTP >= 400 | error de SCAN |
| Respuesta vacía | respuesta sin datos |

- Además es fallida la interfaz sin muestras válidas del día anterior [RF-024] o con error de BD al almacenar [RF-025]. Cada interfaz fallida: log `error` con capa, interfaz y causa.

## Filtrado y validación [RF-023, RF-024]
- Convertir cada fecha UNIX a `datetime` en `America/Caracas`; conservar solo las del día anterior (de 00:00:00 a 23:59:59). Las demás se descartan. Los valores no se modifican.
- Línea inválida (sin fecha UNIX, distinta de cuatro valores, o valores no numéricos): se descarta con warning.
- Esperadas 288 muestras (una cada 5 min). Entre 1 y 287, o más de 288: se almacenan con warning (con la cantidad). Cero válidas: interfaz fallida, no se almacena nada.
- Valores siempre `float` antes de guardar.

## Almacenamiento de crudos [RF-025]
- Un documento por `(interface_id, date)` en `traffic_daily` con `interface_id`, `layer`, `date`, `samples` (cada una con `ts`, `in_avg`, `out_avg`, `in_max`, `out_max`), `created_at` y `updated_at`.
- Nunca dos documentos con el mismo `(interface_id, date)` (`uq_interface_date`). Si existe uno con `samples` vacío, se completa.
- Escritura por interfaz (continua), no por lote de capa. Lo almacenado se conserva aunque otra interfaz o capa falle.
- Error de BD al almacenar: corte de la capa [RF-027].

## Resumen diario [RF-026] — PENDIENTE DE ESPECIFICAR
Ya definido:
- Fase aparte, después de procesar todas las capas, aunque alguna capa haya fallado o se haya cortado.
- Se calcula para toda interfaz con crudos del día anterior y sin resumen de ese día; con lo que haya almacenado, esté completo o no. Quien no tiene crudos, no tiene resumen.
- Un documento por `(interface_id, date)` en `traffic_summary_daily`. Los máximos nunca se promedian.
- El cálculo vive en un componente propio, inyectado.
- Falla de una interfaz: log `error`, continúa con las demás, resultado general fallido.
- No consultar interfaz por interfaz: leer y escribir por lotes, sin cargar todo en memoria.

Pendiente: fórmula exacta del cálculo. No implementar hasta definirla.

## Resultado por capa y corte [RF-027]
- Capa exitosa: sin interfaces fallidas ni corte (las omitidas no cuentan; capa sin activas es exitosa con warning). Capa fallida: alguna interfaz fallida, falla de lectura de la capa, o corte.
- Corte: `max_consecutive_failures` interfaces consecutivas fallidas (contadas en orden de finalización; un éxito reinicia el conteo), o error de BD al almacenar una interfaz.
- Al cortar: cancelar las consultas en curso, descartar lo que está en memoria sin almacenar, no procesar más interfaces de la capa, marcarla fallida y seguir con la siguiente capa. Lo ya almacenado se conserva. Log con causa y cantidad de interfaces no procesadas.

## Resultado general y código de salida [RF-028]
- Exitoso solo si todas las capas lo fueron, hubo interfaces activas en al menos una y el resumen no falló. Una reejecución con todo omitido es exitosa.
- Error general del proceso: configuración inválida, credenciales de SCAN ausentes, BD no disponible al iniciar, o sin capas. No se procesa nada.
- SCAN caído no es error general: se manifiesta como interfaces y capas fallidas.
- Código `0` solo con resultado general exitoso. Propuesta: `1` resultado general fallido (incluye ninguna capa con interfaces activas), `2` error general del proceso.

## Log [RF-029]
Cada mensaje: fecha y hora, nivel (`error`, `warning`, `info`) y descripción. Archivo `/logs/traffic-collector.log`, modo append, rotación automática (`RotatingFileHandler`). Un logger por clase de reporting, inyectado; no usar `print` ni el logger raíz. No se registra cada interfaz exitosa (70.000 a 140.000 por día), solo totales.

| Evento | Nivel | Contenido |
|---|---|---|
| Inicio | info | día anterior y modo (normal o forzado) |
| Error general del proceso | error | causa |
| Capa sin interfaces activas | warning | capa |
| Falla de lectura de capa | error | capa y causa |
| Interfaces omitidas | info | capa y cantidad |
| Interfaz fallida | error | capa, interfaz y causa |
| Línea inválida | warning | capa, interfaz y posición |
| Muestras distintas de 288 | warning | capa, interfaz y cantidad |
| Corte de capa | error | capa, causa y no procesadas |
| Resultado de capa | info / error | capa y cantidades (almacenadas, omitidas, fallidas, no procesadas) |
| Resumen diario | info | cantidad generada |
| Falla del resumen de una interfaz | error | capa, interfaz y causa |
| Resultado general | info / error | resultado y capas fallidas |

Los secretos nunca aparecen en el log.

## Terminal [RF-030]
- Al iniciar: día anterior y modo.
- Por capa: inicio, omitidas y resultado con cantidades; en corte, la causa.
- Inicio y fin del resumen diario.
- Error general del proceso: mensaje con la causa (a `stderr`). Al final: resultado general.
- La salida por terminal vive separada del log.

# Modelo de datos

Todo el acceso a MongoDB vive en `persistence/` (conexión y repositorios). La decisión de qué se omite, filtra, valida o corta es pura y vive fuera de `persistence/`.

Fuente de verdad: `.claude/docs/database.md`.

| Colección | Acceso del servicio |
|---|---|
| `interfaces` | solo lectura (`_id`, `layer`, `scan_url`, `status`) |
| `traffic_daily` | lectura (omisión) y escritura |
| `traffic_summary_daily` | lectura y escritura |

Reglas:
- `layer` en mayúscula completa tal como la guarda `interface-sync` (`BORDE`); se copia sin cambios a los documentos de tráfico.
- `date` es `YYYY-MM-DD` (solo clave del bucket). `ts`, `created_at` y `updated_at` son `datetime` timezone-aware en UTC. Nunca `Timestamp` de BSON.
- Valores de tráfico y resumen: `float` en Python antes de guardar.
- El código nunca depende de la posición en `samples`.
- Consultas por capa o por lote; nunca una por interfaz.

# Pruebas

- pytest, con `make dev-test-traffic-collector`. ruff debe pasar sin errores.
- Cada RF tiene al menos un test por criterio de aceptación. Nombre: `test_<comportamiento>`; referenciar el RF en el docstring.
- Los validadores y el filtrado son puros: se prueban sin base de datos ni red. SCAN se simula con el contenedor del simulador.
- Casos que no pueden faltar: muestra de 00:00:00 del día anterior (entra) y 00:00:00 del día siguiente (sale); 23:55:00 (entra); día anterior fijo aunque cruce la medianoche; línea inválida; 287 y 289 muestras; cero muestras; omisión por crudos existentes; `--force` que no elimina nada si la obtención falla; conteo de fallas consecutivas con un éxito intermedio; corte por error de BD al almacenar; corte que conserva lo almacenado y sigue con la siguiente capa; ninguna capa con interfaces activas; resumen que se ejecuta con una capa fallida; reejecución con todo omitido (código 0).
