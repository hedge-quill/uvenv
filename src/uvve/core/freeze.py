"""Lockfile management for uvve."""

import subprocess
from datetime import datetime
from typing import Any

import toml
from rich.console import Console

from uvve.core.paths import PathManager

console = Console()


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

            # Use uv pip list to get installed packages with exact versions
            cmd = [
                "uv",
                "pip",
                "list",
                "--python",
                str(python_path),
                "--format",
                "freeze",
            ]
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

            # Get tracked packages (manually added via uvve add)
            tracked_packages = self.get_tracked_packages(name)

            # Create lockfile content
            lockfile_data = {
                "uvve": {"version": "0.1.0", "generated": datetime.now().isoformat()},
                "environment": {"name": name, "python_version": python_version},
                "dependencies": dependencies,
                "tracked_packages": tracked_packages,
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
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            raise RuntimeError(f"Failed to generate lockfile: {error_msg}") from e
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

            # Get Python executable
            python_path = self.path_manager.get_env_python_path(name)

            # Install tracked packages (manually added ones) first
            tracked_packages = lockfile_data.get("tracked_packages", [])
            if tracked_packages:
                cmd = [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    str(python_path),
                ] + tracked_packages
                subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Get all dependencies from lockfile for verification
            dependencies = lockfile_data.get("dependencies", [])

            # Update the requirements tracking file with tracked packages
            if tracked_packages:
                self._restore_requirements_file(name, tracked_packages)

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            raise RuntimeError(f"Failed to restore from lockfile: {error_msg}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to restore from lockfile: {e}") from e

    def _restore_requirements_file(self, name: str, packages: list[str]) -> None:
        """Restore the requirements tracking file.

        Args:
            name: Environment name
            packages: List of package specifications to restore
        """
        requirements_path = self.path_manager.get_requirements_path(name)

        with open(requirements_path, "w") as f:
            f.write(f"# uvve requirements for environment: {name}\n")
            f.write(f"# Restored from lockfile on: {datetime.now().isoformat()}\n")
            f.write("# This file tracks manually added packages via 'uvve add'\n\n")
            for req in sorted(packages):
                f.write(f"{req}\n")

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

    def add_packages(self, name: str, packages: list[str]) -> None:
        """Add packages to an environment and track them.

        Args:
            name: Environment name
            packages: List of package specifications (e.g., ['requests', 'django==4.2'])

        Raises:
            RuntimeError: If environment doesn't exist or installation fails
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        try:
            # Get the Python executable for the environment
            python_path = self.path_manager.get_env_python_path(name)

            # Install packages using uv pip install
            # Don't capture output so users can see the installation progress
            cmd = ["uv", "pip", "install", "--python", str(python_path)] + packages
            subprocess.run(cmd, check=True)

            # Update the requirements tracking file
            self._update_requirements_file(name, packages)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install packages") from e
        except Exception as e:
            raise RuntimeError(f"Failed to add packages: {e}") from e

    def _update_requirements_file(self, name: str, new_packages: list[str]) -> None:
        """Update the requirements tracking file with new packages.

        Args:
            name: Environment name
            new_packages: List of package specifications to add
        """
        requirements_path = self.path_manager.get_requirements_path(name)

        # Read existing requirements if file exists
        existing_requirements = set()
        if requirements_path.exists():
            with open(requirements_path) as f:
                existing_requirements = {
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                }

        # Add new packages (convert to set for deduplication)
        new_package_names = set()
        for pkg in new_packages:
            # Extract package name (before any version specifier)
            pkg_name = pkg.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0]
            new_package_names.add(pkg_name.strip())

        # Remove any existing entries for the same packages (to avoid duplicates)
        filtered_requirements = {
            req
            for req in existing_requirements
            if req.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
            not in new_package_names
        }

        # Combine with new packages
        all_requirements = filtered_requirements | set(new_packages)

        # Write updated requirements file
        with open(requirements_path, "w") as f:
            f.write(f"# uvve requirements for environment: {name}\n")
            f.write(f"# Generated on: {datetime.now().isoformat()}\n")
            f.write("# This file tracks manually added packages via 'uvve add'\n\n")
            for req in sorted(all_requirements):
                f.write(f"{req}\n")

    def get_tracked_packages(self, name: str) -> list[str]:
        """Get list of tracked packages for an environment.

        Args:
            name: Environment name

        Returns:
            List of package specifications from the requirements file

        Raises:
            RuntimeError: If environment doesn't exist
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        requirements_path = self.path_manager.get_requirements_path(name)

        if not requirements_path.exists():
            return []

        try:
            with open(requirements_path) as f:
                return [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        except Exception as e:
            raise RuntimeError(f"Failed to read requirements file: {e}") from e

    def show_installed_packages(self, name: str) -> None:
        """Show all installed packages in an environment.

        Args:
            name: Environment name

        Raises:
            RuntimeError: If environment doesn't exist or listing fails
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        try:
            # Get the Python executable for the environment
            python_path = self.path_manager.get_env_python_path(name)

            # Use uv pip list to get installed packages
            cmd = ["uv", "pip", "list", "--python", str(python_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            lines = result.stdout.strip().split("\n")
            if len(lines) <= 2:  # Header lines only
                console.print(
                    f"[yellow]No packages installed in environment '{name}'[/yellow]"
                )
                return

            # Print the output directly (uv pip list has nice formatting)
            for line in lines:
                console.print(line)

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            raise RuntimeError(f"Failed to list packages: {error_msg}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to list packages: {e}") from e

    def remove_packages(self, name: str, packages: list[str]) -> None:
        """Remove packages from an environment and update tracking.

        Args:
            name: Environment name
            packages: List of package names to remove (e.g., ['requests', 'django'])

        Raises:
            RuntimeError: If environment doesn't exist or removal fails
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        try:
            # Get the Python executable for the environment
            python_path = self.path_manager.get_env_python_path(name)

            # Remove packages using uv pip uninstall
            # Don't capture output so users can see the uninstallation progress
            cmd = ["uv", "pip", "uninstall", "--python", str(python_path)] + packages
            subprocess.run(cmd, check=True)

            # Update the requirements tracking file
            self._remove_from_requirements_file(name, packages)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to remove packages") from e
        except Exception as e:
            raise RuntimeError(f"Failed to remove packages: {e}") from e

    def _remove_from_requirements_file(self, name: str, removed_packages: list[str]) -> None:
        """Remove packages from the requirements tracking file.

        Args:
            name: Environment name
            removed_packages: List of package names to remove
        """
        requirements_path = self.path_manager.get_requirements_path(name)

        # If requirements file doesn't exist, nothing to do
        if not requirements_path.exists():
            return

        # Read existing requirements
        existing_requirements = set()
        with open(requirements_path) as f:
            existing_requirements = {
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            }

        # Extract package names from removed packages (handle version specifiers)
        removed_package_names = set()
        for pkg in removed_packages:
            # Extract package name (before any version specifier)
            pkg_name = pkg.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0]
            removed_package_names.add(pkg_name.strip().lower())

        # Filter out removed packages from existing requirements
        filtered_requirements = {
            req
            for req in existing_requirements
            if req.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip().lower()
            not in removed_package_names
        }

        # Write updated requirements file
        with open(requirements_path, "w") as f:
            f.write(f"# uvve requirements for environment: {name}\n")
            f.write(f"# Updated on: {datetime.now().isoformat()}\n")
            f.write("# This file tracks manually added packages via 'uvve add'\n\n")
            for req in sorted(filtered_requirements):
                f.write(f"{req}\n")
