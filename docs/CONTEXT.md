# Proyecto

ScanBackup es un sistema especializado en la creación de un backup personal del sistema SCAN. Es un sistema que proactivamente realiza peticiones diarias al sistema SCAN para obtener los distintos valores de tráfico de red de todas las interfaces existentes, con la finalidad de poder almacenar en una base de datos dichos valores, para poder tener un respaldo y poder realizar reportes de distintos días.

ScanBackup recolecta, importa, exporta y gestiona datos de tráfico de red provenientes del sistema de monitoreo SCAN de CANTV. 

SCAN es un sistema antiguo de la empresa que muestra los valores de tráfico de todas las interfaces de red, por cada 5min, pero solamente del día anterior. Este sistema se encarga de consultar dicha información diariamente para almacenarlas y poder visualizar la data de días, meses o incluso años anteriores.

# Nombre de las capas de red de SCAN
La información actualmente necesaria es todas las capas del BackBoneIP (BBIP):
- "BORDE", también llamado "Enlaces Internacionales", son las interfaces que se conectan con el mundo.
- "BRAS", también llamado "Agregación", son las interfaces principales que van directamente a la MetroEthernet.
    - "BRAS IP", es la información de las IP activas llegadas a los agregadores.
- "CACHING", son las interfaces de los servidores de Caching.
- "RAI", también llamado "Clientes Dedicados", son las interfaces especializadas para las empresas.
- "DINT", también llamado "Distribución Internet".
- "DIST", también llamado "Distribución Regional".
- "IXP", son interfaces para servicios especiales.

# Características del Sistema
El objetivo de la creación de este sistema se divide en distintas características:

## Peticiones
- Obtener un archivo con el listado todas las interfaces de red existentes en SCAN.
- Realizar peticiones rápidas de tráfico a todas las interfaces existentes en SCAN.

## Almacenamiento
- Almacenamiento del listado de interfaces existentes en el sistema SCAN.
- Almacenamiento de la data cruda del día de todas las interfaces obtenidas de SCAN.
- Almacenamiento de un resumen de la data (promedios) del día de todas las interfaces obtenidas.

## Reportes
- Exportación del listado de interfaces activo.
- Exportación de la data almacenada cruda por capas.
- Exportación de la data resumida por capas.

# Estructura
Para lograr los objetivos del sistema, se ha separado la extracción del listado de enlaces de SCAN, de la obtención de tráfico de dichos enlaces. Es por ello que se tiene:
- `DataBackup`: El sistema encargado de la administración completa de interfaces, su obtención de tráfico y almacenamiento.
- `SourceScrapper`: El sistema encargado de conocer la estructura interna de SCAN para obtener el listado de interfaces disponibles para consultar el tráfico.

# Notas Importantes
Es necesario priorizar la correcta comunicación entre ambas partes, y asegurarse de que el sistema funcione y sea de fácil uso y mantenimiento en contenedores docker. Esto con la finalidad de que el proyecto sea altamente portable, para que su funcionamiento no dependa de un servidor en específico.

Además, es importante que el sistema sea de fácil configuración, y tenga un diseño organizado para la fácil creación de manuales e instructivos técnicos y de usuarios.