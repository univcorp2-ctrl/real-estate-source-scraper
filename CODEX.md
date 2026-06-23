# CODEX

## Mission

Create and maintain a compliant, config-driven real estate source inventory and scraper.

## Rules

- Do not bypass robots.txt, login, CAPTCHA, paywalls, or rate limits.
- Prefer official APIs, official CSV/data downloads, RSS, and written permission.
- Keep `data/sources.yml` as the source of truth.
- Add tests whenever parsers or source schemas change.
- Keep CI green.

## Common commands

```bash
pip install -e '.[dev]'
ruff check .
pytest -q
python -m realestate_scraper list-sites --sources data/sources.yml --top 20
python -m realestate_scraper audit --sources data/sources.yml --output outputs/audit.csv
```
