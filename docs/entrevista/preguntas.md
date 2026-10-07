# Banco de preguntas de entrevista

> Se llena al cerrar cada fase con las preguntas de la mini-entrevista. Sirve para repasar antes de una entrevista real: tapa la respuesta, contesta en voz alta y compara.

Formato de cada entrada:

```markdown
### ¿Pregunta? · `F3` · ✅ / 🟡 / ❌
- **Puntos clave:** lo que no puede faltar en una buena respuesta.
- **Repregunta típica:** por dónde seguiría el entrevistador.
- **Mi respuesta:** con tus palabras (esta parte la escribes tú).
```

## Python core

### ¿Qué es un stub? ¿Por qué django-stubs necesita además un plugin de mypy? ¿Qué significa `py.typed`? · `F0` · ✅

- **Puntos clave:**
  - Un stub es un `.pyi` con solo las firmas y los tipos, sin implementación. Los tipos llegan por tres vías: inline con `py.typed` (PEP 561), una distribución de stubs aparte (`django-stubs`, `types-requests`) o typeshed, que mypy trae de serie.
  - mypy hace análisis **estático**; el plugin se engancha al *type-checking*, no a una compilación. Django no genera código en disco: crea atributos en **runtime** con metaclases y descriptores, así que el plugin **simula** lo que haría `ModelBase`.
  - Qué aporta el plugin: `Book.objects` como `Manager[Book]`, las relaciones inversas (`author.book_set`), los tipos de `values()`/`annotate()`, `django.conf.settings` a partir de `django_settings_module` y la asimetría `__get__`/`__set__` de un campo (un `CharField(null=True)` devuelve `str | None` pero acepta más cosas al asignar), que un `.pyi` plano no puede expresar.
  - Sin `py.typed`, mypy **no** asume `Any` en silencio: lanza `import-untyped`. Es `ignore_missing_imports = true` lo que convierte el módulo en `Any`, y entonces `strict` deja de proteger esa frontera.
- **Repregunta típica:** «Si `strict = true` y mypy pasa, ¿puede quedar código sin comprobar en tu proyecto?» (Sí: todo lo que venga de un módulo tratado como `Any`.)
- **Mi respuesta:**

### Orden de los decoradores: ¿por qué `@classmethod` va debajo de `@field_validator`? · `F0` · ✅

- **Puntos clave:**
  - Un decorador es un callable que recibe la función en tiempo de definición (al importar el módulo) y devuelve otra cosa: un wrapper, un descriptor, un objeto marcador.
  - Con decoradores apilados, los *factories* se **evalúan** de arriba abajo (`field_validator(...)` se ejecuta al leer la línea) y las funciones devueltas se **aplican** de abajo arriba.
  - `classmethod` devuelve un descriptor; `field_validator` devuelve un proxy que la metaclase de pydantic recoge del namespace de la clase. Si se invierte el orden, el proxy queda envuelto en un `classmethod`, pydantic no lo reconoce y **el validador no se registra**: falla en silencio si no hay tests.
  - pydantic v2 aplica `classmethod` por su cuenta si falta; se pone de forma explícita por legibilidad, por los type checkers y por las herramientas que no lo automatizan.
  - Pipeline de validación en pydantic-settings: decodificación de la fuente (JSON para tipos complejos, de ahí `NoDecode`) → `before` → validación del tipo → `after`. También existen `wrap` y `plain`.
- **Repregunta típica:** «Escribe un decorador que mida el tiempo de una función. ¿Qué pasa con el `__name__` de la función decorada y cómo lo arreglas?» (`functools.wraps`.)
- **Mi respuesta:**

### ¿Qué imprime una función con un diccionario como argumento por defecto, llamada varias veces? · `F1` · 🟡

- **Puntos clave:**
  - Los valores por defecto se evalúan **una vez**, al ejecutar el `def`, y se guardan en `funcion.__defaults__`. Todas las llamadas que no pasan el argumento comparten **el mismo objeto**.
  - Si la función muta ese objeto y lo devuelve, todas las variables que reciben el resultado son alias: `a is b` es `True` y `len(a) == len(b)` siempre, aunque `a` se asignara «antes».
  - Pasar el argumento de forma explícita (`{}`) no toca el valor por defecto.
  - Arreglo idiomático: `registry=None` y `if registry is None: registry = {}`. No vale `registry or {}` si un diccionario vacío pasado a propósito debe conservarse.
  - En «¿qué imprime?», la salida es la respuesta: hay que seguir el aliasing hasta el final, no solo explicar el mecanismo.
- **Repregunta típica:** «¿Cuándo es útil a propósito un valor por defecto mutable?» (Una caché barata, aunque `functools.cache` es más claro.) «¿Y qué pasa con `def f(t=time.time())`?»
- **Mi respuesta:**

## Django (fundamentos)


### Describe el recorrido de una petición en Django. ¿Qué cambia si mueves un middleware del primer puesto al último? · `F1` · 🟡

