# GL Verse

GL Verse será una base de datos conectada del universo de las series GL: producciones, profesionales, personajes, parejas, plataformas y fuentes, con una capa personal para registrar lo que hemos visto y nuestras valoraciones.

El proyecto está creciendo deliberadamente poco a poco. Primero construiremos un dominio claro en Python y después elegiremos la persistencia y la interfaz.

## Estado actual

La estructura incluye:

- un paquete Python en `src/gl_verse`;
- modelos conectados para series, personas, personajes y créditos;
- separación entre información objetiva y futura información personal;
- un punto de entrada de consola;
- pruebas automatizadas con pytest;
- análisis estático con Ruff;
- validación continua mediante GitHub Actions.

### Primeras relaciones

Un `Credit` conecta una `Person` con una `Series`. Cuando su función es de reparto, también puede indicar qué `Character` interpreta.

De esta forma, Freen es una persona, Sam es un personaje y su participación en *GAP* es el crédito que relaciona las tres entidades.

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

Modelar por separado las parejas artísticas formadas por personas y las parejas ficticias formadas por personajes.
