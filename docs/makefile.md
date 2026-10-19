# Guía operativa del Makefile

El `Makefile` es el punto de entrada operativo de SCAN-Backup. Cada regla lanza contenedores mediante Docker Compose, ya sea en el entorno de desarrollo (`dev-*`) o en el de producción (`prod-*`).

## Índice

| Regla | Nombre |
|---|---|
| [`init`](#make-init) | Inicializar directorios del host |
| [`dev-build`](#make-dev-build) / [`prod-build`](#make-prod-build) | Construir imágenes |
| [`dev-up`](#make-dev-up) / [`prod-up`](#make-prod-up) | Levantar MongoDB |
| [`dev-down`](#make-dev-down) / [`prod-down`](#make-prod-down) | Detener contenedores |
| [`dev-clean`](#make-dev-clean) | Detener contenedores y borrar volúmenes |
| [`dev-logs`](#make-dev-logs) / [`prod-logs`](#make-prod-logs) | Ver logs de MongoDB |
| [`dev-sync`](#make-dev-sync) / [`prod-sync`](#make-prod-sync) | Sincronizar interfaces |
| [`dev-collect`](#make-dev-collect) / [`prod-collect`](#make-prod-collect) | Recolectar tráfico |
| [`dev-report`](#make-dev-report) / [`prod-report`](#make-prod-report) | Generar reportes |
| [`dev-test`](#make-dev-test) | Ejecutar pruebas de todos los servicios |
| [`dev-test-<servicio>`](#make-dev-test-servicio) | Ejecutar pruebas de un servicio |

## Variables generales

Las variables se sobrescriben al invocar la regla: `make <regla> VARIABLE=valor`.

| Variable | Valor por defecto | Aplica a | Descripción |
|---|---|---|---|
| `DEV_ENV_FILE` | `.env.development` | Reglas `dev-*` | Archivo de variables de entorno (credenciales y configuración) usado en desarrollo. |
| `PROD_ENV_FILE` | `.env.production` | Reglas `prod-*` | Archivo de variables de entorno (credenciales y configuración) usado en producción. |
| `ARGS` | vacío | Reglas `*-sync`, `*-collect`, `*-report`, `dev-test`, `dev-test-<servicio>` | Argumentos que se pasan tal cual al comando que ejecuta el contenedor. |

Ejemplo de sobrescritura:

```bash
make prod-up PROD_ENV_FILE=.env.otro
make dev-report ARGS="--help"
```

Notas generales:

- Todas las reglas que ejecutan servicios (`*-sync`, `*-collect`, `*-report`) usan contenedores efímeros: se crean, ejecutan la tarea y se eliminan al terminar (`--rm`).
- El código de salida del servicio se propaga a `make`. Cero indica ejecución exitosa; cualquier otro valor indica fallo. Esto es lo que permite detectar errores desde el `crontab`.
- Las reglas `prod-sync`, `prod-collect` y `prod-report` usan `-T` (sin pseudo-TTY) para poder ejecutarse en entornos no interactivos como el `crontab`. Las reglas `dev-*` sí asignan TTY.
- Los argumentos válidos de `ARGS` en los servicios dependen de la interfaz de línea de comandos de cada uno. `ARGS="--help"` muestra los disponibles.

---

## Preparación

### `make init`

- **Comando:**
  ```bash
  make init
  ```
- **Nombre:** Inicializar directorios del host.
- **Descripción:** Crea, en el directorio del proyecto, la carpeta `exports/` y las carpetas de logs `logs/interface-sync/`, `logs/traffic-collector/` y `logs/reports/`. Estas carpetas son las que se montan en los contenedores como volúmenes del host. Debe ejecutarse una sola vez antes del primer uso, para que Docker no las cree con propietario `root`. Es segura de repetir: si las carpetas ya existen, no hace nada ni borra su contenido. No construye imágenes ni levanta contenedores.
- **Parámetros disponibles:** Ninguno.

---

## Entorno de desarrollo

### `make dev-build`

- **Comando:**
  ```bash
  make dev-build
  ```
- **Nombre:** Construir imágenes de los servicios (desarrollo).
- **Descripción:** Construye las imágenes Docker de `interface-sync`, `traffic-collector` y `reports` usando `docker-compose.dev.yml`. Debe ejecutarse antes de la primera ejecución de los servicios y repetirse cuando cambien las dependencias o el `Dockerfile`. No levanta contenedores, no ejecuta ningún servicio y no modifica la base de datos.
- **Parámetros disponibles:**
  - `DEV_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make dev-build DEV_ENV_FILE=.env.otro
    ```

### `make dev-up`

- **Comando:**
  ```bash
  make dev-up
  ```
- **Nombre:** Levantar MongoDB (desarrollo).
- **Descripción:** Inicia únicamente el contenedor de MongoDB en segundo plano. Los servicios no se inician: se ejecutan bajo demanda con sus propias reglas. Debe estar activo antes de ejecutar cualquier servicio. Si ya está activo, no lo reinicia.
- **Parámetros disponibles:**
  - `DEV_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make dev-up DEV_ENV_FILE=.env.otro
    ```

### `make dev-down`

- **Comando:**
  ```bash
  make dev-down
  ```
- **Nombre:** Detener contenedores (desarrollo).
- **Descripción:** Detiene y elimina los contenedores y la red del entorno de desarrollo, incluido MongoDB. Conserva los volúmenes de Docker, por lo que los datos de la base de datos no se pierden y estarán disponibles al volver a ejecutar `make dev-up`. No elimina imágenes ni los archivos de `logs/` y `exports/`.
- **Parámetros disponibles:**
  - `DEV_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make dev-down DEV_ENV_FILE=.env.otro
    ```

### `make dev-clean`

- **Comando:**
  ```bash
  make dev-clean
  ```
- **Nombre:** Detener contenedores y borrar volúmenes (desarrollo).
- **Descripción:** Hace lo mismo que `make dev-down` y además elimina los volúmenes de Docker del entorno de desarrollo. Si MongoDB almacena sus datos en un volumen de Docker, esta regla borra toda la información de la base de datos de forma irreversible. Úsese solo para reiniciar el entorno desde cero. No elimina imágenes ni los archivos de `logs/` y `exports/`, que residen en el host.
- **Parámetros disponibles:**
  - `DEV_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make dev-clean DEV_ENV_FILE=.env.otro
    ```

### `make dev-logs`

- **Comando:**
  ```bash
  make dev-logs
  ```
- **Nombre:** Ver logs de MongoDB (desarrollo).
- **Descripción:** Muestra en tiempo real los logs del contenedor de MongoDB. La salida queda en seguimiento continuo hasta interrumpirla con `Ctrl+C`; interrumpirla no detiene MongoDB. No muestra los logs de los servicios: esos se escriben en `logs/<servicio>/`.
- **Parámetros disponibles:**
  - `DEV_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make dev-logs DEV_ENV_FILE=.env.otro
    ```

### `make dev-sync`

- **Comando:**
  ```bash
  make dev-sync
  ```
- **Nombre:** Sincronizar interfaces (desarrollo).
- **Descripción:** Ejecuta el servicio `interface-sync` en un contenedor efímero. El servicio obtiene la lista de interfaces de red de SCAN y actualiza en la base de datos su existencia y estatus (activa o desincorporada). No recolecta valores de tráfico ni genera reportes. Es una ejecución manual, bajo demanda. Requiere MongoDB activo (`make dev-up`) y la imagen construida (`make dev-build`).
- **Parámetros disponibles:**
  - `ARGS`: argumentos para el servicio, entre comillas.
    ```bash
    make dev-sync ARGS="--help"
    ```
  - `DEV_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make dev-sync DEV_ENV_FILE=.env.otro
    ```

### `make dev-collect`

- **Comando:**
  ```bash
  make dev-collect
  ```
- **Nombre:** Recolectar tráfico (desarrollo).
- **Descripción:** Ejecuta el servicio `traffic-collector` en un contenedor efímero. El servicio toma de la base de datos las interfaces con estatus activo, consulta a SCAN sus valores de tráfico y los almacena. No actualiza la lista de interfaces (eso lo hace `interface-sync`) y termina con código distinto de cero si no existen interfaces activas. Requiere MongoDB activo (`make dev-up`) y la imagen construida (`make dev-build`).
- **Parámetros disponibles:**
  - `ARGS`: argumentos para el servicio, entre comillas.
    ```bash
    make dev-collect ARGS="--help"
    ```
  - `DEV_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make dev-collect DEV_ENV_FILE=.env.otro
    ```

### `make dev-report`

- **Comando:**
  ```bash
  make dev-report
  ```
- **Nombre:** Generar reportes (desarrollo).
- **Descripción:** Ejecuta el servicio `reports` en un contenedor efímero. El servicio genera reportes de tráfico a partir de los datos almacenados en la base de datos y los exporta como archivos a la carpeta `exports/`. No consulta a SCAN, no recolecta tráfico y no modifica los datos almacenados. Es una ejecución manual, bajo demanda. Requiere MongoDB activo (`make dev-up`) y la imagen construida (`make dev-build`).
- **Parámetros disponibles:**
  - `ARGS`: argumentos del servicio (tipo de reporte, rango de fechas, interfaces, etc.), entre comillas. Los disponibles se consultan con `--help`.
    ```bash
    make dev-report ARGS="--help"
    ```
  - `DEV_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make dev-report DEV_ENV_FILE=.env.otro
    ```

### `make dev-test`

- **Comando:**
  ```bash
  make dev-test
  ```
- **Nombre:** Ejecutar pruebas de todos los servicios.
- **Descripción:** Ejecuta `pytest` de forma secuencial en `interface-sync`, `traffic-collector` y `reports`, cada uno en su propio contenedor efímero. No levanta MongoDB ni otras dependencias (`--no-deps`). Si las pruebas de un servicio fallan, `make` se detiene y no ejecuta las de los servicios restantes. Requiere las imágenes construidas (`make dev-build`).
- **Parámetros disponibles:**
  - `ARGS`: argumentos de `pytest`, entre comillas. Se aplican a los tres servicios.
    ```bash
    make dev-test ARGS="-v"
    ```
  - `DEV_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make dev-test DEV_ENV_FILE=.env.otro
    ```

### `make dev-test-<servicio>`

- **Comando:**
  ```bash
  make dev-test-reports
  ```
- **Nombre:** Ejecutar pruebas de un servicio.
- **Descripción:** Ejecuta `pytest` únicamente en el servicio indicado en el nombre de la regla, en un contenedor efímero y sin levantar MongoDB ni otras dependencias (`--no-deps`). Los servicios válidos son `interface-sync`, `traffic-collector` y `reports`. Requiere la imagen del servicio construida (`make dev-build`).
- **Parámetros disponibles:**
  - `<servicio>`: parte del nombre de la regla. Valores: `interface-sync`, `traffic-collector`, `reports`.
    ```bash
    make dev-test-interface-sync
    make dev-test-traffic-collector
    make dev-test-reports
    ```
  - `ARGS`: argumentos de `pytest`, entre comillas.
    ```bash
    make dev-test-reports ARGS="-x -k nombre_de_la_prueba"
    ```
  - `DEV_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make dev-test-reports DEV_ENV_FILE=.env.otro
    ```

---

## Entorno de producción

Las reglas de producción usan `docker-compose.yml` y `.env.production`. Su comportamiento es equivalente al de las reglas `dev-*` homónimas, salvo lo indicado en cada una.

### `make prod-build`

- **Comando:**
  ```bash
  make prod-build
  ```
- **Nombre:** Construir imágenes de los servicios (producción).
- **Descripción:** Construye las imágenes Docker de `interface-sync`, `traffic-collector` y `reports` usando `docker-compose.yml`. Debe ejecutarse antes de la primera ejecución de los servicios y repetirse cuando cambien las dependencias o el `Dockerfile`. No levanta contenedores ni modifica la base de datos.
- **Parámetros disponibles:**
  - `PROD_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make prod-build PROD_ENV_FILE=.env.otro
    ```

### `make prod-up`

- **Comando:**
  ```bash
  make prod-up
  ```
- **Nombre:** Levantar MongoDB (producción).
- **Descripción:** Inicia únicamente el contenedor de MongoDB en segundo plano. Los servicios no se inician. Debe estar activo antes de ejecutar cualquier servicio, incluida la ejecución automática de `traffic-collector` desde el `crontab`.
- **Parámetros disponibles:**
  - `PROD_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make prod-up PROD_ENV_FILE=.env.otro
    ```

### `make prod-down`

- **Comando:**
  ```bash
  make prod-down
  ```
- **Nombre:** Detener contenedores (producción).
- **Descripción:** Detiene y elimina los contenedores y la red del entorno de producción, incluido MongoDB. Conserva los volúmenes, por lo que los datos no se pierden. No elimina imágenes ni los archivos de `logs/` y `exports/`. Mientras MongoDB esté detenido, los servicios fallarán por falta de conexión, incluida la ejecución del `crontab`.
- **Parámetros disponibles:**
  - `PROD_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make prod-down PROD_ENV_FILE=.env.otro
    ```

### `make prod-logs`

- **Comando:**
  ```bash
  make prod-logs
  ```
- **Nombre:** Ver logs de MongoDB (producción).
- **Descripción:** Muestra en tiempo real los logs del contenedor de MongoDB. La salida queda en seguimiento continuo hasta interrumpirla con `Ctrl+C`; interrumpirla no detiene MongoDB. No muestra los logs de los servicios: esos se escriben en `logs/<servicio>/`.
- **Parámetros disponibles:**
  - `PROD_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make prod-logs PROD_ENV_FILE=.env.otro
    ```

### `make prod-sync`

- **Comando:**
  ```bash
  make prod-sync
  ```
- **Nombre:** Sincronizar interfaces (producción).
- **Descripción:** Ejecuta el servicio `interface-sync` en un contenedor efímero sin TTY. El servicio obtiene la lista de interfaces de red de SCAN y actualiza en la base de datos su existencia y estatus (activa o desincorporada). No recolecta tráfico ni genera reportes. Es una ejecución manual, bajo demanda. Requiere MongoDB activo (`make prod-up`) y la imagen construida (`make prod-build`).
- **Parámetros disponibles:**
  - `ARGS`: argumentos para el servicio, entre comillas.
    ```bash
    make prod-sync ARGS="--help"
    ```
  - `PROD_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make prod-sync PROD_ENV_FILE=.env.otro
    ```

### `make prod-collect`

- **Comando:**
  ```bash
  make prod-collect
  ```
- **Nombre:** Recolectar tráfico (producción).
- **Descripción:** Ejecuta el servicio `traffic-collector` en un contenedor efímero sin TTY. El servicio toma de la base de datos las interfaces con estatus activo, consulta a SCAN sus valores de tráfico del día anterior y los almacena. No actualiza la lista de interfaces y termina con código distinto de cero si no existen interfaces activas. Esta es la regla que debe programarse en el `crontab` y debe ejecutarse una (1) vez por día; su programación es responsabilidad del usuario de operatividad. Requiere MongoDB activo (`make prod-up`) y la imagen construida (`make prod-build`).
  Ejemplo de entrada de `crontab` (ejecución diaria a las 01:00; ajustar la ruta del proyecto):
  ```bash
  0 1 * * * make -C /ruta/al/proyecto prod-collect
  ```
- **Parámetros disponibles:**
  - `ARGS`: argumentos para el servicio, entre comillas.
    ```bash
    make prod-collect ARGS="--help"
    ```
  - `PROD_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make prod-collect PROD_ENV_FILE=.env.otro
    ```

### `make prod-report`

- **Comando:**
  ```bash
  make prod-report
  ```
- **Nombre:** Generar reportes (producción).
- **Descripción:** Ejecuta el servicio `reports` en un contenedor efímero sin TTY. El servicio genera reportes de tráfico a partir de los datos almacenados en la base de datos y los exporta como archivos a la carpeta `exports/`. No consulta a SCAN, no recolecta tráfico y no modifica los datos almacenados. Es una ejecución manual, bajo demanda. Requiere MongoDB activo (`make prod-up`) y la imagen construida (`make prod-build`).
- **Parámetros disponibles:**
  - `ARGS`: argumentos del servicio (tipo de reporte, rango de fechas, interfaces, etc.), entre comillas. Los disponibles se consultan con `--help`.
    ```bash
    make prod-report ARGS="--help"
    ```
  - `PROD_ENV_FILE`: archivo de entorno alternativo.
    ```bash
    make prod-report PROD_ENV_FILE=.env.otro
    ```