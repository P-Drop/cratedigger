# Roadmap de CrateDigger

Este es el mapa completo del tutorial.

- Cada fase se convierte en un reto (`docs/tutorial/retos/fase-NN-slug.md`) **al abrirla**, adaptado a cómo haya ido la anterior.
- El orden es el recomendado. Las fases *extra* (11–14) se pueden reordenar.
- El estado de cada fase está en [`PROGRESO.md`](PROGRESO.md) y las reglas del tutor, en [`CLAUDE.md`](../../CLAUDE.md).

## El dominio en una página

**CrateDigger** es un archivo colaborativo de la discografía del hip hop y de sus samples. En la cultura hip hop, *crate digging* es rebuscar en cajas de vinilos el sample perfecto.

**PostgreSQL** guarda el catálogo y los samples:

| Entidad | Qué representa |
|---|---|
| `Artist` | Una persona o un grupo (MC, productor, DJ, banda de funk…) |
| `Membership` | Quién formó parte de qué grupo y durante qué años |
| `Label` | Un sello discográfico |
| `Release` | Un LP, EP, mixtape, single o recopilatorio |
| `Track` | Una pista dentro de un release |
| `Credit` | Qué artista participa en qué pista y con qué rol (main, featured, producer…) |
| `Sample` | Qué pista samplea a cuál, de qué tipo, quién lo propuso y si está verificado |
| `User` | Anónimos (lectura), *contributors* (proponen) y *moderators* (verifican) |

**MongoDB** guarda las letras con anotaciones al estilo Genius: secciones, líneas, anotaciones y votos.

Preguntas que la API sabrá responder:
- ¿Qué pistas samplean «Amen, Brother» de The Winstons?
- ¿Qué productor fue el más sampleado de cada década?
- ¿Cuál es la genealogía completa de un sample (ascendientes y descendientes)?
- Buscar «kase o» y encontrar «Kase.O». Buscar «rodriguez» y encontrar «Rodríguez».
- Fusionar dos artistas duplicados sin perder ni un crédito.

## Hilos transversales

Estos temas no son fases: se trabajan en todas ellas.

| Hilo | Qué implica |
|---|---|
| Tests y tipado | Cada PR trae tests (reglas y casos borde) y pasa mypy strict. La cobertura mínima es del 85 %. |
| Bruno | A partir de la F4, cada endpoint nuevo tiene su request con aserciones y la colección se ejecuta por CLI. |
| Documentación | El README se mantiene al día. Los ADRs recogen las decisiones importantes: 0001 arquitectura, 0002 modelado, 0003 autenticación, 0004 letras, 0005 despliegue. |
| Secretos | F0: escaneo en pre-commit → F1: variables de entorno y `.env.example` → F2: CI sin secretos reales → F5: clave de firma de los JWT → F10: nada en la imagen → F13: gestor de secretos y rotación. |
| Git | Conventional Commits, una PR por reto e historial limpio. |
| Python core | Cada mini-entrevista incluye una pregunta de Python conectada con la fase. |
| Repaso espaciado | Cada fase se abre con 2 preguntas de «Temas a repasar». |

---

## Fase 0 · Setup profesional

**Objetivo:** tener un repo que cualquiera pueda clonar y levantar con un comando, con puertas de calidad automáticas desde el primer commit.

**Reto**
- Un repo git con la rama `main`, publicado en GitHub con `gh`.
- Un proyecto uv con Python 3.13 fijado y Django 5.2 LTS. Las herramientas van en un grupo de dependencias de desarrollo.
- `startproject` con el paquete de configuración `config` y `manage.py` en la raíz.
- ruff (lint y formato), mypy strict con django-stubs y pytest-django con cobertura, todo en `pyproject.toml`.
- pre-commit con estos hooks:
  - ruff.
  - mypy como hook local con uv.
  - Higiene.
  - Sincronía de `uv.lock`.
  - Escaneo de secretos.
  - Conventional Commits en `commit-msg`.
