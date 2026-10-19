# SCAN-Backup
## Variables de entorno

La configuración sensible del sistema se define mediante variables de entorno. Se parte del archivo de ejemplo del ambiente a utilizar, se copia sin el sufijo `.example` y se completan los valores:

```bash
cp .env.production.example .env.production   # producción
cp .env.development.example .env.development # desarrollo
```

El archivo resultante contiene credenciales: no debe versionarse ni compartirse.

| Ambiente | Archivo de ejemplo | Compose utilizado |
|---|---|---|
| Producción | `.env.production.example` | `docker-compose.yml` |
| Desarrollo | `.env.development.example` | `docker-compose.dev.yml` |

### Base de datos (MongoDB)

| Variable | Obligatoria | Descripción |
|---|---|---|
| `MONGO_USERNAME` | Sí | Nombre del usuario administrador de MongoDB. Se crea automáticamente la primera vez que se inicia la base de datos y es el que usan los tres servicios para conectarse. |
| `MONGO_PASSWORD` | Sí | Contraseña del usuario anterior. Usar una contraseña robusta. |
| `MONGO_DATABASE` | Sí | Nombre de la base de datos donde se almacena toda la información del sistema. Valor recomendado: `scan_backup`. |
| `MONGO_AUTH_SOURCE` | No | Base de datos donde MongoDB valida al usuario. Por defecto `admin`. |
| `MONGO_HOST_PORT` | No (solo desarrollo) | Puerto del equipo local por el cual se accede a MongoDB desde herramientas externas (por ejemplo, Compass). Por defecto `27017`. Solo es accesible desde el mismo equipo (`127.0.0.1`). En producción MongoDB no se expone al exterior y esta variable no se utiliza. |

> **Importante:** `MONGO_USERNAME`, `MONGO_PASSWORD` y `MONGO_DATABASE` se aplican únicamente cuando MongoDB inicializa su volumen de datos por primera vez. Si se modifican después, el usuario existente no cambia y los servicios dejarán de poder conectarse. Para cambiar credenciales con el sistema ya en uso, hay que modificarlas dentro de MongoDB o eliminar el volumen de datos (esto borra todo el histórico).

### Sistema SCAN

| Variable | Obligatoria | Descripción |
|---|---|---|
| `SCAN_USERNAME` | Sí | Usuario con acceso de lectura al sistema SCAN. Lo usan `interface-sync` y `traffic-collector`. El servicio `reports` no lo utiliza. |
| `SCAN_PASSWORD` | Sí | Contraseña del usuario de SCAN. |

### Permisos de archivos

| Variable | Obligatoria | Descripción |
|---|---|---|
| `APP_UID` | No | ID del usuario del servidor que será dueño de los archivos generados (logs y carpeta `exports/`). Por defecto `1000`. Se obtiene con el comando `id -u`. |
| `APP_GID` | No | ID del grupo del usuario anterior. Por defecto `1000`. Se obtiene con el comando `id -g`. |

Ambas variables se aplican al construir las imágenes: si se modifican, las imágenes deben reconstruirse. 

> **Importante:** Las carpetas `logs/` y `exports/` deben existir antes de la primera ejecución y pertenecer a ese usuario; de lo contrario Docker las crea como `root` y los servicios no podrán escribir en ellas.