from __future__ import annotations

import csv
from pathlib import Path

import yaml

from realestate_scraper.models import Source

ALLOWED_TO_SCRAPE_STATUSES = {"pilot", "official_public_data"}
BLOCKED_STATUSES = {"blocked", "research_only"}


def _load_yaml_payload(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        payload = yaml.safe_load(f)
    if not isinstance(payload, dict) or "sources" not in payload:
        raise ValueError(f"{path} must contain top-level key: sources")
    return list(payload["sources"] or [])


def _load_csv_payload(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("id"):
                continue
            categories = [item.strip() for item in row.get("categories", "residential-sale").split(";") if item.strip()]
            base_url = row["base_url"].strip()
            rows.append(
                {
                    "id": row["id"].strip(),
                    "name": row["name"].strip(),
                    "base_url": base_url,
                    "country": row.get("country", "GLOBAL").strip() or "GLOBAL",
                    "language": row.get("language", "en").strip() or "en",
                    "categories": categories,
                    "review_status": row.get("review_status", "needs_review").strip() or "needs_review",
                    "scrape_strategy": row.get("scrape_strategy", "generic_html").strip() or "generic_html",
                    "priority": int(row.get("priority", "5") or 5),
                    "seed_urls": [row.get("seed_url", "").strip() or base_url],
                    "item_url_patterns": [item.strip() for item in row.get("item_url_patterns", "").split(";") if item.strip()],
                    "notes": row.get("notes", "").strip(),
                }
            )
    return rows


def _inventory_files(path: Path) -> list[Path]:
    files = [path]
    for candidate in sorted(path.parent.glob("sources*.yml")):
        if candidate != path and candidate not in files:
            files.append(candidate)
    for candidate in sorted(path.parent.glob("sources*.csv")):
        if candidate not in files:
            files.append(candidate)
    return files


def load_sources(path: str | Path) -> list[Source]:
    path = Path(path)
    items: list[dict] = []
    for inventory_file in _inventory_files(path):
        if inventory_file.suffix.lower() in {".yml", ".yaml"}:
            items.extend(_load_yaml_payload(inventory_file))
        elif inventory_file.suffix.lower() == ".csv":
            items.extend(_load_csv_payload(inventory_file))
    sources = [Source.from_dict(item) for item in items]
    validate_sources(sources)
    return sources


def validate_sources(sources: list[Source]) -> None:
    ids = [source.id for source in sources]
    duplicates = sorted({source_id for source_id in ids if ids.count(source_id) > 1})
    if duplicates:
        raise ValueError(f"duplicate source ids: {duplicates}")
    for source in sources:
        if not source.base_url.startswith(("http://", "https://")):
            raise ValueError(f"{source.id}: base_url must be http(s)")
        if not source.categories:
            raise ValueError(f"{source.id}: categories must not be empty")
        if source.review_status in BLOCKED_STATUSES and source.scrape_strategy not in {"research_only", "metadata_only"}:
            raise ValueError(f"{source.id}: blocked/research_only sources must not use active scrape strategy")


def filter_sources(
    sources: list[Source],
    category: str | None = None,
    source_id: str | None = None,
    include_needs_review: bool = False,
) -> list[Source]:
    filtered: list[Source] = []
    for source in sources:
        if category and category not in source.categories:
            continue
        if source_id and source.id != source_id:
            continue
        if source.review_status in BLOCKED_STATUSES:
            continue
        if source.review_status not in ALLOWED_TO_SCRAPE_STATUSES and not include_needs_review:
            continue
        filtered.append(source)
    return filtered