- Un README en inglés y el **ADR-0001 (arquitectura)**, escrito con tus palabras.

**Criterios clave:**
- Un clon limpio funciona con `uv sync --locked`.
- Todos los checks pasan en verde.
- Se demuestra que los hooks rechazan un commit no convencional y un secreto.

**Entrevista:**
- Lockfile y builds reproducibles.
- uv frente a pip, pip-tools o poetry.
- Dependencias de producción frente a las de desarrollo.
- Linter, formatter y type checker: en qué se diferencian.
- Qué garantiza pre-commit y qué no (`--no-verify` es la razón de que exista el CI).
- Tipado gradual y stubs.
- Conventional Commits y SemVer.
- Merge frente a rebase.
- Qué hacer si se filtra un secreto.

**Problema tipo:** «Hiciste commit y push de `.env` con la contraseña de la BD hace tres commits. ¿Qué haces, y en qué orden?»

## Fase 1 · Infraestructura local y configuración

**Objetivo:** que la app corra contra PostgreSQL y MongoDB en contenedores, con configuración 12-factor y un modelo de usuario propio desde el primer día.

**Reto**
- `compose.yaml` con postgres:17 y mongo:8, volúmenes nombrados, healthchecks y credenciales leídas de `.env`.
- Settings leídos del entorno, tipados y validados al arrancar: si falta una variable obligatoria, la app no arranca (*fail fast*). Tú eliges la librería (django-environ, environs, pydantic-settings…) y justificas la elección.
- Un `.env.example` documentado. `.env` nunca se versiona.
- La app `accounts` con un `User` personalizado **antes del primer `migrate`**.
- En la app `core`, una vista `/health/` **sin DRF** que comprueba PostgreSQL y MongoDB. Devuelve 200 o 503 y un JSON con el detalle.
- Un middleware propio para `X-Request-ID`: lo recibe o lo genera, lo añade a la respuesta y aparece en los logs.

**Criterios clave:**
- Los dos servicios aparecen como `healthy`.
- `migrate` funciona contra PostgreSQL.
- Hay tests de `/health/`, también del 503 simulando el fallo.
- Hay tests del middleware.
- Si falta `SECRET_KEY`, la app da un error claro.

**Entrevista:**
- El ciclo request/response completo: WSGI → middleware → URLconf → vista → middleware.
- El orden de los middlewares y por qué importa.
- Por qué un User personalizado desde el principio (`AbstractUser` frente a `AbstractBaseUser`).
- 12-factor.
- Imagen frente a contenedor.
- Volumen nombrado frente a bind mount.
- `depends_on` con `condition: service_healthy`.
- Riesgos de `DEBUG=True` en producción.
- `ALLOWED_HOSTS`.

**Problema tipo:** «¿Qué imprime este código y por qué?», con una función que usa un diccionario mutable como argumento por defecto.

## Fase 2 · CI y flujo de PRs

**Objetivo:** que nada entre en `main` sin pasar por una PR con el CI en verde.

**Reto**
- Un workflow de GitHub Actions que se ejecute en las PRs y en los push a `main`. Debe incluir:
  - uv con caché.
  - Servicios de PostgreSQL y MongoDB.
  - pre-commit o ruff, mypy y pytest con `--cov-fail-under`.
- Una plantilla de PR.
- Protección de `main` (ruleset o branch protection) que exija PR y el check del CI.
- El badge del CI en el README.
- La estrategia de merge (squash, merge commit o rebase), elegida y justificada en el README.

**Criterios clave:**
- Una PR de prueba con un test roto queda bloqueada y, al arreglarlo, pasa.
- El CI usa caché y tarda un tiempo razonable.

**Entrevista:**
- Continuous Integration, Continuous Delivery y Continuous Deployment: en qué se diferencian.
- Qué debe bloquear un merge.
- Tests flaky: qué son y qué hacer con ellos.
- Secretos en el CI: por qué los tests no deberían necesitarlos.
- Caché de dependencias.
- Qué es un runner.
- Matrices de versiones.

