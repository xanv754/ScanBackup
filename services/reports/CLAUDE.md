# Instrucciones de implementación: servicio `reports` (SCAN-Backup)

Este documento es la especificación de codificación del servicio `reports`, derivada de los requerimientos funcionales RF-031 a RF-046 del ERS, que están aprobados por la usuaria (Angyee). Claude Code no tiene acceso al ERS, por lo que este documento es autocontenido. Cada regla lleva su identificador RF para trazabilidad en código y pruebas.

---

## 0. Forma de trabajo

1. **Antes de escribir código**, lee: `context.md`, `database.md`, `codestyle.md`, `commits.md`, el `Makefile`, `docker-compose.yml`, `docker-compose.dev.yml`, los `.env.*.example`, y el código existente de `services/interface-sync` y `services/traffic-collector`. El servicio nuevo debe seguir sus convenciones (estructura de carpetas, carga de configuración, logging, conexión a MongoDB, CLI, manejo de errores, estilo de pruebas). Si una convención existente contradice este documento, no la ignores: pregunta.
2. **Orden de precedencia cuando haya conflicto:** (1) este documento y los RF que resume, (2) `codestyle.md` y `commits.md`, (3) `context.md` y `database.md`. Esos dos últimos tienen secciones desactualizadas respecto al ERS (ver sección 13). No las "corrijas" tú; repórtalas.
3. **No modifiques** `interface-sync`, `traffic-collector`, `docker-compose*.yml`, `Makefile` ni `.env*` sin preguntar antes. No hay paquete `shared/`: cada servicio es independiente y no se importan módulos entre servicios. Es aceptable duplicar utilidades pequeñas (conexión a MongoDB, configuración de logging).
4. **Presenta un plan** (módulos, clases, orden de implementación) y espera confirmación antes de codificar.
5. **Si algo es ambiguo, pregunta.** No inventes comportamiento. Avisa de errores y mejoras de forma proactiva, sin suavizar el feedback técnico.
6. **Commits:** solo cuando Angyee lo ordene. Conventional Commits, en inglés, sin información innecesaria (sin `Co-Authored-By`, sin autor), sin `push`, separados en pasos funcionales y reversibles.

## 1. Qué hace el servicio

`reports` genera, bajo demanda, un único reporte Excel de tráfico. Dado un rango de fechas (`--start`, `--end`, ambos inclusive), toma los **resúmenes diarios** ya almacenados por `traffic-collector` y calcula, por cada interfaz, el promedio de sus promedios diarios y el máximo de sus máximos diarios. Expresa los valores en Gbps, calcula el porcentaje de uso y exporta un archivo `.xlsx` con una hoja por capa.

Fuera de alcance, no implementar: reportes por hora, valores crudos (`traffic_daily`), listado de interfaces, filtros por capa o interfaz, cualquier escritura en la base de datos.

## 2. Estilo de código (resumen de `codestyle.md`)

- Python 3.13, POO, KISS, SOLID, inyección de dependencias, patrones de diseño reconocibles donde aporten (Repository, Strategy para el exportador).
- Docstring en todos los métodos, en inglés técnico básico. En implementaciones de una interfaz o clase abstracta, solo se mantiene el docstring de la abstracción. Sin abusar.
- **Sin comentarios en el código.** Lo importante va en el docstring.
- Nombres declarativos, sin ambigüedad.
- Actualiza el `README.md` del servicio (es obligatorio: el `pyproject.toml` y el `Dockerfile` lo copian).
- `codestyle.md`: todos los parámetros con tipo definido (evitar `Any` y `object`); sin magic strings: constantes y enumeraciones en `constants.py` / `enums.py` dentro de una carpeta `constants/`; prohibido importar código de otros servicios.
- Dependencias previstas: `pymongo` (síncrono), `pydantic` (modelos, como en los otros servicios), `PyYAML` (`safe_load`), `click`, `openpyxl`; dev: `pytest`, `ruff`. Backend de build `setuptools`, layout `src/`.

## 3. Estructura sugerida

Ajústala a la de los otros servicios.

