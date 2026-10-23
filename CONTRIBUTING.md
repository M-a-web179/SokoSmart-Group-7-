# Contributing to SokoSmart

Thanks for helping build SokoSmart! This guide explains how our team works so
that contributions are fast to review and safe to merge.

## Quick start

1. **Fork / clone** the repository and install dependencies:
   ```bash
   git clone https://github.com/M-a-web179/SokoSmart-Group-7-.git
   cd SokoSmart-Group-7-/services/price-service
   python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```
2. **Pick an issue** from the [GitHub Projects board](../../projects) — check
   the *Backlog* column and assign yourself, so two people don't build the
   same thing.
3. **Create a branch** from the latest `main` (see naming below).
4. **Code + test** — every feature or fix needs a test in `tests/`.
5. **Open a pull request** using the template, link the issue
   (`Closes #12`), and request a review.

## Branch naming

| Prefix | Use |
|---|---|
| `feature/<name>` | New functionality |
| `fix/<name>` | Bug fixes |
| `devops/<name>` | CI/CD, Docker, Terraform, repo config |
| `docs/<name>` | Documentation only |

## Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add USSD price-reporting flow
fix: correct summary rounding for whole numbers
docs: explain how to run the app with Docker
chore: bump dependencies
test: cover USSD back-navigation
ci: add gitleaks secret scanning
build: add Dockerfile
infra: add ECS task definition
```

Keep commits small and focused — one logical change per commit.

## Pull request rules (enforced by branch protection on `main`)

- ✅ At least **1 approving review**
- ✅ All **CI status checks pass** (tests, secret scanning)
- ✅ **Conversations resolved** before merging
- ✅ Branch **up to date** with `main`
- ✅ Stale approvals are dismissed when new commits are pushed
- 🚫 No direct pushes to `main` — administrators included

## Code style

- **Python**: follow the existing layering — `routes.py` (HTTP) →
  `services.py` (business logic) → `repository.py` (data access). No business
  logic in routes; no storage access outside the repository.
- **Tests**: pytest, one behaviour per test, named `test_<what_it_does>`.
  Run `pytest -v` before pushing.
- **Infrastructure**: Terraform in `infra/`, formatted with `terraform fmt`
  and validated with `terraform validate`. Never commit `*.tfvars` or state
  files (they are gitignored — keep it that way).
- **Security**: never commit secrets, API keys or `.env` files. Dependabot
  and Gitleaks run automatically; fix their findings before merging.

## Definition of Done

A task is done when:

- [ ] Code works locally (`python run.py`, try the API/UI/USSD)
- [ ] Tests pass locally **and** in CI
- [ ] Docs updated (README / architecture notes) if behaviour changed
- [ ] PR approved and all conversations resolved
- [ ] Issue closed and the Projects board card moved to *Done*

## Getting help

- Stuck for more than 30 minutes? Ask in the team channel — don't spin.
- Disagree with a review comment? Reply in the thread and resolve it as a
  team; don't dismiss feedback silently.
- Found a security problem? Do **not** open a public issue — tell the team
  lead directly so it can be fixed before disclosure.
