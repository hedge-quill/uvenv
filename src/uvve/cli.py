"""CLI entrypoint for uvve using Typer."""

from __future__ import annotations

import typer
from datetime import datetime
from rich.console import Console
from rich.table import Table

from uvve import __version__
from uvve.core.analytics import AnalyticsManager
from uvve.core.azure import AzureManager
from uvve.core.freeze import FreezeManager
from uvve.core.manager import EnvironmentManager
from uvve.core.python import PythonManager
from uvve.shell.activate import ActivationManager

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
    """Main callback for global options."""


# Initialize managers
env_manager = EnvironmentManager()
python_manager = PythonManager()
freeze_manager = FreezeManager()
activation_manager = ActivationManager()
analytics_manager = AnalyticsManager()


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


@app.command(name="list")
def env_list(
    show_usage: bool = typer.Option(
        False, "--usage", "-u", help="Show usage statistics"
    ),
    sort_by: str = typer.Option(
        "name", "--sort-by", help="Sort by: name, usage, size, last_used"
    ),
) -> None:
    """List all virtual environments."""
    try:
        environments = env_manager.list()
        if not environments:
            console.print("[yellow]No virtual environments found[/yellow]")
            return

        # Get enhanced data if usage info is requested
        if show_usage:
            enhanced_envs = []
            for env in environments:
                metadata = env_manager.get_metadata(env["name"])
                size = env_manager.get_environment_size(env["name"])

                enhanced_env = {
                    **env,
                    "usage_count": metadata.get("usage_count", 0),
                    "last_used": metadata.get("last_used"),
                    "size_bytes": size,
                    "tags": metadata.get("tags", []),
                    "description": metadata.get("description", ""),
                }
                enhanced_envs.append(enhanced_env)
            environments = enhanced_envs

        # Sort environments
        if sort_by == "usage":
            environments.sort(key=lambda x: x.get("usage_count", 0), reverse=True)
        elif sort_by == "size":
            environments.sort(key=lambda x: x.get("size_bytes", 0), reverse=True)
        elif sort_by == "last_used":

            def sort_key(x):
                last_used = x.get("last_used")
                if not last_used:
                    return datetime.min
                try:
                    return datetime.fromisoformat(last_used.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    return datetime.min

            environments.sort(key=sort_key, reverse=True)
        else:
            environments.sort(key=lambda x: x["name"])

        if show_usage:
            table = Table(title="Virtual Environments (with Usage)")
            table.add_column("Name", style="cyan")
            table.add_column("Python", style="green")
            table.add_column("Usage", style="blue")
            table.add_column("Last Used", style="white")
            table.add_column("Size", style="yellow")
            table.add_column("Tags", style="magenta")
            table.add_column("Description", style="dim")

            for env in environments:
                # Format last used
                last_used = env.get("last_used")
                if last_used:
                    try:
                        last_used_dt = datetime.fromisoformat(
                            last_used.replace("Z", "+00:00")
                        )
                        days_ago = (
                            datetime.now() - last_used_dt.replace(tzinfo=None)
                        ).days
                        if days_ago == 0:
                            last_used_str = "Today"
                        elif days_ago == 1:
                            last_used_str = "Yesterday"
                        else:
                            last_used_str = f"{days_ago}d ago"
                    except (ValueError, AttributeError):
                        last_used_str = "Recently"
                else:
                    last_used_str = "Never"

                # Format size
                size_bytes = env.get("size_bytes", 0)
                if size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.0f}KB"
                elif size_bytes < 1024 * 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024):.0f}MB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"

                # Format tags
                tags = env.get("tags", [])
                tags_str = ", ".join(tags) if tags else ""

                # Truncate description
                description = env.get("description", "")
                if len(description) > 30:
                    description = description[:27] + "..."

                table.add_row(
                    env["name"],
                    env["python_version"],
                    str(env.get("usage_count", 0)),
                    last_used_str,
                    size_str,
                    tags_str,
                    description,
                )
        else:
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
def create(
    name: str = typer.Argument(..., help="Name of the virtual environment"),
    python_version: str = typer.Argument(
        ...,
        help="Python version for the environment",
        autocompletion=complete_python_versions,
    ),
    description: str = typer.Option(
        None, "--description", "-d", help="Description for the environment"
    ),
    add_tag: list[str] | None = typer.Option(
        None,
        "--add-tag",
        "-t",
        help="Add a tag to the environment (can be used multiple times)",
    ),
) -> None:
    """Create a new virtual environment."""
    console.print(
        f"[green]Creating environment '{name}' with Python {python_version}...[/green]"
    )

    # Handle mutable default
    if add_tag is None:
        add_tag = []

    # Interactive flow if no description or tags provided
    final_description = description
    final_tags = list(add_tag)

    if description is None:
        final_description = typer.prompt(
            "Description (optional, press Enter to skip)",
            default="",
            show_default=False,
        )

    if not add_tag:
        # Interactive tag collection
        console.print("[cyan]Add tags (optional):[/cyan]")
        console.print(
            "[dim]Press Enter after each tag, or just press Enter to finish[/dim]"
        )

        while True:
            tag = typer.prompt("Tag", default="", show_default=False)
            if not tag.strip():
                break
            final_tags.append(tag.strip())

    try:
        env_manager.create(name, python_version, final_description, final_tags)

        # Show creation summary
        console.print(f"[green]✓[/green] Environment '{name}' created successfully")

        if final_description:
            console.print(f"[dim]Description:[/dim] {final_description}")
        if final_tags:
            console.print(f"[dim]Tags:[/dim] {', '.join(final_tags)}")

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
        # Update usage statistics when activating
        env_manager.update_usage(name)

        activation_script = env_manager.get_activation_script(name)
        console.print(activation_script)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get activation script for '{name}': {e}")
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
def status() -> None:
    """Show environment utility overview."""
    try:
        summary = analytics_manager.get_usage_summary()

        console.print(f"\n[bold cyan]Environment Utility Overview[/bold cyan]")

        # Quick stats
        total = summary["total_environments"]
        unused = summary["unused_environments"]

        if total == 0:
            console.print("[yellow]No environments found[/yellow]")
            return

        # Utility summary
        health_table = Table()
        health_table.add_column("Environment", style="cyan")
        health_table.add_column("Last Used", style="white")
        health_table.add_column("Usage Count", style="green")
        health_table.add_column("Size", style="blue")
        health_table.add_column("Utility", style="magenta")

        for env in summary["environments"]:
            # Utility status
            usage_count = env["usage_count"]
            days_since_use = env["days_since_use"]

            if usage_count == 0:
                health = "🔴 Never used"
            elif days_since_use is None:
                health = "🟡 Recently created"
            elif days_since_use > 90:
                health = "🔴 Stale (90+ days)"
            elif days_since_use > 30:
                health = "🟡 Unused (30+ days)"
            elif usage_count < 5:
                health = "🟡 Low usage"
            else:
                health = "🟢 Healthy"

            # Format last used
            if env["last_used"]:
                if days_since_use is not None:
                    if days_since_use == 0:
                        last_used_str = "Today"
                    elif days_since_use == 1:
                        last_used_str = "Yesterday"
                    else:
                        last_used_str = f"{days_since_use}d ago"
                else:
                    last_used_str = "Recently"
            else:
                last_used_str = "Never"

            # Format size
            size_bytes = env["size_bytes"]
            if size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.0f}KB"
            elif size_bytes < 1024 * 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.0f}MB"
            else:
                size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"

            health_table.add_row(
                env["name"], last_used_str, str(usage_count), size_str, health
            )

        console.print(health_table)

        # Summary message
        if unused > 0:
            console.print(
                f"\n[yellow]💡 Found {unused} unused environment(s). Consider running `uvve cleanup --dry-run` to review.[/yellow]"
            )
        else:
            console.print(
                f"\n[green]✅ All {total} environments are being used actively![/green]"
            )

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get status: {e}")
        raise typer.Exit(1) from None


