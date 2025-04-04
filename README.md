# Sistema CPGRD
Un sistema diseñado para la colleción de data para generación de reportes y otros archivos para la coordinación CPGRD.

# Variables de Entorno
El sistema require un archivo `.env` con las siguientes variables de entorno:

```bash
URI_MONGO="mongodb://user:password@server:port/name_database"
URI_POSTGRES="postgres://user:password@server:port/name_database"
```

Para ejecutar las **pruebas unitarias**, se requiere un archivo `.env` con las siguientes variables de entorno:

```bash
URI_TEST_MONGO="mongodb://user:password@server:port/name_database"
URI_TEST_POSTGRES="postgres://user:password@server:port/name_database"
```
