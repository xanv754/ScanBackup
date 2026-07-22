# ScanBackup

Sistema para recolectar, respaldar y gestionar los datos de tráfico de red del sistema de monitoreo **SCAN**.

## Propósito

SCAN es un sistema de monitoreo que muestra los valores de tráfico de todas las interfaces de red cada 5 minutos, pero solo conserva la información del día anterior, sin histórico. ScanBackup consulta esa información diariamente y la respalda, permitiendo visualizar y analizar datos de días, meses o incluso años anteriores.

El sistema completo está dividido en dos proyectos independientes dentro de este repositorio:

### DataBackup

Es el sistema principal: recolecta, importa, exporta y almacena en MongoDB el tráfico de todas las capas del BackBoneIP (Enlaces Internacionales, Agregación/BRAS, Caching, Clientes Dedicados/RAI, Distribución Internet/Regional, IXP, entre otras), y genera resúmenes y reportes sobre esa data.

Más detalles, instalación, configuración y uso de su CLI en [`DataBackup/README.md`](./DataBackup/README.md).

### SourceScrapper

Módulo auxiliar que, mediante *web scrapping*, obtiene de la plataforma SCAN el listado de interfaces de red disponibles a consultar (enlace, URL, capacidad y modelo del equipo). SCAN no expone una API para esta información, por lo que este proyecto la extrae directamente del HTML. Su salida (CSV) es la fuente que luego DataBackup respalda.

Más detalles, instalación, configuración y uso de su CLI en [`SourceScrapper/README.md`](./SourceScrapper/README.md).

## Requerimientos

Para levantar ambos proyectos juntos con Docker Compose (forma recomendada):

- Docker y el plugin Docker Compose (`docker compose`)
- `make` (opcional, pero simplifica el uso del `docker-compose.yml`)
- Un archivo `config.yml` propio de cada proyecto (ver [Configuración](#configuración))

Para instalar y correr cada proyecto de forma nativa (sin Docker), consulta los requerimientos específicos en el README de cada uno ([DataBackup](./DataBackup/README.md#requerimientos), [SourceScrapper](./SourceScrapper/README.md#requisitos)).

## Configuración

Cada proyecto necesita su propio `config.yml` para funcionar, tanto en ejecución nativa como en Docker:

- `DataBackup/config.yml` — conexión a MongoDB, capas a respaldar, credenciales de SCAN, rutas de datos/logs. Puede partir de `DataBackup/config.example.yml`. Ver [Configuración de DataBackup](./DataBackup/CONFIGURATION.md).
- `SourceScrapper/config.yml` — URLs de SCAN por capa, credenciales de scrapping, formato de exportación. [Configuración de SourceScrapper](./SourceScrapper/README.md#estructura).

Para uso con `docker compose`, `DataBackup` requiere además `DataBackup/config.docker.yml` (igual al `config.yml` nativo, pero con `database.host: "mongodb"` en vez de `localhost`, ya que dentro de la red de Docker el servicio de MongoDB se resuelve por su nombre de servicio, no por `localhost`).

También se necesita un `.env` en la raíz del repositorio con las credenciales de arranque de MongoDB, a partir de `.env.example`:

```bash
cp .env.example .env
```

Las variables `MONGO_APP_*` del `.env` deben coincidir con el bloque `database` de `DataBackup/config.docker.yml`.

## Uso con Docker Compose

```bash
cp .env.example .env   # completar con tus credenciales
make up
```

Esto levanta MongoDB, `databackup` y `sourcescrapper` en una red interna compartida. `databackup` y `sourcescrapper` son imágenes de CLI (no procesos de larga duración), por lo que sus comandos se ejecutan puntualmente con `make databackup` y `make scrape` (ver tabla abajo).

### Reglas del Makefile

| Regla | Qué hace |
| --- | --- |
| `make up` | Levanta todos los servicios en segundo plano. |
| `make build` | Reconstruye las imágenes y levanta los servicios. |
| `make down` | Detiene y elimina los contenedores (conserva volúmenes). |
| `make stop` | Detiene los contenedores sin eliminarlos. |
| `make start` | Reinicia contenedores ya creados (sin recrear). |
| `make restart` | Reinicia todos los servicios (`down` + `up`). |
| `make clean` | Elimina contenedores + volúmenes (borra la data de MongoDB). |
| `make fclean` | Limpieza completa: contenedores, volúmenes e imágenes construidas. |
| `make re` | Limpieza completa + reconstrucción desde cero. |
| `make logs` | Sigue los logs de todos los servicios (`make logs SERVICE=mongodb` para uno solo). |
| `make ps` | Muestra el estado de los contenedores. |
| `make scrape` | Ejecuta el scrapper de fuentes (`make scrape LAYER=all`). |
| `make databackup` | Ejecuta un comando del CLI de databackup (`make databackup CMD="database setup"`). |
| `make mongo-shell` | Abre un `mongosh` autenticado como el usuario de la app. |
| `make help` | Muestra la ayuda con todas las reglas disponibles. |

## Más información

Para el detalle de arquitectura, configuración completa, CLI y pruebas de cada proyecto, consulta el [README de DataBackup](./DataBackup/README.md) y el [README de SourceScrapper](./SourceScrapper/README.md).
