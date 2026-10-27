# Configuración del entorno de producción

Todo el sistema corre en contenedores: no es necesario instalar Python ni MongoDB en el servidor. Todas las reglas disponibles del `Makefile` se detallan en [makefile.md](makefile.md).

## Requisitos previos

- Git
- Docker y Docker Compose v2 (`docker compose`), con el servicio de Docker habilitado en el arranque del servidor
- Make
- Acceso de red desde el servidor al sistema SCAN
- Credenciales de un usuario con acceso de lectura a SCAN

Python 3.13 y las dependencias de cada servicio se instalan dentro de las imágenes Docker.

## 1. Clonar

```bash
git clone https://github.com/xanv754/ScanBackup ScanBackup
cd ScanBackup
git switch main
```

## 2. Variables de entorno

```bash
cp .env.production.example .env.production
chmod 600 .env.production
```

Completar en `.env.production`:

| Variable | Obligatoria | Descripción | Valor Predeterminado o Recomendable |
|---|---|---|---|
| `MONGO_USERNAME` | Sí | Nombre del usuario administrador con el que los servicios se autentican en la base de datos. Se crea la primera vez que se inicia MongoDB. | --- |
| `MONGO_PASSWORD` | Sí | Contraseña del usuario anterior. Usar una contraseña robusta. | --- |
| `MONGO_DATABASE` | Sí | Nombre de la base de datos donde se almacena toda la información del sistema. | `scan_backup` |
| `MONGO_AUTH_SOURCE` | Sí | Base de datos donde MongoDB valida las credenciales del usuario. | `admin` |
| `SCAN_USERNAME` | Sí | Usuario con acceso de lectura al sistema SCAN. Lo usan `interface-sync` y `traffic-collector`. | --- |
| `SCAN_PASSWORD` | Sí | Contraseña del usuario de SCAN. | --- |
| `APP_UID` | No | ID del usuario (UID) del servidor que será dueño de los archivos generados (logs y `exports/`). | Valor de respuesta de la ejecución del comando `id -u`. Por defecto `1000`. |
| `APP_GID` | No | ID del grupo (GID) del usuario anterior. | Valor de respuesta de la ejecución del comando `id -g`. Por defecto `1000`. |

> **Importante:** `.env.production` contiene credenciales: no debe versionarse ni compartirse.

> **Importante:** `MONGO_USERNAME`, `MONGO_PASSWORD` y `MONGO_DATABASE` se aplican únicamente cuando MongoDB inicializa su volumen de datos por primera vez. Si se modifican después, el usuario existente no cambia y los servicios dejarán de poder conectarse. Definir valores definitivos antes del primer `make prod-up`.

## 3. Archivos de configuración de los servicios

`interface-sync` y `reports` leen un `config.yml` propio que se monta en el contenedor en modo lectura. Estos archivos no están en el repositorio (los ignora Git); se crean a partir de su ejemplo:

```bash
cp services/interface-sync/config.yml.example services/interface-sync/config.yml
cp services/reports/config.yml.example services/reports/config.yml
```

- `services/interface-sync/config.yml`: reemplazar los valores de ejemplo por las capas de SCAN a procesar (`layer`, `url` y `vendor` de cada enlace).
- `services/reports/config.yml`: define el prefijo (`preffix_name`) y el formato de fecha (`date_format`) de los nombres de los reportes. Los valores del ejemplo son válidos.

> **Importante:** Ambos archivos deben existir antes de ejecutar los servicios. Si no existen, Docker crea un directorio en su lugar y el servicio falla.

> **Observación:** `traffic-collector` no usa archivo de configuración.

## 4. Preparar directorios del host

```bash
make init
```

Crea `exports/` y `logs/<servicio>/` con el usuario actual, para que Docker no los cree como `root`. Es seguro repetirlo.

> **Importante:** El usuario que ejecuta `make init` debe coincidir con `APP_UID` y `APP_GID`; de lo contrario los servicios no podrán escribir en `logs/` ni `exports/`.

## 5. Construir imágenes

```bash
make prod-build
```

Las dependencias de cada servicio se instalan durante la construcción.

> **Recordatorio:** Repetir este paso cuando cambien las dependencias, el `Dockerfile`, `APP_UID` o `APP_GID`, y después de actualizar el código con `git pull`.

## 6. Base de datos

```bash
make prod-up
```

Levanta únicamente MongoDB. No hay migraciones ni seeds. La base de datos y el usuario se crean automáticamente con las variables `MONGO_*` la primera vez que se inicia el volumen (`scan-backup-mongo-data`).

MongoDB se reinicia automáticamente con Docker (`unless-stopped`), por lo que vuelve a estar activo tras un reinicio del servidor. Solo se detiene si se ejecuta `make prod-down`.

> **Nota:** MongoDB no se publica en ningún puerto del host: solo es accesible por los servicios dentro de la red de Docker.

### Acceder a `mongosh`

Con MongoDB levantado, abrir una sesión interactiva dentro del contenedor `scan-backup-mongo`:

```bash
set -a; source .env.production; set +a

docker exec -it scan-backup-mongo mongosh \
  -u "$MONGO_USERNAME" -p "$MONGO_PASSWORD" \
  --authenticationDatabase "$MONGO_AUTH_SOURCE" "$MONGO_DATABASE"
```

Una vez dentro, algunos comandos útiles (solo lectura):

```javascript
show collections
db.<coleccion>.countDocuments()
db.<coleccion>.findOne()
exit
```