```
services/reports/
  pyproject.toml   README.md   config.yml   Dockerfile
  src/reports/
    cli.py                      composition root + comando click
    settings.py                 ReportSettings (prefix_name, date_format, export_path)
    config_loader.py            lectura y validación de config.yml
    date_range.py               DateRange + DateRangeValidator
    constants/constants.py      constantes (nombres de columnas, "UNDEFINED", claves de config, etc.)
    layers.py                   FIXED_LAYERS (único lugar) y orden de capas
    models.py                   InterfaceInfo, PeriodValues, LayerData, LayerResult, ExecutionResult
    repositories.py             InterfaceRepository / DailySummaryRepository (ABC) + Mongo*
    period_calculator.py        conversión a Gbps, uso (%)
    report_service.py           orquestación (sin conocer click ni openpyxl)
    exporters.py                ReportExporter (ABC) + XlsxReportExporter
    file_naming.py              nombre del archivo + escritura atómica
    logging_setup.py   console.py
  tests/
```

`report_service` depende de abstracciones (repositorios, exportador, reloj, logger, presentador de terminal) inyectadas desde `cli.py`. El reloj inyectable (para "hoy" en `America/Caracas` y la fecha del nombre del archivo) es obligatorio para poder probar RF-033 y RF-042.

## 4. Flujo de ejecución (RF-031, 044)

1. Inicializar el logging (log propio del servicio, en `/logs`).
2. Validar parámetros (RF-033) y configuración (RF-032). **Ejecutar ambas validaciones y acumular todas las causas** de ambas antes de decidir. Si hay alguna causa: registrar cada una en el log (Error), mostrarlas por terminal, terminar con error general. **No se abre ninguna conexión a MongoDB.**
3. Conectar a MongoDB y obtener las capas existentes (RF-034). Si la base no está disponible, falla al obtener las capas o no existe ninguna capa: error general.
4. Registrar/mostrar el inicio de la ejecución con el rango (Info).
5. Para cada capa, en el orden definido (sección 6): procesar (RF-034 a RF-038, 043) y, si tiene datos, agregar su hoja.
6. Evaluar los días del rango sin resúmenes (RF-036).
7. Si hubo al menos una hoja: escribir el archivo (RF-042). Si no, no se escribe nada.
8. Determinar el resultado general y el código de salida (RF-044), registrarlo y mostrarlo.

El servicio no es un proceso permanente: cada ejecución termina por completo. No inicia ejecuciones por sí mismo ni tiene cron interno.

## 5. Entradas

### 5.1 CLI (RF-031, 033)

`reports --start YYYY-MM-DD --end YYYY-MM-DD` (se invoca con `make dev-report ARGS="--start ... --end ..."`).

- Las opciones son obligatorias, pero **no declares `required=True` ni tipos de fecha en click**: click abortaría con su propio error y sin pasar por nuestro log. Declara ambas como texto opcional y valida tú, para poder acumular todas las causas.
- Las opciones no reconocidas también son una causa de invalidez: usa `ignore_unknown_options` y `allow_extra_args`, y reporta las sobrantes como causa.
- `--help` debe describir `--start`, `--end`, el formato, que ambos extremos son inclusivos y que `--end` debe ser anterior al día actual.

### 5.2 Validación del rango (RF-033)

Causas de invalidez (acumular todas las detectables):
1. Opción ausente o vacía.
2. Formato distinto de `YYYY-MM-DD` estricto (usa regex `^\d{4}-\d{2}-\d{2}$` antes de parsear; `strptime` aceptaría `2026-1-5`) o fecha inexistente (`2026-02-30`).
3. `--start` posterior a `--end`.
4. `--end` igual o posterior a hoy. **Hoy se calcula en `America/Caracas`** (`zoneinfo`), con el reloj inyectado.
5. Opciones no reconocidas.

`--start == --end` es válido (un solo día). Cantidad de días del rango = `(end - start).days + 1`.

### 5.3 Configuración `config.yml` (RF-032)

Ruta desde la variable de entorno `CONFIG_PATH` (en Docker: `/app/config.yml`). Se lee con `yaml.safe_load`.

