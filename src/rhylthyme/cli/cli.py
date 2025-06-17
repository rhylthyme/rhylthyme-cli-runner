#!/usr/bin/env python3
"""
Command-line interface for Rhylthyme

This module provides the command-line interface for the Rhylthyme package,
allowing users to validate and run real-time program schedules.
"""

import os
import sys
import click
import subprocess
import pkg_resources
from .validate_program import validate_program_file
from .program_runner import run_program
from .program_planner import plan_program
from .environment_loader import get_default_loader

# Set up the main CLI group
@click.group()
@click.version_option()
def cli():
    """
    Rhylthyme - A tool for working with real-time program schedules.
    
    This CLI tool provides commands for validating and running real-time
    program schedules defined using the Rhylthyme JSON or YAML schema.
    """
    pass

# Validate command
@cli.command()
@click.argument('program_file', type=click.Path(exists=True))
@click.option('--schema', type=click.Path(exists=True), 
              default=lambda: pkg_resources.resource_filename('rhylthyme', 'program_schema.json'),
              help='Path to the schema file (default: built-in schema)')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed validation information')
def validate(program_file, schema, verbose):
    """
    Validate a program file against the schema.
    
    This command checks if the provided program file (JSON or YAML) conforms to the
    Rhylthyme schema and performs additional semantic validations.
    """
    success = validate_program_file(program_file, schema, verbose)
    if not success:
        sys.exit(1)

# Run command
@cli.command()
@click.argument('program_file', type=click.Path(exists=True))
@click.option('--schema', type=click.Path(exists=True), 
              default=lambda: pkg_resources.resource_filename('rhylthyme', 'program_schema.json'),
              help='Path to the schema file (default: built-in schema)')
@click.option('-e', '--environment', type=str,
              help='Environment ID to use (overrides program environment setting)')
@click.option('--time-scale', type=float, default=1.0, 
              help='Time scale factor (default: 1.0)')
@click.option('--validate/--no-validate', default=True, 
              help='Validate the program before running (default: True)')
@click.option('--auto-start', is_flag=True, 
              help='Automatically start the program without waiting for manual trigger')
def run(program_file, schema, environment, time_scale, validate, auto_start):
    """
    Run a program file with the interactive UI.
    
    This command executes the provided program file (JSON or YAML) according to the
    Rhylthyme schema and displays an interactive terminal UI for
    monitoring and controlling the execution.
    
    Use -e/--environment to specify which environment to use when running the program.
    This overrides any environment specified in the program file.
    """
    run_program(program_file, schema, time_scale, validate, auto_start, environment)

# Plan command
@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--verbose', '-v', is_flag=True, help='Show detailed planning information')
def plan(input_file, output_file, verbose):
    """
    Optimize a program schedule to reduce resource contention.
    
    This command analyzes the provided program file (JSON or YAML) for resource
    bottlenecks and creates an optimized version by staggering track and step
    starts to reduce contention at critical junctures.
    
    The optimized program is saved to the specified output file.
    """
    success = plan_program(input_file, output_file, verbose)
    if not success:
        sys.exit(1)
    
    click.echo(f"Optimized program saved to {output_file}")
    click.echo("Run the optimized program with:")
    click.echo(f"  rhylthyme run {output_file}")

# Marimo command
@cli.command()
@click.option('--notebook', type=click.Path(exists=True), 
              default=lambda: os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'examples', 'marimo_example.py'),
              help='Path to the Marimo notebook file')
def marimo(notebook):
    """
    Launch a Marimo notebook for interactive visualization.
    
    This command launches a Marimo notebook that provides an interactive
    web-based UI for visualizing and controlling program execution.
    """
    try:
        # Check if marimo is installed
        subprocess.run(["which", "marimo"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        click.echo("Error: Marimo is not installed. Please install it with 'pip install marimo'.")
        sys.exit(1)
    
    # Launch the Marimo notebook
    click.echo(f"Launching Marimo notebook: {notebook}")
    subprocess.run(["marimo", "edit", notebook])

# Visualize command
@cli.command()
@click.argument('program_file', type=click.Path(exists=True))
@click.option('-o', '--output', type=str, help='Output HTML file path')
@click.option('--no-browser', is_flag=True, help="Don't open browser automatically")
def visualize(program_file, output, no_browser):
    """
    Generate a web-based visualization of a program file.
    
    This command creates an interactive HTML visualization showing the task dependency
    structure, timeline, resource usage, and execution flow of a Rhylthyme program.
    """
    from .web_visualizer import generate_dag_visualization
    
    try:
        output_file = generate_dag_visualization(
            program_file, 
            output, 
            not no_browser
        )
        click.echo(f"Visualization generated: {output_file}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

# Serve command (removed - d3_visualizer functionality deprecated)
# The web visualization is now generated as static HTML files

# Environments command
@cli.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'yaml']), default='table', 
              help='Output format (default: table)')
