# Reto 1 · Infraestructura local y configuración

> **Rama:** `feat/phase-01-infra`. Al terminar, abre una PR contra `main` con una descripción. La protección de `main` llega en la Fase 2, pero el flujo de ramas y PRs se practica desde ahora.
> **Cuando termines:** di «listo para review».

## Contexto

Hasta ahora CrateDigger corre sobre SQLite y no tiene ninguna app. Antes de modelar el catálogo (Fase 3), la base tiene que estar lista:
- Las bases de datos reales en contenedores, iguales para cualquiera que clone el repo.
- La configuración, fuera del código (12-factor).
- Un modelo de usuario propio, porque cambiarlo más adelante es de las migraciones más dolorosas de Django.
- Lo mínimo de observabilidad: saber si la app está sana y poder seguir una petición en los logs.

Parte del trabajo ya está hecho en la Fase 0: `config/env.py` lee el entorno con pydantic-settings, valida los tipos y falla al arrancar si falta `DJANGO_SECRET_KEY`. Ahora toca **ampliarlo**, no rehacerlo.

Dos pendientes de la review de la Fase 0 se resuelven aquí:
- `EnvSettings` no fija la política de variables desconocidas. En cuanto el `.env` lleve también las variables que necesita Compose, eso importa.
- Dónde vive `BASE_DIR`.

## Objetivo

Que con `docker compose up -d` y `uv run python manage.py migrate` la app corra contra PostgreSQL 17 y MongoDB 8 en contenedores, con:
- Configuración 12-factor, tipada y validada.
- Un `User` propio desde el primer `migrate`.
- Un endpoint `/health/` que diga la verdad sobre las dependencias.
- Un identificador por petición que aparezca en la respuesta y en los logs.

## Requisitos

### 1. Compose

- Un `compose.yaml` con dos servicios: `postgres:17` y `mongo:8`.
- Los datos de cada uno en un **volumen nombrado**.
- Un **healthcheck** en cada servicio, con el comando que recomiende su documentación o su imagen oficial.
- Las credenciales se leen de `.env`; ninguna va escrita en `compose.yaml`.
- Los puertos se publican solo en `127.0.0.1`, no en todas las interfaces.
- **Sin** servicio para la app: Django sigue corriendo en tu máquina con `uv run`. El contenedor de la app llega en la Fase 10.

### 2. Settings

- Amplía `EnvSettings` con lo necesario para conectar a PostgreSQL (con **psycopg 3**) y a MongoDB.
- Resuelve cómo conviven en un único `.env` las variables de Compose y las de Django (pregunta de diseño 1).
- Todo lo que contenga una contraseña se trata como secreto, sin que acabe en un `repr` ni en un log.
- `DATABASE_URL` deja de apuntar a SQLite. Borra tu `db.sqlite3` local.

### 3. `.env.example`

- Documenta **cada** variable: qué es y, si aplica, cómo generarla.
- Solo contiene marcadores, nunca valores utilizables.
- Copiar `.env.example` a `.env` y rellenar los marcadores debe bastar para levantar todo.

### 4. App `accounts`

- En `cratedigger/accounts/`, con un modelo `User` propio y `AUTH_USER_MODEL` apuntando a él.
- Debe existir **antes del primer `migrate` contra PostgreSQL**.
- Registrado en el admin, de forma que se puedan crear y editar usuarios desde ahí.
- Por ahora sin campos extra, salvo que justifiques alguno. Los roles llegan en la Fase 5.

### 5. App `core`: `/health/`

- Una vista **sin DRF** en `/health/` que compruebe PostgreSQL y MongoDB.
- Devuelve `200` si todo está bien y `503` si falla alguna dependencia, con un cuerpo JSON que detalle el estado de cada una.
- Ninguna comprobación puede dejar la petición colgada: define timeouts cortos y explícitos.
- El cliente de MongoDB **no** se crea en cada petición.

### 6. Middleware `X-Request-ID`

