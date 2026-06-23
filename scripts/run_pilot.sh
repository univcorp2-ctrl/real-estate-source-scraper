#!/usr/bin/env bash
set -euo pipefail
python -m realestate_scraper list-sites --sources data/sources.yml --category public-auction --top 20
python -m realestate_scraper scrape --sources data/sources.yml --category public-auction --limit 20 --output-dir outputs
