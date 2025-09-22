"""Analytics and status commands."""

import typer
from datetime import datetime
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


def status(
    current: bool = typer.Option(
        False,
        "--current",
        help="Only show the currently active environment name",
    ),
) -> None:
    """Show environment utility overview."""
    if current:
        # Just return the current environment name for shell integration
        try:
            env_manager = EnvironmentManager()
            current_env = env_manager.get_current_environment()
            if current_env:
                console.print(current_env, end="")
            else:
                raise typer.Exit(1)
        except Exception:
            raise typer.Exit(1) from None
        return

    try:
        analytics_manager = AnalyticsManager()
        summary = analytics_manager.get_usage_summary()

        console.print("\n[bold cyan]Environment Utility Overview[/bold cyan]")

        # Quick stats
        total = summary["total_environments"]
        unused = summary["unused_environments"]

        if total == 0:
            console.print("[yellow]No environments found[/yellow]")
            return

        # Utility summary table
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

        # Summary message with percentages
        if unused > 0:
            unused_pct = (unused / total * 100) if total > 0 else 0
            console.print(
                f"\n[yellow]💡 Found {unused} unused environment(s) ({unused_pct:.1f}%). "
                f"Consider running `uvve cleanup --dry-run` to review.[/yellow]"
            )
        else:
            console.print(
                f"\n[green]✅ All {total} environments are being used actively![/green]"
            )

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get status: {e}")
        raise typer.Exit(1) from None


def analytics(
    name: str | None = typer.Argument(
        None,
        help="Name of the virtual environment",
        autocompletion=complete_environment_names,
    ),
    detailed: bool = typer.Option(
        False,
        "--detailed",
        help="Show detailed analytics information",
    ),
) -> None:
    """Show usage analytics and insights."""
    try:
        analytics_manager = AnalyticsManager()

        if name:
            # Show analytics for specific environment
            try:
                env_analytics = analytics_manager.get_environment_analytics(name)
                metadata = env_analytics.get("metadata", {})
                derived_stats = env_analytics.get("derived_stats", {})
                size_info = env_analytics.get("size_info", {})

                console.print(f"\n[bold cyan]Analytics for '{name}'[/bold cyan]")

                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")

                # Basic info
                table.add_row(
                    "Python Version", metadata.get("python_version", "Unknown")
                )

                # Format created_at date
                created_at = metadata.get("created_at")
                if created_at:
                    try:
                        # Remove microseconds and format nicely
                        if "." in created_at:
                            created_at = created_at.split(".")[0]
                        created_str = created_at.replace("T", " ")
                    except Exception:
                        created_str = str(created_at)
                else:
                    created_str = "Unknown"

                table.add_row("Created", created_str)

                # Format last_used date
                last_used = metadata.get("last_used")
                if last_used:
                    try:
                        # Remove microseconds and format nicely
                        if isinstance(last_used, str):
                            if "." in last_used:
                                last_used = last_used.split(".")[0]
                            last_used_str = last_used.replace("T", " ")
                        else:
                            last_used_str = str(last_used)
                    except Exception:
                        last_used_str = str(last_used)
                else:
                    last_used_str = "Never"

                table.add_row("Last Used", last_used_str)

                # Derived stats
                table.add_row(
                    "Days Since Used", str(derived_stats.get("days_since_used", "N/A"))
                )
                table.add_row("Usage Count", str(metadata.get("usage_count", 0)))

                # Size info
                size_bytes = size_info.get("size_bytes", 0)
                if size_bytes > 0:
                    if size_bytes < 1024 * 1024:
                        size_str = f"{size_bytes / 1024:.1f} KB"
                    elif size_bytes < 1024 * 1024 * 1024:
                        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                    else:
                        size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
                else:
                    size_str = "Unknown"

                table.add_row("Size", size_str)

                # Package count (if available)
                package_count = derived_stats.get("package_count", 0)
                table.add_row("Package Count", str(package_count))

                console.print(table)

                # Show tags if any
                tags = metadata.get("tags", [])
                if tags:
                    console.print(f"\n[blue]Tags:[/blue] {', '.join(tags)}")

                # Show description if any
                description = metadata.get("description")
                if description:
                    console.print(f"\n[blue]Description:[/blue] {description}")

            except Exception as e:
                console.print(f"[red]✗[/red] Failed to get analytics for '{name}': {e}")
                raise typer.Exit(1) from None
        else:
            # Show overall analytics
            summary = analytics_manager.get_usage_summary()

            console.print("\n[bold cyan]Environment Usage Summary[/bold cyan]")

            # Usage distribution
            total = summary["total_environments"]
            active = summary["active_environments"]
            unused = summary["unused_environments"]

            if total > 0:
                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Usage Category", style="cyan")
                table.add_column("Count", style="green", justify="right")
                table.add_column("Percentage", style="yellow", justify="right")

                active_pct = (active / total * 100) if total > 0 else 0
                unused_pct = (unused / total * 100) if total > 0 else 0

                table.add_row("Active (Recent Use)", str(active), f"{active_pct:.1f}%")
                table.add_row("Unused (30+ days)", str(unused), f"{unused_pct:.1f}%")
                table.add_row("Total", str(total), "100.0%")

                console.print(table)

            # Show most used environments (sorted by usage count)
            environments = summary.get("environments", [])
            if environments:
                # Filter to active environments and show top 5
                active_envs = [
                    env for env in environments if not env.get("is_unused", False)
                ]

                if active_envs:
                    console.print("\n[bold blue]Most Active Environments:[/bold blue]")
                    for i, env in enumerate(active_envs[:5], 1):
                        usage_count = env.get("usage_count", 0)
                        last_used = env.get("last_used", "Never")
                        if isinstance(last_used, str) and last_used != "Never":
                            try:
                                # Format datetime if it's a string
                                from datetime import datetime

                                dt = datetime.fromisoformat(
                                    last_used.replace("Z", "+00:00")
                                )
                                last_used = dt.strftime("%Y-%m-%d")
                            except (ValueError, AttributeError):
                                pass

                        console.print(
                            f"  {i}. [cyan]{env['name']}[/cyan] - "
                            f"Used {usage_count} times, Last: {last_used}"
                        )
                else:
                    console.print(
                        "\n[yellow]No recently active environments found.[/yellow]"
                    )

                # Show disk usage breakdown
                if detailed:
                    console.print("\n[bold blue]Environment Sizes:[/bold blue]")
                    # Sort by size
                    environments.sort(
                        key=lambda x: x.get("size_bytes", 0), reverse=True
                    )

                    size_table = Table(show_header=True, header_style="bold blue")
                    size_table.add_column("Environment", style="cyan")
                    size_table.add_column("Size", style="green", justify="right")
                    size_table.add_column("Python", style="yellow")
                    size_table.add_column("Status", style="dim")

                    for env in environments[:10]:  # Top 10 by size
                        size_bytes = env.get("size_bytes", 0)
                        size_mb = size_bytes / (1024 * 1024) if size_bytes > 0 else 0
                        size_str = (
                            f"{size_mb:.1f} MB"
                            if size_mb < 1024
                            else f"{size_mb / 1024:.1f} GB"
                        )

                        status = "Unused" if env.get("is_unused", False) else "Active"
                        python_version = env.get("python_version", "unknown")

                        size_table.add_row(
                            env["name"], size_str, python_version, status
                        )

                    console.print(size_table)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get analytics: {e}")
        raise typer.Exit(1) from None