def environments(format):
    """
    List all available environment catalogs.
    
    This command displays all environment catalogs that can be referenced
    by programs. Each environment defines resource constraints for different
    settings like restaurants, bakeries, laboratories, etc.
    """
    loader = get_default_loader()
    envs = loader.list_environments()
    
    if not envs:
        click.echo("No environment catalogs found.")
        return
    
    if format == 'json':
        import json
        click.echo(json.dumps(envs, indent=2))
    elif format == 'yaml':
        import yaml
        click.echo(yaml.dump(envs, default_flow_style=False))
    else:  # table format
        # Calculate column widths
        id_width = max(len(env['id']) for env in envs) + 2
        name_width = max(len(env['name']) for env in envs) + 2
        type_width = max(len(env['type']) for env in envs) + 2
        icon_width = max(len(env.get('icon', '')) for env in envs) + 2
        
        # Print header
        click.echo(f"{'ID':<{id_width}}{'Name':<{name_width}}{'Type':<{type_width}}{'Icon':<{icon_width}}Description")
        click.echo(f"{'-' * id_width}{'-' * name_width}{'-' * type_width}{'-' * icon_width}{'-' * 40}")
        
        # Print environments
        for env in envs:
            description = env['description']
            if len(description) > 40:
                description = description[:37] + "..."
            icon = env.get('icon', 'fa-building')
            click.echo(f"{env['id']:<{id_width}}{env['name']:<{name_width}}{env['type']:<{type_width}}{icon:<{icon_width}}{description}")

# Validate environments command
@cli.command('validate-environments')
@click.option('--environments-dir', type=click.Path(exists=True), default='environments',
              help='Directory containing environment files (default: environments)')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed validation information')
def validate_environments(environments_dir, verbose):
    """
    Validate all environment catalog files against their schemas.
    
    This command checks if environment files conform to the base environment
    schema and validates type-specific requirements (e.g., kitchen environments
    should have appropriate kitchen tasks and equipment).
    """
    try:
        from .environment_schemas import validate_all_environments, EnvironmentValidator
    except ImportError:
        click.echo("Error: Environment validation not available. Missing dependencies.")
        sys.exit(1)
    
    click.echo(f"Validating environments in: {environments_dir}")
    validation_results = validate_all_environments(environments_dir)
    
    if not validation_results:
        click.echo("✓ All environment files are valid!")
        return
    
    # Count errors vs warnings
    total_errors = 0
    total_warnings = 0
    
    for filename, errors in validation_results.items():
        click.echo(f"\n{filename}:")
        for error in errors:
            if error.startswith("Warning:"):
                total_warnings += 1
                if verbose:
                    click.echo(f"  ⚠️  {error}")
            else:
                total_errors += 1
                click.echo(f"  ❌ {error}")
    
    if total_errors > 0:
        click.echo(f"\n❌ Validation failed: {total_errors} errors found")
        if total_warnings > 0:
            click.echo(f"⚠️  {total_warnings} warnings found")
        sys.exit(1)
    elif total_warnings > 0:
        click.echo(f"\n⚠️  Validation passed with {total_warnings} warnings")
        if not verbose:
            click.echo("Use --verbose to see warning details")
    else:
        click.echo("✓ All environment files are valid!")

# Environment info command
@cli.command('environment-info')
@click.argument('environment_type')
def environment_info(environment_type):
    """
    Show information about a specific environment type.
    
    This command displays the required tasks, common tasks, and suggested
    actor types for a given environment type (e.g., kitchen, laboratory, bakery).
    """
    try:
        from .environment_schemas import EnvironmentValidator
        from .environment_icons import get_environment_icon
    except ImportError:
        click.echo("Error: Environment schemas not available.")
        sys.exit(1)
    
    validator = EnvironmentValidator()
    info = validator.get_environment_type_info(environment_type)
    
    if not info:
        click.echo(f"Unknown environment type: {environment_type}")
        click.echo(f"Supported types: {', '.join(sorted(validator.list_supported_types()))}")
        sys.exit(1)
    
    # Get icon
    icon = get_environment_icon(environment_type)
    
    click.echo(f"Environment Type: {environment_type}")
    click.echo(f"Icon: {icon}")
    click.echo(f"Required Tasks: {', '.join(info.get('required_tasks', []))}")
    click.echo(f"Common Tasks: {', '.join(info.get('common_tasks', []))}")
    click.echo(f"Actor Types: {', '.join(info.get('actor_types', []))}")

def main():
    """Entry point for the CLI."""
    cli()

if __name__ == '__main__':
    main() 