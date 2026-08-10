# ATS Insight

A resume-vs-job matching tool: upload a resume, paste or scrape a job
posting, and get an ATS compatibility score with AI-powered improvement
recommendations.

```
resume (PDF/DOCX)              job posting (text or URL)
        │                               │
        ▼                               ▼
  resume parser                  job description parser
   (skills, experience,           (required/nice-to-have skills,
    education, contacts)           experience, keywords)
        └───────────────┬───────────────┘
                         ▼
                  ATS Rule Engine
             (skills/experience/education/
              keywords/formatting → score)
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        Dashboard              AI Recommendations
        (React SPA)              (Gemini, optional)
```

The rule-based ATS core (parsing, scoring, matching) works standalone,
without any AI provider. AI (Gemini) is only used for recommendations,
resume summary rewriting, and interview tips — set `AI_PROVIDER=none` to
run without it.

## Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Alembic, Gemini API
- **Frontend**: React (Vite), Tailwind CSS, Recharts
- **Auth**: JWT, email verification (SMTP or console-logged in dev)

## Project layout

```
ats_insight/
  backend/     FastAPI app, Alembic migrations, tests — see backend/README.md
  frontend/    React SPA — see frontend/README.md
  docker-compose.yml   runs db + backend + frontend together
```

## Quick start (Docker — recommended)

```bash
cp backend/.env.example backend/.env
# edit backend/.env: set GEMINI_API_KEY at minimum

docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000 (docs at `/docs`)
- PostgreSQL: localhost:5432 (user `ats_user` / db `ats_insight`, see `docker-compose.yml`)

The `backend` container runs `alembic upgrade head` automatically before
starting the server.

## Running services individually (without Docker)

See `backend/README.md` and `frontend/README.md` for local setup
(virtualenv, PostgreSQL, `npm install`, etc.) — useful for development with
hot reload on both sides.

## Tests

```bash
cd backend
pytest
```

## Linting & formatting

```bash
# Backend
cd backend && ruff check . && black .

# Frontend
cd frontend && npm run lint && npm run format
```
