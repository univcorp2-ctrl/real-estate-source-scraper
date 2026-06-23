from __future__ import annotations

from pathlib import Path

import yaml

from realestate_scraper.models import Source

ALLOWED_TO_SCRAPE_STATUSES = {"pilot", "official_public_data"}
BLOCKED_STATUSES = {"blocked", "research_only"}


def _load_payload(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        payload = yaml.safe_load(f)
    if not isinstance(payload, dict) or "sources" not in payload:
        raise ValueError(f"{path} must contain top-level key: sources")
    return list(payload["sources"] or [])


def load_sources(path: str | Path) -> list[Source]:
    path = Path(path)
    items = _load_payload(path)
    extra_path = path.with_name(f"{path.stem}.extra{path.suffix}")
    if extra_path.exists():
        items.extend(_load_payload(extra_path))
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
