# GL Verse

GL Verse será una base de datos conectada del universo de las series GL: producciones, profesionales, personajes, parejas, plataformas y fuentes, con una capa personal para registrar lo que hemos visto y nuestras valoraciones.

El proyecto está creciendo deliberadamente poco a poco. Primero construiremos un dominio claro en Python y después elegiremos la persistencia y la interfaz.

## Estado actual

La estructura incluye:

- un paquete Python en `src/gl_verse`;
- modelos conectados para series, personas, personajes y créditos;
- parejas artísticas y parejas ficticias como conceptos independientes;
- separación entre información objetiva y futura información personal;
- un punto de entrada de consola;
- pruebas automatizadas con pytest;
- análisis estático con Ruff;
- validación continua mediante GitHub Actions.

### Relaciones del universo GL

Un `Credit` conecta una `Person` con una `Series`. Cuando su función es de reparto, también puede indicar qué `Character` interpreta.

Las parejas se modelan en dos niveles:

- `ActingPair` une a dos personas reales que trabajan como pareja artística.
- `CharacterPairing` une a dos personajes dentro de una serie.
- `PairingPortrayal` conecta ambas relaciones sin confundirlas.

Así, FreenBecky es una pareja artística, Sam–Mon es una pareja ficticia y `PairingPortrayal` indica que FreenBecky interpreta a Sam–Mon en *GAP*.

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

Añadir productoras, plataformas y disponibilidad para empezar a describir dónde nace y dónde puede verse cada serie.
