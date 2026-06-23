from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import httpx
from openpyxl import Workbook

from realestate_scraper.models import Listing, Source
from realestate_scraper.plugins import get_plugin
from realestate_scraper.robots import RobotsCache, RobotsResult

DEFAULT_USER_AGENT = "RealEstateResearchBot/0.1 (+https://github.com/)"


@dataclass
class AuditRow:
    source_id: str
    source_name: str
    url: str
    review_status: str
    categories: str
    robots_status: str
    allowed: bool
    reason: str


class RealEstateScraper:
    def __init__(self, user_agent: str | None = None, timeout: float = 20.0, delay_seconds: float = 1.0) -> None:
        self.user_agent = user_agent or os.getenv("REAL_ESTATE_SCRAPER_USER_AGENT", DEFAULT_USER_AGENT)
        self.timeout = timeout
        self.delay_seconds = delay_seconds
        self.robots = RobotsCache(self.user_agent, timeout=timeout)
        self.client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": self.user_agent, "Accept-Language": "ja,en;q=0.8"},
        )

    def close(self) -> None:
        self.client.close()

    def audit_sources(self, sources: Iterable[Source]) -> list[AuditRow]:
        rows: list[AuditRow] = []
        for source in sources:
            target = source.seed_urls[0] if source.seed_urls else source.base_url
            result = self.robots.can_fetch(target)
            rows.append(
                AuditRow(
                    source_id=source.id,
                    source_name=source.name,
                    url=target,
                    review_status=source.review_status,
                    categories=",".join(source.categories),
                    robots_status=result.status,
                    allowed=result.allowed,
                    reason=result.reason,
                )
            )
        return rows

    def scrape_sources(self, sources: Iterable[Source], limit: int = 20) -> list[Listing]:
        listings: list[Listing] = []
        seen_urls: set[str] = set()
        for source in sources:
            plugin = get_plugin(source.id)
            for seed_url in source.seed_urls:
                if len(listings) >= limit:
                    return listings
                if not self._robots_allowed(seed_url):
                    continue
                try:
                    seed_html = self._fetch(seed_url)
                except httpx.HTTPError:
                    continue
                time.sleep(self.delay_seconds)
                detail_links = plugin.discover(seed_html, seed_url, source)
                if not detail_links and source.scrape_strategy not in {"api_or_data_download", "metadata_only"}:
                    detail_links = [seed_url]
                for link in detail_links:
                    if len(listings) >= limit:
                        return listings
                    if link in seen_urls:
                        continue
                    seen_urls.add(link)
                    if not self._robots_allowed(link):
                        continue
                    try:
                        html = seed_html if link == seed_url else self._fetch(link)
                    except httpx.HTTPError:
                        continue
                    listings.append(plugin.extract(html, link, source))
                    time.sleep(self.delay_seconds)
        return listings

    def _robots_allowed(self, url: str) -> bool:
        result: RobotsResult = self.robots.can_fetch(url)
        return result.allowed

    def _fetch(self, url: str) -> str:
        response = self.client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type and content_type:
            raise httpx.HTTPError(f"unsupported content type: {content_type}")
        return response.text


def write_listings(listings: list[Listing], output_dir: str | Path) -> dict[str, str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "listings.jsonl"
    csv_path = output_dir / "listings.csv"
    xlsx_path = output_dir / "listings.xlsx"
    manifest_path = output_dir / "run_manifest.json"

    rows = [listing.to_dict() for listing in listings]
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    fieldnames = list(rows[0].keys()) if rows else list(Listing(source_id="", source_name="", url="").to_dict().keys())
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    wb = Workbook()
    ws = wb.active
    ws.title = "listings"
    ws.append(fieldnames)
    for row in rows:
        ws.append([row.get(field, "") for field in fieldnames])
    wb.save(xlsx_path)

    manifest = {"count": len(rows), "files": [str(jsonl_path), str(csv_path), str(xlsx_path)]}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"jsonl": str(jsonl_path), "csv": str(csv_path), "xlsx": str(xlsx_path), "manifest": str(manifest_path)}


def write_audit(rows: list[AuditRow], output: str | Path) -> str:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(rows[0]).keys()) if rows else list(AuditRow("", "", "", "", "", "", False, "").__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    return str(output)
