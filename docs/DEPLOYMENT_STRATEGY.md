# Free / Open-Source Deployment Strategy

## 1. Deployment Goals

- Zero infrastructure cost for MVP.
- Managed services where possible (less ops overhead).
- Single `docker-compose.yml` for local development and one-command deploy.
- Easy path from free tier to paid tier without re-architecture.

## 2. Recommended Stack (Free Tier)

| Layer | Provider | Free Tier Details | Cost |
|-------|----------|-------------------|------|
| Database | **Supabase** (PostgreSQL) | 500 MB, 2 projects | $0 |
| Database | **Neon** (PostgreSQL) | 0.5 GB storage, auto-suspend | $0 |
| Frontend | **Vercel** | Hobby tier, unlimited bandwidth (soft cap) | $0 |
| Backend | **Render** | Free web service (spins down after inactivity) | $0 |
| Backend | **Railway** | ~$5 trial credit then paid | $0 trial |
| Background worker | **Render cron** or **GitHub Actions scheduled** | Free | $0 |
| Domain | Vercel subdomain (`*.vercel.app`) | Free | $0 |
| Email alerts | **Resend** | 3,000 emails/month | $0 |
| Container registry | GitHub Container Registry (GHCR) | Free for public repos | $0 |

**Recommended MVP combo**: Supabase (DB) + Vercel (frontend) + Render (backend + worker cron).

## 3. Render Free Tier Caveats

- Free web services spin down after ~15 min of inactivity; cold start ~30-60s on first request.
- Background workers are not truly free on Render (web service only). Use **Render cron jobs** (free) to hit a `/run-discovery` endpoint on a schedule, or use **GitHub Actions scheduled workflows** (`cron:`) to trigger discovery jobs via HTTP.
- For a truly "always-on" backend without cost, consider running the backend on a free Oracle Cloud Always Free ARM instance or a Raspberry Pi at home, but this adds ops complexity. Start with Render + cron; migrate if needed.

## 4. docker-compose.yml (Local Development)

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: internradar
      POSTGRES_USER: internradar
      POSTGRES_PASSWORD: internradar
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+psycopg2://internradar:internradar@db:5432/internradar
      ENV: development
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## 5. CI/CD (GitHub Actions — Free)

Workflow `.github/workflows/ci.yml`:

1. Lint: `ruff check` (backend), `npm run lint` (frontend).
2. Type-check: `mypy` (backend), `tsc --noEmit` (frontend).
3. Test: `pytest` (backend), `vitest run` (frontend).
4. Build: `docker build` for backend and frontend; push to GHCR on tag/release.
5. Deploy: On push to `main`, render.com auto-deploys from connected GitHub repo; Vercel auto-deploys frontend.

## 6. Environment Variables

### Backend (`.env`)
```
ENV=development
DATABASE_URL=postgresql+psycopg2://...
SECRET_KEY=<generate with openssl rand -hex 32>
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (`.env.local`)
```
NEXT_PUBLIC_API_URL=https://api.internradar.example.com
```

## 7. Deployment Steps (MVP)

1. Create Supabase project; get `DATABASE_URL`.
2. Create Render web service; connect GitHub repo; set `DATABASE_URL` and `SECRET_KEY`.
3. Set up Render cron job (or GitHub Actions scheduled) to call `POST /run-discovery` every 6h.
4. Create Vercel project; connect frontend folder; set `NEXT_PUBLIC_API_URL`.
5. Run `alembic upgrade head` against the production DB (via Render shell or migration hook).
6. Verify: open Vercel URL, confirm opportunities load.

## 8. Scaling Path (When Free Tier Is Outgrown)

| Trigger | Migration |
|---------|-----------|
| DB > 500 MB | Supabase Pro / Neon paid |
| Backend spin-down hurts UX | Render paid instance or Railway |
| Need always-on worker | Celery + Redis on Render/Railway or a cheap VPS |
| Need custom domain | Buy domain, point to Vercel/Render |
| Need SMS/email volume | Upgrade Resend/SendGrid |

## 9. Security Notes for Free-Tier Deployment

- Never commit `.env`; use `.env.example` only.
- Use platform secret stores (Render Environment Variables, Vercel Environment Variables) for production secrets.
- Force HTTPS on all public endpoints.
- Rate-limit public ingest endpoints to prevent abuse.
