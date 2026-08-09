# Formato de importación del catálogo

El documento debe ser JSON UTF-8, declarar `format_version: 1` y utilizar únicamente las secciones necesarias. Los identificadores son estables: una ejecución posterior con el mismo identificador debe contener exactamente los mismos datos.

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
      "status": "announced",
      "synopsis": "Sinopsis contrastada",
      "cover_image_url": "https://example.com/cover.jpg",
      "cover_image_source_url": "https://example.com/official-page"
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
| `series` | `id`, `title`, `country`, `release_year`, `status` | `original_title`, `synopsis`, `cover_image_url`, `cover_image_source_url` |
| `people` | `id`, `name` | `stage_name`, `nationality`, `image_url`, `image_source_url` |
| `characters` | `id`, `name`, `series_id` | — |
| `credits` | `series_id`, `person_id`, `role` | `character_id`, `cast_importance` |
| `acting_pairs` | `id`, `name`, `person_ids` | `active_since`, `image_url`, `image_source_url` |
| `series_pairings` | `id`, `series_id`, `acting_pair_id`, `character_ids`, `role` | — |
| `sources` | `id`, `title`, `url`, `source_type` | `publisher`, `published_on` |
| `provenance` | `source_id`, `entity_type`, `entity_id`, `field_name`, `checked_on`, `status` | `note` |

`person_ids` y `character_ids` contienen exactamente dos identificadores. Las imágenes siempre deben incluir tanto su URL directa como la página que acredita su procedencia.

## Valores permitidos

- `series.status`: `announced`, `airing`, `completed`, `cancelled`.
- `credits.role`: `cast`, `director`, `writer`, `producer`.
- `credits.cast_importance`: `lead`, `supporting`, `guest`.
- `series_pairings.role`: `main`, `supporting`.
- `sources.source_type`: `official`, `platform`, `press`, `interview`, `database`, `community`.
- `provenance.status`: `verified`, `corroborated`, `unverified`, `conflicting`.
- Fechas: formato ISO `YYYY-MM-DD`.

Antes de guardar una carga real, ejecutar siempre:

```bash
gl-verse importar-series archivo.json --dry-run
```
