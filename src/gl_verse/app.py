"""Punto de entrada de GL Verse."""

import argparse
import getpass
import sqlite3
from contextlib import closing
from pathlib import Path

from gl_verse.admin_auth import AdminUserError, create_admin
from gl_verse.catalog_import import CatalogImportError, import_catalog, load_catalog
from gl_verse.database import connect_database
from gl_verse.web_server import serve_web


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
    web = commands.add_parser(
        "web",
        help="Sirve el frontal y la API del catálogo",
    )
    web.add_argument(
        "--database",
        type=Path,
        default=Path("data/gl_verse.db"),
        help="Base SQLite consultada por la API (por defecto: data/gl_verse.db)",
    )
    web.add_argument("--host", default="127.0.0.1", help="Interfaz de red")
    web.add_argument("--port", type=int, default=8000, help="Puerto HTTP")
    admin = commands.add_parser(
        "crear-admin",
        help="Crea un usuario local para el backoffice",
    )
    admin.add_argument("username", help="Nombre del administrador")
    admin.add_argument(
        "--database",
        type=Path,
        default=Path("data/gl_verse.db"),
        help="Base SQLite de destino (por defecto: data/gl_verse.db)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Ejecuta la aplicación o uno de sus comandos."""
    args = _parser().parse_args(argv)
    if args.command is None:
        print(welcome_message())
        return 0

    if args.command == "web":
        try:
            serve_web(args.database, host=args.host, port=args.port)
        except (OSError, sqlite3.Error) as error:
            print(f"No se pudo iniciar GL Verse: {error}")
            return 1
        return 0

    if args.command == "crear-admin":
        password = getpass.getpass("Contraseña (mínimo 12 caracteres): ")
        confirmation = getpass.getpass("Repite la contraseña: ")
        if password != confirmation:
            print("No se pudo crear el administrador: las contraseñas no coinciden")
            return 1
        try:
            with closing(connect_database(args.database)) as connection:
                create_admin(connection, args.username, password)
        except (AdminUserError, sqlite3.Error) as error:
            print(f"No se pudo crear el administrador: {error}")
            return 1
        print(f"Administrador {args.username!r} creado.")
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
        f"{summary.updated_total} actualizados, "
        f"{summary.unchanged_total} sin cambios."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
