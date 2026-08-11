# GL Verse

GL Verse será una base de datos conectada del universo de las series GL: producciones, profesionales, personajes, parejas, plataformas y fuentes, con una capa personal para registrar lo que hemos visto y nuestras valoraciones.

## Aplicación web y API

La carpeta `web/` contiene la experiencia frontal responsive. El comando `gl-verse web` sirve esos recursos y expone el catálogo SQLite en `GET /api/catalog`. La interfaz incluye:

- búsqueda instantánea por serie, pareja ficticia o pareja artística;
- filtros por pareja, país, mes y año de estreno;
- orden por fecha de estreno o título;
- lista personal y fichas navegables de series, parejas y actrices;
- trayectoria conjunta de cada pareja a través de sus series;
- trayectoria individual de cada actriz, incluidas participaciones sin pareja;
- espacios de portada e imagen preparados para mostrar su URL y fuente.
- disponibilidad por plataforma y territorio, con modelo de acceso y subtítulos;
- filtro por plataforma alimentado por SQLite.
- revisión editorial por serie, con fichas pendientes o aprobadas persistidas en SQLite.

Para probar el frontal y la API con la base local:

```bash
gl-verse web
```

Después abre `http://127.0.0.1:8000` en el navegador. Puedes elegir otra base, interfaz o puerto:

```bash
gl-verse web --database data/gl_verse.db --host 127.0.0.1 --port 8080
```

`GET /api/health` permite comprobar que el proceso está activo. Las valoraciones personales y las guías de visionado siguen separadas del catálogo objetivo; sus filtros se activarán cuando esas capas estén persistidas.

### Acceso con Google y backoffice

GL Verse usa Google OpenID Connect. La identidad se guarda mediante el identificador estable `sub` de Google y cada cuenta tiene rol `admin` o `viewer`. Los correos incluidos en `GL_VERSE_ADMIN_EMAILS` se promocionan a admin en su primer acceso; cualquier otra cuenta entra como viewer. Un admin ya persistido no se degrada si cambia esa variable.

En Google Cloud crea un cliente OAuth 2.0 de tipo aplicación web y registra exactamente `http://127.0.0.1:8000/api/auth/google/callback` como URI de redirección autorizada. Antes de iniciar la aplicación, configura en PowerShell:

```powershell
$env:GL_VERSE_GOOGLE_CLIENT_ID="tu-client-id.apps.googleusercontent.com"
$env:GL_VERSE_GOOGLE_CLIENT_SECRET="tu-client-secret"
$env:GL_VERSE_GOOGLE_REDIRECT_URI="http://127.0.0.1:8000/api/auth/google/callback"
$env:GL_VERSE_ADMIN_EMAILS="tu-correo@gmail.com"
gl-verse web
```

Abre `http://127.0.0.1:8000` y pulsa «Entrar con Google». Solo un admin verá y podrá usar `http://127.0.0.1:8000/admin.html`; los viewers conservan acceso de lectura al catálogo. GL Verse no almacena contraseñas ni tokens de Google: crea una sesión local de ocho horas. Toda edición objetiva exige una fuente, queda ligada al `sub` del admin en el historial y devuelve la ficha a pendiente antes de poder aprobarla otra vez.

## Migraciones SQLite

La persistencia utiliza migraciones SQL numeradas:

- `001_initial_schema.sql`: tabla e índices de series.
- `002_seed_gap.sql`: primera ficha real, *GAP: The Series*.
- `003_people_characters_credits.sql`: personas, personajes y créditos profesionales.
- `004_cast_images_and_series_pairings.sql`: imágenes con fuente, importancia del reparto y parejas por serie.
- `005_seed_current_catalog.sql`: consolida las seis fichas visibles, sus actrices, personajes y parejas artísticas.
- `006_catalog_import_provenance.sql`: fuentes y comprobaciones utilizadas por el importador de catálogo.
- `007_series_release_date.sql`: fecha completa de estreno para filtrar por mes y año.
- `008_platforms_and_availability.sql`: plataformas y disponibilidad territorial con subtítulos.
- `009_character_pairings.sql`: desacopla las parejas ficticias de las parejas artísticas.
- `010_extended_catalog.sql`: persiste empresas, colecciones, episodios, etiquetas, advertencias y guías de visionado.
- `011_series_review_status.sql`: guarda la aprobación editorial manual de cada ficha sin mezclarla con el estado de emisión.
- `012_admin_backoffice.sql`: introduce la base del backoffice y su historial editorial.
- `013_google_identity_roles.sql`: sustituye las credenciales locales por identidades Google con roles `admin` y `viewer`.

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

