# Scan Backup
Un sistema diseñado para la recolección de datos de tráfico de todas las interfaces de la red a través de la plataforma de Monitoreo (SCAN), y procesamiento de la misma para la generación de distintos reportes para el análisis de tráfico.

![Diagrama de Procesos](./docs/process.png)

# Documentación 
- Para descargar todo el manual técnico, descargue el archivo [Manual Técnico.pdf](./docs/Manual%20Tecnico.pdf).
- Para ver los diagramas, revisa: [Diagramas](https://lucid.app/lucidchart/dad09d4e-e34e-4d32-a254-e62e64d820e4/edit?viewport_loc=-393%2C-398%2C5836%2C3094%2CbOV_OreY9Nsi&invitationId=inv_2ab76b6f-cab5-4df0-bde3-fcae7c263901) o descargue el archivo [Diagramas.pdf](./docs/Diagramas.pdf).

# Índice
- [¿Cómo funciona?](#-cómo-funciona-)
    - [Recolección de Datos](#recolección-de-datos)
        - [Archivos Fuentes del Sistema](#archivos-fuentes-del-sistema)
    - [Procesamiento de Datos](#procesamiento-de-datos)
    - [Almacenamiento de Datos](#almacenamiento-de-datos)
- [Programación de Tareas](#programación-de-tareas)
- [Logs](#logs)

# ¿Cómo funciona?
El sistema se encarga de recolectar la información del tráfico de las interfaces de red en datos de cada 5 minutos de un día registradas en Monitoreo (SCAN), dando un total de 288 muestras por interfaz en red. Esta data es obtenida gracias a los logs que el sistema de SCAN genera por cada interfaz que monitorea; esto se visualiza al cambiar la extensión de la URL de las interfaces de “.html” a “.log”. Una vez obtenida la data de cada una de las interfaces, estas son procesadas para obtener los promedios de tráfico de cada una de las 288 muestras recolectadas en el día por cada interfaz. Todo con el objetivo de almacenar en la base de datos toda la información recolectada (las 288 muestras de data cruda) y toda la información procesada (los promedios generados).

Gracias a este proceso, el sistema tiene un orden estricto para actualizarse: recolección, procesamiento y almacenamiento de los datos. Todo con el fin de prevalecer la información de tráfico de las interfaces para generar reportes donde se necesiten muestreos de data mayor a 3 días, que es el máximo de días que el sistema de SCAN guarda información.

Para este sistema, todo esto se logra mediante el correcto orden de ejecución de las rutinas. Las rutinas se encuentran en la carpeta `routines/`.

## Recolección de Datos
`scanbackup/routines/scanner.sh`

Este script se encarga de la recolección de los datos de tráfico de SCAN del día anterior de todas las interfaces especificadas en los **archivos fuentes del sistema**, que se encuentran en el directorio `sources/SCAN`. Todo el tráfico obtenido está en base a intervalos de cinco minutos. La información obtenida se alojará en el directorio `data/SCAN`, divido en carpetas según la capa del BBIP que corresponda.

Las capas del BBIP disponibles hasta el momento de esta documentación son: 
-	BORDE: Enlaces Internacionales
-	BRAS: Agregadores
-	CACHING: Servicio.
-	RAI: Servicio.
-	IXP: Servicio.
-	IPBRAS: IP activas de los agregadores.

### Archivos Fuentes del Sistema
Para poder realizar la captura de data, es necesario declarar los archivos fuentes por cada una de las capas disponibles para consultar (BORDE, BRAS, CACHING, RAI, IXP, IPBRAS). Los datos que se especifiquen en cada uno de dichos archivos son los que el sistema se va a encargar de recolectar información. 

Estas fuentes deben estar declaradas en un archivo sin extensión, dentro del directorio `sources/SCAN/` y con el nombre de la capa escrito en mayúscula sin espacios o caracteres especiales. 

Como ya se dijo, los archivos fuentes deben estar clasificados por las capas del sistema, siguiendo el siguiente formato para declarar las interfaces que se va a buscar información:
```bash
link-de-acceso1;nombre-de-la-interfaz1;capacidad-de-la-interfaz1;tipo-de-la-interfaz1
link-de-acceso2;nombre-de-la-interfaz2;capacidad-de-la-interfaz2;tipo-de-la-interfaz2
```

## Procesamiento de Datos
`scanbackup/routines/daily.py`

Esto script se encarga de procesar los datos de SCAN recolectados para generar los resúmenes de promedios de tráfico para todas las interfaces en las que se haya obtenido la información cruda previamente. Esta nueva data promediada será almacenada en el directorio `data/SCAN/DAILY_SUMMARY` en archivos separados por la capa a la que corresponda la interfaz.

## Almacenamiento de Datos
Este módulo se encuentra en la carpeta `updater/`. Se encarga de cargar toda la data recolectada y procesada de las interfaces obtenidas de SCAN en la base de datos del sistema. Realizando la limpieza de toda la data que haya sido almacenada exitosamente. 

> **Nota**: De haber algún problema en la carga de la data, el sistema no borrará los archivos con la data.

Por defecto, este módulo solo almacena la data del día anterior al actual, pero cuenta con distintas opciones para especificar tanto la fecha que se desea cargar, como si se desea cargar toda la data existente sin importar la diferencia de días.

# Programación de Tareas
Para la correcta ejecución del actualizador del sistema, se debe programar la ejecución automática diara del actualizador del sistema. Para ello se debe añadir al *crontab* del sistema el siguiente comando:
```bash
export PWDSCANBACKUP="/home/user/ScanBackup" # Debe reemplazarse por la ruta del directorio del sistema
export USERSCAN="usuario" # Debe reemplazarse por el usuario
export PASSWORDSCAN="contraseña" # Debe reemplazarse por la contraseña

00 04 * * * cd $PWDSCANBACKUP && /usr/bin/make run
```

O puede especificar uno a uno los comandos en el siguiente orden necesario:
```bash
export PWDSCANBACKUP="/home/user/ScanBackup" # Debe reemplazarse por la ruta del directorio del sistema
export USERSCAN="usuario" # Debe reemplazarse por el usuario
export PASSWORDSCAN="contraseña" # Debe reemplazarse por la contraseña

00 04 * * * bash /home/user/ScanBackup/scanbackup/routines/scanner.sh
00 07 * * * /home/user/ScanBackup/.venv/bin/python -m scanbackup.routines.daily
30 07 * * * /home/user/ScanBackup/.venv/bin/python -m scanbackup.updater data
```

**IMPORTANTE**: Si se especifica de esta manera, es importante dejar un espacio de tiempo de mínimo 3h entre el recolector de data (`scanner`) y el procesador de data (`daily`).

# Logs
El sistema lleva un registro de logs de todas las operaciones que se realizan. Esto se puede encontrar en el directorio `data/logs/`.

> **Nota para desarrollador**: Estos logs cuentan con un formato específico para facilitar su lectura. Se insta a respetar dicho formato.
