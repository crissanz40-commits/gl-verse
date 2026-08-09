---
name: incorporar-series-gl
description: Investigar e incorporar series GL en GL Verse con datos contrastados, trazabilidad, prevención de duplicados y el importador JSON del proyecto. Usar cuando se pida añadir, completar o actualizar una o varias series, su reparto, personajes, parejas, disponibilidad, episodios u otros datos relacionados; preparar un cambio de código solo si el modelo no permite guardar la información solicitada.
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

Actualmente, GL Verse utiliza `gl-verse importar-series` para ampliar el catálogo y reserva las migraciones SQL para cambios de esquema y datos iniciales. No asumir que seguirá siendo así: comprobarlo en cada ejecución.

### 2. Delimitar la petición

- Identificar las series y los datos solicitados.
- Distinguir datos objetivos, disponibilidad por territorio y valoraciones subjetivas.
- No ampliar el alcance con entidades o campos que no se hayan pedido.
- Si falta una decisión que cambie el modelo, la carga o el resultado, detenerse y preguntar antes de editar.

### 3. Investigar con fuentes contrastadas

- Priorizar fuentes oficiales de la productora, cadena, plataforma, distribuidora o equipo de la serie.
- Corroborar los datos relevantes con una segunda fuente independiente cuando sea posible, como prensa fiable, entrevistas o bases de datos reconocidas.
- Usar fuentes comunitarias solo para opiniones o como pista de investigación, nunca como único respaldo de un dato objetivo.
- Registrar para cada fuente su título, URL, responsable o medio, fecha de consulta y los campos concretos que respalda.
- Separar claramente los datos confirmados, corroborados, no confirmados y contradictorios.
- No deducir como hecho lo que una fuente no afirma. Mantener como desconocido lo que no pueda verificarse.
- Comprobar de forma específica la disponibilidad actual cuando dependa del país o la plataforma.

### 4. Evitar duplicados

Antes de crear cualquier entidad:

- Buscar coincidencias por identificador, título, título original, nombres alternativos y relaciones existentes.
- Revisar tanto el esquema como las migraciones de datos ya incorporadas.
- Reutilizar las entidades existentes cuando representen a la misma serie, persona, personaje, empresa, plataforma o pareja.
- Seguir la convención de identificadores que ya utilice el repositorio; no crear una nueva sin necesidad.
- No sobrescribir datos existentes ni resolver silenciosamente contradicciones. Documentarlas y pedir una decisión cuando sea necesario.

### 5. Adaptar los datos al modelo real

- Guardar únicamente datos que tengan representación en el modelo y esquema actuales.
- Respetar la separación entre series, personas, personajes, créditos, parejas ficticias y parejas artísticas.
- Respetar las claves foráneas, restricciones y reglas de integridad de SQLite.
- Usar el mecanismo de trazabilidad que exista realmente en el repositorio.
- Si un dato solicitado todavía no puede persistirse, explicar la carencia y preguntar antes de modificar el modelo o el esquema.

### 6. Generar la carga

- Utilizar el mecanismo de carga vigente; no inventar rutas, formatos, comandos ni tecnología.
- Si está disponible `gl-verse importar-series`, leer `docs/catalog-import-format.md` y generar un JSON temporal con las entidades, fuentes y registros de trazabilidad confirmados.
- No guardar el JSON temporal ni la base SQLite en el repositorio.
- Ejecutar primero `gl-verse importar-series <archivo> --dry-run` contra la base de destino.
- Resolver cualquier conflicto de identificadores o posible duplicado; no forzar ni sobrescribir datos.
- Tras una simulación correcta, ejecutar `gl-verse importar-series <archivo>` para guardar la carga cuando la petición autorice incorporarla.
- Si se necesita otra base, indicar explícitamente `--database <ruta>` tanto en la simulación como en la carga real.
- Usar una migración numerada solo cuando sea necesario cambiar el esquema o cargar datos imprescindibles para reconstruir una instalación nueva.

### 7. Probar los cambios

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

### 8. Entregar el resultado

- Para una importación ordinaria, no crear una rama ni un pull request: resumir las entidades añadidas, las fuentes consultadas y el resultado del importador.
- Si hubo que cambiar código o esquema, trabajar en una rama dedicada y preparar un pull request revisable, en borrador salvo indicación contraria.
- No mezclar refactorizaciones ni cambios funcionales ajenos a la carga.
- Señalar expresamente cualquier dato omitido, dudoso o pendiente de decisión.
