"""``rhylthyme import`` and ``rhylthyme search``: the importers from
rhylthyme-importers, reached from the one command people already have.

``rhylthyme-import`` (the importers' own command) still exists; this is the
same work with the CLI's validation and publishing on the end of it.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Optional

import click

INSTALL_HINT = (
    "The importers are a separate package: pip install rhylthyme-importers "
    "(or pip install rhylthyme, which includes them)."
)


def _registry():
    try:
        from rhylthyme_importers import ImporterRegistry
    except ImportError:
        raise click.ClickException(INSTALL_HINT)
    return ImporterRegistry


def _pick(registry, source: str, importer_name: Optional[str]):
    if importer_name:
        importer = registry.get(importer_name)
        if importer is None:
            names = ", ".join(sorted(i["name"] for i in registry.list_importers()))
            raise click.ClickException(
                f"Unknown importer '{importer_name}'. Installed: {names}."
            )
        return importer
    importer = registry.find_for_url(source)
    if importer is None:
        names = ", ".join(sorted(i["name"] for i in registry.list_importers()))
        raise click.ClickException(
            f"No importer recognises {source!r}. Pass -i with one of: {names}. "
            "For a file on disk, name its importer (-i opentrons, -i cooklang, -i slidedeck)."
        )
    return importer


def _import_one(importer, source: str, text: Optional[str]):
    if text is not None and hasattr(importer, "import_from_source"):
        return importer.import_from_source(text)
    if text is not None and hasattr(importer, "import_from_content"):
        return importer.import_from_content(
            text, source_name=Path(source).stem if source != "-" else "recipe"
        )
    path = Path(source)
    if path.is_file():
        # A local file was named explicitly; that is the command line's job
        # to allow (a server never does this).
        if hasattr(importer, "allow_local_files"):
            importer.allow_local_files = True
        return importer.import_from_url(str(path))
    return importer.import_from_url(source)


def _validation(program: dict):
    from .validate_program import validate_program_file_structured

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
        json.dump(program, tmp)
        tmp_path = tmp.name
    try:
        from .cli import _default_schema_path

        return validate_program_file_structured(
            tmp_path, schema_file=_default_schema_path()
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@click.command("import")
@click.argument("source", metavar="URL_OR_ID_OR_FILE")
@click.option(
    "-i",
    "--importer",
    "importer_name",
    default=None,
    help="Which importer to use (default: chosen from the URL).",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False),
    default=None,
    help="Write the program here (default: <name>.json in the current directory).",
)
@click.option(
    "--stdout",
    "to_stdout",
    is_flag=True,
    help="Print the program instead of writing a file.",
)
@click.option(
    "--publish",
    "do_publish",
    is_flag=True,
    help="Also publish it as a live timeline and print the URL.",
)
@click.option(
    "--open",
    "open_url",
    is_flag=True,
    help="With --publish: open the timeline in a browser.",
)
@click.option(
    "--no-validate", is_flag=True, help="Skip validation of the imported program."
)
def import_command(
    source, importer_name, output, to_stdout, do_publish, open_url, no_validate
):
    """Import a recipe, protocol or deck as a program.

    \b
    URL_OR_ID_OR_FILE is a recipe-site or protocols.io URL, a TheMealDB or
    Spoonacular id, a .cook or GitHub .cook URL, or a local .py (Opentrons),
    .cook or .pptx file. `-` reads the source text from stdin (with -i).
      rhylthyme import https://www.seriouseats.com/the-best-chili-recipe
      rhylthyme import 52772 -i themealdb --publish
      rhylthyme import protocol.py -o protocol.json
      rhylthyme importers          # what is installed
    """
    registry = _registry()
    text = None
    if source == "-":
        if not importer_name:
            raise click.ClickException(
                "Reading from stdin needs -i to say which importer."
            )
        text = sys.stdin.read()
    importer = _pick(registry, source, importer_name)
    click.echo(f"Importing with {importer.name}…", err=True)
    result = _import_one(importer, source, text)
    if not result.success:
        raise click.ClickException(result.error or "import failed")
    program = result.program

    if not no_validate:
        v = _validation(program)
        errors = v.get("errors") or v.get("logic_errors") or []
        if not v.get("is_valid", v.get("valid", True)):
            for e in errors[:8]:
                click.echo(
                    f"  ✗ {e if isinstance(e, str) else e.get('message', e)}", err=True
                )
            raise click.ClickException(
                "The imported program does not validate; not published. Re-run with --no-validate to keep it anyway."
            )
        for w in (v.get("warnings") or [])[:5]:
            click.echo(
                f"  ! {w if isinstance(w, str) else w.get('message', w)}", err=True
            )

    payload = json.dumps(program, indent=2, ensure_ascii=False)
    if to_stdout:
        click.echo(payload)
    else:
        target = (
            Path(output)
            if output
            else Path(f"{program.get('programId') or 'program'}.json")
        )
        target.write_text(payload + "\n")
        click.echo(f"Saved {target}", err=True)

    if do_publish:
        from .remote.cli import publish as publish_command

        ctx = click.get_current_context()
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            tmp.write(payload)
            tmp_path = tmp.name
        try:
            ctx.invoke(
                publish_command,
                program_file=tmp_path,
                environment=None,
                open_url=open_url,
                json_output=False,
                quiet=True,
                image_path=None,
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)


@click.command("search")
@click.argument("query")
@click.option(
    "-i",
    "--importer",
    "importer_name",
    default="themealdb",
    show_default=True,
    help="Which catalogue to search.",
)
@click.option("--json", "json_output", is_flag=True)
def search_command(query, importer_name, json_output):
    """Search a recipe or protocol source; import a hit with `rhylthyme import <url>`."""
    registry = _registry()
    importer = registry.get(importer_name)
    if importer is None:
        names = ", ".join(sorted(i["name"] for i in registry.list_importers()))
        raise click.ClickException(
            f"Unknown importer '{importer_name}'. Installed: {names}."
        )
    hits = importer.search(query)
    if json_output:
        click.echo(json.dumps(hits, indent=2, ensure_ascii=False))
        return
    if not hits:
        click.echo("No results.")
        return
    for h in hits:
        click.echo(f"{h.get('name')}\n    {h.get('url')}")
        if h.get("description"):
            click.echo(f"    {h['description']}")


@click.command("importers")
def importers_command():
    """List the installed importers."""
    registry = _registry()
    for info in registry.list_importers():
        domains = info.get("supported_domains") or []
        where = (
            ", ".join(domains[:4])
            + (f", … ({len(domains)} sites)" if len(domains) > 4 else "")
            if domains
            else "files, ids or pasted text"
        )
        click.echo(f"{info['name']:18} {info['description']}  [{where}]")


def register(cli_group: click.Group) -> None:
    cli_group.add_command(import_command)
    cli_group.add_command(search_command)
    cli_group.add_command(importers_command)
