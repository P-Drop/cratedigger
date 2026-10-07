# Progreso

> Este archivo es la fuente de verdad del estado del tutorial. Claude lo lee al empezar cada sesión y lo actualiza al cerrar cada fase.

## Estado actual

- **Fase actual:** 2 · CI y flujo de PRs (sin abrir)
- **Estado:** ⬜ Pendiente de abrir. La Fase 1 está superada con 17/20.
- **Siguiente paso:** mergear la [PR #1](https://github.com/P-Drop/cratedigger/pull/1) en `main`. Después, cuando digas, abro la Fase 2 con el repaso espaciado (2 preguntas) y el enunciado del reto.
- **Última actualización:** 2026-10-07

Leyenda: ⬜ pendiente · 🟦 en curso · 🟨 en review · ✅ superada · 🔁 rehacer

## Resumen de fases

| Fase | Estado | Nota /20 | Cierre | PR |
|---|---|---|---|---|
| 0 · Setup profesional | ✅ | 19 | 2026-09-27 | — (commits directos en `main`) |
| 1 · Infra y configuración | ✅ | 17 | 2026-10-07 | [#1](https://github.com/P-Drop/cratedigger/pull/1) |
| 2 · CI y flujo de PRs | ⬜ | — | — | — |
| 3 · Modelado del catálogo | ⬜ | — | — | — |
| 4 · API del catálogo | ⬜ | — | — | — |
| 5 · Auth, permisos y seguridad | ⬜ | — | — | — |
| 6 · Samples | ⬜ | — | — | — |
| 7 · ORM avanzado y rendimiento | ⬜ | — | — | — |
| 8 · PostgreSQL a fondo | ⬜ | — | — | — |
| 9 · MongoDB: letras anotadas | ⬜ | — | — | — |
| 10 · Docker de producción | ⬜ | — | — | — |
| 11 · Celery + Redis *(extra)* | ⬜ | — | — | — |
| 12 · Caché con Redis *(extra)* | ⬜ | — | — | — |
| 13 · Despliegue *(extra)* | ⬜ | — | — | — |
| 14 · Portafolio y simulacro *(extra)* | ⬜ | — | — | — |

## Temas a repasar

> Esta lista se alimenta con los fallos de las mini-entrevistas y de las reviews. Al abrir cada fase, Claude pregunta 2 temas de aquí. Un tema sale de la lista cuando se responde bien dos veces, en sesiones distintas.

| Tema | Origen | Aciertos |
|---|---|---|
| Qué garantiza un lockfile (grafo transitivo, hashes, resolución universal) y qué **no** garantiza (intérprete, librerías del sistema, compilador). Un contenedor comparte el kernel del host; la imagen solo es reproducible fijada por digest | F0 · P1 🟡 · repaso F1 🟡 (faltó la resolución universal; sobrestimó la reproducibilidad del contenedor) | 0 |
| Secretos ya publicados: detección ≠ prevención. Rotar primero, luego limpiar historial; push protection como barrera previa. Matices: análisis de impacto en paralelo a la rotación, mínimo privilegio | F0 · P2, matiz no cubierto · repaso F1 ✅ | 1 |
| Orden de los middlewares: qué pierde **el cliente** (no solo los logs) cuando una capa exterior cortocircuita; `process_view` y dónde rechaza CSRF. Describir el código propio tal como es, sin atribuirle arquitectura que aún no tiene | F1 · P1 🟡 | 0 |
| Healthchecks de Docker: se ejecutan cada `interval` durante toda la vida del contenedor; lo que se evalúa una sola vez es la condición de `depends_on`. Qué hace y qué no hace `--wait` | F1 · P2, matiz fallado | 0 |
| Request id: política de **aceptación** frente a **generación**; correlación ≠ unicidad; `uuid4` es aleatorio (unicidad probabilística); `uuid7` | F1 · P4 🟡 | 0 |
| Problemas de «¿qué imprime?»: seguir el aliasing hasta el final (si `a is b`, cualquier lectura de `a` ve lo que se hizo por `b`) | F1 · P5 🟡 | 0 |
| Tests que pasan por el motivo equivocado: comprobar que un test falla cuando debe (quitar la fixture, romper el código); coste de un `except Exception` amplio | F1 · review, 2.ª ronda | 0 |

## Ayudas usadas

> Aquí se registran las pistas de nivel 3–4 y cualquier código que Claude escriba a petición.

| Fecha | Fase | Nivel | Sobre qué |
|---|---|---|---|
| — | 0 | ninguna | No se pidió ninguna pista; todo el código y las decisiones son propias |
| — | 1 | ninguna | No se pidió ninguna pista. Hubo una aclaración de criterios (alcance del request id en los logs, 2026-10-05), que no cuenta como pista |

## Registro de evaluaciones

### Fase 0 · Setup profesional (2026-09-27)

| Criterio | Nota | Comentario |
|---|---|---|
| Funcionalidad | 4/4 | Los 10 criterios de aceptación verificados de forma independiente: clon limpio + `uv sync --locked`, los cuatro checks en verde, las dos demostraciones de los hooks y el repo público con README y ADR. Extras no pedidos: licencia MIT y columna de estado en el stack. |
| Diseño y código | 4/4 | `config/env.py` con `SecretStr`, `NoDecode` + validador `before` y *fail fast*; `[tool.pydantic-mypy]` con `init_typed`; selección de reglas de ruff justificada una por una. El refactor eliminó la fuga de `Any`: los settings pasaron de `Any` a `str`, `bool`, `list[str]` y un `TypedDict`. |
| Tests | 4/4 | 20 tests, 100 % de cobertura. Aislamiento con `_env_file=None`, fixture derivada de `model_fields`, aserciones sobre `errors()` en vez de sobre mensajes, y casos borde reales (`"a,,b, ,"`, asimetría entre variable extra en `.env` y en el entorno). |
| Proceso | 3/4 | Commits atómicos y convencionales, remoto y `stages` corregidos. Restan tres lecciones: un commit de 169 caracteres con dos temas dentro; reescritura y force-push de historial ya publicado por un typo; y cambios en el README publicados sin revisar el renderizado (la tabla quedó rota). Los tests del refactor llegaron después de la review, no con el cambio. |
| Entrevista | 4/4 | P1 🟡 (lockfile: faltaron dependencias transitivas, hashes y la mitad de «qué no garantiza»). P2, P3, P4 y P5 ✅, con investigación propia y un experimento para verificar el orden de los decoradores. |
| **Total** | **19/20** | **Listo para entrevista** |

- **Fortalezas:**
  - Investigación autónoma con causa raíz. El análisis de por qué detect-secrets no vio la clave en `.env.example` (`FileType.EXAMPLE` se salta los transformers) es material de entrevista.
  - Dos decisiones propias bien fundamentadas y ejecutadas: gitleaks en lugar de detect-secrets y pydantic-settings en lugar de django-environ.
  - Documenta el porqué donde se lee: comentarios en `pyproject.toml`, ADR-0001 con trade-offs honestos y las respuestas de diseño escritas en el repo.
- **A mejorar:**
  - La primera entrega publicó una `SECRET_KEY` usable en un repo público. No hubo filtración real (no era la clave local), pero el reflejo debe ser automático: en un archivo de ejemplo solo van marcadores.
  - Los tests acompañan al cambio, no llegan después de que alguien señale el hueco.
  - Lo que se publica se revisa renderizado, no en el diff.
- **Mini-entrevista:** P1 🟡 · P2 ✅ · P3 ✅ · P4 ✅ · P5 ✅

### Fase 1 · Infraestructura local y configuración (2026-10-07)

| Criterio | Nota | Comentario |
|---|---|---|
| Funcionalidad | 4/4 | Los 10 criterios de aceptación verificados de forma independiente, también en vivo: ambos servicios `healthy`, `/health/` 200 y 503 con cada BD parada (2,3 s con Mongo caído), `X-Request-ID` reutilizado, sustituido y presente en 404 y 400. Desviación aceptada y documentada: MongoDB 7 en lugar de 8 (SERVER-121912). |
| Diseño y código | 4/4 | `${VAR:?}` en Compose coherente con el *fail fast* de `EnvSettings`; `pg_isready -h 127.0.0.1`; middleware sin inyección por construcción y con `reset` en `finally`; registro de checks; `MongoClient` perezoso con `@cache`; `SET LOCAL statement_timeout`. La primera entrega tenía `django.server` saliendo por el handler de último recurso (`propagate`), corregido. Nit abierto: `InterfaceError` no hereda de `DatabaseError`. |
| Tests | 3/4 | Estado final bueno: 76 tests, 100 % sobre 163 sentencias reales, marker `integration` y suite unitaria sin infraestructura en 0,5 s. Resta: hicieron falta tres rondas. Los tests contaban en la cobertura (heredado de F0), faltaba el test de logging, y un refactor dejó dos tests pasando por el bloqueo de BD de pytest-django en lugar de por el fallo simulado. |
| Proceso | 3/4 | PR bien descrita, con desviaciones y evidencias; README al día; mensajes de commit que explican el porqué y las limitaciones. Resta: dos asuntos de 109 y 120 caracteres (lección repetida de F0), `cac0eb3` mezcla cuatro cambios y una errata en un asunto ya publicado. Bien resuelto: no se reescribió historial publicado. |
| Entrevista | 3/4 | P1 🟡 · P2 ✅ · P3 ✅ · P4 🟡 · P5 🟡. Las tres repreguntas respondidas, ✅. Los 🟡 son de precisión, no de concepto: «nunca afecta al cliente», alternativas de generación cuando se preguntaba por aceptación, y una salida mal calculada pese a explicar bien el mecanismo. |
| **Total** | **17/20** | **Sólido** |

- **Fortalezas:**
  - Detalles de infraestructura por encima del nivel junior: el healthcheck que evita el falso `healthy` de la inicialización, la interpolación obligatoria en Compose y la explicación de `MongoClient` con fork.
  - Respuestas de diseño a nivel de entrevista: `InconsistentMigrationHistory` y la migración a un User propio en producción; liveness frente a readiness.
  - Reacción a la review: cada hallazgo corregido en un commit propio, y razonamiento honesto ante lo que no conoce («no tengo experiencia, pero razono»).
- **A mejorar:**
  - Verificar lo que se afirma: el commit `b2867d1` decía que `django.server` propagaba a root y no era cierto. Una prueba manual de 10 segundos lo habría mostrado.
  - Comprobar que un test falla cuando debe, sobre todo después de un refactor del código que prueba.
  - En la entrevista: responder a lo que se pregunta, no adornar el código propio y calcular la salida hasta el final.
  - Asuntos de commit de 72 caracteres como máximo: segunda fase en la que aparece.
- **Mini-entrevista:** P1 🟡 · P2 ✅ · P3 ✅ · P4 🟡 · P5 🟡
- **Añadido a «Temas a repasar»:** orden de middlewares y efecto en el cliente; ciclo de vida de los healthcheck y `depends_on`; aceptación frente a generación del request id; aliasing en «¿qué imprime?»; tests que pasan por el motivo equivocado.
- **Pendiente para fases futuras:** el stack de `CLAUDE.md` y el ROADMAP dicen MongoDB 8; revisar cuando se resuelva SERVER-121912.

<!-- Plantilla: se copia al cerrar cada fase.

### Fase N · Título (AAAA-MM-DD)

| Criterio | Nota | Comentario |
|---|---|---|
| Funcionalidad | /4 | |
| Diseño y código | /4 | |
| Tests | /4 | |
| Proceso | /4 | |
| Entrevista | /4 | |
| **Total** | **/20** | Etiqueta |

- **Fortalezas:**
- **A mejorar:**
- **Mini-entrevista:** P1 ✅ · P2 🟡 · P3 ❌ · P4 ✅ · P5 ✅
- **Añadido a «Temas a repasar»:**
-->
