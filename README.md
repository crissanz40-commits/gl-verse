# GL Verse

GL Verse será una base de datos conectada del universo de las series GL: producciones, profesionales, personajes, parejas, plataformas y fuentes, con una capa personal para registrar lo que hemos visto y nuestras valoraciones.

## Estado actual

El dominio representa series, personas, personajes, parejas, industria, disponibilidad, estructura narrativa, guía de visionado y procedencia de los datos.

La persistencia utiliza SQLite y migraciones SQL numeradas:

- `001_initial_schema.sql` crea la tabla e índices de series.
- `002_seed_gap.sql` añade la primera ficha real: *GAP: The Series*.

Una base nueva ejecuta todas las migraciones en orden. Una base existente ejecuta únicamente las versiones pendientes.

### Primera migración de datos

La migración de GAP guarda:

- identificador estable `gap-2022`;
- título internacional y título original tailandés;
- país y año de estreno;
- estado finalizado;
- una sinopsis breve.

La inserción es idempotente: puede inicializarse la base varias veces sin duplicar GAP. Si ya existe una ficha con ese identificador, la migración respeta sus datos en lugar de sobrescribirlos.

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

Crear la migración estructural para personas, personajes y créditos y completar después la ficha relacional de GAP.