**Problema tipo:** «El CI pasa en tu máquina pero falla en GitHub. Dime cinco causas probables y cómo depurarías cada una.»

## Fase 3 · Modelado del catálogo

**Objetivo:** un modelo relacional sólido, con las invariantes garantizadas por la base de datos y las decisiones documentadas.

**Reto**
- Los modelos `Artist`, `Membership`, `Label`, `Release`, `Track` y `Credit`.
- **ADR-0002** con un diagrama ER en Mermaid. Debe responder:
  - ¿Un grupo es un `Artist` más o un modelo aparte?
  - ¿Cómo se modelan los créditos y los roles?
- Las invariantes van en la BD:
  - `UniqueConstraint`, por ejemplo una posición única por release.
  - `CheckConstraint`, por ejemplo años coherentes y duraciones y bpm positivos.
  - Índices para las consultas previsibles.
- `TextChoices`, slugs y un modelo abstracto con timestamps en `core`.
- Un admin útil: `list_display`, `search_fields`, `list_filter`, inlines, `autocomplete_fields` y `list_select_related`.
- factory_boy, y tests que demuestren que las constraints saltan (`IntegrityError`).
- Un management command `seed_catalog` **idempotente** con:
  - Rap en español, de España y Latinoamérica.
  - Clásicos de EE. UU.
  - Los discos de funk y soul más sampleados, como «Amen, Brother» de The Winstons o «Funky Drummer» de James Brown.

**Criterios clave:**
- Las migraciones son limpias y tienen nombres descriptivos.
- Ejecutar el seed dos veces deja los mismos datos.
- Las constraints están probadas.
- El admin es navegable sin N+1 evidentes.

**Entrevista:**
- `null` frente a `blank`.
- Las opciones de `on_delete` y cuándo usar cada una.
- FK, OneToOne y ManyToMany con `through`.
- `related_name`.
- Constraints en la BD frente a `clean()`: `save()` no llama a `full_clean()`.
- `UniqueConstraint` frente a `unique_together`.
- Herencia abstracta, multi-tabla y proxy.
- Claves naturales frente a subrogadas (`CompositePrimaryKey`, nueva en 5.2).
- Qué hacen `makemigrations` y `migrate`.
- Data migrations con `RunPython`.
- Conflictos de migraciones en un equipo.

**Problema tipo:** «Traduce a SQL un filtro del ORM que atraviese tres relaciones de tus modelos y compruébalo con `str(qs.query)`. ¿Por qué pueden salir filas duplicadas y cómo se evitan?»

## Fase 4 · API REST del catálogo

**Objetivo:** una API REST coherente, documentada y probada, que respete la arquitectura de services y selectors.

**Reto**
- CRUD de artists, labels, releases y tracks bajo `/api/v1/`.
- Vistas delgadas: las lecturas van en `selectors.py` y las escrituras en `services.py`.
- Serializers de entrada y de salida separados cuando el caso lo justifique: lectura anidada y escritura por id o slug.
- Paginación, filtros con django-filter (país, década, tipo de release…), búsqueda y ordenación.
- Un formato de error uniforme según la RFC 9457 (`application/problem+json`).
- OpenAPI con drf-spectacular y Swagger UI, sin warnings.
- Una **colección de Bruno** con un request por endpoint, entornos sin secretos y aserciones. Se ejecuta con la CLI.
- Tests de la API con `APIClient` y `pytest.mark.parametrize`.

**Criterios clave:**
- Cada caso devuelve el código de estado correcto.
- El schema se genera sin warnings.
- La colección de Bruno pasa en local.
- La cobertura es ≥ 85 %.

