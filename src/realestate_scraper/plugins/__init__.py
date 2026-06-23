"""Site-specific scraper plugins."""

from realestate_scraper.plugins.registry import get_plugin, list_plugins

__all__ = ["get_plugin", "list_plugins"]
