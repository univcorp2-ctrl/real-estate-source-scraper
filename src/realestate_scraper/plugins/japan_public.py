from __future__ import annotations

from realestate_scraper.plugins.base import FieldRule, SitePlugin


BIT_COURTS = SitePlugin(
    plugin_id="bit_courts",
    source_ids=("bit-courts",),
    detail_url_patterns=(r"/app/", r"/detail/", r"/info/", r"/pdf/", r"/top/"),
    field_rules=(
        FieldRule("title", labels=("物件名", "事件番号", "売却区分番号"), css=("h1", "h2")),
        FieldRule("price_text", labels=("売却基準価額", "買受可能価額", "評価額")),
        FieldRule("address_text", labels=("所在地", "物件所在地", "所在地・交通")),
        FieldRule("area_text", labels=("土地面積", "建物面積", "専有面積")),
        FieldRule("property_type", labels=("種類", "物件種別", "財産種別")),
    ),
    notes="Public auction source. Top page exposes auction search, sale result, historical data, schedules, and help. Treat PDF document sets as official documents and store metadata first.",
)

NTA_KOUBAI = SitePlugin(
    plugin_id="nta_koubai",
    source_ids=("nta-koubai",),
    detail_url_patterns=(r"/auctionx/public/hp\d+\.php", r"/auctionx/public/", r"/public/"),
    field_rules=(
        FieldRule("title", labels=("名称", "財産名称", "売却区分番号"), css=("h1", "h2", ".contents h2")),
        FieldRule("price_text", labels=("見積価額", "公売保証金", "価額")),
        FieldRule("address_text", labels=("所在地", "財産所在地", "住所")),
        FieldRule("area_text", labels=("地積", "床面積", "土地面積", "建物面積")),
        FieldRule("property_type", labels=("財産の種類", "財産区分", "種類")),
    ),
    notes="National Tax Agency public sale pages expose public land/building categories. Login and e-Tax flows are out of scope.",
)

MOF_NATIONAL_PROPERTY = SitePlugin(
    plugin_id="mof_national_property",
    source_ids=("mof-national-property",),
    detail_url_patterns=(r"/policy/national_property/", r"/national_property/list/", r"\.pdf$", r"\.html?$"),
    field_rules=(
        FieldRule("title", labels=("物件名", "所在地"), css=("h1", "h2")),
        FieldRule("price_text", labels=("予定価格", "売却価格", "価格")),
        FieldRule("address_text", labels=("所在地", "住所")),
        FieldRule("area_text", labels=("数量", "面積", "土地面積")),
        FieldRule("property_type", labels=("区分", "種類")),
    ),
    notes="Ministry of Finance national property sale source. Prefer official tables/downloads; PDF parsing should be separate and low-load.",
)

MLIT_REINFO = SitePlugin(
    plugin_id="mlit_reinfolib",
    source_ids=("mlit-reinfolib", "mlit-landprice", "reins-market"),
    detail_url_patterns=(r"/help/apiManual/", r"/api/", r"/landPrice/"),
    field_rules=(
        FieldRule("title", css=("h1", "h2", "title")),
        FieldRule("property_type", regex=r"(不動産取引価格情報|地価公示|地価調査|国土数値情報|API)"),
    ),
    notes="Official market-data/API/download source. Prefer API connector or official download rather than HTML detail crawling.",
)

PUBLIC_PLUGINS = [BIT_COURTS, NTA_KOUBAI, MOF_NATIONAL_PROPERTY, MLIT_REINFO]
