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
- separación entre información objetiva y futura información personal;
- pruebas automatizadas y validación continua.

### Relaciones del universo GL

Un `Credit` conecta una `Person` con una `Series`. Cuando su función es de reparto, también puede indicar qué `Character` interpreta.

Las parejas se modelan en dos niveles:

- `ActingPair` une a dos personas reales que trabajan como pareja artística.
- `CharacterPairing` une a dos personajes dentro de una serie.
- `PairingPortrayal` conecta ambas relaciones sin confundirlas.

Así, FreenBecky es una pareja artística, Sam–Mon es una pareja ficticia y `PairingPortrayal` indica que FreenBecky interpreta a Sam–Mon en *GAP*.

La industria y la disponibilidad se modelan por separado:

- `Company` representa una empresa.
- `SeriesCompany` indica si produce, emite o distribuye una serie.
- `Platform` representa un servicio donde puede verse.
- `Availability` registra el territorio, modalidad de acceso, enlace oficial y subtítulos.

La estructura narrativa diferencia tres niveles:

- `SeriesCollection` agrupa producciones relacionadas, como una antología.
- `Season` representa una temporada concreta de una serie.
- `Episode` pertenece a una temporada y puede ser regular o especial.

Así, *Four Elements* puede agrupar varias series independientes sin tratarlas artificialmente como temporadas.

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

Añadir géneros, tropos, advertencias de contenido y tipo de final para mejorar el descubrimiento de series.
