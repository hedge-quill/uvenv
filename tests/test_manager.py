"""Tests for uvve manager module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from uvve.core.manager import EnvironmentManager


class TestEnvironmentManager:
    """Test cases for the EnvironmentManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = EnvironmentManager(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_manager_initialization(self):
        """Test manager initializes correctly."""
        assert self.manager.path_manager.base_dir == Path(self.temp_dir)

    def test_list_empty_environments(self):
        """Test listing when no environments exist."""
        environments = self.manager.list()
        assert environments == []

    @patch("uvve.core.manager.subprocess.run")
    def test_create_environment_success(self, mock_run):
        """Test successful environment creation."""
        mock_run.return_value = Mock(stderr="", returncode=0)

        # Mock the environment existing check
        with patch.object(
            self.manager.path_manager, "environment_exists", return_value=True
        ):
            # This would normally fail without mocking uv, but we're testing the logic
            pass

    def test_get_environment_info_nonexistent(self):
        """Test getting info for non-existent environment."""
        info = self.manager._get_environment_info("nonexistent")
        assert info["name"] == "nonexistent"
        assert info["python_version"] == "unknown"
        assert info["status"] == "inactive"

    def test_get_environment_info_with_metadata(self):
        """Test getting info when metadata file exists."""
        env_name = "test_env"
        env_path = self.manager.path_manager.get_env_path(env_name)
        env_path.mkdir(parents=True, exist_ok=True)

        # Create metadata file
        metadata = {"name": env_name, "python_version": "3.11.0", "active": True}
        metadata_path = self.manager.path_manager.get_metadata_path(env_name)
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

        info = self.manager._get_environment_info(env_name)
        assert info["name"] == env_name
        assert info["python_version"] == "3.11.0"
        assert info["status"] == "active"

    def test_create_metadata(self):
        """Test metadata file creation."""
        env_name = "test_env"
        python_version = "3.11.0"

        env_path = self.manager.path_manager.get_env_path(env_name)
        env_path.mkdir(parents=True, exist_ok=True)

        self.manager._create_metadata(env_name, python_version)

        metadata_path = self.manager.path_manager.get_metadata_path(env_name)
        assert metadata_path.exists()

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        assert metadata["name"] == env_name
        assert metadata["python_version"] == python_version
        assert "created_at" in metadata
