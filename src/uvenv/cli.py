"""CLI entrypoint for uvenv using Typer."""

import typer
from rich.console import Console
from rich.table import Table

from uvenv import __version__
from uvenv.core.freeze import FreezeManager
from uvenv.core.manager import EnvironmentManager
from uvenv.core.python import PythonManager
from uvenv.shell.activate import ActivationManager

console = Console()


def version_callback(value: bool) -> None:
    """Handle version option."""
    if value:
        console.print(f"uvenv version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="uvenv",
    help="A CLI tool for managing Python virtual environments using uv",
    rich_markup_mode="rich",
)


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
    """Main callback for global options."""


# Initialize managers
env_manager = EnvironmentManager()
python_manager = PythonManager()
freeze_manager = FreezeManager()
activation_manager = ActivationManager()


def complete_environment_names() -> list[str]:
    """Provide completion for environment names."""
    try:
        environments = env_manager.list()
        return [env.get("name", "") for env in environments if env.get("name")]
    except Exception:
        # If there's an error, return empty list to avoid breaking completion
        return []


def complete_python_versions() -> list[str]:
    """Provide completion for Python versions."""
    try:
        # Get installed Python versions
        installed = python_manager.list_installed()
        versions = [v.get("version", "") for v in installed if v.get("version")]

        # Add some common versions for convenience
        common_versions = ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]

        # Combine and deduplicate
        all_versions = list(set(versions + common_versions))
        return sorted(all_versions, reverse=True)
    except Exception:
        # Fallback to common versions
        return ["3.12", "3.11", "3.10", "3.9", "3.8"]


# Create Python command group
python_app = typer.Typer(
    name="python",
    help="Manage Python versions",
    rich_markup_mode="rich",
)
app.add_typer(python_app, name="python")


@python_app.command()
def install(
    version: str = typer.Argument(..., help="Python version to install"),
) -> None:
    """Install a Python version using uv."""
    console.print(f"[green]Installing Python {version}...[/green]")
    try:
        python_manager.install(version)
        console.print(f"[green]✓[/green] Python {version} installed successfully")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to install Python {version}: {e}")
        raise typer.Exit(1) from None


@python_app.command(name="list")
def python_list() -> None:
    """List available and installed Python versions."""
    try:
        # Get installed versions
        installed = python_manager.list_installed()
        # Get available versions
        available = python_manager.list_available()

        if not installed and not available:
            console.print("[yellow]No Python versions found[/yellow]")
            return

        table = Table(title="Python Versions")
        table.add_column("Version", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Location", style="dim")

        # Track which versions we've already shown
        shown_versions = set()

        # First, show installed versions
        for version_info in installed:
            version = version_info.get("version", "unknown")
            location = version_info.get("executable", "unknown")
            table.add_row(version, "✓ Installed", location)
            shown_versions.add(version)

        # Then show available versions that aren't installed
        for version in available:
            if version not in shown_versions:
                table.add_row(version, "Available", "")

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list Python versions: {e}")
        raise typer.Exit(1) from None


@app.command()
def create(
    name: str = typer.Argument(..., help="Name of the virtual environment"),
    python_version: str = typer.Argument(
        ...,
        help="Python version for the environment",
        autocompletion=complete_python_versions,
    ),
) -> None:
    """Create a new virtual environment."""
    console.print(
        f"[green]Creating environment '{name}' with Python {python_version}...[/green]"
    )
    try:
        env_manager.create(name, python_version)
        console.print(f"[green]✓[/green] Environment '{name}' created successfully")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create environment '{name}': {e}")
        raise typer.Exit(1) from None


@app.command()
def activate(
    name: str = typer.Argument(
        ...,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
) -> None:
    """Print shell activation snippet for the environment."""
    try:
        activation_script = env_manager.get_activation_script(name)
        console.print(activation_script)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get activation script for '{name}': {e}")
        raise typer.Exit(1) from None


@app.command(name="list")
def env_list() -> None:
    """List all virtual environments."""
    try:
        environments = env_manager.list()
        if not environments:
            console.print("[yellow]No virtual environments found[/yellow]")
            return

        table = Table(title="Virtual Environments")
        table.add_column("Name", style="cyan")
        table.add_column("Python Version", style="green")
        table.add_column("Path", style="blue")
        table.add_column("Status", style="magenta")

        for env in environments:
            table.add_row(
                env["name"], env["python_version"], env["path"], env["status"]
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list environments: {e}")
        raise typer.Exit(1) from None


@app.command()
def remove(
    name: str = typer.Argument(
        ...,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force removal without confirmation"
    ),
) -> None:
    """Remove a virtual environment."""
    if not force:
        confirm = typer.confirm(
            f"Are you sure you want to remove environment '{name}'?"
        )
        if not confirm:
            console.print("[yellow]Operation cancelled[/yellow]")
            return

    try:
        env_manager.remove(name)
        console.print(f"[green]✓[/green] Environment '{name}' removed successfully")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to remove environment '{name}': {e}")
        raise typer.Exit(1) from None


@app.command()
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
        freeze_manager.lock(name)
        console.print(f"[green]✓[/green] Lockfile generated for '{name}'")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to generate lockfile for '{name}': {e}")
        raise typer.Exit(1) from None


@app.command()
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
        freeze_manager.thaw(name)
        console.print(f"[green]✓[/green] Environment '{name}' rebuilt from lockfile")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to rebuild environment '{name}': {e}")
        raise typer.Exit(1) from None


@app.command()
def shell_integration(
    shell: str = typer.Option(
        None,
        "--shell",
        help="Target shell (bash, zsh, fish, powershell). Auto-detected if not "
        "specified.",
    ),
    print_only: bool = typer.Option(
        False,
        "--print",
        help="Print integration script instead of installation instructions",
    ),
) -> None:
    """Install shell integration for uvenv.

    This enables 'uvenv activate <env>' to work directly without eval.
    """
    try:
        integration_script = activation_manager.generate_shell_integration(shell)

        if print_only:
            console.print(integration_script)
            return

        detected_shell = activation_manager._detect_shell() if shell is None else shell

        # Show installation instructions
        console.print(f"[green]Shell integration for {detected_shell}[/green]")
        console.print(
            "\n[yellow]Add the following to your shell configuration:[/yellow]"
        )

        if detected_shell in ("bash", "zsh"):
            config_file = "~/.bashrc" if detected_shell == "bash" else "~/.zshrc"
            console.print(f"\n[cyan]# Add to {config_file}[/cyan]")
        elif detected_shell == "fish":
            console.print("\n[cyan]# Add to ~/.config/fish/config.fish[/cyan]")
        elif detected_shell == "powershell":
            console.print("\n[cyan]# Add to your PowerShell profile[/cyan]")

        console.print(f"\n{integration_script}")

        console.print("\n[green]After adding this and restarting your shell:[/green]")
        console.print("• [cyan]uvenv activate myenv[/cyan] - Will activate directly")
        console.print("• [cyan]uvenv list[/cyan] - Works normally")
        console.print("• [cyan]uvenv python install 3.12[/cyan] - Works normally")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to generate shell integration: {e}")
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