La versión 5 lleva a SQLite las fichas que ya aparecen en el prototipo: *GAP*, *The Loyal Pin*, *Pluto*, *23.5*, *The Secret of Us* y *Affair*. La carga reutiliza actrices y parejas compartidas, conserva registros existentes y puede inicializarse de nuevo sin duplicar relaciones.

La versión 8 persiste dónde puede verse cada serie. Una disponibilidad pertenece a una combinación única de serie, plataforma y territorio (`GLOBAL` o código ISO de dos letras); el modelo de acceso y la URL oficial se guardan en esa relación, mientras que los idiomas de subtítulos se normalizan en una tabla hija.

La versión 9 permite registrar una pareja ficticia con sus dos personajes aunque no exista una pareja artística confirmada. El vínculo con `acting_pairs` es opcional y puede añadirse después; SQLite mantiene la pertenencia de ambos personajes a la serie, evita duplicados aunque se invierta su orden y, cuando hay pareja artística, comprueba su correspondencia con el reparto.

## Importar nuevas series sin modificar el código

Las ampliaciones del catálogo se preparan como JSON y se incorporan directamente a SQLite. El formato admite series, personas, personajes, créditos, parejas ficticias, vínculos artísticos opcionales, plataformas, disponibilidad territorial y las fuentes que respaldan cada campo. La especificación completa está en [`docs/catalog-import-format.md`](docs/catalog-import-format.md).

Primero conviene simular la carga completa:

```bash
gl-verse importar-series nueva-serie.json --dry-run
```

Si no aparecen conflictos, se guarda con:

```bash
gl-verse importar-series nueva-serie.json
```

Por defecto se utiliza `data/gl_verse.db`; otra base puede indicarse con `--database ruta.db`. Repetir el mismo archivo no duplica registros. Si un identificador existente contiene información distinta o se detecta otra ficha con el mismo título o nombre, toda la operación se cancela sin guardar cambios parciales.

El JSON utilizado para una carga puede ser temporal: las fuentes y su fecha de comprobación quedan persistidas en SQLite. La base local y los archivos generados no deben subirse al repositorio.

### Primera migración de datos

La ficha de GAP incluye su identificador, títulos, país, año, estado y sinopsis. La inserción es idempotente y respeta cualquier ficha existente con el mismo identificador.

### Por qué SQLite

SQLite es gratuito, no necesita servidor y guarda toda la información en `data/gl_verse.db`. El archivo local no se sube a GitHub; las migraciones necesarias para reconstruirlo sí.

### Guía de visionado

`ViewingGuide` se persiste junto al catálogo y mantiene separadas la intensidad dramática y el tipo de final. La API y el frontal solo activan sus filtros cuando hay datos importados; el modo confort combina **zero drama + final feliz**.

### Fuentes y trazabilidad

`Source` y `ProvenanceRecord` permiten vincular cada dato con su fuente, fecha de comprobación y estado de confianza.

### Revisión editorial

Cada ficha aparece inicialmente como pendiente. Desde su detalle en la web puede marcarse como revisada o reabrirse. Este estado es una decisión editorial local y no reemplaza la trazabilidad del catálogo; la skill de incorporación omite las fichas aprobadas salvo que se solicite expresamente corregirlas.

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

Persistir la capa personal de visionado y valoraciones para activar “Mi lista”, la ordenación por nota y las recomendaciones.
