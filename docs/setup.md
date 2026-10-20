# Configuración del entorno de desarrollo

Todo el entorno corre en contenedores: no es necesario instalar Python ni MongoDB en el equipo. Todas las reglas disponibles del `Makefile` se detallan en [makefile.md](makefile.md).

## Requisitos previos

- Git
- Docker y Docker Compose v2 (`docker compose`)
- Make

Python 3.13 y las dependencias de cada servicio se instalan dentro de las imágenes Docker.

## 1. Clonar

```bash
git clone https://github.com/xanv754/ScanBackup ScanBackup
cd ScanBackup
git switch develop
```

## 2. Variables de entorno

```bash
cp .env.development.example .env.development
```

Completar en `.env.development`:

| Variable | Obligatoria | Descripción | Valor Predeterminado o Recomendable |
|---|---|---|---|
| `MONGO_USERNAME` | Sí | Nombre del usuario con el que los servicios se autentican en la base de datos. | --- |
| `MONGO_PASSWORD` | Sí | Contraseña del usuario con el que los servicios se autentican en la base datos. | --- |
| `MONGO_DATABASE` | Sí | Nombre de la base de datos que utilizan los servicios. | `scan_backup` |
| `MONGO_AUTH_SOURCE` | Sí | Indica la base de datos donde MongoDB verifica las credenciales que autentican a la base de datos del sistema. | `admin` |
| `MONGO_HOST_PORT` | Sí | Puerto del host por el que se expone MongoDB. | `27017` |
| `SCAN_USERNAME` | Sí | Nombre del usuario de acceso al simulador de SCAN. | --- |
| `SCAN_PASSWORD` | Sí | Contraseña del usuario de acceso al simulador de SCAN. | --- |
| `APP_UID` | Sí | Nombre de la base de datos que utilizan los servicios | Valor de respuesta de la ejecución del comando `id -u`. |
| `APP_GID` | Sí | Nombre de la base de datos que utilizan los servicios | Valor de respuesta de la ejecución del comando `id -g`. |
| `SCAN_SIM_HOST_PORT` | No | Puerto del host donde se publica el simulador de SCAN en `127.0.0.1` | `8443` |

## 3. Preparar directorios del host

```bash
make init
```

Crea `exports/` y `logs/<servicio>/` con el usuario actual, para que Docker no los cree como `root`. Es seguro repetirlo.

## 4. Construir imágenes y dependencias

```bash
make dev-build
```

Las dependencias de cada servicio se instalan durante la construcción. 

> **Recordatorio:** Repetir este paso cuando cambien las dependencias, el `Dockerfile`, `APP_UID` o `APP_GID`.

## 5. Base de datos

```bash
make dev-up
```

Levanta únicamente MongoDB. No hay migraciones ni seeds. La base de datos y el usuario se crean automáticamente con las variables `MONGO_*` la primera vez que se inicia el volumen. 

> **Nota:** Para acceder desde herramientas externas (por ejemplo, Compass) usar `127.0.0.1:<MONGO_HOST_PORT>`.

## 6. Simulador de SCAN

