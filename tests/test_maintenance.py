"""Tests for maintenance commands."""

import tempfile
from unittest.mock import patch

from typer.testing import CliRunner

from uvve.commands.maintenance import cleanup, edit
from uvve.core.analytics import AnalyticsManager
from uvve.core.manager import EnvironmentManager


class TestMaintenanceCommands:
    """Test cases for maintenance commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def test_edit_command_description(self):
        """Test edit command with description update."""
        with patch.object(EnvironmentManager, "get_metadata") as mock_get_metadata:
            with patch.object(
                EnvironmentManager, "update_metadata_field"
            ) as mock_update:
                mock_get_metadata.return_value = {
                    "tags": ["existing"],
                    "description": "old description",
                }

                result = self.runner.invoke(
                    edit, ["test-env", "--description", "New description"]
                )
                assert result.exit_code == 0
                assert "Updated environment 'test-env'" in result.stdout
                assert "description: 'New description'" in result.stdout
                mock_update.assert_called_with(
                    "test-env", "description", "New description"
                )

    def test_edit_command_add_tags(self):
        """Test edit command with tag addition."""
        with patch.object(EnvironmentManager, "get_metadata") as mock_get_metadata:
            with patch.object(
                EnvironmentManager, "update_metadata_field"
            ) as mock_update:
                mock_get_metadata.return_value = {
                    "tags": ["existing"],
                    "description": "",
                }

                result = self.runner.invoke(
                    edit,
                    ["test-env", "--add-tag", "new-tag", "--add-tag", "another-tag"],
                )
                assert result.exit_code == 0
                assert "Updated environment 'test-env'" in result.stdout
                assert "added tags: new-tag, another-tag" in result.stdout
                # Should be called with existing + new tags
                mock_update.assert_called_with(
                    "test-env", "tags", ["existing", "new-tag", "another-tag"]
                )

    def test_edit_command_remove_tags(self):
        """Test edit command with tag removal."""
        with patch.object(EnvironmentManager, "get_metadata") as mock_get_metadata:
            with patch.object(
                EnvironmentManager, "update_metadata_field"
            ) as mock_update:
                mock_get_metadata.return_value = {
                    "tags": ["tag1", "tag2", "tag3"],
                    "description": "",
                }

                result = self.runner.invoke(edit, ["test-env", "--remove-tag", "tag2"])
                assert result.exit_code == 0
                assert "Updated environment 'test-env'" in result.stdout
                assert "removed tags: tag2" in result.stdout
                # Should be called with remaining tags
                mock_update.assert_called_with("test-env", "tags", ["tag1", "tag3"])

    def test_edit_command_project_root(self):
        """Test edit command with project root update."""
        with patch.object(EnvironmentManager, "get_metadata") as mock_get_metadata:
            with patch.object(
                EnvironmentManager, "update_metadata_field"
            ) as mock_update:
                mock_get_metadata.return_value = {"tags": [], "description": ""}

                result = self.runner.invoke(
                    edit, ["test-env", "--project-root", "/path/to/project"]
                )
                assert result.exit_code == 0
                assert "Updated environment 'test-env'" in result.stdout
                assert "project root:" in result.stdout

    def test_edit_command_no_changes(self):
        """Test edit command with no changes specified."""
        result = self.runner.invoke(edit, ["test-env"])
        assert result.exit_code == 0
        assert "No changes specified" in result.stdout

    def test_edit_command_nonexistent_environment(self):
        """Test edit command with nonexistent environment."""
        with patch.object(EnvironmentManager, "get_metadata") as mock_get_metadata:
            mock_get_metadata.side_effect = RuntimeError("Environment does not exist")

            result = self.runner.invoke(
                edit, ["nonexistent-env", "--description", "test"]
            )
            assert result.exit_code == 1
            assert "Failed to edit environment" in result.stdout

    def test_cleanup_command_dry_run_no_unused(self):
        """Test cleanup command dry run with no unused environments."""
        with patch.object(AnalyticsManager, "find_unused_environments") as mock_find:
            mock_find.return_value = []

            result = self.runner.invoke(cleanup, ["--dry-run"])
            assert result.exit_code == 0
            assert "No environments found that are unused" in result.stdout

    def test_cleanup_command_dry_run_with_unused(self):
        """Test cleanup command dry run with unused environments."""
        mock_unused = [
            {
                "name": "unused-env1",
                "last_used": None,
                "days_since_used": 45,
                "size": "10 MB",
                "size_mb": 10,
            },
            {
                "name": "unused-env2",
                "last_used": "2025-08-01",
                "days_since_used": 52,
                "size": "5 MB",
                "size_mb": 5,
            },
        ]

        with patch.object(AnalyticsManager, "find_unused_environments") as mock_find:
            mock_find.return_value = mock_unused

            result = self.runner.invoke(cleanup, ["--dry-run", "--unused-for", "30"])
            assert result.exit_code == 0
            assert "Found 2 environment(s) to clean up" in result.stdout
            assert "unused-env1" in result.stdout
            assert "unused-env2" in result.stdout
            assert "This was a dry run" in result.stdout

    def test_cleanup_command_interactive_cancel(self):
        """Test cleanup command interactive mode with user cancellation."""
        mock_unused = [
            {
                "name": "unused-env1",
                "last_used": None,
                "days_since_used": 45,
                "size": "10 MB",
                "size_mb": 10,
            }
        ]

        with patch.object(AnalyticsManager, "find_unused_environments") as mock_find:
            with patch("typer.confirm") as mock_confirm:
                mock_find.return_value = mock_unused
                mock_confirm.return_value = False  # User cancels

                result = self.runner.invoke(
                    cleanup, ["--interactive", "--unused-for", "30"], input="n\n"
                )
                # Should not crash even if user cancels
                assert result.exit_code in [0, 1]

    def test_cleanup_command_batch_cancel(self):
        """Test cleanup command batch mode with user cancellation."""
        mock_unused = [
            {
                "name": "unused-env1",
                "last_used": None,
                "days_since_used": 45,
                "size": "10 MB",
                "size_mb": 10,
            }
        ]

        with patch.object(AnalyticsManager, "find_unused_environments") as mock_find:
            with patch("typer.confirm") as mock_confirm:
                mock_find.return_value = mock_unused
                mock_confirm.return_value = False  # User cancels batch removal

                result = self.runner.invoke(
                    cleanup, ["--unused-for", "30"], input="n\n"
                )
                assert result.exit_code == 0
                assert "Cleanup cancelled" in result.stdout

    def test_cleanup_command_successful_removal(self):
        """Test cleanup command with successful environment removal."""
        mock_unused = [
            {
                "name": "unused-env1",
                "last_used": None,
                "days_since_used": 45,
                "size": "10 MB",
                "size_mb": 10,
            }
        ]

        with patch.object(AnalyticsManager, "find_unused_environments") as mock_find:
            with patch.object(EnvironmentManager, "remove") as mock_remove:
                with patch("typer.confirm") as mock_confirm:
                    mock_find.return_value = mock_unused
                    mock_confirm.return_value = True  # User confirms removal
                    mock_remove.return_value = None  # Successful removal

                    result = self.runner.invoke(
                        cleanup, ["--unused-for", "30"], input="y\n"
                    )
                    assert result.exit_code == 0
                    assert "Cleaned up 1 environment(s)" in result.stdout

    def test_cleanup_command_removal_error(self):
        """Test cleanup command with removal error."""
        mock_unused = [
            {
                "name": "unused-env1",
                "last_used": None,
                "days_since_used": 45,
                "size": "10 MB",
                "size_mb": 10,
            }
        ]

        with patch.object(AnalyticsManager, "find_unused_environments") as mock_find:
            with patch.object(EnvironmentManager, "remove") as mock_remove:
                with patch("typer.confirm") as mock_confirm:
                    mock_find.return_value = mock_unused
                    mock_confirm.return_value = True
                    mock_remove.side_effect = RuntimeError("Permission denied")

                    result = self.runner.invoke(
                        cleanup, ["--unused-for", "30"], input="y\n"
                    )
                    assert result.exit_code == 0
                    assert "Failed to remove" in result.stdout

    def test_edit_command_combine_operations(self):
        """Test edit command combining multiple operations."""
        with patch.object(EnvironmentManager, "get_metadata") as mock_get_metadata:
            with patch.object(
                EnvironmentManager, "update_metadata_field"
            ) as mock_update:
                mock_get_metadata.return_value = {
                    "tags": ["old-tag"],
                    "description": "old desc",
                }

                result = self.runner.invoke(
                    edit,
                    [
                        "test-env",
                        "--description",
                        "New description",
                        "--add-tag",
                        "new-tag",
                        "--remove-tag",
                        "old-tag",
                    ],
                )
                assert result.exit_code == 0
                assert "Updated environment 'test-env'" in result.stdout
                assert "description:" in result.stdout
                assert "added tags:" in result.stdout
                assert "removed tags:" in result.stdout
