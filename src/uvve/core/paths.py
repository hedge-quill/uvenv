"""Manages path operations for uvve."""

import os
from pathlib import Path
from typing import Optional


class PathManager:
    """Manages paths for uvve virtual environments."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        """Initialize the path manager.

        Args:
            base_dir: Base directory for uvve environments.
                     Defaults to ~/.uvve
        """
        if base_dir is None:
            base_dir = os.path.expanduser("~/.uvve")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_env_path(self, name: str) -> Path:
        """Get the path for a specific environment.

        Args:
            name: Environment name

        Returns:
            Path to the environment directory
        """
        return self.base_dir / name

    def get_env_bin_path(self, name: str) -> Path:
        """Get the bin directory path for an environment.

        Args:
            name: Environment name

        Returns:
            Path to the environment's bin directory
        """
        env_path = self.get_env_path(name)
        # On Windows, it's Scripts, on Unix-like systems it's bin
        return env_path / ("Scripts" if os.name == "nt" else "bin")

    def get_env_python_path(self, name: str) -> Path:
        """Get the Python executable path for an environment.

        Args:
            name: Environment name

        Returns:
            Path to the Python executable
        """
        bin_path = self.get_env_bin_path(name)
        python_name = "python.exe" if os.name == "nt" else "python"
        return bin_path / python_name

    def get_lockfile_path(self, name: str) -> Path:
        """Get the lockfile path for an environment.

        Args:
            name: Environment name

        Returns:
            Path to the uvve.lock file
        """
        return self.get_env_path(name) / "uvve.lock"

    def get_requirements_path(self, name: str) -> Path:
        """Get the requirements file path for an environment.

        Args:
            name: Environment name

        Returns:
            Path to the uvve.requirements.txt file
        """
        return self.get_env_path(name) / "uvve.requirements.txt"

    def get_metadata_path(self, name: str) -> Path:
        """Get the metadata file path for an environment.

        Args:
            name: Environment name

        Returns:
            Path to the uvve.meta.json file
        """
        return self.get_env_path(name) / "uvve.meta.json"

    def list_environments(self) -> list[str]:
        """List all environment names.

        Returns:
            List of environment names
        """
        if not self.base_dir.exists():
            return []

        envs = []
        for item in self.base_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                envs.append(item.name)

        return sorted(envs)

    def environment_exists(self, name: str) -> bool:
        """Check if an environment exists.

        Args:
            name: Environment name

        Returns:
            True if environment exists, False otherwise
        """
        env_path = self.get_env_path(name)
        python_path = self.get_env_python_path(name)
        return env_path.exists() and python_path.exists()
