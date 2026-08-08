# ATS Insight — Backend

FastAPI backend for analyzing resumes against job descriptions using ATS scoring and AI-powered recommendations via Gemini.

The project follows a hybrid architecture: a **rule-based ATS core** that works independently of AI, combined with a separate **AI layer** used for recommendations, rewriting, and interview preparation.

## Quick Start with Docker

Docker is the recommended way to run the project because PostgreSQL is provided out of the box.

```bash
cp .env.example .env
# Fill in .env (GEMINI_API_KEY is required for AI features)

docker-compose up --build
```

The `api` container automatically runs:

```bash
alembic upgrade head
```

before starting the application, so no manual database migration steps are required.

The application will be available at:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

## Local Development Without Docker

For local development, you need a running PostgreSQL instance. SQLite can also be used for quick testing.

```bash
cd ats_insight_backend

python -m venv venv
```

Activate the virtual environment:

**Windows:**

```powershell
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Then configure `.env` with your credentials:

```env
GEMINI_API_KEY=your_api_key
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/ats_insight
```

For quick testing without PostgreSQL, you can temporarily use:

```env
DATABASE_URL=sqlite:///./ats_insight.db
```

Apply database migrations:

```bash
alembic upgrade head
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

## Database Migrations

Database schema changes are managed entirely through **Alembic**.

`Base.metadata.create_all()` is not used.

Apply all pending migrations:

```bash
alembic upgrade head
```

After changing a SQLAlchemy model, generate a new migration:

```bash
alembic revision --autogenerate -m "describe the change"
```

**Always review the generated migration before applying it.**

Apply the migration:

```bash
alembic upgrade head
```

Rollback the latest migration:

```bash
alembic downgrade -1
```

Check the current database revision:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

The initial migration creates the main application tables:

- `users`
- `resumes`
- `jobs`
- `analyses`

## Project Structure

```text
app/
├── core/                 # Configuration, database, security (JWT, bcrypt)
├── models/               # SQLAlchemy models
│   ├── User
│   ├── Resume
│   ├── Job
│   └── Analysis
├── schemas/              # Pydantic request/response schemas
├── api/
│   └── routes/            # API endpoints
│       ├── auth
│       ├── resumes
│       ├── jobs
│       └── analyses
├── services/             # PDF/DOCX extraction, parsing, ATS engine
└── providers/            # AI provider abstraction
    ├── BaseAIProvider
    ├── GeminiProvider
    ├── OllamaProvider
    └── NoOp
```

## API Flow

### 1. Register

```http
POST /api/v1/auth/register
```

Creates a new user account and starts the email verification process.

### 2. Login

```http
POST /api/v1/auth/login
```

Returns a JWT access token.

Authentication uses OAuth2 password flow:

```text
username = user email
password = user password
```

### 3. Upload Resume

```http
POST /api/v1/resumes/upload
```

Uploads and parses a resume.

Request type:

```text
multipart/form-data
file=<resume>
```

Supported resume processing includes PDF/DOCX extraction and skills parsing.

### 4. Create Job

```http
POST /api/v1/jobs
```

Example:

```json
{
  "title": "Python Developer",
  "raw_text": "We are looking for a Python developer..."
}
```

### 5. Analyze Resume

```http
POST /api/v1/analyses
```

Example:

```json
{
  "resume_id": 1,
  "job_id": 1,
  "use_ai": true
}
```

This runs the ATS analysis and optionally generates AI recommendations.

### 6. Analysis History

```http
GET /api/v1/analyses
```

Returns previous resume/job analyses.

### 7. Resume Version Comparison

```http
GET /api/v1/resumes/{id}/versions
```

Returns different versions of a resume and allows their ATS scores to be compared.

All routes except `/auth/*` require:

```http
Authorization: Bearer <token>
```

## ATS Scoring

The core ATS engine works **without AI**.

The overall score is calculated using the following weighted criteria:

