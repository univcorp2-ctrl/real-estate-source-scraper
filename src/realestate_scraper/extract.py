from __future__ import annotations

import re
from html import unescape
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from realestate_scraper.models import Listing, Source, stable_hash

PRICE_RE = re.compile(
    r"(?:(?:価格|販売価格|賃料|家賃|Price|Rent)[:：\s]*)?([0-9０-９,.]+\s*(?:億円|万円|円|yen|JPY|USD|ドル|€|EUR|£|GBP))",
    re.IGNORECASE,
)
YIELD_RE = re.compile(r"(?:利回り|表面利回り|想定利回り|Yield)[:：\s]*([0-9０-９.]+\s*%)", re.IGNORECASE)
AREA_RE = re.compile(r"(?:専有面積|土地面積|建物面積|面積|Area)[:：\s]*([0-9０-９.,]+\s*(?:m2|㎡|平米|坪|sqft|sq ft))", re.IGNORECASE)
AGE_RE = re.compile(r"(?:築年数|築年月|築|Built|Year built)[:：\s]*([^\n\r]{2,40})", re.IGNORECASE)
STATION_RE = re.compile(r"(?:最寄駅|交通|駅徒歩|Station|Access)[:：\s]*([^\n\r]{2,80})", re.IGNORECASE)
ADDRESS_RE = re.compile(r"(?:所在地|住所|Address|Location)[:：\s]*([^\n\r]{2,120})", re.IGNORECASE)

PROPERTY_KEYWORDS = [
    "一棟マンション",
    "区分マンション",
    "アパート",
    "マンション",
    "戸建",
    "一戸建て",
    "土地",
    "店舗",
    "オフィス",
    "ビル",
    "物流",
    "倉庫",
    "Apartment",
    "House",
    "Condo",
    "Land",
    "Office",
    "Retail",
]


def clean_text(text: str) -> str:
    text = unescape(text)
    text = re.sub(r"[\t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def page_title(soup: BeautifulSoup) -> str:
    for selector in ["h1", "meta[property='og:title']", "title"]:
        node = soup.select_one(selector)
        if not node:
            continue
        if node.name == "meta":
            value = node.get("content", "")
        else:
            value = node.get_text(" ", strip=True)
        if value:
            return clean_text(value)
    return ""


def first_match(regex: re.Pattern[str], text: str) -> str:
    match = regex.search(text)
    if not match:
        return ""
    return clean_text(match.group(1))


def detect_property_type(text: str) -> str:
    for keyword in PROPERTY_KEYWORDS:
        if keyword.lower() in text.lower():
            return keyword
    return ""


def extract_listing_from_html(html: str, url: str, source: Source) -> Listing:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "noscript", "svg"]):
        node.decompose()
    text = clean_text(soup.get_text("\n", strip=True))
    return Listing(
        source_id=source.id,
        source_name=source.name,
        url=url,
        title=page_title(soup),
        price_text=first_match(PRICE_RE, text),
        yield_text=first_match(YIELD_RE, text),
        address_text=first_match(ADDRESS_RE, text),
        station_text=first_match(STATION_RE, text),
        area_text=first_match(AREA_RE, text),
        building_age_text=first_match(AGE_RE, text),
        property_type=detect_property_type(text),
        raw_text_hash=stable_hash(text),
    )


def discover_links(html: str, base_url: str, patterns: list[str], same_host_only: bool = True) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    base_host = re.sub(r"^www\.", "", __import__("urllib.parse").parse.urlparse(base_url).netloc)
    compiled = [re.compile(pattern) for pattern in patterns]
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href"))
        absolute = urljoin(base_url, href)
        parsed = __import__("urllib.parse").parse.urlparse(absolute)
        host = re.sub(r"^www\.", "", parsed.netloc)
        if same_host_only and host != base_host:
            continue
        if compiled and not any(pattern.search(absolute) for pattern in compiled):
            continue
        if absolute not in links:
            links.append(absolute)
    return links
