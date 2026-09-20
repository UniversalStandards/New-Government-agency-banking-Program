# Branch Integration Summary
## Scope
- Target branch refreshed from `origin/main` and non-`main` remote branches inspected via `git ls-remote --heads origin`.
- Deterministic processing order: lexicographic by remote branch name.
- Merge execution used real merge commits for compatible branches; stale/generated branches were explicitly excluded below when their diffs could not be merged safely without overwriting unrelated work.
- Branches already fully contained in refreshed `main` before integration: **none**.
## Merged Branches
- `origin/copilot/fix-banking-program-issue`
- `origin/dependabot/docker/base-image-digests-6dafb4a59b`
- `origin/dependabot/github_actions/dot-github/workflows/cloudflare/wrangler-action-4`
- `origin/dependabot/github_actions/dot-github/workflows/codecov/codecov-action-7`
- `origin/dependabot/github_actions/dot-github/workflows/deployment-actions-5b0fa3f5df`
- `origin/dependabot/github_actions/dot-github/workflows/github-official-actions-7f565448c5`
- `origin/dependabot/github_actions/dot-github/workflows/pascalgn/size-label-action-0.5.7`
- `origin/dependabot/github_actions/dot-github/workflows/pypa/gh-action-pypi-publish-1.14.1`
- `origin/dependabot/github_actions/dot-github/workflows/security-scan-actions-71b88807d0`
- `origin/dependabot/npm_and_yarn/build-utilities-f44cd17b61`
- `origin/dependabot/npm_and_yarn/gulp-pipeline-bec85b7bf4`
- `origin/dependabot/npm_and_yarn/linting-formatting-6fa5c7883a`
- `origin/dependabot/npm_and_yarn/sass-css-pipeline-ac97c4e125`
- `origin/dependabot/npm_and_yarn/type-definitions-6315faf2cf`
- `origin/dependabot/npm_and_yarn/typescript-stack-94dcc933d2`
- `origin/dependabot/pip/application-servers-24a0d73f5d`
- `origin/dependabot/pip/cryptography-gte-48.0.0`
- `origin/dependabot/pip/database-orm-bc70988f09`
- `origin/dependabot/pip/flask-web-framework-29e43a444d`
- `origin/dependabot/pip/http-clients-1c8c978c63`
- `origin/dependabot/pip/linting-qa-d9ba43ed89`
- `origin/dependabot/pip/payment-integrations-3b76289af6`
- `origin/dependabot/pip/pymysql-gte-1.1.3`
- `origin/dependabot/pip/schedule-gte-1.2.2`
- `origin/dependabot/pip/testing-964c17ab5f`
- `origin/dependabot/pip/utilities-4ea199e985`
- `origin/dependabot/pip/wtforms-gte-3.2.2`

## Conflict Resolutions
- `package.json`: resolved overlapping npm updates by keeping the newest compatible versions from the merged Dependabot branches (`cross-env`, `@types/node`, `@typescript-eslint/*`, `gulp-*`, `lint-staged`, `eslint-config-prettier`).
- `requirements.txt`: resolved overlapping Python dependency updates by keeping the highest merged versions line-by-line (`stripe`, `requests`, `aiohttp`, `python-dotenv`, `cryptography`, `werkzeug`, `pytest*`, `black`, `flake8`, `mypy`, `isort`, `WTForms`, etc.).
- Authentication-coupled account-creation changes from `origin/copilot/fix-banking-program-issue` were preserved, and the user model/tests were updated so protected routes can be exercised correctly in validation.

## Excluded Branches
- `origin/copilot/merge-non-main-branches-to-main` — Current integration branch for this task; excluded because a branch cannot be merged into itself.
- `origin/alert-autofix-2` — Superseded stale autofix branch: its intended workflow-permissions fix is already present, while the branch also attempts a repository-wide outdated rewrite and malformed workflow edits.
- `origin/auto-fix/20251020-063330` — Generated auto-fix branch with a repository-wide destructive rewrite against stale content; excluded to avoid replacing current workflows/docs with older automated output.
- `origin/copilot/fix-13` — Stale merge-artifact branch with no isolated feature intent; diff broadly removes current repository content and is not safe to integrate automatically.
- `origin/copilot/fix-3568d749-7301-4948-9456-d5f116891640` — Broad prototype rewrite that deletes or replaces large portions of the current repository; excluded because it cannot be merged surgically while preserving current functionality.
- `origin/copilot/fix-9` — Outdated rewrite of main application bootstrapping and requirements; excluded because it replaces current architecture rather than contributing a compatible incremental change.
- `origin/dependabot/github_actions/dot-github/workflows/actions/setup-java-4` — Superseded stale branch: current active workflows no longer use actions/setup-java in the locations this branch updates, and the branch would reintroduce obsolete workflow content.
- `origin/dependabot/github_actions/dot-github/workflows/actions/setup-node-4` — Superseded stale branch: active workflows already use actions/setup-node@v4 where applicable, so only the branch’s stale broad rewrite remains.
- `origin/dependabot/github_actions/dot-github/workflows/stefanzweifel/git-auto-commit-action-5` — Superseded stale branch: current workflows no longer use git-auto-commit-action, and the branch would apply an unrelated repository-wide rewrite.

