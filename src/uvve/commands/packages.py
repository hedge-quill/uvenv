"""Package management commands."""

import typer
from rich.console import Console

from uvve.core.freeze import FreezeManager
from uvve.core.manager import EnvironmentManager

console = Console()


def complete_environment_names(incomplete: str) -> list[str]:
    """Auto-completion for environment names."""
    try:
        manager = EnvironmentManager()
        envs = manager.list()
        return [env["name"] for env in envs if env["name"].startswith(incomplete)]
    except Exception:
        return []


def add(
    packages: list[str] = typer.Argument(
        ...,
        help="Package names to install (e.g., 'requests' or 'django==4.2')",
    ),
) -> None:
    """Add packages to the currently active uvve environment."""
    try:
        # Check if a uvve environment is currently active
        env_manager = EnvironmentManager()
        current_env = env_manager.get_current_environment()

        if not current_env:
            console.print("[red]✗[/red] No uvve environment is currently active")
            console.print(
                "Activate an environment first with: [cyan]uvve activate <env_name>[/cyan]"
            )
            raise typer.Exit(1)

        console.print(
            f"[blue]Installing packages to environment '{current_env}'...[/blue]"
        )

        # Install packages using uv pip install
        freeze_manager = FreezeManager()
        freeze_manager.add_packages(current_env, packages)

        package_list = ", ".join(packages)
        console.print(f"[green]✓[/green] Successfully added packages: {package_list}")
        console.print(f"[dim]Environment: {current_env}[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to add packages: {e}")
        raise typer.Exit(1) from None


def lock(
    name: str = typer.Argument(
        ...,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
) -> None:
    """Generate a lockfile for the environment."""
    console.print(f"[green]Generating lockfile for environment '{name}'...[/green]")
    try:
        freeze_manager = FreezeManager()
        freeze_manager.lock(name)
        console.print(f"[green]✓[/green] Lockfile generated for '{name}'")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to generate lockfile for '{name}': {e}")
        raise typer.Exit(1) from None


def freeze(
    name: str = typer.Argument(
        ...,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
    tracked_only: bool = typer.Option(
        False,
        "--tracked-only",
        help="Show only packages added via 'uvve add'",
    ),
) -> None:
    """Show installed packages in the environment."""
    try:
        freeze_manager = FreezeManager()
        if tracked_only:
            # Show only tracked packages (added via uvve add)
            packages = freeze_manager.get_tracked_packages(name)
            if not packages:
                console.print(
                    f"[yellow]No tracked packages found for environment '{name}'[/yellow]"
                )
                console.print("Use [cyan]uvve add <package>[/cyan] to add packages")
                return

            console.print(f"[bold cyan]Tracked packages in '{name}':[/bold cyan]")
            for package in packages:
                console.print(f"  {package}")
        else:
            # Show all installed packages
            console.print(
                f"[blue]Getting installed packages for environment '{name}'...[/blue]"
            )
            freeze_manager.show_installed_packages(name)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to show packages: {e}")
        raise typer.Exit(1) from None


def thaw(
    name: str = typer.Argument(
        ...,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
) -> None:
    """Rebuild environment from lockfile."""
    console.print(f"[green]Rebuilding environment '{name}' from lockfile...[/green]")
    try:
        freeze_manager = FreezeManager()
        freeze_manager.thaw(name)
        console.print(f"[green]✓[/green] Environment '{name}' rebuilt from lockfile")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to rebuild environment '{name}': {e}")
        raise typer.Exit(1) from None
