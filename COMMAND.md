# Índice
- [Makefile](#makefile)
    - [Configuración del Sistema](#configuración-del-sistema)
    - [Ejecución del Sistema](#ejecución-del-sistema)
    - [Creación de Carpetas](#creación-de-carpetas)
    - [Recolección de Datos de SCAN](#recolección-de-datos-de-scan)
    - [Procesamiento de Datos de SCAN](#procesamiento-de-datos-de-scan)
    - [Recolección y Procesamiento de Datos de SCAN](#recolección-y-procesamiento-de-datos-de-scan)
    - [Almacenamiento de la Data Obtenida](#almacenamiento-de-la-data-obtenida)
    - [Limpieza de Data y Archivos Temporales](#limpieza-de-data-y-archivos-temporales)
    - [Actualización de Fuentes](#actualización-de-fuentes)
- [Interfaz de Línea de Comandos del Sistema](#interfaz-de-línea-de-comandos-del-sistema)
    - [Recolección de Datos Manual](#recolección-de-datos-manual)
        - [Recolección en Día Específico](#recolección-en-día-específico)
        - [Recolección en Capa Específica](#recolección-en-capa-específica)
    - [Procesamiento de Datos Manual](#procesamiento-de-datos-manual)
        - [Procesamiento de Día Específico](#procesamiento-de-día-específico)
        - [Procesamiento de Capa Específica](#procesamiento-de-capa-específica)
    - [Almacenamiento de Datos Manual](#almacenamiento-de-datos-manual)
        - [Almacenamiento de Día Específico](#almacenamiento-de-día-específico)
        - [Almacenamiento de Capa Específica](#almacenamiento-de-capa-específica)
        - [Almacenamiento de Toda la Data Existente](#almacenamiento-de-toda-la-data-existente)
    - [Almacenamiento Único de Data Procesada](#almacenamiento-único-de-data-procesada)
        - [Almacenamiento de Día Específico](#almacenamiento-de-día-específico-1)
        - [Almacenamiento de Toda la Data Existente](#almacenamiento-de-toda-la-data-existente-1)
    - [Actualización de Archivos Fuentes del Sistema](#actualización-de-archivos-fuentes-del-sistema)
        - [Actualización de las Fuentes de una Capa Específica](#actualización-de-las-fuentes-de-una-capa-específica)
    - [Operaciones en la Base de Datos](#operaciones-en-la-base-de-datos)
        - [Construcción de la Base de Datos](#construcción-de-la-base-de-datos)
        - [Destrucción de la Base de Datos](#destrucción-de-la-base-de-datos)
    - [Generación de Reportes](#generación-de-reportes)
        - [Generación de Reporte Diario](#generación-de-reporte-diario)
        - [Generación de Reporte Semanal](#generación-de-reporte-semanal)
        - [Generación de Reporte Quincenal](#generación-de-reporte-quincenal)
        - [Generación de Reporte Mensual](#generación-de-reporte-mensual)

# Comandos
## Makefile
El sistema cuenta con un archivo `Makefile` que contiene toda la información necesaria para ejecutar las rutinas de manera automática, y realizar las operaciones necesarias para el correcto funcionamiento del sistema.

### Configuración del Sistema
Para instanciar correctamente el sistema, se debe ejecutar el siguiente comando:
```bash
make setup
```

Esto creará las carpetas necesarias para el funcionamiento del sistema, creará la base de datos e instalará las dependencias de Python.

### Ejecución del Sistema
Para poder ejecutar el sistema, se debe ejecutar el siguiente comando:
```bash
make run
```

Esto capturará la data del día anterior, procesará los datos y los almacenará en la base de datos del sistema.

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
make run-dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

### Creación de Carpetas
Si se necesita solo crear las carpetas requeridas para el funcionamiento del sistema, se debe ejecutar el siguiente comando:
```bash
make setup-files
```

### Recolección de Datos de SCAN
Si se necesita solo recolectar los datos de SCAN, se debe ejecutar el siguiente comando:
```bash
make run-scan
```

Más información sobre las rutinas de recolección de datos se encuentra en la sección [Recolección de Datos](./DOCUMENTATION.md#recolección-de-datos).

### Procesamiento de Datos de SCAN
Si se necesita solo procesar los datos de SCAN y obtener la data correspondiente a los promedios diarios, se debe ejecutar el siguiente comando:
```bash
make run-daily
```

Más información sobre las rutinas de procesamiento de datos se encuentra en la sección [Procesamiento de Datos](./DOCUMENTATION.md#procesamiento-de-datos).

### Recolección y Procesamiento de Datos de SCAN
Si se necesita solo recolectar y procesar los datos de SCAN, se debe ejecutar el siguiente comando:
```bash
make run-base
```

### Almacenamiento de la Data Obtenida
Si se necesita solo almacenar la data existente temporal en el sistema, se debe ejecutar el siguiente comando:
```bash
make run-updater
```

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
make run-updater-dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

### Limpieza de Data y Archivos Temporales
Si se necesita limpiar las carpetas donde se almacenan temporalmente la data obtenida de SCAN antes de guardarse en la base de datos, se debe ejecutar el siguiente comando:
```bash
make clean-data
```

> *Nota*: Tome precaución de utilizar este comando antes de que la data se haya almacenado previamente en la base de datos.

### Actualización de Fuentes
Si se requiere actualizar los archivos fuentes que utiliza el sistema para recolectar la información de SCAN puede ejecutar el comando:
```bash
make updater-sources
```

**IMPORTANTE**: Tenga en cuenta que una vez ejecutado el comando, se recomienda la revisión manual de los archivos, ya que el sistema pudiera no encontrar alguna información de las interfaces en SCAN, dejando así valores por defecto para su modificación manual.

## Interfaz de Línea de Comandos del Sistema
Para la ejecución de los comandos descritos a continuación, se recuerda la activación del entorno virtual.

### Recolección de Datos Manual
Para realizar la ejecución manual para recolectar los datos de SCAN, se debe ejecutar el siguiente comando:
```bash
bash $(pwd)/scanbackup/routines/scanner.sh 
```

Esto iniciará la ejecución de consulta de tráfico de las interfaces especificas en los archivos fuentes del sistema. Para más información, revisar: [Archivos Fuentes del Sistema](./DOCUMENTATION.md#archivos-fuentes-del-sistema).

#### Recolección en Día Específico
Si se requiere especificar una fecha para recolectar información, se debe ejecutar el siguiente comando:
```bash
bash $(pwd)/scanbackup/routines/scanner.sh <FECHA>
```

Donde `<FECHA>` es la fecha del día que se desea recolectar en el formato `YYYY-MM-DD`. Por defecto, si no se especifica, se recolectará los datos del día anterior al actual.

#### Recolección en Capa Específica
Si se requiere especificar una capa para recolectar información solo de esa capa, se debe ejecutar el siguiente comando:
```bash
bash $(pwd)/scanbackup/routines/scanner.sh <FECHA> <LAYER>
```

Donde `<FECHA>` es la fecha del día que se desea recolectar en el formato `YYYY-MM-DD` y `<LAYER>` es la capa de la que se desea recolectar los datos. 

> **Nota**: Las capas disponibles son: `BORDE`, `BRAS`, `CACHING`, `RAI`, `IXP`, `IPBRAS`. Por defecto, si no se especifica, se recolectará los datos de todas las capas del día anterior al actual.

### Procesamiento de Datos Manual
Para realizar la ejecución manual para procesar los datos recolectados de SCAN, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.routines.daily
```

#### Procesamiento de Día Específico
Si se requiere especificar una fecha solo para procesar la data recolectada de SCAN que pertenezca a ese día, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.routines.daily --date <FECHA>
```

Donde `<FECHA>` es la fecha del día que se desea procesar en el formato `YYYY-MM-DD`. Por defecto, si no se especifica, se procesará los datos del día anterior al actual.

#### Procesamiento de Capa Específica
Si se requiere especificar una capa solo para procesar la data recolectada de SCAN que pertenezca a esa capa, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.routines.daily --layer <LAYER>
```

Donde `<LAYER>` es la capa de la que se desea procesar los datos.

> **Nota**: Las capas disponibles son: `BORDE`, `BRAS`, `CACHING`, `RAI`, `IXP`, `IPBRAS`. Por defecto, si no se especifica, se procesará los datos de todas las capas.

### Almacenamiento de Datos Manual
Para almacenar toda la data recolectada y procesada, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater data
```

Esto almacenará la data recolectada y procesada de todas las capas del día anterior al actual.

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
python3 -m scanbackup.updater data --dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

#### Almacenamiento de Día Específico
Para almacenar los datos de SCAN de una fecha específica, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater data --date <FECHA>
```

Donde `<FECHA>` es la fecha del día que se desea almacenar en el formato `YYYY-MM-DD`.

> Nota: La bandera `--dev` es válida para combinación.

#### Almacenamiento de Capa Específica
Para almacenar los datos de SCAN de una capa específica, se debe ejecutar el siguiente comando según la capa deseada:
```bash
python3 -m scanbackup.updater data --borde 
python3 -m scanbackup.updater data --bras
python3 -m scanbackup.updater data --caching
python3 -m scanbackup.updater data --rai
python3 -m scanbackup.updater data --ixp
python3 -m scanbackup.updater data --ipbras
```

> Nota: La bandera `--date` y `--dev` es válida para combinación.

#### Almacenamiento de Toda la Data Existente
Para subir toda la data recolectada y procesada, sin importar las fechas, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater data --force
```

Esto subirá la data recolectada y procesada de todas las capas de todas las fechas que se obtenga.

> Nota: La bandera `--dev` es válida para combinación.

### Almacenamiento Único de Data Procesada
Para subir solo la data procesada de los resúmenes de promedios de tráfico diarios, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater daily
```

Esto subirá la data procesada de los resúmenes diarios de todas las capas del día anterior al actual.

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
python3 -m scanbackup.updater daily --dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

#### Almacenamiento de Día Específico
Para subir solo la data procesada de los resúmenes diarios de una fecha específica, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater daily --date <FECHA>
```

Donde `<FECHA>` es la fecha del día que se desea almacenar en el formato `YYYY-MM-DD`.

> Nota: La bandera `--dev` es válida para combinación.

#### Almacenamiento de Toda la Data Existente
Para subir todos los resúmenes diarios, sin importar las fechas, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater daily --force
```

Esto subirá los resúmenes diarios de todas las capas de todas las fechas que se obtenga.

> Nota: La bandera `--dev` es válida para combinación.

### Actualización de Archivos Fuentes del Sistema
> **Nota**: Se deben especificar las variables de entorno opcionales para el correcto funcionamiento de este apartado. Véase: [Otras Variables de Entorno](./README.md#otras-variables-de-entorno).

Para actualizar de forma automática los archivos fuentes del sistema (también válido para crear los archivos fuentes del sistema por primera vez), se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater sources
```

Esto realizará un *web scrapping* en el sistema SCAN para obtener todas las interfaces de las distintas capas del sistema para su consulta.

**IMPORTANTE**: Este módulo puede verse afectado con un cambio considerable en la estructura de la página de SCAN. Se recomienda ejecutar este comando con precaución. *NO SE AUTOMATICE DIARIAMENTE*. También debe tener en cuenta que, en algunos casos, pudiera faltar la capacidad de las interfaces si no se logra obtener. Se debe escribir la misma manualmente en el archivo.

**SIEMPRE REALICE UNA REVISIÓN DE LOS ARCHIVOS FUENTES UNA VEZ FINALIZADA LA AUTOMATIZACIÓN.**

#### Actualización de las Fuentes de una Capa Específica
Para actualizar las fuentes del sistema solo para una capa específica, se debe ejecutar el siguiente comando según la capa deseada:
```bash
python3 -m scanbackup.updater sources --borde 
python3 -m scanbackup.updater sources --bras
python3 -m scanbackup.updater sources --caching
python3 -m scanbackup.updater sources --rai
python3 -m scanbackup.updater sources --ipbras
```

### Operaciones en la Base de Datos
#### Construcción de la Base de Datos
Para construir la base de datos, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.database start
```

Esto creará la base de datos con los esquemas e índices correspondientes.

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
python3 -m scanbackup.database start --dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

#### Destrucción de la Base de Datos
Para destruir la base de datos, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.database drop
```

Esto eliminará toda la información de la base de datos de manera irreversible.

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
python3 -m scanbackup.database drop --dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

### Generación de Reportes
#### Generación de Reporte Diario
Para generar el reporte diario, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup diario
```

Esto generará el reporte del día anterior y lo exportará en un archivo .xlsx llamado `Data_Diario_BBIP.xlsx`.

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
python3 -m scanbackup diario --dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

Además, se puede especificar la fecha para el que se desea generar el reporte, con el siguiente comando:
```bash
python3 -m scanbackup diario --date <FECHA>
```

Donde `<FECHA>` es la fecha del día que se desea generar el reporte en el formato `YYYY-MM-DD`.

> Nota: La bandera `--dev` es válida para combinación.

#### Generación de Reporte Semanal
Para generar el reporte semanal, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup semanal
```

Esto generará un reporte con el promedio de datos desde el lunes de la semana pasada hasta el domingo de la semana cursando. Este reporte será exportado un archivo .xlsx llamado `Data_Semanal_BBIP.xlsx`.

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
python3 -m scanbackup semanal --dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

Además, se puede especificar la fecha para el que se desea generar el reporte, con el siguiente comando:
```bash
python3 -m scanbackup semanal --literal
```

Esto generará un reporte desde de la semana contando los 7 días hacia atrás iniciando desde el día actual.

> Nota: La bandera `--dev` es válida para combinación.

#### Generación de Reporte Quincenal
Para generar el reporte quincenal, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup quincenal
```

Esto generará un reporte con el promedio de datos desde el primer día del mes hasta el día 15 del mes. Este reporte será exportado un archivo .xlsx llamado `Data_Quincenal_BBIP.xlsx`.

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
python3 -m scanbackup quincenal --dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

Además, se puede especificar la fecha para el que se desea generar el reporte, con el siguiente comando:
```bash
python3 -m scanbackup quincenal --literal
```

Esto generará un reporte desde de la quincena contando los 15 días hacia atrás iniciando desde el día actual.

> Nota: La bandera `--dev` es válida para combinación.

#### Generación de Reporte Mensual
Para generar el reporte mensual, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup mensual
```

Esto generará un reporte con el promedio de datos desde el primer día del mes hasta el día 30 del mes. Este reporte será exportado un archivo .xlsx llamado `Data_Mensual_BBIP.xlsx`.

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
python3 -m scanbackup mensual --dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

Además, se puede especificar la fecha para el que se desea generar el reporte, con el siguiente comando:
```bash
python3 -m scanbackup mensual --literal
```

Esto generará un reporte desde de la mensual contando los 30 días hacia atrás iniciando desde el día actual.

> Nota: La bandera `--dev` es válida para combinación.