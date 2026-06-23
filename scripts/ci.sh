#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
pip install -e '.[dev]'
ruff check .
pytest -q
python -m realestate_scraper list-sites --sources data/sources.yml --top 5
mkdir -p outputs
python -m realestate_scraper list-sites --sources data/sources.yml --category public-auction --top 10 > outputs/source_preview.jsonl
