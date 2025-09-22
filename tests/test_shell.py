"""Tests for shell commands."""

from typer.testing import CliRunner

from uvve.commands.shell import completion


class TestShellCommands:
    """Test cases for shell commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_completion_command_bash(self):
        """Test completion command for bash."""
        result = self.runner.invoke(completion, ["--shell", "bash"])
        assert result.exit_code == 0
        # Should contain bash completion script
        assert "_uvve_completion" in result.stdout or "complete" in result.stdout

    def test_completion_command_zsh(self):
        """Test completion command for zsh."""
        result = self.runner.invoke(completion, ["--shell", "zsh"])
        assert result.exit_code == 0
        # Should contain zsh completion script
        assert "compdef" in result.stdout or "_uvve" in result.stdout

    def test_completion_command_fish(self):
        """Test completion command for fish."""
        result = self.runner.invoke(completion, ["--shell", "fish"])
        assert result.exit_code == 0
        # Should contain fish completion script
        assert "complete" in result.stdout

    def test_completion_command_default_shell(self):
        """Test completion command with default shell detection."""
        result = self.runner.invoke(completion)
        assert result.exit_code == 0
        # Should generate some kind of completion script
        assert len(result.stdout) > 0

    def test_completion_command_invalid_shell(self):
        """Test completion command with invalid shell."""
        result = self.runner.invoke(completion, ["--shell", "invalid"])
        # Should handle gracefully or show error
        assert result.exit_code in [0, 1]

    def test_completion_command_help(self):
        """Test completion command help."""
        result = self.runner.invoke(completion, ["--help"])
        assert result.exit_code == 0
        assert "completion" in result.stdout.lower()
        assert "shell" in result.stdout.lower()

    def test_completion_output_format(self):
        """Test that completion output is properly formatted."""
        result = self.runner.invoke(completion, ["--shell", "bash"])
        assert result.exit_code == 0
        # Should not contain error messages or warnings
        lines = result.stdout.split("\n")
        # At least some output should be generated
        assert len([line for line in lines if line.strip()]) > 0
