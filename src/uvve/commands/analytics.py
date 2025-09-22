"""Analytics and status commands."""

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

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Description", style="dim")

        table.add_row("Total Environments", str(total), "All created environments")
        table.add_row(
            "Active Environments", str(total - unused), "Recently used environments"
        )
        table.add_row("Unused Environments", str(unused), "Not used in 30+ days")

        if total > 0:
            efficiency = round(((total - unused) / total) * 100, 1)
            table.add_row(
                "Efficiency", f"{efficiency}%", "Percentage of environments in use"
            )

        console.print(table)

        # Recommendations
        if unused > 0:
            console.print(
                f"\n[yellow]💡 Found {unused} unused environment(s). "
                f"Consider running `uvve cleanup --dry-run` to review.[/yellow]"
            )

        # Total disk usage
        total_size = summary.get("total_size_mb", 0)
        if total_size > 0:
            size_gb = total_size / 1024
            console.print(f"\n[blue]Total disk usage: {size_gb:.1f} GB[/blue]")

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

                console.print(f"\n[bold cyan]Analytics for '{name}'[/bold cyan]")

                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")

                table.add_row(
                    "Python Version", env_analytics.get("python_version", "Unknown")
                )
                table.add_row("Created", env_analytics.get("created", "Unknown"))
                table.add_row("Last Used", env_analytics.get("last_used", "Never"))
                table.add_row(
                    "Days Since Used", str(env_analytics.get("days_since_used", "N/A"))
                )
                table.add_row("Size", env_analytics.get("size", "Unknown"))
                table.add_row(
                    "Package Count", str(env_analytics.get("package_count", 0))
                )

                console.print(table)

                # Show tags if any
                tags = env_analytics.get("tags", [])
                if tags:
                    console.print(f"\n[blue]Tags:[/blue] {', '.join(tags)}")

                # Show description if any
                description = env_analytics.get("description")
                if description:
                    console.print(f"\n[blue]Description:[/blue] {description}")

            except Exception as e:
                console.print(f"[red]✗[/red] Failed to get analytics for '{name}': {e}")
                raise typer.Exit(1)
        else:
            # Show overall analytics
            summary = analytics_manager.get_usage_summary()

            console.print("\n[bold cyan]Environment Usage Summary[/bold cyan]")

            # Usage distribution
            if summary["environments_by_usage"]:
                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Usage Category", style="cyan")
                table.add_column("Count", style="green", justify="right")
                table.add_column("Percentage", style="yellow", justify="right")

                total = summary["total_environments"]
                for category, count in summary["environments_by_usage"].items():
                    percentage = (count / total * 100) if total > 0 else 0
                    table.add_row(category, str(count), f"{percentage:.1f}%")

                console.print(table)

            # Show most used environments
            if summary.get("most_used_environments"):
                console.print("\n[bold blue]Most Active Environments:[/bold blue]")
                for i, env in enumerate(summary["most_used_environments"][:5], 1):
                    last_used = env.get("last_used", "Never")
                    console.print(
                        f"  {i}. [cyan]{env['name']}[/cyan] - Last used: {last_used}"
                    )

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get analytics: {e}")
        raise typer.Exit(1) from None
