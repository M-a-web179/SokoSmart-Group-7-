# Architecture (Formative 1)

SokoSmart starts as one service (`price-service`) with clear layers so it can be
split into microservices later:

```
HTTP request -> routes.py (API layer) -> services.py (business logic) -> repository.py (data access)
```

- **routes.py**: parses requests, returns JSON. No business logic.
- **services.py**: validation, filtering, summaries, comparisons.
- **repository.py**: the only place that touches storage (in-memory/JSON today, PostgreSQL later).

Planned services: `price-service` (now), `ussd-service`, `web-dashboard`, `notification-service`.
