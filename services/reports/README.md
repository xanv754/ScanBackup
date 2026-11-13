# Reports

Genera, bajo demanda, un reporte Excel (`.xlsx`) del tráfico de las interfaces a partir de los resúmenes diarios que guarda `traffic-collector`. Solo lee MongoDB (`interfaces` y `traffic_summary_daily`): no escribe en la base de datos ni consulta SCAN.

## Comando

```bash
make prod-report ARGS="--start 2026-03-01 --end 2026-03-31"
make prod-report ARGS="--help"
```

| Opción | Significado |
|---|---|
| `--start` | Primer día del rango, `YYYY-MM-DD`, incluido. Obligatoria |
| `--end` | Último día del rango, `YYYY-MM-DD`, incluido. Obligatoria y anterior al día actual (`America/Caracas`) |

`--start` y `--end` pueden ser iguales (un solo día). Los parámetros y la configuración se validan juntos antes de abrir MongoDB y se informan todas las causas; las opciones no reconocidas también son una causa. Cada ejecución termina por completo: no queda ningún proceso.

## Configuración

Variables de entorno: `MONGO_*` y `CONFIG_PATH` (por defecto `/app/config.yml`). Las credenciales solo se leen del entorno y nunca aparecen en el log ni en la terminal.

`config.yml` (se crea desde `config.yml.example`), bajo `metadata.reports`. Todas las claves son opcionales:

| Clave | Defecto | Significado |
|---|---|---|
| `prefix_name` | `ScanBackup` | Prefijo del nombre del archivo. Sin `/ \ : * ? " < > \|` |
| `date_format` | `%Y%m%d_%H%M%S` | Formato `strftime` de la fecha de generación en el nombre. Solo directivas estándar; el resultado no puede tener caracteres prohibidos en un nombre de archivo (por ejemplo `%x` produce `/`) |
| `export_path` | `~` | Directorio existente con permiso de escritura. El servicio nunca lo crea |

En Docker `export_path` debe ser `/exports` (el volumen `./exports` del host); el defecto `~` apunta a un directorio no persistente del contenedor. Una clave no reconocida en cualquier nivel, un archivo ilegible o un valor inválido termina el proceso con código `2` y lista todas las causas.

## Funcionamiento

1. Obtiene las capas existentes (valores distintos de `interfaces.layer`, de cualquier estatus), sin distinguir mayúsculas y minúsculas. Se procesan una a una: primero las fijas que existan (`BORDE`, `BRAS`, `CACHING`, `RAI`, `DINT`, `DIST`, `IXP`) en ese orden y luego las demás en orden alfabético. Una capa nueva se incluye sin cambiar código.
2. Por capa, lee las interfaces de `interfaces` (nombre, tipo y capacidad salen siempre de ahí) y agrega en la base de datos sus resúmenes del rango. Las interfaces sin resúmenes en el rango no se incluyen.
3. Por interfaz: `In Prom`/`Out Prom` es el promedio de los promedios diarios (cada día pesa igual) e `In Max`/`Out Max` el máximo de los máximos diarios. Se convierte de bps a Gbps (`/ 1e9`) sin redondear. `Uso (%) = max(In Max, Out Max) / Capacidad * 100`, sin límite superior; es `0` si la capacidad es `0`.
4. Una interfaz con menos resúmenes que los días del rango se calcula con los días disponibles (nunca se rellena ni se interpola) y se informa la cantidad por capa. Cada día del rango sin resúmenes en ninguna capa procesada con éxito se informa como advertencia. Si ninguna capa se procesó con éxito no se evalúan los días.
5. Escribe el archivo si hay al menos una hoja.

### Archivo

`<prefix_name>_<fecha de generación>.xlsx` en `export_path`, por ejemplo `ScanBackup_20261110_153000.xlsx`. La fecha es la de generación en `America/Caracas`, no el rango. Si ya existe un archivo con ese nombre se sobrescribe. La escritura es atómica: se escribe un temporal en el mismo directorio y se reemplaza; si falla, no queda archivo parcial y el anterior queda intacto.

Una hoja por capa con al menos una interfaz, con el nombre de la capa en mayúsculas (máximo 31 caracteres y sin `: \ / ? * [ ]`; si no cumple, la capa es fallida). Fila 1 en negrita e inmovilizada, y formato `0.00` en las columnas B a H; el valor de la celda conserva su precisión (openpyxl lo guarda con 16 cifras significativas).

| Columna | Contenido |
|---|---|
| A `Interfaz` | Nombre en mayúsculas |
| B `In Prom` / C `In Max` | Gbps de entrada |
| D `Out Prom` / E `Out Max` | Gbps de salida |
| F `Capacidad` | `capacity_gbps` |
| G `Tipo` | Fabricante en mayúsculas, `UNDEFINED` si no hay |
| H `Uso (%)` | Porcentaje de uso |

Las filas se ordenan por `Tipo` y `Interfaz`; la URL de SCAN desempata sin exportarse.

## Códigos de salida

| Código | Significado |
|---|---|
| `0` | Todas las capas exitosas, al menos una con datos y archivo escrito |
| `1` | Resultado general fallido: alguna capa fallida (error de base de datos o nombre de hoja inválido), ninguna capa con datos (no se genera archivo) o falla al escribir. Las hojas obtenidas se exportan igual |
| `2` | Error general del proceso: parámetros o configuración inválidos, base de datos no disponible, falla al obtener las capas, ninguna capa existente, log no escribible o error inesperado |

## Logs

`/logs/reports.log` (rotativo, en modo append, bind mount del host). Cada línea lleva fecha y hora, nivel y descripción. No se registra cada interfaz: solo el rango, las capas, las advertencias, el archivo generado y los resultados. La terminal muestra lo mismo; los errores, las advertencias y los resultados fallidos salen por `stderr`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `constants/` | Constantes y enumeraciones |
| `domain/` | Rango de fechas, capas, modelos, cálculo y resultados (puros) |
| `persistence/` | Conexión y repositorios de MongoDB (solo lectura) |
| `export/` | Exportador (abstracción y `.xlsx`), nombre del archivo y escritura atómica |
| `service/` | Procesador de capa y orquestación del reporte |
| `reporting/` | Eventos tipados, log y terminal |

`cli.py` es la raíz de composición. Para agregar un formato nuevo basta una implementación de `ReportExporter`.
