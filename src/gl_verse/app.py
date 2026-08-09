"""Punto de entrada de GL Verse."""

import argparse
import sqlite3
from contextlib import closing
from pathlib import Path

from gl_verse.catalog_import import CatalogImportError, import_catalog, load_catalog
from gl_verse.database import connect_database


def welcome_message() -> str:
    """Devuelve el mensaje inicial de la aplicación."""
    return "Bienvenida a GL Verse ✨"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gl-verse", description="Herramientas de GL Verse")
    commands = parser.add_subparsers(dest="command")
    importer = commands.add_parser(
        "importar-series",
        help="Valida e incorpora un catálogo JSON en SQLite",
    )
    importer.add_argument("catalog", type=Path, help="Archivo JSON preparado para importar")
    importer.add_argument(
        "--database",
        type=Path,
        default=Path("data/gl_verse.db"),
        help="Base SQLite de destino (por defecto: data/gl_verse.db)",
    )
    importer.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida toda la carga y la revierte antes de guardar",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Ejecuta la aplicación o uno de sus comandos."""
    args = _parser().parse_args(argv)
    if args.command is None:
        print(welcome_message())
        return 0

    try:
        document = load_catalog(args.catalog)
        with closing(connect_database(args.database)) as connection:
            summary = import_catalog(connection, document, dry_run=args.dry_run)
    except (CatalogImportError, OSError, sqlite3.Error) as error:
        print(f"No se pudo importar el catálogo: {error}")
        return 1

    prefix = "Simulación correcta" if summary.dry_run else "Importación completada"
    print(
        f"{prefix}: {summary.inserted_total} registros nuevos, "
        f"{summary.unchanged_total} sin cambios."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