```yaml
metadata:
  reports:
    prefix_name: "ScanBackup"
    date_format: "%Y%m%d_%H%M%S"
    export_path: "/exports"
```

| Clave | Defecto si se omite |
|---|---|
| `prefix_name` | `"ScanBackup"` |
| `date_format` | `"%Y%m%d_%H%M%S"` |
| `export_path` | `"~"` |

Todas son opcionales. Un archivo vacío (`safe_load` devuelve `None`) equivale a todos los valores por defecto.

La configuración es inválida (acumular todas las causas) si:
- el archivo no existe o no se puede leer;
- no es YAML válido, o la raíz no es un mapeo;
- tiene claves no reconocidas, en cualquier nivel (solo se reconocen `metadata` → `reports` → las tres claves);
- `prefix_name` no es texto, está vacío o solo tiene espacios, o contiene caracteres no permitidos en un nombre de archivo (`/ \ : * ? " < > |` y NUL);
- `date_format` no es texto, está vacío, no es un formato válido o produce caracteres no permitidos en un nombre de archivo;
- `export_path` no es texto, está vacío, no es un directorio existente o el usuario no tiene permiso de escritura (`os.access`). **El servicio nunca crea el directorio.**

Sobre `date_format`: `strftime` en Linux no falla con directivas desconocidas (las deja literales), así que no basta con "que no lance excepción". Valida cada `%x` contra el conjunto de directivas estándar admitidas (`a A w d b B m y Y H I p M S f z Z j U W c x X %`), rechaza un `%` final suelto, y formatea una fecha de muestra para verificar que el resultado no contenga caracteres prohibidos (`%x` produce `11/11/26`, que se rechaza por la `/`). Un formato sin directivas es válido (produce siempre el mismo nombre y sobrescribe: es decisión del usuario operador).

`export_path`: un `~` inicial se expande al directorio personal del usuario que ejecuta el servicio (`os.path.expanduser`). En Docker eso sería `/home/app`, que **no es persistente**. El `config.yml` del servicio debe declarar `export_path: "/exports"` (volumen ya montado en el compose). No cambies el defecto `~`: lo exige el ERS.

### 5.4 Variables de entorno

Las que ya recibe el servicio en el compose: `MONGO_HOST`, `MONGO_PORT`, `MONGO_USERNAME`, `MONGO_PASSWORD`, `MONGO_DATABASE`, `MONGO_AUTH_SOURCE`, `CONFIG_PATH`. `reports` no usa credenciales de SCAN. Nunca imprimas credenciales en el log ni por terminal.

## 6. Capas y orden (RF-034, 039)

- **Capas existentes** = valores distintos de `interfaces.layer`, sin importar `status`.
- **Nombre canónico de capa** = `valor.strip().upper()`. Las capas se comparan sin distinguir mayúsculas y minúsculas (según `database.md` se almacenan en mayúscula; la comparación sin distinguir mayúsculas es defensiva). Mantén, por capa canónica, el conjunto de valores originales para consultar `interfaces` con ellos.
- **Orden de procesamiento y de hojas:** primero las capas fijas que existan, en este orden exacto: `BORDE, BRAS, CACHING, RAI, DINT, DIST, IXP`; después cualquier otra capa existente, en orden alfabético ascendente por nombre canónico.
- La lista de capas fijas vive en **un único lugar** (`layers.py`). **No uses un `Enum` para validar capas (`database.md`, regla 6, y regla 20):** el reporte debe incluir capas que no estén en esa lista (capas futuras) sin cambiar código.
- Una capa fija sin interfaces almacenadas no es una capa existente: no se procesa y no genera advertencia.
- Las capas se procesan una a una; no se inicia una hasta terminar la anterior.

## 7. Lectura de datos (RF-034)

Base: MongoDB, colecciones (fuente de verdad: `database.md`):
- `interfaces`: `_id`, `layer`, `name`, `vendor`, `capacity_gbps`, `scan_url`, `status`, ...
- `traffic_summary_daily`: `interface_id`, `layer`, `date` (string `YYYY-MM-DD`), `in_avg`, `out_avg`, `in_max`, `out_max`. Único por `(interface_id, date)`. Los valores están en **bps** (ya multiplicados por 8,022 por `traffic-collector`; no los toques).

