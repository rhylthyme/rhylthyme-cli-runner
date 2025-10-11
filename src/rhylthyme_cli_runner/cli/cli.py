import json
import os
import sys

import click


@click.group()
def cli():
    """Rhylthyme CLI Runner"""
    pass


@cli.command()
@click.argument("program_file", type=click.Path(exists=True))
@click.option(
    "--env", "-e", type=click.Path(exists=True), help="Environment file (optional)"
)
@click.option("--debug", is_flag=True, help="Enable debug output")
def run(program_file, env, debug):
    """Run a Rhylthyme program."""
    click.echo(f"Running program: {program_file}")
    if env:
        click.echo(f"Using environment: {env}")
    if debug:
        click.echo("Debug mode enabled.")
    # Placeholder: Add actual program running logic here
    click.echo("[run] Not yet implemented.")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--type",
    "-t",
    type=click.Choice(["program", "environment"]),
    default="program",
    help="Type of file to validate",
)
def validate(input_file, type):
    """Validate a Rhylthyme program or environment file against the spec."""
    click.echo(f"Validating {type}: {input_file}")
    import importlib.resources

    import jsonschema

    if type == "program":
        with open(input_file) as f:
            data = json.load(f)
        # Load schema from rhylthyme-spec package
        import pkg_resources

        schema_path = pkg_resources.resource_filename(
            "rhylthyme_spec", "schemas/program_schema.json"
        )
        with open(schema_path) as sf:
            schema = json.load(sf)
        try:
            jsonschema.validate(instance=data, schema=schema)
            click.echo("Validation successful.")
        except jsonschema.ValidationError as e:
            click.echo(f"Validation failed: {e.message}")
            sys.exit(1)
    else:
        click.echo("Environment validation not yet implemented.")
        sys.exit(1)


if __name__ == "__main__":
    cli()