- **Puntos clave:**
  - Servidor WSGI → `environ` → `WSGIHandler` (`request_started`, construye el `HttpRequest`) → cadena de middlewares → resolución de la URL → `process_view` → vista con sus decoradores → respuesta de vuelta por los middlewares en orden inverso → `request_finished` al cerrar la respuesta.
  - Modelo de cebolla: cada middleware envuelve al siguiente y puede **cortocircuitar** devolviendo una respuesta sin llamarlo.
  - Las excepciones se convierten en respuestas en cada capa; los 4xx/5xx devueltos se registran en `django.request` **fuera** de la cadena.
  - Un middleware situado al final no ve lo que cortocircuitan los anteriores (redirección a HTTPS, `APPEND_SLASH`, `DisallowedHost`): esas respuestas salen sin su cabecera y esos logs, sin su contexto. Afecta también **al cliente**.
  - CSRF rechaza en `process_view`, que corre en la capa más interna: esa respuesta sí atraviesa todos los middlewares.
- **Repregunta típica:** «¿Por qué `SecurityMiddleware` va casi el primero y `AuthenticationMiddleware` después de `SessionMiddleware`?» (Dependencia de datos: `request.user` se construye a partir de `request.session`, y es perezoso.)
- **Mi respuesta:**

## ORM y SQL

_Todavía no hay preguntas._

## APIs REST y DRF

_Todavía no hay preguntas._

## Testing

_Todavía no hay preguntas._

## Seguridad y autenticación

### ¿Qué te da `SecretStr` y de qué no te protege? · `F0` · ✅

- **Puntos clave:**
  - Envuelve el valor en un atributo de instancia privado y lo enmascara en `repr`, `str` y la serialización JSON: protege de la exposición accidental en logs, en Sentry y en respuestas.
  - El beneficio más fuerte es el tipado: mypy no acepta un `SecretStr` donde se espera `str`, así que cada exposición pasa por `.get_secret_value()` y eso convierte un `grep` en una auditoría de dónde sale el secreto.
  - No protege de: un secreto commiteado (eso es gitleaks o push protection), la memoria del proceso, un debugger, ni del valor una vez extraído.
  - Django enmascara en la página de debug y en los emails de error los settings cuyo **nombre** encaje con `API|AUTH|TOKEN|KEY|SECRET|PASS|SIGNATURE|HTTP_COOKIE`, recorriendo los diccionarios de forma recursiva. Por eso `DATABASES` sale con `PASSWORD` oculto, pero un setting llamado `DATABASE_URL` **no encajaría con nada** y se mostraría entero: la URL cruda no se convierte en setting de Django.
  - Es una heurística basada en nombres, igual que un escáner de secretos lo es sobre formatos. Por eso se apilan capas.
- **Repregunta típica:** «¿Y cómo evitas que el secreto aparezca en los logs de tu propio código, no en los de Django?» (Filtros de logging, no interpolar objetos completos, revisar los `extra` de los loggers.)
- **Mi respuesta:**

### Se te ha filtrado un secreto en un repo público. ¿Qué haces, y en qué orden? · `F0` · *(pendiente de preguntar)*

- **Puntos clave:**
  - **Rotar primero.** El secreto está en el remoto, en la API de GitHub, en los forks y en cachés: borrarlo del repo no lo desfiltra.
  - Después limpiar el historial (`git filter-repo`), coordinar el force-push y revisar accesos y logs por si se usó.
  - Prevención: push protection del secret scanning (rechaza el push antes de que aterrice), hooks locales como primer aviso y CI como red.
  - Distinguir **detección** (llega tarde para un secreto) de **prevención** (lo impide).
- **Mi respuesta:**

### Se despliega con `DEBUG=True` y `ALLOWED_HOSTS=["*"]`. ¿Qué riesgos tiene cada uno? · `F1` · ✅

- **Puntos clave:**
  - `DEBUG=True`: páginas de error con traceback, código, variables locales, ajustes y versiones; el 404 lista las rutas. Además acumula todas las consultas en `connection.queries` (memoria).
  - El filtrado de secretos de la página de error va **por nombre** del ajuste (`KEY`, `SECRET`, `PASS`, `TOKEN`…): una URL de conexión con la contraseña dentro se muestra entera.
  - `ALLOWED_HOSTS` valida la cabecera `Host`, que controla el cliente y que Django usa para construir URLs absolutas. Con `"*"`: envenenamiento del enlace de recuperación de contraseña y de cachés.
  - Con `DEBUG=False` y lista vacía, Django rechaza todas las peticiones: valor por defecto seguro.
  - Prevención: `manage.py check --deploy` en el pipeline y validación del `Host` también en el proxy. Postmortem sin culpables: falla el proceso, no la persona.
- **Repregunta típica:** «El balanceador hace health checks por IP y recibe un 400. ¿Cómo lo resuelves sin abrir `ALLOWED_HOSTS`?» (Configurar la cabecera `Host` del health check en el balanceador.)
- **Mi respuesta:**

## PostgreSQL

_Todavía no hay preguntas._

## MongoDB y NoSQL

_Todavía no hay preguntas._

## Arquitectura y diseño