- Si la petición trae la cabecera `X-Request-ID` **y es válida**, se reutiliza. Si no, se genera uno.
- El id se devuelve en la cabecera `X-Request-ID` de la respuesta.
- El id aparece en **cada** línea de log emitida mientras la petición está dentro de tu middleware (entre que entra y que sale), también en las de otros módulos. Configura `LOGGING` para ello.
- Cada petición deja **al menos una** línea de log con su id, también cuando todo va bien.
- Al salir del middleware, el id no puede quedar vivo para la siguiente petición.
- *Aclaración (2026-10-05):* las líneas que Django emite fuera de la cadena de middlewares (`django.server` y el aviso de `django.request` para respuestas 4xx/5xx devueltas por la vista) no están obligadas a llevar el id. Si lo consigues sin fugas, suma.
- Decide qué significa «válida» y justifícalo.

### 7. Tests

- Cada app nueva tiene su propio `tests/`.
- `/health/`: un caso con todo sano, un `503` por fallo de PostgreSQL y otro por fallo de MongoDB, con los fallos **simulados**.
- Middleware: genera el id si no viene, reutiliza uno válido, sustituye uno inválido y el id aparece en los logs.
- `accounts`: `get_user_model()` devuelve tu modelo y se puede crear un usuario y un superusuario.
- Tests de lo que añadas a `EnvSettings`, en la línea de los que ya tienes.
- Los tests que usan la BD corren contra PostgreSQL, no contra SQLite.

### 8. Documentación

- El README explica cómo levantar la infraestructura desde cero y actualiza la columna de estado del stack.
- Respuestas a las preguntas de diseño, en la descripción de la PR o al final de este archivo.

## Criterios de aceptación

- [x] `docker compose ps` muestra `postgres` y `mongo` como `healthy`.

```bash
NAME                     IMAGE                   COMMAND                  SERVICE    CREATED          STATUS                    PORTS
cratedigger-mongo-1      mongo:7.0.43-jammy      "docker-entrypoint.s…"   mongo      24 seconds ago   Up 23 seconds (healthy)   127.0.0.1:27017->27017/tcp
cratedigger-postgres-1   postgres:17.11-trixie   "docker-entrypoint.s…"   postgres   24 seconds ago   Up 23 seconds (healthy)   127.0.0.1:5432->5432/tcp
```
- [X] Tras `docker compose down -v` y `docker compose up -d`, `migrate` funciona desde cero contra PostgreSQL.

```bash
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying accounts.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying sessions.0001_initial... OK
```

- [X] En la BD existe la tabla del `User` de `accounts` y **no** existe `auth_user`. Pega la salida de `\dt` en la PR.

```bash
                       List of relations
 Schema |              Name              | Type  |    Owner
--------+--------------------------------+-------+-------------
 public | accounts_user                  | table | cratedigger
 public | accounts_user_groups           | table | cratedigger
 public | accounts_user_user_permissions | table | cratedigger
 public | auth_group                     | table | cratedigger
 public | auth_group_permissions         | table | cratedigger
 public | auth_permission                | table | cratedigger
 public | django_admin_log               | table | cratedigger
 public | django_content_type            | table | cratedigger
 public | django_migrations              | table | cratedigger
 public | django_session                 | table | cratedigger
(10 rows)
```

- [x] `curl -i localhost:8000/health/` devuelve `200` con el JSON de detalle.

```bash
HTTP/1.1 200 OK
Date: Thu, 01 Oct 2026 20:09:07 GMT
Server: WSGIServer/0.2 CPython/3.13.15
Content-Type: application/json
Expires: Thu, 01 Oct 2026 20:09:07 GMT
Cache-Control: max-age=0, no-cache, no-store, must-revalidate, private
X-Frame-Options: DENY
Content-Length: 70
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin

{"status": "healthy", "checks": {"postgresql": "up", "mongodb": "up"}}
```

- [x] Con `docker compose stop mongo`, `/health/` devuelve `503` en pocos segundos, no tras 30. Pega ambas salidas en la PR.

```bash
> time curl -i http://localhost:8000/health/

HTTP/1.1 503 Service Unavailable
Date: Thu, 01 Oct 2026 20:13:12 GMT
Server: WSGIServer/0.2 CPython/3.13.15
Content-Type: application/json
Expires: Thu, 01 Oct 2026 20:13:12 GMT
Cache-Control: max-age=0, no-cache, no-store, must-revalidate, private
X-Frame-Options: DENY
Content-Length: 74
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin

{"status": "unhealthy", "checks": {"postgresql": "up", "mongodb": "down"}}
real	0m2,081s
user	0m0,007s
sys	0m0,012s
```