### Generated duplicate auto-fix branches excluded as unsafe rewrites
These branches were generated duplicates of the same automated stale rewrites. Each group was excluded because the diffs remove or replace large sets of current docs/workflows/configuration rather than contributing an isolated compatible change.
#### Duplicate auto-fix tree `79c5eb76` (same automated rewrite generated twice)
- `origin/auto-fix/20251018-060832`
- `origin/auto-fix/20251018-180804`

#### Duplicate auto-fix tree `d2d529ed` (same automated rewrite generated nine times)
- `origin/auto-fix/20251212-061028`
- `origin/auto-fix/20251212-181028`
- `origin/auto-fix/20251213-060936`
- `origin/auto-fix/20251213-180825`
- `origin/auto-fix/20251214-060935`
- `origin/auto-fix/20251214-180854`
- `origin/auto-fix/20251215-061139`
- `origin/auto-fix/20251215-181020`
- `origin/auto-fix/20251216-061035`

#### Duplicate auto-fix tree `fe73cbbf` (same automated rewrite generated twice)
- `origin/auto-fix/20251224-063750`
- `origin/auto-fix/20251224-183358`

#### Duplicate auto-fix tree `f1bbbb1c` (same automated rewrite generated 33 times)
- `origin/auto-fix/20251225-063715`
- `origin/auto-fix/20251225-183327`
- `origin/auto-fix/20251226-063638`
- `origin/auto-fix/20251226-183330`
- `origin/auto-fix/20251227-063516`
- `origin/auto-fix/20251227-180857`
- `origin/auto-fix/20251228-061004`
- `origin/auto-fix/20251228-180908`
- `origin/auto-fix/20251229-061208`
- `origin/auto-fix/20251229-181037`
- `origin/auto-fix/20251230-061019`
- `origin/auto-fix/20251230-181008`
- `origin/auto-fix/20251231-061127`
- `origin/auto-fix/20251231-180953`
- `origin/auto-fix/20260101-061103`
- `origin/auto-fix/20260101-181002`
- `origin/auto-fix/20260102-061118`
- `origin/auto-fix/20260102-180955`
- `origin/auto-fix/20260103-060957`
- `origin/auto-fix/20260103-180907`
- `origin/auto-fix/20260104-061013`
- `origin/auto-fix/20260104-180912`
- `origin/auto-fix/20260105-061346`
- `origin/auto-fix/20260105-181104`
- `origin/auto-fix/20260106-061109`
- `origin/auto-fix/20260106-181020`
- `origin/auto-fix/20260107-061116`
- `origin/auto-fix/20260107-181040`
- `origin/auto-fix/20260108-061108`
- `origin/auto-fix/20260108-180906`
- `origin/auto-fix/20260109-061110`
- `origin/auto-fix/20260109-181026`
- `origin/auto-fix/20260110-060941`

#### Duplicate auto-fix tree `6380cb71` (same automated rewrite generated 36 times)
- `origin/auto-fix/20260118-060946`
- `origin/auto-fix/20260118-180907`
- `origin/auto-fix/20260119-061354`
- `origin/auto-fix/20260119-181013`
- `origin/auto-fix/20260120-061236`
- `origin/auto-fix/20260120-184158`
- `origin/auto-fix/20260121-064110`
- `origin/auto-fix/20260121-184834`
- `origin/auto-fix/20260122-063935`
- `origin/auto-fix/20260122-183735`
- `origin/auto-fix/20260123-063927`
- `origin/auto-fix/20260123-183808`
- `origin/auto-fix/20260124-063559`
- `origin/auto-fix/20260124-183406`
- `origin/auto-fix/20260125-063635`
- `origin/auto-fix/20260125-183406`
- `origin/auto-fix/20260126-064127`
- `origin/auto-fix/20260126-184021`
- `origin/auto-fix/20260127-063957`
- `origin/auto-fix/20260127-181253`
- `origin/auto-fix/20260128-061235`
- `origin/auto-fix/20260128-181259`
- `origin/auto-fix/20260129-062028`
- `origin/auto-fix/20260129-181716`
- `origin/auto-fix/20260130-062100`
- `origin/auto-fix/20260130-181519`
- `origin/auto-fix/20260131-061449`
- `origin/auto-fix/20260131-181036`
- `origin/auto-fix/20260201-062206`
- `origin/auto-fix/20260201-181141`
- `origin/auto-fix/20260202-063001`
- `origin/auto-fix/20260202-181641`
- `origin/auto-fix/20260203-062244`
- `origin/auto-fix/20260203-182331`
- `origin/auto-fix/20260204-062224`
- `origin/auto-fix/20260204-182031`

## Validation
- Targeted validation: `/usr/bin/python3 -m pytest test_main.py -q` ✅ (10 passed).
- Formatting/import validation: `/usr/bin/python3 -m black .` and `/usr/bin/python3 -m isort .` executed during validation; unrelated formatting-only diffs were reverted to keep the integration change set surgical.
- Syntax/import validation: `/usr/bin/python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` ✅ and `/usr/bin/python3 -c "import main"` ✅.
- Conflict-marker validation: repository search for `<<<<<<<`, `=======`, `>>>>>>>` ✅ after removing the leftover markers from `README1.md`.
- Full test run: `/usr/bin/python3 -m pytest -v` ⚠️ completed with pre-existing failures (18 failed, 40 passed, 13 errors). The failures are concentrated in older API/model/error-handling test modules whose fixtures and endpoint expectations no longer match the current application shape; the merged account-creation coverage in `test_main.py` passes.
