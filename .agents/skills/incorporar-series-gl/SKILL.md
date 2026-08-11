---
name: incorporar-series-gl
description: Investigar, auditar y completar series GL en GL Verse con datos contrastados, trazabilidad, prevención de duplicados y el importador JSON del proyecto. Usar cuando se pida añadir o actualizar series, reparto, personajes, parejas, imágenes, disponibilidad, empresas, colecciones, temporadas, episodios, etiquetas, advertencias, nivel de drama o tipo de final; preparar código solo si el modelo real no permite guardar la información solicitada.
---

# Incorporar series GL

## Objetivo

Investigar datos reales de una o varias series GL e incorporarlos a GL Verse sin inventar información, duplicar entidades ni romper el modelo existente.

## Flujo de trabajo

### 1. Revisar el repositorio

Antes de investigar o editar:

1. Leer `AGENTS.md`, `README.md` y `pyproject.toml`.
2. Revisar el modelo, los repositorios, las migraciones y las pruebas actuales.
3. Identificar el mecanismo vigente de carga de datos y los comandos de comprobación.
4. Seguir siempre el estado real del repositorio aunque haya cambiado respecto a estas instrucciones.
5. Leer [references/catalog-coverage.md](references/catalog-coverage.md) al completar una ficha, auditar campos pendientes o clasificar drama, final, etiquetas o advertencias.

Actualmente, GL Verse utiliza `gl-verse importar-series` para ampliar el catálogo y reserva las migraciones SQL para cambios de esquema y datos iniciales. No asumir que seguirá siendo así: comprobarlo en cada ejecución.

### 2. Delimitar la petición

- Consultar `series_review_status` antes de auditar o preparar una carga. Si una serie está `approved`, omitirla e informar de que ya fue aceptada editorialmente, salvo que el usuario pida expresamente revisarla, corregirla o reabrirla.
- Tratar `pending` y la ausencia de registro como pendientes de revisión. El estado editorial no demuestra que un dato sea verdadero y no sustituye fuentes ni procedencia.
- No cambiar una ficha `approved` durante una carga rutinaria. Para corregirla, confirmar el alcance solicitado y devolverla primero a `pending` desde el backoffice autenticado.
- Identificar las series y los datos solicitados.
- Distinguir datos objetivos, disponibilidad por territorio y valoraciones subjetivas.
- Si se pide «completar» sin enumerar campos, auditar todas las dimensiones de la matriz de cobertura y cargar solo las que sean aplicables y verificables.
- Separar auditoría y carga: una auditoría completa puede resolverse mediante varios lotes pequeños. Elegir un lote cohesivo, declarar qué queda fuera y no ampliar identidades o relaciones sin revisarlas.
- No ampliar el alcance con entidades o campos que no se hayan pedido.
- Si falta una decisión que cambie el modelo, la carga o el resultado, detenerse y preguntar antes de editar.

### 3. Investigar con fuentes contrastadas

- Priorizar fuentes oficiales de la productora, cadena, plataforma, distribuidora o equipo de la serie.
- Corroborar los datos relevantes con una segunda fuente independiente cuando sea posible, como prensa fiable, entrevistas o bases de datos reconocidas.
- Usar fuentes comunitarias solo para opiniones o como pista de investigación, nunca como único respaldo de un dato objetivo.
- Registrar para cada fuente su título, URL, responsable o medio, fecha de consulta y los campos concretos que respalda.
- No marcar una fuente como `verified` solo porque se haya localizado. Inspeccionar el contenido que respalda el dato; si solo está corroborado por fuentes secundarias, usar `corroborated`.
- Separar claramente los datos confirmados, corroborados, no confirmados y contradictorios.
- No deducir como hecho lo que una fuente no afirma. Mantener como desconocido lo que no pueda verificarse.
- Comprobar de forma específica la disponibilidad actual cuando dependa del país o la plataforma.
- Tratar el tipo de final y su nota como spoilers. Verificar el final en el episodio final, una sinopsis oficial o una fuente secundaria fiable; no inferirlo desde promociones o comentarios aislados.
- Aplicar literalmente la rúbrica compartida de drama, final y advertencias. No clasificar por intuición ni confundir conflicto emocional, género dramático y contenido sensible.

### 4. Evitar duplicados

Antes de crear cualquier entidad:

- Buscar coincidencias por identificador, título, título original, nombres alternativos y relaciones existentes.
- Revisar tanto el esquema como las migraciones de datos ya incorporadas.
- Reutilizar las entidades existentes cuando representen a la misma serie, persona, personaje, empresa, plataforma, colección, etiqueta, advertencia o pareja.
- Seguir la convención de identificadores que ya utilice el repositorio; no crear una nueva sin necesidad.
- No sobrescribir datos existentes ni resolver silenciosamente contradicciones. Documentarlas y pedir una decisión cuando sea necesario.
- Registrar una fuente contradictoria con estado `conflicting` y una nota concreta; guardar un valor solo si otra evidencia suficiente lo sostiene.

### 5. Adaptar los datos al modelo real