- [x] La respuesta lleva `X-Request-ID`. Una petición con `-H "X-Request-ID: <uno válido>"` lo devuelve igual y ese id aparece en al menos una línea de la salida de `runserver`, también con `/health/` en 200.

```bash
curl -i -H "X-Request-Id: 7a7f536f-2182-492b-8ca1-ae5165c3914a" http://localhost:8000/health/
HTTP/1.1 200 OK
Date: Mon, 05 Oct 2026 08:25:02 GMT
Server: WSGIServer/0.2 CPython/3.13.15
Content-Type: application/json
Expires: Mon, 05 Oct 2026 08:25:02 GMT
Cache-Control: max-age=0, no-cache, no-store, must-revalidate, private
X-Frame-Options: DENY
Content-Length: 70
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin
X-Request-ID: 7a7f536f-2182-492b-8ca1-ae5165c3914a

{"status": "healthy", "checks": {"postgresql": "up", "mongodb": "up"}}

---

2026-10-05 08:25:02,145 INFO [7a7f536f-2182-492b-8ca1-ae5165c3914a] cratedigger.core.middleware: GET '/health/' 200 47.9ms
```

- [x] Sin `DJANGO_SECRET_KEY` (u otra variable obligatoria), `manage.py check` falla con un mensaje que dice qué falta.

```bash
pydantic_core._pydantic_core.ValidationError: 7 validation errors for EnvSettings
django_secret_key
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
postgres_db
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
postgres_user
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
postgres_password
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
mongo_db
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
mongo_user
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
mongo_password
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
```

- [x] `uv run pre-commit run --all-files`, `uv run mypy .` y `uv run pytest` en verde, con cobertura ≥ 85 %.
- [x] En el repo no hay `.env` ni `db.sqlite3`, y `.env.example` solo tiene marcadores.
- [x] La rama `feat/phase-01-infra` tiene commits atómicos y convencionales, y la PR está descrita.

## Restricciones

- Sin DRF: `/health/` es una vista de Django pura.
- PyMongo directo, sin ODM ni djongo.
- psycopg 3, no psycopg2.
- Sin Redis, sin Celery y sin contenedor de la app.
- Sin lógica de negocio ni modelos de dominio.
- Sin dependencias de fases futuras.
- Ningún secreto en `compose.yaml`, en el código ni en los tests.

## Preguntas de diseño

Respóndelas en la PR o al final de este archivo.

1. ¿Qué hace hoy `EnvSettings` con una variable del `.env` que no conoce? ¿Qué política elegiste para convivir con las variables de Compose y por qué? ¿Cómo encaja con `init_forbid_extra` del plugin de mypy?

Desde el módulo de `env.py`, `EnvSettings` carga todas las variables del archivo que recibe como `_env_file`. Cuando se instancia en `settings.py` con `.env`, se ejecuta en el arranque del servidor. Ya que he configurado `model_config` de forma explícita con `extra="forbid"`, fallará si existe una variable desconocida en `.env`, impidiendo que el servidor se inicie. `EnvSettings` también carga las variables del entorno de shell, pero solo busca las que coinciden con el nombre de un atributo, el resto las ignora porque no las ve. Esto es útil para los tests, donde puedo probar todas las variables de entorno y su validación utilizando un archivo de variables diferente o definiendo `_env_file=None` y configurando variables para el entorno de test como fixture. El test que prueba como `EnvSettings` rechaza y falla variables desconocidas es `test_unknown_key_in_env_file_is_forbidden`. En el test `test_unknown_environment_variable_is_ignored` se demuestra el comportamiento descrito, que supone un trade-off para entornos de producción donde las variables no estén definidas en un archivo, sino en un entorno que tenga una variable mal escrita. Esta será ignorada y se tomará el valor por defecto, si lo tiene. Por ello, es importante definir `DEBUG` con el valor `False` por defecto (*fail-safe defaults*). Si fuera `True`, un entorno de producción con `DEGUB=False`, fallaría silenciosamente y lo dejaría en `True`.

