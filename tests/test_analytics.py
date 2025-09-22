"""Tests for analytics commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from uvve.commands.analytics import analytics, status
from uvve.core.analytics import AnalyticsManager
from uvve.core.manager import EnvironmentManager


class TestAnalyticsCommands:
    """Test cases for analytics commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def test_status_command_no_environments(self):
        """Test status command when no environments exist."""
        with patch.object(AnalyticsManager, "get_usage_summary") as mock_summary:
            mock_summary.return_value = {"total_environments": 0, "environments": []}

            result = self.runner.invoke(status)

            assert result.exit_code == 0
            assert "No environments found" in result.stdout

    def test_status_command_with_environments(self):
        """Test status command with mock environments."""
        mock_envs = [
            {
                "name": "test-env",
                "usage_count": 5,
                "last_used": "2025-09-22T10:00:00",
                "size_bytes": 1024 * 1024,  # 1MB
            }
        ]

        with patch.object(AnalyticsManager, "get_environment_list") as mock_list:
            mock_list.return_value = mock_envs

            result = self.runner.invoke(status)
            assert result.exit_code == 0
            assert "Environment Utility Overview" in result.stdout

    def test_analytics_overall_summary(self):
        """Test analytics command for overall summary."""
        mock_summary = {
            "total_environments": 3,
            "active_environments": 1,
            "unused_environments": 2,
            "environments": [
                {
                    "name": "active-env",
                    "usage_count": 10,
                    "last_used": "2025-09-22T10:00:00",
                    "is_unused": False,
                    "size_bytes": 1024 * 1024,
                    "python_version": "3.11",
                },
                {
                    "name": "unused-env1",
                    "usage_count": 0,
                    "last_used": None,
                    "is_unused": True,
                    "size_bytes": 512 * 1024,
                    "python_version": "3.10",
                },
            ],
        }

        with patch.object(AnalyticsManager, "get_usage_summary") as mock_summary_method:
            mock_summary_method.return_value = mock_summary

            result = self.runner.invoke(analytics)
            assert result.exit_code == 0
            assert "Environment Usage Summary" in result.stdout
            assert "Usage Category" in result.stdout
            assert "Percentage" in result.stdout

    def test_analytics_specific_environment(self):
        """Test analytics command for specific environment."""
        mock_analytics = {
            "name": "test-env",
            "metadata": {
                "python_version": "3.11",
                "created_at": "2025-09-21T19:12:59.142153",
                "last_used": "2025-09-22T20:55:31.562345",
                "usage_count": 5,
                "tags": ["test", "dev"],
                "description": "Test environment",
            },
            "derived_stats": {"days_since_used": 0, "package_count": 10},
            "size_info": {
                "size_bytes": 1024 * 1024 * 5  # 5MB
            },
        }

        with patch.object(
            AnalyticsManager, "get_environment_analytics"
        ) as mock_analytics_method:
            mock_analytics_method.return_value = mock_analytics

            result = self.runner.invoke(analytics, ["test-env"])
            assert result.exit_code == 0
            assert "Analytics for 'test-env'" in result.stdout
            assert "Python Version" in result.stdout
            assert "Created" in result.stdout
            assert "Last Used" in result.stdout

    def test_analytics_nonexistent_environment(self):
        """Test analytics command for nonexistent environment."""
        with patch.object(
            AnalyticsManager, "get_environment_analytics"
        ) as mock_analytics_method:
            mock_analytics_method.side_effect = RuntimeError(
                "Environment 'nonexistent' does not exist"
            )

            result = self.runner.invoke(analytics, ["nonexistent"])
            assert result.exit_code == 1
            assert "Failed to get analytics" in result.stdout

    def test_analytics_detailed_view(self):
        """Test analytics command with detailed flag."""
        mock_summary = {
            "total_environments": 2,
            "active_environments": 1,
            "unused_environments": 1,
            "environments": [
                {
                    "name": "env1",
                    "usage_count": 5,
                    "last_used": "2025-09-22T10:00:00",
                    "is_unused": False,
                    "size_bytes": 1024 * 1024 * 10,  # 10MB
                    "python_version": "3.11",
                },
                {
                    "name": "env2",
                    "usage_count": 0,
                    "last_used": None,
                    "is_unused": True,
                    "size_bytes": 1024 * 1024 * 5,  # 5MB
                    "python_version": "3.10",
                },
            ],
        }

        with patch.object(AnalyticsManager, "get_usage_summary") as mock_summary_method:
            mock_summary_method.return_value = mock_summary

            result = self.runner.invoke(analytics, ["--detailed"])
            assert result.exit_code == 0
            assert "Environment Usage Summary" in result.stdout
            assert "Environment Sizes" in result.stdout

    def test_status_with_percentages(self):
        """Test that status command shows percentages."""
        mock_envs = [
            {
                "name": "active-env",
                "usage_count": 5,
                "last_used": "2025-09-22T10:00:00",
                "size_bytes": 1024 * 1024,
            },
            {
                "name": "unused-env1",
                "usage_count": 0,
                "last_used": None,
                "size_bytes": 512 * 1024,
            },
            {
                "name": "unused-env2",
                "usage_count": 0,
                "last_used": None,
                "size_bytes": 512 * 1024,
            },
        ]

        with patch.object(AnalyticsManager, "get_environment_list") as mock_list:
            mock_list.return_value = mock_envs

            result = self.runner.invoke(status)
            assert result.exit_code == 0
            # Should show percentage in the summary
            assert "%" in result.stdout

    def test_date_formatting(self):
        """Test that dates are properly formatted in analytics."""
        mock_analytics = {
            "name": "test-env",
            "metadata": {
                "python_version": "3.11",
                "created_at": "2025-09-21T19:12:59.142153",
                "last_used": "2025-09-22T20:55:31.562345",
                "usage_count": 1,
                "tags": [],
                "description": "",
            },
            "derived_stats": {"days_since_used": 0, "package_count": 0},
            "size_info": {"size_bytes": 1024 * 1024},
        }

        with patch.object(
            AnalyticsManager, "get_environment_analytics"
        ) as mock_analytics_method:
            mock_analytics_method.return_value = mock_analytics

            result = self.runner.invoke(analytics, ["test-env"])
            assert result.exit_code == 0
            # Check that dates are formatted without microseconds and with space instead of T
            assert "2025-09-21 19:12:59" in result.stdout
            assert "2025-09-22 20:55:31" in result.stdout
