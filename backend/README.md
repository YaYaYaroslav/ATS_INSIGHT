# ATS Insight — Backend

FastAPI backend for resume-vs-job ATS scoring, with AI-powered recommendations
via Gemini.

Rule-based ATS core (scoring, parsing, matching) works without any AI
provider. The AI layer (Gemini/Ollama) is only used for recommendations,
summary rewriting, and interview tips.

## Setup

From the repository root, see the top-level `README.md` for running the
whole stack via `docker-compose`. To run only the backend locally:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt   # includes requirements.txt + pytest/ruff/black

cp .env.example .env
# edit .env: set GEMINI_API_KEY and DATABASE_URL

alembic upgrade head
uvicorn app.main:app --reload
```

App runs on http://localhost:8000, Swagger docs at http://localhost:8000/docs.

## Project layout

```
app/
  core/         config, database, security (JWT, bcrypt)
  models/       SQLAlchemy models: User, Resume, Job, Analysis
  schemas/      Pydantic request/response schemas
  api/routes/   auth, resumes, jobs, analyses
  services/     PDF/DOCX extraction, resume/job parsing, ATS engine, scraper, email
  providers/    BaseAIProvider -> GeminiProvider / OllamaProvider / NoOp
alembic/        Database migrations
tests/          pytest suite (unit + integration)
scripts/        One-off diagnostic scripts
```

## Migrations (Alembic)

Schema is fully managed by Alembic — `Base.metadata.create_all()` is not used.

```bash
alembic upgrade head                              # apply all migrations
alembic revision --autogenerate -m "description"  # generate a new migration after a model change
alembic downgrade -1                               # roll back the last migration
alembic current                                    # show current DB version
```

## Tests

```bash
pytest
```

Tests use an isolated SQLite file and `AI_PROVIDER=none`, so they never touch
your real database or require a Gemini key.

## Linting & formatting

```bash
ruff check .
black .
```

## API flow

1. `POST /api/v1/auth/register` — creates an account (unverified) and sends a verification email
2. `GET /api/v1/auth/verify-email?token=...` — verifies the account
3. `POST /api/v1/auth/login` — returns a JWT (form-data: `username`=email, `password`)
4. `POST /api/v1/resumes/upload` — upload a resume (multipart/form-data, field `file`)
5. `POST /api/v1/jobs` or `POST /api/v1/jobs/from-url` — add a job description
6. `POST /api/v1/analyses` — run the ATS analysis (`{"resume_id": 1, "job_id": 1, "use_ai": true}`)
7. `GET /api/v1/analyses` — analysis history
8. `GET /api/v1/resumes/{id}/versions` — compare resume versions (v1/v2/v3 + scores)

All routes except `/auth/*` require `Authorization: Bearer <token>`.

## Email verification

If `SMTP_HOST` is empty in `.env`, verification emails are not actually sent —
they're printed to the `uvicorn` console instead (look for the `EMAIL (SMTP
not configured...)` block), so you can copy the link for local testing.

## What works without AI (`AI_PROVIDER=none`)

Upload, PDF/DOCX parsing, skills extraction, ATS scoring, matched/missing
skills, analysis history, resume version comparison, job scraping.

## What uses Gemini (`AI_PROVIDER=gemini`)

`ai_recommendations` and `ai_summary_rewrite` in the analysis result, and
`GET /api/v1/analyses/{id}/interview-tips`.

## Not included in this MVP

- A route for `GeminiProvider.rewrite_bullet_points` (the service method already exists)
- Export to PDF/HTML/JSON
- Rate limiting on auth endpoints
- Caching AI responses by (resume_id, job_id)