| Category | Weight |
|---|---:|
| Skills | 35% |
| Experience | 25% |
| Keywords | 20% |
| Education | 10% |
| Formatting | 10% |

The ATS engine provides:

- Overall ATS score
- Matched skills
- Missing skills
- Keyword analysis
- Experience analysis
- Education analysis
- Formatting analysis

This means the core resume analysis remains functional even when no AI provider is configured.

## AI Features

AI functionality is optional and separated from the core ATS engine.

### Gemini

Set:

```env
AI_PROVIDER=gemini
```

Gemini is used for:

- `ai_recommendations`
- `ai_summary_rewrite`
- Interview preparation tips
- Resume improvement suggestions

### Ollama

The architecture also supports a local Ollama provider, allowing AI functionality without relying exclusively on a cloud API.

### No AI

For completely rule-based analysis:

```env
AI_PROVIDER=none
```

The application can still perform:

- Resume upload
- PDF/DOCX parsing
- Skills extraction
- ATS scoring
- Matched/missing skills analysis
- Analysis history
- Resume version comparison

## Email Verification

User registration includes email verification.

### Registration

```http
POST /api/v1/auth/register
```

A newly registered user is created with:

```text
is_verified = false
```

A verification email is then sent to the user's email address.

### Development Mode

If `SMTP_HOST` is not configured, the application does not send a real email.

Instead, the verification email and its link are logged to the Uvicorn console.

This makes email verification easy to test during local development.

### Verify Email

```http
GET /api/v1/auth/verify-email?token=<token>
```

The verification link points to the frontend:

```text
{FRONTEND_BASE_URL}/verify-email?token=<token>
```

The frontend then calls the backend verification endpoint.

### Login Protection

Users cannot log in until their email has been verified.

An unverified account receives:

```http
403 Forbidden
```

### Resend Verification

```http
POST /api/v1/auth/resend-verification
```

Generates and sends a new verification email.

### SMTP Configuration

For real email delivery, configure:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=your_email@gmail.com
SMTP_USE_TLS=true
```

For Gmail, `SMTP_PASSWORD` should be a **Google App Password**, not the regular Google account password.

## Authentication & Security

The backend uses:

- JWT authentication
- Password hashing with bcrypt
- OAuth2 password flow
- Email verification
- Protected API routes
- Environment-based configuration
- PostgreSQL for persistent data storage

Sensitive credentials should be stored in `.env` and never committed to Git.

Make sure `.env` is included in `.gitignore`.

## Current Features

### Backend

- FastAPI REST API
- PostgreSQL database
- SQLAlchemy ORM
- Alembic migrations
- JWT authentication
- Email verification
- PDF/DOCX resume parsing
- Job management
- Resume management
- Resume versioning
- ATS scoring
- Skills extraction
- Keyword matching
- Analysis history

### AI

- Gemini integration
- Ollama provider support
- AI recommendations
- Summary rewriting
- Interview preparation
- AI provider abstraction

### Developer Experience

- Docker support
- Docker Compose
- Swagger/OpenAPI documentation
- Environment-based configuration
- Automatic database migrations in Docker

## Roadmap

The following features are planned for future versions:

- Bullet-point rewrite endpoint
  - The underlying `GeminiProvider.rewrite_bullet_points()` service is already implemented.
- Resume export to PDF/HTML/JSON
- React frontend
  - Dashboard
  - ATS score visualization
  - Analysis history
  - Resume comparison
  - Charts
- Authentication rate limiting
- AI response caching based on `(resume_id, job_id)`
- Further ATS scoring improvements
- Additional AI providers

## Tech Stack

**Backend**

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic

**Authentication & Security**

- JWT
- bcrypt
- OAuth2

**AI**

- Google Gemini
- Ollama

**Document Processing**

- PDF/DOCX parsing

**Infrastructure**

- Docker
- Docker Compose
- Uvicorn

## License

This project is currently intended as a portfolio/pet project.