He elegido una política de convivencia de todas las variables en un único `.env`. En este momento las variables las consumen Django y Docker Compose, pero Django consume todas, también las de PostgreSQL y MongoDB, para configurar sus servicios de base de datos. El trade-off aplica cuando existan variables en `.env` que no consuma Django: en ese caso `EnvSettings` debe seguir cargando y validando todas las variables. La validación y los valores por defecto de `EnvSettings` es otro trade-off asumido, ya que solo aplican a Django, en `compose.yaml` se deben repetir los valores por defecto, y se puede dar una desincronización ante el cambio de un puerto u otro valor. Un error typo en una variable de `compose.yaml` podría fallar de forma silenciosa. Me ha ocurrido que definí `${POSTGRES_POST:-5432}`, con `PORT` mal escrito. En este caso `compose.yaml` no encuentra la variable, pero al tener un valor por defecto, aplica silenciosamente el puerto 5432. Esto no ocurre para las credenciales `${POSTGRES_USER:?}`, donde `compose.yaml` toma la variable como requerida y traza el error si no existe.

He tomado esta decisión porque me parece la mejor opción en este momento, al considerar el archivo `.env` como única fuente de verdad y definición de todas las variables. La alternativa es crear distintos archivos con variables de entorno para los distintos consumidores, lo que podría dar lugar a la repetición de variables y el mantenimiento de sincronización de valores que esto conlleva.

La opción `init_forbid_extra` del plugin de mypy detecta de forma estática argumentos con nombres desconocidos en las llamadas al constructor. Solo instancio `EnvSettings` una vez en `settings.py`, al arrancar el servidor, pero en los test de `test_env.py` pruebo su comportamiento ante distintos escenarios. Aquí es donde aplica mypy sobre el tipado de la instancia, bloqueando argumentos desconocidos. Esto complementa de forma coherente mi configuración actual, `init_forbid_extra` actuando cuando se ejecuta mypy (manual, pre-commit o CI si está configurado) y `extra="forbid"` al arrancar el servidor. En el caso de cambiar el `model_config` a `extra="ignore"`, entonces existirían configuraciones contradictorias, con mypy bloqueando los argumentos con nombres desconocidos y model_config aceptando e igorando las variables no definidas.


2. ¿Dónde vive `BASE_DIR` (o su equivalente) y por qué ahí?

`BASE_DIR` define la ruta raíz del proyecto a partir de la cual se escriben las rutas relativas de los archivos del proyecto: .env, plantillas, estáticos... Se configura y vive en `settings.py` junto al resto de la configuración de Django.

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

Su valor depende de la localización del archivo `settings.py` respecto a la raíz. Para este caso, resuelve la ruta absoluta de `settings.py` y sube dos niveles (primer parent: directorio `config/` -> segundo parent: directorio raíz del proyecto). Esto significa que si un día la configuración se divide en un paquete más: `settings/base.py`; se requiere añadir un `.parent` más a `BASE_DIR`.

Sería un error definir `BASE_DIR` junto a las variables de entorno en un `.env`. Según el desarrollo **12-factor**, lo que va al entorno es lo que cambia entre despliegues y `BASE_DIR` no es configuración: ponerlo como variable de entorno permitiría sobreescribirlo con un valor que dejaría de ser cierto cuando el proyecto se clone a otra máquina.

Tampoco se debe definir en el archivo `env.py`, el cual sabe *qué* configuración necesita la app y la valida; no sabe de *dónde* se lee. Las piezas se conectan en `settings.py`, el único punto que sabe dónde está el fichero `.env` para pasarlo a una instancia de `EnvSettings`. Esto proporciona la ventaja de poder instanciar `EnvSettings(_env_file=None)` o un `.env` temporal diferente al `.env` real, muy útil para probar la validación de variables de entorno, como demuestran los test que he realizado en este proyecto (p.ej `test_unknown_key_in_env_file_is_forbidden`).


3. ¿Por qué `AbstractUser` o por qué `AbstractBaseUser`? Tu `db.sqlite3` ya tenía aplicadas las migraciones de `auth.User`: ¿qué habría pasado si hubieras añadido el `User` propio sobre esa BD? ¿Y si fuera producción con datos reales?

