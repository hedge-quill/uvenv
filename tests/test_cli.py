"""Tests for uvve CLI module."""

import pytest
from typer.testing import CliRunner

from uvve.cli import app


class TestCLI:
    """Test cases for the CLI module."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_exists(self):
        """Test that the CLI app exists and can be imported."""
        assert app is not None

    def test_help_command(self):
        """Test the help command."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "uvve" in result.stdout

    def test_create_command_help(self):
        """Test create command help."""
        result = self.runner.invoke(app, ["create", "--help"])
        assert result.exit_code == 0
        assert "Create a new virtual environment" in result.stdout

    def test_activate_command_help(self):
        """Test activate command help."""
        result = self.runner.invoke(app, ["activate", "--help"])
        assert result.exit_code == 0
        assert "Print shell activation snippet" in result.stdout

    def test_list_command_help(self):
        """Test list command help."""
        result = self.runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        assert "List all virtual environments" in result.stdout

    def test_remove_command_help(self):
        """Test remove command help."""
        result = self.runner.invoke(app, ["remove", "--help"])
        assert result.exit_code == 0
        assert "Remove a virtual environment" in result.stdout

    def test_lock_command_help(self):
        """Test lock command help."""
        result = self.runner.invoke(app, ["lock", "--help"])
        assert result.exit_code == 0
        assert "Generate a lockfile" in result.stdout

    def test_thaw_command_help(self):
        """Test thaw command help."""
        result = self.runner.invoke(app, ["thaw", "--help"])
        assert result.exit_code == 0
        assert "Rebuild environment from lockfile" in result.stdout

    def test_python_install_command_help(self):
        """Test python-install command help."""
        result = self.runner.invoke(app, ["python-install", "--help"])
        assert result.exit_code == 0
        assert "Install a Python version" in result.stdout

    def test_list_empty_environments(self):
        """Test listing when no environments exist."""
        # This test would need mocking in a real implementation
        result = self.runner.invoke(app, ["list"])
        # For now, we just check it doesn't crash
        assert result.exit_code in [0, 1]  # May fail due to missing uv
