# CI Status

GitHub Actions workflow file `.github/workflows/ci.yml` could not be committed by the automation worker. The GitHub API returned `404: Not Found` only for files under `.github/workflows/`, while normal repository files were committed successfully.

The same CI steps are available in `scripts/ci.sh`, and the exact workflow template is stored at `docs/github-actions-ci-template.yml`.

Expected CI steps:

1. checkout
2. setup-python 3.11
3. install package with dev dependencies
4. ruff check
5. pytest
6. source inventory validation
7. upload output preview artifact