**Entrevista:**
- Métodos seguros e idempotentes.
- PUT frente a PATCH.
- 400 frente a 422, 401 frente a 403, y cuándo usar 404 y 409.
- `Serializer` frente a `ModelSerializer`.
- `APIView`, `GenericAPIView` y `ViewSet`.
- El flujo de validación de DRF: `is_valid`, `validate_<campo>` y `validate`.
- Paginación por offset frente a cursor.
- Estrategias de versionado.
- Fat models, service layer y hexagonal: defiende la tuya.

**Problema tipo:** «Diseña el endpoint para añadir un featuring a una pista: método, URL, cuerpo, respuestas y códigos de error.»

## Fase 5 · Autenticación, permisos y seguridad

**Objetivo:** saber quién llama (authn) y qué puede hacer (authz), y proteger la API de abusos y de errores de configuración.

**Reto**
- JWT con simplejwt: access de vida corta y refresh con rotación y blacklist.
- Roles con los Groups de Django:
  - El anónimo solo lee.
  - El `contributor` propone samples y anota letras.
  - El `moderator` verifica y fusiona.
- Permisos a nivel de objeto; por ejemplo, editar solo tus propias propuestas sin verificar.
- Throttling para anónimos y para usuarios, con un scope más estricto en las escrituras.
- CORS configurado para un frontend hipotético.
- `manage.py check --deploy` limpio con la configuración de producción.
- **ADR-0003**: la estrategia de autenticación y dónde guardaría el token un frontend.
- La matriz de permisos (rol × endpoint × método → código esperado), testeada con `parametrize`.

**Criterios clave:**
- La matriz de permisos pasa entera.
- Un token caducado o en blacklist devuelve 401.
- El throttling devuelve 429.

**Entrevista:**
- Authn frente a authz.
- Sesión, token y JWT: qué es stateless y el problema de la revocación.
- Dónde guardar un JWT en una SPA: cookie httpOnly o localStorage, XSS frente a CSRF.
- Cómo funciona CSRF y por qué DRF lo exige con `SessionAuthentication`.
- Hashing de contraseñas (PBKDF2 y Argon2, salt) y por qué no basta con SHA-256.
- El OWASP API Security Top 10 aplicado a esta API.

**Problema tipo:** «Decodifica este JWT sin verificarlo. ¿Qué contiene, qué garantiza la firma y qué **no** garantiza?»

## Fase 6 · Samples: relaciones auto-referenciales y reglas de negocio

**Objetivo:** modelar el corazón del dominio, qué pista samplea a cuál, con reglas que no caben en una constraint.

**Reto**
- `Sample` es una M2M de `Track` consigo mismo, con modelo intermedio (`through`) y dirigida (`symmetrical=False`). Guarda:
  - Qué pista samplea y cuál es sampleada.
  - El tipo: break o batería, voz, loop o melodía, interpolación.
  - Marcas de tiempo opcionales.
  - Quién lo propuso y si está verificado.
- Un `CheckConstraint` impide que una pista se samplee a sí misma y un `UniqueConstraint` impide los duplicados.
- Una regla multi-fila en el service `register_sample()`: la pista sampleada debe ser anterior a la que samplea. ¿Por qué no puede ser una constraint de la BD?
- Moderación con los roles de la F5: el contributor propone y el moderator verifica. La acción `verify` debe ser **idempotente**.
- Un QuerySet personalizado con `with_sample_counts()` y `most_sampled()`.
- Endpoints para el CRUD de samples, para «qué samplea esta pista» y para «quién la ha sampleado».

**Criterios clave:**
- Las reglas se prueban tanto en el service como en la API.
- Verificar dos veces no rompe nada ni duplica efectos.

**Entrevista:**
- M2M a sí mismo y el parámetro `symmetrical`.
- `related_name` en los dos sentidos.
- Dónde va cada validación (serializer, service, modelo o BD) y por qué.
- `Manager` frente a `QuerySet` (`as_manager()`).
- Señales: cuándo sí y cuándo no.
- Idempotencia.

**Problema tipo:** «¿Qué pasa si dos moderadores verifican el mismo sample a la vez? ¿Y si la verificación envía un email?»

