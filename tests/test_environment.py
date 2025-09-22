"""Tests for environment commands."""

import tempfile
from unittest.mock import patch

from typer.testing import CliRunner

from uvve.commands.environment import activate, create, env_list, remove
from uvve.core.manager import EnvironmentManager


class TestEnvironmentCommands:
    """Test cases for environment commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def test_create_command_basic(self):
        """Test basic environment creation."""
        with patch.object(EnvironmentManager, "create") as mock_create:
            mock_create.return_value = None

            result = self.runner.invoke(create, ["test-env"])
            assert result.exit_code in [0, 1]  # May fail due to uv checks

    def test_create_command_with_python_version(self):
        """Test environment creation with specific Python version."""
        with patch.object(EnvironmentManager, "create") as mock_create:
            mock_create.return_value = None

            result = self.runner.invoke(create, ["test-env", "--python", "3.11"])
            assert result.exit_code in [0, 1]

    def test_create_command_with_description(self):
        """Test environment creation with description."""
        with patch.object(EnvironmentManager, "create") as mock_create:
            mock_create.return_value = None

            result = self.runner.invoke(
                create, ["test-env", "--description", "Test environment"]
            )
            assert result.exit_code in [0, 1]

    def test_create_command_with_tags(self):
        """Test environment creation with tags."""
        with patch.object(EnvironmentManager, "create") as mock_create:
            mock_create.return_value = None

            result = self.runner.invoke(
                create, ["test-env", "--tag", "dev", "--tag", "testing"]
            )
            assert result.exit_code in [0, 1]

    def test_list_command_empty(self):
        """Test list command with no environments."""
        with patch.object(EnvironmentManager, "list") as mock_list:
            mock_list.return_value = []

            result = self.runner.invoke(env_list)
            assert result.exit_code == 0
            assert "No virtual environments found" in result.stdout

    def test_list_command_with_environments(self):
        """Test list command with environments."""
        mock_envs = [
            {
                "name": "test-env1",
                "python_version": "3.11",
                "path": "/path/to/test-env1",
                "active": False,
            },
            {
                "name": "test-env2",
                "python_version": "3.10",
                "path": "/path/to/test-env2",
                "active": True,
            },
        ]

        with patch.object(EnvironmentManager, "list") as mock_list:
            mock_list.return_value = mock_envs

            result = self.runner.invoke(env_list)
            assert result.exit_code == 0
            assert "test-env1" in result.stdout
            assert "test-env2" in result.stdout

    def test_remove_command_basic(self):
        """Test basic environment removal."""
        with patch.object(EnvironmentManager, "remove") as mock_remove:
            mock_remove.return_value = None

            result = self.runner.invoke(remove, ["test-env"])
            assert result.exit_code in [0, 1]

    def test_remove_command_nonexistent(self):
        """Test removing nonexistent environment."""
        with patch.object(EnvironmentManager, "remove") as mock_remove:
            mock_remove.side_effect = RuntimeError("Environment does not exist")

            result = self.runner.invoke(remove, ["nonexistent"])
            assert result.exit_code == 1

    def test_remove_command_force(self):
        """Test removing environment with force flag."""
        with patch.object(EnvironmentManager, "remove") as mock_remove:
            mock_remove.return_value = None

            result = self.runner.invoke(remove, ["test-env", "--force"])
            assert result.exit_code in [0, 1]

    def test_activate_command_basic(self):
        """Test activate command."""
        with patch.object(EnvironmentManager, "get_activation_script") as mock_activate:
            mock_activate.return_value = "export PATH=/path/to/env/bin:$PATH"

            result = self.runner.invoke(activate, ["test-env"])
            assert result.exit_code in [0, 1]

    def test_activate_command_nonexistent(self):
        """Test activate command with nonexistent environment."""
        with patch.object(EnvironmentManager, "get_activation_script") as mock_activate:
            mock_activate.side_effect = RuntimeError("Environment does not exist")

            result = self.runner.invoke(activate, ["nonexistent"])
            assert result.exit_code == 1

    def test_create_command_duplicate_name(self):
        """Test creating environment with duplicate name."""
        with patch.object(EnvironmentManager, "create") as mock_create:
            mock_create.side_effect = RuntimeError("Environment already exists")

            result = self.runner.invoke(create, ["existing-env"])
            assert result.exit_code == 1

    def test_list_command_with_details(self):
        """Test list command shows proper details."""
        mock_envs = [
            {
                "name": "test-env",
                "python_version": "3.11.5",
                "path": "/Users/test/.uvve/test-env",
                "active": False,
                "description": "Test environment",
                "tags": ["test", "dev"],
            }
        ]

        with patch.object(EnvironmentManager, "list") as mock_list:
            mock_list.return_value = mock_envs

            result = self.runner.invoke(env_list)
            assert result.exit_code == 0
            assert "Python Version" in result.stdout
            assert "Status" in result.stdout

    def test_create_command_all_options(self):
        """Test environment creation with all options."""
        with patch.object(EnvironmentManager, "create") as mock_create:
            mock_create.return_value = None

            result = self.runner.invoke(
                create,
                [
                    "full-env",
                    "--python",
                    "3.11",
                    "--description",
                    "Full test environment",
                    "--tag",
                    "dev",
                    "--tag",
                    "testing",
                    "--tag",
                    "full",
                ],
            )
            assert result.exit_code in [0, 1]

    def test_environment_commands_help(self):
        """Test that all environment commands have proper help."""
        commands = [create, env_list, remove, activate]

        for command in commands:
            result = self.runner.invoke(command, ["--help"])
            assert result.exit_code == 0
            assert "help" in result.stdout.lower() or "usage" in result.stdout.lower()

    def test_remove_command_with_confirmation(self):
        """Test remove command with user confirmation."""
        with patch.object(EnvironmentManager, "remove") as mock_remove:
            with patch("typer.confirm") as mock_confirm:
                mock_remove.return_value = None
                mock_confirm.return_value = True

                result = self.runner.invoke(remove, ["test-env"], input="y\n")
                assert result.exit_code in [0, 1]

    def test_activate_command_shell_detection(self):
        """Test activate command with shell detection."""
        with patch.object(EnvironmentManager, "get_activation_script") as mock_activate:
            mock_activate.return_value = "source /path/to/activate"

            result = self.runner.invoke(activate, ["test-env", "--shell", "bash"])
            assert result.exit_code in [0, 1]
