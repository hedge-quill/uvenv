"""Analytics and usage tracking for uvve environments."""

from datetime import datetime
from typing import Any

from uvve.core.manager import EnvironmentManager
from uvve.core.paths import PathManager


class AnalyticsManager:
    """Manages analytics and usage tracking for virtual environments."""

    def __init__(self, base_dir: str | None = None) -> None:
        """Initialize the analytics manager.

        Args:
            base_dir: Base directory for environments
        """
        self.path_manager = PathManager(base_dir)
        self.env_manager = EnvironmentManager(base_dir)

    def get_environment_analytics(self, name: str) -> dict[str, Any]:
        """Get detailed analytics for a specific environment.

        Args:
            name: Environment name

        Returns:
            Dictionary with analytics data

        Raises:
            RuntimeError: If environment doesn't exist
        """
        metadata = self.env_manager.get_metadata(name)

        # Calculate derived statistics
        return {
            "name": name,
            "metadata": metadata,
            "derived_stats": self._calculate_derived_stats(metadata),
            "size_info": self._get_size_info(name),
        }

    def get_usage_summary(self) -> dict[str, Any]:
        """Get usage summary for all environments.

        Returns:
            Dictionary with usage summary
        """
        environments = self.env_manager.list()

        total_size = 0
        total_usage = 0
        unused_count = 0
        active_count = 0

        env_stats = []

        for env in environments:
            env_name = env["name"]
            metadata = self.env_manager.get_metadata(env_name)
            size = self.env_manager.get_environment_size(env_name)

            usage_count = metadata.get("usage_count", 0)
            last_used = metadata.get("last_used")

            # Calculate days since last use
            days_since_use = None
            if last_used:
                try:
                    last_used_dt = datetime.fromisoformat(
                        last_used.replace("Z", "+00:00")
                    )
                    days_since_use = (
                        datetime.now() - last_used_dt.replace(tzinfo=None)
                    ).days
                except (ValueError, AttributeError):
                    days_since_use = None

            is_unused = (days_since_use is None and usage_count == 0) or (
                days_since_use and days_since_use > 30
            )

            env_stat = {
                "name": env_name,
                "usage_count": usage_count,
                "last_used": last_used,
                "days_since_use": days_since_use,
                "size_bytes": size,
                "is_unused": is_unused,
                "python_version": metadata.get("python_version", "unknown"),
                "tags": metadata.get("tags", []),
            }

            env_stats.append(env_stat)

            total_size += size
            total_usage += usage_count

            if is_unused:
                unused_count += 1
            else:
                active_count += 1

        # Sort by usage count (most used first)
        env_stats.sort(key=lambda x: x["usage_count"], reverse=True)

        return {
            "total_environments": len(environments),
            "active_environments": active_count,
            "unused_environments": unused_count,
            "total_size_bytes": total_size,
            "total_usage_count": total_usage,
            "environments": env_stats,
        }

    def find_unused_environments(self, days: int = 30) -> list[dict[str, Any]]:
        """Find environments that haven't been used for specified days.

        Args:
            days: Number of days to consider as unused

        Returns:
            List of unused environment information
        """
        unused = []
        environments = self.env_manager.list()

        for env in environments:
            env_name = env["name"]
            metadata = self.env_manager.get_metadata(env_name)

            last_used = metadata.get("last_used")
            usage_count = metadata.get("usage_count", 0)

            # Check if unused
            is_unused = False
            days_since_use = None

            if last_used is None and usage_count == 0:
                # Never used
                is_unused = True
                days_since_use = "never"
            elif last_used:
                try:
                    last_used_dt = datetime.fromisoformat(
                        last_used.replace("Z", "+00:00")
                    )
                    days_since_use = (
                        datetime.now() - last_used_dt.replace(tzinfo=None)
                    ).days
                    is_unused = days_since_use >= days
                except (ValueError, AttributeError):
                    is_unused = True
                    days_since_use = "unknown"

            if is_unused:
                size = self.env_manager.get_environment_size(env_name)
                unused.append(
                    {
                        "name": env_name,
                        "days_since_use": days_since_use,
                        "usage_count": usage_count,
                        "size_bytes": size,
                        "python_version": metadata.get("python_version", "unknown"),
                        "created_at": metadata.get("created_at"),
                    }
                )

        # Sort by days since use (oldest first)
        unused.sort(
            key=lambda x: (
                float("inf")
                if x["days_since_use"] == "never"
                else float("inf")
                if x["days_since_use"] == "unknown"
                else x["days_since_use"]
            ),
            reverse=True,
        )

        return unused

    def find_low_usage_environments(self, max_usage: int = 5) -> list[dict[str, Any]]:
        """Find environments with low usage counts.

        Args:
            max_usage: Maximum usage count to consider as low usage

        Returns:
            List of low usage environment information
        """
        low_usage = []
        environments = self.env_manager.list()

        for env in environments:
            env_name = env["name"]
            metadata = self.env_manager.get_metadata(env_name)
            usage_count = metadata.get("usage_count", 0)

            if usage_count <= max_usage:
                size = self.env_manager.get_environment_size(env_name)
                low_usage.append(
                    {
                        "name": env_name,
                        "usage_count": usage_count,
                        "size_bytes": size,
                        "last_used": metadata.get("last_used"),
                        "python_version": metadata.get("python_version", "unknown"),
                        "created_at": metadata.get("created_at"),
                    }
                )

        # Sort by usage count (lowest first)
        low_usage.sort(key=lambda x: x["usage_count"])

        return low_usage

    def _calculate_derived_stats(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Calculate derived statistics from metadata.

        Args:
            metadata: Environment metadata

        Returns:
            Dictionary with derived statistics
        """
        stats = {}

        # Calculate age
        created_at = metadata.get("created_at")
        if created_at:
            try:
                created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                age_days = (datetime.now() - created_dt.replace(tzinfo=None)).days
                stats["age_days"] = age_days
            except (ValueError, AttributeError):
                stats["age_days"] = None
        else:
            stats["age_days"] = None

        # Calculate days since last use
        last_used = metadata.get("last_used")
        if last_used:
            try:
                last_used_dt = datetime.fromisoformat(last_used.replace("Z", "+00:00"))
                days_since_use = (
                    datetime.now() - last_used_dt.replace(tzinfo=None)
                ).days
                stats["days_since_use"] = days_since_use
            except (ValueError, AttributeError):
                stats["days_since_use"] = None
        else:
            stats["days_since_use"] = None

        # Usage frequency (usage per day since creation)
        usage_count = metadata.get("usage_count", 0)
        age_days = stats.get("age_days")

        if age_days and age_days > 0:
            stats["usage_frequency"] = usage_count / age_days
        else:
            stats["usage_frequency"] = 0

        return stats

    def _get_size_info(self, name: str) -> dict[str, Any]:
        """Get size information for an environment.

        Args:
            name: Environment name

        Returns:
            Dictionary with size information
        """
        try:
            size_bytes = self.env_manager.get_environment_size(name)

            # Convert to human readable
            if size_bytes < 1024:
                size_human = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_human = f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                size_human = f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                size_human = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

            return {
                "size_bytes": size_bytes,
                "size_human": size_human,
            }
        except Exception:
            return {
                "size_bytes": 0,
                "size_human": "unknown",
            }
