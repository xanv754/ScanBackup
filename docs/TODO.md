# TO-DO
> Tareas pendientes de realizar

- [x] Realizar conexiones a la base de datos
  - [x] Si la base de datos no existe, crearla.
  - [x] Realizar migraciones por CLI.
  - [x] Realizar rollback por CLI.
- [x] Crear Makefile para ejecutar el sistema.
- Funciones para procesamiento de datos. Obtención en dataframes.
  - [ ] Obtener todo el tráfico de un día de una capa.
  - [ ] Obtener todo el tráfico de un mes de una capa.


# FIXME
> Tareas pendientes de arreglar
- [ ] Salidas de los logs en consola. Solo las que sean necesarias.
- [ ] Reapertura de "emergencia" conexión a la base de datos si ya se ha cerrado la conexión previamente.

# REFACTOR
> Tareas pendientes de revisar/modernizar
- [x] Salidas de los logs en consola. Buscar todos las salidas de los logs y definir que son necesarias realmente imprimir por consola.
- [x] Carga de variables de entorno en el archivo de configuración.
- [ ] Cambio clase ResponseTransform para aplicar patrón Adapter.
- [ ] Cambio del nombre de la tabla *ip_history* -> *ip_bras*.
- [ ] Cambio de nombre del print en logHandler -> *printStr*.
- [ ] Agregar que *printStr* sea un método de clase.

# UNIT TEST
> Tareas pendientes de realizar para las pruebas unitarias
- [ ] Test de carga de datos del actualizador de las capas.
- [ ] Agregar test para PostgreSQL.