Por cada capa:
1. Leer las interfaces de la capa (todos los estatus), con proyección de `_id, name, vendor, capacity_gbps, layer`. **La pertenencia a la capa y los datos descriptivos salen siempre de `interfaces`, nunca del campo `layer` del resumen** (denormalizado y posiblemente desactualizado).
2. Agregar los resúmenes en el servidor con `$match` + `$sort` + `$group`:

```
$match: { interface_id: { $in: [ids de la capa] }, date: { $gte: "<start>", $lte: "<end>" } }
$sort:  { interface_id: 1, date: 1 }
$group: { _id: "$interface_id",
          in_avg:  { $avg: "$in_avg" },  out_avg: { $avg: "$out_avg" },
          in_max:  { $max: "$in_max" },  out_max: { $max: "$out_max" },
          days:    { $sum: 1 } }
```

   El `$sort` previo (respaldado por el índice `uq_interface_date`) hace determinista el orden de acumulación de los `$avg` y, por tanto, el resultado (RF-031, criterio 4). Si la lista de `$in` es muy grande (estimación: 10.000 a 20.000 interfaces por capa), dividirla en lotes y combinar resultados.
3. Las interfaces sin resumen en el rango no aparecen en el resultado del `$group` y **no se incluyen** en el reporte.
4. Para RF-036, obtener también las fechas distintas con resumen en el rango (`$group` por `date`) de esa capa.

Las comparaciones de rango son sobre el string `date` (orden lexicográfico = cronológico en `YYYY-MM-DD`).

Solo lectura: ninguna operación `insert/update/delete/upsert`. Las agregaciones se hacen en el servidor (no en Python); el resultado por capa sí se procesa en Python.

Cualquier `pymongo.errors.PyMongoError` durante la lectura o agregación de una capa hace **fallida** esa capa (RF-043) y el servicio continúa con la siguiente.

## 8. Cálculo (RF-035, 036, 037, 038)

Por interfaz incluida, a partir de la fila agregada (bps):

| Valor | Cálculo |
|---|---|
| In Prom | media aritmética de los `in_avg` diarios (cada día pesa igual) |
| Out Prom | media aritmética de los `out_avg` diarios |
| In Max | máximo de los `in_max` diarios (no se promedia) |
| Out Max | máximo de los `out_max` diarios |

Luego:
1. **Conversión (RF-037):** dividir esos cuatro valores entre `1_000_000_000` (decimal). Sin redondeo. La capacidad ya está en Gbps: no se convierte.
2. **Uso (%) (RF-038):** `max(in_max_gbps, out_max_gbps) / capacity_gbps * 100`. Sin límite superior (puede ser > 100). Si `capacity_gbps == 0`, el uso es `0`. No se almacena.
3. Un valor diario igual a 0 es válido y se incluye en el cálculo. Un `capacity_gbps` igual a 0 se exporta como 0.
4. Usar `float` en todo el cálculo; sin redondeos intermedios.

Ejemplo de verificación: tres resúmenes diarios con `in_avg` = 2e9, 4e9, 6e9; `out_avg` = 1e9 ×3; `in_max` = 5e9, 9e9, 7e9; `out_max` = 2e9, 3e9, 2.5e9; capacidad 10 → In Prom 4,0; Out Prom 1,0; In Max 9,0; Out Max 3,0; Uso 90,0 (usa `in_max` porque es el mayor). Con capacidad 0, Uso = 0.

### Días sin resumen (RF-036)

- Una interfaz con menos resúmenes que los días del rango se calcula con los días disponibles. Nunca se rellena ni interpola.
- Advertencia (log y terminal), con la fecha, por cada día del rango sin resúmenes en ninguna capa **procesada con éxito**.
- Advertencia por capa con la cantidad de interfaces incluidas cuyos `days` < días del rango (solo si la cantidad es > 0).
- No hacen fallida a la capa ni al reporte.