### ¿Por qué tu middleware solo acepta un `X-Request-ID` entrante si es un UUID? ¿Qué alternativas hay y cuándo te equivocas? · `F1` · 🟡

- **Puntos clave:**
  - Distinguir **aceptar** un id entrante de **generar** uno propio: son dos decisiones.
  - A favor del UUID: validación trivial, formato y tamaño fijos, y devolver siempre `str(uuid.UUID(...))` elimina la inyección en logs por construcción.
  - Alternativas de aceptación: generar siempre (pierdes la correlación con el cliente), lista blanca de caracteres con longitud máxima (más compatible, validación propia), o fiarse solo de un proxy de confianza.
  - Un id entrante sirve para **correlacionar**, no garantiza **unicidad**: el cliente puede repetirlo.
  - `uuid4` es aleatorio (122 bits): unicidad probabilística. `uuid7` lleva marca de tiempo, es ordenable y revela cuándo se creó.
  - Cuándo falla: un proxy o un sistema de trazas con otro formato; sustituir su id rompe la correlación.
- **Repregunta típica:** «¿En qué se diferencia un request id de una traza distribuida? ¿Qué es `traceparent`?»
- **Mi respuesta:**

## Docker y DevOps (CI/CD, despliegue)

### ¿Qué es un lockfile? ¿`uv sync` frente a `uv sync --locked`? · `F0` · 🟡

- **Puntos clave:**
  - Un lockfile fija el **grafo resuelto completo**: no solo tus dependencias directas, también las **transitivas**, con **hashes** por artefacto (integridad de cadena de suministro) y, en uv, una resolución **universal** con marcadores por plataforma y versión de Python.
  - `uv sync`: la fuente de verdad es `pyproject.toml`; si el lock está desfasado, lo regenera en silencio. `uv sync --locked`: la fuente de verdad es `uv.lock` y **aborta** si tendría que cambiarlo. `--frozen`: usa el lock sin ni siquiera compararlo con `pyproject.toml`. El eje `--exact`/`--inexact` es otro: si se eliminan o se respetan los paquetes del entorno que no están en el lock.
  - En CI, siempre `--locked` (o `--frozen` en un `docker build`), para que un lock desfasado sea un error y no una instalación distinta.
  - **Qué no garantiza:** el intérprete (de ahí `.python-version`), las librerías del sistema (libpq, OpenSSL), el compilador de las extensiones en C, ni el entorno. Reproducibilidad real = lock + intérprete fijado + imagen de contenedor.
- **Repregunta típica:** «Si el lockfile ya fija las versiones, ¿por qué necesitas además una imagen de Docker?»
- **Mi respuesta:**

### Alguien hace `git commit --no-verify` y sube código sin formatear, con errores de tipos y una API key. ¿Qué lo impide? · `F0` · ✅

- **Puntos clave:**
  - Los hooks locales son **conveniencia** (feedback rápido, saltable con `--no-verify`); la **puerta** está en el servidor: CI ejecutando lo mismo que los hooks, más `main` protegida con checks **marcados como requeridos**. Que el workflow exista no basta si el ruleset no lo exige; añade *require branches to be up to date* para el caso de dos PRs verdes que rompen juntas.
  - Truco de paridad: ejecutar `pre-commit run --all-files` dentro del workflow, para tener una única fuente de verdad de la lista de hooks.
  - Matiz que separa niveles: para el formato y los tipos, bloquear el merge resuelve. Para el secreto **no**: ya está en el remoto. Ahí hace falta prevención previa al push (push protection) y rotación.
- **Repregunta típica:** «¿Y si el colaborador tiene permisos de admin en el repo?» (Reglas que aplican también a administradores, revisión obligatoria, CODEOWNERS.)
- **Mi respuesta:**

### Haces `docker compose down` y `up -d`: ¿qué se destruye y qué sobrevive? ¿Qué garantiza `depends_on`? · `F1` · ✅

- **Puntos clave:**
  - Imagen: plantilla inmutable por capas. Contenedor: proceso con una capa de escritura encima. Volumen: almacenamiento con ciclo de vida propio.
  - `down` elimina contenedores (con su capa de escritura) y la red; imágenes y volúmenes sobreviven. `down -v` borra también los volúmenes.
  - Las credenciales de las imágenes de BD solo se aplican al **inicializar** el volumen: cambiarlas en `.env` después provoca errores de autenticación.
  - `depends_on` a secas solo ordena el arranque (contenedor iniciado, no listo). Con `condition: service_healthy` espera al healthcheck, **una vez**, al arrancar.
  - Los healthchecks siguen ejecutándose cada `interval`; Compose marca el contenedor como `unhealthy` pero no actúa sobre los dependientes. `--wait` solo bloquea el comando hasta que todo esté `healthy`.
  - La app debe tolerar la caída posterior de la BD: timeouts, reintentos y un readiness propio.
- **Repregunta típica:** «Cambias `POSTGRES_PASSWORD`, haces `down` y `up`, y la app no autentica. ¿Por qué?»
- **Mi respuesta:**

## Git

_Todavía no hay preguntas._

## Celery, Redis y caché

_Todavía no hay preguntas._
