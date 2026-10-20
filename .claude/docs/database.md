# MongoDB - Contexto de base de datos

## Visión general
- Versión de MongoDB: 8.0
- Driver/ODM: Motor + Pydantic (Python) + PyMongo
- Base de datos: `scanbackuo_db` (obtenida de `MONGO_DATABASE` del archivo de variables de entorno `.env.*`)
- Rol de Mongo en el sistema: datos de documentos con esquema flexible.

## Colecciones, Campos, Índices y Relaciones
```json
{
  "collections": [
    {
      "name": "interfaces",
      "fields": [
        {
          "name": "_id",
          "type": "ObjectId",
          "required": true,
          "isArray": false
        },
        {
          "name": "layer",
          "type": "String",
          "required": true,
          "isArray": false
        },
        {
          "name": "name",
          "type": "String",
          "required": true,
          "isArray": false
        },
        {
          "name": "vendor",
          "type": "String",
          "required": true,
          "isArray": false
        },
        {
          "name": "capacity_gbps",
          "type": "Double",
          "required": true,
          "isArray": false
        },
        {
          "name": "scan_url",
          "type": "String",
          "required": true,
          "isArray": false
        },
        {
          "name": "status",
          "type": "Enum",
          "values": ["activo", "desincorporada"],
          "required": true,
          "isArray": false
        },
        {
          "name": "created_at",
          "type": "Date",
          "required": true,
          "isArray": false
        },
        {
          "name": "updated_at",
          "type": "Date",
          "required": true,
          "isArray": false
        }
      ],
      "indexes": [
        { "name": "uq_scan_url", "fields": [{ "name": "scan_url", "order": 1 }], "unique": true },
        { "name": "idx_status", "fields": [{ "name": "status", "order": 1 }], "unique": false },
        { "name": "idx_layer_name", "fields": [{ "name": "layer", "order": 1 }, { "name": "name", "order": 1 }], "unique": false }
      ]
    },
    {
      "name": "traffic_daily",
      "fields": [
        {
          "name": "_id",
          "type": "ObjectId",
          "required": true,
          "isArray": false
        },
        {
          "name": "interface_id",
          "type": "ObjectId",
          "required": true,
          "isArray": false
        },
        {
          "name": "layer",
          "type": "String",
          "required": true,
          "isArray": false
        },
        {
          "name": "date",
          "type": "String",
          "required": true,
          "isArray": false
        },
        {
          "name": "samples",
          "type": "Array",
          "required": true,
          "isArray": true,
          "fields": [
            {
              "name": "ts",
              "type": "Date",
              "required": true,
              "isArray": false
            },
            {
              "name": "in_avg",
              "type": "Double",
              "required": true,
              "isArray": false
            },
            {
              "name": "out_avg",
              "type": "Double",
              "required": true,
              "isArray": false
            },
            {
              "name": "in_max",
              "type": "Double",
              "required": true,
              "isArray": false
            },
            {
              "name": "out_max",
              "type": "Double",
              "required": true,
              "isArray": false
            }
          ]
        }
      ],
      "indexes": [
        { "name": "uq_interface_date", "fields": [{ "name": "interface_id", "order": 1 }, { "name": "date", "order": 1 }], "unique": true },
        { "name": "idx_date_layer", "fields": [{ "name": "date", "order": 1 }, { "name": "layer", "order": 1 }], "unique": false }
      ]
    },
    {
      "name": "traffic_summary_daily",
      "fields": [
        {
          "name": "_id",
          "type": "ObjectId",
          "required": true,
          "isArray": false
        },
        {
          "name": "interface_id",
          "type": "ObjectId",
          "required": true,
          "isArray": false
        },
        {
          "name": "layer",
          "type": "String",
          "required": true,
          "isArray": false
        },
        {
          "name": "date",
          "type": "String",
          "required": true,
          "isArray": false
        },
        {
          "name": "in_avg",
          "type": "Double",
          "required": true,
          "isArray": false
        },
        {
          "name": "out_avg",
          "type": "Double",
          "required": true,
          "isArray": false
        },
        {
          "name": "in_max",
          "type": "Double",
          "required": true,
          "isArray": false
        },
        {
          "name": "out_max",
          "type": "Double",
          "required": true,
          "isArray": false
        }
      ],
      "indexes": [
        { "name": "uq_interface_date", "fields": [{ "name": "interface_id", "order": 1 }, { "name": "date", "order": 1 }], "unique": true },
        { "name": "idx_date_layer", "fields": [{ "name": "date", "order": 1 }, { "name": "layer", "order": 1 }], "unique": false }
      ]
    }
  ],
  "relationships": [
    {
      "from": "interfaces._id",
      "to": "traffic_daily.interface_id",
      "type": "one-to-many"
    },
    {
      "from": "interfaces._id",
      "to": "traffic_summary_daily.interface_id",
      "type": "one-to-many"
    }
  ],
  "denormalized": [
    { "field": "layer", "source": "interfaces.layer", "in": ["traffic_daily", "traffic_summary_daily"] }
  ]
}
```