## 9. Archivo Excel (RF-039, 040, 041, 042)

### Estructura
- Un único `.xlsx` con una hoja por capa que tenga al menos una interfaz incluida. Capa sin datos: no se crea hoja.
- Nombre de hoja = nombre canónico de la capa (mayúsculas). Restricciones: máximo 31 caracteres y ninguno de `: \ / ? * [ ]`. Si no se cumplen, **la capa es fallida** (RF-043), no se crea su hoja y se registra el error. Valida esto antes de leer los datos de la capa.
- Las hojas siguen el orden de la sección 6. No hay hojas adicionales (sin portada ni metadatos).
- Se exportan siempre las hojas obtenidas, aunque otra capa haya fallado. Si no hay ninguna hoja, **no se genera archivo**.

### Columnas (fila 1 = encabezados, en este orden exacto)

| # | Encabezado | Contenido |
|---|---|---|
| A | `Interfaz` | `name`, en mayúsculas |
| B | `In Prom` | Gbps |
| C | `In Max` | Gbps (máximo de los `in_max`) |
| D | `Out Prom` | Gbps |
| E | `Out Max` | Gbps (máximo de los `out_max`) |
| F | `Capacidad` | `capacity_gbps` (0 se conserva como 0) |
| G | `Tipo` | `vendor` en mayúsculas; vacío o sin definir → `UNDEFINED` |
| H | `Uso (%)` | cálculo de la sección 8 |

- Las cuatro columnas de tráfico siempre están presentes y cada fila lleva los cuatro valores.
- Los valores numéricos son celdas numéricas (no texto). No se exporta `scan_url`, `status` ni fechas.
- Filas ordenadas ascendentemente por `Tipo` y luego por `Interfaz` (valores ya en mayúsculas, comparación por código de caracteres). Añade `scan_url` como último criterio de desempate (no se exporta) para que el orden sea determinista si dos interfaces comparten tipo y nombre.

### Formato (RF-041)
- Fila de encabezados en negrita, primera fila inmovilizada (`A2`), y formato numérico `0.00` en las columnas B a H. Es solo visual: el valor de la celda conserva su precisión completa. Nada más (sin colores ni anchos).
- Con 10.000 a 20.000 interfaces por capa, evalúa `openpyxl` en modo `write_only`. Verifica que soporte cumplir RF-041 (negrita, inmovilizado, formato numérico). Si no, usa modo normal y mide el consumo (objetivo RNF: 1 GB).

### Nombre y escritura (RF-042)
- Nombre: `f"{prefix_name}_{generated_at.strftime(date_format)}.xlsx"`. `generated_at` = hora actual en `America/Caracas` al generar el archivo (reloj inyectado). El nombre no incluye el rango. Con valores por defecto: `ScanBackup_20261110_153000.xlsx`.
- Se guarda en `export_path`. **Si ya existe un archivo con ese nombre, se sobrescribe.**
- **Escritura atómica:** escribir a un archivo temporal en el mismo directorio y finalizar con `os.replace`. Si falla la escritura, se borra el temporal, no queda archivo parcial y un archivo previo del mismo nombre queda intacto. Una falla de escritura vuelve fallido el resultado general (RF-044) y se registra (Error).
- El exportador es una abstracción (`ReportExporter`) con una implementación `.xlsx`, para poder agregar formatos sin tocar el cálculo ni la orquestación (`context.md`).

## 10. Resultados y código de salida (RF-043, 044)

### Resultado por capa
- **Exitoso:** lectura y cálculo sin error, incluida la capa sin interfaces con resúmenes en el rango (en ese caso: advertencia en log y terminal, y sin hoja).
- **Fallido:** error de base de datos al leer interfaces o resúmenes, o nombre de capa inválido como nombre de hoja. Se registra el error con capa y causa, no se crea su hoja y se sigue con la siguiente capa.

