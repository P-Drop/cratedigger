# Reto 0 · Setup profesional

> **Rama:** ninguna. En esta fase commiteas directamente en `main`; las PRs y la protección de `main` llegan en la Fase 2.
> **Cuando termines:** di «listo para review».

## Contexto

Un proyecto profesional empieza antes de la primera línea de lógica:
- Cualquiera debe poder clonarlo y levantarlo con un solo comando.
- Los errores más comunes se deben cazar **antes** de hacer el commit.

Esto también sale en las entrevistas: «¿cómo gestionas las dependencias?», «¿qué es un lockfile?», «¿qué haces para mantener la calidad del código?».

Este directorio ya contiene `CLAUDE.md` y `docs/`, el material del tutorial. Tu trabajo es convertirlo en el repo de **CrateDigger**.

## Objetivo

Un repo público en GitHub con un proyecto Django 5.2 vacío pero **profesional**:
- Dependencias reproducibles con uv.
- Calidad automatizada con ruff, mypy, pytest y pre-commit.
- La arquitectura documentada en un ADR.

## Requisitos

### 1. Git y GitHub

- Un repositorio git cuya rama por defecto sea `main`.
- Un `.gitignore` que cubra Python/Django, uv, los entornos (`.env`), la cobertura, los IDEs y la configuración local de Claude Code (`.claude/settings.local.json`). `CLAUDE.md` **sí** se versiona.
- Un repo **público** en GitHub creado con `gh` (nombre sugerido: `cratedigger`), con `main` subida.

### 2. Proyecto con uv

- Python 3.13 fijado para el proyecto.
- Django 5.2 LTS como dependencia, con un rango de versiones que **no** permita saltar a 6.x.
- Las herramientas de desarrollo van en un grupo de dependencias de desarrollo, no en las de producción: ruff, mypy, django-stubs, pytest, pytest-django, pytest-cov, factory-boy y pre-commit.
- `uv.lock` versionado.

### 3. Proyecto Django

- Creado con `startproject`, de forma que el paquete de configuración se llame `config` y `manage.py` quede en la raíz del repo.
- Todavía **sin apps** y con la base de datos por defecto (SQLite). PostgreSQL llega en la Fase 1.

### 4. Calidad (todo configurado en `pyproject.toml`)

- **ruff** para lint y formato. Elige un conjunto de reglas más amplio que el que viene por defecto y justifica la elección.
- **mypy** en modo `strict` con el plugin de django-stubs.
- **pytest** con pytest-django y la cobertura activada. El umbral mínimo del 85 % se exigirá cuando haya código de verdad, pero puedes dejarlo ya configurado.
- Al menos **un smoke test** que tenga sentido, por ejemplo que el proyecto arranca y que una URL responde.

### 5. pre-commit

Hooks mínimos:
- ruff (lint con autofix) y ruff-format.
- mypy como hook **local** que use el entorno de uv.
- Higiene: espacios al final de línea, salto de línea al final del archivo, YAML y TOML válidos, archivos grandes, marcas de conflicto de merge y claves privadas.
- Comprobación de que `uv.lock` está sincronizado con `pyproject.toml`.
- **Escaneo de secretos**, con la herramienta que elijas.
- **Conventional Commits**, validados en la fase `commit-msg`.

Tanto los hooks de `pre-commit` como los de `commit-msg` deben quedar instalados con un único `pre-commit install`.

### 6. Documentación

- `README.md`, en inglés, con:
  - El nombre del proyecto y una frase que lo explique.
  - El stack.
  - Cómo instalarlo y ejecutarlo (`uv sync`, `runserver`, los tests).
  - Su estado actual.
- `docs/adr/0000-plantilla.md`: una plantilla de ADR en el formato de Michael Nygard (título, estado, contexto, decisión y consecuencias).
- `docs/adr/0001-arquitectura.md`: la arquitectura del proyecto, **explicada con tus palabras** (ver la sección siguiente).

### 7. Commits

- Varios commits **atómicos**, con mensajes en inglés que sigan Conventional Commits. No vale un único «initial commit» con todo.

## La decisión de arquitectura (para tu ADR-0001)

Me pediste una arquitectura moderna y demandada, pero sin sobreingeniería. Esta es la decisión; tu trabajo es **entenderla y defenderla** en el ADR.

