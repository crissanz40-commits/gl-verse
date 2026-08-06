# GL Verse

GL Verse será una base de datos conectada del universo de las series GL: producciones, profesionales, personajes, parejas, plataformas y fuentes, con una capa personal para registrar lo que hemos visto y nuestras valoraciones.

## Prototipo web

La carpeta `web/` contiene una primera experiencia frontal responsive para explorar el universo GL. Incluye:

- búsqueda instantánea por serie, pareja ficticia o pareja artística;
- selección de plataformas;
- filtros por drama, tipo de final, pareja y país;
- modo confort para encontrar títulos **zero dramas + final feliz**;
- orden por popularidad, química, estreno o nivel de drama;
- lista personal y fichas emergentes de las parejas.

Los datos de esta primera versión son demostrativos. Más adelante la interfaz consumirá la información validada de SQLite.

Para probarla localmente sin instalar dependencias adicionales:

```bash
python -m http.server 8000 --directory web
```

Después abre `http://localhost:8000` en el navegador.

## Migraciones SQLite

La persistencia utiliza migraciones SQL numeradas:

- `001_initial_schema.sql`: tabla e índices de series.
- `002_seed_gap.sql`: primera ficha real, *GAP: The Series*.
- `003_people_characters_credits.sql`: personas, personajes y créditos profesionales.
- `004_cast_images_and_series_pairings.sql`: imágenes con fuente, importancia del reparto y parejas por serie.

Una base nueva ejecuta todas las migraciones en orden. Una base existente aplica únicamente las versiones pendientes.

### Integridad relacional

La versión 3 garantiza desde SQLite que:

- cada personaje pertenece a una serie existente;
- cada crédito enlaza una serie y una persona existentes;
- solo los créditos de reparto pueden señalar un personaje;
- el personaje de un crédito pertenece a esa misma serie;
- un mismo crédito no puede duplicarse;
- al eliminar una serie se eliminan sus personajes y créditos relacionados.

Esto impide combinaciones incoherentes aunque los datos se introduzcan fuera de la aplicación.

La versión 4 añade el modelo necesario para navegar por actrices y parejas:

- cada portada o imagen guarda tanto su URL como la URL de su fuente;
- una participación de reparto puede ser protagonista, secundaria o invitada;
- una actriz puede participar en una serie sin formar pareja;
- una pareja artística une dos actrices sin depender de una serie concreta;
- `series_pairings` registra cada trabajo compartido, sus personajes y si la pareja es principal o secundaria;
- la trayectoria conjunta de una pareja se obtiene recorriendo sus participaciones en distintas series;
- SQLite impide duplicar una pareja invirtiendo el orden de sus integrantes y comprueba que sus personajes coincidan con el reparto real.

### Primera migración de datos

La ficha de GAP incluye su identificador, títulos, país, año, estado y sinopsis. La inserción es idempotente y respeta cualquier ficha existente con el mismo identificador.

### Por qué SQLite

SQLite es gratuito, no necesita servidor y guarda toda la información en `data/gl_verse.db`. El archivo local no se sube a GitHub; las migraciones necesarias para reconstruirlo sí.

### Guía de visionado

`ViewingGuide` permite aplicar nuestro filtro de confort: **zero drama + final feliz**.

### Fuentes y trazabilidad

`Source` y `ProvenanceRecord` permiten vincular cada dato con su fuente, fecha de comprobación y estado de confianza.

## Preparación del entorno

Necesitas Python 3.11 o posterior.

```bash
python -m venv .venv
```

Activa el entorno virtual e instala el proyecto:

```bash
# Windows
.venv\Scripts\activate

# macOS o Linux
source .venv/bin/activate

python -m pip install -e ".[dev]"
```

## Ejecutar las comprobaciones

```bash
pytest
ruff check .
```

## Próximo paso

Conectar el prototipo web con una API de lectura basada en SQLite y sustituir los datos de demostración por fichas trazables.
