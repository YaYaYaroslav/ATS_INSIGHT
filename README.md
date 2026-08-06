# ATS Insight — Backend

FastAPI backend for analyzing resumes against job descriptions (ATS scoring + AI recommendations powered by Gemini).

Implemented according to the architecture:

- **Rule-based ATS core** — works completely without AI
- **Separate AI layer** (Gemini/Ollama) — used only for recommendations, rewriting, and interview tips

---

## Quick Start (Local, without Docker)

```bash
cd ats_insight_backend

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Open .env and add your GEMINI_API_KEY

uvicorn app.main:app --reload
```

The application will start at:

```
http://localhost:8000
```

Interactive API documentation (Swagger):

```
http://localhost:8000/docs
```

By default, the application uses SQLite (`ats_insight.db`) — no additional services are required for a quick start.

---

# Running with Docker (PostgreSQL)

```bash
cp .env.example .env

# Fill in .env file (GEMINI_API_KEY is required)

docker-compose up --build
```

---

# Project Structure

```
app/
  core/         # Configuration, database, security (JWT, bcrypt)
  models/       # SQLAlchemy models: User, Resume, Job, Analysis
  schemas/      # Pydantic request/response schemas
  api/routes/   # Auth, resumes, jobs, analyses endpoints
  services/     # PDF/DOCX extractor, resume/job parser, ATS engine
  providers/    # BaseAIProvider -> GeminiProvider / OllamaProvider / NoOp
```

---

# Main API Flow

### 1. User Registration

```
POST /api/v1/auth/register
```

Creates a new user account.

---

### 2. User Login

```
POST /api/v1/auth/login
```

Returns JWT authentication token.

Request format:

```
form-data:
username=email
password=password
```

---

### 3. Resume Upload

```
POST /api/v1/resumes/upload
```

Upload a resume file.

Request format:

```
multipart/form-data

field:
file
```

Supported formats:

- PDF
- DOCX

---

### 4. Create Job Description

```
POST /api/v1/jobs
```

Example request:

```json
{
  "title": "Python Developer",
  "raw_text": "Job description content..."
}
```

---

### 5. Run Resume Analysis

```
POST /api/v1/analyses
```

Example request:

```json
{
  "resume_id": 1,
  "job_id": 1,
  "use_ai": true
}
```

---

### 6. Analysis History

```
GET /api/v1/analyses
```

Returns previous resume analyses.

---

### 7. Resume Version Comparison

```
GET /api/v1/resumes/{id}/versions
```

Compare different versions of the same resume:

```
v1 / v2 / v3 + ATS scores
```

---

All routes except:

```
/auth/*
```

require authentication:

```
Authorization: Bearer <token>
```

---

# Features Available Without AI

Environment:

```
AI_PROVIDER=none
```

Available features:

- Resume upload
- PDF/DOCX text extraction
- Skills extraction
- ATS score calculation
- Matched skills detection
- Missing skills detection
- Analysis history
- Resume version comparison

ATS scoring system:

| Category | Weight |
|----------|--------|
| Skills | 35% |
| Experience | 25% |
| Education | 10% |
| Keywords | 20% |
| Formatting | 10% |

---

# AI Features (Gemini)

Environment:

```
AI_PROVIDER=gemini
```

Gemini is used for:

### AI Recommendations

Provides improvement suggestions based on ATS analysis.

---

### Summary Rewrite

```
ai_summary_rewrite
```

Generates a more professional resume summary.

---

### Interview Tips

Endpoint:

```
GET /api/v1/analyses/{id}/interview-tips
```

Provides interview preparation recommendations based on the analyzed vacancy.

---

# Architecture Overview

The project separates deterministic ATS logic from AI functionality.

## ATS Core

Responsible for:

- Resume parsing
- Job description parsing
- Skills matching
- Keyword analysis
- Score calculation

Works without external AI services.

---

## AI Layer

Responsible for:

- Resume improvement recommendations
- Professional summary rewriting
- Interview preparation tips

Supported providers:

- Gemini
- Ollama
- NoOp provider

---

# Future Improvements (Not Included in MVP)

- Alembic migrations instead of `create_all`
- Endpoint for rewriting resume bullet points

  Service already implemented:

```
GeminiProvider.rewrite_bullet_points
```

  Only API route needs to be added.

- Export analysis results:

  - PDF
  - HTML
  - JSON

- React frontend:

  - Dashboard
  - Analytics
  - ATS score visualization
  - Charts (Plotly / Chart.js)

- Rate limiting for authentication endpoints

- AI response caching:

```
(resume_id, job_id)
```

---

# Tech Stack

Backend:

- FastAPI
- SQLAlchemy
- Pydantic
- SQLite / PostgreSQL
- JWT Authentication
- bcrypt

AI:

- Google Gemini API
- Ollama (optional)

Document Processing:

- PDF parser
- DOCX parser

Deployment:

- Docker
- Docker Compose