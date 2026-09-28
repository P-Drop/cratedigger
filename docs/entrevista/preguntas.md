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

## Django (fundamentos)

_Todavía no hay preguntas._

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

## PostgreSQL

_Todavía no hay preguntas._

## MongoDB y NoSQL

_Todavía no hay preguntas._

## Arquitectura y diseño

_Todavía no hay preguntas._

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

## Git

_Todavía no hay preguntas._

## Celery, Redis y caché

_Todavía no hay preguntas._
