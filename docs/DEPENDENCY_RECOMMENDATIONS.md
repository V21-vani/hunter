# Dependency Recommendations

All recommendations favor free, open-source, and lightweight options consistent with the preferred architecture and free-tier deployment constraint.

## 1. Frontend (Next.js + TypeScript + Tailwind)

| Package | Purpose | Version / Notes |
|---------|---------|-----------------|
| `next` | React framework (App Router) | Latest LTS |
| `react` / `react-dom` | UI library | Latest |
| `typescript` | Type safety | Latest |
| `tailwindcss` | Styling | Latest |
| `postcss`, `autoprefixer` | Tailwind tooling | Latest |
| `lucide-react` | Icons | MIT |
| `clsx` + `tailwind-merge` | ClassName utilities | MIT |
| `zod` | Schema validation (form/API) | MIT |
| `axios` or native `fetch` | HTTP client | — |
| `date-fns` | Date formatting | MIT |
| `vitest` + `testing-library` | Unit/component testing | MIT |

## 2. Backend (Python FastAPI)

| Package | Purpose | Version / Notes |
|---------|---------|-----------------|
| `fastapi` | Web framework | Latest |
| `uvicorn` | ASGI server | Latest |
| `sqlalchemy` | ORM | 2.0+ |
| `alembic` | Migrations | Latest |
| `psycopg2-binary` | PostgreSQL driver | Latest |
| `pydantic` | Data validation / settings | v2 |
| `pydantic-settings` | `.env` config | v2 |
| `httpx` | HTTP client for crawling | Latest |
| `beautifulsoup4` | HTML parsing | Latest |
| `lxml` | BS4 parser backend | Latest |
| `playwright` | JS-rendered page crawling | Latest (browsers installed via `playwright install`) |
| `apscheduler` | Lightweight background scheduler | Latest |
| `python-jose[cryptography]` or `pyjwt` | JWT auth | MIT/Apache |
| `passlib[bcrypt]` | Password hashing | If self-managed auth |
| `python-dotenv` | Load `.env` in dev | Latest |
| `structlog` | Structured logging | Latest |
| `pytest` + `pytest-asyncio` | Testing | Latest |
| `factory-boy` | Test data factories | Latest |
| `httpx` (for TestClient) | API testing | via FastAPI TestClient |

## 3. Optional / Later-Stage (Not MVP)

| Package | Purpose | When to add |
|---------|---------|-------------|
| `spacy` | NLP for enrichment (skills, duration) | Post-MVP if regex insufficient |
| `langchain` | LLM-based enrichment | Post-MVP |
| `celery` + `redis` | Heavy background jobs | If APScheduler outgrown |
| `strawberry` / `ariadne` | GraphQL | If frontend needs flexible queries |
| `prometheus-client` | Metrics | Observability stage |

## 4. Dev / CI / Linting

| Package | Purpose |
|---------|---------|
| `ruff` | Linting + formatting (fast, replaces flake8+black+isort) |
| `mypy` | Static type checking |
| `pre-commit` | Pre-commit hooks |
| `github-actions` | CI workflow (lint, test, docker build) |

## 5. Infrastructure (Free Tier)

| Component | Recommendation | Free Tier |
|-----------|----------------|-----------|
| PostgreSQL | Supabase or Neon | 500 MB / 0.5 GB |
| Frontend hosting | Vercel | Hobby (free) |
| Backend hosting | Render or Railway | Render free tier (web service spins down) |
| Background worker | Render cron / GitHub Actions scheduled | Free |
| Domain | Vercel/Railway subdomain | Free |
| Email (alerts) | Resend or SendGrid | Free tier |

## 6. Version Pinning Strategy

- Use exact versions in `requirements.txt` / `package.json` for reproducibility.
- Use `pip-compile` (pip-tools) or `poetry` lockfile for backend if desired; `requirements.txt` is simplest for free-tier deploys.
- Frontend: `package-lock.json` committed.

## 7. What to Avoid (Paid / Heavy)

- No AWS RDS (costs money even at small sizes).
- No Celery + Redis unless APScheduler proves insufficient.
- No commercial crawling APIs (Apify, Bright Data) — use direct httpx/Playwright against public pages.
- No proprietary auth (Auth0 paid tiers) — self-managed JWT or Supabase Auth free tier.
