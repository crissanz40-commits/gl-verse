# GL Verse

GL Verse será un catálogo personal de series GL para descubrir historias, registrar lo que hemos visto y guardar nuestras propias valoraciones.

El proyecto está empezando deliberadamente pequeño: primero construiremos una base clara en Python y después decidiremos juntas qué funcionalidades añadir.

## Estado actual

La primera estructura incluye:

- un paquete Python en `src/gl_verse`;
- un modelo inicial para representar series;
- un punto de entrada de consola;
- pruebas automatizadas con pytest;
- configuración de formato y análisis con Ruff.

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

Definir qué información queremos guardar de cada serie antes de elegir una base de datos o construir la interfaz.
