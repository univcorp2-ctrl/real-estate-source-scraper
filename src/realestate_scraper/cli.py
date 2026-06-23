from __future__ import annotations

import argparse
import json
from pathlib import Path

from realestate_scraper.scraper import RealEstateScraper, write_audit, write_listings
from realestate_scraper.sources import filter_sources, load_sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Real estate source inventory, audit, and scraper")
    sub = parser.add_subparsers(dest="command", required=True)

    list_sites = sub.add_parser("list-sites", help="List configured sources")
    list_sites.add_argument("--sources", default="data/sources.yml")
    list_sites.add_argument("--category")
    list_sites.add_argument("--top", type=int, default=0)

    audit = sub.add_parser("audit", help="Audit robots availability for configured sources")
    audit.add_argument("--sources", default="data/sources.yml")
    audit.add_argument("--category")
    audit.add_argument("--output", default="outputs/audit.csv")

    scrape = sub.add_parser("scrape", help="Scrape allowed/pilot sources with low load")
    scrape.add_argument("--sources", default="data/sources.yml")
    scrape.add_argument("--category")
    scrape.add_argument("--source-id")
    scrape.add_argument("--limit", type=int, default=20)
    scrape.add_argument("--output-dir", default="outputs")
    scrape.add_argument(
        "--include-needs-review",
        action="store_true",
        help="Include sources marked needs_review after your own legal/contract review. robots.txt is still enforced.",
    )
    scrape.add_argument("--delay-seconds", type=float, default=1.0)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    sources = load_sources(args.sources)

    if args.command == "list-sites":
        rows = sources
        if args.category:
            rows = [source for source in rows if args.category in source.categories]
        rows = sorted(rows, key=lambda item: (item.priority, item.id))
        if args.top:
            rows = rows[: args.top]
        for source in rows:
            print(
                json.dumps(
                    {
                        "id": source.id,
                        "name": source.name,
                        "base_url": source.base_url,
                        "categories": source.categories,
                        "review_status": source.review_status,
                        "strategy": source.scrape_strategy,
                    },
                    ensure_ascii=False,
                )
            )
        return 0

    scraper = RealEstateScraper(delay_seconds=getattr(args, "delay_seconds", 1.0))
    try:
        if args.command == "audit":
            rows = sources
            if args.category:
                rows = [source for source in rows if args.category in source.categories]
            output = write_audit(scraper.audit_sources(rows), args.output)
            print(f"audit written: {output}")
            return 0

        if args.command == "scrape":
            rows = filter_sources(
                sources,
                category=args.category,
                source_id=args.source_id,
                include_needs_review=args.include_needs_review,
            )
            listings = scraper.scrape_sources(rows, limit=args.limit)
            files = write_listings(listings, Path(args.output_dir))
            print(json.dumps({"count": len(listings), "files": files}, ensure_ascii=False, indent=2))
            return 0
    finally:
        scraper.close()

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
