# Reto 2 · CI y flujo de PRs

> **Rama:** `feat/phase-02-ci`. Al terminar, abre una PR contra `main` con una descripción. Es la última PR que podrá entrar sin pasar por las reglas que tú vas a definir.
> **Cuando termines:** di «listo para review».

## Contexto

Hoy la calidad de CrateDigger depende de que pre-commit se ejecute en tu máquina. Eso es una cortesía, no una garantía: `git commit --no-verify` se lo salta, un clon nuevo no tiene los hooks instalados y nadie comprueba que los tests pasen en un entorno que no sea el tuyo. La PR #1 se pudo mergear sin que ninguna máquina ajena ejecutara nada.

La Fase 1 dejó el terreno preparado, y este reto parte de ahí:

- El marker `integration` separa los tests que necesitan PostgreSQL y MongoDB reales. La suite `-m "not integration"` corre sin infraestructura en medio segundo.
- `EnvSettings` tiene 7 variables obligatorias y `extra="forbid"`. En el CI no hay `.env`.
- `compose.yaml` fija `postgres:17.11-trixie` y `mongo:7.0.43-jammy`. En la PR #1 te comprometiste a automatizar su actualización en esta fase.
- `addopts` lleva `--cov` y `--cov-fail-under=85` con tu nota «temporal, después irá solo en CI».
- gitleaks solo mira lo que está en *staging*. El historial completo no lo escanea nadie.
- El merge de la Fase 1 quedó en `main` como `Merge phase 01: local infrastructure and configuration (#N)`: un asunto que no es convencional y que conserva un `#N` literal. Tenlo delante cuando elijas la estrategia de merge.

En GitHub, el repo no tiene ninguna regla: no hay rulesets, los tres métodos de merge están permitidos y las ramas no se borran al mergear.

## Objetivo

Que nada entre en `main` sin pasar por una PR con el CI en verde, y que eso lo garantice GitHub y no tu disciplina.

## Requisitos

### 1. Workflow de CI

- Un workflow de GitHub Actions que se ejecute en las PRs contra `main` y en los push a `main`.
- uv instalado en una versión fijada, con **caché** ligada al lockfile.
- Las dependencias se instalan de forma que el job **falle** si `uv.lock` no está sincronizado con `pyproject.toml`.
- La versión de Python sale de una única fuente de verdad, la que ya tiene el repo. No se repite a mano en el workflow.
- Permisos del `GITHUB_TOKEN` reducidos al mínimo que el workflow necesita, declarados de forma explícita.
- Un push nuevo a una PR cancela la ejecución anterior que siga en curso.
- Cada job tiene un límite de tiempo explícito.
- Las actions de terceros van fijadas a una versión concreta (pregunta de diseño 3).

### 2. Qué se comprueba

- **Calidad:** lint, formato y tipos. Tú decides si con pre-commit, con las herramientas directamente o con una mezcla (pregunta de diseño 1). Lo que se ejecute en CI y lo que se ejecute en local no pueden divergir en versiones.
- **Tests unitarios:** se ejecutan **sin** servicios levantados. Si un test unitario necesita una BD, el CI debe delatarlo.
- **Tests de integración:** contra PostgreSQL y MongoDB como *service containers*, en las **mismas versiones** que `compose.yaml` y con healthchecks: los tests no pueden arrancar antes de que los servicios estén listos.
- **Cobertura:** el umbral del 85 % se exige en el CI. Resuelve la nota «temporal» de `addopts` y decide dónde y sobre qué datos se evalúa (pregunta de diseño 2).

### 3. Configuración y secretos en el CI

- Las variables que `EnvSettings` exige llegan por entorno.
- **Sin GitHub Secrets y sin secretos reales**: las credenciales de los servicios del CI son de usar y tirar, y deben verse como tales.
- Un job que escanee secretos en el **historial completo** del repo, no solo en el último commit.

### 4. Actualización automática de dependencias

