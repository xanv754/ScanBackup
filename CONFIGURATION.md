# Archivo de Configuración

Este documento describe todos los parámetros disponibles en el archivo `config.yml` utilizados por el sistema.

---

# Configuración Completa de Ejemplo

```yaml
layers:
  bbip:
    schema_collection: "BBIP"
    names:
      - "example"
  ip:
    schema_collection: "IP"
    names:
      - "example"

database:
  host: "localhost"
  port: "27017"
  name: "scanbackup_db"
  user: "user"
  password: "password"

metadata:
  dir_data: "data"

  logs:
    dir_name: "logs"
    filename: "scanbackup"
    extension: "log"
    msg_format: "%(asctime)s %(levelname)s %(message)s"
    date_format: "%Y-%m-%d %H:%M:%S"

  scanner:
    dir_storage: "data"
    dir_sources: "sources"
    extension: "csv"
    date_format: "%Y-%m-%d"
    file_delimiter: ";"
    port_separator_replacement: "&"
    space_separator_replacement: "_"
    scan_credentials:
      username: "username"
      password: "password"

  reports:
    preffix_name: "ScanBackup"
    date_format: "%Y%m%d_%H%M%S"
```

---

# layers

Define los nombres de las capas existentes en SCAN que se desea respaldar.

## layers.<grupo>

Define la configuración de una capa de SCAN para el sistema.

### schema_collection

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Define el esquema de estructura que se utilizará para almacenar los datos obtenidos en la base de datos del sistema.

#### Ejemplo

```yaml
schema_collection: "BBIP"
```

### Valores Disponibles

| Grupo        | Valor  |
| ------------ | ------ |
| `layer.bbip` | `BBIP` |
| `layer.ip`   | `IP`   |

---

### names

| Propiedad         | Valor        |
| ----------------- | ------------ |
| Tipo              | list[string] |
| Obligatorio       | Sí           |

#### Descripción

Define el nombre de todas las colecciones que se utilizarán para almacenar los datos obtenidos en la base de datos del sistema.

#### Ejemplo

```yaml
names:
  - capa1
  - capa2
  - capa3
```

> Nota: El campo **no** es case sensitive. Todo valor será transformado a mayúculas.

---

# database

Configuración de conexión a la base de datos de MongoDB.

## host

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Host de conexión a la base de datos.

#### Ejemplo

```yaml
host: "localhost"
```

---

## port

| Propiedad         | Valor   |
| ----------------- | ------- |
| Tipo              | integer |
| Obligatorio       | Sí      |

#### Descripción

Puerto de conexión a la base de datos.

#### Ejemplo

```yaml
port: 27017
```

---

## name

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Nombre de la base de datos.

#### Ejemplo

```yaml
name: my_database
```

---

## user

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |
| Valor por defecto | N/A    |

#### Descripción

Nombre de usuario para conexión a la base de datos.

#### Ejemplo

```yaml
user: admin
```

---

## password

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |
| Valor por defecto | N/A    |

#### Descripción

Contrasena para conexión a la base de datos.

#### Ejemplo

```yaml
password: secret
```

---

# metadata

Configuración de toda la metadata generada o requerida para el sistema.

## dir_data

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Nombre de la carpeta para almacenar o buscar cualquier información que pueda necesitar o exportar el sistema.

#### Ejemplo

```yaml
dir_data: data
```

---

# metadata.logs

Configuración de la metadata de los logs del sistema.

## dir_name

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Nombre de la carpeta donde se almacenarán los logs del sistema.

---

## filename

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Nombre del archivo donde se almacenarán los logs del sistema.

---

## extension

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Extensión del archivo donde se almacenarán los logs del sistema. Se recomienda utilizar la extensión `.log`.

---

## msg_format

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |
| Valor por defecto | N/A    |

#### Descripción

Formato de los mensajes que se utilizarán para registrar eventos en el log del sistema. Léase [atributos de Logging](https://docs.python.org/3/library/logging.html#logrecord-attributes) para obtener más información sobre los formatos válidos para el logging.

### Ejemplo
```yaml
msg_format: "%(asctime)s %(levelname)s %(message)s"
```

---

## date_format

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |


#### Descripción

Formato de fecha para el logging. Léase [Formatos para fechas](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) para obtener más información sobre los formatos de fechas válidos para el logging.

### Ejemplo
```yaml
date_format: "%Y-%m-%d %H:%M:%S"
```

---

# metadata.scanner

Configuración utilizada por el módulo de recolector del tráfico existente en SCAN.

## dir_storage

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Nombre de la carpeta donde se almacenarán los datos recolectados por el scanner.

---

## dir_sources

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Nombre de la carpeta donde se esperan encontrar las fuentes de enlaces a recolectar data por el scanner.

---

## extension

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Nombre de la extensión de los archivos a recolectar por el scanner.

---

## date_format

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Formato de fecha para los datos de tráfico obtenido. Léase [Formatos para fechas](https://www.gnu.org/software/coreutils/manual/html_node/Date-conversion-specifiers.html) para obtener más información sobre los formatos de fechas válidos para el scanner.

### Ejemplo
```yaml
date_format: "%Y-%m-%d"
```

---

## file_delimiter

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Símbolo de separador de data. Este símbolo será utilizado para separar la data de tráfico obtenida.

> Nota: Este símbolo debe concordar con el delimitador de la fuente de enlaces sumistrada al scanner.

### Ejemplo
```yaml
file_delimiter: ";"
```

---

## port_separator_replacement

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |
| Valor por defecto | N/A    |

#### Descripción

Símbolo para reemplazar el símbolo "/" separador de puertos en los nombres de los enlaces de red.

> Advertencia: Recomendamos **NO** utilizar el símbolo "\\".

---

## space_separator_replacement

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |
| Valor por defecto | N/A    |

#### Descripción

Símbolo para reemplazar el espacio en los nombres de los enlaces de red.

> Advertencia: Recomendamos **NO** utilizar el símbolo "\\".

---

# metadata.scanner.scan_credentials

Credenciales de la página de SCAN.

## username

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Nombre de usuario para el ingreso de sesión de SCAN.

---

## password

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Contrasena de usuario para el ingreso de sesión de SCAN.

---

# metadata.reports

Configuración para la generación de reportes.

## preffix_name

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |

#### Descripción

Texto a agregar al inicio de los nombres de los archivos de reportes generados por el sistema.

---

## date_format

| Propiedad         | Valor  |
| ----------------- | ------ |
| Tipo              | string |
| Obligatorio       | Sí     |


#### Descripción

Formato de fecha para los nombres de los archivos de reportes generados por el sistema.  Léase [Formatos para fechas](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) para obtener más información sobre los formatos de fechas válidos.

### Ejemplo
```yaml
date_format: "%Y-%m-%d_%H-%M-%S"
```

---



