from realestate_scraper.extract import discover_links, extract_listing_from_html
from realestate_scraper.models import Source


def source() -> Source:
    return Source(
        id="sample",
        name="Sample Site",
        base_url="https://example.com/",
        country="JP",
        language="ja",
        categories=["investment"],
        review_status="pilot",
        scrape_strategy="generic_html",
        seed_urls=["https://example.com/list"],
        item_url_patterns=[r"/property/"],
    )


def test_extract_listing_from_japanese_html() -> None:
    html = """
    <html><head><title>一棟マンション 東京都渋谷区</title></head>
    <body>
      <h1>渋谷区 一棟マンション</h1>
      <dl>
        <dt>価格</dt><dd>1億2,000万円</dd>
        <dt>表面利回り</dt><dd>5.7%</dd>
        <dt>所在地</dt><dd>東京都渋谷区本町</dd>
        <dt>交通</dt><dd>初台駅 徒歩8分</dd>
        <dt>土地面積</dt><dd>120.4㎡</dd>
        <dt>築年月</dt><dd>2010年4月</dd>
      </dl>
    </body></html>
    """
    listing = extract_listing_from_html(html, "https://example.com/property/1", source())
    assert listing.title == "渋谷区 一棟マンション"
    assert listing.price_text == "1億2,000万円"
    assert listing.yield_text == "5.7%"
    assert "東京都渋谷区" in listing.address_text
    assert listing.property_type == "一棟マンション"
    assert listing.raw_text_hash


def test_discover_links_filters_by_pattern_and_host() -> None:
    html = """
    <a href='/property/1'>detail</a>
    <a href='https://example.com/news/2'>news</a>
    <a href='https://other.example.com/property/3'>external</a>
    """
    links = discover_links(html, "https://example.com/list", [r"/property/"])
    assert links == ["https://example.com/property/1"]
