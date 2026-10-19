# Configuración del entorno de desarrollo

Todo el entorno corre en contenedores: no es necesario instalar Python ni MongoDB en el equipo. Las reglas disponibles del `Makefile` se detallan en [makefile.md](makefile.md) y las variables de entorno en el [README](../README.md).

## Requisitos previos

- Git
- Docker y Docker Compose v2 (`docker compose`)
- Make
- Acceso de red al sistema SCAN y credenciales de lectura (necesarias para `interface-sync` y `traffic-collector`)

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

- `MONGO_USERNAME`, `MONGO_PASSWORD`, `MONGO_DATABASE` (recomendado: `scan_backup`), `MONGO_HOST_PORT`.
- `SCAN_USERNAME`, `SCAN_PASSWORD`.
- `APP_UID` y `APP_GID` con el resultado de `id -u` y `id -g`.

Este archivo contiene credenciales: no debe versionarse. El detalle de cada variable está en el [README](../README.md#variables-de-entorno).

## 3. Preparar directorios del host

```bash
make init
```

Crea `exports/` y `logs/<servicio>/` con el usuario actual, para que Docker no los cree como `root`. Es seguro repetirlo.

## 4. Construir imágenes y dependencias

```bash
make dev-build
```

Las dependencias de cada servicio se instalan durante la construcción. Repetir este paso cuando cambien las dependencias, el `Dockerfile`, `APP_UID` o `APP_GID`.

## 5. Base de datos

```bash
make dev-up
```

Levanta únicamente MongoDB. No hay migraciones ni seeds: la base de datos y el usuario se crean automáticamente con las variables `MONGO_*` la primera vez que se inicia el volumen. Para acceder desde herramientas externas (por ejemplo, Compass) usar `127.0.0.1:<MONGO_HOST_PORT>` (por defecto `27017`).

## 6. Ejecutar los servicios

Los servicios no permanecen levantados; se ejecutan bajo demanda en contenedores efímeros. El orden inicial recomendado es:

```bash
make dev-sync      # carga las interfaces desde SCAN
make dev-collect   # recolecta el tráfico de las interfaces activas
make dev-report    # genera los reportes en exports/
```

Los argumentos de cada servicio se consultan con `ARGS="--help"`, por ejemplo `make dev-report ARGS="--help"`.

## 7. Verificar que funciona

- MongoDB activo: `make dev-logs` (salir con `Ctrl+C`; no detiene MongoDB).
- Servicios operativos: `make dev-sync ARGS="--help"` debe terminar con código `0`.
- Logs de los servicios: `logs/<servicio>/`.

Las pruebas (`make dev-test`) aún no están disponibles, ya que no existen tests en el proyecto.

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
| `make: *** No rule to make target` o `env file not found` | Falta `.env.development` | Repetir el paso 2 |
