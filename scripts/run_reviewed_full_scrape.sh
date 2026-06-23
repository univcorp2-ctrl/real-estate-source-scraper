#!/usr/bin/env bash
set -euo pipefail
mkdir -p outputs/reviewed
python -m realestate_scraper scrape \
  --sources data/sources.yml \
  --include-needs-review \
  --limit "${SCRAPE_LIMIT:-200}" \
  --delay-seconds "${SCRAPE_DELAY_SECONDS:-3}" \
  --output-dir outputs/reviewed