@app.command()
def edit(
    name: str = typer.Argument(
        ...,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
    description: str = typer.Option(
        None, "--description", "-d", help="Set environment description"
    ),
    add_tag: str = typer.Option(None, "--add-tag", help="Add a tag to the environment"),
    remove_tag: str = typer.Option(
        None, "--remove-tag", help="Remove a tag from the environment"
    ),
    project_root: str = typer.Option(
        None, "--project-root", help="Set project root directory"
    ),
) -> None:
    """Edit environment metadata."""
    try:
        if not any([description is not None, add_tag, remove_tag, project_root]):
            console.print(
                "[yellow]No changes specified. Use --help to see available options.[/yellow]"
            )
            return

        # Get current metadata
        metadata = env_manager.get_metadata(name)

        # Update description
        if description is not None:
            env_manager.update_metadata_field(name, "description", description)
            console.print(f"[green]✓[/green] Updated description for '{name}'")

        # Add tag
        if add_tag:
            current_tags = metadata.get("tags", [])
            if add_tag not in current_tags:
                current_tags.append(add_tag)
                env_manager.update_metadata_field(name, "tags", current_tags)
                console.print(f"[green]✓[/green] Added tag '{add_tag}' to '{name}'")
            else:
                console.print(
                    f"[yellow]Tag '{add_tag}' already exists on '{name}'[/yellow]"
                )

        # Remove tag
        if remove_tag:
            current_tags = metadata.get("tags", [])
            if remove_tag in current_tags:
                current_tags.remove(remove_tag)
                env_manager.update_metadata_field(name, "tags", current_tags)
                console.print(
                    f"[green]✓[/green] Removed tag '{remove_tag}' from '{name}'"
                )
            else:
                console.print(
                    f"[yellow]Tag '{remove_tag}' not found on '{name}'[/yellow]"
                )

        # Update project root
        if project_root:
            import os

            project_root_path = os.path.abspath(os.path.expanduser(project_root))
            env_manager.update_metadata_field(name, "project_root", project_root_path)
            console.print(
                f"[green]✓[/green] Set project root for '{name}' to '{project_root_path}'"
            )

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to edit metadata for '{name}': {e}")
        raise typer.Exit(1) from None


@app.command()
def analytics(
    name: str = typer.Argument(
        None,
        help="Environment name for detailed analytics (optional)",
        autocompletion=complete_environment_names,
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed analytics"
    ),
) -> None:
    """Show environment usage analytics."""
    try:
        if name:
            # Show analytics for specific environment
            analytics_data = analytics_manager.get_environment_analytics(name)
            metadata = analytics_data["metadata"]
            derived = analytics_data["derived_stats"]
            size_info = analytics_data["size_info"]

            console.print(f"\n[bold cyan]Analytics for '{name}'[/bold cyan]")

            # Basic info
            table = Table(title="Environment Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Name", metadata.get("name", "unknown"))
            table.add_row("Python Version", metadata.get("python_version", "unknown"))
            table.add_row(
                "Description", metadata.get("description", "") or "No description"
            )
            table.add_row("Tags", ", ".join(metadata.get("tags", [])) or "No tags")
            table.add_row("Size", size_info["size_human"])

            console.print(table)

            # Usage statistics
            usage_table = Table(title="Usage Statistics")
            usage_table.add_column("Metric", style="cyan")
            usage_table.add_column("Value", style="white")

            usage_table.add_row("Usage Count", str(metadata.get("usage_count", 0)))
            usage_table.add_row("Last Used", metadata.get("last_used") or "Never")

            if derived["age_days"] is not None:
                usage_table.add_row("Age (days)", str(derived["age_days"]))

            if derived["days_since_use"] is not None:
                usage_table.add_row("Days Since Use", str(derived["days_since_use"]))
            else:
                usage_table.add_row("Days Since Use", "Never used")

            usage_table.add_row(
                "Usage Frequency", f"{derived['usage_frequency']:.3f}/day"
            )

            console.print(usage_table)

        else:
            # Show summary for all environments
            summary = analytics_manager.get_usage_summary()

            console.print(f"\n[bold cyan]Environment Usage Summary[/bold cyan]")

            # Overall stats
            stats_table = Table(title="Overall Statistics")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="white")

            stats_table.add_row(
                "Total Environments", str(summary["total_environments"])
            )
            stats_table.add_row(
                "Active Environments", str(summary["active_environments"])
            )
            stats_table.add_row(
                "Unused Environments", str(summary["unused_environments"])
            )

            # Convert total size to human readable
            total_bytes = summary["total_size_bytes"]
            if total_bytes < 1024 * 1024:
                size_str = f"{total_bytes / 1024:.1f} KB"
            elif total_bytes < 1024 * 1024 * 1024:
                size_str = f"{total_bytes / (1024 * 1024):.1f} MB"
            else:
                size_str = f"{total_bytes / (1024 * 1024 * 1024):.1f} GB"

            stats_table.add_row("Total Size", size_str)
            stats_table.add_row("Total Usage Count", str(summary["total_usage_count"]))

            console.print(stats_table)

            # Environment list
            if summary["environments"]:
                env_table = Table(title="Environment Details")
                env_table.add_column("Name", style="cyan")
                env_table.add_column("Usage", style="green")
                env_table.add_column("Last Used", style="white")
                env_table.add_column("Size", style="blue")
                env_table.add_column("Status", style="magenta")

                for env in summary["environments"]:
                    # Format last used
                    last_used = env["last_used"]
                    if last_used:
                        if env["days_since_use"] is not None:
                            if env["days_since_use"] == 0:
                                last_used_str = "Today"
                            elif env["days_since_use"] == 1:
                                last_used_str = "Yesterday"
                            else:
                                last_used_str = f"{env['days_since_use']}d ago"
                        else:
                            last_used_str = "Recently"
                    else:
                        last_used_str = "Never"

                    # Format size
                    size_bytes = env["size_bytes"]
                    if size_bytes < 1024 * 1024:
                        size_str = f"{size_bytes / 1024:.0f}KB"
                    elif size_bytes < 1024 * 1024 * 1024:
                        size_str = f"{size_bytes / (1024 * 1024):.0f}MB"
                    else:
                        size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"

                    # Status
                    status = "⚠️ Unused" if env["is_unused"] else "✅ Active"

                    env_table.add_row(
                        env["name"],
                        str(env["usage_count"]),
                        last_used_str,
                        size_str,
                        status,
                    )

                console.print(env_table)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get analytics: {e}")
        raise typer.Exit(1) from None


