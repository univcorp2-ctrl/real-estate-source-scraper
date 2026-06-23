from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    base_url: str
    country: str
    language: str
    categories: list[str]
    review_status: str
    scrape_strategy: str
    priority: int = 3
    seed_urls: list[str] = field(default_factory=list)
    item_url_patterns: list[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Source":
        required = ["id", "name", "base_url", "country", "language", "categories", "review_status", "scrape_strategy"]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"source missing required fields: {missing}")
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            base_url=str(data["base_url"]),
            country=str(data["country"]),
            language=str(data["language"]),
            categories=list(data["categories"] or []),
            review_status=str(data["review_status"]),
            scrape_strategy=str(data["scrape_strategy"]),
            priority=int(data.get("priority", 3)),
            seed_urls=list(data.get("seed_urls") or [data["base_url"]]),
            item_url_patterns=list(data.get("item_url_patterns") or []),
            notes=str(data.get("notes", "")),
        )


@dataclass
class Listing:
    source_id: str
    source_name: str
    url: str
    title: str = ""
    price_text: str = ""
    yield_text: str = ""
    address_text: str = ""
    station_text: str = ""
    area_text: str = ""
    building_age_text: str = ""
    property_type: str = ""
    fetched_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    raw_text_hash: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "url": self.url,
            "title": self.title,
            "price_text": self.price_text,
            "yield_text": self.yield_text,
            "address_text": self.address_text,
            "station_text": self.station_text,
            "area_text": self.area_text,
            "building_age_text": self.building_age_text,
            "property_type": self.property_type,
            "fetched_at": self.fetched_at,
            "raw_text_hash": self.raw_text_hash,
        }


def stable_hash(text: str) -> str:
    return sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]