Para crear un modelo de usuario propio en Django se hereda de la clase `AbstractUser` o `AbstractBaseUser`. Hay diferencias entre ellos, `AbstractUser` proporciona unos atributos definidos por defecto para el usuario (email, nombre, flags...), métodos como `create_user` o `create_superuser` y es compatible con `UserAdmin` para gestión desde el panel de administración. En cambio, `AbstractBaseUser` solo proporciona los atributos `password` y `last_login`, el resto hay que definirlos, y también requiere configuración adicional de `PermissionsMixin` y panel admin. Esta clase es ideal para cambiar el modo de identificación de usuario (p.ej. email en lugar de username) y ofrece mayor detalle de personalización con el coste de aplicar configuración adicional más compleja. En el caso de uso de este proyecto, en una fase de desarrollo temprana donde se requiere un usuario propio general, sin cambio de identificación necesario, la clase `Base` no aporta beneficio, sino complejidad. Por ello se decide utilizar `AbstractUser` que ofrece la posibilidad del modelo de usuario propio con personalización de atributos y métodos, y además simplifica la configuración con las herramientas de Django.

En el escenario propuesto ocurre lo siguiente: en la primera migración, Django ejecuta por defecto las migraciones de herramientas propias como admin (admin.0001_initial) o auth (auth.0001_initial); la migración de auth crea la tabla `auth_user` si no existe un `AUTH_USER_MODEL` propio definido en *settings*, con claves foráneas de la tabla `django_admin_log` que apuntando a ella; si posteriormente se crea un modelo de usuario propio y se intenta realizar la migración, se produce un error `InconsistentMigrationHistory` y se interrumpe la migración. Esto ocurre porque `admin.0001_initial` consta como aplicada, pero su dependencia `accounts.0001_initial` no lo está. Django detecta esta inconsistencia en el grafo de migraciones y cancela la operación sin ejecutarla, con la excepción `InconsistentMigrationHistory`. En desarrollo, con una base de datos vacía o de prueba, se resuelve fácilmente borrando la base de datos (`docker compose down -v`) y ejecutando las migraciones sobre una base de datos nueva, esta vez con accounts.0001_initial en la primera migración y `AUTH_USER_MODEL` apuntando al modelo propio para que no se cree la tabla auth_user y accounts_user sea la tabla de usuarios de la aplicación.

Este mismo escenario en producción es más delicado, porque la base de datos contiene información que no puede ser eliminada y creada de nuevo desde cero. Requiere operaciones manuales para ajustar el histórico de migraciones y el esquema del modelo. El procedimiento más habitual en este caso es:

- Indicar en el modelo de usuario propio que reutiliza la tabla existente con `db_table = "auth_user"`.
- Marcar la migración inicial del modelo de usuario como aplicada, sin ejecutarla.
- Corregir los registros de `django_content_type`.

Django es explícito en su documentación, sobre la ausencia de un método automático para resolver este conflicto y recomienda la creación de un usuario propio para nuevos proyectos desde la primera migración, aunque el de serie fuera suficiente porque no sea estrictamente necesaria la personalización de su modelo y atributos.


4. `/health/`: ¿qué detalle expones en una URL pública y qué te callas? ¿Qué timeout elegiste y qué pasaría sin él? ¿Tu endpoint es de *liveness* o de *readiness*, y por qué importa la diferencia?

En el endpoint público `/health/` expongo únicamente el estado de los servicios `postgresql` y `mongodb`, con el código del protocolo HTTP asociado: 200 si los dos servicios responden o 503 si falla alguno. No expongo los mensajes de excepción que se pueden producir con un intento de conexión fallida u otros, donde se muestran: secretos, nombres de host, puertos, usuarios o versiones. Estos detalles van al log interno, con el `request_id` de la petición, solo accesible para administradores o desarrolladores autorizados. He creado un test `test_health_does_not_leak_exception_details` que lo demuestra.

Conviene mencionar que mi endpoint público está filtrando información sobre los servicios de base de datos que utilizo, postgresql y mongodb. Sería una práctica más segura dejar solo el código de estado en el endpoint público y definir un endpoint privado con la información por servicio. Es un trade-off aceptado, teniendo en cuenta que el repositorio y el código también son públicos.

He elegido un timeout de 2 segundos en cada servicio (~4s total en el peor caso) para el healthcheck. En PostgreSQL he configurado `connect_timeout` de forma global en `settings.py` para todas las peticiones. Mientras que en mongo, el timeout global por defecto es de 30s, aunque yo lo he configurado en 5s y en el healthcheck lo he reducido a 2s, suficientes para probar la conexión y revelar un fallo. Ahora las bases de datos son locales, cuando estén en producción (desplegadas en Supabase, Mongo Atlas o servidores propios), puede requerir una ampliación de timeout, aunque 2 segundos deberían ser suficientes para probar un healthcheck eficiente y prefiero fallar rápido también para peticiones normales.