@app.command()
def cleanup(
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be removed without actually removing"
    ),
    unused_for: int = typer.Option(
        30, "--unused-for", help="Days since last use to consider unused"
    ),
    low_usage: bool = typer.Option(
        False, "--low-usage", help="Include environments with low usage (≤5 uses)"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Ask before removing each environment"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Remove without confirmation"
    ),
) -> None:
    """Clean up unused environments."""
    try:
        unused_envs = analytics_manager.find_unused_environments(unused_for)

        if low_usage:
            low_usage_envs = analytics_manager.find_low_usage_environments(5)
            # Merge lists, avoiding duplicates
            unused_names = {env["name"] for env in unused_envs}
            for env in low_usage_envs:
                if env["name"] not in unused_names:
                    unused_envs.append(env)

        if not unused_envs:
            console.print(
                f"[green]✅ No environments found that are unused for {unused_for}+ days[/green]"
            )
            return

        # Calculate total size to be freed
        total_size = sum(env["size_bytes"] for env in unused_envs)
        if total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.1f} GB"

        console.print(
            f"\n[yellow]🗑️  Found {len(unused_envs)} environment(s) to clean up:[/yellow]"
        )

        # Show what will be removed
        cleanup_table = Table()
        cleanup_table.add_column("Environment", style="cyan")
        cleanup_table.add_column("Last Used", style="white")
        cleanup_table.add_column("Usage Count", style="green")
        cleanup_table.add_column("Size", style="blue")
        cleanup_table.add_column("Reason", style="yellow")

        for env in unused_envs:
            # Format last used
            days_since_use = env["days_since_use"]
            if days_since_use == "never":
                last_used_str = "Never"
                reason = "Never used"
            elif days_since_use == "unknown":
                last_used_str = "Unknown"
                reason = "Unknown usage"
            else:
                last_used_str = f"{days_since_use}d ago"
                reason = f"Unused {days_since_use}d"

            # Add low usage reason if applicable
            if env["usage_count"] <= 5 and days_since_use not in ("never", "unknown"):
                reason += f", low usage ({env['usage_count']})"

            # Format size
            size_bytes = env["size_bytes"]
            if size_bytes < 1024 * 1024:
                env_size_str = f"{size_bytes / 1024:.0f}KB"
            elif size_bytes < 1024 * 1024 * 1024:
                env_size_str = f"{size_bytes / (1024 * 1024):.0f}MB"
            else:
                env_size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"

            cleanup_table.add_row(
                env["name"],
                last_used_str,
                str(env["usage_count"]),
                env_size_str,
                reason,
            )

        console.print(cleanup_table)
        console.print(f"\n[cyan]Total space to be freed: {size_str}[/cyan]")

        if dry_run:
            console.print(
                "\n[blue]💡 This was a dry run. Use without --dry-run to actually remove environments.[/blue]"
            )
            return

        # Confirm removal
        removed_count = 0
        skipped_count = 0

        if interactive:
            console.print(
                f"\n[yellow]Interactive mode - you'll be asked about each environment:[/yellow]"
            )
            for env in unused_envs:
                confirm = typer.confirm(f"Remove '{env['name']}'?")
                if confirm:
                    try:
                        env_manager.remove(env["name"])
                        console.print(f"[green]✓[/green] Removed '{env['name']}'")
                        removed_count += 1
                    except Exception as e:
                        console.print(
                            f"[red]✗[/red] Failed to remove '{env['name']}': {e}"
                        )
                else:
                    console.print(f"[yellow]Skipped '{env['name']}'[/yellow]")
                    skipped_count += 1
        else:
            if not force:
                env_names = [env["name"] for env in unused_envs]
                confirm = typer.confirm(
                    f"Remove all {len(unused_envs)} environments? This will free {size_str}"
                )
                if not confirm:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return

            # Remove all environments
            for env in unused_envs:
                try:
                    env_manager.remove(env["name"])
                    console.print(f"[green]✓[/green] Removed '{env['name']}'")
                    removed_count += 1
                except Exception as e:
                    console.print(f"[red]✗[/red] Failed to remove '{env['name']}': {e}")

        # Summary
        if removed_count > 0:
            actual_freed = sum(env["size_bytes"] for env in unused_envs[:removed_count])
            if actual_freed < 1024 * 1024:
                freed_str = f"{actual_freed / 1024:.1f} KB"
            elif actual_freed < 1024 * 1024 * 1024:
                freed_str = f"{actual_freed / (1024 * 1024):.1f} MB"
            else:
                freed_str = f"{actual_freed / (1024 * 1024 * 1024):.1f} GB"

            console.print(
                f"\n[green]✅ Cleaned up {removed_count} environment(s), freed {freed_str}[/green]"
            )

        if skipped_count > 0:
            console.print(f"[yellow]Skipped {skipped_count} environment(s)[/yellow]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to cleanup environments: {e}")
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
        help="Output only the shell script (for piping to config files)",
    ),
) -> None:
    """Generate shell integration for uvve.

    This enables 'uvve activate <env>' to work directly without eval.

    Examples:
      uvve shell-integration                    # Show instructions
      uvve shell-integration --print           # Output script only
      uvve shell-integration --print >> ~/.zshrc  # Install to zsh
    """
    try:
        integration_script = activation_manager.generate_shell_integration(shell)

        if print_only:
            # Disable syntax highlighting to ensure plain text output when piping to config files.
            # This avoids unwanted ANSI color codes or formatting in shell configuration files.
            console.print(integration_script, highlight=False)
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
            console.print(f"[dim]uvve shell-integration --print >> {config_file}[/dim]")
        elif detected_shell == "fish":
            console.print("\n[cyan]# Add to ~/.config/fish/config.fish[/cyan]")
            console.print(
                "[dim]uvve shell-integration --print >> ~/.config/fish/config.fish[/dim]"
            )
        elif detected_shell == "powershell":
            console.print("\n[cyan]# Add to your PowerShell profile[/cyan]")

        console.print(f"\n{integration_script}")

        console.print("\n[green]After adding this and restarting your shell:[/green]")
        console.print("• [cyan]uvve activate myenv[/cyan] - Will activate directly")
        console.print("• [cyan]uvve list[/cyan] - Works normally")
        console.print("• [cyan]uvve python install 3.12[/cyan] - Works normally")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to generate shell integration: {e}")
        raise typer.Exit(1) from None


