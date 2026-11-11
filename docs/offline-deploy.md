# Despliegue en un servidor sin conexión a internet

Guía para construir las imágenes en un servidor **A** (con internet), empaquetarlas, trasladarlas a un servidor **B** (sin internet), desempaquetarlas y levantar el sistema. La configuración general del entorno se detalla en [production.md](production.md); las reglas del `Makefile` en [makefile.md](makefile.md).

| Servidor | Rol | Requisitos |
|---|---|---|
| A (build) | Descarga dependencias y construye las imágenes | Internet, Git, Docker y Docker Compose v2, Make |
| B (destino) | Ejecuta el sistema | Docker y Docker Compose v2, Make, acceso de red a SCAN. **No** necesita internet, Git ni Python |

> **Importante:** A y B deben tener la misma arquitectura de CPU (`uname -m`, p. ej. `x86_64`). Una imagen construida para `x86_64` no corre en `aarch64`.

> **Importante:** B no puede construir imágenes (no alcanza PyPI ni Docker Hub). Nunca ejecutar `make prod-build` en B.

## Imágenes que se trasladan

| Imagen | Origen |
|---|---|
| `scan-backup/interface-sync:prod` | Construida en A |
| `scan-backup/traffic-collector:prod` | Construida en A |
| `scan-backup/reports:prod` | Construida en A |
| `mongo:8.0` | Descargada de Docker Hub en A |

## En el servidor A

### 1. Clonar y definir el usuario de B

```bash
git clone https://github.com/xanv754/ScanBackup ScanBackup
cd ScanBackup
git switch main
```

El usuario `app` dentro de las imágenes se crea con `APP_UID` y `APP_GID` **en tiempo de construcción**. Deben ser el UID/GID del usuario que operará el sistema en **B**, no el de A. Consultarlos en B:

```bash
# en B
id -u && id -g
```

### 2. Variables de entorno de construcción

```bash
cp .env.production.example .env.production
```

Para construir solo se necesitan `APP_UID` y `APP_GID`, pero Compose exige que las demás variables obligatorias existan: dejar valores temporales en `MONGO_USERNAME`, `MONGO_PASSWORD`, `SCAN_USERNAME` y `SCAN_PASSWORD`. **No** son las definitivas ni se trasladan; las reales se crean en B.

```bash
# ejemplo: B opera con el usuario operador (UID 1001, GID 1001)
sed -i 's/^APP_UID=.*/APP_UID=1001/; s/^APP_GID=.*/APP_GID=1001/' .env.production
sed -i 's/^\(MONGO_USERNAME\|MONGO_PASSWORD\|SCAN_USERNAME\|SCAN_PASSWORD\)=$/\1=temporal/' .env.production
```

### 3. Construir y descargar imágenes

```bash
make prod-build
docker pull mongo:8.0
```

### 4. Verificar

```bash
docker image ls --filter "reference=scan-backup/*" --filter "reference=mongo:8.0"
```

Deben aparecer las cuatro imágenes de la tabla anterior.

### 5. Empaquetar

Se genera un único paquete con las imágenes y los archivos que B necesita para operar (no incluye código fuente ni secretos):

```bash
VERSION=$(git describe --tags --always)
PKG=scan-backup-$VERSION
mkdir -p $PKG/services/{interface-sync,traffic-collector,reports}

docker save \
  scan-backup/interface-sync:prod \
  scan-backup/traffic-collector:prod \
  scan-backup/reports:prod \
  mongo:8.0 | gzip > $PKG/images.tar.gz

cp docker-compose.yml Makefile .env.production.example $PKG/
for svc in interface-sync traffic-collector reports; do
  cp services/$svc/config.yml.example $PKG/services/$svc/
done

tar -czf $PKG.tar.gz $PKG
sha256sum $PKG.tar.gz > $PKG.tar.gz.sha256
ls -lh $PKG.tar.gz
```

Resultado de ejemplo: `scan-backup-v1.0.0.tar.gz` (≈ 400–600 MB, la mayor parte es `mongo:8.0`).

### 6. Trasladar a B

Con red entre A y B:

```bash
scp $PKG.tar.gz $PKG.tar.gz.sha256 operador@10.0.0.20:/home/operador/
```

Sin red entre ellos: copiar ambos archivos a un medio extraíble (USB, disco) y llevarlo a B.

