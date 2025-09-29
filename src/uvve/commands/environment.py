"""Environment management commands."""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from uvve.core.manager import EnvironmentManager
from uvve.shell.activate import ActivationManager

console = Console()


def complete_environment_names(incomplete: str) -> list[str]:
    """Auto-completion for environment names."""
    try:
        manager = EnvironmentManager()
        envs = manager.list()
        return [env["name"] for env in envs if env["name"].startswith(incomplete)]
    except Exception:
        return []


def env_list(
    usage: bool = typer.Option(
        False,
        "--usage",
        help="Show usage statistics for environments",
    ),
) -> None:
    """List all virtual environments."""
    try:
        env_manager = EnvironmentManager()
        envs = env_manager.list()

        if not envs:
            console.print("[yellow]No virtual environments found[/yellow]")
            console.print(
                "Create one with: [cyan]uvve create <name> <python_version>[/cyan]"
            )
            return

        # Create table
        if usage:
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Python Version", style="green")
            table.add_column("Path", style="dim")
            table.add_column("Last Used", style="yellow")
            table.add_column("Days Ago", style="magenta", justify="right")
            table.add_column("Size", style="blue", justify="right")
        else:
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Python Version", style="green")
            table.add_column("Path", style="dim")
            table.add_column("Status", style="yellow")

        # Add environments to table
        for env in envs:
            if usage:
                if env.get("last_used"):
                    last_used = env["last_used"].strftime("%Y-%m-%d %H:%M")
                    days_ago = str(env.get("days_since_used", "N/A"))
                else:
                    last_used = "Never"
                    days_ago = "N/A"

                size = env.get("size", "Unknown")
                table.add_row(
                    env["name"],
                    env["python_version"],
                    env["path"],
                    last_used,
                    days_ago,
                    size,
                )
            else:
                status = env.get("status", "unknown")
                table.add_row(
                    env["name"],
                    env["python_version"],
                    env["path"],
                    status,
                )

        # Show table
        title = "Virtual Environments" + (" (with Usage)" if usage else "")
        console.print(f"[bold blue]{title}[/bold blue]")
        console.print(table)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list environments: {e}")
        raise typer.Exit(1) from None


def create(
    name: str = typer.Argument(..., help="Name of the virtual environment"),
    python_version: str = typer.Argument(
        ..., help="Python version (e.g., '3.11', '3.12')"
    ),
    description: str | None = typer.Option(
        None,
        "--description",
        "-d",
        help="Description of the environment",
    ),
    add_tag: list[str] | None = typer.Option(
        None,
        "--add-tag",
        "-t",
        help="Add a tag to the environment (can be used multiple times)",
    ),
) -> None:
    """Create a virtual environment with optional metadata."""
    if add_tag is None:
        add_tag = []

    try:
        env_manager = EnvironmentManager()
        env_manager.create(
            name=name,
            python_version=python_version,
            description=description,
            tags=add_tag,
        )
        console.print(f"[green]✓[/green] Environment '{name}' created successfully")
        console.print(f"[dim]Python version: {python_version}[/dim]")
        if description:
            console.print(f"[dim]Description: {description}[/dim]")
        if add_tag:
            console.print(f"[dim]Tags: {', '.join(add_tag)}[/dim]")
        console.print(f"\nActivate with: [cyan]uvve activate {name}[/cyan]")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create environment '{name}': {e}")
        raise typer.Exit(1) from None


def activate(
    name: str = typer.Argument(
        ...,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
) -> None:
    """Activate environment (with shell integration) or print activation snippet."""
    try:
        activation_manager = ActivationManager()
        activation_script = activation_manager.get_activation_script(name)
        console.print(activation_script, end="")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to activate environment '{name}': {e}")
        raise typer.Exit(1) from None


def delete(
    name: str = typer.Argument(
        ...,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
) -> None:
    """Delete a virtual environment."""
    try:
        env_manager = EnvironmentManager()
        env_manager.remove(name)
        console.print(f"[green]✓[/green] Environment '{name}' deleted successfully")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to delete environment '{name}': {e}")
        raise typer.Exit(1) from None


def local(
    env_name: str = typer.Argument(..., help="Name of the environment to use locally"),
) -> None:
    """Create a .uvve-version file to auto-activate environment in this directory."""
    try:
        env_manager = EnvironmentManager()

        # Check if environment exists
        if not env_manager.path_manager.environment_exists(env_name):
            console.print(f"[red]✗[/red] Environment '{env_name}' does not exist")
            console.print("Run [cyan]uvve list[/cyan] to see available environments")
            raise typer.Exit(1)

        # Create .uvve-version file in current directory
        version_file = Path.cwd() / ".uvve-version"

        try:
            version_file.write_text(env_name + "\n")
            console.print(
                f"[green]✓[/green] Created .uvve-version file with environment '{env_name}'"
            )
            console.print(f"[dim]Location: {version_file}[/dim]")

            # Check if shell integration is available
            if hasattr(ActivationManager, "has_shell_integration"):
                console.print(
                    "\n[yellow]💡 Tip:[/yellow] Make sure you have uvve shell integration installed for auto-activation:"
                )
                console.print(
                    "  [cyan]uvve shell-integration >> ~/.zshrc && source ~/.zshrc[/cyan]"
                )

        except PermissionError:
            console.print(f"[red]✗[/red] Permission denied writing to {version_file}")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to create .uvve-version file: {e}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to set local environment: {e}")
        raise typer.Exit(1) from None
