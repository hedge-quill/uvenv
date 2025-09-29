"""Python version management for uvve."""

import subprocess


class PythonManager:
    """Manages Python version installation and listing using uv."""

    def install(self, version: str) -> None:
        """Install a Python version using uv.

        Args:
            version: Python version to install (e.g., "3.11", "3.11.5")

        Raises:
            RuntimeError: If installation fails
        """
        try:
            cmd = ["uv", "python", "install", version]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install Python {version}: {e.stderr}") from e

    def remove(self, version: str) -> None:
        """Remove a Python version using uv.

        Args:
            version: Python version to remove (e.g., "3.11", "3.11.5")

        Raises:
            RuntimeError: If removal fails
        """
        try:
            cmd = ["uv", "python", "uninstall", version]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to remove Python {version}: {e.stderr}") from e

    def list_installed(self) -> list[str]:
        """List installed Python versions.

        Returns:
            List of installed Python version strings

        Raises:
            RuntimeError: If listing fails
        """
        try:
            cmd = ["uv", "python", "list"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Parse the output - look for lines that have actual paths (not <download available>)
            versions = []
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line and "<download available>" not in line:
                    # Extract version from format like "cpython-3.13.5-macos-aarch64-none"
                    parts = line.split()
                    if len(parts) >= 2:
                        version_part = parts[0]
                        # Extract just the version number (e.g., "3.13.5" from "cpython-3.13.5-macos-aarch64-none")
                        if "cpython-" in version_part:
                            try:
                                version = version_part.split("-")[1]
                                # Only include if it looks like a valid version (x.y.z or x.y)
                                if "." in version and all(
                                    part.isdigit() for part in version.split(".")
                                ):
                                    versions.append(version)
                            except (IndexError, ValueError):
                                continue

            # Remove duplicates and sort
            return sorted(
                list(set(versions)), key=lambda v: [int(x) for x in v.split(".")]
            )

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to list Python versions: {e.stderr}") from e

    def list_available(self) -> list[str]:
        """List available Python versions for installation.

        Returns:
            List of available Python versions

        Raises:
            RuntimeError: If listing fails
        """
        try:
            cmd = ["uv", "python", "list"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Parse all versions (both installed and available)
            versions = []
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line:
                    # Extract version from format like "cpython-3.13.5-macos-aarch64-none"
                    parts = line.split()
                    if len(parts) >= 1:
                        version_part = parts[0]
                        # Extract just the version number
                        if "cpython-" in version_part:
                            try:
                                version = version_part.split("-")[1]
                                # Only include if it looks like a valid version
                                if "." in version and all(
                                    part.isdigit() for part in version.split(".")
                                ):
                                    versions.append(version)
                            except (IndexError, ValueError):
                                continue

            # Remove duplicates and sort
            return sorted(set(versions), key=lambda v: [int(x) for x in v.split(".")])

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to list available Python versions: {e.stderr}"
            ) from e

    def get_version_info(self, version: str) -> dict[str, str | bool | None]:
        """Get detailed information about a Python version.

        Args:
            version: Python version to get info for

        Returns:
            Dictionary with version information

        Raises:
            RuntimeError: If getting info fails
        """
        try:
            # Check if version is installed
            installed_versions = self.list_installed()

            if version in installed_versions:
                return {
                    "version": version,
                    "installed": True,
                    "path": self.get_python_path(version),
                }

            return {"version": version, "installed": False, "path": None}
        except Exception as e:
            raise RuntimeError(f"Failed to get info for Python {version}: {e}") from e

    def get_python_path(self, version: str) -> str:
        """Get the path to a specific Python version.

        Args:
            version: Python version to get path for

        Returns:
            Path to the Python executable

        Raises:
            RuntimeError: If version not found or getting path fails
        """
        try:
            cmd = ["uv", "python", "list"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Look for the specific version
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line and "<download available>" not in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        version_part = parts[0]
                        path_part = " ".join(parts[1:])

                        # Extract version number from version_part
                        if "cpython-" in version_part:
                            try:
                                extracted_version = version_part.split("-")[1]
                                if extracted_version == version:
                                    return path_part
                            except (IndexError, ValueError):
                                continue

            raise RuntimeError(f"Python {version} not found or not installed")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get Python path: {e.stderr}") from e
