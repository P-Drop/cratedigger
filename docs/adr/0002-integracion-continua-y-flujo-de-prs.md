# ADR-0002: Integración continua y flujo de PRs

## Estado

Aceptada    2026-10-14

## Contexto

Hasta la Fase 1, la calidad del proyecto dependía de los hooks de pre-commit en mi máquina. Esa barrera se salta con `git commit --no-verify`, no existe en un clon nuevo y no comprueba nada fuera de mi entorno local. La PR de la Fase 1 llegó a `main` sin que ninguna máquina ajena ejecutara los tests, y su *merge commit* quedó con un asunto no convencional.

El objetivo de la Fase 2 es que nada entre en `main` sin pasar por una PR con el CI en verde, y que eso lo garantice GitHub y no mi disciplina. El repositorio es público, admite PRs desde forks y lo desarrollo yo solo, con una rama y una PR por fase.

El detalle de cada decisión, las pruebas y las alternativas analizadas están en el [reto de la Fase 2](../tutorial/retos/fase-02-ci.md). Este ADR recoge las decisiones que condicionan el trabajo de las fases siguientes.

## Decisión

### 1. El CI es la barrera real y `main` está protegida por un ruleset

- Workflow de GitHub Actions en `pull_request` y `push` a `main`, con seis jobs separados por responsabilidad: calidad, escaneo de secretos en todo el historial, tests unitarios **sin** servicios, tests de integración con PostgreSQL y MongoDB como *service containers*, cobertura combinada y comprobación de los mensajes de commit.
- El workflow reutiliza los hooks definidos en `.pre-commit-config.yaml`. Para no repetir la lista ejecuta todos los hooks, por lo que se configura una lista de excepciones con `ci: skip: [uv-lock, gitleaks]`. En caso de añadir hooks que validan en CI no se requiere actualización, se añaden a esta lista solamente los hooks estrictamente locales.
- Los seis checks son obligatorios en un ruleset sobre `main`, con su origen fijado a GitHub Actions. El ruleset exige PR, prohíbe el *force push* y el borrado, exige que la rama esté al día con `main` y **no tiene excepciones**, tampoco para mí como administrador.
- El umbral de cobertura (85 %) vive en `[tool.coverage.report] fail_under` y se evalúa una sola vez, sobre los datos combinados de los tests unitarios y de integración.
- El CI no usa secretos: las variables de configuración son valores falsos y desechables. Las PRs de contribuidores externos requieren aprobación antes de ejecutar el workflow.

### 2. Estrategia de merge: *merge commit*

- Solo está habilitado el *merge commit*. El asunto del merge es el título de la PR, que debe seguir Conventional Commits, y la rama se borra al mergear.
- Las ramas se actualizan con `main` mediante *rebase*, para no introducir *merge commits* de `main` en la rama.
- Todos los commits de la rama llegan a `main`, así que deben ser atómicos, convencionales y estar limpios antes de la review.

### 3. Versiones fijadas con una única fuente de verdad

- Actions fijadas por SHA, con la versión en un comentario. Imágenes de Docker fijadas por *digest*, idénticas en `compose.yaml` y en el workflow. Runner fijado por etiqueta (`ubuntu-24.04`).
- `uv.lock` es la fuente de verdad de las herramientas de calidad: ruff y mypy se ejecutan como hooks locales con `uv run`, y el CI los invoca a través de pre-commit. La versión de Python sale de `.python-version` y la de uv de `required-version`.

### 4. Actualización de dependencias con Renovate

- Renovate, con cadencia semanal. Las versiones duplicadas (uv en `pyproject.toml` y en pre-commit, gitleaks en pre-commit y en el workflow, imágenes en `compose.yaml` y en el workflow) se agrupan para actualizarse en la misma PR.
- Las actualizaciones *major* y los cambios de intérprete de Python requieren aprobación en el *dependency dashboard*. Mongo se mantiene por debajo de 8 hasta que se resuelva SERVER-121912.
- Sin *automerge* por ahora.

### Alternativas descartadas

- ***Squash merge***: aplastaría una PR de fase con varios temas en un único commit y perdería la granularidad para `bisect` y `blame`. Sería la opción razonable con PRs pequeñas de un solo propósito.
- ***Rebase merge***: conserva los commits, pero pierde la agrupación por fase en el historial.
- **Un único job de CI**: más simple, pero los tests unitarios se ejecutarían con las bases de datos levantadas y no se detectaría un test unitario que dependa de ellas. Además, los jobs no se ejecutarían en paralelo.
- **Dependabot**: es nativo de GitHub, pero no puede mantener sincronizadas las copias duplicadas de una misma versión.
- **Fijar actions por tag y el runner con `ubuntu-latest`**: son referencias móviles. Un tag puede moverse a otro commit, y `ubuntu-latest` cambia de sistema cuando GitHub lo decide.
- ***Merge queue***: resuelve los conflictos semánticos entre PRs simultáneas sin forzar reejecuciones en cadena, pero no compensa con un solo desarrollador.

## Consecuencias

### Positivas

- La calidad de `main` deja de depender de mi disciplina: ningún cambio llega sin PR y sin los cinco checks en verde, y la regla me afecta igual que a cualquier colaborador.
- El historial de `main` conserva los commits atómicos y, a la vez, se puede leer por fases con `git log --first-parent`. El título de la PR evita asuntos no convencionales como el del merge de la Fase 1.
- Las versiones de herramientas, actions e imágenes son reproducibles, y sus actualizaciones llegan como PRs revisables que pasan el mismo CI.
- Un CI sin secretos permite aceptar PRs desde forks con el evento `pull_request`, sin tener que recurrir a `pull_request_target`.

### Trade-off

- El historial de `main` no es lineal, y cada commit de la rama debe estar limpio antes de la review.
- Exigir la rama al día obliga a hacer *rebase* y a repetir el CI cada vez que `main` avanza. Con un solo desarrollador el coste es mínimo, pero escalaría mal con muchas PRs simultáneas.
- Renovate es una app de terceros con permiso de escritura en el repositorio. Su configuración (`customManagers`, reglas de agrupación y aprobación) añade complejidad.
- Quedan pasos manuales: actualizar el hash SHA-256 de gitleaks en cada nueva versión (la PR de Renovate falla hasta hacerlo) e instalar localmente la versión exacta de uv.
- La configuración de GitHub (ruleset, métodos de merge, *push protection*, aprobación de forks) no vive en el código. `.github/rulesets/main.json` es una copia de referencia que puede quedar desfasada si se cambia desde la web.
