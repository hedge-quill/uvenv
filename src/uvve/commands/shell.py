"""Shell integration commands (activate, completion)."""

import typer
from rich.console import Console

from uvve.shell.activate import ActivationManager
from uvve.shell.completion import CompletionManager

console = Console()


def complete_environment_names(incomplete: str) -> list[str]:
    """Auto-completion for environment names."""
    try:
        from uvve.core.manager import EnvironmentManager

        manager = EnvironmentManager()
        envs = manager.list()
        return [env["name"] for env in envs if env["name"].startswith(incomplete)]
    except Exception:
        return []


def activate(
    name: str = typer.Argument(
        ...,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
    shell: str | None = typer.Option(
        None,
        "--shell",
        "-s",
        help="Target shell (bash, zsh, fish, powershell)",
    ),
) -> None:
    """Generate shell activation script for an environment."""
    try:
        activation_manager = ActivationManager()
        script = activation_manager.get_activation_script(name, shell)
        console.print(script)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get activation script: {e}")
        raise typer.Exit(1) from None


def completion(
    shell: str = typer.Argument(
        "bash",
        help="Target shell (bash, zsh, fish, powershell)",
    ),
    install: bool = typer.Option(
        False,
        "--install",
        "-i",
        help="Install completion script to shell config",
    ),
    path: str | None = typer.Option(
        None,
        "--path",
        "-p",
        help="Custom path to install completion script",
    ),
) -> None:
    """Generate or install shell completion scripts."""
    try:
        completion_manager = CompletionManager()

        if install:
            instructions = completion_manager.install_completion(shell, path)
            console.print(instructions)
            console.print(f"[green]✓[/green] Completion setup instructions for {shell}")
            console.print(
                "[yellow]💡 Restart your shell or source your profile "
                "to enable completion[/yellow]"
            )
        else:
            # Just output the completion script
            if shell == "bash":
                script = completion_manager.get_bash_completion()
            elif shell == "zsh":
                script = completion_manager.get_zsh_completion()
            elif shell == "fish":
                script = completion_manager.get_fish_completion()
            else:
                console.print(f"[red]✗[/red] Unsupported shell: {shell}")
                raise typer.Exit(1)

            console.print(script)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to setup completion: {e}")
        raise typer.Exit(1) from None
