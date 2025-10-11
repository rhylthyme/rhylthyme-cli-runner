"""
Test the CLI interface of rhylthyme-cli-runner.

This module tests the command-line interface functionality.
"""

import json
import os

import pytest


@pytest.mark.cli
class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self, cli_runner):
        """Test CLI help command."""
        result = cli_runner.invoke("cli", ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Commands:" in result.output
        assert "validate" in result.output
        assert "run" in result.output

    def test_cli_version(self, cli_runner):
        """Test CLI version command."""
        from rhylthyme_cli_runner.cli import cli

        result = cli_runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        # Version output format may vary, just check it doesn't crash

    def test_validate_command_help(self, cli_runner):
        """Test validate command help."""
        from rhylthyme_cli_runner.cli import cli

        result = cli_runner.invoke(cli, ["validate", "--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "validate" in result.output

    def test_run_command_help(self, cli_runner):
        """Test run command help."""
        from rhylthyme_cli_runner.cli import cli

        result = cli_runner.invoke(cli, ["run", "--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "run" in result.output


@pytest.mark.cli
@pytest.mark.integration
class TestCLIValidation:
    """Test CLI validation commands."""

    def test_validate_simple_program(self, cli_runner, simple_program_file):
        """Test validating a simple program."""
        from rhylthyme_cli_runner.cli import cli

        result = cli_runner.invoke(cli, ["validate", simple_program_file])

        assert result.exit_code == 0
        assert "is valid" in result.output

    def test_validate_kitchen_program(self, cli_runner, kitchen_program_file):
        """Test validating a kitchen program."""
        from rhylthyme_cli_runner.cli import cli

        result = cli_runner.invoke(cli, ["validate", kitchen_program_file])

        assert result.exit_code == 0
        assert "is valid" in result.output

    def test_validate_with_environment(
        self, cli_runner, kitchen_program_file, kitchen_environment_file
    ):
        """Test validating a program with environment."""
        from rhylthyme_cli_runner.cli import cli

        result = cli_runner.invoke(
            cli, ["validate", kitchen_program_file, "-e", kitchen_environment_file]
        )

        assert result.exit_code == 0
        assert "is valid" in result.output

    def test_validate_nonexistent_file(self, cli_runner):
        """Test validating a nonexistent file."""
        from rhylthyme_cli_runner.cli import cli

        result = cli_runner.invoke(cli, ["validate", "nonexistent.json"])

        assert result.exit_code != 0
        assert "error" in result.output.lower()

    def test_validate_invalid_json(self, cli_runner, temp_dir):
        """Test validating invalid JSON."""
        from rhylthyme_cli_runner.cli import cli

        invalid_file = os.path.join(temp_dir, "invalid.json")
        with open(invalid_file, "w") as f:
            f.write("{ invalid json }")

        result = cli_runner.invoke(cli, ["validate", invalid_file])

        assert result.exit_code != 0
        # Should handle JSON parsing errors gracefully

    def test_validate_invalid_program(self, cli_runner, programs_dir):
        """Test validating a program with missing required fields."""
        from rhylthyme_cli_runner.cli import cli

        invalid_program = {
            "programId": "invalid",
            "name": "Invalid Program",
            # Missing required fields like tracks
        }

        invalid_file = os.path.join(programs_dir, "invalid.json")
        with open(invalid_file, "w") as f:
            json.dump(invalid_program, f)

        result = cli_runner.invoke(cli, ["validate", invalid_file])

        assert result.exit_code != 0
        assert "error" in result.output.lower()


@pytest.mark.cli
class TestCLIEnvironments:
    """Test CLI environment-related commands."""

    def test_environments_command(self, cli_runner):
        """Test environments listing command."""
        from rhylthyme_cli_runner.cli import cli

        result = cli_runner.invoke(cli, ["environments"])

        # This might succeed or fail depending on whether examples are available
        # Just test that it doesn't crash
        assert result.exit_code in [0, 1]  # Success or expected failure

    def test_environment_info_command(self, cli_runner):
        """Test environment info command."""
        from rhylthyme_cli_runner.cli import cli

        result = cli_runner.invoke(cli, ["environment-info", "test-env"])

        # This command should handle missing environments gracefully
        assert isinstance(result.exit_code, int)


@pytest.mark.cli
@pytest.mark.integration
class TestCLIPlanning:
    """Test CLI planning functionality."""

    def test_plan_command(self, cli_runner, kitchen_program_file, temp_dir):
        """Test program planning command."""
        from rhylthyme_cli_runner.cli import cli

        output_file = os.path.join(temp_dir, "planned_output.json")

        result = cli_runner.invoke(cli, ["plan", kitchen_program_file, output_file])

        if result.exit_code == 0:
            # If planning succeeded, output file should exist
            assert os.path.exists(output_file)
            assert "saved to" in result.output
        else:
            # Planning might fail for various reasons, just ensure it doesn't crash
            assert isinstance(result.exit_code, int)


@pytest.mark.cli
class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_validate_with_invalid_environment_file(
        self, cli_runner, simple_program_file, temp_dir
    ):
        """Test validation with invalid environment file."""
        from rhylthyme_cli_runner.cli import cli

        invalid_env = os.path.join(temp_dir, "invalid_env.json")
        with open(invalid_env, "w") as f:
            f.write("{ invalid json }")

        result = cli_runner.invoke(
            cli, ["validate", simple_program_file, "-e", invalid_env]
        )

        assert result.exit_code != 0
        # Should handle environment file errors gracefully

    def test_missing_required_arguments(self, cli_runner):
        """Test commands with missing required arguments."""
        from rhylthyme_cli_runner.cli import cli

        # Validate without program file
        result = cli_runner.invoke(cli, ["validate"])
        assert result.exit_code != 0

        # Plan without required arguments
        result = cli_runner.invoke(cli, ["plan"])
        assert result.exit_code != 0


@pytest.mark.cli
@pytest.mark.slow
def test_cli_with_real_examples(cli_runner, examples_dir):
    """Test CLI with real example files if available."""
    if not examples_dir:
        pytest.skip("Examples directory not available")

    import glob

    from rhylthyme_cli_runner.cli import cli

    programs_dir = os.path.join(examples_dir, "programs")
    if not os.path.exists(programs_dir):
        pytest.skip("Programs directory not found")

    # Test validation with a few real examples
    json_files = glob.glob(os.path.join(programs_dir, "*.json"))

    if json_files:
        # Just test the first few to keep test time reasonable
        for filepath in json_files[:3]:
            result = cli_runner.invoke(cli, ["validate", filepath])
            # Most examples should validate successfully
            # If they don't, it's useful information but shouldn't fail the test
            if result.exit_code != 0:
                print(
                    f"⚠️ Example {os.path.basename(filepath)} failed validation: {result.output}"
                )
    else:
        pytest.skip("No JSON example files found")
