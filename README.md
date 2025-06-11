# Sistema CPGRD
Un sistema diseñado para la colleción de data para generación de reportes y otros archivos para la coordinación CPGRD.

# Variables de Entorno
El sistema require un archivo `.env.production` o `.env` con las siguientes variables de entorno:

```bash
URI_MONGO="mongodb://user:password@server:port/name_database"
URI_POSTGRES="postgres://user:password@server:port/name_database"
```

> *Nota*: Para ejecutar las **pruebas unitarias** es necesario un archivo `.env.test` con las variables de entorno. Si se desea trabajar en el entorno de desarrollo, se debe usar el archivo `.env.development`.