- Configura Dependabot o Renovate (tú eliges y justificas) para cubrir, como mínimo, las dependencias de Python y las actions del workflow.
- Las imágenes de `compose.yaml` y los hooks de pre-commit: comprueba en la documentación de la herramienta que elijas si los soporta. Si alguno no se puede cubrir, documenta cómo lo mantendrás al día.
- Con una cadencia y una agrupación que no te inunden de PRs.

### 5. Flujo de PRs

- Una plantilla de PR que pida lo que tu Definition of Done exige. Corta: una plantilla que nadie rellena no sirve.
- Un **ruleset** sobre `main` que:
  - Exija PR para cualquier cambio.
  - Exija en verde los checks del CI que tú decidas (pregunta de diseño 5).
  - Impida el force-push y el borrado de la rama.
  - Se te aplique **también a ti**, que eres admin del repo.
- Una estrategia de merge elegida, justificada en el README y **reflejada en los ajustes del repo**: los métodos que descartes quedan deshabilitados. Decide también qué pasa con la rama tras el merge.

### 6. Documentación

- El badge del CI en el README, apuntando a `main`.
- La fila «CI» del stack actualizada y una sección breve sobre el flujo de contribución: rama, PR, checks y estrategia de merge.
- Las respuestas a las preguntas de diseño, en la PR o al final de este archivo.

## Criterios de aceptación

- [ ] El workflow se ejecuta en la PR de esta fase y termina en verde. Enlaza el run en la PR.
- [ ] Una **PR de prueba** con un test roto a propósito queda con el check en rojo y el botón de merge bloqueado. Tras arreglarlo, pasa. Enlaza la PR y pega una captura o la salida de `gh pr checks` de ambos estados. La PR de prueba se cierra sin mergear.
- [ ] Un `git push` directo a `main` es rechazado. Pega la salida.
- [ ] Un job que modifica `pyproject.toml` sin regenerar `uv.lock` falla. Demuéstralo en la PR de prueba o en un run enlazado.
- [ ] La segunda ejecución del workflow muestra *cache hit* en uv. Anota en la PR el tiempo total con la caché fría y con la caché caliente.
- [ ] Los tests unitarios pasan en un job que no tiene servicios; los de integración, en uno que los tiene. Ningún test queda sin ejecutarse: el número total coincide con el de `uv run pytest` en local.
- [ ] El CI falla si la cobertura baja del 85 %. Explica en la PR cómo lo comprobaste.
- [ ] El workflow no usa ningún secreto de GitHub y sus `permissions` están declarados.
- [ ] El escaneo de secretos recorre todo el historial y pasa.
- [ ] `gh api repos/P-Drop/cratedigger/rulesets` muestra el ruleset activo. Pega en la PR el detalle de sus reglas y de quién puede saltárselas.
- [ ] `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed,deleteBranchOnMerge` refleja la estrategia que describes en el README.
- [ ] La configuración de actualización de dependencias está en `main` y la herramienta ha abierto, o ha informado de que no necesita abrir, su primera PR.
- [ ] El badge del README se ve bien **renderizado** en GitHub y enlaza al workflow.
- [ ] `uv run pre-commit run --all-files`, `uv run mypy .` y `uv run pytest` siguen en verde en local.
- [ ] Commits atómicos y convencionales, con asuntos de **72 caracteres como máximo**. La PR está descrita con tu plantilla.

## Restricciones

- Solo GitHub Actions con runners alojados por GitHub. Sin servicios de CI externos.
- Sin GitHub Secrets.
- Sin `docker compose` dentro del CI: los servicios son *service containers* del workflow.
- Sin `continue-on-error` ni condiciones que dejen un check en verde cuando algo ha fallado.
- No se rebaja ningún umbral ni se excluye código de la cobertura para que el CI pase.
- No se reescribe el historial publicado de `main`.
- El ruleset no tiene una excepción a tu nombre.

## Preguntas de diseño

Respóndelas en la PR o al final de este archivo.

