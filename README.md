# Sistema CPGRD
Un sistema diseñado para la colleción de data para generación de reportes y otros archivos para la coordinación CPGRD.

# Variables de Entorno
El sistema require un archivo `.env` con las siguientes variables de entorno:

```bash
URI_MONGO="mongodb://user:password@server:port/name_database"
URI_POSTGRES="postgres://user:password@server:port/name_database"
```

Para ejecutar las **pruebas unitarias**, se requiere un archivo `.env` con las siguientes variables de entorno:

```bash
URI_TEST_MONGO="mongodb://user:password@server:port/name_database"
URI_TEST_POSTGRES="postgres://user:password@server:port/name_database"
```

# Makefile
El sistema cuenta con un archivo Makefile para facilitar la ejecución de tareas comunes.

## Tareas Disponibles
1. `make setup`: Crea entornos virtuales, instala las dependencias necesarias y define rutas.
2. `make test`: Ejecuta las pruebas unitarias del sistema.
3. `make migration`: Ejecuta las migraciones de la base de datos.
4. `make rollback`: Ejecuta las migraciones inversas de la base de datos.
5. `make updater`: Ejecuta el actualizador del sistema. Este actualizará la base de datos con la data del día actual.
5. `make updater-date` o `make DATE=YYYY-MM-DD updater-date`: Ejecuta el actualizador del sistema. Este actualizará la base de datos con la data del día actual o, si se especifica una fecha (`DATE`), actualizará la base datos con la fecha proporcionada.
6. `make clean`: Elimina archivos generados por el sistema.