### Resultado general
- **Exitoso** solo si: todas las capas fueron exitosas, al menos una aportó datos y el archivo se escribió correctamente.
- **Fallido** si: alguna capa fue fallida; o ninguna capa aportó datos (no se genera archivo); o falló la escritura. Se completan las demás capas y se exportan las hojas obtenidas, si las hay.
- **Error general del proceso:** parámetros inválidos, configuración inválida, base de datos no disponible al iniciar, falla al obtener las capas o ninguna capa existente. No se procesa ninguna capa ni se genera archivo; con parámetros o configuración inválidos tampoco se consulta la base.

| Situación | Código de salida |
|---|---|
| Resultado general exitoso (incluye capas sin datos si al menos una aportó datos) | `0` |
| Resultado general fallido (capa fallida, ninguna capa aportó datos, falla al escribir el archivo) | `1` |
| Error general del proceso (parámetros o configuración inválidos, base de datos no disponible, falla al obtener las capas o ninguna capa existente) | `2` |

Se alinea con `interface-sync` y `traffic-collector` (`0` / `1` / `2`). El ERS solo exige "distinto de cero".

## 11. Log y terminal (RF-045, 046)

**Log** propio en `/logs` (volumen `./logs/reports`), módulo `logging` estándar, con rotación y en modo append (los mensajes de ejecuciones previas no se pierden). Cada mensaje lleva fecha y hora, nivel (error, warning, info) y descripción. **No se registra un mensaje por interfaz** incluida. Mantén el formato y el idioma de mensajes que usen los otros servicios.

| Evento | Nivel | Contenido |
|---|---|---|
| Inicio de la ejecución | Info | rango solicitado |
| Causa de invalidez de parámetros o configuración | Error | una entrada por causa |
| Error general del proceso | Error | causa |
| Capa sin datos | Warning | capa |
| Falla de una capa | Error | capa y causa |
| Día del rango sin resúmenes | Warning | fecha |
| Interfaces con menos resúmenes que los días del rango | Warning | capa y cantidad |
| Resultado de una capa | Info si exitoso, Error si fallido | capa y cantidad de interfaces incluidas |
| Archivo generado | Info | nombre, ubicación, hojas creadas, total de interfaces exportadas |
| Falla en la generación del archivo | Error | causa |
| Resultado general | Info si exitoso, Error si fallido | resultado y capas fallidas |

**Terminal:** rango solicitado al iniciar; por capa, resultado y cantidad de interfaces incluidas (o la advertencia de capa sin datos); advertencias de días sin resúmenes; nombre y ubicación del archivo generado; mensaje de error con la causa ante error general, falla de capa o falla de escritura; resultado general al final. Usa `click.echo` (errores y advertencias a stderr si así lo hacen los otros servicios).

El inicio de ejecución solo se registra y muestra cuando el rango es válido. Si los parámetros son inválidos se muestran las causas.

## 12. Docker y operación

- Los `Dockerfile` ya tienen etapas `dev` y `prod` (el de `interface-sync` usa `ENTRYPOINT ["interface_sync"]`). Para `reports` el punto de entrada debe ser el script de consola declarado en su `pyproject.toml`. Verifica el `Dockerfile` existente del servicio y avisa si no coincide.
- Volúmenes ya definidos para `reports`: `config.yml` (solo lectura), `./logs/reports:/logs`, `./exports:/exports`. Los contenedores corren con `cap_drop: ALL` y `no-new-privileges` (en producción), con el usuario `app` (UID/GID configurables): el directorio `/exports` del host debe ser escribible por ese UID.
- Ejecución: `make dev-report ARGS="--start 2026-03-01 --end 2026-03-31"` / `make prod-report ARGS="..."`. Pruebas: `make dev-test-reports`.

## 13. Discrepancias abiertas: informar a Angyee antes de codificar

Los documentos oficiales del proyecto (`context.md`, `database.md`, `codestyle.md`, `makefile.md`, `setup.md`, `production.md`, compose y `.env.*.example`) ya concuerdan con el ERS en alcance, lectura (`database.md`, reglas 19 a 24), estatus (`activa` / `desincorporada`), capas (`layer` en mayúscula, no es enum) y `export_path: /exports` en Docker. Ya no hay que reportar eso. Siguen abiertas:

