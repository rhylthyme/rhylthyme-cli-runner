"""``rhylthyme login | logout | whoami | generate``.

``generate`` is the natural-language path: it sends the request to the
hosted MCP server's ``import_text`` tool (four model turns, run and paid
for server-side, so it needs a sign-in), then publishes the resulting
program with ``visualize_schedule`` and prints the Gantt summary and the
live-timeline URL. ``--run`` hands the program straight to ``rhylthyme
run`` for the terminal runner.
"""

from __future__ import annotations

import json
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

import click

from . import auth
from .mcp_client import McpClient, McpError, ToolError, endpoint_for, extract_program

ENVIRONMENTS = ["generic", "kitchen", "lab", "events", "gym"]


def _fail(msg: str) -> None:
    raise click.ClickException(msg)


@click.command("login")
@click.option(
    "--token",
    help="Store a pasted access token instead of signing in through the browser (expires in about an hour).",
)
@click.option(
    "--no-browser", is_flag=True, help="Print the sign-in URL instead of opening it."
)
def login(token: Optional[str], no_browser: bool):
    """Sign in to rhylthyme.com so `generate` can use the hosted MCP server."""
    try:
        if token:
            auth.login_with_token(token)
            click.echo(
                f"Saved token to {auth.credentials_path()} (no refresh; run `rhylthyme login` again when it expires)."
            )
            return
        creds = auth.login_via_browser(open_browser=not no_browser, echo=click.echo)
    except auth.AuthError as e:
        _fail(str(e))
    except OSError as e:
        _fail(f"Could not reach {auth.site_url()}: {e}")
    who = creds.get("email") or "your account"
    click.echo(f"Signed in as {who}. Session saved to {auth.credentials_path()}.")


@click.command("logout")
def logout():
    """Forget the stored rhylthyme.com session."""
    if auth.clear_credentials():
        click.echo("Signed out.")
    else:
        click.echo("Not signed in.")


@click.command("whoami")
def whoami():
    """Show the stored sign-in and when it expires."""
    creds = auth.load_credentials()
    if not creds:
        click.echo("Not signed in. Run `rhylthyme login`.")
        return
    exp = creds.get("expires_at")
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime(exp)) if exp else "unknown"
    renew = "renews automatically" if creds.get("refresh_token") else "no refresh token"
    click.echo(
        f"{creds.get('email') or 'signed in'} · access token expires {when} · {renew}"
    )


def _read_request(words, file) -> str:
    parts = []
    if file:
        parts.append(sys.stdin.read() if file == "-" else Path(file).read_text())
    if words:
        parts.append(" ".join(words))
    if not parts and not sys.stdin.isatty():
        parts.append(sys.stdin.read())
    text = "\n\n".join(p.strip() for p in parts if p and p.strip())
    if not text:
        _fail(
            'Describe what to schedule, e.g. rhylthyme generate "roast chicken and two sides for 6, dinner at 7pm"'
        )
    return text


@click.command("generate")
@click.argument("request", nargs=-1)
@click.option(
    "-f",
    "--file",
    "file",
    type=click.Path(allow_dash=True),
    help="Read the request or source text (recipe, protocol, run sheet) from a file, or - for stdin.",
)
@click.option(
    "-e",
    "--env",
    "environment",
    type=click.Choice(ENVIRONMENTS),
    default="generic",
    show_default=True,
    help="Where it happens. Picks the timeline site and the model's vocabulary.",
)
@click.option(
    "--by",
    "deadline",
    help='When everything must be done, e.g. "19:00" or "dinner at 7pm".',
)
@click.option(
    "--with",
    "hints",
    help='Equipment and people limits, e.g. "one oven, four burners, two cooks".',
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False),
    help="Save the program JSON here.",
)
@click.option(
    "--no-publish",
    is_flag=True,
    help="Only build the program; don't create a live timeline.",
)
@click.option(
    "--open", "open_url", is_flag=True, help="Open the live timeline in a browser."
)
@click.option(
    "--run",
    "run_after",
    is_flag=True,
    help="Run the program in the terminal runner afterwards.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Print {url, program, ...} as JSON instead of the summary.",
)
@click.option("-q", "--quiet", is_flag=True, help="Print only the live-timeline URL.")
@click.pass_context
def generate(
    ctx,
    request,
    file,
    environment,
    deadline,
    hints,
    output,
    no_publish,
    open_url,
    run_after,
    json_output,
    quiet,
):
    """Turn a natural-language request into a program and a live timeline.

    \b
    Examples:
      rhylthyme generate "roast chicken, potatoes and green beans for 6" -e kitchen --by 19:00 --with "one oven"
      rhylthyme generate -e lab -f western_blot.txt -o blot.json --run
      pbpaste | rhylthyme generate -e events --by "doors at 18:30"

    Uses the hosted MCP server (mcp.rhylthyme.com); run `rhylthyme login` once first.
    """
    text = _read_request(request, file)
    try:
        token = auth.access_token()
    except auth.AuthError as e:
        _fail(str(e))

    client = McpClient(url=endpoint_for(environment))
    say = (
        (lambda m: None)
        if (quiet or json_output)
        else (lambda m: click.echo(m, err=True))
    )

    args = {"text": text, "environmentType": environment, "token": token}
    if deadline:
        args["deadline"] = deadline
    if hints:
        args["hints"] = hints
    say(
        "Building the schedule (the server reads your request in four passes; ~20-60 s)…"
    )
    try:
        imported = client.call_tool("import_text", args, timeout=240)
    except ToolError as e:
        if "login" in e.text.lower() or "token" in e.text.lower():
            _fail(f"{e.text}\n\nYour sign-in may have expired: run `rhylthyme login`.")
        _fail(e.text)
    except McpError as e:
        _fail(str(e))
    program = extract_program(imported.text)
    if not program:
        _fail("The server did not return a program.\n\n" + imported.text[:1500])

    if output:
        Path(output).write_text(json.dumps(program, indent=2) + "\n")
        say(f"Saved program to {output}")

    published = None
    if not no_publish:
        say("Publishing the live timeline…")
        try:
            published = client.call_tool(
                "visualize_schedule", {"program": program}, timeout=60
            )
        except (ToolError, McpError) as e:
            _fail(f"Built the program but could not publish it: {e}")
    url = (published.structured or {}).get("url") if published else None

    if json_output:
        click.echo(
            json.dumps(
                {
                    "url": url,
                    "imageUrl": (
                        (published.structured or {}).get("imageUrl")
                        if published
                        else None
                    ),
                    "makespanSeconds": (
                        (published.structured or {}).get("makespanSeconds")
                        if published
                        else None
                    ),
                    "program": program,
                },
                indent=2,
            )
        )
    elif quiet:
        if url:
            click.echo(url)
    else:
        click.echo(
            (published or imported)
            .text.split("\n\nCall **visualize_schedule**")[0]
            .strip()
        )
        if url:
            click.echo(f"\nLive timeline: {url}")

    if open_url and url:
        webbrowser.open(url)

    if run_after:
        from ..cli import run as run_command

        path = output
        if not path:
            safe = (
                "".join(
                    c if c.isalnum() else "_"
                    for c in (program.get("name") or "program")
                )
                .strip("_")
                .lower()
            )
            path = str(Path.cwd() / f"{safe or 'program'}.json")
            Path(path).write_text(json.dumps(program, indent=2) + "\n")
            say(f"Saved program to {path}")
        ctx.invoke(run_command, program_file=path)


def register(cli_group: click.Group) -> None:
    for command in (login, logout, whoami, generate):
        cli_group.add_command(command)
