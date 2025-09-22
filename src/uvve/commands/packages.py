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
    env_name: str | None = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment name (auto-detected if not provided)",
        autocompletion=complete_environment_names,
    ),
) -> None:
    """Add packages to a uvve environment."""
    try:
        env_manager = EnvironmentManager()

        # Determine which environment to use
        if env_name:
            target_env = env_name
        else:
            # Try to auto-detect current environment
            current_env = env_manager.get_current_environment()
            if not current_env:
                console.print("[red]✗[/red] No uvve environment is currently active")
                console.print(
                    "Either activate an environment with: [cyan]uvve activate <env_name>[/cyan]"
                )
                console.print(
                    "Or specify environment with: [cyan]uvve add --env <env_name> <packages>[/cyan]"
                )
                raise typer.Exit(1)
            target_env = current_env

        console.print(
            f"[blue]Adding packages to environment '{target_env}'...[/blue]"
        )

        # Install packages using uv pip install
        freeze_manager = FreezeManager()
        freeze_manager.add_packages(target_env, packages)

        package_list = ", ".join(packages)
        console.print(f"[green]✓[/green] Successfully added packages: {package_list}")
        console.print(f"[dim]Environment: {target_env}[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to add packages: {e}")
        raise typer.Exit(1) from None

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to add packages: {e}")
        raise typer.Exit(1) from None


def lock(
    name: str | None = typer.Argument(
        None,
        help="Name of the virtual environment (auto-detected if not provided)",
        autocompletion=complete_environment_names,
    ),
) -> None:
    """Generate a lockfile for the environment."""
    try:
        env_manager = EnvironmentManager()

        # Determine which environment to use
        if name:
            target_env = name
        else:
            # Try to auto-detect current environment
            current_env = env_manager.get_current_environment()
            if not current_env:
                console.print("[red]✗[/red] No uvve environment is currently active")
                console.print(
                    "Either activate an environment with: [cyan]uvve activate <env_name>[/cyan]"
                )
                console.print(
                    "Or specify environment with: [cyan]uvve lock <env_name>[/cyan]"
                )
                raise typer.Exit(1)
            target_env = current_env

        console.print(
            f"[green]Generating lockfile for environment '{target_env}'...[/green]"
        )
        freeze_manager = FreezeManager()
        freeze_manager.lock(target_env)
        console.print(f"[green]✓[/green] Lockfile generated for '{target_env}'")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to generate lockfile: {e}")
        raise typer.Exit(1) from None


def freeze(
    name: str | None = typer.Argument(
        None,
        help="Name of the virtual environment (auto-detected if not provided)",
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
        env_manager = EnvironmentManager()

        # Determine which environment to use
        if name:
            target_env = name
        else:
            # Try to auto-detect current environment
            current_env = env_manager.get_current_environment()
            if not current_env:
                console.print("[red]✗[/red] No uvve environment is currently active")
                console.print(
                    "Either activate an environment with: [cyan]uvve activate <env_name>[/cyan]"
                )
                console.print(
                    "Or specify environment with: [cyan]uvve freeze <env_name>[/cyan]"
                )
                raise typer.Exit(1)
            target_env = current_env

        freeze_manager = FreezeManager()
        if tracked_only:
            # Show only tracked packages (added via uvve add)
            packages = freeze_manager.get_tracked_packages(target_env)
            if not packages:
                console.print(
                    f"[yellow]No tracked packages found for environment '{target_env}'[/yellow]"
                )
                console.print("Use [cyan]uvve add <package>[/cyan] to add packages")
                return

            console.print(f"[bold cyan]Tracked packages in '{target_env}':[/bold cyan]")
            for package in packages:
                console.print(f"  {package}")
        else:
            # Show all installed packages
            console.print(
                f"[blue]Getting installed packages for environment '{target_env}'...[/blue]"
            )
            freeze_manager.show_installed_packages(target_env)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to show packages: {e}")
        raise typer.Exit(1) from None


def thaw(
    name: str | None = typer.Argument(
        None,
        help="Name of the virtual environment (auto-detected if not provided)",
        autocompletion=complete_environment_names,
    ),
) -> None:
    """Rebuild environment from lockfile."""
    try:
        env_manager = EnvironmentManager()

        # Determine which environment to use
        if name:
            target_env = name
        else:
            # Try to auto-detect current environment
            current_env = env_manager.get_current_environment()
            if not current_env:
                console.print("[red]✗[/red] No uvve environment is currently active")
                console.print(
                    "Either activate an environment with: [cyan]uvve activate <env_name>[/cyan]"
                )
                console.print(
                    "Or specify environment with: [cyan]uvve thaw <env_name>[/cyan]"
                )
                raise typer.Exit(1)
            target_env = current_env

        console.print(
            f"[green]Rebuilding environment '{target_env}' from lockfile...[/green]"
        )
        freeze_manager = FreezeManager()
        freeze_manager.thaw(target_env)
        console.print(
            f"[green]✓[/green] Environment '{target_env}' rebuilt from lockfile"
        )

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to rebuild environment: {e}")
        raise typer.Exit(1) from None


def remove(
    packages: list[str] = typer.Argument(
        ...,
        help="Package names to remove (e.g., 'requests' or 'django')",
    ),
    env_name: str | None = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment name (auto-detected if not provided)",
        autocompletion=complete_environment_names,
    ),
) -> None:
    """Remove packages from a uvve environment."""
    try:
        env_manager = EnvironmentManager()

        # Determine which environment to use
        if env_name:
            target_env = env_name
        else:
            # Try to auto-detect current environment
            current_env = env_manager.get_current_environment()
            if not current_env:
                console.print("[red]✗[/red] No uvve environment is currently active")
                console.print(
                    "Either activate an environment with: [cyan]uvve activate <env_name>[/cyan]"
                )
                console.print(
                    "Or specify environment with: [cyan]uvve remove --env <env_name> <packages>[/cyan]"
                )
                raise typer.Exit(1)
            target_env = current_env

        console.print(
            f"[blue]Removing packages from environment '{target_env}'...[/blue]"
        )

        # Remove packages using FreezeManager
        freeze_manager = FreezeManager()
        freeze_manager.remove_packages(target_env, packages)

        package_list = ", ".join(packages)
        console.print(f"[green]✓[/green] Successfully removed packages: {package_list}")
        console.print(f"[dim]Environment: {target_env}[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to remove packages: {e}")
        raise typer.Exit(1) from None