@app.command()
def setup_azure(
    feed_url: str = typer.Option(
        None,
        "--feed-url",
        "-u",
        help="Azure DevOps artifact feed URL",
    ),
    feed_name: str = typer.Option(
        "private-registry",
        "--feed-name",
        "-n",
        help="Name for the feed in configuration",
    ),
    env_name: str = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment name to install keyring packages into",
    ),
) -> None:
    """Set up Azure DevOps package feed authentication for uv."""
    try:
        azure_manager = AzureManager()

        # Interactive prompt if no URL provided
        if not feed_url:
            console.print(
                "[cyan]Setting up Azure DevOps package feed authentication[/cyan]"
            )
            console.print("Please provide your Azure DevOps artifact feed URL.")
            console.print(
                "Example: https://pkgs.dev.azure.com/myorg/_packaging/myfeed/pypi/simple/"
            )
            feed_url = typer.prompt("Feed URL")

        # Interactive prompt for environment if not provided
        if not env_name:
            # Try to detect current active uvve environment
            current_env = env_manager.get_current_environment()
            if current_env:
                env_name = current_env
                console.print(f"[green]Detected active environment: {env_name}[/green]")
            else:
                # No active environment, check available environments
                envs = env_manager.list()

                if envs:
                    console.print(
                        f"\n[cyan]No active uvve environment detected. Available environments:[/cyan]"
                    )
                    for env in envs:
                        console.print(f"  • {env['name']}")
                    env_name = typer.prompt(
                        "Environment name to install keyring packages into (or press Enter to skip)",
                        default="",
                    )
                    if not env_name.strip():
                        env_name = None
                else:
                    console.print(
                        "\n[yellow]No environments found. Keyring packages will be installed globally.[/yellow]"
                    )

        # Show installation progress
        if env_name:
            console.print(
                f"\n[yellow]Installing keyring packages into environment '{env_name}'...[/yellow]"
            )
        else:
            console.print("\n[yellow]Installing keyring packages globally...[/yellow]")

        # Set up the feed
        azure_manager.setup_azure_feed(feed_url, feed_name, env_name)

        # Get status
        status = azure_manager.get_status()

        console.print(
            f"\n[green]✅ Azure feed '{feed_name}' configured successfully![/green]"
        )
        console.print(f"Feed URL: {feed_url}")
        console.print(f"Config file: {status['config_file_path']}")

        # Show shell setup instructions
        console.print("\n[bold cyan]Shell Setup Instructions:[/bold cyan]")
        console.print("Add these environment variables to your shell:")

        commands = azure_manager.get_shell_setup_commands(feed_name)
        shell = "bash"  # Default, could detect from env
        console.print(f"\n[yellow]{commands[shell]}[/yellow]")

        console.print(
            "\n[dim]💡 Make sure you're authenticated with Azure CLI: `az login`[/dim]"
        )

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to set up Azure feed: {e}")
        raise typer.Exit(1) from None


