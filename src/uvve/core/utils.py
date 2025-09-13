"""Utility functions for uvve."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def run_command(
    cmd: list[str], cwd: Optional[Path] = None
) -> subprocess.CompletedProcess:
    """Run a command and return the result.

    Args:
        cmd: Command and arguments to run
        cwd: Working directory for the command

    Returns:
        CompletedProcess instance

    Raises:
        RuntimeError: If command fails
    """
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{e.stderr}") from e


def check_uv_available() -> bool:
    """Check if uv is available in PATH.

    Returns:
        True if uv is available, False otherwise
    """
    return shutil.which("uv") is not None


def ensure_uv_available() -> None:
    """Ensure uv is available, raise error if not.

    Raises:
        RuntimeError: If uv is not available
    """
    if not check_uv_available():
        raise RuntimeError(
            "uv is not available in PATH. Please install it first:\n"
            "curl -LsSf https://astral.sh/uv/install.sh | sh"
        )


def validate_environment_name(name: str) -> None:
    """Validate environment name.

    Args:
        name: Environment name to validate

    Raises:
        ValueError: If name is invalid
    """
    if not name:
        raise ValueError("Environment name cannot be empty")

    if not name.replace("-", "").replace("_", "").replace(".", "").isalnum():
        raise ValueError(
            "Environment name can only contain letters, numbers, hyphens, "
            "underscores, and periods"
        )

    if name.startswith("."):
        raise ValueError("Environment name cannot start with a period")


def validate_python_version(version: str) -> None:
    """Validate Python version string.

    Args:
        version: Python version to validate

    Raises:
        ValueError: If version is invalid
    """
    if not version:
        raise ValueError("Python version cannot be empty")

    # Basic version format validation
    parts = version.split(".")
    if len(parts) < 2 or len(parts) > 3:
        raise ValueError("Python version must be in format 'X.Y' or 'X.Y.Z'")

    try:
        major = int(parts[0])
        minor = int(parts[1])

        if major < 3:
            raise ValueError("Python 3.0+ is required")

        if len(parts) == 3:
            int(parts[2])  # Validate patch version is integer

    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError("Python version parts must be integers") from e
        raise


def get_terminal_width() -> int:
    """Get terminal width for formatting output.

    Returns:
        Terminal width in characters, defaults to 80
    """
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def format_table_row(columns: list[str], widths: list[int]) -> str:
    """Format a table row with proper column widths.

    Args:
        columns: Column values
        widths: Column widths

    Returns:
        Formatted row string
    """
    formatted_cols = []
    for col, width in zip(columns, widths):
        if len(col) > width:
            col = col[: width - 3] + "..."
        formatted_cols.append(col.ljust(width))

    return " | ".join(formatted_cols)
