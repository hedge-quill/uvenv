"""Tests for uvve python module."""

from unittest.mock import Mock, patch

from uvve.core.python import PythonManager


class TestPythonManager:
    """Test cases for the PythonManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PythonManager()

    @patch("uvve.core.python.subprocess.run")
    def test_install_success(self, mock_run):
        """Test successful Python installation."""
        mock_run.return_value = Mock(stderr="", returncode=0)

        # Should not raise an exception
        self.manager.install("3.11.0")

        # Verify the command was called correctly
        mock_run.assert_called_once_with(
            ["uv", "python", "install", "3.11.0"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("uvve.core.python.subprocess.run")
    def test_install_failure(self, mock_run):
        """Test failed Python installation."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "uv", stderr="Error message")

        try:
            self.manager.install("3.11.0")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Failed to install Python 3.11.0" in str(e)

    @patch("uvve.core.python.subprocess.run")
    def test_list_installed_success(self, mock_run):
        """Test successful listing of installed Python versions."""
        mock_output = "3.11.0 /path/to/python3.11\n3.10.5 /path/to/python3.10\n"
        mock_run.return_value = Mock(stdout=mock_output, returncode=0)

        versions = self.manager.list_installed()

        assert len(versions) == 2
        assert versions[0]["version"] == "3.11.0"
        assert versions[0]["path"] == "/path/to/python3.11"
        assert versions[1]["version"] == "3.10.5"
        assert versions[1]["path"] == "/path/to/python3.10"

    @patch("uvve.core.python.subprocess.run")
    def test_list_installed_empty(self, mock_run):
        """Test listing when no Python versions are installed."""
        mock_run.return_value = Mock(stdout="", returncode=0)

        versions = self.manager.list_installed()
        assert versions == []

    @patch("uvve.core.python.subprocess.run")
    def test_list_available_success(self, mock_run):
        """Test successful listing of available Python versions."""
        mock_output = "3.11.0\n3.10.5\n3.9.12\n"
        mock_run.return_value = Mock(stdout=mock_output, returncode=0)

        versions = self.manager.list_available()

        assert "3.11.0" in versions
        assert "3.10.5" in versions
        assert "3.9.12" in versions

    def test_get_version_info_installed(self):
        """Test getting version info for installed version."""
        with patch.object(self.manager, "list_installed") as mock_list:
            mock_list.return_value = [
                {"version": "3.11.0", "path": "/path/to/python3.11"}
            ]

            info = self.manager.get_version_info("3.11.0")

            assert info["version"] == "3.11.0"
            assert info["installed"] is True
            assert info["path"] == "/path/to/python3.11"

    def test_get_version_info_not_installed(self):
        """Test getting version info for non-installed version."""
        with patch.object(self.manager, "list_installed") as mock_list:
            mock_list.return_value = []

            info = self.manager.get_version_info("3.11.0")

            assert info["version"] == "3.11.0"
            assert info["installed"] is False
            assert info["path"] is None
