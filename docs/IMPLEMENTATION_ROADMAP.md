# Implementation Roadmap

## Guiding Principle

Do not implement the entire application at once. Build and approve incrementally, one module at a time. Each phase ends with a working, deployable slice and a checkpoint for approval before starting the next.

---

## Phase 0 — Repository Audit & Architecture (CURRENT)

**Goal**: Produce deliverables and get approval.

| Item | Status |
|------|--------|
| Repository audit | Complete (`docs/PHASE0_REPOSITORY_AUDIT.md`) |
| Architecture diagram | Complete (`docs/ARCHITECTURE_DIAGRAM.md`) |
| Database design | Complete (`docs/DATABASE_DESIGN.md`) |
| Module breakdown | Complete (`docs/MODULE_BREAKDOWN.md`) |
| Dependency recommendations | Complete (`docs/DEPENDENCY_RECOMMENDATIONS.md`) |
| Deployment strategy | Complete (`docs/DEPLOYMENT_STRATEGY.md`) |
| Implementation roadmap | Complete (`docs/IMPLEMENTATION_ROADMAP.md`) |

**Exit criteria**: Stakeholder approval of architecture + database design.

---

## Phase 1 — Foundation (Backend + DB + One Adapter)

**Goal**: A runnable FastAPI backend, PostgreSQL schema, Alembic migrations, and a single working source adapter.

| Task | Details |
|------|---------|
| 1.1 | Initialize repo structure (`backend/`, `frontend/`, `docs/`). |
| 1.2 | Add Python `.gitignore` entries (`__pycache__/`, `.venv/`, `*.pyc`, `.env`). |
| 1.3 | `backend/pyproject.toml` or `requirements.txt` with FastAPI, SQLAlchemy, Alembic, psycopg2, httpx, beautifulsoup4, pydantic-settings. |
| 1.4 | SQLAlchemy base + Alembic; initial migration `001_initial_schema` (opportunities, source_runs tables only). |
| 1.5 | FastAPI app factory (`main.py`) + health endpoint `GET /health`. |
| 1.6 | `adapters/base.py` abstract contract + `adapters/registry.py`. |
| 1.7 | First adapter: **Greenhouse** (public job boards; JSON-friendly, no Playwright needed). |
| 1.8 | `services/discovery_service.py` — run adapter, normalize, insert `opportunity` with `status='discovered'`. |
| 1.9 | `GET /opportunities` endpoint listing discovered opportunities. |
| 1.10 | Dockerfile + docker-compose for local dev. |
| 1.11 | CI: GitHub Actions lint + test + build. |

**Exit criteria**: `docker-compose up` runs; Greenhouse adapter discovers opportunities; `GET /opportunities` returns them; Alembic migrations apply cleanly.

## Phase 2 — Verification & Enrichment

**Goal**: Confirm active openings and enrich with stipend/duration/location/eligibility.

| Task | Details |
|------|---------|
| 2.1 | Add `verifications` and `enrichments` tables; migration. |
| 2.2 | `services/verification_service.py` — re-check source URL; detect filled/closed signals; store evidence. |
| 2.3 | `PATCH /opportunities/{id}/verify` manual verify trigger. |
| 2.4 | `services/enrichment_service.py` — regex-based extraction of stipend, duration, location, eligibility. |
| 2.5 | Update `opportunities` enrichment fields; `GET /opportunities/{id}` detail includes verification + enrichment. |
| 2.6 | Unit tests for verification signals and enrichment extraction. |

**Exit criteria**: Discovered opportunities can be verified (active/rejected) and enriched; detail view shows evidence and extracted fields.

## Phase 3 — Ranking & Frontend MVP

**Goal**: Rank opportunities and display them in a Next.js UI.

| Task | Details |
|------|---------|
| 3.1 | Add `rankings` table; migration. |
| 3.2 | `services/ranking_service.py` — weighted scoring (stipend, recency, employer brand, India-remote). |
| 3.3 | `GET /opportunities?sort=rank_score` returns ranked list. |
| 3.4 | Initialize `frontend/` (Next.js + TypeScript + Tailwind). |
| 3.5 | Frontend: opportunity listing page with search, filters (remote, paid, location, source), sort by rank. |
| 3.6 | Frontend: opportunity detail page showing verification evidence + enrichment. |
| 3.7 | Connect frontend to backend API (via `NEXT_PUBLIC_API_URL`). |