- **Capas pragmáticas** al estilo de *HackSoft Django Styleguide*:
  - Vistas y serializers delgados, que solo se ocupan del HTTP.
  - `services.py` con los casos de uso de escritura: reglas de negocio y transacciones.
  - `selectors.py` con las lecturas optimizadas.
  - Los modelos, con las invariantes garantizadas por la base de datos.
- **Puertos y adaptadores (hexagonal) solo en los bordes**: MongoDB (las letras) y la API de MusicBrainz. Cada puerto es un `typing.Protocol` con un adaptador real y un fake para los tests.
- **Alternativas descartadas**:
  - *Fat models*: la lógica se dispersa entre modelos, señales y serializers, y cuesta testearla y seguirla.
  - *Hexagonal o Clean Architecture en todo el proyecto*: envolver el ORM en repositorios hace perder el admin, `ModelSerializer`, los filtros… y obliga a duplicar modelos. Es mucho coste para un equipo pequeño.

El ADR debe incluir el contexto, la decisión, las alternativas consideradas y las consecuencias, tanto las positivas **como las negativas**.

Lectura recomendada antes de escribirlo:
- El README de HackSoft Django Styleguide, en especial las secciones de services y selectors.
- De *Cosmic Python*: el capítulo 2 (Repository), el capítulo 4 (Service Layer) y el apéndice sobre Django.

## Criterios de aceptación

- [x] Un clon limpio del repo se instala con `uv sync --locked` sin errores.
- [x] `uv run python manage.py check` no muestra problemas y `runserver` arranca.
- [x] `uv run pre-commit run --all-files` pasa sin errores.
- [x] `uv run mypy .` pasa en modo strict.
- [x] `uv run pytest` pasa y muestra el informe de cobertura.
- [x] **Demostración 1:** un commit con el mensaje `arreglos varios` es rechazado por el hook. Pega la salida en el chat.

```bash
[Bad commit message] >> arreglos varios
Your commit message does not follow Conventional Commits formatting
https://www.conventionalcommits.org/

```

- [x] **Demostración 2:** un archivo con una credencial falsa pero de formato realista, inventada por ti, es bloqueado por el escaneo de secretos. Pega la salida y **no lo commitees**.

```bash
ERROR: Potential secrets about to be committed to git repo!

Secret Type: AWS Access Key
Location:    config/settings.py:20

Secret Type: Base64 High Entropy String
Location:    config/settings.py:20

Secret Type: Secret Keyword
Location:    config/settings.py:20

```

- [x] En el repo no hay `.env`, `.venv/`, `__pycache__/`, `db.sqlite3`, `.coverage` ni `.claude/settings.local.json`.
- [x] El repo es público en GitHub y tiene el README y el ADR-0001.
- [x] El historial está formado por commits atómicos y convencionales.

## Preguntas de diseño

Respóndelas en el ADR, en el README o en el chat cuando pidas la review:

1. ¿Qué reglas de ruff activaste y por qué? ¿Ignoraste alguna?

Activo las reglas de ruff linter recomendadas que respentan el estilo PEP8 y mantienen un código limpio y legible:

- Longitud de línea de 88 caracteres.
- pycodestyle (reglas E y W).
- pyflakes (relga F).
- isort (regla I).
- pyupdate (regla UP)
- flake8-bugbear (regla B).
- Simplificaciones de código (regla SIM).
- Comprehensions limpias (regla C4).
- Naming de PEP8 (regla N).
- flake8-use-pathlib: pathlib en lugar de os.path (regla PTH).
- flake8-datetimez: utilizar datetimes con zona horaria (regla DTZ).
- flake8-django: específicaciones Django (regla DJ).
- flake8-bandit: seguridad (regla S).
- Detectar print / pprint (regla T20).
- Reglas propias Ruff (regla RUF).

Para el formatter de ruff:

- Activo el formateo del código de ejemplo en docstrings de funciones.

Ignoro la siguiente regla para todo el código fuente:

- E501: longitud de línea. La longitud de línea ya está definida y gestionada por otra regla.

También ignoro la siguiente regla para la suite de tests:

- S101: uso de assert. Se desactiva para permitir asserts solo en tests.

---

2. ¿Por qué mypy como hook local con uv y no con el repositorio espejo oficial (`mirrors-mypy`)?

