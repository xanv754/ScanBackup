# Resumen
DataBackup es el corazón y cerebro de ScanBackup. Es el encargado de realizar todos los procesos para obtener los resultados más útiles para los analistas de tráfico. 

Se encarga de almacenar la información de las interfaces, de almacenar la información de tráfico de las interfaces, de recuperar la información almacenada y crear reportes por todas las capas para su fácil consumo.

# Objetivos
## Peticiones
- Realizar peticiones rápidas de tráfico a todas las interfaces existentes en SCAN.

## Almacenamiento
- Almacenamiento del listado de interfaces existentes en el sistema SCAN.
- Almacenamiento de la data cruda del día de todas las interfaces obtenidas de SCAN.
- Almacenamiento de un resumen de la data (promedios) del día de todas las interfaces obtenidas.

## Reportes
- Exportación del listado de interfaces activo.
- Exportación de la data almacenada cruda por capas.
- Exportación de la data resumida por capas.


# Estructura
## General
- `data/`: Carpeta base en donde se encuentran todos los archivos de texto plano creados o necesarios para el sistema.
- `scanbackup/`: Código fuente.
- `tests/`: Pruebas unitarias del sistema.

## Código Fuente
La arquitectura del sistema se basa en Clean Architecture.

```
domain ← application ← infrastructure
```

En donde:

- `domain/`: Entidades, repositorios y servicios. Cero dependencias externas, cero conocimiento de infraestructura (nada de `_id`, DTOs, schemas de MongoDB).
- `application/`: Casos de uso. Aquí vive la validación de reglas de negocio. 
- `infrastructure/`: Implementaciones concretas.
  - `infrastructure/persistence/mongodb`: Conexiones con la base de datos MongoDB. Repositorios Mongo, constantes para la base de datos, esquemas, validaciones, índices.
  - `infrastructure/readers/`: Lectores de data (CSV, Excel, etc.), con `BaseReader` abstracto.
  - `infrastructure/writers/`: Exportadores de data (CSV, Excel, etc.), con `BaseWriter` abstracto.
- `shared/`: Utilidades transversales. Constantes del sistema, configuración del sistema, errores personalizados, salidas por terminal con `rich`, tipos de datos del sistema, etc.


# CLI

Construido con Click. Comando de entrada:

```bash
python -m scanbackup --help
```

Todo el sistema debe contener con un CLI sólido que permita realizar las operaciones necesarias para su uso.