Cada driver actúa de forma distinta, en PostgreSQL utilizo `psycopg3` que utiliza la librería `libpq`. Si no tuviera `connect_timeout` configurado, esperaría la conexión hasta que el sistema operativo abandone el intento TCP (en Linux puede durar minutos). No he configurado `timeout`, sino `connect_timeout` global que protege del peor escenario: un host que no responde. Si el servicio de PostgreSQL está caído (escenario con el contenedor parado), la conexión se rechaza al instante. En cambio, MongoDB utiliza `pymongo`, que reintenta la selección del servidor durante todo el timeout. He probado a detener el contenedor de mongo y acceder al endpoint, midiendo un tiempo de 2,08s en la operación. Es importante definir unos timeouts de forma que la consulta total a los servicios quede por debajo del timeout de la herramienta que consulta el healthcheck (p.ej. en Kubernetes tiene un timeout por defecto de 1s para pruebas liveness/readiness, si lo utilizo debo fijar un `timeoutSeconds` mayor a 4s para el probe). También es importante limitar los tiempos de conexión en un servidor WSGI, donde cada petición ocupa un worker de forma síncrona. De esta forma, si una dependencia se cuelga, el worker se bloquea y el orquestador sigue consultando `/health/` hasta que los workers se agotan y la aplicación se bloquea ante cualquier petición.

El endpoint `/health/` es *readiness* porque prueba la disponibilidad de servicios externos de base de datos para determinar si el servicio está listo para usarse. Un endpoint *liveness* simplemente prueba la disponibilidad del propio servidor, devolviendo 200 en una URL para probar que el servidor está activo. Esta diferencia influye en cómo resuelve el orquestador los problemas de conexión a un servicio. Si es *liveness*, reinicia el contenedor. Si es *readiness*, deja de enviarle tráfico. Es evidente que el endpoint no puede ser *liveness*, porque ante un servicio caído (p.ej. postgres), el orquestador reiniciará todos los contenedores de la app una y otra vez, lo que no va a solucionar la conexión al servicio y además dejaría el resto de servicios inoperativos. La app dejaría de atender incluso las peticiones que no necesitan el servicio caído.


5. Middleware: ¿en qué posición de `MIDDLEWARE` lo pusiste y por qué? ¿Por qué no te fías de cualquier `X-Request-ID` entrante? ¿Cómo llega el id a los logs de otros módulos, y por qué `contextvars` y no `threading.local` (o al revés)?

Lo he situado el primero en la lista de middlewares de `settings.py`. Esto significa que es la primera capa que actúa sobre las request entrantes y la última sobre las response salientes. El motivo es que, ya que mi middleware añade request_id a los mensajes del logger, quiero que todas las peticiones lo utilicen, también las que sean bloqueadas por otros middlewares como `Security`. Situarlo más abajo en la lista haría que las peticiones que filtren y bloqueen middlewares superiores no utilicen request_id en sus logs ni en la response, y considero que es más útil para debugging y monitorización identificar cada una de las peticiones.

Se pueden dar tres casos ante una request: que no tenga la cabecera `X-Request-ID`, que la tenga con un valor válido o que la tenga y el valor no sea válido. Si no la tiene se crea uno para ser utilizado en todos los logs posteriores y en la response; si lo tiene y es válido se reutiliza. Pero no me puedo fiar de cualquier `X-Request-ID` porque cualquier cliente puede alterar el header de su request e introducir líneas falsas en los logs. También se puede dar un problema de tamaño al aceptar cabeceras enormes que se almacenarían en los logs. Para prevenirlo, valido cada `X-Request-ID` entrante y normalizo a su forma canónica. Si no es válido, se descarta y se genera uno nuevo en formato válido para la response. En este caso, la request llega del cliente y eso hace que no sea de confianza. Pero en producción, donde el endpoint vive tras un proxy, el escenario cambia y sí podría aceptar el request_id entrante para correlacionar con sus logs si el proxy se encarga de sobreescribir el header del cliente, lo que se denomina frontera de confianza.

