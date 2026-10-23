# SokoSmart

SokoSmart is a web-based agricultural price platform designed to help small-scale farmers and market traders in East Africa make better selling decisions by providing crop price information and market price records.

The project addresses a practical African agricultural challenge: farmers and small traders often lack timely, reliable price information and may sell produce at unfavorable prices because they cannot easily compare prices across markets.

## Problem

Smallholder farmers and informal market traders often depend on word of mouth or local knowledge to decide where and when to sell produce. This can lead to:

- Selling at lower prices than those available in nearby markets.
- Limited visibility of price differences between markets.
- Difficulty recording and sharing reliable price information.
- Reduced bargaining power for farmers and small traders.

## Solution

SokoSmart provides a simple REST API where users can record, view, update, and delete crop price information. This creates a foundation for future tools that help farmers compare market prices before selling.

## Target Users

- Small-scale farmers who want to compare selling prices.
- Market traders and vendors tracking produce prices.
- Agricultural cooperatives collecting market data.
- Local administrators who maintain market price records.

## Value Proposition

SokoSmart gives farmers and traders a structured way to store and access crop price information. By making price records available through a simple API, the platform can support future mobile, web, or USSD-based tools for comparing market prices.

## Current Features

### Price Service API

The backend provides a REST API for managing crop price records.

- `GET /health` — checks that the service is running.
- `GET /api/prices` — returns all recorded prices.
- `GET /api/prices/<price_id>` — returns one price record.
- `POST /api/prices` — creates a new price record.
- `PUT /api/prices/<price_id>` — updates an existing price record.
- `DELETE /api/prices/<price_id>` — deletes a price record.

Example request:

```bash
curl -X POST http://localhost:5000/api/prices \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "Maize",
    "market": "Kimironko Market",
    "price": 650,
    "unit": "RWF/kg"
  }'
```

## Project Structure

```text
.
├── .github/
│   └── workflows/
├── services/
│   └── price-service/
│       ├── app/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── repository.py
│       │   └── routes.py
│       ├── tests/
│       ├── requirements.txt
│       └── requirements-dev.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- pip
- Git

### Clone the Repository

```bash
git clone [https://github.com/M-a-web179/SokoSmart-Group-7-.git](https://github.com/M-a-web179/SokoSmart-Group-7-.git)
cd SokoSmart-Group-7-
```

### Set Up the Price Service

```bash
cd services/price-service
python -m venv venv
source venv/bin/activate
```

On Windows PowerShell:

```powershell
cd services/price-service
python -m venv venv
venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run the API

```bash
flask --app app run --debug
```

Then open:

```text
http://localhost:5000/health
```

### Run Tests

```bash
pytest -v
```

### Run Linting

```bash
ruff check .
```

Automatically fix supported lint issues:

```bash
ruff check . --fix
```

## CI/CD

The repository uses GitHub Actions to automatically run:

- Unit tests with `pytest`.
- Python linting with `ruff`.
- Secret scanning with Gitleaks.

Pull requests must pass the required checks before they can be merged.

## Security Practices

- `.env` files and other secrets are excluded through `.gitignore`.
- Gitleaks scans pull requests for accidentally committed secrets.
- Branch protection requires reviews and passing CI checks before merging.

## Future Improvements

Planned future work includes:

- A USSD interface for farmers using basic mobile phones.
- A web dashboard for browsing and managing price records.
- Docker support for easier deployment.
- PostgreSQL persistence for long-term price data.
- Terraform configuration for cloud infrastructure.

## Contributing

1. Create a feature branch from `main`.
2. Make your changes.
3. Run tests and linting locally.
4. Open a pull request.
5. Request review from a teammate.
6. Merge only after CI passes and the PR is approved.

## Team

| Member | Contribution |
|---|---|
|Matthew | Project foundation, documentation, and repository setup |
| Dominion | CI, linting, formatting, and secure collaboration workflow |
| Victor | USSD menu, Docker support, Dependabot, and secret scanning |
| Hamzat | Web dashboard, Terraform plan, and contributing guide |

## License

This project is for educational purposes as part of a software engineering group project.
