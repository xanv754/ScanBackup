# Sistema CPGRD
Un sistema diseñado para la colleción de data para generación de reportes y otros archivos para la coordinación CPGRD.

# Variables de Entorno
El sistema require un archivo `.env.production` o `.env` con las siguientes variables de entorno:

```bash
URI_MONGO="mongodb://user:password@server:port/name_database"
URI_POSTGRES="postgres://user:password@server:port/name_database"
```

> *Nota*: Para ejecutar las **pruebas unitarias** o trabajar en desarrollo, se recomienda un archivo `.env.development` con las variables de entorno.
