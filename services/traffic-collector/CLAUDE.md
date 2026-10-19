## Validaciones
Antes de realizar consultas a SCAN, `traffic-collector` valida:

1. Que existan interfaces activas en la base de datos. Si no existen, registra una advertencia en terminal y en su log, y termina con código distinto de cero.
2. Que no exista ya un registro de tráfico del día en curso. Si existe, registra una advertencia en terminal y en su log, y termina con código distinto de cero sin realizar consultas. Esto garantiza la regla de una (1) ejecución diaria, independientemente de cómo se haya lanzado el servicio.