El identificador de cada petición se declara como una ContextVar: su valor es compartido por un contexto desde que se crea hasta que se resetea (al salir del middleware). He creado el filtro `RequestIdFilter` que añade la variable de contexto como `request_id` a cada record del log. Este filtro lo he conectado al handler de root, al que propagan todos los loggers (un filtro sobre un logger no actuaría sobre los registros que le lleguen de loggers hijos). Así la pueden utilizar los logs de otros módulos, pero no todos. Hay módulos propios de Django, como django.server o django.request, que actúan después de la cadena middleware. Como el valor de `request_id` se asocia a la ContextVar después de ser validado dentro del middleware y se resetea al final, estos módulos de Django no la pueden utilizar. Para el caso concreto de django.server, lo que he hecho ha sido crear un log similar propio dentro de mi middleware, que sí utiliza el valor de request_id. Este log reemplaza el de django.server, pero para no duplicar los logs, he subido el nivel de django.server a WARNING, así no tengo logs INFO duplicados para peticiones normales. Se asume que los logs de django.request se sigan mostrando con el valor por defecto de `request_id` ("-").


En un servidor web, la práctica recomendada para variables de contexto compartidas utiliza la librería `contextvars`, `threading.local` también sirve para compartir variables de contexto por hilos, pero falla en código asíncrono. Para un servidor WSGI ambas son válidas, pero `contextvars` mantiene el valor por tarea asíncrona, lo que me permite definir vistas asíncronas en fases posteriores.

Al definir mi propio logger para todas las peticiones, que utiliza la url de la petición como variable, he tenido que proteger la ruta loggeada con `%r` para prevenir la inyección en el log de acceso.


6. ¿Qué variante de psycopg instalaste (`binary`, `c` o la pura) y por qué? ¿Dónde vive el `MongoClient` y cuántas instancias hay por proceso?

Utilizo la versión `psycopg 3`, variante `binary`, la opción recomendada por su documentación para un **desarrollo** rápido. `psycopg` utiliza una librería del sistema oficial de PostgreSQL `libpq`, que está escrita en C. La diferencia entre las variantes es de dónde obtiene `psycopg` esta librería. Con la opción `binary`, la librería se instala compilada en sus binarios, junto a una copia de OpenSSL y la extensión de C, por lo que no requiere ningún recurso adicional del sistema. La variante `c` instala solamente la extensión de C para `psycopg`, por tanto requiere un compilador de C en el sistema, las cabeceras de python y de libpq (con los paquetes de desarrollo del sistema). Esta variante es ideal para producción, donde una compilación en varias etapas permite dejar la imagen final sin compilador. Además, como compila sobre una librería del sistema, esta se debe encontrar actualizada como el resto de librerías. La opción `binary` utiliza una copia que puede estar desfasada respecto a la versión oficial, los parches de actualización y seguridad no me llegan hasta que `psycopg` publique una nueva versión. La opción pura utiliza directamente python sobre la librería del sistema. Se descarta por un problema de rendimiento, ya que utilizar python para la adaptación de datos de PostgreSQL es más lento que C.

Mi elección ha sido la variante `binary`, porque en estos momentos la app corre en mi máquina local y no quiero depender de un compilador ni de cabeceras del sistema. Cuando llegue la Fase 10, revisaré la opción para construir la imagen de producción.

En mi proyecto, `MongoClient` vive en la aplicación `cratedigger.core`, en el módulo `mongo.py`, instanciado y devuelto dentro de la función `get_client()`. No se instancia con la importación del módulo, sino en la llamada a la función `get_client()` que tiene el decorador `@cache` para reutilizar el cliente por un proceso. De esta forma solo existe una instancia del cliente de mongo (con sus hilos de supervisión y pool de conexiones) por proceso. Esto también evita el problema de compartir el cliente en un fork, donde se copian objetos y memoria pero no los hilos de supervisión. Crear dos objetos compartidos apuntando al mismo socket pueden causar colisiones y corromper los datos, esta es una restricción documentada de PyMongo que conviene evitar (`MongoClient` no es *fork-safe*). Para ello el cliente se instancia en la llamada a get_client(), que ocurre en cada worker después del fork, así cada cliente se crea con sus hilos, memoria y objetos independientes. Esta ha sido una decisión anticipada para la Fase 10 con gunicorn, donde se realizará el fork para distintos workers, todavía no resuelve ningún problema de acuerdo al estado de desarrollo actual.


