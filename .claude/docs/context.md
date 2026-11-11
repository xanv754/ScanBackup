# SCAN-Backup

## Objetivo y Alcance
SCAN-Backup es un sistema desarrollado para obtener la información de tráfico de las distintas interfaces de red monitoreadas diariamente por el sistema SCAN. Dado que SCAN actualmente no conserva un histórico de los valores de tráfico que registra, SCAN-Backup suple dicha necesidad recolectando los valores de tráfico, en periodos de 5 minutos, que SCAN obtiene del día anterior al actual, y almacenándolos para conformar el histórico de tráfico de las interfaces de red. Todo ello tiene como finalidad poder generar, bajo demanda, un reporte de tráfico por rango de fechas, exportado a un archivo Excel (`.xlsx`) destinado a los analistas, consultores o líderes de la coordinación Gestión Producto Red de Datos de CANTV.

SCAN-Backup no monitorea las interfaces en vivo ni realiza consultas a los equipos de red. Toda la información obtenida se extrae exclusivamente de la información que muestra el sistema SCAN. SCAN-Backup obtiene de SCAN la información de las interfaces de red, lo que le permite consultar los valores de tráfico que SCAN obtuvo de dichas interfaces y almacenarlos en la base de datos de SCAN-Backup. Asimismo, no modifica ni altera los valores de tráfico almacenados, ni agrega ni elimina interfaces de red declaradas en SCAN. Los valores que muestra el reporte se calculan en cada generación a partir de los valores almacenados, sin alterarlos.

Dado que SCAN no almacena valores de tráfico de días antiguos, SCAN-Backup inicia su recolección a partir de su puesta en marcha. Las consultas a SCAN se realizan diariamente para obtener toda la información de tráfico del día anterior. El sistema depende de los datos de SCAN; por ello, cualquier cambio, detención o corrupción de SCAN, como sistema base, afectará el correcto funcionamiento de SCAN-Backup o, en el peor de los casos, lo impedirá. Si el tráfico de una interfaz no se obtiene y el servicio no se reejecuta antes de las 00:00, el tráfico de esa interfaz para ese día no puede recuperarse.

A la fecha de redacción de este documento, el sistema contempla únicamente la recolección de tráfico de todas las capas del BackboneIP de la red de CANTV. No se contempla la información de las direcciones IP activas (BRAS IP) que SCAN muestra en la capa BRAS.

### Reporte
- Se genera bajo demanda del usuario operador, con un rango de fechas (`--start`, `--end`, ambos inclusive) de días anteriores al actual.
- Trabaja únicamente con los resúmenes diarios y con la información de las interfaces almacenadas. No consulta valores crudos, no recalcula resúmenes y no modifica la base de datos.
- Por cada interfaz con al menos un resumen dentro del rango, calcula el promedio de sus promedios diarios y el máximo de sus máximos diarios, los expresa en Gbps y calcula su porcentaje de uso.
- Incluye interfaces activas y desincorporadas. Se calcula con los días que tengan resumen; los días sin resumen no se completan.
- No incluye valores crudos, listado de interfaces ni promedios por hora.

### Supuestos y puntos abiertos
- Se asume que el snapshot que SCAN entrega por interfaz contiene siempre el día anterior completo; las muestras de otros días pueden estar incompletas y se descartan.
- Se asume correcto el factor de conversión 8,022 del resumen diario. La unidad que entrega SCAN no está confirmada: equivale a bps solo si SCAN reporta bytes/s.
- Se asume que `capacity_gbps` está en Gbps.
- Volumen estimado: de 10.000 a 20.000 interfaces por capa (proyección; el Excel de ejemplo tiene 611 interfaces en total).

## Estructura del proyecto
El sistema se divide en tres servicios independientes, cada uno con una única responsabilidad:

- **`interface-sync`**: Servicio encargado de obtener, mediante scraping, la lista de interfaces de red existentes en el sistema SCAN y de mantenerla sincronizada en la base de datos. Cada interfaz se registra con su estatus (activa o desincorporada), el cual este servicio actualiza en cada ejecución.
- **`traffic-collector`**: Servicio encargado de respaldar los valores de tráfico del día anterior. Procesa una a una las capas existentes en la base de datos (valores distintos de `layer` en `interfaces`, sin importar el estatus), en orden alfabético ascendente. Por cada capa lee sus interfaces activas, omite las que ya tienen valores crudos del día anterior, consulta a SCAN las demás y almacena los valores validados. Al terminar todas las capas, genera el resumen diario.
- **`reports`**: Servicio encargado de generar el reporte de tráfico por rango de fechas a partir de los resúmenes diarios y de las interfaces almacenadas, y de exportarlo a un archivo para los usuarios del sistema.

Los servicios no se comunican directamente entre sí. La base de datos, única para todos, es el único punto de integración entre ellos. Cada colección tiene un único servicio escritor:

