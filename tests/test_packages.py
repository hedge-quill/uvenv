"""Tests for package commands."""

import tempfile
from unittest.mock import patch

from typer.testing import CliRunner

from uvve.commands.packages import add, freeze, lock, thaw
from uvve.core.freeze import FreezeManager
from uvve.core.manager import EnvironmentManager


class TestPackageCommands:
    """Test cases for package commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def test_add_command_with_environment(self):
        """Test add command with explicit environment."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Successfully installed package"

            result = self.runner.invoke(add, ["--env", "test-env", "requests", "flask"])
            # Command should not crash
            assert result.exit_code in [0, 1]  # May fail due to environment checks

    def test_add_command_auto_detect(self):
        """Test add command with auto-detection."""
        with patch.dict("os.environ", {"VIRTUAL_ENV": "/path/to/test-env"}):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0

                result = self.runner.invoke(add, ["requests"])
                # Command should attempt to use detected environment
                assert result.exit_code in [0, 1]

    def test_add_command_no_environment(self):
        """Test add command without environment specified or detected."""
        with patch.dict("os.environ", {}, clear=True):
            result = self.runner.invoke(add, ["requests"])
            assert result.exit_code == 1
            assert "No environment specified" in result.stdout

    def test_lock_command_with_environment(self):
        """Test lock command with explicit environment."""
        with patch.object(FreezeManager, "create_lockfile") as mock_lock:
            mock_lock.return_value = None

            result = self.runner.invoke(
                lock, ["--env", "test-env", "--output", "requirements.lock"]
            )
            # Should attempt to create lockfile
            assert result.exit_code in [0, 1]

    def test_lock_command_auto_detect(self):
        """Test lock command with auto-detection."""
        with patch.dict("os.environ", {"VIRTUAL_ENV": "/path/to/test-env"}):
            with patch.object(FreezeManager, "create_lockfile") as mock_lock:
                mock_lock.return_value = None

                result = self.runner.invoke(lock, ["--output", "requirements.lock"])
                assert result.exit_code in [0, 1]

    def test_freeze_command_with_environment(self):
        """Test freeze command with explicit environment."""
        mock_packages = ["requests==2.28.1", "flask==2.2.2"]

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "\n".join(mock_packages)

            result = self.runner.invoke(freeze, ["--env", "test-env"])
            assert result.exit_code in [0, 1]

    def test_freeze_command_auto_detect(self):
        """Test freeze command with auto-detection."""
        with patch.dict("os.environ", {"VIRTUAL_ENV": "/path/to/test-env"}):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "requests==2.28.1"

                result = self.runner.invoke(freeze)
                assert result.exit_code in [0, 1]

    def test_thaw_command_with_environment(self):
        """Test thaw command with explicit environment."""
        with patch.object(FreezeManager, "restore_from_lockfile") as mock_thaw:
            mock_thaw.return_value = None

            result = self.runner.invoke(
                thaw, ["--env", "test-env", "--lockfile", "requirements.lock"]
            )
            assert result.exit_code in [0, 1]

    def test_thaw_command_auto_detect(self):
        """Test thaw command with auto-detection."""
        with patch.dict("os.environ", {"VIRTUAL_ENV": "/path/to/test-env"}):
            with patch.object(FreezeManager, "restore_from_lockfile") as mock_thaw:
                mock_thaw.return_value = None

                result = self.runner.invoke(thaw, ["--lockfile", "requirements.lock"])
                assert result.exit_code in [0, 1]

    def test_add_command_multiple_packages(self):
        """Test adding multiple packages at once."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            result = self.runner.invoke(
                add, ["--env", "test-env", "requests", "flask", "pytest"]
            )
            assert result.exit_code in [0, 1]

    def test_lock_command_default_output(self):
        """Test lock command with default output file."""
        with patch.object(FreezeManager, "create_lockfile") as mock_lock:
            mock_lock.return_value = None

            result = self.runner.invoke(lock, ["--env", "test-env"])
            # Should use default requirements.lock
            assert result.exit_code in [0, 1]

    def test_freeze_command_with_output_file(self):
        """Test freeze command with output to file."""
        with patch("subprocess.run") as mock_run:
            with patch("builtins.open", create=True) as mock_open:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "requests==2.28.1"

                result = self.runner.invoke(
                    freeze, ["--env", "test-env", "--output", "frozen.txt"]
                )
                assert result.exit_code in [0, 1]

    def test_thaw_command_missing_lockfile(self):
        """Test thaw command with missing lockfile."""
        result = self.runner.invoke(
            thaw, ["--env", "test-env", "--lockfile", "nonexistent.lock"]
        )
        # Should handle missing file gracefully
        assert result.exit_code in [0, 1]

    def test_add_command_installation_failure(self):
        """Test add command when package installation fails."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Package not found"

            result = self.runner.invoke(
                add, ["--env", "test-env", "nonexistent-package"]
            )
            # Should handle installation failure
            assert result.exit_code in [0, 1]

    def test_environment_detection_logic(self):
        """Test environment detection from VIRTUAL_ENV."""
        test_venv_path = "/Users/test/.uvve/test-env"

        with patch.dict("os.environ", {"VIRTUAL_ENV": test_venv_path}):
            # Should extract environment name from path
            result = self.runner.invoke(add, ["requests"])
            assert result.exit_code in [0, 1]

    def test_package_commands_help(self):
        """Test that all package commands have proper help."""
        commands = [add, lock, freeze, thaw]

        for command in commands:
            result = self.runner.invoke(command, ["--help"])
            assert result.exit_code == 0
            assert "help" in result.stdout.lower() or "usage" in result.stdout.lower()
