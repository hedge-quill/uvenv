"""Azure integration commands."""

import typer
from rich.console import Console
from rich.table import Table

from uvve.core.azure import AzureManager

console = Console()


def complete_subscription_ids(incomplete: str) -> list[str]:
    """Auto-completion for Azure subscription IDs."""
    try:
        azure_manager = AzureManager()
        subscriptions = azure_manager.list_subscriptions()
        return [sub["id"] for sub in subscriptions if sub["id"].startswith(incomplete)]
    except Exception:
        return []


def azure_login(
    tenant: str | None = typer.Option(
        None,
        "--tenant",
        "-t",
        help="Tenant ID to login to",
    ),
    use_device_code: bool = typer.Option(
        False,
        "--device-code",
        help="Use device code flow for authentication",
    ),
) -> None:
    """Login to Azure CLI."""
    try:
        azure_manager = AzureManager()
        azure_manager.login(tenant=tenant, use_device_code=use_device_code)

        # Show current subscription after login
        subscription = azure_manager.get_current_subscription()
        console.print(
            f"[green]✓[/green] Logged in to Azure "
            f"(Subscription: {subscription.get('name', 'Unknown')})"
        )

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to login to Azure: {e}")
        raise typer.Exit(1) from None


def azure_logout() -> None:
    """Logout from Azure CLI."""
    try:
        azure_manager = AzureManager()
        azure_manager.logout()
        console.print("[green]✓[/green] Logged out from Azure")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to logout from Azure: {e}")
        raise typer.Exit(1) from None


def azure_subscription(
    subscription_id: str | None = typer.Argument(
        None,
        help="Subscription ID to set as current",
        autocompletion=complete_subscription_ids,
    ),
    list_all: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all available subscriptions",
    ),
) -> None:
    """Set or list Azure subscriptions."""
    try:
        azure_manager = AzureManager()

        if list_all:
            # List all subscriptions
            subscriptions = azure_manager.list_subscriptions()
            current_sub = azure_manager.get_current_subscription()
            current_id = current_sub.get("id") if current_sub else None

            if not subscriptions:
                console.print(
                    "[yellow]No subscriptions found. "
                    "Make sure you're logged in to Azure.[/yellow]"
                )
                return

            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Current", width=8, justify="center")
            table.add_column("Name", style="cyan")
            table.add_column("ID", style="dim")
            table.add_column("State", style="green")

            for sub in subscriptions:
                is_current = "✓" if sub["id"] == current_id else ""
                table.add_row(
                    is_current,
                    sub.get("name", "Unknown"),
                    sub.get("id", "Unknown"),
                    sub.get("state", "Unknown"),
                )

            console.print(table)
            return

        if subscription_id:
            # Set current subscription
            azure_manager.set_subscription(subscription_id)
            subscription = azure_manager.get_current_subscription()
            console.print(
                f"[green]✓[/green] Set current subscription to: "
                f"{subscription.get('name', 'Unknown')} ({subscription_id})"
            )
        else:
            # Show current subscription
            subscription = azure_manager.get_current_subscription()
            if subscription:
                console.print(
                    f"Current subscription: {subscription.get('name', 'Unknown')} "
                    f"({subscription.get('id', 'Unknown')})"
                )
            else:
                console.print(
                    "[yellow]No current subscription set. "
                    "Use 'uvve azure subscription <id>' to set one.[/yellow]"
                )

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to manage subscription: {e}")
        raise typer.Exit(1) from None


def azure_account() -> None:
    """Show Azure account information."""
    try:
        azure_manager = AzureManager()
        account_info = azure_manager.get_account_info()

        console.print("[bold blue]Azure Account Information:[/bold blue]")
        console.print(f"User: {account_info.get('user', {}).get('name', 'Unknown')}")
        console.print(f"Type: {account_info.get('user', {}).get('type', 'Unknown')}")

        # Show current subscription
        subscription = azure_manager.get_current_subscription()
        if subscription:
            console.print(
                f"Current Subscription: {subscription.get('name', 'Unknown')} "
                f"({subscription.get('id', 'Unknown')})"
            )
        else:
            console.print("Current Subscription: [yellow]None set[/yellow]")

        # Show tenant info if available
        tenant_id = account_info.get("tenantId")
        if tenant_id:
            console.print(f"Tenant ID: {tenant_id}")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get account info: {e}")
        console.print("[yellow]💡 Try running 'uvve azure login' first[/yellow]")
        raise typer.Exit(1) from None
