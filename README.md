# SokoSmart

> **Know the market price before you go to market.**

SokoSmart is a crop market-price tracker for smallholder farmers and traders in East Africa. Farmers and market agents report prices; anyone can compare the same crop across markets and see where it is cheapest or where it sells best.

## Problem Statement
Smallholder farmers often sell crops without knowing current prices in nearby markets. Middlemen exploit this information gap, so farmers lose income and buyers overpay. Price data exists mostly by word of mouth and is rarely shared in a structured, accessible way.

## Target Users
- **Smallholder farmers** deciding where and when to sell
- **Market traders and small retailers** deciding where to buy stock
- **Market agents / cooperative staff** who report daily prices
- **NGOs and local government** monitoring food prices

## Core Features
1. **View prices** for crops across markets, with filtering by crop and market
2. **Report a price** with validation (crop, market, price, unit, date)
3. **Price summary**: average, min, max, cheapest and most expensive market per crop
4. **Market comparison** for one crop, cheapest first
5. *(Planned)* USSD menu for feature-phone users and a web dashboard

## Technology Stack
| Layer | Choice |
|---|---|
| Language / framework | Python 3.10+, Flask |
| Data (now) | In-memory store seeded from JSON |
| Data (planned) | PostgreSQL |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Containers (planned) | Docker, Docker Compose |
| Cloud / IaC (planned) | Terraform on AWS |

## Project Structure
```
sokosmart/
├── .github/                 # CODEOWNERS, PR template, CI workflow
├── docs/                    # Architecture notes
├── infra/                   # Terraform (planned)
├── scripts/                 # Helper scripts (issue creation)
└── services/
    └── price-service/
        ├── app/
        │   ├── routes.py        # HTTP layer
        │   ├── services.py      # Business logic
        │   ├── repository.py    # Data access
        │   ├── models.py        # Data models
        │   └── config.py        # Env-based config
        ├── data/seed_prices.json
        ├── tests/
        ├── requirements.txt
        └── run.py
```
The routes → services → repository layering keeps concerns separate so the service can later be split into microservices.

## Getting Started (run locally)

**Prerequisites:** Python 3.10+ and Git.

```bash
# 1. Clone
git clone https://github.com/<ORG_OR_USER>/sokosmart.git
cd sokosmart/services/price-service

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# 3. Install dependencies
pip install -r requirements-dev.txt

# 4. (Optional) configure environment
cp .env.example .env              # Windows: copy .env.example .env

# 5. Run the app  ->  http://localhost:5000
python run.py

# 6. Run the tests
pytest -v
```

### Try the API
```bash
curl http://localhost:5000/health
curl "http://localhost:5000/api/prices?crop=maize"
curl http://localhost:5000/api/prices/summary
curl http://localhost:5000/api/crops/maize/compare
curl -X POST http://localhost:5000/api/prices \
  -H "Content-Type: application/json" \
  -d '{"crop":"maize","market":"Huye","price":410}'
```
On Windows PowerShell use `curl.exe` or `Invoke-RestMethod`, or simply open the GET URLs in your browser.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/prices?crop=&market=` | List/filter prices |
| POST | `/api/prices` | Report a new price |
| GET | `/api/prices/summary` | Per-crop statistics |
| GET | `/api/crops/<crop>/compare` | Compare markets for a crop |

## Team Workflow
- `main` is protected: **no direct pushes**; all changes go through pull requests with at least 1 approval.
- Branch names: `feature/<name>`, `fix/<name>`, `devops/<name>`, `docs/<name>`.
- Commit style: `feat:`, `fix:`, `docs:`, `chore:`, `test:`, `ci:`.
- Every PR links an issue and is tracked on the GitHub Projects board.

## License
MIT. See [LICENSE](LICENSE).
