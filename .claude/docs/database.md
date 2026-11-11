# MongoDB - Contexto de base de datos

## Visión general
- Versión de MongoDB: 8.0
- Driver/ODM: PyMongo + Pydantic (Python). Todo acceso síncrono.
- Base de datos: `scan_backup` (obtenida de `MONGO_DATABASE` del archivo de variables de entorno `.env.*`)
- Rol de Mongo en el sistema: datos de documentos con esquema flexible.
- Un único servicio escribe en cada colección: `interface-sync` en `interfaces`; `traffic-collector` en `traffic_daily` y `traffic_summary_daily`. `reports` solo lee.

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
          "values": ["activa", "desincorporada"],
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
        { "name": "uq_interface_date", "fields": [{ "name": "interface_id", "order": 1 }, { "name": "date", "order": 1 }], "unique": true },
        { "name": "idx_date", "fields": [{ "name": "date", "order": 1 }], "unique": false }
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
  ]
}
```

## Convenciones
- Nombres de colecciones: `snake_case`, plural.
- Nombres de campos: `snake_case`.
- Fechas siempre en UTC.
- IDs de negocio: UUID string; `_id` solo interno.
- Soft delete: campo `deleted_at` (null = activo), excepto en `interfaces`, que nunca se elimina y usa `status`, y en `traffic_daily` y `traffic_summary_daily`, cuyos documentos del día solo se eliminan físicamente con `traffic-collector --force` (regla 16).
- Todo documento incluye `created_at` y `updated_at`.

## Reglas para Claude
### Esquema y tipos
1. **Fuente de verdad:** el JSON del esquema. Si el código y el JSON difieren, el JSON manda. Todo cambio de esquema se hace primero en el JSON.
2. **`traffic_daily` es un bucket:** un documento por `(interface_id, date)` con un arreglo `samples`. Se espera una muestra cada 5 minutos (288 por día), pero el arreglo puede tener entre 1 y 287 muestras o más de 288 (se almacenan con advertencia) y puede estar vacío en un documento aún no completado. Cada muestra lleva su propio `ts`. El código nunca debe depender de la posición en el arreglo ni de que haya 288 muestras.
3. **Tipos numéricos:** los valores de tráfico y `capacity_gbps` son `Double`. Convertir siempre a `float` en Python antes de guardar, para evitar tipos mixtos (`int`/`float`) en un mismo campo.
4. **Fechas:** `date` es string `YYYY-MM-DD` (solo clave del bucket). `ts`, `created_at` y `updated_at` son `Date` nativo (`datetime` con zona horaria, UTC), nunca `Timestamp` de BSON. `ts` proviene de la fecha UNIX de cada línea del archivo `.log` de SCAN. El formato `HH:MM:SS` se aplica solo al exportar.
5. **Zona horaria y día anterior:** `America/Caracas` (UTC-4 fijo). En agregaciones por hora o día, usar `timezone: "America/Caracas"` en los operadores de fecha. El día anterior es la fecha actual en `America/Caracas` menos un día, calculada una sola vez al inicio de la ejecución. El filtro de muestras del día anterior (de 00:00:00 a 23:59:59) se hace en `America/Caracas`, no en UTC.
6. **Estandarización:** `layer` y `vendor` se almacenan en mayúscula completa (por ejemplo, `BORDE`, `HUAWEI`). Un `vendor` omitido, vacío o `undefined` se almacena como `UNDEFINED`. Todo `vendor` distinto de `UNDEFINED` tiene prioridad: un `UNDEFINED` obtenido nunca sustituye a un `vendor` almacenado distinto de `UNDEFINED`. Las capas son configurables, por lo que `layer` no es un enum.
7. **Estatus:** `Status` (`activa`, `desincorporada`) es un `Enum` de Python, definido en un único lugar y validado en los repositorios.
8. **Capacidad sin dato:** `capacity_gbps` vale `0` cuando la capacidad no está disponible. Un valor ausente o no válido obtenido de SCAN nunca sustituye a una capacidad válida almacenada.
9. **Nombres declarativos:** `scan_url` equivale a la "dirección URL de consulta de tráfico" del ERS y `capacity_gbps` lleva la unidad en el nombre. No renombrar.
10. **Identidad de la interfaz:** `scan_url` la identifica de forma única (`uq_scan_url`) y no cambia. Una interfaz nunca se elimina: si deja de existir en SCAN pasa a `desincorporada` y conserva su histórico bajo su `_id`.
11. **Unidades:**
    - `traffic_daily` guarda los valores crudos sin modificar, en la unidad que entrega SCAN.
    - `traffic_summary_daily` guarda los valores crudos × 8,022 (`SCAN_VALUE_TO_BPS_FACTOR`, equivalente al factor histórico `0.000000008022` expresado en bps en lugar de Gbps). Equivale a bps solo si SCAN reporta bytes/s; esa unidad no está confirmada, y el factor se asume correcto.
    - `capacity_gbps` se asume en Gbps.
    - Si se confirma una unidad distinta, actualizar el factor, el docstring de `Sample` y esta regla.
12. **Escritor único:** solo el servicio indicado en "Visión general" escribe en cada colección. `traffic-collector` y `reports` nunca escriben en `interfaces`.

### Escritura (`traffic-collector`)
13. **Idempotencia y unicidad:** toda escritura de tráfico es `upsert` sobre `(interface_id, date)`, reemplazando `layer` y `samples` completos con `$set`; `created_at` se fija solo al insertar (`$setOnInsert`) y `updated_at` en cada escritura. Nunca existen dos documentos con el mismo `(interface_id, date)`; un documento existente con `samples` vacío se completa. Reejecutar un día debe ser seguro.
14. **Escritura por interfaz y omisión:** cada interfaz se almacena apenas se obtiene y valida, no por lote de capa; lo almacenado se conserva aunque otra interfaz o capa falle. Sin `--force`, una interfaz con su documento del día anterior y al menos una muestra se omite (no se consulta a SCAN ni se modifica). La omisión depende solo de `traffic_daily`, no del resumen, y se resuelve con una sola consulta por capa sobre `(date, layer)` apoyada en `idx_date_layer`, nunca una consulta por interfaz.
15. **Resumen diario en una fase aparte:** se ejecuta después de procesar todas las capas, aunque alguna haya fallado. Genera el resumen de toda interfaz con documento en `traffic_daily` del día anterior (aunque se haya almacenado en una ejecución anterior del mismo día) con al menos una muestra y sin resumen de ese día. Un resumen existente nunca se recalcula ni se actualiza. Se guarda con `upsert` sobre `(interface_id, date)`, con `interface_id`, `layer`, `date`, los cuatro valores, `created_at` (`$setOnInsert`) y `updated_at`. Se lee con un solo cursor sobre los documentos del día y una sola consulta de los resúmenes existentes, sin cargar todo en memoria ni consultar por interfaz. Un error de base de datos detiene la fase completa y conserva los resúmenes ya generados.
16. **Recolección forzada (`--force`):** por interfaz, primero se obtienen, filtran y validan los datos nuevos. Solo si es exitoso se elimina el resumen del día de la interfaz, luego su documento de `traffic_daily` y se almacenan los datos nuevos; el resumen se vuelve a generar en la fase de resumen. Si no se obtienen datos válidos, no se elimina nada. Sin `--force` el servicio nunca elimina datos. Riesgo asumido por el usuario operador: si falla entre eliminar y almacenar, la interfaz queda sin datos del día.
17. **El resumen se calcula en un componente propio:** inyectado en el collector, puro (sin red ni base de datos), no mezclar su lógica con la extracción de datos. Un día sin muestras no genera resumen.
**Reglas de cálculo del resumen diario:** `in_avg` y `out_avg` con la media aritmética de los valores de sus muestras; `in_max` y `out_max` con el máximo de los valores de sus muestras; los cuatro resultados × 8,022. Nunca promediar los máximos dentro del día. Sin redondeo.

### Lectura (`traffic-collector`)
18. **Capas existentes:** son los valores distintos de `interfaces.layer`, sin importar el estatus, procesadas en orden alfabético ascendente, una a la vez. Por capa, una sola lectura de las interfaces `activa` (solo `_id` y `scan_url`); la lista no se actualiza durante la capa.

### Lectura (`reports`)
19. **Colecciones que lee:** solo `interfaces` y `traffic_summary_daily`. Nunca `traffic_daily`. Ninguna operación de escritura.
20. **Capa e interfaces:** la pertenencia a la capa y los datos descriptivos (`name`, `vendor`, `capacity_gbps`, `layer`) salen siempre de `interfaces` (activas y desincorporadas), nunca del campo `layer` del resumen, que es una copia desnormalizada. Para cada capa se obtienen los `_id` de `interfaces` y se filtra el resumen por `interface_id` y `date`, apoyado en `uq_interface_date`. Las capas existentes se procesan una a una: primero las fijas que existan, en el orden `BORDE`, `BRAS`, `CACHING`, `RAI`, `DINT`, `DIST`, `IXP`, y después cualquier otra capa en orden alfabético ascendente. La lista de capas fijas vive en un único lugar del código; no usar un `Enum` para validar capas.
21. **Agregaciones en el servidor** (`$match` + `$sort` por `interface_id`, `date` + `$group`), no en Python. Por interfaz: `in_avg` y `out_avg` con `$avg` de los valores diarios (cada día pesa igual), `in_max` y `out_max` con `$max` de los valores diarios (nunca se promedian), y la cantidad de días. Las interfaces sin resumen en el rango no se incluyen. El `$sort` hace determinista el resultado. Las comparaciones de rango se hacen sobre el string `date`. Una lista de `_id` muy grande se divide en lotes. Los reportes grandes se procesan por capa, liberando la memoria de cada capa al construir su hoja.
22. **Conversión y porcentaje de uso:** los valores del resumen están en bps. `reports` los convierte a Gbps dividiendo entre `1e9`, sin redondeo y una sola vez; `capacity_gbps` no se convierte. El porcentaje de uso no se almacena: se calcula en cada reporte como `max(in_max_gbps, out_max_gbps) / capacity_gbps * 100`, sin límite superior (puede superar 100). Si `capacity_gbps` es 0 (capacidad no disponible), el uso es 0 y la capacidad se exporta como 0. Documentar la fórmula en el docstring.
23. **Una sola capacidad por interfaz:** el porcentaje de meses pasados se calcula con la capacidad actual de `interfaces`, y el nombre, capa y proveedor son los actuales. Es una decisión explícita, no un bug.
24. **Días sin resumen:** una interfaz con menos resúmenes que los días del rango se calcula con los días disponibles. Nunca se rellena ni se interpola. Se informa con advertencia, sin hacer fallida la capa.