1. Repasa tu `.pre-commit-config.yaml` hook por hook. ¿Cuáles tiene sentido ejecutar en el CI, cuáles no y cuáles hay que ejecutar de otra forma? Si pre-commit ya lo comprueba todo en local, ¿qué aporta repetirlo en el CI?
2. ¿Un job o varios? ¿Qué ganas y qué pierdes con cada opción? Si separas los tests unitarios de los de integración, ¿qué mide cada job por separado y cómo consigues que el 85 % se evalúe sobre el total?
3. Al referenciar una action, ¿qué diferencia hay entre fijarla a una rama, a un tag o al SHA de un commit? ¿Qué elegiste y qué riesgo aceptas? Enlázalo con lo que aprendiste sobre los tags de las imágenes de Docker.
4. ¿Qué diferencia hay entre los eventos `pull_request` y `pull_request_target`? ¿Por qué importa en un repo público que acepta PRs desde forks, y qué tiene que ver con que tu CI no necesite secretos?
5. ¿Qué checks marcaste como obligatorios en el ruleset y por qué esos? ¿Qué pasa con un check obligatorio si su job no llega a ejecutarse (por un filtro de rutas, por ejemplo)? ¿Exiges que la rama esté al día con `main` antes de mergear? ¿Qué coste tiene?
6. Squash, merge commit o rebase: ¿qué queda en `main` con cada uno y qué pasa con tus commits atómicos? ¿Cómo evita tu elección que se repita un asunto como el de `aa61ff7`? ¿Qué papel juega entonces el título de la PR?
7. Dependabot o Renovate: ¿por qué uno y no otro? ¿Mergearías sus PRs de forma automática? ¿Con qué condiciones?
8. Tu CI ejecuta código de cualquier PR. ¿Qué podría hacer una PR maliciosa desde un fork con el workflow tal como lo has dejado, y qué se lo impide?

## Recursos

- GitHub Actions: [Sintaxis de workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) · [Eventos](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) · [Service containers de PostgreSQL](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers) · [Caché de dependencias](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching) · [Uso seguro](https://docs.github.com/en/actions/reference/security/secure-use) · [Badge de estado](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge)
- uv: [Uso en GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/) · [setup-uv](https://github.com/astral-sh/setup-uv)
- Repositorio: [Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) · [API REST de reglas](https://docs.github.com/en/rest/repos/rules) · [Métodos de merge](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github) · [Plantilla de PR](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository)
- Dependencias: [Opciones de Dependabot](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference) · [Renovate](https://docs.renovatebot.com/)
- Calidad: [pre-commit en CI](https://pre-commit.com/#usage-in-continuous-integration) · [coverage: comandos](https://coverage.readthedocs.io/en/latest/cmd.html) · [gitleaks](https://github.com/gitleaks/gitleaks)
- Imágenes: [mongo en Docker Hub](https://hub.docker.com/_/mongo) (variables y healthcheck del servicio)

## Fuera de alcance

- Matriz de versiones de Python o de bases de datos. Es tema de entrevista, no requisito.
- El build de la imagen de la app en el CI (Fase 10).
- Continuous Delivery y despliegue (Fase 13).
- La colección de Bruno en el CI (Fase 4).
- Publicar la cobertura en servicios externos (Codecov y similares).
- Código de la app: esta fase no debería tocar `cratedigger/` salvo que el CI destape un fallo real.

## Temas de la mini-entrevista

- Continuous Integration, Continuous Delivery y Continuous Deployment.
- Qué debe bloquear un merge y qué no.
- Tests flaky.
- Secretos en el CI y el modelo de confianza de las PRs.
- Caché de dependencias: claves, invalidación y qué se cachea.
- Runners y aislamiento entre jobs.
- Matrices de versiones.
- Estrategias de merge e historial de git.
- «Pasa en mi máquina pero falla en el CI».
- Python core: entornos, intérprete y resolución de imports.
