"""Azure DevOps package feed authentication setup for uvve."""

from __future__ import annotations

import os
import subprocess
import toml
from pathlib import Path


class AzureManager:
    """Manages Azure DevOps package feed authentication setup."""

    def __init__(self) -> None:
        """Initialize the Azure manager."""
        self.uv_config_dir = Path.home() / ".config" / "uv"
        self.uv_config_file = self.uv_config_dir / "uv.toml"

    def _install_keyring_packages(
        self, env_name: str | None = None
    ) -> tuple[bool, str]:
        """Install required keyring packages.

        Args:
            env_name: Name of the virtual environment to install into.
                     If None, attempts to install system-wide.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if env_name:
                # Install into specific virtual environment
                from uvve.core.paths import PathManager

                path_manager = PathManager()

                if not path_manager.environment_exists(env_name):
                    return False, f"Environment '{env_name}' does not exist"

                env_path = path_manager.get_env_path(env_name)

                # Use uv pip install with the virtual environment
                python_path = str(env_path / "bin" / "python")
                subprocess.run(
                    [
                        "uv",
                        "pip",
                        "install",
                        "--python",
                        python_path,
                        "keyring",
                        "artifacts-keyring",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            else:
                # Install system-wide (fallback)
                subprocess.run(
                    [
                        "uv",
                        "pip",
                        "install",
                        "--system",
                        "keyring",
                        "artifacts-keyring",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )

            return True, ""
        except subprocess.CalledProcessError as e:
            error_msg = (
                f"Failed to install keyring packages: "
                f"{e.stderr if e.stderr else e.stdout}"
            )
            return False, error_msg
        except FileNotFoundError:
            return False, "uv command not found. Please ensure uv is installed."

    def setup_azure_feed(
        self,
        feed_url: str,
        feed_name: str = "private-registry",
        env_name: str | None = None,
    ) -> None:
        """Set up Azure DevOps package feed authentication.

        Args:
            feed_url: The Azure DevOps artifact feed URL
            feed_name: Name for the private registry (default: "private-registry")
            env_name: Name of virtual environment to install keyring packages into

        Raises:
            RuntimeError: If setup fails
        """
        try:
            # Install required keyring packages first
            success, error_msg = self._install_keyring_packages(env_name)
            if not success:
                raise RuntimeError(f"Failed to install keyring packages: {error_msg}")

            # Ensure uv config directory exists
            self.uv_config_dir.mkdir(parents=True, exist_ok=True)

            # Load existing config or create new one
            config = self._load_uv_config()

            # Add or update the index entry
            self._add_index_to_config(config, feed_name, feed_url)

            # Save the updated config
            self._save_uv_config(config)

            # Set environment variables
            self._setup_environment_variables(feed_name)

        except Exception as e:
            raise RuntimeError(f"Failed to setup Azure feed: {e}") from e

    def _load_uv_config(self) -> dict[str, any]:
        """Load existing uv.toml configuration.

        Returns:
            Dictionary containing the current configuration
        """
        if self.uv_config_file.exists():
            try:
                with open(self.uv_config_file) as f:
                    return toml.load(f)
            except Exception:
                # If loading fails, start with empty config
                return {}
        return {}

    def _add_index_to_config(self, config: dict[str, any], name: str, url: str) -> None:
        """Add index configuration to the config dictionary.

        Args:
            config: Configuration dictionary to modify
            name: Registry name
            url: Registry URL
        """
        # Initialize index array if it doesn't exist
        if "index" not in config:
            config["index"] = []

        # Always ensure PyPI is included as the primary index
        pypi_exists = any(
            index.get("url") == "https://pypi.org/simple/" for index in config["index"]
        )

        if not pypi_exists:
            config["index"].insert(
                0, {"name": "pypi", "url": "https://pypi.org/simple/"}
            )

        # Check if registry already exists and update it
        existing_index = None
        for i, index in enumerate(config["index"]):
            if index.get("name") == name:
                existing_index = i
                break

        index_entry = {"name": name, "url": url}

        if existing_index is not None:
            # Update existing entry
            config["index"][existing_index] = index_entry
        else:
            # Add new entry
            config["index"].append(index_entry)

    def _save_uv_config(self, config: dict[str, any]) -> None:
        """Save configuration to uv.toml file.

        Args:
            config: Configuration dictionary to save
        """
        with open(self.uv_config_file, "w") as f:
            toml.dump(config, f)

    def _setup_environment_variables(self, feed_name: str) -> None:
        """Set up environment variables for Azure authentication.

        Args:
            feed_name: Name of the feed for environment variable naming
        """
        # Set keyring provider
        os.environ["UV_KEYRING_PROVIDER"] = "subprocess"

        # Set username for the private registry
        username_var = f"UV_INDEX_{feed_name.upper().replace('-', '_')}_USERNAME"
        os.environ[username_var] = "VssSessionToken"

    def get_status(self) -> dict[str, any]:
        """Get current Azure feed configuration status.

        Returns:
            Dictionary containing configuration status
        """
        status = {
            "config_file_exists": self.uv_config_file.exists(),
            "config_file_path": str(self.uv_config_file),
            "keyring_provider": os.environ.get("UV_KEYRING_PROVIDER"),
            "configured_indexes": [],
        }

        if status["config_file_exists"]:
            try:
                config = self._load_uv_config()
                if "index" in config:
                    status["configured_indexes"] = config["index"]
            except Exception:
                status["config_load_error"] = True

        # Check for Azure-related environment variables
        azure_env_vars = {}
        for key, value in os.environ.items():
            if key.startswith("UV_INDEX_") and key.endswith("_USERNAME"):
                azure_env_vars[key] = value
        status["azure_env_vars"] = azure_env_vars

        return status

    def remove_azure_feed(self, feed_name: str = "private-registry") -> None:
        """Remove Azure feed configuration.

        Args:
            feed_name: Name of the feed to remove
        """
        if not self.uv_config_file.exists():
            return

        try:
            config = self._load_uv_config()

            # Remove the index entry
            if "index" in config:
                config["index"] = [
                    index for index in config["index"] if index.get("name") != feed_name
                ]

                # If no indexes left, remove the entire index section
                if not config["index"]:
                    del config["index"]

            # Save updated config
            self._save_uv_config(config)

            # Clean up environment variables
            username_var = f"UV_INDEX_{feed_name.upper().replace('-', '_')}_USERNAME"
            os.environ.pop(username_var, None)

        except Exception as e:
            raise RuntimeError(f"Failed to remove Azure feed: {e}") from e

    def validate_feed_url(self, url: str) -> bool:
        """Validate if the URL looks like an Azure DevOps feed URL.

        Args:
            url: URL to validate

        Returns:
            True if URL appears to be a valid Azure DevOps feed URL
        """
        # Basic validation for Azure DevOps package feed URLs
        azure_patterns = [
            "pkgs.dev.azure.com",
            "feeds.dev.azure.com",
            ".pkgs.visualstudio.com",
            ".feeds.visualstudio.com",
        ]

        return any(pattern in url.lower() for pattern in azure_patterns)

    def get_shell_setup_commands(
        self, feed_name: str = "private-registry"
    ) -> dict[str, str]:
        """Get shell commands to set up environment variables.

        Args:
            feed_name: Name of the feed

        Returns:
            Dictionary with shell commands for different shells
        """
        username_var = f"UV_INDEX_{feed_name.upper().replace('-', '_')}_USERNAME"

        return {
            "bash": f"""# Add to ~/.bashrc or ~/.bash_profile
export UV_KEYRING_PROVIDER=subprocess
export {username_var}=VssSessionToken""",
            "zsh": f"""# Add to ~/.zshrc
export UV_KEYRING_PROVIDER=subprocess
export {username_var}=VssSessionToken""",
            "fish": f"""# Add to ~/.config/fish/config.fish
set -gx UV_KEYRING_PROVIDER subprocess
set -gx {username_var} VssSessionToken""",
            "powershell": f"""# Add to PowerShell profile
$env:UV_KEYRING_PROVIDER = "subprocess"
$env:{username_var} = "VssSessionToken\"""",
        }
