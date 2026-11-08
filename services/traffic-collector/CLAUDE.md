# traffic-collector — guía de implementación de la recolección (RF-016 a RF-025 y RF-027 a RF-030)
 
Fuera de alcance: el cálculo del resumen diario (RF-026). Solo se deja el punto de enganche.
Base: `CLAUDE.md` del servicio, `database.md` y `codestyle.md`.
 
## 1. Estructura
 
```
services/traffic-collector/
  pyproject.toml            # entrada CLI: traffic_collector
  Dockerfile
  config.yml                # max_concurrent_requests, request_timeout_seconds, max_consecutive_failures
  src/traffic_collector/
    cli.py                  # click + composition root + código de salida
    settings.py             # entorno + config.yml (Pydantic), validación al iniciar
    domain/                 # modelos y enums puros
      models.py             # ActiveInterface, Sample, DailyTraffic
      results.py            # InterfaceResult, LayerResult, RunResult, causas (Enum)
    clock.py                # TargetDate: día anterior en America/Caracas (se inyecta "hoy")
    scan/
      client.py             # ScanClient (Protocol) + HttpScanClient
      errors.py             # ScanTimeout, ScanUnreachable, ScanUnauthorized, ScanHttpError, ScanEmptyResponse
    parsing/
      log_parser.py         # texto -> líneas válidas/ inválidas (puro)
      day_filter.py         # fecha UNIX -> datetime Caracas, deja solo el día anterior (puro)
      validator.py          # reglas de las 288 muestras (puro)
    persistence/
      connection.py
      interface_repository.py   # solo lectura
      traffic_repository.py     # omisión, guardado, borrado forzado
      summary_repository.py     # solo borrado del día (force); el resto es de RF-026
    collection/
      interface_processor.py    # obtener -> parsear -> filtrar -> validar -> InterfaceOutcome
      layer_processor.py        # omisión, paralelismo acotado, corte
      run_orchestrator.py       # capas en orden, enganche de resumen, resultado general
    reporting/
      events.py                 # eventos tipados
      run_logger.py             # RF-029
      terminal.py               # RF-030
  tests/
```
 
Patrones: inyección de dependencias por constructor (nada de globales), `Protocol` para `ScanClient` y repositorios, composición en `cli.py`. Lo que decide (omitir, filtrar, validar, contar fallas, resultado) es puro y no toca BD ni red.
 
## 2. Decisión de diseño clave: paralelismo
 
- Los hilos de trabajo SOLO descargan (`ScanClient.fetch(scan_url) -> str`). Son I/O puro.
- El hilo principal procesa cada respuesta a medida que llega: parsear, filtrar, validar, contar fallas y almacenar, en orden de finalización.
- Por qué: el corte (RF-027) se decide en un solo lugar sin condiciones de carrera, "fallas consecutivas en orden de finalización" queda bien definido, y lo descargado después del corte se descarta sin haberse almacenado.
- Enviar al pool con ventana acotada: nunca más de `max_concurrent_requests` tareas en vuelo (no encolar 20.000 futuros). Usar `concurrent.futures.ThreadPoolExecutor` con `wait(..., return_when=FIRST_COMPLETED)`.
- Una `requests.Session` por hilo (`threading.local`); no compartir una sola.
- Al cortar: dejar de enviar, `cancel()` a lo pendiente, esperar a las que ya corren y descartar su resultado.
## 3. Orden de construcción (cada paso con sus tests antes de seguir)
 
1. **Base:** `pyproject.toml`, Dockerfile, servicio en `docker-compose*.yml`, targets del Makefile, `settings.py`. Si la configuración es inválida: error general del proceso.
2. **Dominio y `clock.py`:** `TargetDate.previous_day(today)`; fecha calculada una sola vez en `cli.py` y pasada a todos [RF-016].
3. **Parsing puro** [RF-023, RF-024]: línea → 5 campos numéricos; descartar inválidas (warning); convertir UNIX a `datetime` tz Caracas y conservar solo el día anterior; devolver `ts` en UTC; validador: 0 válidas = fallo, `!= 288` = warning. Valores a `float`.
4. **Cliente SCAN** [RF-016, RF-022]: `HttpScanClient` con autenticación básica y timeout configurable; mapear excepciones (`Timeout` antes que `ConnectionError`; 401; otro >= 400; respuesta vacía) a `errors.py`. Sin reintentos. Probar contra el simulador de SCAN.
5. **Repositorios** [RF-018, RF-020, RF-021, RF-025]:
   - `InterfaceRepository`: `distinct("layer")` ordenado ascendente; `active_by_layer(layer)` con solo `_id` y `scan_url` (una consulta por capa).
   - `TrafficRepository`: `interface_ids_with_samples(layer, date)` (una consulta por capa; filtro `date`, `layer`, `"samples.0": {"$exists": true}`, proyección `interface_id`); `save(daily)` como `update_one(upsert)` por `(interface_id, date)` con `$set` de `layer`, `samples`, `updated_at` y `$setOnInsert` de `created_at`; `delete_day(interface_id, date)`.
   - `SummaryRepository.delete_day(interface_id, date)`.
   - Probar contra el MongoDB de desarrollo (índice único `uq_interface_date`).