Configuro mypy como hook local para así utilizar una única fuente de verdad para las dependencias, el uv.lock del repositorio.

---

3. ¿Qué herramienta de escaneo de secretos elegiste y por qué?

Uso gitleaks. En pincipio utilicé detect-secrets porque me pareció que al estar escrito en python implementaría mejor. Pero su heurística falló y detecté un error cuando filtré un secreto (DJANGO_SECRET_KEY válida) en .env.example. Comprobé que detect-secrets detectaba el secreto en settings.py y en un fichero env_temp. Descubrí que el fichero .env.example lo clasificaba como FileType EXAMPLE y no aplicaba los transformers, por ello el Regex de detección de un secreto clave=valor sin comillas ("valor") no lo detectaba. He reemplazado por gitleaks que es más rápido, está escrito en Go y analiza todo el historial del repo (aunque no mantiene un .secrets.baseline para nuevos secretos, procesa con rapidez, pero requiere una instalación global con los binarios en local). He comprobado que gitleaks sí detecta el caso del secreto en .env.example.

---

4. ¿Qué hiciste con las migraciones en ruff y en mypy, y por qué?

Configuro ambas tools en pyproject.toml para que ignoren y no actúen sobre las migraciones. Es código autogenerado por el ORM de Django que no tengo que editar, ni corregir ni testear.

---

5. ¿Versionas `docs/tutorial/` y `docs/entrevista/` (tus notas y tus evaluaciones) en el repo público, o los añades al `.gitignore`? ¿Qué pros y contras tiene cada opción?

Los versiono por trasparencia. Este proyecto, además de crear una herramienta, tiene como objetivo evaluar y desarrollar mis habilidades. Por lo tanto estos archivos forman parte del proyecto, son públicos y abiertos tanto a reclutadores como a todo aquel que quiera obtener un aprendizaje de este desarrollo.

En este caso, mantengo mi progreso y respuestas públicas y accesibles desde el repositorio.

---

## Restricciones

- Todo con uv: nada de `pip install` ni de `requirements.txt`.
- Django 5.2 LTS, no 6.x.
- No añadas todavía dependencias de fases futuras (DRF, psycopg, pymongo…).

## Recursos

- uv: [Working on projects](https://docs.astral.sh/uv/guides/projects/) · [Dependency groups](https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-groups) · [uv con pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/)
- Django 5.2: [Tutorial, parte 1](https://docs.djangoproject.com/en/5.2/intro/tutorial01/) · [startproject](https://docs.djangoproject.com/en/5.2/ref/django-admin/#startproject)
- Ruff: [Configuring Ruff](https://docs.astral.sh/ruff/configuration/) · [Rules](https://docs.astral.sh/ruff/rules/)
- mypy: [The mypy configuration file](https://mypy.readthedocs.io/en/stable/config_file.html) · [django-stubs](https://github.com/typeddjango/django-stubs)
- Tests: [pytest-django](https://pytest-django.readthedocs.io/) · [pytest-cov](https://pytest-cov.readthedocs.io/)
- pre-commit: [pre-commit.com](https://pre-commit.com/) · [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks) · [ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit) · [uv-pre-commit](https://github.com/astral-sh/uv-pre-commit)
- Secretos: [detect-secrets](https://github.com/Yelp/detect-secrets) · [gitleaks](https://github.com/gitleaks/gitleaks)
- Git y GitHub: [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/) · [gh repo create](https://cli.github.com/manual/gh_repo_create)
- ADRs: [adr.github.io](https://adr.github.io/) · [Documenting Architecture Decisions (Nygard)](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- Arquitectura: [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide) · [Cosmic Python](https://www.cosmicpython.com/book/preface.html)

## Fuera de alcance

- Docker, PostgreSQL y MongoDB (Fase 1).
- El CI y las PRs (Fase 2).
- Cualquier modelo o app de dominio (Fase 3).

## Temas de la mini-entrevista

- Lockfile y builds reproducibles.
- uv frente a pip o poetry.
- Dependencias de producción frente a las de desarrollo.
- Linter, formatter y type checker.
- Qué garantiza pre-commit y qué no.
- Tipado gradual y stubs.
- Conventional Commits y SemVer.
- Merge frente a rebase.
- Qué hacer si se filtra un secreto.
