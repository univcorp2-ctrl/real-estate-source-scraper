from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup

from realestate_scraper.extract import clean_text, discover_links, extract_listing_from_html
from realestate_scraper.models import Listing, Source


@dataclass(frozen=True)
class FieldRule:
    field: str
    labels: tuple[str, ...] = ()
    css: tuple[str, ...] = ()
    regex: str | None = None


@dataclass(frozen=True)
class SitePlugin:
    """Site-specific parser.

    Plugins parse public HTML that has already passed robots.txt checks. They do
    not log in, bypass CAPTCHA, evade access controls, or call private APIs.
    """

    plugin_id: str
    source_ids: tuple[str, ...]
    detail_url_patterns: tuple[str, ...]
    field_rules: tuple[FieldRule, ...] = ()
    same_host_only: bool = True
    notes: str = ""

    def discover(self, html: str, base_url: str, source: Source) -> list[str]:
        patterns = list(self.detail_url_patterns or tuple(source.item_url_patterns))
        return discover_links(html, base_url, patterns, same_host_only=self.same_host_only)

    def extract(self, html: str, url: str, source: Source) -> Listing:
        listing = extract_listing_from_html(html, url, source)
        soup = BeautifulSoup(html, "html.parser")
        page_text = clean_text(soup.get_text("\n", strip=True))
        for rule in self.field_rules:
            value = self._extract_by_rule(soup, page_text, rule)
            if value and hasattr(listing, rule.field):
                setattr(listing, rule.field, value)
        return listing

    def _extract_by_rule(self, soup: BeautifulSoup, page_text: str, rule: FieldRule) -> str:
        for selector in rule.css:
            node = soup.select_one(selector)
            if node:
                value = clean_text(node.get_text(" ", strip=True))
                if value:
                    return value
        for label in rule.labels:
            value = extract_labeled_value(soup, label)
            if value:
                return value
            value = extract_labeled_value_from_text(page_text, label)
            if value:
                return value
        if rule.regex:
            match = re.search(rule.regex, page_text, flags=re.IGNORECASE | re.MULTILINE)
            if match:
                return clean_text(match.group(1))
        return ""


class GenericPlugin(SitePlugin):
    def __init__(self) -> None:
        super().__init__(
            plugin_id="generic",
            source_ids=(),
            detail_url_patterns=(
                r"/property/",
                r"/properties/",
                r"/detail/",
                r"/details/",
                r"/listing/",
                r"/listings/",
                r"/estate/",
                r"/realestate/",
                r"/bukken/",
                r"/chintai/",
                r"/sale/",
                r"/rent/",
                r"/buy/",
                r"/for-sale/",
                r"/to-rent/",
                r"/homedetails/",
                r"/inmueble/",
                r"/annunci/",
                r"/imovel/",
            ),
            field_rules=(
                FieldRule("title", css=("h1", "title")),
                FieldRule("price_text", labels=("価格", "販売価格", "賃料", "家賃", "Price", "Rent", "Asking price")),
                FieldRule("yield_text", labels=("利回り", "表面利回り", "想定利回り", "Yield")),
                FieldRule("address_text", labels=("所在地", "住所", "Address", "Location")),
                FieldRule("station_text", labels=("交通", "最寄駅", "Station", "Access")),
                FieldRule("area_text", labels=("専有面積", "土地面積", "建物面積", "Area", "Floor area", "Land size")),
                FieldRule("building_age_text", labels=("築年月", "築年数", "Year built", "Built")),
                FieldRule("property_type", labels=("物件種別", "種別", "Property type", "Type")),
            ),
            notes="Generic parser for all inventory sources. It is label/regex based and requires source-specific validation for production.",
        )


def extract_labeled_value(soup: BeautifulSoup, label: str) -> str:
    label_pattern = re.compile(rf"^\s*{re.escape(label)}\s*$", flags=re.IGNORECASE)
    for node in soup.find_all(string=label_pattern):
        parent = node.parent
        if not parent:
            continue
        if parent.name in {"dt", "th"}:
            sibling = parent.find_next_sibling(["dd", "td"])
            if sibling:
                value = clean_text(sibling.get_text(" ", strip=True))
                if value:
                    return value
        row = parent.find_parent("tr")
        if row:
            cells = row.find_all(["td", "th"])
            for index, cell in enumerate(cells[:-1]):
                if clean_text(cell.get_text(" ", strip=True)).lower() == label.lower():
                    value = clean_text(cells[index + 1].get_text(" ", strip=True))
                    if value:
                        return value
    return ""


def extract_labeled_value_from_text(text: str, label: str) -> str:
    pattern = re.compile(rf"{re.escape(label)}\s*[:：]?\s*([^\n\r]{{1,160}})", flags=re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return ""
    return clean_text(match.group(1))
