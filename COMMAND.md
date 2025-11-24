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
    - [Especificar Fecha para Recolección de Datos](#especificar-fecha-para-recolección-de-datos)
    - [Especificar Capa de BBIP para Recolección de Datos](#especificar-capa-de-bbip-para-recolección-de-datos)
    - [Especificar Fecha para el Procesamiento de Datos](#especificar-fecha-para-el-procesamiento-de-datos)
    - [Especificar Capa de BBIP para el Procesamiento de Datos](#especificar-capa-de-bbip-para-el-procesamiento-de-datos)
    - [Almacenamiento de Datos](#almacenamiento-de-datos)
    - [Especificar Fecha para Almacenamiento de Datos](#especificar-fecha-para-almacenamiento-de-datos)
    - [Especificar Capa de BBIP para Almacenamiento de Datos](#especificar-capa-de-bbip-para-almacenamiento-de-datos)
    - [Forzar la Carga de Toda la Data Recolectada](#forzar-la-carga-de-toda-la-data-recolectada)
    - [Especificar Carga de los Resúmenes Diarios](#especificar-carga-de-los-resúmenes-diarios)
    - [Especificar Fecha para la Carga de los Resúmenes Diarios](#especificar-fecha-para-la-carga-de-los-resúmenes-diarios)
    - [Forzar la Cargar de Todos los Resúmenes Diarios](#forzar-la-cargar-de-todos-los-resúmenes-diarios)
    - [Especificar Capa para Actualizar las Fuentes](#especificar-capa-para-actualizar-las-fuentes)
    - [Construcción de la Base de Datos](#construcción-de-la-base-de-datos)
    - [Destrucción de la Base de Datos](#destrucción-de-la-base-de-datos)
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

### Especificar Fecha para Recolección de Datos
Para recolectar los datos de SCAN de una fecha específica, se debe ejecutar el siguiente comando:
```bash
bash $(pwd)/scanbackup/routines/scanner.sh <FECHA>
```

Donde `<FECHA>` es la fecha del día que se desea recolectar en el formato `YYYY-MM-DD`. 

Por defecto, si no se especifica, se recolectará los datos del día anterior al actual.

### Especificar Capa de BBIP para Recolección de Datos
Para recolectar los datos de SCAN de una capa específica, se debe ejecutar el siguiente comando:
```bash
bash $(pwd)/scanbackup/routines/scanner.sh <FECHA> <LAYER>
```

Donde `<FECHA>` es la fecha del día que se desea recolectar en el formato `YYYY-MM-DD` y `<LAYER>` es la capa de la que se desea recolectar los datos. 

Las capas disponibles son: `BORDE`, `BRAS`, `CACHING`, `RAI`, `IXP`, `IPBRAS`.

Por defecto, si no se especifica, se recolectará los datos de todas las capas del día anterior al actual.

### Especificar Fecha para el Procesamiento de Datos
Para procesar los datos de SCAN de una fecha específica y obtener los promedios diarios, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.routines.daily --date <FECHA>
```

Donde `<FECHA>` es la fecha del día que se desea procesar en el formato `YYYY-MM-DD`. 

Por defecto, si no se especifica, se procesará los datos del día anterior al actual.

### Especificar Capa de BBIP para el Procesamiento de Datos
Para procesar los datos de SCAN de una capa específica y obtener los promedios diarios, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.routines.daily --layer <LAYER>
```

Donde `<LAYER>` es la capa de la que se desea procesar los datos.

Las capas disponibles son: `BORDE`, `BRAS`, `CACHING`, `RAI`, `IXP`, `IPBRAS`.

Por defecto, si no se especifica, se procesará los datos de todas las capas.

### Almacenamiento de Datos
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

### Especificar Fecha para Almacenamiento de Datos
Para almacenar los datos de SCAN de una fecha específica, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater data --date <FECHA>
```

Donde `<FECHA>` es la fecha del día que se desea almacenar en el formato `YYYY-MM-DD`.

> Nota: La bandera `--dev` es válida para combinación.

### Especificar Capa de BBIP para Almacenamiento de Datos
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

### Forzar la Carga de Toda la Data Recolectada
Para subir toda la data recolectada y procesada, sin importar las fechas, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater data --force
```

Esto subirá la data recolectada y procesada de todas las capas de todas las fechas que se obtenga.

> Nota: La bandera `--dev` es válida para combinación.

### Especificar Carga de los Resúmenes Diarios
Para subir solo la data procesada de los resúmenes diarios, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater daily
```

Esto subirá la data procesada de los resúmenes diarios de todas las capas del día anterior al actual.

También se puede ejecutar el comando en modo desarrollo, ejecutando el siguiente comando:
```bash
python3 -m scanbackup.updater daily --dev
```

**IMPORTANTE**: Para esto se debe creado el archivo `.env.development` con las variables de entorno requeridas.

### Especificar Fecha para la Carga de los Resúmenes Diarios
Para subir solo la data procesada de los resúmenes diarios de una fecha específica, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater daily --date <FECHA>
```

Donde `<FECHA>` es la fecha del día que se desea almacenar en el formato `YYYY-MM-DD`.

> Nota: La bandera `--dev` es válida para combinación.

### Forzar la Cargar de Todos los Resúmenes Diarios
Para subir todos los resúmenes diarios, sin importar las fechas, se debe ejecutar el siguiente comando:
```bash
python3 -m scanbackup.updater daily --force
```

Esto subirá los resúmenes diarios de todas las capas de todas las fechas que se obtenga.

> Nota: La bandera `--dev` es válida para combinación.

### Especificar Capa para Actualizar las Fuentes
Para actualizar las fuentes del sistema solo para una capa específica, se debe ejecutar el siguiente comando según la capa deseada:
```bash
python3 -m scanbackup.updater sources --borde 
python3 -m scanbackup.updater sources --bras
python3 -m scanbackup.updater sources --caching
python3 -m scanbackup.updater sources --rai
python3 -m scanbackup.updater sources --ipbras
```

### Construcción de la Base de Datos
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


### Destrucción de la Base de Datos
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

### Generación de Reporte Diario
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

### Generación de Reporte Semanal
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

### Generación de Reporte Quincenal
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

### Generación de Reporte Mensual
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