6. **`InterfaceProcessor`:** recibe el texto descargado (o el error) y devuelve un resultado de interfaz [RF-022] con causa. En `--force`, solo si es exitoso: borrar resumen, borrar crudos, guardar [RF-021]. Si no se obtiene, no se borra nada.
7. **`LayerProcessor`** [RF-019, RF-020, RF-027]: leer interfaces activas; capa vacía = warning y exitosa; omisión por una consulta (salvo `--force`); ventana de descargas; contador de fallas consecutivas (un éxito lo reinicia); corte por umbral o por error de BD al almacenar; resultado de capa (fallida si alguna interfaz falló). Lo ya almacenado se conserva.
8. **`RunOrchestrator`** [RF-018, RF-019, RF-028]: obtener capas (sin capas o BD caída = error general; sin cero peticiones a SCAN), recorrer en orden, continuar tras una capa fallida, llamar al enganche de resumen (`SummaryPhase`, protocolo; mientras RF-026 esté pendiente, implementación vacía que informa "pendiente" y no falla), calcular el resultado general.
9. **Reporting** [RF-029, RF-030]: eventos tipados que `RunLogger` y `TerminalReporter` consumen (el procesamiento no escribe texto). Log con `RotatingFileHandler` en `/logs/traffic-collector.log`. No registrar cada interfaz exitosa. Errores de terminal a `stderr`.
10. **CLI** [RF-017]: `traffic_collector [--force]`; ensamblar dependencias; código de salida `0` solo con resultado general exitoso, `1` resultado fallido o ninguna capa con interfaces activas, `2` error general del proceso.
## 4. Reglas que no se pueden olvidar
 
- El día anterior se calcula una vez y es el mismo para todas las capas, aunque la ejecución cruce la medianoche.
- Nunca una consulta a la BD por interfaz.
- Una capa es fallida si alguna interfaz falló, aunque se hayan procesado todas. La omitida no cuenta como falla.
- Cero muestras válidas = interfaz fallida y cuenta para las fallas consecutivas.
- Entre 1 y 287 (o más de 288) muestras: se guardan con warning.
- Capa vacía: warning y continúa. Todas vacías: código distinto de cero.
- Una reejecución con todo omitido sale con `0`.
- El archivo descargado no se escribe a disco ni se conserva.
- Los secretos no aparecen en logs ni en terminal.
## 5. Pruebas mínimas (un test por criterio, RF en el docstring)
 
- Puros (sin BD ni red): filtrado de borde (00:00:00 entra, 00:00:00 del día siguiente sale, 23:55:00 entra), línea inválida, 0/287/288/289 muestras, conteo de fallas consecutivas con éxito intermedio, resultado de capa y general, código de salida.
- `HttpScanClient` contra el simulador: cada causa de fallo (timeout, sin conexión, 401, 500, vacío).
- Repositorios contra MongoDB de desarrollo: omisión en una consulta, `upsert` sin duplicados, completar un documento con `samples` vacío, borrado forzado.
- Integración con SCAN simulado: capa que se corta y la siguiente continúa; error de BD al almacenar corta la capa y conserva lo almacenado; `--force` sin datos nuevos no borra; segunda ejecución sin `--force` no consulta a SCAN.
- `ruff check .` sin errores.
## 6. Dependencias tuyas
 
- Fixtures y simulador de SCAN con `.log` reales (varias fechas, más y menos de 288 muestras, líneas rotas).
- Targets finales del `Makefile` y nombres de las claves de `config.yml`.
- Decisión sobre un RF de lectura y validación de la configuración del collector.
- Fórmula del resumen diario (RF-026) para conectar `SummaryPhase`.
