from __future__ import annotations

from realestate_scraper.plugins.base import GenericPlugin, SitePlugin
from realestate_scraper.plugins.international import INTL_PLUGINS
from realestate_scraper.plugins.japan_portals import JP_PORTAL_PLUGINS
from realestate_scraper.plugins.japan_public import PUBLIC_PLUGINS

_PLUGINS: list[SitePlugin] = [*PUBLIC_PLUGINS, *JP_PORTAL_PLUGINS, *INTL_PLUGINS]
_GENERIC = GenericPlugin()


def list_plugins() -> list[SitePlugin]:
    return list(_PLUGINS)


def get_plugin(source_id: str) -> SitePlugin:
    for plugin in _PLUGINS:
        if source_id in plugin.source_ids:
            return plugin
    return _GENERIC
