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
app.command("remove")(environment.remove)
app.command("local")(environment.local)
app.command("list")(environment.env_list)

# Register package commands
app.command("add")(packages.add)
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
        
        if not typer.confirm(
            f"Are you sure you want to remove Python {version}?"
        ):
            console.print("[yellow]Removal cancelled[/yellow]")
            return
        
        python_manager.remove(version)
        console.print(f"[green]✓[/green] Python {version} removed successfully")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to remove Python {version}: {e}")
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
