# Sistema de Gestión de Red de Datos
Un sistema diseñado para la recolección de datos de tráfico de todas las interfaces de la red, procesamiento de la data y generación de distintos reportes para el análisis de la coordinación CPGRD.

## Índice
- [Requerimientos](#requerimientos)
    - [Variables de Entorno](#variables-de-entorno)
    - [Variables en Shell](#variables-en-shell)
    - [Instalación de dependencias](#instalación-de-dependencias)
- [Ejecución de rutinas](#ejecución-de-rutinas)
    - [Recolección de datos](#recolección-de-datos)
    - [Procesamiento de datos](#procesamiento-de-datos)
    - [Almacenamiento de datos](#almacenamiento-de-datos)
- [Inicio y Mantenimiento del sistema](#inicio-y-mantenimiento-del-sistema)
    - [Captura de Data](#captura-de-data)
    - [Inicialización del Sistema](#inicialización-del-sistema)
    - [Programación de Tareas](#programación-de-tareas)
    - [Logs](#logs)
- [Interfaz de Línea de Comandos](#interfaz-de-línea-de-comandos)
    - [Base de Datos](#base-de-datos)
        - [Inicializar la base de datos](#crear-la-base-de-datos)
        - [Eliminación de la base de datos](#borrar-la-base-de-datos)
    - [Generación de Reportes](#generación-de-reportes)
        - [Reporte diario](#generar-el-reporte-diario)
        - [Reporte semanal](#generar-el-reporte-semanal)
        - [Reporte quincenal](#generar-el-reporte-quincenal)
        - [Reporte mensual](#generar-el-reporte-mensual)
    - [Actualización del sistema](#actualización-del-sistema)
        - [Carga de data](#actualización-del-sistema)
            - [Almacenamiento de data de un día específico](#almacenamiento-de-data-de-un-día-específico)
            - [Carga de todos los datos obtenidos](#carga-de-todos-los-datos-obtenidos)
        - [Carga de reportes diarios](#almacenamiento-único-de-los-reportes-diarios)
            - [Almacenamiento de reporte diario de un día específico](#almacenamiento-de-reporte-diario-de-un-día-específico)
            - [Carga de todos los reportes diarios obtenidos](#carga-de-todos-los-reportes-diarios-obtenidos)
    - [Actualización de las fuentes de enlaces del sistema](#actualización-de-las-fuentes-de-enlaces-del-sistema)
        - [Actualización de las fuentes de enlaces para todas las capas](#actualización-de-las-fuentes-de-enlaces-para-todas-las-capas)
        - [Actualización de las fuentes de enlaces para la capa `Borde`](#actualización-de-las-fuentes-de-enlaces-para-la-capa-borde)
        - [Actualización de las fuentes de enlaces para la capa `Bras`](#actualización-de-las-fuentes-de-enlaces-para-la-capa-bras)
        - [Actualización de las fuentes de enlaces para la capa `Caching`](#actualización-de-las-fuentes-de-enlaces-para-la-capa-caching)
        - [Actualización de las fuentes de enlaces para la capa `Rai`](#actualización-de-las-fuentes-de-enlaces-para-la-capa-rai)
- [Pruebas unitarias](#pruebas-unitarias)

------------------------------------------------------------------

# Documentación 
- Para ver la documentación de los diagramas, revisa: [diagramas](https://drive.google.com/file/d/1OHpYc9LDjmO_SAFFDzrM-Qdf7UrZxNz0/view?usp=sharing).

**IMPORTANTE:** Antes de realizar cualquier operación o modificación del sistema, se recomienda leer toda la documentación de este documento para entender el funcionamiento del sistema y sus procedimientos.

# Requerimientos
## Variables de Entorno
El sistema require un archivo `.env.production` o `.env` con las siguientes variables de entorno:

```bash
URI_MONGO="mongodb://user:password@server:port/name_database"
SCAN_USERNAME="username"
SCAN_PASSWORD="password"
SCAN_URL_BORDE_HW="url" # Página principal de los enlaces
SCAN_URL_BORDE_CISCO="url" # Página principal de los enlaces
SCAN_URL_BRAS="url" # Página principal de los enlaces
SCAN_URL_CACHING="url" # Página principal de los enlaces
SCAN_URL_RAI_HW="url" # Página principal de los enlaces
SCAN_URL_RAI_ZTE="url" # Página principal de los enlaces
```
> *Nota*: Para la carga de variables de entorno en modo desarrollador se debe tener el archivo `.env.development` y especificar la opción en los comandos correspondientes.

## Variables en Shell
Además, el sistema requiere que se añadan las siguiente variables a nuestro archivo de shell (`.bashrc` o `.zshrc`):
```bash
export HOMEPROJECT="/home/SystemCGPRD" # Debe reemplazarse por la ruta del directorio del sistema
export USERSCAN="usuario" # Debe reemplazarse por el usuario
export PASSWORDSCAN="contraseña" # Debe reemplazarse por la contraseña
```
> *Nota:* Esto es importante para el correcto funcionamiento de la captura de data.

## Instalación 
El sistema cuenta con un archivo `pyproject.toml` que contiene toda la información necesaria para instalar el sistema. Para instalar el sistema, se debe ejecutar el siguiente comando:
```bash
pip install -e .
```

Se puede instalar manualmente de esta forma o con el [inicializador del sistema](#inicialización-del-sistema).

# Rutinas de Ejecución
El sistema se encarga de recolectar la información del tráfico en datos de cada 5 minutos de todas las interfaces de la red. Esta data, una vez obtenida, es procesada y almacenada en la base de datos del sistema.

El sistema tiene un orden estricto para dicha operación: recolección, procesamiento y almacenamiento de los datos. Esto se logra mediante el correcto orden de ejecución de las rutinas. Las rutinas se encuentran en la carpeta `routines/`.

## Recolección de datos
Para recolectar los datos de SCAN, se debe ejecutar el siguiente comando:
```bash
bash systemgrd/routines/scan.sh
```

Esto recolectará los datos de tráfico de SCAN del día anterior de todas las interfaces especificadas en el directorio `sources/SCAN`. Todo el tráfico obtenido está en base a intervalos de cinco minutos. La información obtenida se alojará en el directorio `data/SCAN` según la capa que corresponda. Dicha carpeta debe encontrarse fuera de la carpeta `systemgrd/`.

## Procesamiento de datos
Para procesar los datos de SCAN y obtener la data correspondiente al reporte diario, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd.routines.diario
```

Esto procesará los datos de SCAN del día anterior, y los almacenará en el directorio `data/SCAN/Reportes-Diarios` según la capa que corresponda. Dicha carpeta debe encontrarse fuera de la carpeta `systemgrd/`.

## Almacenamiento de datos
Para almacenar los datos de SCAN, se debe ejecutar el siguiente comando del módulo `updater`:
```bash
python -m systemgrd.updater data
```

Este módulo se encuentra en la carpeta `updater/`. Se encarga de cargar los datos de SCAN en la base de datos del sistema.
> Nota: Para más información de los comandos del módulo `updater`, véase la sección [Actualización del sistema](#actualización-del-sistema).


# Inicio y Mantenimiento del sistema
## Captura de Data
Para poder realizar la captura de data, es necesario poder proporcionarles los links para consultar los datos. Estos links deben estar en un archivo `.txt` en el directorio `sources/SCAN/`. Dicha carpeta debe encontrarse fuera de la carpeta `systemgrd/`.

Estos links deben estar separados por las capas del sistema, con el siguiente formato:
```
link-de-acceso nombre-de-la-interfaz capacidad-de-la-interfaz tipo-de-la-interfaz
```

## Inicialización del Sistema
El sistema almacena y busca datos en carpetas específicas creadas especialmente para el sistema. Además, el sistema requiere que se crean la base de datos con sus colecciones correspondientes. Eso sin contar que el sistema requiere las dependencias de Python previamente mencionadas. Para poder realizar todas esas operaciones correctamente, se puede ejecutar el siguiente comando:
```bash
make setup
```

Este comando creará las carpetas necesarias para el funcionamiento del sistema, creará la base de datos y instalará las dependencias de Python.

## Actualización de las fuentes
Para actualizar o obtener la base de las fuentes de los enlaces necesarios para el funcionamiento del sistema, se debe ejecutar el siguiente comando:
```bash
make sources
```

Este comando actualizará las fuentes de los enlaces y los almacenará en el directorio `sources/SCAN/` en la capa correspondiente. Esto se refiere a que, realizando un web scrapping de la información en SCAN sobre las interfaces de las capas, se obtienen las fuentes de los enlaces existentes (con sus otros valores necesarios) para la correcta extracción de datos.

Cabe destacar que, en dichas fuentes, no hay seguridad de que se obtengan las capacidades correctas según el negocio de la empresa, por lo que se debe revisar manualmente las fuentes obtenidas para el correcto funcionamiento del actualizador de la data de SCAN. El actualizador de las fuentes de SCAN solo agrega o elimina interfaces en los archivos de la carpeta `sources/SCAN/`, pero no modifica información de las capacidade de las interfaces ya registradas. Esto con el fin de no dañar los valores de registradas.

Si no es posible obtener la capacidad de una interfaz, por defecto se colocará un valor absurdo para su identificación (101010101010101010101010101010101010101).

Por ello **no se recomienda ejecutar en automático el actualizador de las fuentes todos los días**. Siempre se debe revisar los valores extraídos de las capas.

## Ejecución del Sistema
Para poder ejecutar el sistema, se debe ejecutar el siguiente comando:
```bash
make run
```

Este comando capturará la data del día anterior, procesará los datos y los almacenará en la base de datos del sistema.

## Limpieza de Datos
Para limpiar los archivos de datos capturados, se debe ejecutar el siguiente comando:
```bash
make clean-data
```

Este comando eliminará todos los data capturada sin afectar a la base de datos.

## Programación de Tareas
Para la correcta ejecución de las rutinas diariamente, se debe configurar el sistema para que se ejecuten automáticamente. Para ello se debe añadir al crontab del sistema el siguiente comando:
```bash
export HOMEPROJECT="/home/user/SystemCGPRD" # Debe reemplazarse por la ruta del directorio del sistema
export USERSCAN="usuario" # Debe reemplazarse por el usuario
export PASSWORDSCAN="contraseña" # Debe reemplazarse por la contraseña

00 04 * * * bash /home/user/SystemCGPRD/systemgrd/routines/scan.sh
00 07 * * * /home/user/SystemCGPRD/.venv/bin/python -m systemgrd.routines.diario
30 07 * * * /home/user/SystemCGPRD/.venv/bin/python -m systemgrd.updater data
```
o 
```bash
export HOMEPROJECT="/home/user/SystemCGPRD" # Debe reemplazarse por la ruta del directorio del sistema
export USERSCAN="usuario" # Debe reemplazarse por el usuario
export PASSWORDSCAN="contraseña" # Debe reemplazarse por la contraseña

00 04 * * * cd $HOMEPROJECT && /usr/bin/make run
```

## Logs
El sistema lleva un registros de logs en el directorio `data/logs/`. Estos logs cuentan con un formato específico para facilitar su lectura. Cada operación que ejecuta el sistema se registra en dichos archivos. Dicha carpeta debe encontrarse fuera de la carpeta `systemgrd/`.


# Interfaz de Línea de Comandos
## Base de Datos
El módulo `database` contiene las funciones para la manipulación de la base de datos. Este módulo se encuentra en la carpeta `database/`.

Puede leer la información sobre los comandos disponibles ejecutando:
```bash
python -m systemgrd.database --help
``` 

### Crear la base de datos
Para crear una nueva base de datos, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd.database start
```

Esto creará la base de datos del sistema, así como todas las colecciones necesarias con esquemas e índices correspondientes.

#### Opciones Extras
Si se desea crear la base de datos en modo desarrollo, cargando las variables de desarrollo, utilice la bandera `--dev` para que el sistema cargue las variables del archivo `.env.development`:
```bash
python -m systemgrd.database start --dev
```

Si se desea crear la base de datos en modo de pruebas, cargando las variables de pruebas, utilice la bandera `--test` para que el sistema cargue las variables del archivo `.env.testing`:
```bash
python -m systemgrd.database start --test
```

### Borrar la base de datos
Para borrar la base de datos, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd.database drop
```

Esto eliminará toda la información de la base de datos de manera irreversible. Se debe tener precaución al utilizar este comando.

#### Opciones Extras
Si se desea borrar la base de datos en modo desarrollo, cargando las variables de desarrollo, utilice la bandera `--dev` para que el sistema cargue las variables del archivo `.env.development`:
```bash
python -m systemgrd.database drop --dev
```

Si se desea borrar la base de datos en modo de pruebas, cargando las variables de pruebas, utilice la bandera `--test` para que el sistema cargue las variables del archivo `.env.testing`:
```bash
python -m systemgrd.database drop --test
```

## Generación de Reportes
El módulo `reports` contiene las funciones para la generación de reportes. Estos reportes se encuentran en el mismo directorio que el sistema, en la carpeta `reports/`.

Puede leer la información sobre los comandos disponibles ejecutando:
```bash
python -m systemgrd --help
```
o 
```bash
python systemgrd/__main__.py
```

### Generar el reporte diario
Para generar el reporte diario, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd diario
```

Esto obtendrá el reporte del día anterior y lo exportará en un archivo .xlsx llamado `Resumen_Diario.xlsx`. 
> *Nota:* La ubicación predeterminada es la carpeta de descargas del sistema. Si no se encuentra dicha carpeta, se dejará el archivo en el home del usuario.

### Generar el reporte semanal
Para generar el reporte semanal, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd semanal
```

Esto generará un reporte con el promedio de datos desde el lunes de la semana pasada hasta el domingo de la semana cursando. Este reporte será exportado un archivo .xlsx llamado `Resumen_Semanal.xlsx`. 
> *Nota:* La ubicación predeterminada es la carpeta de descargas del sistema. Si no se encuentra dicha carpeta, se dejará el archivo en el home del usuario.

#### Opciones Extras
Si se desea generar un reporte semanal con la data exacta de 7 días hacia atrás, es decir, contando desde el día anterior a la fecha en la que se está generando el reporte hasta 7 días atrás, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd semanal --literal
```

### Generar el reporte quincenal
Para generar el reporte quincenal, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd quincenal
```

Esto generará un reporte con el promedio de datos desde el primer día del mes hasta el día 15 del mes (solo promediará los días en los que se obtenga información). Este reporte será exportado un archivo .xlsx llamado `Resumen_Quincenal.xlsx`. 
> *Nota:* La ubicación predeterminada es la carpeta de descargas del sistema. Si no se encuentra dicha carpeta, se dejará el archivo en el home del usuario.

#### Opciones Extras
Si se desea generar un reporte quincenal con la data exacta de 15 días hacia atrás, es decir, contando desde el día anterior a la fecha en la que se está generando el reporte, hasta 15 días atrás (sin importar que se pueda obtener data del mes pasado), se debe ejecutar el siguiente comando:
```bash
python -m systemgrd quincenal --literal
```

### Generar el reporte mensual
Para generar el reporte mensual, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd mensual
```

Esto generará un reporte con el promedio de datos desde el primer día del mes hasta el día 30 del mes (solo promediará los días en los que se obtenga información). Este reporte será exportado un archivo .xlsx llamado `Resumen_Mensual.xlsx`. 
> *Nota:* La ubicación predeterminada es la carpeta de descargas del sistema. Si no se encuentra dicha carpeta, se dejará el archivo en el home del usuario.

#### Opciones Extras
Si se desea generar un reporte mensual con la data exacta de 30 días hacia atrás, es decir, contando desde el día anterior a la fecha en la que se está generando el reporte, hasta 30 días atrás (sin importar que se pueda obtener data del mes pasado), se debe ejecutar el siguiente comando:
```bash
python -m systemgrd mensual --literal
```

## Actualización del sistema
Puede leer la información sobre los comandos disponibles ejecutando:
```bash
python -m systemgrd.updater --help
```

### Almacenamiento de datos
Para almacenar los datos de SCAN, se debe ejecutar el siguiente comando del módulo `updater`:
```bash
python -m systemgrd.updater data
```

Este módulo se encuentra en la carpeta `updater/`. Se encarga de cargar los datos de SCAN en la base de datos del sistema.

#### Opciones Extras
#### Almacenamiento de data de un día específico
Si se tiene recolectado y procesado la data de un día distinto al día anterior, se puede mandar a almacenar con el siguiente comando:
```bash
python -m systemgrd.updater data --date yyyy-mm-dd
```

Donde `yyyy-mm-dd` es la fecha del día que se desea cargar escrito en dicho formato.

#### Carga de todos los datos obtenidos
Si se desea cargar todos los datos recolectados y procesados, indistintamente de la diferencia de fechas que puede contener los archivos, se puede mandar a cargar con el siguiente comando:
```bash
python -m systemgrd.updater data --force
```

Esto cargará todos los datos que se encuentren en los archivos en los directorios correspondientes.

### Almacenamiento único de los reportes diarios
Si se desea solo almacenar los reportes diarios que se tienen procesados, se puede mandar a almacenar con el siguiente comando:
```bash
python -m systemgrd.updater daily
```

#### Opciones Extras
#### Almacenamiento de reporte diario de un día específico
Si se tiene procesado la data del reporte diario de un día distinto al día anterior, se puede mandar a almacenar con el siguiente comando:
```bash
python -m systemgrd.updater daily --date yyyy-mm-dd
```

Donde `yyyy-mm-dd` es la fecha del día que se desea cargar escrito en dicho formato.

#### Carga de todos los reportes diarios obtenidos
Si se desea cargar todos los datos procesados de los reportes diarios, indistintamente de la diferencia de fechas que puede contener los archivos, se puede mandar a cargar con el siguiente comando:
```bash
python -m systemgrd.updater daily --force
```

Esto cargará todos los datos que se encuentren en los archivos en los directorios correspondientes.

## Actualización de las fuentes de enlaces del sistema
Puede leer la información sobre los comandos disponibles ejecutando:
```bash
python -m systemgrd.updater sources --help
```

### Actualización de las fuentes de enlaces para todas las capas
Para actualizar todas las fuentes de enlaces para todas las capas, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd.updater sources
```

Esto actualizará las fuentes de enlaces para todas las capas y los almacenará en el directorio `sources/SCAN/` en un `.txt` con el nombre de la capa correspondiente.

### Actualización de las fuentes de enlaces para la capa `Borde`
Para actualizar las fuentes de enlaces para la capa `Borde`, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd.updater sources --borde
```

Esto actualizará las fuentes de enlaces para la capa `Borde` y los almacenará en el directorio `sources/SCAN/` en un `.txt` con el nombre de la misma capa.

### Actualización de las fuentes de enlaces para la capa `Bras`
Para actualizar las fuentes de enlaces para la capa `Bras`, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd.updater sources --bras
```

Esto actualizará las fuentes de enlaces para la capa `Bras` y los almacenará en el directorio `sources/SCAN/` en un `.txt` con el nombre de la misma capa.

### Actualización de las fuentes de enlaces para la capa `Caching`
Para actualizar las fuentes de enlaces para la capa `Caching`, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd.updater sources --caching
```

Esto actualizará las fuentes de enlaces para la capa `Caching` y los almacenará en el directorio `sources/SCAN/` en un `.txt` con el nombre de la misma capa.

### Actualización de las fuentes de enlaces para la capa `Rai`
Para actualizar las fuentes de enlaces para la capa `Rai`, se debe ejecutar el siguiente comando:
```bash
python -m systemgrd.updater sources --rai
```

Esto actualizará las fuentes de enlaces para la capa `Rai` y los almacenará en el directorio `sources/SCAN/` en un `.txt` con el nombre de la misma capa.

# Pruebas unitarias
Para ejecutar las pruebas unitarias del sistema, necesario tener el archivo `env.testing` con todas las [Variables de Entorno](#variables-de-entorno). Los siguientes comandos ejecutan las pruebas pertinentes:
```bash
python -m unittest discover -s systemgrd/test/querys -p "*_test.py"
python -m unittest discover -s systemgrd/test/updater -p "*_test.py"
python -m unittest discover -s systemgrd/test/handler -p "*_test.py"
```
> *Nota:* Tenga en cuenta que siempre puede ejecutar pruebas unitarias individualmente siguiendo la documentación oficial de Unittest de python.