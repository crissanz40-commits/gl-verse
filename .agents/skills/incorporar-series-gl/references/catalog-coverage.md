# Cobertura y clasificación del catálogo

Leer esta referencia al completar una ficha, auditar huecos o investigar metadatos de descubrimiento.

## Matriz de cobertura

Clasificar cada dimensión como `confirmada`, `pendiente`, `no aplicable` o `conflictiva`. No rellenar un campo solo para eliminar un hueco.

| Dimensión | Comprobar |
| --- | --- |
| Serie | título, título original, país, año, fecha exacta, estado, sinopsis |
| Imágenes | portada directa y página fuente; imágenes de personas y parejas cuando se soliciten |
| Reparto | personas, nombres artísticos, nacionalidad, personajes, créditos e importancia |
| Parejas | pareja ficticia por personajes; pareja artística solo si está confirmada |
| Industria | empresas y rol `producer`, `broadcaster` o `distributor` |
| Disponibilidad | plataforma, territorio, modelo de acceso, URL oficial y subtítulos actuales |
| Estructura | colección aplicable, orden, temporadas, episodios regulares/especiales, fechas y duración |
| Descubrimiento | géneros, tropos, temas y tonos reutilizables |
| Seguridad | advertencias de contenido y severidad |
| Guía | nivel de drama, tipo de final y nota breve de spoiler |
| Evidencia | fuentes, fecha de consulta, estado y procedencia de cada dato relevante |

Antes de crear empresas, colecciones, plataformas, etiquetas o advertencias, buscar por ID, nombre y variantes. Reutilizar vocabulario existente; no crear sinónimos como entidades distintas.

Una auditoría completa no obliga a cargar todo de una vez. Priorizar un lote cohesivo en este orden:

1. Identidad, fechas y relaciones estructurales.
2. Empresas, disponibilidad y episodios verificables.
3. Etiquetas, advertencias y guía con fuentes suficientes.
4. Enriquecimientos opcionales como títulos de episodios, duración e imágenes.

Declarar siempre lo que se difiere. No ampliar reparto secundario o identidades durante un piloto si no se han auditado con el mismo rigor.

## Trazabilidad mínima

- Añadir procedencia para cada entidad o relación nueva y para cada campo material que se complete o clasifique.
- Exigir trazabilidad específica para imágenes, disponibilidad, roles de empresa, pertenencia a colecciones, etiquetas, advertencias y guía de drama/final.
- Una misma fuente puede respaldar varios campos mediante registros separados.
- No inventar procedencia de relaciones que el `EntityType` actual no admita. Señalar la limitación; si el usuario necesita resolverla, proponer un cambio de esquema/importador separado.
- Si una fuente discrepa, conservar su URL con estado `conflicting` y explicar la discrepancia. No usar el valor conflictivo salvo que otra evidencia lo resuelva.

## Escala de drama

Clasificar la intensidad del conflicto emocional de la pareja principal a lo largo de la obra canónica completa. No puntuar la calidad, el género comercial ni una escena sensible aislada. Registrar esa escena también como advertencia cuando corresponda.

| Valor | Nivel | Criterio |
| --- | --- | --- |
| `zero_drama` | 0 · Sin drama | Relación estable; conflictos mínimos, sin ruptura ni separación significativa. |
| `light` | 1 · Ligero | La experiencia dominante es romántica o amable; hay celos, presión o malentendidos puntuales, pero el conflicto ocupa poco tiempo y no deja sufrimiento sostenido. |
| `moderate` | 2 · Moderado | Existe al menos un arco relevante de presión, ruptura, secretos o separación durante varios episodios, pero no domina la mayor parte de la serie. |
| `high` | 3 · Alto | El sufrimiento o conflicto grave es sostenido, recurrente y constituye uno de los motores principales durante gran parte de la serie. |

Reglas:

- Evaluar la experiencia dominante de la pareja principal durante el arco completo, no el momento de máxima tensión.
- Ponderar duración, recurrencia y severidad. Un pico intenso concentrado al final puede justificar `moderate`, pero no basta por sí solo para `high`.
- Reservar `high` para historias donde el conflicto grave ocupa una parte amplia del metraje o reaparece en varios arcos importantes. Una ruptura, salto temporal o antagonista familiar no lo determina automáticamente.
- Una advertencia grave no eleva automáticamente el drama si no estructura el arco emocional.
- Ante duda entre dos niveles, comparar qué tono y dinámica ocupan la mayoría de episodios. No subir de nivel únicamente para hacer conservador el filtro; documentar la decisión y usar las advertencias para señalar riesgos concretos.
- Si la evidencia no permite clasificar, omitir `viewing_guides`; no adivinar.
- El modo confort acordado corresponde a niveles 0–1 con `happy_ever_after` o `happy_for_now`. Tratar esta regla como política de producto separada de la clasificación.
- Verificar la implementación vigente antes de afirmar que el modo confort aplica esa política. Si el código usa otra regla, informar de la discrepancia y no cambiarlo durante una carga de datos sin autorización.

