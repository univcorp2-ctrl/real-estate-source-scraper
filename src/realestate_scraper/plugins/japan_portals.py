from __future__ import annotations

from realestate_scraper.plugins.base import FieldRule, SitePlugin


COMMON_JP_FIELDS = (
    FieldRule("title", css=("h1", "title")),
    FieldRule("price_text", labels=("価格", "販売価格", "賃料", "家賃")),
    FieldRule("yield_text", labels=("利回り", "表面利回り", "想定利回り")),
    FieldRule("address_text", labels=("所在地", "住所")),
    FieldRule("station_text", labels=("交通", "最寄駅", "沿線・駅")),
    FieldRule("area_text", labels=("専有面積", "土地面積", "建物面積", "床面積")),
    FieldRule("building_age_text", labels=("築年月", "築年数")),
    FieldRule("property_type", labels=("物件種別", "種別", "種類")),
)

SUUMO = SitePlugin(
    plugin_id="suumo",
    source_ids=("suumo",),
    detail_url_patterns=(r"/chintai/", r"/ms/", r"/ikkodate/", r"/tochi/", r"/jj/"),
    field_rules=COMMON_JP_FIELDS,
    notes="SUUMO robots.txt contains many Disallow rules for internal endpoints, printout paths, parameterized sort/search URLs, and API-like paths. Bingbot has Crawl-delay: 30.",
)

LIFULL_HOMES = SitePlugin(
    plugin_id="lifull_homes",
    source_ids=("lifull-homes", "homes-toushi", "lifull-akiyabank"),
    detail_url_patterns=(r"/chintai/", r"/mansion/", r"/kodate/", r"/tochi/", r"/toushi/", r"/akiyabank/"),
    field_rules=COMMON_JP_FIELDS,
    notes="Large residential portal plus investment/vacant-home branches. Use official partnership/API/data feed for production where possible.",
)

ATHOME = SitePlugin(
    plugin_id="athome",
    source_ids=("athome", "athome-toushi"),
    detail_url_patterns=(r"/chintai/", r"/mansion/", r"/kodate/", r"/tochi/", r"/toushi/", r"/office/"),
    field_rules=COMMON_JP_FIELDS,
    notes="Residential, commercial, and investment portal. Parser handles common table/dl labels only.",
)

YAHOO_REALESTATE = SitePlugin(
    plugin_id="yahoo_realestate",
    source_ids=("yahoo-realestate",),
    detail_url_patterns=(r"/rent/", r"/used/", r"/new/", r"/land/", r"/detail/"),
    field_rules=COMMON_JP_FIELDS,
    notes="Some routes may be dynamic. Use static public pages only where robots permits.",
)

RAKUMACHI = SitePlugin(
    plugin_id="rakumachi",
    source_ids=("rakumachi",),
    detail_url_patterns=(r"/syuuekibukken/", r"/property/"),
    field_rules=COMMON_JP_FIELDS,
    notes="Investment-property portal. Validate one public detail page and update CSS selectors before production.",
)

KENBIYA = SitePlugin(
    plugin_id="kenbiya",
    source_ids=("kenbiya",),
    detail_url_patterns=(r"/pp", r"/income/", r"/property/"),
    field_rules=COMMON_JP_FIELDS,
    notes="Investment-property portal. Label-based parser must be validated against live allowed pages.",
)

UR_RENT = SitePlugin(
    plugin_id="ur_rent",
    source_ids=("ur-net",),
    detail_url_patterns=(r"/chintai/", r"/kanto/", r"/kansai/", r"/detail/"),
    field_rules=COMMON_JP_FIELDS,
    notes="Public-housing style rental source. Still requires live robots check before fetch.",
)

JP_PORTAL_PLUGINS = [SUUMO, LIFULL_HOMES, ATHOME, YAHOO_REALESTATE, RAKUMACHI, KENBIYA, UR_RENT]
