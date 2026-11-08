# Traffic Collector

Recolecta, vía SCAN, el tráfico (periodos de 5 minutos) del día anterior de las interfaces activas y lo almacena en MongoDB (`traffic_daily`). No consulta equipos de red ni modifica datos de SCAN.

## Comando

```bash
make dev-collect                    # recolecta el día anterior (America/Caracas)
make dev-collect ARGS="--force"     # vuelve a consultar lo ya recolectado
```

Se ejecuta una (1) vez por día vía `crontab` (responsabilidad del usuario de operatividad) y puede reejecutarse el mismo día: las interfaces que ya tienen muestras del día se omiten, con una sola consulta por capa. Con `--force` se consultan todas; por interfaz, solo si la nueva obtención es válida se elimina su resumen y sus valores crudos del día y se almacenan los nuevos. Si no se obtiene, no se elimina nada. Al final de cada ejecución se completan los resúmenes diarios que falten.

## Configuración

Variables de entorno: `SCAN_USERNAME`, `SCAN_PASSWORD`, `MONGO_*` y `CONFIG_PATH` (por defecto `/app/config.yml`). Los secretos solo se leen del entorno y nunca aparecen en el log ni en la terminal.

`config.yml` (se crea desde `config.yml.example`):

| Clave | Significado |
|---|---|
| `max_concurrent_requests` | Máximo de consultas simultáneas a SCAN |
| `request_timeout_seconds` | Tiempo máximo de espera de una respuesta de SCAN |
| `max_consecutive_failures` | Interfaces consecutivas fallidas que cortan el procesamiento de una capa |

Una configuración ausente o inválida termina el proceso con código `2` y lista todas las causas.

## Funcionamiento

1. Calcula una sola vez el día anterior en `America/Caracas`; es el mismo para todas las capas, aunque la ejecución cruce la medianoche.
2. Lee las capas en orden ascendente y las procesa una tras otra. Una capa fallida o cortada no impide las siguientes.
3. Por capa: lee las interfaces activas, omite las ya recolectadas y descarga los `.log` con consultas en paralelo acotadas por `max_concurrent_requests`. Los hilos solo descargan; el hilo principal procesa cada respuesta a medida que llega (parsear, filtrar el día, validar y almacenar).
4. Cada línea del `.log` es `<fecha UNIX> <In Prom> <Out Prom> <In Max> <Out Max>`. Las líneas inválidas se descartan con un aviso. Se conservan solo las muestras del día anterior (de 00:00:00 a 23:55:00).
5. Se esperan 288 muestras: entre 1 y 287, o más de 288, se almacenan con aviso; cero muestras válidas es una interfaz fallida.
6. Una capa se corta si hay `max_consecutive_failures` interfaces fallidas consecutivas (un éxito reinicia la cuenta) o si falla la base de datos al almacenar. Lo ya almacenado se conserva.
7. Al terminar todas las capas se genera el resumen diario (RF-026) en `traffic_summary_daily`: `in_avg`/`out_avg` son el promedio de las muestras y `in_max`/`out_max` el máximo (nunca el promedio de máximos), todos multiplicados por `8.022` (el factor histórico `0.000000008022` expresado en bps en vez de Gbps; equivale a bps si SCAN reporta bytes/s, unidad aún sin confirmar). Se omiten las interfaces que ya tienen resumen o no tienen muestras. Un error de base de datos detiene la fase y hace fallar el resultado general. El porcentaje de uso no se almacena: lo calcula `reports`.

Las fallas de una interfaz (sin conexión, tiempo agotado, credenciales rechazadas, error HTTP, respuesta vacía, sin muestras válidas, error de base de datos) no se reintentan y se registran con capa, interfaz y causa.

## Códigos de salida

| Código | Significado |
|---|---|
| `0` | Todas las capas exitosas (una reejecución con todo omitido también sale con `0`) |
| `1` | Resultado general fallido: alguna capa o interfaz fallida, o ninguna capa con interfaces activas |
| `2` | Error general del proceso: configuración inválida, credenciales ausentes, base de datos no disponible, sin capas, log no escribible o error inesperado |

## Logs

`/logs/traffic-collector.log` (rotativo, bind mount del host). No se registra cada interfaz exitosa: solo avisos, errores y el resumen de cada capa. La terminal muestra el avance por capa; los errores salen por `stderr`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `domain/` | Modelos y resultados puros |
| `parsing/` | Parser del `.log`, filtro del día y validador de muestras (puros) |
| `scan/` | Cliente HTTP de SCAN y sus errores |
| `persistence/` | Conexión y repositorios de MongoDB |
| `collection/` | Procesadores de interfaz y de capa, orquestador y fase de resumen diario |
| `reporting/` | Eventos tipados, log y terminal |

`cli.py` es la raíz de composición: ensambla las dependencias y devuelve el código de salida.

## Pruebas

```bash
make dev-test-traffic-collector
```

Las pruebas de integración (`-m integration`) usan una base temporal en el MongoDB de desarrollo y un SCAN simulado en proceso; se omiten si MongoDB no está disponible.
