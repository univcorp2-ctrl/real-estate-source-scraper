from __future__ import annotations

from realestate_scraper.plugins.base import FieldRule, SitePlugin


INTL_FIELDS = (
    FieldRule("title", css=("h1", "title", "[data-testid='home-details-chip']")),
    FieldRule("price_text", labels=("Price", "Rent", "Guide price", "Asking price", "Sale price")),
    FieldRule("address_text", labels=("Address", "Location")),
    FieldRule("area_text", labels=("Area", "Floor area", "Land size", "Living area")),
    FieldRule("building_age_text", labels=("Year built", "Built")),
    FieldRule("property_type", labels=("Property type", "Type")),
)

GENERIC_INTERNATIONAL = SitePlugin(
    plugin_id="generic_international_listing",
    source_ids=(
        "zillow",
        "realtor",
        "redfin",
        "rightmove",
        "zoopla",
        "idealista",
        "realestate-au",
        "domain-au",
        "propertyguru-sg",
        "bayut",
        "propertyfinder-ae",
        "magicbricks",
        "acres99",
        "housing-com",
        "lamudi-ph",
        "property24",
        "daft",
    ),
    detail_url_patterns=(r"/property/", r"/properties/", r"/homedetails/", r"/home/", r"/listing/", r"/details/", r"/for-sale/", r"/to-rent/"),
    field_rules=INTL_FIELDS,
    notes="International portals often restrict automated access and use dynamic rendering. This is a low-confidence static HTML parser only.",
)

INTL_PLUGINS = [GENERIC_INTERNATIONAL]