7. Para los datos de las BDs, ¿volumen nombrado o bind mount? ¿Qué pierdes con cada opción? ¿Fijaste la versión exacta de las imágenes o solo la mayor?

He utilizado volúmenes nombrados `cratedigger_mongo-data` y `cratedigger_postgres-data` en ambos servicios, es la práctica recomendada para servicios de bases de datos. Los volúmenes nombrados utilizan rutas del sistema propias de docker para la persistencia de datos. Estos archivos no están a la vista del proyecto, se accede a ellos mediante root o comandos docker. Para realizar copias de seguridad, la práctica habitual es `pg_dump` o `mongodump` desde el contenedor. En cambio, los volúmenes bind mount utilizan una carpeta del sistema, compartiendo archivos legibles con el contenedor. Estos se utilizan para código o configuración. No es la mejor opción para volúmenes de bases de datos por varias razones: gestión de archivos y permisos (postgres escribe con su propio usuario), comparte una carpeta del sistema que debe existir (configuración adicional para portabilidad), deben ser borrados manualmente con permisos de administrador (down -v no los borra), un descuido puede incluir los archivos en el repositorio (commit sin .gitignore).

 He fijado la versión completa mayor.minor.patch-sufijo_distro (postgresql `17.11-trixie` y mongo `7.0.43-jammy`), aceptando el trade-off de no fijar solo mayor: pierdo las actualizaciones minor y parches, pero solo temporalmente. En la siguiente fase voy a implementar Dependabot/Renovate en CI, que detecta actualizaciones sobre las imagenes con la versión completa. Con esta opción obtengo control sobre los tiempos de actualización, aunque asumo que los tags pueden ser mutables. En la fase de producción si tendrá imagenes fijadas por digest para asegurar la reproducibilidad.


## Recursos

- Compose: [Services](https://docs.docker.com/reference/compose-file/services/) (`healthcheck`, `ports`, `env_file`) · [Volumes](https://docs.docker.com/reference/compose-file/volumes/) · [Variables en Compose](https://docs.docker.com/compose/how-tos/environment-variables/) · [Orden de arranque](https://docs.docker.com/compose/how-tos/startup-order/)
- Imágenes: [postgres en Docker Hub](https://hub.docker.com/_/postgres) · [mongo en Docker Hub](https://hub.docker.com/_/mongo)
- Django 5.2: [Custom user model](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#substituting-a-custom-user-model) · [Middleware](https://docs.djangoproject.com/en/5.2/topics/http/middleware/) · [Logging](https://docs.djangoproject.com/en/5.2/topics/logging/) · [Bases de datos: PostgreSQL](https://docs.djangoproject.com/en/5.2/ref/databases/#postgresql-notes)
- Configuración: [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) · [12-factor: Config](https://12factor.net/es/config)
- Drivers: [psycopg 3: instalación](https://www.psycopg.org/psycopg3/docs/basic/install.html) · [PyMongo](https://pymongo.readthedocs.io/) (`MongoClient`, timeouts, comando `ping`)
- Python: [`contextvars`](https://docs.python.org/3/library/contextvars.html) · [`logging`: filtros](https://docs.python.org/3/library/logging.html#filter-objects)
- Tests: [pytest-django: base de datos](https://pytest-django.readthedocs.io/en/latest/database.html) · [`caplog`](https://docs.pytest.org/en/stable/how-to/logging.html)

## Fuera de alcance

- El CI y la protección de `main` (Fase 2).
- Los modelos del catálogo (Fase 3).
- DRF y cualquier endpoint de la API (Fase 4).
- Roles, JWT y permisos (Fase 5).
- El modelo de documentos de MongoDB y el puerto `LyricsRepository` (Fase 9). Aquí Mongo solo se usa para el `ping`.
- El Dockerfile de la app y gunicorn (Fase 10).

## Temas de la mini-entrevista

- El ciclo request/response completo en Django.
- El orden de los middlewares.
- User personalizado: `AbstractUser` frente a `AbstractBaseUser`.
- 12-factor.
- Imagen frente a contenedor.
- Volumen nombrado frente a bind mount.
- `depends_on` y los healthchecks.
- `DEBUG` y `ALLOWED_HOSTS` en producción.
- Python core: mutabilidad y argumentos por defecto.
