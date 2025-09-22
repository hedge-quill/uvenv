"""Maintenance commands (cleanup, edit)."""

import typer
from rich.console import Console
from rich.table import Table

from uvve.core.analytics import AnalyticsManager
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


def edit(
    name: str = typer.Argument(
        ...,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
    description: str | None = typer.Option(
        None,
        "--description",
        "-d",
        help="Update environment description",
    ),
    add_tag: list[str] | None = typer.Option(
        None,
        "--add-tag",
        "-t",
        help="Add a tag to the environment (can be used multiple times)",
    ),
    remove_tag: list[str] | None = typer.Option(
        None,
        "--remove-tag",
        "-r",
        help="Remove a tag from the environment (can be used multiple times)",
    ),
    project_root: str | None = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Set project root path for the environment",
    ),
) -> None:
    """Edit environment metadata (description, tags)."""
    if add_tag is None:
        add_tag = []
    if remove_tag is None:
        remove_tag = []

    # Check if any changes were specified
    if not any([description, add_tag, remove_tag, project_root]):
        console.print(
            "[yellow]No changes specified. Use --help to see available options.[/yellow]"
        )
        return

    try:
        env_manager = EnvironmentManager()

        # Get current metadata
        current_metadata = env_manager.get_metadata(name)
        changes_made = []

        if description is not None:
            env_manager.update_metadata_field(name, "description", description)
            changes_made.append(f"description: '{description}'")

        if add_tag:
            current_tags = current_metadata.get("tags", [])
            new_tags = list(set(current_tags + add_tag))  # Avoid duplicates
            env_manager.update_metadata_field(name, "tags", new_tags)
            changes_made.append(f"added tags: {', '.join(add_tag)}")

        if remove_tag:
            current_tags = current_metadata.get("tags", [])
            new_tags = [tag for tag in current_tags if tag not in remove_tag]
            env_manager.update_metadata_field(name, "tags", new_tags)
            changes_made.append(f"removed tags: {', '.join(remove_tag)}")

        if project_root:
            # Convert to absolute path
            from pathlib import Path

            project_root_path = Path(project_root).resolve()
            env_manager.update_metadata_field(
                name, "project_root", str(project_root_path)
            )
            changes_made.append(f"project root: '{project_root_path}'")

        if changes_made:
            console.print(f"[green]✓[/green] Updated environment '{name}':")
            for change in changes_made:
                console.print(f"  • {change}")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to edit environment '{name}': {e}")
        raise typer.Exit(1) from None


def cleanup(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be cleaned up without actually removing anything",
    ),
    unused_for: int = typer.Option(
        30,
        "--unused-for",
        help="Remove environments unused for this many days",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Ask before removing each environment",
    ),
) -> None:
    """Clean up unused environments."""
    try:
        analytics_manager = AnalyticsManager()
        env_manager = EnvironmentManager()

        # Get unused environments
        unused_envs = analytics_manager.find_unused_environments(unused_for)

        if not unused_envs:
            console.print(
                f"[green]✅ No environments found that are unused for {unused_for}+ days[/green]"
            )
            return

        # Calculate total size
        total_size_mb = sum(env.get("size_mb", 0) for env in unused_envs)
        size_str = (
            f"{total_size_mb / 1024:.1f} GB"
            if total_size_mb > 1024
            else f"{total_size_mb} MB"
        )

        # Show what would be cleaned up
        console.print(
            f"\n[yellow]🗑️  Found {len(unused_envs)} environment(s) to clean up:[/yellow]"
        )

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Name", style="cyan")
        table.add_column("Last Used", style="yellow")
        table.add_column("Days Ago", style="magenta", justify="right")
        table.add_column("Size", style="blue", justify="right")

        for env in unused_envs:
            last_used = env.get("last_used", "Never")
            if hasattr(last_used, "strftime"):
                last_used = last_used.strftime("%Y-%m-%d")

            table.add_row(
                env["name"],
                str(last_used),
                str(env.get("days_since_used", "N/A")),
                env.get("size", "Unknown"),
            )

        console.print(table)

        if dry_run:
            console.print(
                "\n[blue]💡 This was a dry run. Use without --dry-run to actually remove environments.[/blue]"
            )
            return

        # Actually remove environments
        if interactive:
            console.print(
                "\n[yellow]Interactive mode - you'll be asked about each environment:[/yellow]"
            )
            removed_count = 0
            freed_mb = 0

            for env in unused_envs:
                should_remove = typer.confirm(
                    f"Remove environment '{env['name']}'? "
                    f"(Last used: {env.get('last_used', 'Never')})"
                )
                if should_remove:
                    try:
                        env_manager.remove(env["name"])
                        removed_count += 1
                        freed_mb += env.get("size_mb", 0)
                        console.print(f"[green]✓[/green] Removed '{env['name']}'")
                    except Exception as e:
                        console.print(
                            f"[red]✗[/red] Failed to remove '{env['name']}': {e}"
                        )
        else:
            # Batch removal
            if not typer.confirm(
                f"Remove all {len(unused_envs)} environments? This will free {size_str}"
            ):
                console.print("[yellow]Cleanup cancelled[/yellow]")
                return

            removed_count = 0
            freed_mb = 0

            for env in unused_envs:
                try:
                    env_manager.remove(env["name"])
                    removed_count += 1
                    freed_mb += env.get("size_mb", 0)
                except Exception as e:
                    console.print(f"[red]✗[/red] Failed to remove '{env['name']}': {e}")

        # Show results
        if removed_count > 0:
            freed_str = (
                f"{freed_mb / 1024:.1f} GB" if freed_mb > 1024 else f"{freed_mb} MB"
            )
            console.print(
                f"\n[green]✅ Cleaned up {removed_count} environment(s), freed {freed_str}[/green]"
            )
        else:
            console.print("\n[yellow]No environments were removed[/yellow]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to cleanup environments: {e}")
        raise typer.Exit(1) from None