## 7. Carga inicial de interfaces

`traffic-collector` solo consulta las interfaces activas registradas en la base de datos, por lo que antes de su primera ejecución deben cargarse con `interface-sync`:

```bash
make prod-sync ARGS="run"
```

Sin el comando `run`, `interface-sync` solo muestra la ayuda. Códigos de salida de `run`: `0` todas las páginas exitosas, `1` al menos una página fallida, `2` error general del proceso.

> **Recordatorio:** `interface-sync` es de ejecución manual. Debe repetirse cada vez que se incorporen o desincorporen interfaces en SCAN.

## 8. Programar la recolección diaria

`traffic-collector` debe ejecutarse **una (1) vez por día** y su programación es responsabilidad del usuario de operatividad. Editar el `crontab` del usuario que opera el sistema (`crontab -e`):

```bash
0 1 * * * make -C /ruta/al/proyecto prod-collect
```

Ejecuta la recolección todos los días a las 01:00 y toma el tráfico del día anterior. Ajustar la ruta del proyecto.

- La regla usa `-T` (sin pseudo-TTY), por lo que es válida en `crontab`.
- El código de salida del servicio se propaga a `make`: cualquier valor distinto de cero indica fallo (incluida la ausencia de interfaces activas).
- El usuario del `crontab` debe pertenecer al grupo `docker` y MongoDB debe estar activo (`make prod-up`).

## 9. Generar reportes

```bash
make prod-report ARGS="--help"
```

Los reportes se generan bajo demanda a partir de los datos almacenados y se exportan a `exports/`. No consulta SCAN ni modifica datos. Los argumentos disponibles (tipo de reporte, rango de fechas, etc.) se consultan con `--help`.

## 10. Verificar que funciona

- MongoDB activo: `make prod-logs` (salir con `Ctrl+C`; no detiene MongoDB).
- Servicios operativos: `make prod-report ARGS="--help"` debe terminar con código `0`.
- Recolección: tras la primera ejecución del `crontab` (o ejecutando `make prod-collect` manualmente), verificar el código de salida con `echo $?` y revisar `logs/traffic-collector/`.
- Logs de los servicios: `logs/<servicio>/` (rotativos, uno por servicio).

## Operación

### Actualizar el sistema

```bash
git pull
make prod-build
```

Los contenedores de los servicios son efímeros, por lo que la nueva imagen se usa en la siguiente ejecución. No es necesario reiniciar MongoDB.

> **Observación:** Evitar actualizar durante la ventana de ejecución del `crontab`.

### Detener y reiniciar

```bash
make prod-down   # detiene contenedores, conserva los datos
make prod-up     # vuelve a levantar MongoDB
```

`make prod-down` no borra los datos (volumen `scan-backup-mongo-data`), `logs/` ni `exports/`. Mientras MongoDB esté detenido, todos los servicios fallan por falta de conexión, incluida la ejecución del `crontab`.

### Respaldo de la base de datos

El histórico vive únicamente en el volumen de MongoDB. Se recomienda respaldarlo periódicamente fuera del servidor:

```bash
set -a; source .env.production; set +a

docker exec scan-backup-mongo mongodump \
  -u "$MONGO_USERNAME" -p "$MONGO_PASSWORD" \
  --authenticationDatabase "$MONGO_AUTH_SOURCE" \
  --db "$MONGO_DATABASE" --archive --gzip > scan_backup_$(date +%Y%m%d).gz
```

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `MONGO_USERNAME is required` (o similar) al ejecutar `make` | Falta `.env.production` o tiene variables vacías | Repetir el paso 2 y completar las variables obligatorias |
| Los servicios no pueden escribir en `logs/` o `exports/` | Las carpetas fueron creadas por Docker como `root`, o `APP_UID`/`APP_GID` no coinciden con el propietario | Corregir el propietario (`sudo chown -R $(id -u):$(id -g) logs exports`), verificar `APP_UID`/`APP_GID` y ejecutar `make prod-build` |
| Error de autenticación contra MongoDB tras cambiar credenciales | `MONGO_USERNAME`, `MONGO_PASSWORD` y `MONGO_DATABASE` solo se aplican al inicializar el volumen | Restaurar los valores originales. Cambiarlas con el sistema en uso requiere modificarlas dentro de MongoDB |
| Los servicios fallan por falta de conexión a MongoDB | MongoDB no está activo | Ejecutar `make prod-up` y revisar `make prod-logs` |
| `make prod-collect` termina con código distinto de cero | No hay interfaces activas en la base de datos | Ejecutar primero `make prod-sync ARGS="run"` |
| `make prod-sync` o `make prod-collect` fallan al consultar SCAN | Credenciales `SCAN_*` incorrectas, o SCAN inaccesible o modificado | Verificar `SCAN_USERNAME`, `SCAN_PASSWORD`, la conectividad desde el servidor y las URLs de `services/interface-sync/config.yml` |
| El servicio falla al iniciar y `config.yml` aparece como directorio | `config.yml` no existía al ejecutar el servicio y Docker creó un directorio | Eliminar el directorio y crear el archivo desde su ejemplo (paso 3) |
| La recolección no se ejecuta desde el `crontab` | Ruta incorrecta, usuario sin permisos de Docker o MongoDB detenido | Verificar la ruta en el `crontab`, que el usuario pertenezca al grupo `docker` y que MongoDB esté activo |
| `make: *** No rule to make target` o `env file not found` | Falta `.env.production` | Repetir el paso 2 |