@app.command()
def feed_status() -> None:
    """Show package feed configuration status."""
    try:
        azure_manager = AzureManager()
        status = azure_manager.get_status()

        console.print("[bold cyan]Package Feed Configuration Status[/bold cyan]\n")

        # Config file status
        if status["config_file_exists"]:
            console.print(
                f"[green]✅[/green] Config file: {status['config_file_path']}"
            )
        else:
            console.print(
                f"[yellow]⚠️[/yellow] No config file found at: {status['config_file_path']}"
            )

        # Keyring provider
        if status["keyring_provider"]:
            console.print(
                f"[green]✅[/green] Keyring provider: {status['keyring_provider']}"
            )
        else:
            console.print("[yellow]⚠️[/yellow] UV_KEYRING_PROVIDER not set")

        # Configured indexes
        if status["configured_indexes"]:
            console.print(
                f"\n[bold]Configured Azure Feeds ({len(status['configured_indexes'])}):[/bold]"
            )
            for idx in status["configured_indexes"]:
                console.print(
                    f"  • {idx.get('name', 'unnamed')}: {idx.get('url', 'no URL')}"
                )
        else:
            console.print("\n[yellow]No Azure feeds configured[/yellow]")

        # Azure environment variables
        if status["azure_env_vars"]:
            console.print(
                f"\n[bold]Azure Environment Variables ({len(status['azure_env_vars'])}):[/bold]"
            )
            for var, value in status["azure_env_vars"].items():
                console.print(f"  • {var}={value}")
        else:
            console.print("\n[yellow]No Azure environment variables set[/yellow]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get Azure status: {e}")
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
