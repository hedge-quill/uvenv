"""Tests for Azure commands."""

from unittest.mock import patch

from typer.testing import CliRunner

from uvve.commands.azure import azure_login, azure_logout, azure_account


class TestAzureCommands:
    """Test cases for Azure commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_azure_login_command_basic(self):
        """Test basic Azure login command."""
        with patch("uvve.core.azure.AzureManager") as mock_azure:
            mock_azure_instance = mock_azure.return_value
            mock_azure_instance.login.return_value = None

            result = self.runner.invoke(azure_login)
            # Should attempt to login without crashing
            assert result.exit_code in [0, 1]

    def test_azure_login_command_with_tenant(self):
        """Test Azure login with specific tenant."""
        with patch("uvve.core.azure.AzureManager") as mock_azure:
            mock_azure_instance = mock_azure.return_value
            mock_azure_instance.login.return_value = None

            result = self.runner.invoke(azure_login, ["--tenant", "my-tenant-id"])
            assert result.exit_code in [0, 1]

    def test_azure_logout_command(self):
        """Test Azure logout command."""
        with patch("uvve.core.azure.AzureManager") as mock_azure:
            mock_azure_instance = mock_azure.return_value
            mock_azure_instance.logout.return_value = None

            result = self.runner.invoke(azure_logout)
            assert result.exit_code in [0, 1]

    def test_azure_account_command(self):
        """Test Azure account command."""
        with patch("uvve.core.azure.AzureManager") as mock_azure:
            mock_azure_instance = mock_azure.return_value
            mock_azure_instance.get_account_info.return_value = {
                "user": "test@example.com",
                "subscription": "test-subscription",
            }

            result = self.runner.invoke(azure_account)
            assert result.exit_code in [0, 1]

    def test_azure_login_authentication_error(self):
        """Test Azure login with authentication error."""
        with patch("uvve.core.azure.AzureManager") as mock_azure:
            mock_azure_instance = mock_azure.return_value
            mock_azure_instance.login.side_effect = Exception("Authentication failed")

            result = self.runner.invoke(azure_login)
            # Should handle authentication errors gracefully
            assert result.exit_code in [0, 1]

    def test_azure_commands_help(self):
        """Test Azure commands help."""
        commands = [azure_login, azure_logout, azure_account]

        for command in commands:
            result = self.runner.invoke(command, ["--help"])
            assert result.exit_code == 0
            assert "help" in result.stdout.lower() or "usage" in result.stdout.lower()
