# Setup and Operations

## ローカル開発

```bash
git clone <repo-url>
cd real-estate-source-scraper
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Codespaces

GitHubのリポジトリ画面で `Code` → `Codespaces` → `Create codespace on main` を押すだけで、Python 3.11 と依存関係の入った環境を作れます。

## サイト一覧の確認

```bash
python -m realestate_scraper list-sites --sources data/sources.yml --top 20
python -m realestate_scraper list-sites --sources data/sources.yml --category investment
```

## 監査

```bash
python -m realestate_scraper audit --sources data/sources.yml --output outputs/audit.csv
```

`outputs/audit.csv` に `allowed`, `robots_status`, `reason` が出ます。

## 収集

```bash
python -m realestate_scraper scrape --sources data/sources.yml --category public-auction --limit 20 --output-dir outputs
```

`needs_review` のソースを含める場合は、各サイトの規約・robots・契約・許諾を確認した後にのみ以下を使います。

```bash
python -m realestate_scraper scrape --sources data/sources.yml --category investment --include-needs-review --limit 10
```

## User-Agent

```bash
export REAL_ESTATE_SCRAPER_USER_AGENT="RealEstateResearchBot/0.1 contact:you@example.com"
```

## GitHub Actionsで成果物を作る

`.github/workflows/ci.yml` は手動実行 `workflow_dispatch` に対応しています。将来、本番収集をActionsで行う場合は、許諾済みサイトだけを対象にした別workflowを作るのが安全です。

## Secrets

現時点で必須Secretsはありません。将来、公式APIを使う場合は以下のような名前でGitHub Actions Secretsに保存してください。

- `MLIT_API_KEY`
- `PROPERTY_DATA_VENDOR_API_KEY`
- `SLACK_WEBHOOK_URL`

実値はリポジトリにコミットしないでください。

## トラブルシューティング

- 取得件数が0件: robotsで不許可、HTMLではなくJS描画、リンクパターン不一致の可能性があります。
- 文字化け: CSVは `utf-8-sig` で保存しています。ExcelではXLSXを優先してください。
- 抽出精度が低い: 汎用抽出なので、サイト別pluginを追加してください。
- 403/429: アクセス頻度を下げ、公式API・データ契約を検討してください。