### Ancla de calibración

Clasificar `gap-2022` como `moderate` (nivel 2): la presión familiar, el chantaje y la separación son relevantes, pero están concentrados principalmente en el tramo final; el romance y la comedia ocupan gran parte de la serie. Su boda corresponde por separado a `happy_ever_after`. No clasificarla como `high` por tomar únicamente los episodios de mayor tensión.

## Tipo de final

Clasificar el resultado de la pareja principal. No usar el estado general de otros personajes.

| Valor | Criterio |
| --- | --- |
| `happy_ever_after` | Terminan juntas y existe compromiso o futuro estable explícito. |
| `happy_for_now` | Terminan juntas o reconciliadas, pero el futuro permanece parcialmente incierto. |
| `bittersweet` | Hay un resultado positivo parcial acompañado de una pérdida o coste irreversible importante. |
| `open` | El estado o futuro de la relación queda deliberadamente sin resolver. |
| `sad` | No terminan juntas y el desenlace no alcanza el carácter catastrófico de `tragic`. |
| `tragic` | Muerte u otro desenlace irreversible especialmente grave impide la relación. |
| `unknown` | La serie sigue en emisión o el final todavía no se ha podido comprobar. |

- Verificar series completadas con el episodio final, una sinopsis oficial o una fuente secundaria fiable que describa el desenlace.
- No usar promociones, clips parciales ni comentarios comunitarios como única prueba.
- Mantener `ending_note` breve, factual y marcada como spoiler en cualquier presentación. No narrar todo el final.
- Usar `unknown` cuando la guía de drama sí está respaldada pero el desenlace aún no existe o no está confirmado; omitir la guía completa si tampoco puede justificarse el drama.

## Advertencias de contenido

Las advertencias describen contenido sensible, no intensidad romántica. Reutilizar IDs estables y aplicar severidad de forma conservadora:

| Valor | Criterio |
| --- | --- |
| `low` | Presencia breve, implícita o no gráfica. |
| `medium` | Presencia explícita o recurrente con impacto narrativo relevante. |
| `high` | Contenido gráfico, sostenido o central con impacto potencialmente severo. |

No registrar «sin advertencias» por ausencia de menciones. Una advertencia requiere evidencia sobre la obra, preferiblemente una guía oficial/plataforma o la comprobación directa de episodios; corroborar con fuentes fiables cuando sea posible.

## Etiquetas

- `genre`: género narrativo, por ejemplo romance o comedia.
- `trope`: patrón narrativo, por ejemplo friends-to-lovers.
- `theme`: tema tratado, por ejemplo identidad o familia.
- `tone`: tono sostenido, por ejemplo cálido o melancólico.

No usar etiquetas para duplicar nivel de drama, final, advertencias, país, estado o plataforma.

Usar IDs ingleses en kebab-case y nombres visibles en español cuando proceda. Buscar primero el vocabulario ya guardado. Preferir una etiqueta canónica reutilizable frente a variantes como `workplace`, `office-romance` y `workplace-romance` sin una decisión explícita.

## Relaciones dudosas

- `acting_pairs.active_since`: omitir salvo que una fuente y la convención vigente definan una fecha de inicio pública para la pareja artística. No asumir automáticamente la fecha de estreno de su primera serie.
- Colecciones: crear una relación solo con evidencia de antología, franquicia o universo compartido. Compartir novela, autora, título parecido o personajes reinterpretados no demuestra continuidad; una obra escénica tampoco convierte por sí sola dos series en colección.
- Episodios: no inventar títulos ni duraciones. Número, tipo y fecha pueden cargarse de forma independiente si están verificados.

## Piloto GAP

Usar `gap-2022` como primera prueba de la skill actualizada. El piloto debe:

1. Auditar todos los registros existentes asociados a GAP.
2. Investigar únicamente dimensiones pendientes o incompletas.
3. Reutilizar personas, personajes, FreenBecky, plataformas y fuentes existentes.
4. Cargar un lote temporal mediante el importador, con trazabilidad por campo o relación.
5. Demostrar simulación correcta, importación real, segunda simulación sin cambios y lectura desde API/web.
6. Dejar por escrito cualquier omisión. Una portada existente no se sustituye hasta que el importador disponga de una operación explícita y segura de reemplazo.
