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
- El id aparece en **cada** línea de log emitida durante esa petición, también en las de otros módulos. Configura `LOGGING` para ello.
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

- [ ] `docker compose ps` muestra `postgres` y `mongo` como `healthy`.
- [ ] Tras `docker compose down -v` y `docker compose up -d`, `migrate` funciona desde cero contra PostgreSQL.
- [ ] En la BD existe la tabla del `User` de `accounts` y **no** existe `auth_user`. Pega la salida de `\dt` en la PR.
- [ ] `curl -i localhost:8000/health/` devuelve `200` con el JSON de detalle.
- [ ] Con `docker compose stop mongo`, `/health/` devuelve `503` en pocos segundos, no tras 30. Pega ambas salidas en la PR.
- [ ] La respuesta lleva `X-Request-ID`. Una petición con `-H "X-Request-ID: <uno válido>"` lo devuelve igual y ese id aparece en el log de `runserver`.
- [ ] Sin `DJANGO_SECRET_KEY` (u otra variable obligatoria), `manage.py check` falla con un mensaje que dice qué falta.
- [ ] `uv run pre-commit run --all-files`, `uv run mypy .` y `uv run pytest` en verde, con cobertura ≥ 85 %.
- [ ] En el repo no hay `.env` ni `db.sqlite3`, y `.env.example` solo tiene marcadores.
- [ ] La rama `feat/phase-01-infra` tiene commits atómicos y convencionales, y la PR está descrita.

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
2. ¿Dónde vive `BASE_DIR` (o su equivalente) y por qué ahí?
3. ¿Por qué `AbstractUser` o por qué `AbstractBaseUser`? Tu `db.sqlite3` ya tenía aplicadas las migraciones de `auth.User`: ¿qué habría pasado si hubieras añadido el `User` propio sobre esa BD? ¿Y si fuera producción con datos reales?
4. `/health/`: ¿qué detalle expones en una URL pública y qué te callas? ¿Qué timeout elegiste y qué pasaría sin él? ¿Tu endpoint es de *liveness* o de *readiness*, y por qué importa la diferencia?
5. Middleware: ¿en qué posición de `MIDDLEWARE` lo pusiste y por qué? ¿Por qué no te fías de cualquier `X-Request-ID` entrante? ¿Cómo llega el id a los logs de otros módulos, y por qué `contextvars` y no `threading.local` (o al revés)?
6. ¿Qué variante de psycopg instalaste (`binary`, `c` o la pura) y por qué? ¿Dónde vive el `MongoClient` y cuántas instancias hay por proceso?
7. Para los datos de las BDs, ¿volumen nombrado o bind mount? ¿Qué pierdes con cada opción? ¿Fijaste la versión exacta de las imágenes o solo la mayor?

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
