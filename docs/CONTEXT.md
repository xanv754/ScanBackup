# Proyecto
SCAN-Backup es un sistema desarrollado para obtener la información de tráfico de las distintas interfaces de red monitoreadas diariamente por el sistema SCAN. Dado que SCAN actualmente no conserva un histórico de los valores de tráfico que registra, SCAN-Backup suple dicha necesidad recolectando los valores de tráfico, en periodos de 5 minutos, que SCAN obtiene del día anterior al actual, y almacenándolos para conformar el histórico de tráfico de las interfaces de red. Todo ello tiene como finalidad poder generar reportes de promedios de tráfico por hora o por día, reportes de valores crudos de varios días en conjunto y reportes de tráfico de interfaces de red específicas, para su exportación a un documento destinado a los analistas, consultores o líderes de la coordinación Gestión Producto Red de Datos de CANTV.

SCAN-Backup no monitorea las interfaces en vivo ni realiza consultas a los equipos de red. Toda la información obtenida se extrae exclusivamente de la información que muestra el sistema SCAN. SCAN-Backup obtiene de SCAN la información de las interfaces de red, lo que le permite consultar los valores de tráfico que SCAN obtuvo de dichas interfaces y almacenarlos en la base de datos de SCAN-Backup. Asimismo, no modifica ni altera los valores de tráfico, ni agrega ni elimina interfaces de red declaradas en SCAN.

Dado que SCAN no almacena valores de tráfico de días antiguos, SCAN-Backup inicia su recolección a partir de su puesta en marcha. Las consultas a SCAN se realizan diariamente para obtener toda la información de tráfico del día anterior. El sistema depende de los datos de SCAN; por ello, cualquier cambio, detención o corrupción de SCAN, como sistema base, afectará el correcto funcionamiento de SCAN-Backup o, en el peor de los casos, lo impedirá.

A la fecha de redacción de este documento, el sistema contempla únicamente la recolección de tráfico de todas las capas del BackboneIP de la red de CANTV.

# Estructura del proyecto
El sistema se divide en tres servicios independientes, cada uno con una única responsabilidad:

- **`interface-sync`**: Servicio encargado de obtener, mediante scraping, la lista de interfaces de red existentes en el sistema SCAN y de mantenerla sincronizada en la base de datos. Cada interfaz se registra con su estatus (activa o desincorporada), el cual este servicio actualiza en cada ejecución.
- **`traffic-collector`**: Servicio encargado de respaldar los valores de tráfico de las interfaces. Obtiene de la base de datos la lista de interfaces con estatus activo, consulta a SCAN los valores de tráfico de cada una y los almacena.
- **`reports`**: Servicio encargado de generar reportes de tráfico a partir de los datos almacenados en la base de datos, y de exportarlos a archivos para los usuarios del sistema.

Los servicios no se comunican directamente entre sí. La base de datos, única para todos, es el único punto de integración entre ellos.