## En el servidor B

Ejemplo con el usuario `operador` y el paquete en `/home/operador/`.

### 1. Verificar integridad y desempaquetar

```bash
cd /home/operador
sha256sum -c scan-backup-v1.0.0.tar.gz.sha256
tar -xzf scan-backup-v1.0.0.tar.gz
cd scan-backup-v1.0.0
```

Debe imprimir `scan-backup-v1.0.0.tar.gz: OK`.

### 2. Cargar las imágenes

```bash
docker load < images.tar.gz
docker image ls --filter "reference=scan-backup/*" --filter "reference=mongo:8.0"
```

Deben aparecer las cuatro imágenes. Con ellas cargadas, Compose no intenta descargar ni construir nada.

### 3. Variables de entorno definitivas

```bash
cp .env.production.example .env.production
chmod 600 .env.production
```

Completar `.env.production` con los valores reales (ver tabla en [production.md](production.md#2-variables-de-entorno)). `APP_UID` y `APP_GID` deben ser los mismos usados al construir en A.

> **Importante:** `MONGO_USERNAME`, `MONGO_PASSWORD` y `MONGO_DATABASE` se aplican solo cuando MongoDB inicializa su volumen por primera vez. Definir los valores definitivos antes de `make prod-up`.

### 4. Archivos de configuración

```bash
for svc in interface-sync traffic-collector reports; do
  cp services/$svc/config.yml.example services/$svc/config.yml
done
```

Editarlos según [production.md](production.md#3-archivos-de-configuración-de-los-servicios) (capas y URLs de SCAN en `interface-sync`, `export_path: /exports` en `reports`). Si el paquete se prepara desde un equipo que ya tiene los `config.yml` definitivos, se pueden copiar en lugar del ejemplo.

### 5. Directorios del host y MongoDB

```bash
make init
make prod-up
make prod-logs      # esperar a que MongoDB esté listo; salir con Ctrl+C
```

`make init` debe ejecutarlo el usuario cuyo UID/GID se usó como `APP_UID`/`APP_GID`.

### 6. Cargar interfaces y verificar

```bash
make prod-sync ARGS="run"
make prod-collect
echo $?                          # 0 = éxito
make prod-report ARGS="--help"
```

La programación diaria de `traffic-collector` en el `crontab` se hace igual que en [production.md](production.md#8-programar-la-recolección-diaria).

## Actualizar un sistema ya desplegado en B

Repetir en A los pasos 1–6 (con el nuevo código y `VERSION`) y en B:

```bash
sha256sum -c scan-backup-v1.1.0.tar.gz.sha256
tar -xzf scan-backup-v1.1.0.tar.gz
docker load < scan-backup-v1.1.0/images.tar.gz
```

Los servicios son efímeros: la siguiente ejecución usa la imagen cargada. No hace falta reiniciar MongoDB ni tocar `.env.production`, los `config.yml`, `logs/` ni `exports/` de la instalación existente. Si el nuevo paquete trae cambios en `docker-compose.yml` o `Makefile`, copiarlos a la carpeta de operación de B y ejecutar `make prod-up` para recrear MongoDB; el volumen de datos se conserva.

> **Observación:** Evitar actualizar durante la ventana de ejecución del `crontab`. Para liberar espacio, eliminar imágenes antiguas con `docker image prune`.

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `exec format error` al ejecutar un servicio | Arquitectura distinta entre A y B | Construir en un servidor A con la misma arquitectura que B |
| Los servicios no pueden escribir en `logs/` o `exports/` | `APP_UID`/`APP_GID` usados al construir no coinciden con el usuario de B | Reconstruir en A con el UID/GID correcto y repetir el traslado |
| Compose intenta construir o descargar imágenes | Las imágenes no están cargadas, o `docker load` falló | Verificar con `docker image ls`, repetir `docker load`. No ejecutar `make prod-build` en B |
| `sha256sum -c` falla | Paquete corrupto durante el traslado | Copiar nuevamente el paquete |
| `MONGO_USERNAME is required` al ejecutar `make` | Falta `.env.production` o tiene variables vacías en B | Repetir el paso 3 de B |
| El servicio falla y `config.yml` aparece como directorio | `config.yml` no existía al ejecutar el servicio | Eliminar el directorio y crear el archivo desde su ejemplo |
