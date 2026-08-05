# GL Verse

GL Verse será una base de datos conectada del universo de las series GL: producciones, profesionales, personajes, parejas, plataformas y fuentes, con una capa personal para registrar lo que hemos visto y nuestras valoraciones.

El proyecto está creciendo deliberadamente poco a poco. Primero construiremos un dominio claro en Python y después elegiremos la persistencia y la interfaz.

## Estado actual

La estructura incluye:

- modelos conectados para series, personas, personajes y créditos;
- parejas artísticas y parejas ficticias como conceptos independientes;
- productoras, distribuidoras, cadenas y plataformas;
- disponibilidad por territorio, modalidad de acceso y subtítulos;
- colecciones, temporadas, episodios regulares y especiales;
- géneros, tropos, temas, tonos y advertencias de contenido;
- nivel de drama y tipo de final;
- separación entre información objetiva y futura información personal;
- pruebas automatizadas y validación continua.

### Guía de visionado

`ViewingGuide` separa dos preguntas que no siempre tienen la misma respuesta:

- `DramaLevel`: cuánto drama contiene el recorrido.
- `EndingType`: cómo termina la pareja principal.

Los finales distinguen entre:

- `HAPPY_EVER_AFTER`: felices para siempre;
- `HAPPY_FOR_NOW`: felices por ahora;
- agridulce, abierto, triste, trágico o todavía desconocido.

La propiedad `is_zero_drama_with_happy_ending` permite aplicar directamente nuestro filtro de confort: **zero drama + final feliz**.

La futura interfaz tratará el tipo y la explicación del final como información con spoiler y podrá mantenerlos ocultos hasta que la usuaria decida mostrarlos.

### Relaciones principales

- `Credit` conecta personas, personajes y series.
- `ActingPair`, `CharacterPairing` y `PairingPortrayal` distinguen las parejas reales y ficticias.
- `Company`, `Platform` y `Availability` describen industria y visionado.
- `SeriesCollection`, `Season` y `Episode` describen la estructura narrativa.
- `Tag` y `ContentWarning` ayudan a descubrir una serie adecuada para cada momento.

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

Añadir fuentes y procedencia para saber de dónde sale cada dato y cuándo fue verificado.
