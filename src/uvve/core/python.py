"""Python version management for uvve."""

import subprocess
from typing import List, Dict, Any


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

    def list_installed(self) -> List[Dict[str, Any]]:
        """List installed Python versions.

        Returns:
            List of dictionaries with Python version info

        Raises:
            RuntimeError: If listing fails
        """
        try:
            cmd = ["uv", "python", "list"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Parse the output (this is a simplified parser)
            versions = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    # This would need more sophisticated parsing in real implementation
                    parts = line.split()
                    if len(parts) >= 2:
                        versions.append(
                            {
                                "version": parts[0],
                                "path": " ".join(parts[1:])
                                if len(parts) > 1
                                else "unknown",
                            }
                        )

            return versions
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to list Python versions: {e.stderr}") from e

    def list_available(self) -> List[str]:
        """List available Python versions for installation.

        Returns:
            List of available Python versions

        Raises:
            RuntimeError: If listing fails
        """
        try:
            cmd = ["uv", "python", "list", "--only-installed", "false"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Parse available versions
            versions = []
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("*"):
                    # Extract version number (simplified parsing)
                    version = line.split()[0]
                    if version:
                        versions.append(version)

            return versions
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to list available Python versions: {e.stderr}"
            ) from e

    def get_version_info(self, version: str) -> Dict[str, Any]:
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

            for installed in installed_versions:
                if installed["version"] == version:
                    return {
                        "version": version,
                        "installed": True,
                        "path": installed["path"],
                    }

            return {"version": version, "installed": False, "path": None}
        except Exception as e:
            raise RuntimeError(f"Failed to get info for Python {version}: {e}") from e