En desarrollo no se consulta SCAN real. El servicio `scan-simulator` (nginx) replica SCAN: HTTPS con certificado autofirmado, HTTP Basic con `SCAN_USERNAME`/`SCAN_PASSWORD` y las páginas y logs MRTG de `dev/scan-simulator/fixtures/`. Detalle del servicio en [makefile.md](makefile.md#simulador-de-scan-desarrollo).

Requisitos previos del simulador:

- `dev/scan-simulator/fixtures/pages.map`: Crearlo a partir del ejemplo (`pages.map.example`) y reemplazar las URLs por las escritas en `services/interface-sync/config.yml`:
  ```bash
  cp dev/scan-simulator/fixtures/pages.map.example dev/scan-simulator/fixtures/pages.map
  ```

  > **Observación:** No existe en el repositorio (está ignorado por Git porque contiene URLs internas). Si no existe, nginx no arranca.

- Hosts de SCAN: Los hosts de SCAN se resuelven al simulador dentro de la red de Docker mediante aliases (`docker-compose.dev.yml`). Las URLs de `config.yml` deben usar estos hosts y coincidir con las entradas de `pages.map`.

Contenido de las fixtures:

- Páginas de las capas: archivos HTML en `dev/scan-simulator/fixtures/pages/`, registrados en `pages.map` con su URL exacta.
- Logs MRTG: archivos en `dev/scan-simulator/fixtures/static/` con el mismo path de la URL (por ejemplo, `https://<host>/mrtg/x.log` → `fixtures/static/mrtg/x.log`).
- Una URL sin fixture responde `404`; el request queda en `make dev-sim-logs`.

> **Recordatorio:** Ambas carpetas se montan en modo lectura, por lo que los cambios en HTML y logs se aplican sin reiniciar. Los cambios en `pages.map` o en las plantillas de `dev/scan-simulator/templates/` requieren `make dev-sim-restart`.

Levantar y verificar el simulador:

```bash
make dev-sim-up
make dev-sim-status    # debe mostrar "healthy"
```

> **Nota:** Los servicios `dev-sync`, `dev-collect` y `dev-report` lo levantan automáticamente si no está activo.

Una vez que el servicio esté levantado, puedes realizar las peticiones como se realizarían al sistema SCAN. Por ejemplo:
```bash
set -a; source .env.development; set +a

# HTML de la página de Borde
curl -k -u "$SCAN_USERNAME:$SCAN_PASSWORD" \
  "https://127.0.0.1:8443/cgi-bin/graficas-v2-intl-hw.cgi?/monitoreo/mrtg/dummy/BACKBONE-HW-ENLACES.dummy"

# Valores crudos de una interfaz
curl -k -u "$SCAN_USERNAME:$SCAN_PASSWORD" https://127.0.0.1:8443/mrtg/r27696-ge200hwi.log
```

## 7. Ejecutar los servicios

Los servicios no permanecen levantados; se ejecutan bajo demanda en contenedores efímeros. El orden inicial recomendado es:

```bash
make dev-sync      # carga las interfaces desde SCAN
make dev-collect   # recolecta el tráfico de las interfaces activas
make dev-report    # genera los reportes en exports/
```

Los argumentos de cada servicio se consultan con `ARGS="--help"`. Por ejemplo:

```bash
make dev-report ARGS="--help"
```

## 8. Verificar que funciona

- MongoDB activo: `make dev-logs` (salir con `Ctrl+C`; no detiene MongoDB).
- Servicios operativos: `make dev-sync ARGS="--help"` debe terminar con código `0`.
- Logs de los servicios: `logs/<servicio>/`.

> **Nota:** Las pruebas (`make dev-test`) aún no están disponibles, ya que no existen tests en el proyecto.

## Detener y reiniciar

```bash
make dev-down    # detiene contenedores, conserva los datos
make dev-clean   # detiene contenedores y BORRA la base de datos (irreversible)
```

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| Los servicios no pueden escribir en `logs/` o `exports/` | Las carpetas fueron creadas por Docker como `root`, o `APP_UID`/`APP_GID` no coinciden con tu usuario | Corregir el propietario (`sudo chown -R $(id -u):$(id -g) logs exports`), verificar `APP_UID`/`APP_GID` y ejecutar `make dev-build` |
| Error de autenticación contra MongoDB tras cambiar credenciales | `MONGO_USERNAME`, `MONGO_PASSWORD` y `MONGO_DATABASE` solo se aplican al inicializar el volumen | Restaurar los valores originales, o ejecutar `make dev-clean` y `make dev-up` (borra los datos) |
| `port is already allocated` al ejecutar `make dev-up` | `MONGO_HOST_PORT` está en uso por otro proceso | Cambiar `MONGO_HOST_PORT` en `.env.development` |
| Los servicios fallan por falta de conexión a MongoDB | MongoDB no está activo | Ejecutar `make dev-up` y revisar `make dev-logs` |
| `make dev-collect` termina con código distinto de cero | No hay interfaces activas en la base de datos | Ejecutar primero `make dev-sync` |
| `make dev-sync` o `make dev-collect` fallan al consultar SCAN | Credenciales `SCAN_*` incorrectas, o SCAN inaccesible o modificado | Verificar `SCAN_USERNAME`, `SCAN_PASSWORD` y la conectividad desde el equipo |
| `make dev-sim-up` falla o el simulador no pasa a `healthy` | Falta `pages.map`, o `SCAN_USERNAME`/`SCAN_PASSWORD` no definidos | Crear `pages.map` desde el ejemplo (paso 6), revisar `make dev-sim-logs` |
| El simulador responde `404` a `interface-sync` o `traffic-collector` | La URL pedida no está registrada en `pages.map` o no hay archivo en `fixtures/` | Comparar la URL de `config.yml` con `pages.map` y revisar los logs del simulador |
| `port is already allocated` al ejecutar `make dev-sim-up` | `SCAN_SIM_HOST_PORT` está en uso | Cambiar `SCAN_SIM_HOST_PORT` en `.env.development` |
| `make: *** No rule to make target` o `env file not found` | Falta `.env.development` | Repetir el paso 2 |