- Guardar únicamente datos que tengan representación en el modelo y esquema actuales.
- Respetar la separación entre series, personas, personajes, créditos, parejas ficticias, parejas artísticas, empresas, disponibilidad, estructura narrativa y metadatos de descubrimiento.
- Mantener separados `drama_level`, `ending_type` y las advertencias de contenido. No guardar opiniones o estados personales de visionado en el catálogo objetivo.
- Respetar las claves foráneas, restricciones y reglas de integridad de SQLite.
- Usar el mecanismo de trazabilidad que exista realmente en el repositorio.
- Si un dato solicitado todavía no puede persistirse, explicar la carencia y preguntar antes de modificar el modelo o el esquema.

### 6. Auditar la cobertura

- Separar el estado editorial de la cobertura: `approved` significa que el usuario acepta la ficha actual, no que todas las dimensiones posibles sean aplicables o estén completas.
- Consultar SQLite antes de investigar y producir por serie una lista de campos `confirmados`, `pendientes`, `no aplicables` y `conflictivos`.
- Revisar como mínimo: ficha y fechas; imágenes con fuente; reparto, personajes y parejas; empresas; plataformas por territorio; colecciones; temporadas y episodios; etiquetas; advertencias; guía de drama y final; fuentes y trazabilidad.
- No considerar incompleta una colección, temporada especial, advertencia o relación que no sea aplicable. No convertir la falta de evidencia en un valor negativo como «sin advertencias» o «sin drama».
- Priorizar primero identificadores, relaciones y datos objetivos; clasificar spoilers solo cuando las fuentes permitan aplicar la rúbrica.
- Auditar el vocabulario existente antes de crear IDs compartidos. Normalizar nuevos IDs en kebab-case y no crear variantes semánticas sin decidir primero cuál será la entidad canónica.

### 7. Generar la carga

- Utilizar el mecanismo de carga vigente; no inventar rutas, formatos, comandos ni tecnología.
- Si está disponible `gl-verse importar-series`, leer `docs/catalog-import-format.md` y generar un JSON temporal con las entidades, fuentes y registros de trazabilidad confirmados.
- Incluir solo las secciones necesarias y respetar sus dependencias: entidades reutilizables antes de relaciones; temporadas antes de episodios; fuentes antes de procedencia.
- No guardar el JSON temporal ni la base SQLite en el repositorio.
- Ejecutar primero `gl-verse importar-series <archivo> --dry-run` contra la base de destino.
- Resolver cualquier conflicto de identificadores o posible duplicado; no forzar ni sobrescribir datos.
- Tras una simulación correcta, ejecutar `gl-verse importar-series <archivo>` para guardar la carga cuando la petición autorice incorporarla.
- Repetir la simulación después de la carga y exigir cero inserciones y cero actualizaciones para demostrar idempotencia.
- Si se necesita otra base, indicar explícitamente `--database <ruta>` tanto en la simulación como en la carga real.
- Usar una migración numerada solo cuando sea necesario cambiar el esquema o cargar datos imprescindibles para reconstruir una instalación nueva.

### 8. Probar con GAP

Cuando se use `gap-2022` como piloto:

1. Auditar la ficha existente completa antes de investigar y no recrear entidades ya presentes.
2. Preparar un lote pequeño con los campos nuevos o vacíos que puedan verificarse.
3. Aplicar la rúbrica de drama/final sobre la obra completa y documentar por separado cualquier advertencia.
4. Si se está evaluando la skill, trabajar sobre una copia temporal: ejecutar simulación, importación y segunda simulación sin tocar la base real. Si el usuario autorizó cargar GAP, usar la base real después de una simulación correcta.
5. Comprobar SQLite y la salida de `catalog_payload`; comprobar `GET /api/catalog` y la web cuando se haya autorizado y realizado una carga real.
6. Informar de los campos que sigan pendientes y del motivo. No editar SQLite a mano para eludir un conflicto del importador.

### 9. Probar los cambios

Añadir o actualizar pruebas que cubran, según corresponda:

- la carga de las nuevas entidades;
- la actualización desde la versión anterior;
- la ausencia de duplicados;
- la conservación de datos existentes;
- la integridad de las relaciones;
- el comportamiento ante una segunda inicialización.

Ejecutar las comprobaciones definidas por el repositorio. Actualmente son:

```bash
pytest
ruff check .
```

No declarar una comprobación como superada si no se ha ejecutado.

### 10. Entregar el resultado

- No marcar automáticamente una serie como `approved` tras importarla. Esa decisión corresponde al usuario desde el backoffice autenticado después de revisar la ficha. Una edición objetiva realizada allí debe incluir fuente, conservar su auditoría y devolver la ficha a `pending`.
- Para una importación ordinaria, no crear una rama ni un pull request: resumir las entidades añadidas, las fuentes consultadas y el resultado del importador.
- Si hubo que cambiar código o esquema, trabajar en una rama dedicada y preparar un pull request revisable, en borrador salvo indicación contraria.
- No mezclar refactorizaciones ni cambios funcionales ajenos a la carga.
- Resumir la cobertura antes/después por dimensión y señalar expresamente cualquier dato omitido, no aplicable, dudoso o pendiente de decisión.
