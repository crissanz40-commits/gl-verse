# Repository guidance

## Scope

These instructions apply to the entire repository.

## Project conventions

- GL Verse targets Python 3.11 or later and uses the `src/` layout.
- Keep objective catalogue data separate from personal viewing data.
- Preserve the distinction between series, people, characters, credits, fictional pairings, and artistic pairings.
- Treat `web/` as a static prototype until the repository introduces an API explicitly.

## Changes

- Inspect the existing domain model, repositories, migrations, and tests before changing behavior.
- Prefer small, focused changes that follow the current structure and naming.
- For SQLite schema or seed changes, add the next numbered migration. Do not rewrite migrations already in use.
- Keep migrations idempotent where appropriate and preserve database constraints and existing data.
- Use stable identifiers, avoid duplicates, and record traceable sources for real GL data. Do not invent facts.
- Do not commit local databases, virtual environments, generated files, or unrelated changes.
- Add or update tests whenever behavior, persistence, or data-loading rules change.

## Validation

Install development dependencies with:

```bash
python -m pip install -e ".[dev]"
```

Before opening or updating a pull request, run:

```bash
pytest
ruff check .
```

For JavaScript changes, also run:

```bash
node --check web/app.js
```

## Pull requests

Keep each pull request focused. Explain model or migration decisions, identify any data sources added, and report the checks executed.
