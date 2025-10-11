# Rhylthyme CLI Runner

Command-line interface for validating and running Rhylthyme real-time program schedules.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/rhylthyme/rhylthyme-cli-runner.git
cd rhylthyme-cli-runner

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### From PyPI

```bash
pip install rhylthyme-cli-runner
```

## Quick Start

The Rhylthyme CLI provides commands for working with real-time program schedules defined using the Rhylthyme JSON or YAML schema.

### Validate a Program

Validate a program file against the schema to ensure it's properly formatted:

```bash
# Validate a JSON or YAML program file
rhylthyme validate my_program.json

# Validate with verbose output
rhylthyme validate my_program.json --verbose

# Validate with JSON output for CI/scripting
rhylthyme validate my_program.json --json

# Validate in strict mode (requires all tasks in resourceConstraints)
rhylthyme validate my_program.json --strict
```

### Run a Program

Run a program with an interactive terminal UI for monitoring and controlling execution:

```bash
# Run a program file
rhylthyme run examples/breakfast_schedule.json

# Run with automatic start (no manual trigger needed)
rhylthyme run examples/breakfast_schedule.json --auto-start

# Run with a different time scale (2x faster)
rhylthyme run examples/breakfast_schedule.json --time-scale 2.0

# Run with a specific environment
rhylthyme run examples/breakfast_schedule.json --environment kitchen

# Run without validation (if you're sure the file is valid)
rhylthyme run examples/breakfast_schedule.json --no-validate
```

### Optimize a Program

Create an optimized version of a program to reduce resource contention:

```bash
# Optimize a program and save to new file
rhylthyme plan examples/breakfast_schedule.json optimized_breakfast.json

# Optimize with verbose output
rhylthyme plan examples/breakfast_schedule.json optimized_breakfast.json --verbose
```

### Work with Environments

List and validate environment catalogs:

```bash
# List all available environments
rhylthyme environments

# List environments in JSON format
rhylthyme environments --format json

# Validate all environment files
rhylthyme validate-environments

# Show information about a specific environment type
rhylthyme environment-info kitchen
```

## Program File Examples

### Simple Breakfast Schedule

```json
{
  "programId": "breakfast-schedule",
  "name": "Breakfast Schedule",
  "description": "Coordinated breakfast preparation",
  "environmentType": "kitchen",
  "startTrigger": {
    "type": "manual"
  },
  "tracks": [
    {
      "trackId": "eggs",
      "name": "Scrambled Eggs",
      "steps": [
        {
          "stepId": "crack-eggs",
          "name": "Crack and Whisk Eggs",
          "startTrigger": {
            "type": "programStart"
          },
          "duration": {
            "type": "fixed",
            "seconds": 60
          }
        }
      ]
    }
  ],
  "resourceConstraints": [
    {
      "task": "stove-burner",
      "maxConcurrent": 2,
      "description": "Maximum stove burners"
    }
  ],
  "version": "1.0.0"
}
```

## Interactive UI Controls

When running a program, the interactive UI provides these controls:

- **Space**: Start/stop the program
- **Enter**: Trigger manual steps
- **Arrow keys**: Navigate between steps
- **q**: Quit the program
- **r**: Refresh the display
- **s**: Sort by different criteria

## Command Reference

### `rhylthyme validate`

Validates program files against the schema.

**Options:**
- `--schema PATH`: Path to schema file (default: built-in schema)
- `--verbose, -v`: Show detailed validation information

### `rhylthyme run`

Runs programs with interactive terminal UI.

**Options:**
- `--schema PATH`: Path to schema file (default: built-in schema)
- `-e, --environment TEXT`: Environment ID to use
- `--time-scale FLOAT`: Time scale factor (default: 1.0)
- `--validate / --no-validate`: Validate before running (default: True)
- `--auto-start`: Automatically start without manual trigger

### `rhylthyme plan`

Optimizes program schedules to reduce resource contention.

**Options:**
- `--verbose, -v`: Show detailed planning information

### `rhylthyme environments`

Lists available environment catalogs.

**Options:**
- `--format, -f`: Output format (table, json, yaml)

### `rhylthyme validate-environments`

Validates environment catalog files.

**Options:**
- `--environments-dir PATH`: Directory containing environment files
- `--verbose, -v`: Show detailed validation information

### `rhylthyme environment-info`

Shows information about a specific environment type.

## Development

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`

## License

Apache License 2.0 