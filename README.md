# GL Verse

GL Verse será una base de datos conectada del universo de las series GL: producciones, profesionales, personajes, parejas, plataformas y fuentes, con una capa personal para registrar lo que hemos visto y nuestras valoraciones.

## Estado actual

El dominio ya representa series, personas, personajes, parejas, industria, disponibilidad, estructura narrativa, guía de visionado y procedencia de los datos.

La primera persistencia real utiliza SQLite e incluye:

- creación automática de `data/gl_verse.db`;
- esquema versionado;
- tabla e índices para series;
- guardado, recuperación y listado mediante `SeriesRepository`;
- integridad para identificadores duplicados;
- pruebas con bases de datos temporales en memoria.

### Por qué SQLite

SQLite es gratuito, no necesita servidor y guarda toda la información en un archivo. El archivo local de datos no se sube a GitHub. El esquema y el código para reconstruirlo sí forman parte del repositorio.

Esta primera versión persiste únicamente las series. Las demás entidades se incorporarán mediante nuevas versiones del esquema, manteniendo los cambios pequeños y comprobables.

### Guía de visionado

`ViewingGuide` separa cuánto drama contiene una historia de cómo termina la pareja principal. La propiedad `is_zero_drama_with_happy_ending` permite aplicar nuestro filtro de confort: **zero drama + final feliz**.

### Fuentes y trazabilidad

`Source` y `ProvenanceRecord` permiten vincular cada dato con su fuente, fecha de comprobación y estado de confianza.

## Preparación del entorno

Necesitas Python 3.11 o posterior.

```bash
python -m venv .venv
```

Activa el entorno virtual:

```bash
# Windows
.venv\Scripts\activate

# macOS o Linux
source .venv/bin/activate
```

Instala el proyecto con sus herramientas de desarrollo:

```bash
python -m pip install -e ".[dev]"
```

## Ejecutar GL Verse

```bash
gl-verse
```

## Ejecutar las comprobaciones

```bash
pytest
ruff check .
```

## Próximo paso

Añadir una migración para guardar personas, personajes y créditos en SQLite.
