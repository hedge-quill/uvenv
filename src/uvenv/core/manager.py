"""Environment management for uvenv."""

import json
import shutil
import subprocess
from datetime import datetime
from typing import Any

from uvenv.core.paths import PathManager


class EnvironmentManager:
    """Manages virtual environment creation, listing, and removal."""

    def __init__(self, base_dir: str | None = None) -> None:
        """Initialize the environment manager.

        Args:
            base_dir: Base directory for environments
        """
        self.path_manager = PathManager(base_dir)

    def create(self, name: str, python_version: str) -> None:
        """Create a new virtual environment.

        Args:
            name: Environment name
            python_version: Python version to use

        Raises:
            RuntimeError: If environment creation fails
        """
        if self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' already exists")

        env_path = self.path_manager.get_env_path(name)

        try:
            # Create the environment using uv
            cmd = ["uv", "venv", str(env_path), "--python", python_version]

            _ = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Create metadata file
            self._create_metadata(name, python_version)

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

    def _create_metadata(self, name: str, python_version: str) -> None:
        """Create metadata file for an environment.

        Args:
            name: Environment name
            python_version: Python version used
        """
        metadata = {
            "name": name,
            "python_version": python_version,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "active": False,
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
