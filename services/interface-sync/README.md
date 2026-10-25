# Interface Sync

Sincroniza las interfaces de red de SCAN con la colección `interfaces` de MongoDB.

## Comando

```bash
make dev-sync ARGS="run"
```

`run` carga `config.yml`, verifica SCAN y la base de datos, y procesa cada página declarada (scraping, validación y almacenamiento). Muestra un spinner y los mensajes de avance por terminal, y registra los eventos en `/logs/interface-sync.log`.

## Verificación de SCAN

Es lo primero que se ejecuta tras cargar `config.yml`. Se deriva la ruta base (esquema y host) de cada página, sin repetidas, y se consulta cada una con la autenticación configurada. Una ruta responde si SCAN contesta con cualquier estatus HTTP salvo `401` (credenciales rechazadas) y `>= 500` (error de SCAN); un `404` en la ruta base cuenta como respuesta. Se verifican todas las rutas, y el resultado de cada una se registra en el log (`info` o `error`) y se muestra por terminal. Si alguna no responde, no se procesa ninguna página y el proceso termina con código `2`.

## Almacenamiento

Cada página, tras el scraping y la validación, registra las interfaces nuevas, actualiza las existentes y reactiva las `desincorporada` que reaparecen. Cuando terminan todas las páginas, cada capa cuyas páginas fueron todas exitosas desincorpora las interfaces `activa` que ya no aparecen en su listado. Una capa con alguna página fallida no se desincorpora.

El vendor `UNDEFINED` nunca sustituye a un vendor concreto almacenado; un vendor concreto siempre sustituye al almacenado. Una capacidad `0` por defecto no sustituye a una almacenada distinta de `0`.

El resultado del scraping y el de la base de datos se informan por separado; si cualquiera falla, el proceso termina con código `1`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `persistence/` | Todo el acceso a MongoDB: conexión, `InterfaceDocument` y `InterfaceRepository` (`pydantic-mongo`) |
| `synchronization/` | Lógica pura de qué cambia (`InterfaceChangePlanner`) y desincorporación por capa (`LayerDecommissioner`) |

| Código | Significado |
|---|---|
| `0` | Todas las páginas exitosas |
| `1` | Al menos una página fallida (scraping o base de datos) o una desincorporación de capa fallida |
| `2` | Error general del proceso (configuración inválida, credenciales ausentes, SCAN o base de datos no disponibles, error inesperado) |
