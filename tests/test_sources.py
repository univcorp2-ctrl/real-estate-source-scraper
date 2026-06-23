from pathlib import Path

from realestate_scraper.sources import filter_sources, load_sources


def test_sources_file_is_large_and_valid() -> None:
    sources = load_sources(Path("data/sources.yml"))
    assert len(sources) >= 100
    assert len({source.id for source in sources}) == len(sources)
    categories = {category for source in sources for category in source.categories}
    assert "investment" in categories
    assert "public-auction" in categories
    assert "residential-rent" in categories


def test_filter_excludes_needs_review_by_default() -> None:
    sources = load_sources(Path("data/sources.yml"))
    filtered = filter_sources(sources, category="investment")
    assert all(source.review_status in {"pilot", "official_public_data"} for source in filtered)


def test_filter_can_include_reviewed_sources() -> None:
    sources = load_sources(Path("data/sources.yml"))
    filtered = filter_sources(sources, category="investment", include_needs_review=True)
    assert any(source.review_status == "needs_review" for source in filtered)