**Exit criteria**: Users can browse ranked, verified, enriched internships in the Next.js UI.

## Phase 4 — More Adapters + Monitoring

**Goal**: Expand source coverage and keep opportunities fresh.

| Task | Details |
|------|---------|
| 4.1 | Add adapters: Lever, Ashby, SmartRecruiters, Workday (Playwright for JS-rendered). |
| 4.2 | Add adapters: company_page (generic), Reddit, LinkedIn (public posts). |
| 4.3 | `workers/scheduler.py` + `workers/jobs.py` (APScheduler). |
| 4.4 | `monitoring_history` table; migration. |
| 4.5 | Scheduled re-check: new opps at 24h/3d/7d; verified active at 7d. |
| 4.6 | Status transitions: verified -> monitored -> expired. |
| 4.7 | `POST /run-discovery` endpoint for cron/GitHub Actions triggering. |

**Exit criteria**: Multiple sources crawl on a schedule; opportunities transition through monitoring lifecycle; stale ones marked expired.

## Phase 5 — Users, Alerts & Auth (Post-MVP)

**Goal**: User accounts, saved searches, email alerts.

| Task | Details |
|------|---------|
| 5.1 | `users` and `alerts` tables; migration. |
| 5.2 | JWT auth (self-managed) or Supabase Auth integration. |
| 5.3 | `POST /auth/register`, `POST /auth/login`, JWT middleware. |
| 5.4 | Saved searches + alert subscriptions. |
| 5.5 | Email alerts via Resend (free tier: 3,000/month). |
| 5.6 | Frontend: `/auth/*`, `/dashboard`, alert management. |

**Exit criteria**: Users can sign up, save searches, and receive email alerts for new matching internships.

## Phase 6 — X/Twitter, Instagram, Telegram, Discord + Hardening

**Goal**: Social-source coverage and production hardening.

| Task | Details |
|------|---------|
| 6.1 | Adapters: X/Twitter, Instagram (public posts/reels), Telegram, Discord. |
| 6.2 | Playwright handling for JS-heavy social pages. |
| 6.3 | Rate-limit public endpoints; robots.txt respect. |
| 6.4 | Structured logging + basic metrics. |
| 6.5 | Load/performance testing on free-tier DB. |

**Exit criteria**: All vision sources covered; system stable under expected load.

## Approval Gates

| Gate | What's Approved | When |
|------|----------------|------|
| Gate 0 | Architecture + database design | End of Phase 0 |
| Gate 1 | Backend foundation + one adapter | End of Phase 1 |
| Gate 2 | Verification + enrichment | End of Phase 2 |
| Gate 3 | Ranking + frontend MVP | End of Phase 3 |
| Gate 4 | Multi-adapter + monitoring | End of Phase 4 |
| Gate 5 | Auth + alerts | End of Phase 5 |
| Gate 6 | Social sources + hardening | End of Phase 6 |

## Estimated Effort (Relative)

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 0 | Done | — |
| Phase 1 | Medium | Phase 0 approval |
| Phase 2 | Medium | Phase 1 approval |
| Phase 3 | Medium | Phase 2 approval |
| Phase 4 | Large | Phase 3 approval |
| Phase 5 | Medium | Phase 4 approval |
| Phase 6 | Medium | Phase 5 approval |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| ATS sites block scrapers / change markup | Adapters isolated per source; fix one without touching others. Use Playwright only where needed. |
| LinkedIn/Instagram/X restrict public access | Start with sources that are openly accessible (Greenhouse, Lever, company pages); treat social as best-effort. |
| Render free tier spins down | Use cron/GitHub Actions to warm the backend; accept cold start for MVP. |
| Free DB storage fills | Opportunities are text-light; 500 MB is ample for MVP. Archive expired records if needed. |

## Immediate Next Step

Wait for stakeholder approval of this Phase 0 plan (architecture + database + modules + dependencies + deployment + roadmap). Upon approval, begin Phase 1 (Foundation).
