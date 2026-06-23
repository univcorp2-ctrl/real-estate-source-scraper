from realestate_scraper.models import Source
from realestate_scraper.plugins import get_plugin, list_plugins


def test_dedicated_plugin_is_registered() -> None:
    assert get_plugin("suumo").plugin_id == "suumo"
    assert get_plugin("bit-courts").plugin_id == "bit_courts"
    assert get_plugin("rakumachi").plugin_id == "rakumachi"
    assert list_plugins()


def test_generic_plugin_extracts_common_html() -> None:
    plugin = get_plugin("unknown-source")
    source = Source(
        id="unknown-source",
        name="Unknown",
        base_url="https://example.com/",
        country="US",
        language="en",
        categories=["residential-sale"],
        review_status="pilot",
        scrape_strategy="generic_html",
        seed_urls=["https://example.com/"],
    )
    html = """
    <html><head><title>123 Main Street</title></head><body>
      <h1>123 Main Street</h1>
      <dl><dt>Price</dt><dd>$500000</dd><dt>Address</dt><dd>123 Main Street</dd><dt>Area</dt><dd>1200 sqft</dd></dl>
    </body></html>
    """
    listing = plugin.extract(html, "https://example.com/property/1", source)
    assert listing.title == "123 Main Street"
    assert listing.price_text == "$500000"
    assert listing.address_text == "123 Main Street"
    assert listing.area_text == "1200 sqft"