1. RNF-R-15 exige un usuario de MongoDB de solo lectura para `reports`, pero el compose entrega a todos los servicios las mismas credenciales de administrador (`production.md`). Requiere una decisión de infraestructura (variables propias para `reports`) o relajar el RNF. No modifiques el compose sin preguntar.
2. `production.md` (paso 3) escribe `preffix_name` y omite `export_path` al describir el `config.yml` de `reports`. La clave correcta es `prefix_name`; debe documentarse también `export_path`.
3. Existen dos `config.yml.example` de `reports` en el proyecto con `export_path` distinto (`"~"` y `"~/exports"`). En Docker ambos apuntan a `/home/app`, que no es persistente. El ejemplo del servicio debe declarar `export_path: "/exports"` (sección 5.3). El defecto en código sigue siendo `~`.
4. `makefile.md`, `setup.md` y `production.md` describen los argumentos de `reports` como "tipo de reporte, rango de fechas, interfaces". Solo existen `--start` y `--end`. Actualiza esos textos al implementar (regla de `codestyle.md`: mantener la documentación al día).
5. `makefile.md` indica que `dev-report` levanta el simulador de SCAN, pero en `docker-compose.dev.yml` `reports` solo depende de MongoDB. `reports` no usa SCAN, así que el compose es correcto y la documentación es la que sobra.
6. `setup.md` indica que `reports` aún no tiene tests y que `make dev-test-reports` termina sin pruebas. Actualízalo al crear las pruebas.
7. Si el `config.yml` de `reports` necesita otras claves además de `metadata.reports.*`, avísalo: RF-032 trata cualquier clave no reconocida como configuración inválida.

## 14. Pruebas (pytest)

- **Unitarias, sin base de datos ni archivos reales** (RNF-R-20): validación de rango (todas las causas y su acumulación, reloj fijo en `America/Caracas`, `start == end`, hoy y futuro, `2026-1-5`, `2026-02-30`), validación de configuración (cada causa, acumulación, defectos, archivo vacío, `~`, directorio inexistente sin crearlo, `date_format` con `%x`), cálculo (ejemplo numérico de la sección 8, valores 0, capacidad 0, uso > 100, un solo día, días faltantes), orden de capas (fijas, luego adicionales alfabéticas, capa fija inexistente no procesada), nombre de hoja inválido, nombre de archivo, resultados por capa y general con repositorios y exportador falsos (todos los casos de RF-043 y RF-044, incluidos los códigos de salida).
- **Exportador:** generar un archivo y releerlo con `openpyxl`: nombres y orden de hojas, encabezados exactos, orden de columnas, celdas numéricas, mayúsculas en `Interfaz` y `Tipo`, `UNDEFINED`, orden de filas, negrita, inmovilizado, formato `0.00`, sin hojas extra, sin archivo si no hay hojas, sobrescritura de un archivo existente, escritura atómica (si falla, no queda parcial y el previo queda intacto).
- **Log y terminal:** cada evento de la tabla con nivel y contenido; ningún mensaje por interfaz; mensajes de ejecuciones previas se conservan.
- **Integración** (MongoDB del entorno dev, datos sembrados por el fixture): lectura por capa con capa modificada, interfaces desincorporadas incluidas, interfaz sin resúmenes excluida, extremos del rango inclusive, capas con distinta combinación de mayúsculas, solo lectura (la base no cambia), determinismo (dos ejecuciones → mismo contenido).
- Nombra cada prueba con el RF y el criterio que cubre (por ejemplo `test_rf038_capacity_zero_gives_zero_usage`).

## 15. Definición de terminado

- Todos los criterios de aceptación de RF-031 a RF-046 cubiertos por pruebas, `ruff` sin errores, `pytest` en verde (`make dev-test-reports`).
- `README.md` del servicio con uso, `config.yml`, salida, códigos de salida y logs.
- Ejecución real con `make dev-report` sobre datos sembrados, abriendo el `.xlsx` resultante y comparándolo con la especificación de la sección 9.
- Lista final de discrepancias abiertas y mejoras detectadas.