| Colección | Escribe | Lee |
|---|---|---|
| `interfaces` | `interface-sync` | `traffic-collector`, `reports` |
| `traffic_daily` | `traffic-collector` | `traffic-collector` |
| `traffic_summary_daily` | `traffic-collector` | `traffic-collector`, `reports` |

No existe un paquete compartido entre servicios: cada uno se conecta solo a MongoDB.

## Tecnologías

Las tecnologías listadas a continuación son las definidas para el sistema, aunque pueden a lo largo del desarrollo añadirse nuevas depedencias según sea la necesidad. Estas son las básicas al comenzar.

### Lenguaje y entorno

| Tecnología | Uso |
|---|---|
| Python 3.13 | Lenguaje de desarrollo de los tres servicios |
| pip | Instalación de dependencias; cada servicio es un paquete con su propio `pyproject.toml` |
| `concurrent.futures` (biblioteca estándar) | Consultas simultáneas a SCAN en `traffic-collector`, sin dependencias nuevas |

Cada servicio se define como un paquete Python independiente, con su propio `pyproject.toml` que declara sus dependencias y su punto de entrada CLI. Backend de build: `setuptools`.

### Persistencia

| Tecnología | Uso |
|---|---|
| MongoDB | Base de datos única, compartida por todos los servicios |
| PyMongo | Driver de conexión a MongoDB (acceso síncrono) |
| Pydantic | Modelos y validación de datos |

### Comunicación con SCAN

| Tecnología | Uso | Servicio |
|---|---|---|
| requests | Peticiones HTTP hacia SCAN (autenticación básica) | `interface-sync`, `traffic-collector` |
| BeautifulSoup | Scraping del HTML de SCAN | `interface-sync` |

### Configuración e interfaz

| Tecnología | Uso |
|---|---|
| PyYAML | Lectura de archivos de configuración (`safe_load`) |
| click | Interfaz de línea de comandos de cada servicio |

### Infraestructura

| Tecnología | Uso |
|---|---|
| Docker | Contenerización de cada servicio |
| Docker Compose | Orquestación de los servicios y la base de datos |
| Make | Punto de entrada operativo: el `Makefile` define los targets que ejecutan los servicios en orden |

### Calidad

| Tecnología | Uso |
|---|---|
| pytest | Pruebas automatizadas |
| ruff | Linting y formateo |

### Exportación de reportes

| Tecnología | Uso | Servicio |
|---|---|---|
| openpyxl | Generación de reportes en formato `.xlsx` | `reports` |

El formato inicial de exportación es `.xlsx`. La exportación debe diseñarse sobre una abstracción que permita agregar otros formatos sin modificar la lógica de generación de reportes.

## Configuración

Cada servicio tiene su propio archivo `config.yml`, cuya ruta se recibe por la variable de entorno `CONFIG_PATH`. Se lee con `safe_load`. Los secretos (credenciales de base de datos y de SCAN) se proporcionan mediante variables de entorno, no mediante los archivos de configuración, y nunca aparecen en el log ni en la terminal.

- **`traffic-collector`**: valores configurables con defecto: máximo de consultas simultáneas a SCAN (5), tiempo de espera de la respuesta de SCAN y número de fallas consecutivas que cortan una capa (5).
- **`reports`**: claves opcionales bajo `metadata.reports`:

| Clave | Defecto | Uso |
|---|---|---|
| `prefix_name` | `ScanBackup` | Prefijo del nombre del archivo de exportación |
| `date_format` | `%Y%m%d_%H%M%S` | Formato de fecha y hora de generación en el nombre del archivo |
| `export_path` | `~` | Directorio de exportación |

Una configuración inválida (archivo ilegible, YAML inválido, claves no reconocidas, valores inválidos, `export_path` inexistente o sin permiso de escritura) es un error general del proceso. El servicio nunca crea el directorio de exportación. En Docker, `export_path` debe declararse como `/exports` en el `config.yml`, porque `~` apunta a un directorio no persistente del contenedor.

## Ejecución

Los servicios no son procesos permanentes: cada uno se ejecuta, completa su tarea y termina. Solo MongoDB permanece activo. Los servicios se ejecutan mediante contenedores efímeros (`docker compose run --rm`) lanzados desde el `Makefile`.

Los tres servicios son independientes entre sí: el fallo de uno no impide la ejecución de los demás. La única condición compartida es la disponibilidad de la base de datos. `reports` puede ejecutarse mientras los otros servicios están en ejecución.

