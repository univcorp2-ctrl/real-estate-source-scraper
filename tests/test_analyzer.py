from realestate_scraper.analyzer import render_site_analysis_markdown, summarize_html_structure, summarize_robots_text


def test_summarize_robots_text_counts_rules() -> None:
    summary = summarize_robots_text(
        "https://example.com/robots.txt",
        "User-agent: *\nDisallow: /private\nAllow: /public\nCrawl-delay: 5\nSitemap: https://example.com/sitemap.xml\n",
        200,
    )
    assert summary.fetch_status == "ok"
    assert summary.disallow_count == 1
    assert summary.allow_count == 1
    assert summary.crawl_delay == "5"
    assert any("Disallow" in rule for rule in summary.important_rules)


def test_summarize_html_structure_detects_links_and_labels() -> None:
    html = """
    <html><head><title>Search</title></head><body>
      <h1>Listings</h1>
      <form action="/search"><input name="q"></form>
      <a href="/property/1">Property</a>
      <dl><dt>Price</dt><dd>$100</dd></dl>
    </body></html>
    """
    summary = summarize_html_structure(html, "https://example.com/", [r"/property/"])
    assert summary.title == "Search"
    assert summary.forms[0]["action"] == "https://example.com/search"
    assert summary.likely_detail_links == ["https://example.com/property/1"]
    assert "Price" in summary.detected_labels


def test_render_site_analysis_markdown_empty() -> None:
    markdown = render_site_analysis_markdown([])
    assert "Generated Site Analysis" in markdown