## Fase 7 · ORM avanzado y rendimiento

**Objetivo:** consultas correctas **y** eficientes, medidas en lugar de intuidas.

**Reto**
- Detectar los N+1 con django-debug-toolbar y blindar cada listado con `django_assert_num_queries`: el número de queries no puede crecer con el número de filas.
- Corregirlos con `select_related`, `prefetch_related` y `Prefetch(queryset=..., to_attr=...)`.
- Estadísticas en `/api/v1/stats/`:
  - Las pistas más sampleadas: `annotate` + `Count`.
  - Conteos condicionales: `Count(..., filter=Q(...))`.
  - El último lanzamiento de cada artista: `Subquery` + `OuterRef`.
  - El productor más sampleado de cada década: `Window` + `Rank` con partición.
- `F()` para actualizar contadores sin condiciones de carrera.
- `bulk_create` en el seed, midiendo el antes y el después.
- `QuerySet.explain()` sobre una consulta lenta, y un índice que la mejore con su justificación.
- Un export CSV grande con `iterator()` y respuesta en streaming.

**Criterios clave:**
- Cada listado tiene un test del número de queries.
- `explain()` muestra que el índice se usa.
- El export no carga todo en memoria.

**Entrevista:**
- El problema N+1.
- `select_related` (JOIN) frente a `prefetch_related` (segunda query con `IN`).
- Evaluación perezosa y caché del QuerySet.
- `annotate` frente a `aggregate`.
- Expresiones `F` y `Q`, y `Subquery`.
- Window functions.
- El coste de un índice en las escrituras.
- Índices compuestos y el orden de sus columnas.
- `exists()`, `count()` y `len()`.
- `iterator()` y los generadores.

**Problema tipo:** «Esta vista hace 101 queries para 100 releases. Encuentra por qué y arréglala.» (Se te da el código.)

## Fase 8 · PostgreSQL a fondo

**Objetivo:** aprovechar lo que PostgreSQL hace mejor que un ORM genérico y entender las transacciones de verdad.

**Reto**
- Búsqueda full-text en artistas, releases y pistas con `SearchVector`, `SearchQuery`, `SearchRank`, un índice GIN y `unaccent`.
- Búsqueda difusa con `pg_trgm` y `TrigramSimilarity`.
- **Genealogía de samples** con un CTE recursivo en SQL crudo **parametrizado**:
  - Devuelve los ascendientes y los descendientes de una pista.
  - Tiene límite de profundidad y protección contra ciclos.
  - Se compara con la versión ingenua en Python, en número de queries y en tiempo.
- **Fusión de artistas duplicados**, como acción de moderador:
  - Reasigna créditos, membresías y demás referencias dentro de `transaction.atomic()`, con `select_for_update()`.
  - Resuelve los conflictos de unicidad.
  - Los efectos secundarios van en `transaction.on_commit()`.

**Criterios clave:**
- La genealogía se prueba con un grafo conocido, incluido un ciclo metido a propósito.
- La fusión es todo o nada: un test fuerza un fallo a mitad y comprueba el rollback.

**Entrevista:**
- Inyección SQL y consultas parametrizadas: `%s` frente a f-strings.
- ACID.
- Niveles de aislamiento (READ COMMITTED es el de PostgreSQL por defecto) y sus anomalías.
- `atomic()` anidado y savepoints.
- `select_for_update` y deadlocks.
- `ATOMIC_REQUESTS`: pros y contras.
- CTE recursivos.
- `LIKE` frente a full-text frente a trigramas.
- Tipos de índice: B-tree, GIN y GiST.

**Problema tipo:** «Escribe a mano un CTE recursivo que devuelva todas las pistas que descienden de «Amen, Brother», hasta profundidad 3.»

## Fase 9 · MongoDB: letras anotadas

**Objetivo:** entender cuándo y cómo usar una base de datos documental junto a una relacional, sin acoplar el dominio a ella.

