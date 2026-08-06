# Guía de trabajo del repositorio

## Alcance

Estas instrucciones se aplican a todo el repositorio.

## Convenciones del proyecto

- GL Verse utiliza Python 3.11 o posterior y organiza el código dentro de `src/`.
- Mantén separados los datos objetivos del catálogo y los datos personales de visionado.
- Conserva la distinción entre series, personas, personajes, créditos, parejas ficticias y parejas artísticas.
- Trata `web/` como un prototipo estático hasta que el repositorio incorpore una API de forma explícita.

## Cómo realizar cambios

- Revisa el modelo de dominio, los repositorios, las migraciones y las pruebas existentes antes de modificar el comportamiento.
- Haz cambios pequeños y centrados, respetando la estructura y los nombres actuales.
- Para modificar el esquema de SQLite o cargar datos iniciales, añade la siguiente migración numerada. No reescribas migraciones que ya estén en uso.
- Cuando corresponda, las migraciones deben poder ejecutarse más de una vez sin duplicar datos ni producir errores. Conserva las restricciones de la base de datos y los datos existentes.
- Usa identificadores estables, evita duplicados y registra fuentes comprobables para los datos reales de series GL. No inventes información.
- No subas bases de datos locales, entornos virtuales, archivos generados ni cambios ajenos a la tarea.
- Añade o actualiza pruebas cuando cambie el comportamiento, la persistencia o la forma de cargar datos.

## Comprobaciones

Instala las dependencias de desarrollo con:

```bash
python -m pip install -e ".[dev]"
```

Antes de abrir o actualizar un pull request, ejecuta:

```bash
pytest
ruff check .
```

Si modificas JavaScript, ejecuta también:

```bash
node --check web/app.js
```

## Pull requests

Mantén cada pull request centrado en una sola tarea. Explica las decisiones sobre el modelo o las migraciones, indica las fuentes de datos añadidas y deja constancia de las comprobaciones ejecutadas.
