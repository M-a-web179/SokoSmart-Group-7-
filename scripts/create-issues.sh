#!/usr/bin/env bash
set -euo pipefail

REPO="M-a-web179/sokosmart"
U1="member1-username"
U2="member2-username"
U3="member3-username"
U4="member4-username"
MS="Formative 1 - Project Foundation"

for l in "feature:0e8a16" "bug:d73a4a" "devops:1d76db" "security:b60205" "documentation:0075ca" "setup:fbca04" "testing:5319e7"; do
  gh label create "${l%%:*}" --color "${l##*:}" --repo "$REPO" --force
done

gh api "repos/$REPO/milestones" -f title="$MS" -f due_on="2026-10-23T21:59:00Z" \
  -f description="Formative 1 deadline: Friday 11:59 PM" >/dev/null 2>&1 || echo "Milestone exists, continuing"

issue() {
  local body url
  body=$(printf '**User story:** %s\n\n**Acceptance criteria:**\n%b' "$4" "$5")
  url=$(gh issue create --repo "$REPO" --title "$1" --label "$2" --assignee "$3" --milestone "$MS" --body "$body")
  echo "$url"
  if [ "${6:-}" = "close" ]; then gh issue close "$url" >/dev/null; fi
}

issue "Set up GitHub repository and add collaborators" "setup" "$U1" \
  "N/A (setup task)" "- [x] Repo created with MIT license\n- [x] All members added as collaborators\n- [x] Issues and Projects enabled" close
issue "Write project README" "documentation" "$U1" \
  "As a new contributor, I want a clear README so that I can understand and run the project quickly." \
  "- [x] Name, tagline, problem, users, features, stack\n- [x] Install and run instructions" close
issue "Configure .gitignore and verify no secrets are committed" "setup,security" "$U1" \
  "As a team, we want secrets and junk files ignored so that nothing sensitive reaches GitHub." \
  "- [x] .env, venv, node_modules, IDE, logs, OS files ignored\n- [x] git ls-files shows no secrets" close
issue "Set up branch protection on main" "security,devops" "$U1" \
  "As a team lead, I want main protected so that no unreviewed code is merged." \
  "- [x] PR required, 1 approval, stale approvals dismissed\n- [x] Status checks, up-to-date branch, conversation resolution\n- [x] Applies to administrators" close
issue "Create GitHub Projects board and initial issues" "setup,documentation" "$U1" \
  "As a team, we want a Kanban board so that everyone can see who is doing what." \
  "- [x] Backlog / In Progress / Done columns\n- [x] 12+ issues with labels, assignees, milestone" close

issue "Build core price service: list and filter prices" "feature" "$U1" \
  "As a farmer, I want to see crop prices in different markets so that I know where to sell." \
  "- [ ] GET /api/prices returns all prices\n- [ ] Filtering by crop and market works\n- [ ] Runs locally using README steps"
issue "Add price reporting with validation and summary/compare endpoints" "feature" "$U1" \
  "As a market agent, I want to report prices so that farmers see fresh data." \
  "- [ ] POST /api/prices validates input (400 on bad data)\n- [ ] /api/prices/summary and /api/crops/<crop>/compare work"
issue "Review and test the core price service PR" "testing" "$U2" \
  "As a team, we want peer review so that code quality stays high." \
  "- [ ] Pull the branch and run pytest\n- [ ] Try the API with curl\n- [ ] Leave review comments and approve"

issue "Add USSD-style menu with two levels" "feature" "$U3" \
  "As a feature-phone user, I want a USSD menu so that I can check prices without internet." \
  "- [ ] Level 1: choose crop\n- [ ] Level 2: show prices by market\n- [ ] Unit tests for menu navigation"
issue "Build simple web dashboard" "feature" "$U4" \
  "As a trader, I want a web page of prices so that I can compare markets visually." \
  "- [ ] Page lists summary table\n- [ ] Crop filter works\n- [ ] Mobile friendly"
issue "Replace in-memory store with PostgreSQL" "feature,devops" "$U2" \
  "As an operator, I want persistent storage so that reported prices survive restarts." \
  "- [ ] New repository class using PostgreSQL\n- [ ] Config via environment variables\n- [ ] Existing tests still pass"
issue "Plan and extend CI pipeline (GitHub Actions)" "devops" "$U2" \
  "As a developer, I want automated checks on every PR so that broken code is caught early." \
  "- [ ] Workflow runs pytest on PRs (starter exists)\n- [ ] Add linting (ruff or flake8)\n- [ ] Status check required on main"
issue "Plan containerization (Dockerfile and docker-compose)" "devops" "$U3" \
  "As a DevOps engineer, I want a container image so that the app runs the same everywhere." \
  "- [ ] Dockerfile for price-service\n- [ ] docker-compose with app + database\n- [ ] Documented in README"
issue "Plan Terraform / cloud deployment" "devops" "$U4" \
  "As a team, we want infrastructure as code so that deployments are repeatable." \
  "- [ ] Architecture diagram in docs/\n- [ ] Cloud provider and services chosen\n- [ ] Terraform skeleton in infra/"
issue "Enable Dependabot and secret scanning" "security" "$U3" \
  "As a team, we want automatic security alerts so that vulnerable dependencies are fixed fast." \
  "- [ ] Dependabot enabled for pip\n- [ ] Secret scanning and push protection on"
issue "Write CONTRIBUTING guide and architecture diagram" "documentation" "$U4" \
  "As a new contributor, I want contribution rules so that my PRs follow team standards." \
  "- [ ] Branch, commit and PR conventions\n- [ ] Architecture diagram added to docs/"

echo "Done. Add the issues to your Project board (Add item > paste issues, or enable the auto-add workflow)."
