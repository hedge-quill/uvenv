"""CLI entrypoint for uvve using Typer."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from uvve import __version__
from uvve.commands import analytics, azure, environment, maintenance, packages, shell
from uvve.core.python import PythonManager

console = Console()


def version_callback(value: bool) -> None:
    """Handle version option."""
    if value:
        console.print(f"uvve version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="uvve",
    help="A CLI tool for managing Python virtual environments using uv",
    rich_markup_mode="rich",
)

# Create Python command group
python_app = typer.Typer(
    name="python",
    help="Manage Python versions",
    rich_markup_mode="rich",
)
app.add_typer(python_app, name="python")


@app.callback()
def main_callback(
    _version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """A CLI tool for managing Python virtual environments using uv."""
    pass


# Register environment commands
app.command("create")(environment.create)
app.command("activate")(environment.activate)
app.command("delete")(environment.delete)
app.command("local")(environment.local)
app.command("list")(environment.env_list)

# Package commands
app.command("add")(packages.add)
app.command("remove")(packages.remove)
app.command("lock")(packages.lock)
app.command("freeze")(packages.freeze)
app.command("thaw")(packages.thaw)

# Register analytics commands
app.command("status")(analytics.status)
app.command("analytics")(analytics.analytics)

# Register maintenance commands
app.command("edit")(maintenance.edit)
app.command("cleanup")(maintenance.cleanup)

# Register Azure commands
azure_app = typer.Typer(
    name="azure",
    help="Azure integration commands",
    rich_markup_mode="rich",
)
azure_app.command("login")(azure.azure_login)
azure_app.command("logout")(azure.azure_logout)
azure_app.command("subscription")(azure.azure_subscription)
azure_app.command("account")(azure.azure_account)
app.add_typer(azure_app, name="azure")

# Register shell commands
shell_app = typer.Typer(
    name="shell",
    help="Shell integration commands",
    rich_markup_mode="rich",
)
shell_app.command("activate")(shell.activate)
shell_app.command("completion")(shell.completion)
app.add_typer(shell_app, name="shell")


# Python management commands
def complete_python_versions(incomplete: str) -> list[str]:
    """Auto-completion for Python versions."""
    try:
        python_manager = PythonManager()
        versions = python_manager.list_available()
        return [v for v in versions if v.startswith(incomplete)]
    except Exception:
        return []


@python_app.command("list")
def python_list() -> None:
    """List available Python versions."""
    try:
        python_manager = PythonManager()
        available_versions = python_manager.list_available()
        installed_versions = python_manager.list_installed()

        if not available_versions:
            console.print("[yellow]No Python versions found[/yellow]")
            return

        # Create table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Version", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Path", style="dim")

        for version in available_versions:
            if version in installed_versions:
                status = "✓ Installed"
                path = python_manager.get_python_path(version)
            else:
                status = "Available"
                path = "-"

            table.add_row(version, status, path)

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list Python versions: {e}")
        raise typer.Exit(1) from None


@python_app.command("install")
def python_install(
    version: str = typer.Argument(
        ...,
        help="Python version to install",
        autocompletion=complete_python_versions,
    ),
) -> None:
    """Install a Python version."""
    try:
        python_manager = PythonManager()

        with console.status(f"[bold blue]Installing Python {version}..."):
            python_manager.install(version)

        console.print(f"[green]✓[/green] Python {version} installed successfully")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to install Python {version}: {e}")
        raise typer.Exit(1) from None


@python_app.command("remove")
def python_remove(
    version: str = typer.Argument(
        ...,
        help="Python version to remove",
        autocompletion=complete_python_versions,
    ),
) -> None:
    """Remove a Python version."""
    try:
        python_manager = PythonManager()

        if not typer.confirm(f"Are you sure you want to remove Python {version}?"):
            console.print("[yellow]Removal cancelled[/yellow]")
            return

        python_manager.remove(version)
        console.print(f"[green]✓[/green] Python {version} removed successfully")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to remove Python {version}: {e}")
        raise typer.Exit(1) from None


def complete_environment_names(incomplete: str) -> list[str]:
    """Auto-completion for environment names."""
    try:
        from uvve.core.manager import EnvironmentManager

        env_manager = EnvironmentManager()
        environments = env_manager.list()
        return [
            env["name"] for env in environments if env["name"].startswith(incomplete)
        ]
    except Exception:
        return []


@python_app.command("bump")
def python_bump(
    new_version: str = typer.Argument(
        ...,
        help="Target Python version (e.g., '3.13.5')",
        autocompletion=complete_python_versions,
    ),
    env_name: str | None = typer.Argument(
        None,
        help="Environment name (auto-detected if not provided)",
        autocompletion=complete_environment_names,
    ),
) -> None:
    """Bump the Python version of a virtual environment."""
    try:
        from uvve.core.manager import EnvironmentManager
        from uvve.core.freeze import FreezeManager

        env_manager = EnvironmentManager()
        freeze_manager = FreezeManager()
        python_manager = PythonManager()

        # Determine which environment to bump
        if env_name:
            # Use specified environment
            target_env = env_name
            if not env_manager.path_manager.environment_exists(target_env):
                console.print(
                    f"[red]✗[/red] Environment '{target_env}' does not exist."
                )
                raise typer.Exit(1)
        else:
            # Auto-detect current environment
            target_env = env_manager.get_current_environment()
            if not target_env:
                console.print("[red]✗[/red] No uvve environment is currently active.")
                console.print(
                    "Either activate an environment with: [cyan]uvve activate <env_name>[/cyan]"
                )
                console.print(
                    "Or specify environment with: [cyan]uvve python bump <version> <env_name>[/cyan]"
                )
                raise typer.Exit(1)

        # Check if target Python version is available
        available_versions = python_manager.list_available()
        if new_version not in available_versions:
            console.print(f"[red]✗[/red] Python {new_version} is not available.")
            console.print("Available versions:")
            for version in available_versions[-10:]:  # Show last 10 versions
                console.print(f"  - {version}")
            raise typer.Exit(1)

        # Get current environment metadata to check current Python version
        current_metadata = env_manager.get_metadata(target_env)
        current_python = current_metadata.get("python_version", "unknown")

        if current_python == new_version:
            console.print(
                f"[yellow]Environment '{target_env}' is already using Python {new_version}[/yellow]"
            )
            return

        console.print(
            f"[blue]Bumping environment '{target_env}' from Python {current_python} to {new_version}...[/blue]"
        )

        # Create a temporary lockfile to preserve dependencies
        temp_env_name = f"{target_env}_bump_temp"

        # Step 1: Create lockfile from current environment
        console.print("[dim]1. Creating lockfile from current environment...[/dim]")
        freeze_manager.lock(target_env)

        # Step 2: Create temporary environment with new Python version
        console.print(
            f"[dim]2. Creating temporary environment with Python {new_version}...[/dim]"
        )
        env_manager.create(
            name=temp_env_name,
            python_version=new_version,
            description=current_metadata.get("description", ""),
            tags=current_metadata.get("tags", []),
        )

        # Step 3: Restore dependencies to temporary environment
        console.print("[dim]3. Restoring dependencies...[/dim]")
        # Copy the lockfile from the source to the temp environment so thaw can find it
        import shutil as shutil_module

        source_lockfile = freeze_manager.path_manager.get_lockfile_path(target_env)
        temp_lockfile = freeze_manager.path_manager.get_lockfile_path(temp_env_name)
        if source_lockfile.exists():
            shutil_module.copy2(source_lockfile, temp_lockfile)
            freeze_manager.thaw(temp_env_name)

        # Step 4: Remove old environment
        console.print("[dim]4. Removing old environment...[/dim]")
        env_manager.remove(target_env)

        # Step 5: Rename temporary environment to original name
        console.print("[dim]5. Renaming temporary environment...[/dim]")
        import shutil

        temp_path = env_manager.path_manager.get_env_path(temp_env_name)
        target_path = env_manager.path_manager.get_env_path(target_env)
        shutil.move(str(temp_path), str(target_path))

        # Update metadata with new Python version
        env_manager._create_metadata(
            name=target_env,
            python_version=new_version,
            description=current_metadata.get("description", ""),
            tags=current_metadata.get("tags", []),
        )

        console.print(
            f"[green]✓[/green] Environment '{target_env}' successfully bumped to Python {new_version}"
        )
        console.print(f"Activate with: [cyan]uvve activate {target_env}[/cyan]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to bump Python version: {e}")
        # Clean up temporary environment if it exists
        try:
            temp_env_name = f"{target_env}_bump_temp"
            if env_manager.path_manager.environment_exists(temp_env_name):
                env_manager.remove(temp_env_name)
        except:
            pass
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
