#!/usr/bin/env bash
set -euo pipefail
mkdir -p outputs/site-analysis outputs/safe
python -m realestate_scraper list-sites --sources data/sources.yml --top 0 > outputs/all_sources.jsonl
python -m realestate_scraper analyze-sites --sources data/sources.yml --limit 0 --output-dir outputs/site-analysis
python -m realestate_scraper audit --sources data/sources.yml --output outputs/audit.csv
python -m realestate_scraper scrape --sources data/sources.yml --limit 200 --delay-seconds 1 --output-dir outputs/safe
