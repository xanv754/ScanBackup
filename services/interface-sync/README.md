# Interface Sync

Sincroniza las interfaces de red de SCAN con la colección `interfaces` de MongoDB.

## Comando

```bash
make dev-sync ARGS="run"
```

`run` carga `config.yml`, verifica SCAN y la base de datos, y procesa cada página declarada (scraping, validación y almacenamiento). Muestra un spinner y los mensajes de avance por terminal, y registra los eventos en `/logs/interface-sync.log`.

Estado actual: la verificación de SCAN, la verificación de la base de datos y el almacenamiento están pendientes (`TODO`).

| Código | Significado |
|---|---|
| `0` | Todas las páginas exitosas |
| `1` | Al menos una página fallida |
| `2` | Error general del proceso (configuración inválida, credenciales ausentes, SCAN o base de datos no disponibles, error inesperado) |
