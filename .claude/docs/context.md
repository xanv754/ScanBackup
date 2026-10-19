# SCAN-Backup

## Objetivo y Alcance
SCAN-Backup es un sistema desarrollado para obtener la información de tráfico de las distintas interfaces de red monitoreadas diariamente por el sistema SCAN. Dado que SCAN actualmente no conserva un histórico de los valores de tráfico que registra, SCAN-Backup suple dicha necesidad recolectando los valores de tráfico, en periodos de 5 minutos, que SCAN obtiene del día anterior al actual, y almacenándolos para conformar el histórico de tráfico de las interfaces de red. Todo ello tiene como finalidad poder generar reportes de promedios de tráfico por hora o por día, reportes de valores crudos de varios días en conjunto y reportes de tráfico de interfaces de red específicas, para su exportación a un documento destinado a los analistas, consultores o líderes de la coordinación Gestión Producto Red de Datos de CANTV.

SCAN-Backup no monitorea las interfaces en vivo ni realiza consultas a los equipos de red. Toda la información obtenida se extrae exclusivamente de la información que muestra el sistema SCAN. SCAN-Backup obtiene de SCAN la información de las interfaces de red, lo que le permite consultar los valores de tráfico que SCAN obtuvo de dichas interfaces y almacenarlos en la base de datos de SCAN-Backup. Asimismo, no modifica ni altera los valores de tráfico, ni agrega ni elimina interfaces de red declaradas en SCAN.

Dado que SCAN no almacena valores de tráfico de días antiguos, SCAN-Backup inicia su recolección a partir de su puesta en marcha. Las consultas a SCAN se realizan diariamente para obtener toda la información de tráfico del día anterior. El sistema depende de los datos de SCAN; por ello, cualquier cambio, detención o corrupción de SCAN, como sistema base, afectará el correcto funcionamiento de SCAN-Backup o, en el peor de los casos, lo impedirá.

A la fecha de redacción de este documento, el sistema contempla únicamente la recolección de tráfico de todas las capas del BackboneIP de la red de CANTV.

## Estructura del proyecto
El sistema se divide en tres servicios independientes, cada uno con una única responsabilidad:

- **`interface-sync`**: Servicio encargado de obtener, mediante scraping, la lista de interfaces de red existentes en el sistema SCAN y de mantenerla sincronizada en la base de datos. Cada interfaz se registra con su estatus (activa o desincorporada), el cual este servicio actualiza en cada ejecución.
- **`traffic-collector`**: Servicio encargado de respaldar los valores de tráfico de las interfaces. Obtiene de la base de datos la lista de interfaces con estatus activo, consulta a SCAN los valores de tráfico de cada una y los almacena.
- **`reports`**: Servicio encargado de generar reportes de tráfico a partir de los datos almacenados en la base de datos, y de exportarlos a archivos para los usuarios del sistema.

Los servicios no se comunican directamente entre sí. La base de datos, única para todos, es el único punto de integración entre ellos.

## Tecnologías

Las tecnologías listadas a continuación son las definidas para el sistema, aunque pueden a lo largo del desarrollo añadirse nuevas depedencias según sea la necesidad. Estas son las básicas al comenzar.

### Lenguaje y entorno

| Tecnología | Uso |
|---|---|
| Python 3.13 | Lenguaje de desarrollo de los tres servicios |
| pip | Instalación de dependencias; cada servicio es un paquete con su propio `pyproject.toml` |

Cada servicio se define como un paquete Python independiente, con su propio `pyproject.toml` que declara sus dependencias y su punto de entrada CLI. Backend de build: `setuptools`.

### Persistencia

| Tecnología | Uso |
|---|---|
| MongoDB | Base de datos única, compartida por todos los servicios |
| PyMongo | Driver de conexión a MongoDB (acceso síncrono) |

### Comunicación con SCAN

| Tecnología | Uso | Servicio |
|---|---|---|
| requests | Peticiones HTTP hacia SCAN | `interface-sync`, `traffic-collector` |
| BeautifulSoup | Scraping del HTML de SCAN | `interface-sync` |

### Configuración e interfaz

| Tecnología | Uso |
|---|---|
| PyYAML | Lectura de archivos de configuración (`safe_load`) |
| click | Interfaz de línea de comandos de cada servicio |

Los secretos (credenciales de base de datos y de SCAN) se proporcionan mediante variables de entorno, no mediante los archivos de configuración.

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

## Ejecución

Los servicios no son procesos permanentes: cada uno se ejecuta, completa su tarea y termina. Solo MongoDB permanece activo. Los servicios se ejecutan mediante contenedores efímeros (`docker compose run --rm`) lanzados desde el `Makefile`.

Los tres servicios son independientes entre sí: el fallo de uno no impide la ejecución de los demás. La única condición compartida es la disponibilidad de la base de datos.

| Servicio | Modo de ejecución |
|---|---|
| `traffic-collector` | Automática, mediante `crontab` del servidor. Debe ejecutarse una (1) vez por día. Esta regla es obligatoria |
| `interface-sync` | Manual, bajo demanda del usuario de operatividad |
| `reports` | Manual, bajo demanda del usuario de operatividad |

La programación en el `crontab` es responsabilidad del usuario de operatividad y no forma parte del sistema.

### Códigos de salida

Todo servicio debe terminar con código de salida `0` únicamente ante una ejecución exitosa. Cualquier otro resultado debe terminar con código distinto de cero, para que sea detectable desde el `crontab` y el `Makefile`. Esto incluye:

- Errores de ejecución o de conexión.
- Ausencia de datos requeridos para operar (por ejemplo, `traffic-collector` sin interfaces activas en la base de datos).

## Registro de operaciones (logs)

Cada servicio mantiene sus propios archivos `.log` con el registro de operaciones y errores.

- Los logs son permanentes: se almacenan en un volumen del host (bind mount), de modo que persistan tras la finalización y eliminación del contenedor.
- Se utiliza el módulo `logging` de la biblioteca estándar, sin dependencias adicionales.
- Los archivos rotan automáticamente para evitar crecimiento ilimitado.
- Cada servicio escribe en su propio directorio de logs, sin compartir archivos con otros servicios.

## Exportación de archivos

Todos los archivos generados por el servicio `reports` se almacenan en la carpeta `exports/`, ubicada en un volumen del host (bind mount), de modo que persistan tras la finalización y eliminación del contenedor. Ningún otro servicio escribe en esta carpeta.