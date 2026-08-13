# Formato de importación del catálogo

El documento debe ser JSON UTF-8, declarar `format_version: 1` y utilizar únicamente las secciones necesarias. Los identificadores son estables. Una ejecución posterior puede completar campos opcionales que todavía estén vacíos en una serie, persona, pareja artística o plataforma, pero nunca sustituir un valor ya guardado. Omitir un campo opcional conserva su valor actual; en una disponibilidad existente, los idiomas de subtítulos se amplían de forma aditiva.

```json
{
  "format_version": 1,
  "series": [
    {
      "id": "identificador-serie-2026",
      "title": "Título internacional",
      "original_title": "Título original",
      "country": "Tailandia",
      "release_year": 2026,
      "release_date": "2026-03-09",
      "status": "announced",
      "synopsis": "Sinopsis contrastada",
      "cover_image_url": "https://example.com/cover.jpg",
      "cover_image_source_url": "https://example.com/official-page"
    }
  ],
  "series_image_replacements": [
    {
      "series_id": "identificador-serie-2026",
      "expected": {
        "url": "https://images.example.com/cover-anterior.jpg",
        "source_url": "https://example.com/fuente-anterior"
      },
      "replacement": {
        "url": "https://images.example.com/cover-nueva.jpg",
        "source_url": "https://example.com/fuente-nueva"
      }
    }
  ],
  "platforms": [
    {
      "id": "example-stream",
      "name": "Example Stream",
      "website_url": "https://stream.example.com"
    }
  ],
  "availability": [
    {
      "series_id": "identificador-serie-2026",
      "platform_id": "example-stream",
      "territory": "ES",
      "access_model": "subscription",
      "official_url": "https://stream.example.com/serie-2026",
      "subtitle_languages": ["es", "en"]
    }
  ],
  "companies": [
    {
      "id": "example-studio",
      "name": "Example Studio",
      "country": "Tailandia",
      "website_url": "https://studio.example.com"
    }
  ],
  "series_companies": [
    {
      "series_id": "identificador-serie-2026",
      "company_id": "example-studio",
      "role": "producer"
    }
  ],
  "viewing_guides": [
    {
      "series_id": "identificador-serie-2026",
      "drama_level": "light",
      "ending_type": "happy_for_now",
      "ending_note": "Nota breve respaldada por la fuente."
    }
  ],
  "sources": [
    {
      "id": "serie-2026-official",
      "title": "Official series page",
      "url": "https://example.com/official-page",
      "source_type": "official",
      "publisher": "Productora"
    }
  ],
  "provenance": [
    {
      "source_id": "serie-2026-official",
      "entity_type": "series",
      "entity_id": "identificador-serie-2026",
      "field_name": "title",
      "checked_on": "2026-08-10",
      "status": "verified"
    }
  ]
}
```

## Secciones

| Sección | Campos obligatorios | Campos opcionales |
| --- | --- | --- |
| `series` | `id`, `title`, `country`, `release_year`, `status` | `release_date`, `original_title`, `synopsis`, `cover_image_url`, `cover_image_source_url` |
| `series_image_replacements` | `series_id`, `expected`, `replacement` | — |
| `people` | `id`, `name` | `stage_name`, `nationality`, `image_url`, `image_source_url` |
| `characters` | `id`, `name`, `series_id` | — |
| `credits` | `series_id`, `person_id`, `role` | `character_id`, `cast_importance` |
| `acting_pairs` | `id`, `name`, `person_ids` | `active_since`, `image_url`, `image_source_url` |
| `series_pairings` | `id`, `series_id`, `character_ids`, `role` | `acting_pair_id` |
| `platforms` | `id`, `name` | `website_url` |
| `availability` | `series_id`, `platform_id`, `territory`, `access_model`, `official_url` | `subtitle_languages` |
| `companies` | `id`, `name` | `country`, `website_url` |
| `series_companies` | `series_id`, `company_id`, `role` | — |
| `collections` | `id`, `title`, `kind` | `description` |
| `collection_entries` | `collection_id`, `series_id`, `position` | — |
| `seasons` | `id`, `series_id`, `number` | `title`, `release_year` |
| `episodes` | `id`, `season_id`, `number` | `title`, `kind`, `air_date`, `duration_minutes` |
| `tags` | `id`, `name`, `category` | — |
| `series_tags` | `series_id`, `tag_id` | — |
| `content_warnings` | `id`, `name` | `description` |
| `series_content_warnings` | `series_id`, `warning_id`, `severity` | — |
| `viewing_guides` | `series_id`, `drama_level`, `ending_type` | `ending_note` |
| `sources` | `id`, `title`, `url`, `source_type` | `publisher`, `published_on` |
| `provenance` | `source_id`, `entity_type`, `entity_id`, `field_name`, `checked_on`, `status` | `note` |

