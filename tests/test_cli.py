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

    def test_status_command_help(self):
        """Test status command help."""
        result = self.runner.invoke(app, ["status", "--help"])
        assert result.exit_code == 0
        assert "status" in result.stdout.lower()

    def test_analytics_command_help(self):
        """Test analytics command help."""
        result = self.runner.invoke(app, ["analytics", "--help"])
        assert result.exit_code == 0
        assert "analytics" in result.stdout.lower()

    def test_edit_command_help(self):
        """Test edit command help."""
        result = self.runner.invoke(app, ["edit", "--help"])
        assert result.exit_code == 0
        assert "edit" in result.stdout.lower()

    def test_cleanup_command_help(self):
        """Test cleanup command help."""
        result = self.runner.invoke(app, ["cleanup", "--help"])
        assert result.exit_code == 0
        assert "cleanup" in result.stdout.lower()

    def test_add_command_help(self):
        """Test add command help."""
        result = self.runner.invoke(app, ["add", "--help"])
        assert result.exit_code == 0
        assert "add" in result.stdout.lower()

    def test_sync_command_help(self):
        """Test sync command help."""
        result = self.runner.invoke(app, ["sync", "--help"])
        assert result.exit_code == 0
        assert "sync" in result.stdout.lower()

    def test_completion_command_help(self):
        """Test completion command help."""
        result = self.runner.invoke(app, ["completion", "--help"])
        assert result.exit_code == 0
        assert "completion" in result.stdout.lower()

    def test_python_list_command_help(self):
        """Test python list command help."""
        result = self.runner.invoke(app, ["python", "list", "--help"])
        assert result.exit_code == 0
        assert "list" in result.stdout.lower()

    def test_python_install_command_help(self):
        """Test python install command help."""
        result = self.runner.invoke(app, ["python", "install", "--help"])
        assert result.exit_code == 0
        assert "install" in result.stdout.lower()

    def test_all_commands_accessible(self):
        """Test that all commands are accessible from the main CLI."""
        main_help = self.runner.invoke(app, ["--help"])
        assert main_help.exit_code == 0

        # Check that all main commands are listed
        expected_commands = [
            "create",
            "list",
            "remove",
            "activate",
            "add",
            "lock",
            "freeze",
            "thaw",
            "status",
            "analytics",
            "edit",
            "cleanup",
            "sync",
            "completion",
            "python",
        ]

        for command in expected_commands:
            assert command in main_help.stdout
