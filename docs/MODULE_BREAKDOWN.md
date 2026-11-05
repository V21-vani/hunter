# Module Breakdown

InternRadar is organized into independent modules. Each source has its own adapter. Discovery, verification, enrichment, ranking, and monitoring are separate services with their own tables and failure boundaries.

## Recommended Repository Structure

```
internradar/
├── docs/                          # Phase 0 deliverables and architecture
├── frontend/                      # Next.js + TypeScript + Tailwind
│   ├── app/                       # App Router
│   │   ├── (dashboard)/
│   │   ├── (auth)/
│   │   ├── api/                   # API routes (optional BFF)
│   │   └── layout.tsx
│   ├── components/
│   ├── lib/                       # api client, utils
│   ├── styles/
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── next.config.js
├── backend/                       # Python FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app factory
│   │   ├── api/                   # REST route v1
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── opportunities.py
│   │   │       ├── sources.py
│   │   │       ├── verification.py
│   │   │       ├── enrichment.py
│   │   │       ├── ranking.py
│   │   │       ├── monitoring.py
│   │   │       ├── alerts.py
│   │   │       └── auth.py
│   │   ├── core/                  # config, security, logging
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/                    # SQLAlchemy + Alembic
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── alembic/
│   │   ├── models/
│   │   │   ├── opportunity.py
│   │   │   ├── source_run.py
│   │   │   ├── verification.py
│   │   │   ├── enrichment.py
│   │   │   ├── ranking.py
│   │   │   ├── monitoring_history.py
│   │   │   ├── user.py
│   │   │   └── alert.py
│   │   ├── schemas/
│   │   │   ├── opportunity.py
│   │   │   ├── source_run.py
│   │   │   ├── verification.py
│   │   │   ├── enrichment.py
│   │   │   ├── ranking.py
│   │   │   ├── user.py
│   │   │   └── alert.py
│   │   ├── services/
│   │   │   ├── discovery_service.py
│   │   │   ├── verification_service.py
│   │   │   ├── enrichment_service.py
│   │   │   ├── ranking_service.py
│   │   │   └── monitoring_service.py
│   │   ├── adapters/              # source adapters (ONE PER SOURCE)

## Module 2 — Ingest & Normalize

**Purpose**: Receive raw candidates, convert to canonical schema, deduplicate.

**Components**:
- `api/v1/ingest.py` — receive raw opportunities (from adapters or webhooks).
- `services/discovery_service.py` — orchestrates adapter discovery -> ingest -> normalize.
- `utils/normalize.py` — map source-specific fields to canonical `Opportunity` schema.
- `utils/dedupe.py` — dedupe by `(source, source_id)` and fuzzy title+company matching.

**Output**: Canonical `opportunity` row with `status = 'discovered'`.

## Module 3 — Verification

**Purpose**: Establish that the employer actually has an active opening.

**Components**:
- `services/verification_service.py` — re-checks the source URL or company career page.
- `api/v1/verification.py` — manual verify trigger.
- `models/verification.py` — stores `is_active`, `evidence`, `method`, `checked_at`.

**Logic**:
- Fetch `source_url`; check for keywords indicating the role is filled/closed.
- Compare against known "filled" signals (e.g., "no longer accepting", "position closed").
- Store `verification_evidence` (screenshot path, matched snippet, timestamp).
- Update `opportunities.verification_status` and `status` (`verified` or `rejected`).

**Failure boundary**: Verification failures do not delete the opportunity; they mark `verification_status = 'unverified'` and allow re-check later.

## Module 4 — Enrichment

**Purpose**: Collect stipend, duration, location, and eligibility.

**Components**:
- `services/enrichment_service.py` — runs extraction on `description_raw`.
- `models/enrichment.py` — per-field enrichment with confidence scores.
- Extraction via regex + lightweight NLP (spaCy optional; regex-first for MVP).

**Fields extracted**:
- `stipend_min`, `stipend_max`, `stipend_currency`
- `duration_min_months`, `duration_max_months`
- `location`, `is_remote`
- `eligibility` (degree, batch, skills)

**Failure boundary**: Missing fields are stored as NULL with `confidence = 0`; opportunity still flows to ranking.

## Module 5 — Ranking

**Purpose**: Decide how valuable the opportunity is.

**Components**:
- `services/ranking_service.py` — computes score and stores factors.
- `models/ranking.py` — `score`, `factors` jsonb.

**Scoring factors (example weights, configurable)**:
- Stipend amount (INR): 30%
- Recency (days since posted): 20%
- Employer brand / company size: 25%
- India + remote fit: 25%

**Output**: `rank_score` on `opportunities`; full breakdown in `rankings.factors`.

**Failure boundary**: Ranking defaults to score 0 if factors missing; opportunity still visible but unranked.

## Module 6 — Monitoring

**Purpose**: Check whether an opportunity remains active over time.

**Components**:
- `workers/scheduler.py` — lightweight scheduler (APScheduler or cron-based).
- `workers/jobs.py` — per-opportunity re-check jobs.
- `services/monitoring_service.py` — triggers verification re-check, updates status.
- `models/monitoring_history.py` — audit trail of status transitions.

**Schedule**:
- New opportunities: re-check after 24h, 3d, 7d.
- Verified active: re-check every 7d.
- Expired/rejected: no further checks unless manually re-triggered.

**Failure boundary**: Monitor failures are logged; status unchanged; retry with backoff.

## Module 7 — Frontend (Next.js)

**Purpose**: User-facing dashboard for discovering and tracking internships.

**Pages**:
- `/` — landing / opportunity listings with search & filters.
- `/opportunities/[id]` — detail view with verification evidence and enrichment.
- `/auth/*` — login/signup (optional for MVP).
- `/dashboard` — saved searches, alerts, application tracking.

**Features**:
- Filter by source, location, remote, paid, stipend range, duration.
- Sort by rank score, recency.
- Subscribe to alerts (email/webhook).

## Module 8 — Auth & Users (MVP: optional)

**Purpose**: User accounts, saved searches, alerts.

**Components**:
- `models/user.py`, `models/alert.py`
- `api/v1/auth.py`
- JWT-based auth (Python `jose` / `pyjwt`) or delegate to Supabase Auth.

**Note**: Can be deferred to post-MVP; anonymous browsing is the default.

## Cross-Cutting Concerns

| Concern | Implementation |
|---------|----------------|
| Configuration | Pydantic `BaseSettings` (`core/config.py`), `.env` |
| Logging | Python `logging` + structlog (JSON logs) |
| Error handling | Global FastAPI exception handlers; per-adapter try/except |
| Testing | pytest + pytest-asyncio; factory_boy for test data |
| CI | GitHub Actions: lint, type-check (mypy), test, build Docker images |


## Module 1 — Discovery (Source Adapters)

**Purpose**: Find potential opportunities from public sources.

**Components**:
- `adapters/base.py` — abstract base class with `discover()` and `extract_enrichment()`.
- `adapters/registry.py` — maps source names to adapter classes.
- One adapter directory per source under `adapters/<source>/`.
- `crawling/http_client.py` — httpx-based client with retries, timeouts, user-agent rotation.
- `crawling/bs4_parser.py` — BeautifulSoup helpers for static HTML.
- `crawling/playwright_client.py` — Playwright for JS-rendered pages (LinkedIn, Instagram, etc.).

**Adapters (priority order)**:
1. `greenhouse` — public Greenhouse job boards (JSON API-friendly).
2. `lever` — public Lever job boards.
3. `ashby` — public Ashby boards.
4. `smartrecruiters` — public SmartRecruiters jobs.
5. `workday` — public Workday careers (often JS-rendered; needs Playwright).
6. `company_page` — generic company career page scraper.
7. `linkedin` — public company/founder/recruiter posts.
8. `x_twitter` — public posts.
9. `instagram` — public posts/reels.
10. `reddit` — hiring communities.
11. `telegram` — public channels.
12. `discord` — public communities.
13. `startup_board` — startup hiring boards / founder announcements.
14. `generic` — fallback for any other public source.

**Output**: `RawOpportunity` (source, source_id, source_url, title, company, description_raw, captured_at).

**Failure boundary**: Adapter errors are caught per-source; one failing adapter does not block others. Errors logged to `source_runs`.
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # abstract adapter contract
│   │   │   ├── registry.py        # source -> adapter mapping
│   │   │   ├── company_page/
│   │   │   ├── greenhouse/
│   │   │   ├── lever/
│   │   │   ├── ashby/
│   │   │   ├── smartrecruiters/
│   │   │   ├── workday/
│   │   │   ├── linkedin/
│   │   │   ├── x_twitter/
│   │   │   ├── instagram/
│   │   │   ├── reddit/
│   │   │   ├── telegram/
│   │   │   ├── discord/
│   │   │   └── startup_board/
│   │   ├── crawling/
│   │   │   ├── http_client.py     # httpx wrapper
│   │   │   ├── bs4_parser.py      # BeautifulSoup helpers
│   │   │   └── playwright_client.py
│   │   ├── workers/
│   │   │   ├── scheduler.py
│   │   │   └── jobs.py
│   │   ├── utils/
│   │   │   ├── normalize.py
│   │   │   └── dedupe.py
│   │   └── tests/
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md