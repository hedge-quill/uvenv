"""Lockfile management for uvve."""

import subprocess
from datetime import datetime
from typing import Any

import toml

from uvve.core.paths import PathManager


class FreezeManager:
    """Manages environment freezing and thawing via lockfiles."""

    def __init__(self, base_dir: str | None = None) -> None:
        """Initialize the freeze manager.

        Args:
            base_dir: Base directory for environments
        """
        self.path_manager = PathManager(base_dir)

    def lock(self, name: str) -> None:
        """Generate a lockfile for an environment.

        Args:
            name: Environment name

        Raises:
            RuntimeError: If environment doesn't exist or locking fails
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        try:
            # Get the Python executable for the environment
            python_path = self.path_manager.get_env_python_path(name)

            # Run pip freeze to get installed packages
            cmd = [str(python_path), "-m", "pip", "freeze"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Parse the freeze output
            dependencies = []
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    dependencies.append(line)

            # Get Python version
            version_cmd = [str(python_path), "--version"]
            version_result = subprocess.run(
                version_cmd, capture_output=True, text=True, check=True
            )
            python_version = version_result.stdout.strip().split()[-1]

            # Create lockfile content
            lockfile_data = {
                "uvve": {"version": "0.1.0", "generated": datetime.now().isoformat()},
                "environment": {"name": name, "python_version": python_version},
                "dependencies": dependencies,
                "metadata": {
                    "locked_at": datetime.now().isoformat(),
                    "platform": self._get_platform_info(),
                },
            }

            # Write lockfile
            lockfile_path = self.path_manager.get_lockfile_path(name)
            with open(lockfile_path, "w") as f:
                toml.dump(lockfile_data, f)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to generate lockfile: {e.stderr}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to generate lockfile: {e}") from e

    def thaw(self, name: str) -> None:
        """Rebuild environment from lockfile.

        Args:
            name: Environment name

        Raises:
            RuntimeError: If lockfile doesn't exist or thawing fails
        """
        lockfile_path = self.path_manager.get_lockfile_path(name)

        if not lockfile_path.exists():
            raise RuntimeError(f"No lockfile found for environment '{name}'")

        try:
            # Read lockfile
            with open(lockfile_path) as f:
                lockfile_data = toml.load(f)

            # Verify environment exists
            if not self.path_manager.environment_exists(name):
                raise RuntimeError(
                    f"Environment '{name}' does not exist. Create it first."
                )

            # Get dependencies from lockfile
            dependencies = lockfile_data.get("dependencies", [])

            if not dependencies:
                return  # Nothing to install

            # Get Python executable
            python_path = self.path_manager.get_env_python_path(name)

            # Install dependencies
            cmd = [str(python_path), "-m", "pip", "install"] + dependencies
            subprocess.run(cmd, capture_output=True, text=True, check=True)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to restore from lockfile: {e.stderr}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to restore from lockfile: {e}") from e

    def get_lockfile_info(self, name: str) -> dict[str, Any]:
        """Get information from a lockfile.

        Args:
            name: Environment name

        Returns:
            Dictionary with lockfile information

        Raises:
            RuntimeError: If lockfile doesn't exist or is invalid
        """
        lockfile_path = self.path_manager.get_lockfile_path(name)

        if not lockfile_path.exists():
            raise RuntimeError(f"No lockfile found for environment '{name}'")

        try:
            with open(lockfile_path) as f:
                return toml.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read lockfile: {e}") from e

    def _get_platform_info(self) -> dict[str, str]:
        """Get platform information for lockfile metadata.

        Returns:
            Dictionary with platform info
        """
        import platform

        return {
            "system": platform.system(),
            "machine": platform.machine(),
            "python_implementation": platform.python_implementation(),
        }