**Reto**
- **Reconocimiento, sin código**: con `mongosh` dentro del contenedor, practicar insert, find con proyecciones, operadores de actualización, índices y `explain()`.
- Un modelo de documento para letras al estilo Genius:
  - Estructura: pista (el `track_id` de Postgres) → secciones (intro, verso, estribillo, con el artista que las interpreta) → líneas → anotaciones y votos.
  - **ADR-0004**: qué va embebido y qué va referenciado, teniendo en cuenta el límite de 16 MB y el crecimiento de los arrays.
- El puerto `LyricsRepository` (`typing.Protocol`), con:
  - Un adaptador PyMongo que reutiliza un único `MongoClient`.
  - Un fake en memoria.
- Un management command `mongo_setup` idempotente que crea los índices (único por `track_id` e índice de texto) y la validación `$jsonSchema` de la colección.
- Votos atómicos en las anotaciones con `$inc` + `$addToSet` y sin doble voto. Compáralo con `F()` en PostgreSQL.
- Estadísticas con el aggregation pipeline: las pistas más anotadas, los anotadores más activos y las palabras más frecuentes por artista.
- La API con `Serializer` planos, porque no hay `ModelSerializer` para Mongo.
- Consistencia entre bases de datos:
  - El `track_id` debe existir en PostgreSQL.
  - Al borrar una pista, sus letras se limpian con `on_commit()`.
  - ¿Qué pasa si esa limpieza falla?
- Tests unitarios con el fake y tests de integración con una base de datos de test real, creada y destruida por un fixture.
- ⚠️ Solo versos inventados, nunca letras reales.

**Criterios clave:**
- Los services no importan `pymongo`; solo lo importa el adaptador.
- El doble voto está bloqueado.
- `mongo_setup` se puede ejecutar varias veces sin problema.

**Entrevista:**
- SQL frente a NoSQL. ¿Y por qué no JSONB en PostgreSQL? Respóndelo con honestidad.
- Embebido frente a referencia.
- El límite de 16 MB y los arrays sin límite.
- Atomicidad por documento.
- Transacciones multi-documento (necesitan un replica set).
- Índices y `explain()` en Mongo.
- El orden de las etapas del pipeline: `$match` lo antes posible.
- Qué es un `ObjectId`.
- El patrón repositorio y la inyección de dependencias.
- Consistencia eventual entre bases de datos.

**Problema tipo:** «Escribe el pipeline que devuelva los 5 artistas con más anotaciones en sus versos.»

## Fase 10 · Docker de producción

**Objetivo:** una imagen pequeña, segura y reproducible que arranque igual en cualquier sitio.

**Reto**
- Un Dockerfile multi-stage con uv: cache mounts, `uv sync --locked --no-dev`, bytecode precompilado y usuario no-root.
- gunicorn configurado (workers y timeouts) y whitenoise para los estáticos.
- Un `.dockerignore` completo y un `HEALTHCHECK` contra `/health/`.
- Compose con perfiles de desarrollo y de producción local. Las migraciones se ejecutan como servicio one-off, no al arrancar la app.
- Un presupuesto de tamaño de imagen (por ejemplo, < 250 MB) y el build de la imagen en el CI.
- Ningún secreto dentro de la imagen.

**Criterios clave:**
- El perfil de producción levanta todo y `/health/` devuelve 200.
- La app corre como usuario no-root.
- `docker history` no muestra ningún secreto.

**Entrevista:**
- Capas y caché: por qué se copia primero el lockfile.
- Multi-stage.
- `CMD` frente a `ENTRYPOINT`, la forma exec, el PID 1 y las señales.
- Por qué no-root.
- Workers frente a threads en gunicorn, el GIL y el modo free-threaded de Python.
- WSGI frente a ASGI.
- Estáticos en producción.
- Migraciones sin downtime (expand/contract).
- Por qué los build args no sirven para secretos.

