"""Test the uvve CLI commands to ensure they work correctly."""

import subprocess
from unittest.mock import Mock, patch


def test_cli_basic():
    """Test that basic CLI works."""
    result = subprocess.run(
        ["python", "-m", "uvve", "--help"],
        cwd="/Users/mgale/dev/hedge-quill/uvve",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Usage" in result.stdout


def test_python_commands():
    """Test python commands."""
    result = subprocess.run(
        ["python", "-m", "uvve", "python", "--help"],
        cwd="/Users/mgale/dev/hedge-quill/uvve",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Python version management" in result.stdout


def test_import_commands():
    """Test that all command modules can be imported."""
    import uvve.commands.analytics
    import uvve.commands.azure
    import uvve.commands.environment
    import uvve.commands.maintenance
    import uvve.commands.packages
    import uvve.commands.shell

    # Test that the main functions exist
    assert hasattr(uvve.commands.analytics, "status")
    assert hasattr(uvve.commands.analytics, "analytics")
    assert hasattr(uvve.commands.environment, "create")
    assert hasattr(uvve.commands.environment, "env_list")
    assert hasattr(uvve.commands.maintenance, "edit")
    assert hasattr(uvve.commands.maintenance, "cleanup")
    assert hasattr(uvve.commands.packages, "add")
    assert hasattr(uvve.commands.packages, "freeze")
    assert hasattr(uvve.commands.azure, "azure_login")
    assert hasattr(uvve.commands.shell, "completion")


def test_core_managers():
    """Test that core managers can be instantiated."""
    from uvve.core.analytics import AnalyticsManager
    from uvve.core.freeze import FreezeManager
    from uvve.core.manager import EnvironmentManager
    from uvve.core.python import PythonManager

    # Test managers can be created
    env_mgr = EnvironmentManager()
    analytics_mgr = AnalyticsManager()
    freeze_mgr = FreezeManager()
    python_mgr = PythonManager()

    assert env_mgr is not None
    assert analytics_mgr is not None
    assert freeze_mgr is not None
    assert python_mgr is not None


def test_freeze_manager_methods():
    """Test FreezeManager has correct methods."""
    from uvve.core.freeze import FreezeManager

    mgr = FreezeManager()

    # Check that the actual methods exist
    assert hasattr(mgr, "lock")
    assert hasattr(mgr, "thaw")
    assert hasattr(mgr, "add_packages")
    assert hasattr(mgr, "get_tracked_packages")


def test_analytics_manager_methods():
    """Test AnalyticsManager has correct methods."""
    from uvve.core.analytics import AnalyticsManager

    mgr = AnalyticsManager()

    # Check that the actual methods exist
    assert hasattr(mgr, "get_usage_summary")
    assert hasattr(mgr, "get_environment_analytics")
    assert hasattr(mgr, "find_unused_environments")


@patch("uvve.core.python.subprocess.run")
def test_python_manager_parsing(mock_run):
    """Test that Python manager correctly parses uv output."""
    from uvve.core.python import PythonManager

    # Mock the subprocess.run for list_installed
    mock_output = "3.11.0 /path/to/python3.11\n3.10.5 /path/to/python3.10\n"
    mock_run.return_value = Mock(stdout=mock_output, returncode=0)

    manager = PythonManager()
    versions = manager.list_installed()

    # Should parse the output correctly
    assert len(versions) == 2
    assert versions[0]["version"] == "3.11.0"
    assert versions[1]["version"] == "3.10.5"


def test_command_help_outputs():
    """Test that command help outputs work."""
    commands = [
        ["analytics", "--help"],
        ["status", "--help"],
        ["create", "--help"],
        ["list", "--help"],
        ["add", "--help"],
        ["freeze", "--help"],
        ["edit", "--help"],
        ["cleanup", "--help"],
        ["completion", "--help"],
    ]

    for cmd in commands:
        result = subprocess.run(
            ["python", "-m", "uvve"] + cmd,
            cwd="/Users/mgale/dev/hedge-quill/uvve",
            capture_output=True,
            text=True,
        )
        # Help should work for all commands
        assert result.returncode == 0, f"Command {cmd} failed with: {result.stderr}"
        assert "Usage" in result.stdout or "Show this message" in result.stdout
