# ADR-0001: Arquitectura

## Estado

Aceptada    2026-09-23

## Contexto

Un proyecto de software requiere una decisión de arquitectura en la fase de diseño, acorde a las características y el alcance del proyecto.

Crate Digger se proyecta como una API REST pública sobre música Hip Hop, con reglas de negocio propias, consultas a API's externas, base de datos relacional y no relacional, desplegada en producción.

Además, el objetivo principal de este proyecto es aprender sobre desarrollo backend moderno, con buenas prácticas y adaptado a la tendencia actual de la industria. Teniendo en cuenta mi punto de partida como desarrollador y el alcance esperado, es importante elegir una arquitectura para el proyecto demandada, documentada y al mismo tiempo evitar la sobreingeniería. De este modo podré entenderla, ponerla en práctica y sacar el mayor provecho.

## Decisión

Decido aplicar una arquitectura híbrida basada en **Capas pragmáticas** (siguiendo el estilo de [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide)) combinada con **puertos y adaptadores** de **Arquitectura Hexagonal** solo en los bordes, para conectar la base de datos documental y las referencias externas como consultas a APIs de terceros.

La razón de esta elección es tomar los beneficios de estos modelos limitando su complejidad, sin dejar de aprovechar herramientas nativas de Django, como el ORM, el panel de administración, builds y métodos propios.

Por lo tanto, el modelo elegido se compone de:

- Capa de presentación con vistas y serializers delgados, que se ocupan solo del HTTP.

- Capa de servicios con los casos de uso, que concentra las reglas de negocio y transacciones.

- Selectores para lecturas optimizadas

- Capa de dominio con los modelos, cuyas invariantes quedan garantizadas por la base de datos.

- Puertos y adaptadores para MongoDB (lyrics) y API de MusicBrainz: cada puerto es una interfaz (`typing.Protocol`) que implementa un adaptador real y un fake para los tests.

### Alternativas consideradas

- *Fat models*: Se descarta porque la lógica de negocio se dispersa entre modelos, señales y serializers, lo que dificulta el testing y mantenimiento.

- *Hexagonal* / *Clean Architecture* puro: Complejidad y coste elevados para un proyecto solo-dev, ya que se pierden funciones nativas de Django y obliga a duplicar modelos.

## Consecuencias

### Positivas

- La lógica de negocio vive en la capa de servicios, al contrario que *Fat models*, por lo que facilita las pruebas y el seguimiento. Esto, además, crea una línea diferenciada entre lo que *hace* la API y lo que *muestra*.

- Se respeta el principio DIP SOLID Inversión de Dependencias. Con la configuración del ORM de Django para la base de datos relacional y los puertos y adaptadores para Mongo y APIs externas, el núcleo del sistema no depende de los motores elegidos ni del payload de la API. Esto facilita un posible cambio de servicio o actualización en la conexión con los servicios existentes sin alterar la lógica de negocio ni el resto de la API.

- La arquitectura de capas y los puertos y adaptadores permiten optimizar los tests. Se pueden realizar pruebas unitarias de cada servicio o adaptador de forma independiente, utilizando mock y fake data para evitar conexiones a base de datos innecesarias que ralentizarían la suite.

### Trade-off

- La decisión implica lidiar con la complejidad de una arquitectura para la que no tengo experiencia. Tengo que comprender y elegir la estructura adecuada y documentarme sobre las prácticas recomendadas, sus problemas y limitaciones.

- Django presenta limitaciones para arquitecturas no monolíticas. Además de utilizar DRF, voy a tener que conciliar la configuración de sus funciones nativas (como el panel de administración) y prescindir de las que no sean compatibles.