## Convenciones
- Nombres de colecciones: `snake_case`, plural.
- Nombres de campos: `snake_case`.
- Fechas siempre en UTC.
- IDs de negocio: UUID string; `_id` solo interno.
- Soft delete: campo `deleted_at` (null = activo).
- Todo documento incluye `created_at` y `updated_at`.

## Reglas para Claude
### Esquema y tipos
1. **Fuente de verdad:** el JSON del esquema. Si el código y el JSON difieren, el JSON manda. Todo cambio de esquema se hace primero en el JSON.
2. **`traffic_daily` es un bucket:** un documento por `(interface_id, date)` con un arreglo `samples` de 288 muestras. Cada muestra lleva su propio `ts`. El código nunca debe depender de la posición en el arreglo.
3. **Tipos numéricos:** los valores de tráfico y `capacity_gbps` son `Double`. Convertir siempre a `float` en Python antes de guardar, para evitar tipos mixtos (`int`/`float`) en un mismo campo.
4. **Fechas:** `date` es string `YYYY-MM-DD` (solo clave del bucket). `ts`, `created_at` y `updated_at` son `Date` nativo (`datetime`), nunca `Timestamp` de BSON. El formato `HH:MM:SS` se aplica solo al exportar.
5. **Zona horaria:** `America/Caracas` (UTC-4 fijo). En agregaciones por hora o día, usar `timezone: "America/Caracas"` en los operadores de fecha.
6. **Enums en código:** `Layer` (`borde`, `bras`, `caching`, `rai`, `ixp`, `dint`, `dist`) y `Status` (`activo`, `desincorporada`) como `Enum` de Python, definidos en un único lugar y validados en los repositorios. Los valores son los del dominio, en español.
7. **Nombres declarativos:** `scan_url` equivale a "dirección" del ERS y `capacity_gbps` lleva la unidad en el nombre. No renombrar.

### Escritura (`traffic-collector`)
8. **Idempotencia:** toda escritura de tráfico es `upsert` sobre `(interface_id, date)`, reemplazando `samples` completo con `$set`. Reejecutar un día debe ser seguro.
9. **Orden de escritura:** primero el bucket en `traffic_daily` y después el resumen en `traffic_summary_daily`. Si falla cualquiera de las dos, la interfaz cuenta como fallo del día y el servicio termina con código distinto de cero.
10. **El resumen se calcula en un componente propio:** inyectado en el collector, no mezclar su lógica con la extracción de datos.
**Reglas de cálculo del resumen diario:** `in_avg` y `out_avg` con promedio, `in_max` y `out_max` con máximo. Nunca promediar los máximos dentro del día.

### Lectura (`reports`)
 
11. **Reportes mensuales, semanales y quincenales** leen `traffic_summary_daily`, no `traffic_daily`. Los reportes de valores crudos leen `traffic_daily`.
12. **El porcentaje de uso no se almacena:** Se calcula al generar el reporte con la capacidad actual de `interfaces`: `in_max / (capacity_gbps * 1e9) * 100`. Los datos están en bps y la capacidad en Gbps, así que la conversión es obligatoria. Documentar la fórmula en el docstring.
13. **Agregaciones en el servidor** (`$group`), no en Python. Los reportes grandes se procesan con cursor y streaming hacia openpyxl, sin cargar todo en memoria.
14. **Una sola capacidad por interfaz:** el porcentaje de meses pasados se calcula con la capacidad actual. Es una decisión explícita, no un bug.
