# GL Verse

GL Verse será una base de datos conectada del universo de las series GL: producciones, profesionales, personajes, parejas, plataformas y fuentes, con una capa personal para registrar lo que hemos visto y nuestras valoraciones.

El proyecto está creciendo deliberadamente poco a poco. Primero construiremos un dominio claro en Python y después elegiremos la persistencia y la interfaz.

## Estado actual

La estructura incluye:

- series, personas, personajes, créditos y parejas;
- productoras, plataformas y disponibilidad territorial;
- colecciones, temporadas y episodios;
- géneros, tropos, advertencias, nivel de drama y tipo de final;
- fuentes vinculadas a datos concretos;
- fecha y estado de verificación;
- separación entre información objetiva y futura información personal;
- pruebas automatizadas y validación continua.

### Guía de visionado

`ViewingGuide` separa cuánto drama contiene una historia de cómo termina la pareja principal. La propiedad `is_zero_drama_with_happy_ending` permite aplicar directamente nuestro filtro de confort: **zero drama + final feliz**.

La futura interfaz tratará el tipo y la explicación del final como información con spoiler y podrá mantenerlos ocultos hasta que la usuaria decida mostrarlos.

### Fuentes y trazabilidad

- `Source` representa la página o publicación consultada.
- `ProvenanceRecord` conecta esa fuente con una entidad y un campo concreto.
- `VerificationStatus` distingue datos verificados, corroborados, no verificados o con fuentes contradictorias.
- `needs_review` detecta información que lleva demasiado tiempo sin comprobarse.

Una fuente no respalda automáticamente toda una ficha. Puede confirmar únicamente un dato, como el número de episodios, el reparto o la disponibilidad en España.

### Relaciones principales

- `Credit` conecta personas, personajes y series.
- `ActingPair`, `CharacterPairing` y `PairingPortrayal` distinguen parejas reales y ficticias.
- `Company`, `Platform` y `Availability` describen industria y visionado.
- `SeriesCollection`, `Season` y `Episode` describen la estructura narrativa.
- `Tag`, `ContentWarning` y `ViewingGuide` ayudan a elegir una serie.
- `Source` y `ProvenanceRecord` explican de dónde sale cada dato.

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

Convertir el modelo en una base de datos SQLite real para empezar a guardar y consultar información.
