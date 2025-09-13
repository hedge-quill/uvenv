"""Environment management for uvve."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from uvve.core.paths import PathManager


class EnvironmentManager:
    """Manages virtual environment creation, listing, and removal."""

    def __init__(self, base_dir: str | None = None) -> None:
        """Initialize the environment manager.

        Args:
            base_dir: Base directory for environments
        """
        self.path_manager = PathManager(base_dir)

    def get_current_environment(self) -> str | None:
        """Get the name of the currently activated uvve environment.

        Returns:
            Environment name if a uvve environment is active, None otherwise
        """
        virtual_env = os.environ.get("VIRTUAL_ENV")
        if not virtual_env:
            return None

        virtual_env_path = Path(virtual_env)
        base_dir = self.path_manager.base_dir

        # Check if the virtual environment is within our uvve base directory
        try:
            relative_path = virtual_env_path.relative_to(base_dir)
            # The environment name should be the first part of the relative path
            env_name = relative_path.parts[0]

            # Verify this is actually a uvve environment
            if self.path_manager.environment_exists(env_name):
                return env_name
        except ValueError:
            # virtual_env_path is not relative to base_dir
            pass

        return None

    def create(
        self,
        name: str,
        python_version: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> None:
        """Create a new virtual environment.

        Args:
            name: Environment name
            python_version: Python version to use
            description: Optional description for the environment
            tags: Optional list of tags for the environment

        Raises:
            RuntimeError: If environment creation fails
        """
        if tags is None:
            tags = []
        if self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' already exists")

        env_path = self.path_manager.get_env_path(name)

        try:
            # Create the environment using uv
            cmd = ["uv", "venv", str(env_path), "--python", python_version]

            _ = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Create metadata file
            self._create_metadata(name, python_version, description, tags)

        except subprocess.CalledProcessError as e:
            # Clean up partial environment if creation failed
            if env_path.exists():
                shutil.rmtree(env_path)
            raise RuntimeError(f"Failed to create environment: {e.stderr}") from e

    def remove(self, name: str) -> None:
        """Remove a virtual environment.

        Args:
            name: Environment name

        Raises:
            RuntimeError: If environment doesn't exist or removal fails
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        env_path = self.path_manager.get_env_path(name)

        try:
            shutil.rmtree(env_path)
        except OSError as e:
            raise RuntimeError(f"Failed to remove environment: {e}") from e

    def list(self) -> list[dict[str, Any]]:
        """List all virtual environments.

        Returns:
            List of environment dictionaries with details
        """
        envs = []

        for env_name in self.path_manager.list_environments():
            env_info = self._get_environment_info(env_name)
            envs.append(env_info)

        return envs

    def get_activation_script(self, name: str) -> str:
        """Get shell activation script for an environment.

        Args:
            name: Environment name

        Returns:
            Shell activation script

        Raises:
            RuntimeError: If environment doesn't exist
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        bin_path = self.path_manager.get_env_bin_path(name)

        # Return shell-specific activation command
        # This is a simplified version - real implementation would detect shell
        return f"source {bin_path}/activate"

    def _create_metadata(
        self,
        name: str,
        python_version: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> None:
        """Create metadata file for an environment.

        Args:
            name: Environment name
            python_version: Python version used
            description: Optional description for the environment
            tags: Optional list of tags for the environment
        """
        if tags is None:
            tags = []

        metadata = {
            "name": name,
            "description": description,
            "tags": tags,
            "python_version": python_version,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "usage_count": 0,
            "active": False,
            "project_root": None,
            "size_bytes": None,
        }

        metadata_path = self.path_manager.get_metadata_path(name)
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _get_environment_info(self, name: str) -> dict[str, Any]:
        """Get information about an environment.

        Args:
            name: Environment name

        Returns:
            Dictionary with environment information
        """
        env_path = self.path_manager.get_env_path(name)
        metadata_path = self.path_manager.get_metadata_path(name)

        # Default info
        info = {
            "name": name,
            "path": str(env_path),
            "python_version": "unknown",
            "status": "inactive",
        }

        # Try to load metadata
        if metadata_path.exists():
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)
                    info.update(
                        {
                            "python_version": metadata.get("python_version", "unknown"),
                            "status": "active"
                            if metadata.get("active", False)
                            else "inactive",
                        }
                    )
            except (json.JSONDecodeError, OSError):
                pass  # Use defaults if metadata is corrupted

        return info

    def update_usage(self, name: str) -> None:
        """Update usage statistics for an environment.

        Args:
            name: Environment name

        Raises:
            RuntimeError: If environment doesn't exist
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        metadata_path = self.path_manager.get_metadata_path(name)

        # Load existing metadata or create default
        if metadata_path.exists():
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)
            except (json.JSONDecodeError, OSError):
                metadata = self._get_default_metadata(name)
        else:
            metadata = self._get_default_metadata(name)

        # Update usage statistics
        metadata["last_used"] = datetime.now().isoformat()
        metadata["usage_count"] = metadata.get("usage_count", 0) + 1

        # Save updated metadata
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def update_metadata_field(self, name: str, field: str, value: Any) -> None:
        """Update a specific metadata field for an environment.

        Args:
            name: Environment name
            field: Metadata field to update
            value: New value for the field

        Raises:
            RuntimeError: If environment doesn't exist
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        metadata_path = self.path_manager.get_metadata_path(name)

        # Load existing metadata
        if metadata_path.exists():
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)
            except (json.JSONDecodeError, OSError):
                metadata = self._get_default_metadata(name)
        else:
            metadata = self._get_default_metadata(name)

        # Update the field
        metadata[field] = value

        # Save updated metadata
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def get_metadata(self, name: str) -> dict[str, Any]:
        """Get complete metadata for an environment.

        Args:
            name: Environment name

        Returns:
            Dictionary with complete metadata

        Raises:
            RuntimeError: If environment doesn't exist
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        metadata_path = self.path_manager.get_metadata_path(name)

        if metadata_path.exists():
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)

                # Ensure all expected fields exist
                default_metadata = self._get_default_metadata(name)
                for key, default_value in default_metadata.items():
                    if key not in metadata:
                        metadata[key] = default_value

                return metadata
            except (json.JSONDecodeError, OSError):
                return self._get_default_metadata(name)
        else:
            return self._get_default_metadata(name)

    def _get_default_metadata(self, name: str) -> dict[str, Any]:
        """Get default metadata structure for an environment.

        Args:
            name: Environment name

        Returns:
            Default metadata dictionary
        """
        return {
            "name": name,
            "description": "",
            "tags": [],
            "python_version": "unknown",
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "usage_count": 0,
            "active": False,
            "project_root": None,
            "size_bytes": None,
        }

    def get_environment_size(self, name: str) -> int:
        """Calculate the disk size of an environment in bytes.

        Args:
            name: Environment name

        Returns:
            Size in bytes

        Raises:
            RuntimeError: If environment doesn't exist
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        env_path = self.path_manager.get_env_path(name)
        total_size = 0

        try:
            for dirpath, _dirnames, filenames in os.walk(env_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue  # Skip files that can't be accessed
        except OSError as e:
            raise RuntimeError(
                f"Failed to calculate size for environment '{name}'"
            ) from e

        return total_size