**Problema tipo:** «Este Dockerfile tarda 5 minutos en cada build aunque solo cambies una línea de código. Arréglalo.»

## Fase 11 · Celery + Redis *(extra)*

**Objetivo:** sacar el trabajo lento del ciclo request/response de forma fiable.

**Reto**
- Redis en Compose, la app de Celery en `config/celery.py` y el worker como servicio.
- Una tarea que importa la discografía de un artista desde la API de MusicBrainz (sus datos principales tienen licencia CC0).
- El cliente de MusicBrainz como puerto y adaptador (httpx), con:
  - Un User-Agent identificativo, que es obligatorio.
  - Como máximo 1 petición por segundo.
  - Reintentos con backoff exponencial y jitter ante un 503.
- Idempotencia: `update_or_create` por el identificador de MusicBrainz (mbid). Importar dos veces no duplica nada.
- Un endpoint que encola la importación y responde `202 Accepted` con un `ImportJob` consultable (estado y errores). El encolado se hace en `transaction.on_commit()`.
- Tests con un fake del cliente y con la tarea ejecutada de forma síncrona.

**Criterios clave:**
- La importación es idempotente y respeta el rate limit.
- Un fallo transitorio se reintenta y uno permanente queda registrado en el job.

**Entrevista:**
- Por qué usar tareas en segundo plano.
- Broker frente a result backend.
- Entrega at-least-once y por qué las tareas deben ser idempotentes.
- `acks_late`.
- Reintentos y backoff.
- Qué pasa si encolas dentro de una transacción que luego hace rollback.
- Celery, RQ y el framework de Tasks de Django 6.
- `202` + polling frente a webhooks.

**Problema tipo:** «Una tarea que envía emails se ejecutó dos veces y el usuario recibió dos correos. ¿Por qué pudo pasar y cómo lo evitas?»

## Fase 12 · Caché con Redis *(extra)*

**Objetivo:** responder más rápido sin servir datos incorrectos.

**Reto**
- El backend de caché Redis nativo de Django.
- Cache-aside en los endpoints de estadísticas y de genealogía, con claves versionadas y un TTL justificado.
- Invalidación en `transaction.on_commit()` cuando se crea o se verifica un sample.
- Mitigación del cache stampede en la clave más costosa.
- Caché HTTP (`ETag`/`Last-Modified` y `Cache-Control`) en algún endpoint de lectura.
- Medición del antes y el después.

**Criterios clave:**
- Los tests demuestran la invalidación: no se sirven datos obsoletos después de verificar un sample.
- La mejora está medida y documentada.

**Entrevista:**
- Estrategias: cache-aside, write-through y write-behind.
- Invalidación.
- Stampede.
- Qué no cachear: datos por usuario y permisos.
- Caché HTTP frente a caché de aplicación.
- TTL y políticas de expulsión.
- Redis frente a Memcached.

**Problema tipo:** «Tras activar la caché, algunos usuarios ven datos de otros. ¿Qué ha pasado?»

## Fase 13 · Despliegue en la nube y secretos en producción *(extra)*

**Objetivo:** una URL pública para el portafolio, desplegada de forma automática y segura.

**Reto**
- La plataforma (Render, Koyeb, Fly.io, Railway…) se elige según el free tier vigente y se justifica en el **ADR-0005**.
- PostgreSQL gestionado, MongoDB Atlas en su tier gratuito y Redis gestionado si hay Celery.
- Los secretos viven en el gestor de la plataforma y en GitHub; ninguno en el repo ni en la imagen.
- CD: al mergear en `main` con el CI en verde se despliega de forma automática, y las migraciones son un paso del despliegue.
- HTTPS, HSTS, `SECURE_PROXY_SSL_HEADER` y `CSRF_TRUSTED_ORIGINS`, con `check --deploy` limpio.
- Un smoke test tras el despliegue con la CLI de Bruno contra producción.
- Un procedimiento documentado para rotar `SECRET_KEY` y la clave de firma de los JWT.

