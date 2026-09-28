# Progreso

> Este archivo es la fuente de verdad del estado del tutorial. Claude lo lee al empezar cada sesión y lo actualiza al cerrar cada fase.

## Estado actual

- **Fase actual:** 1 · Infraestructura local y configuración
- **Estado:** 🟦 En curso. Reto en [`retos/fase-01-infra.md`](retos/fase-01-infra.md).
- **Siguiente paso:** crear la rama `feat/phase-01-infra`, implementar el reto y decir «listo para review».
- **Última actualización:** 2026-09-28

Leyenda: ⬜ pendiente · 🟦 en curso · 🟨 en review · ✅ superada · 🔁 rehacer

## Resumen de fases

| Fase | Estado | Nota /20 | Cierre | PR |
|---|---|---|---|---|
| 0 · Setup profesional | ✅ | 19 | 2026-09-27 | — (commits directos en `main`) |
| 1 · Infra y configuración | 🟦 | — | — | — |
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
| Pendientes de decidir en F1: `extra="forbid"` con las variables de Compose, y dónde vive `BASE_DIR` | F0 · review → preguntas de diseño 1 y 2 del reto F1 | 0 |

## Ayudas usadas

> Aquí se registran las pistas de nivel 3–4 y cualquier código que Claude escriba a petición.

| Fecha | Fase | Nivel | Sobre qué |
|---|---|---|---|
| — | 0 | ninguna | No se pidió ninguna pista; todo el código y las decisiones son propias |

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
