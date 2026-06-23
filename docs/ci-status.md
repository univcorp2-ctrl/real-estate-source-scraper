# CI Status

Last updated: 2026-06-23

The repository contents, source inventory, scraper implementation, tests, documentation, devcontainer, and local CI runner were committed successfully.

GitHub Actions workflow creation is blocked for files under `.github/workflows/` from the automation worker. The GitHub API returned `404: Not Found` only for workflow paths while ordinary repository files were committed successfully.

Retry history:

1. `.github/workflows/ci.yml` -> GitHub API 404
2. `.github/workflows/ci.yml` retry -> GitHub API 404
3. `.github/workflows/site-analysis-ci.yaml` -> GitHub API 404

Because the workflow file cannot be committed, no GitHub Actions run exists yet and `checkGitHubCiV120` returns `status: not_found`.

The exact workflow content is stored in `docs/github-actions-ci-template.yml`, and equivalent local CI steps are stored in `scripts/ci.sh`.

Expected test command:

```bash
scripts/ci.sh
```

Expected CI steps:

1. checkout
2. setup-python 3.11
3. install package with dev dependencies
4. ruff check
5. pytest
6. source inventory validation
7. upload output preview artifact

This is not a code/test failure. It is a workflow-file creation failure caused by the GitHub API rejecting `.github/workflows/*` writes for the current automation context.
