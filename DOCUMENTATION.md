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
El sistema se encarga de recolectar la información del tráfico en datos de cada 5 minutos de todas las interfaces de la red registradas en SCAN. Esta data, una vez obtenida, es procesada para obtener los promedios diarios del tráfico de cada una de las interfaces de las capas obtenidas, para luego almacenar en la base de datos toda la información recolectada y procesada.

El sistema tiene un orden estricto para dicha operación: recolección, procesamiento y almacenamiento de los datos. Esto se logra mediante el correcto orden de ejecución de las rutinas. Las rutinas se encuentran en la carpeta `routines/`.

## Recolección de Datos
`scanbackup/routines/scanner.sh`

Este script se encarga de la recolección de los datos de tráfico de SCAN del día anterior de todas las interfaces especificadas en el directorio `sources/SCAN`. Todo el tráfico obtenido está en base a intervalos de cinco minutos. La información obtenida se alojará en el directorio `data/SCAN`, divido en carpetas según la capa que corresponda.

### Archivos Fuentes del Sistema
Para poder realizar la captura de data, es necesario declarar las fuentes a cada una de las capas disponibles para consultar (BORDE, BRAS, CACHING, RAI, IXP, IPBRAS). Los datos que se especifiquen en cada uno de dichos archivos, son los que el sistema se va a encargar de recolectar información. Estas fuentes deben estar en un archivo sin extensión en el directorio `sources/SCAN/`, con el nombre de la capa escrito en mayúscula sin espacios o caracteres  especiales. 

Como ya se dijo, los archivos fuentes deben estar clasificados por las capas del sistema, siguiendo el siguiente formato:
```
link-de-acceso;nombre-de-la-interfaz;capacidad-de-la-interfaz;tipo-de-la-interfaz
```

## Procesamiento de Datos
`scanbackup/routines/daily.py`

Esto script se encarga de procesar los datos de SCAN recolectados para generar los resúmenes de promedios de tráfico para todas las interfaces que se encuentren disponibles para las capas del sistema. La nueva data que se genere será almacenada en el directorio `data/SCAN/DAILY_SUMMARY` según la capa que corresponda.

## Almacenamiento de Datos
Este módulo se encuentra en la carpeta `updater/`, se encarga de cargar toda la data recolectada y procesada de las interfaces obtenidas de SCAN en la base de datos del sistema.


# Programación de Tareas
Para la correcta ejecución del actualizador del sistema, se debe configurar la programación de tareas para que se ejecute automáticamente. Para ello se debe añadir al crontab del sistema el siguiente comando:
```bash
export PWDSCANBACKUP="/home/user/ScanBackup" # Debe reemplazarse por la ruta del directorio del sistema
export USERSCAN="usuario" # Debe reemplazarse por el usuario
export PASSWORDSCAN="contraseña" # Debe reemplazarse por la contraseña

00 04 * * * cd $PWDSCANBACKUP && /usr/bin/make run
```

O de forma más textual:
```bash
export PWDSCANBACKUP="/home/user/ScanBackup" # Debe reemplazarse por la ruta del directorio del sistema
export USERSCAN="usuario" # Debe reemplazarse por el usuario
export PASSWORDSCAN="contraseña" # Debe reemplazarse por la contraseña

00 04 * * * bash /home/user/ScanBackup/scanbackup/routines/scanner.sh
00 07 * * * /home/user/ScanBackup/.venv/bin/python -m scanbackup.routines.diario
30 07 * * * /home/user/ScanBackup/.venv/bin/python -m scanbackup.updater data
```

# Logs
El sistema lleva un registros de logs en el directorio `data/logs/`. Estos logs cuentan con un formato específico para facilitar su lectura. Cada operación que ejecuta el sistema se registra en dichos archivos. 