**Criterios clave:**
- La URL pública está en el README.
- Un merge a `main` despliega solo.
- El smoke test pasa.

**Entrevista:**
- Estrategias de despliegue: rolling, blue/green y canary.
- Rollback y migraciones irreversibles.
- Rotación de secretos y mínimo privilegio.
- Logs, métricas y trazas.
- Qué comprobar después de un despliegue.

**Problema tipo:** «Tras desplegar, todos los POST devuelven 403 por CSRF y el admin no carga los CSS. Diagnostica.»

## Fase 14 · Portafolio final y simulacro de entrevista *(extra)*

**Objetivo:** convertir el proyecto en tu mejor argumento de entrevista.

**Reto**
- El README final, en inglés, con:
  - Un pitch del proyecto.
  - El diagrama de arquitectura en Mermaid.
  - El stack y cómo ejecutarlo.
  - Las decisiones, con enlaces a los ADRs.
  - Swagger, el badge del CI y la URL pública.
- El tag `v1.0.0` y un CHANGELOG generado a partir de los Conventional Commits.
- Bonus: migrar de Django 5.2 a 6.x (release notes, deprecations y tests en verde).
- **Simulacro de entrevista** de 45–60 minutos:
  - Presentación del proyecto.
  - «Cuéntame una decisión técnica difícil».
  - Teoría de Python, Django, SQL y HTTP.
  - Live coding de ORM/SQL o de un algoritmo sencillo.
  - Un mini diseño de sistema.
  - Al final: feedback completo y un plan de repaso.

**Criterio clave:** alguien que no conoce el proyecto lo entiende y lo arranca solo con el README.

---

## Recursos de referencia

| Tema | Recursos |
|---|---|
| Django 5.2 | [Documentación](https://docs.djangoproject.com/en/5.2/) · [Optimización de la BD](https://docs.djangoproject.com/en/5.2/topics/db/optimization/) · [Checklist de despliegue](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) |
| DRF | [django-rest-framework.org](https://www.django-rest-framework.org/) · [drf-spectacular](https://drf-spectacular.readthedocs.io/) · [django-filter](https://django-filter.readthedocs.io/) · [simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/) |
| Arquitectura | [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide) · [Cosmic Python](https://www.cosmicpython.com/book/preface.html) (incluye un apéndice sobre Django) |
| PostgreSQL | [Documentación de PostgreSQL 17](https://www.postgresql.org/docs/17/) · [Use The Index, Luke](https://use-the-index-luke.com/es) |
| MongoDB | [Data modeling](https://www.mongodb.com/docs/manual/data-modeling/) · [Aggregation](https://www.mongodb.com/docs/manual/aggregation/) · [PyMongo](https://pymongo.readthedocs.io/) |
| Tooling | [uv](https://docs.astral.sh/uv/) · [Ruff](https://docs.astral.sh/ruff/) · [mypy](https://mypy.readthedocs.io/) · [django-stubs](https://github.com/typeddjango/django-stubs) · [pytest-django](https://pytest-django.readthedocs.io/) · [pre-commit](https://pre-commit.com/) |
| Docker | [uv en Docker](https://docs.astral.sh/uv/guides/integration/docker/) · [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/) · [Orden de arranque en Compose](https://docs.docker.com/compose/how-tos/startup-order/) |
| APIs | [RFC 9457 (Problem Details)](https://www.rfc-editor.org/rfc/rfc9457) · [OWASP API Security](https://owasp.org/API-Security/) · [Bruno](https://docs.usebruno.com/) |
| Procesos | [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/) · [ADRs](https://adr.github.io/) · [12-factor](https://12factor.net/es/) |
| Extras | [Celery con Django](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html) · [API de MusicBrainz](https://musicbrainz.org/doc/MusicBrainz_API) · [Caché en Django](https://docs.djangoproject.com/en/5.2/topics/cache/) |