`person_ids` y `character_ids` contienen exactamente dos identificadores. Las imágenes siempre deben incluir tanto su URL directa como la página que acredita su procedencia.

`series_image_replacements` es la única operación que sustituye una portada ya guardada. Tanto `expected` como `replacement` requieren `url` y `source_url`. La importación solo actualiza si las dos URLs actuales coinciden con `expected`; si ya coinciden con `replacement`, la operación es idempotente; cualquier otro estado se considera conflicto y revierte todo el lote. Debe conservarse la procedencia anterior y añadirse una fuente para la nueva imagen.

`series_pairings` representa ante todo la pareja ficticia de dos personajes dentro de una serie. `acting_pair_id` solo se incluye cuando también existe una pareja artística verificada entre sus intérpretes. Los documentos anteriores que ya lo incluyen siguen siendo compatibles. Una carga posterior puede completar este vínculo si estaba vacío, pero no sustituir uno ya guardado. La combinación de serie y personajes es única con independencia del orden de `character_ids`.

Cada disponibilidad es única por serie, plataforma y territorio. `territory` usa `GLOBAL` o un código ISO de país de dos letras en mayúsculas, por ejemplo `ES`, `TH` o `US`. Una carga posterior puede añadir idiomas de subtítulos, pero cambiar el modelo de acceso o la URL oficial de una disponibilidad existente se considera un conflicto. Para su trazabilidad, `provenance.entity_id` se forma como `series_id:platform_id:territory`.

Las colecciones ordenan sus series con `position`; las temporadas son únicas por serie y número, y los episodios por temporada, número y tipo. Los campos descriptivos opcionales pueden completarse después si siguen vacíos, pero una clasificación o relación existente nunca se sustituye silenciosamente.

`viewing_guides` mantiene separadas dos dimensiones: `drama_level` describe la intensidad dramática general y `ending_type` el resultado emocional del final de la pareja principal. `ending_note` aporta contexto sin reemplazar ninguna de las dos clasificaciones. No debe usarse para datos personales de visionado.

El estado editorial `pending`/`approved` no forma parte del JSON de catálogo. Se gestiona desde la ficha web para que una importación de datos objetivos no pueda aprobar una serie en nombre del usuario.

Los identificadores de trazabilidad de las relaciones se forman así:

- `series_company`: `series_id:company_id:role`.
- `collection_entry`: `collection_id:series_id`.
- `series_tag`: `series_id:tag_id`.
- `series_content_warning`: `series_id:warning_id`.
- `viewing_guide`: el propio `series_id`.

## Valores permitidos

- `series.status`: `announced`, `airing`, `completed`, `cancelled`.
- `credits.role`: `cast`, `director`, `writer`, `producer`.
- `credits.cast_importance`: `lead`, `supporting`, `guest`.
- `series_pairings.role`: `main`, `supporting`.
- `availability.access_model`: `free`, `subscription`, `rental`, `purchase`.
- `series_companies.role`: `producer`, `broadcaster`, `distributor`.
- `collections.kind`: `anthology`, `franchise`, `shared_universe`.
- `episodes.kind`: `regular`, `special` (si se omite, se usa `regular`).
- `tags.category`: `genre`, `trope`, `theme`, `tone`.
- `series_content_warnings.severity`: `low`, `medium`, `high`.
- `viewing_guides.drama_level`: `zero_drama`, `light`, `moderate`, `high`.
- `viewing_guides.ending_type`: `happy_ever_after`, `happy_for_now`, `bittersweet`, `open`, `sad`, `tragic`, `unknown`.
- `sources.source_type`: `official`, `platform`, `press`, `interview`, `database`, `community`.
- `provenance.status`: `verified`, `corroborated`, `unverified`, `conflicting`.
- Fechas: formato ISO `YYYY-MM-DD`.

Antes de guardar una carga real, ejecutar siempre:

```bash
gl-verse importar-series archivo.json --dry-run
```