| Servicio | Modo de ejecución |
|---|---|
| `traffic-collector` | Automática, mediante `crontab` del servidor. Debe ejecutarse una (1) vez por día, en horas de la mañana, de modo que finalice antes de las 00:00. Esta regla es obligatoria. El usuario operador puede reejecutarlo el mismo día: las interfaces con valores crudos del día anterior se omiten, por lo que solo recupera lo faltante. La opción `--force` consulta todas las interfaces activas y reemplaza los datos del día anterior |
| `interface-sync` | Manual, bajo demanda del usuario de operatividad |
| `reports` | Manual, bajo demanda del usuario de operatividad, con `--start YYYY-MM-DD --end YYYY-MM-DD` |

La programación en el `crontab` es responsabilidad del usuario de operatividad y no forma parte del sistema. Tampoco hay bloqueo de ejecuciones simultáneas: el usuario de operatividad no debe ejecutar más de una vez a la vez `interface-sync` ni `traffic-collector`.

### Día anterior
Es la fecha actual en `America/Caracas` menos un día. `traffic-collector` lo calcula una sola vez al inicio y es el mismo para todas las capas, aunque la ejecución cruce la medianoche. Se espera una muestra cada 5 minutos (288 por día).

### Flujo de `traffic-collector`
1. Obtiene las capas existentes. Si la base de datos no está disponible, falla al obtenerlas o no existe ninguna capa, termina con error general del proceso sin realizar peticiones a SCAN.
2. Por cada capa, en secuencia: lee sus interfaces activas (una sola vez), omite las que ya tienen valores crudos, consulta a SCAN, filtra las muestras del día anterior, las valida y las almacena. Cada interfaz se almacena apenas se obtiene y valida.
3. Una interfaz fallida hace fallida su capa. Al llegar al máximo de fallas consecutivas, o ante un error de base de datos al almacenar, se corta el procesamiento de esa capa, se conserva lo ya almacenado y se continúa con la siguiente. Una capa fallida no impide las demás.
4. Al terminar todas las capas, aunque alguna haya fallado, genera el resumen diario de las interfaces con valores crudos del día anterior y sin resumen de ese día. Un resumen ya almacenado no se recalcula, y solo se genera el resumen del día anterior.
5. No hay reintentos de consultas fallidas ni se conservan en disco los archivos `.log` recibidos de SCAN.

### Códigos de salida

Todo servicio debe terminar con código de salida `0` únicamente ante un resultado general exitoso. Cualquier otro resultado debe terminar con código distinto de cero, para que sea detectable desde el `crontab` y el `Makefile`. Esto incluye:

- Errores de ejecución o de conexión.
- Parámetros o configuración inválidos.
- Ausencia de datos requeridos para operar (por ejemplo, `traffic-collector` sin interfaces activas en ninguna capa, o `reports` sin ninguna capa que aporte datos).
- Resultado general fallido por una o más capas, interfaces o resúmenes fallidos.

Una reejecución de `traffic-collector` donde todo se omite termina con código `0`.

## Registro de operaciones (logs)

Cada servicio mantiene sus propios archivos `.log` con el registro de operaciones y errores.

- Los logs son permanentes: se almacenan en un volumen del host (bind mount), de modo que persistan tras la finalización y eliminación del contenedor.
- Los mensajes de cada ejecución se agregan sin eliminar los anteriores.
- Se utiliza el módulo `logging` de la biblioteca estándar, sin dependencias adicionales.
- Los archivos rotan automáticamente para evitar crecimiento ilimitado.
- Cada servicio escribe en su propio directorio de logs, sin compartir archivos con otros servicios.
- `traffic-collector` y `reports` no registran un mensaje por cada interfaz exitosa, solo totales por capa, para limitar el tamaño del log.
- Además del log, `traffic-collector` y `reports` informan el avance y los resultados por terminal.

## Exportación de archivos

Todos los archivos generados por el servicio `reports` se almacenan en la carpeta `exports/`, ubicada en un volumen del host (bind mount) y montada en `/exports`, de modo que persistan tras la finalización y eliminación del contenedor. Ningún otro servicio escribe en esta carpeta.

- Cada ejecución genera como máximo un archivo `.xlsx`, con nombre `<prefix_name>_<fecha según date_format>.xlsx`. La fecha es la de generación en `America/Caracas`; el nombre no incluye el rango. Si ya existe un archivo con el mismo nombre, se sobrescribe. La escritura es atómica: una falla no deja un archivo parcial.
- Una hoja por capa existente con al menos una interfaz incluida. El nombre de la hoja es el de la capa en mayúsculas. Orden: `BORDE`, `BRAS`, `CACHING`, `RAI`, `DINT`, `DIST`, `IXP` y, a continuación, cualquier otra capa existente en orden alfabético ascendente. Una capa sin datos no genera hoja. Si ninguna capa aporta datos, no se genera archivo.
- Columnas, en este orden: `Interfaz`, `In Prom`, `In Max`, `Out Prom`, `Out Max` (Gbps), `Capacidad` (Gbps), `Tipo` (proveedor) y `Uso (%)`.
- Si una capa falla, se exportan las hojas de las demás, pero el resultado general es fallido.
