# ATS Insight

> Full-stack AI-powered ATS platform for resume analysis, job matching, and career optimization.

ATS Insight is a full-stack application designed to help candidates understand how well their resume matches a specific job description.

The platform combines a **rule-based ATS engine** with optional **AI-powered analysis**, providing objective resume scoring, skill matching, actionable recommendations, resume improvements, and interview preparation.

The core ATS analysis works independently of AI, while AI is used as an additional intelligence layer for more advanced recommendations.

---

## ✨ Features

### 📄 Resume Analysis

- Upload resumes in PDF/DOCX format
- Extract and parse resume content
- Detect technical skills and keywords
- Analyze experience and education
- Evaluate resume formatting
- Calculate an overall ATS compatibility score
- Identify matched and missing skills

### 🎯 ATS Scoring

ATS Insight uses a weighted scoring system to evaluate how well a resume matches a job description.

| Category | Weight |
|---|---:|
| Skills | 35% |
| Experience | 25% |
| Keywords | 20% |
| Education | 10% |
| Formatting | 10% |

The scoring engine is **rule-based and does not require AI**, making the core analysis deterministic, transparent, and available even when no AI provider is configured.

### 💼 Job Management

Users can:

- Create job descriptions
- Store job requirements
- Analyze resumes against specific positions
- Reuse previously created job descriptions
- Compare different resumes against the same position

### 🤖 AI-Powered Recommendations

When AI is enabled, ATS Insight can provide:

- Resume improvement recommendations
- AI-generated resume summary rewrites
- Missing skill suggestions
- Content improvement suggestions
- Interview preparation tips
- Job-specific career recommendations

The AI layer is intentionally separated from the ATS engine so the application does not depend entirely on an external AI service.

### 📊 Analysis History

Users can access previous analyses and review:

- ATS scores
- Matched skills
- Missing skills
- AI recommendations
- Resume/job combinations
- Previous analysis results

### 🔄 Resume Versioning

ATS Insight supports multiple versions of a resume, allowing users to track how changes affect their ATS score.

### 🔐 Authentication

The application includes:

- User registration
- JWT authentication
- Secure password hashing
- Email verification
- Verification email resend functionality
- Protected API endpoints

### 📧 Email Verification

New accounts require email verification before login.

The system supports SMTP-based email delivery and can also operate in development mode, where verification links are logged to the application console instead of being sent through a real SMTP server.

### 🐳 Docker Support

The backend infrastructure can be started using Docker Compose with:

- FastAPI
- PostgreSQL
- Automatic Alembic migrations
- Persistent PostgreSQL storage

---

## 🏗️ Architecture

ATS Insight separates the presentation layer, API, business logic, database layer, and AI providers.

```text
                         ┌─────────────────────┐
                         │       Frontend      │
                         │      React App      │
                         └──────────┬──────────┘
                                    │
                                    │ REST API
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │      Backend        │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │ ATS Engine  │       │ PostgreSQL  │       │ AI Provider │
       │ Rule-based  │       │  Database   │       │ Gemini /    │
       │             │       │             │       │ Ollama      │
       └─────────────┘       └─────────────┘       └─────────────┘
```

### Core Principle

The ATS engine does not depend on AI.

```text
Resume
   │
   ▼
Parsing
   │
   ▼
Rule-based ATS Engine
   │
   ├── Skills
   ├── Experience
   ├── Education
   ├── Keywords
   └── Formatting
   │
   ▼
ATS Score
   │
   └──────────────► Optional AI Layer
                         │
                         ├── Recommendations
                         ├── Summary Rewrite
                         └── Interview Tips
```

---

## 🛠️ Tech Stack

### Frontend

- React
- JavaScript / TypeScript
- REST API integration
- Component-based UI

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Alembic
- Uvicorn

### Authentication & Security

- JWT
- OAuth2 password flow
- bcrypt
- Email verification
- SMTP

### AI

- Google Gemini
- Ollama
- Provider abstraction layer

### Document Processing

- PDF parsing
- DOCX parsing
- Resume text extraction

### Infrastructure

- Docker
- Docker Compose
- PostgreSQL
- Environment-based configuration

---

## 📁 Project Structure

```text
ATS_INSIGHT/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── providers/
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Requirements

- Python 3.11+
- Node.js 18+
- PostgreSQL 16+ or Docker
- Git
- Gemini API key or a local Ollama instance for AI features

### 🐳 Running with Docker

Clone the repository:

```bash
git clone https://github.com/YaYaYaroslav/ATS_INSIGHT.git
cd ATS_INSIGHT
```

Create the environment file.

Linux/macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure the required environment variables:

```env
GEMINI_API_KEY=your_api_key
```

Start the application:

```bash
docker compose up --build
```

The API container automatically runs:

```bash
alembic upgrade head
```

before starting FastAPI.

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

## 💻 Local Development

### Backend

```bash
cd backend
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the database:

```env
DATABASE_URL=postgresql+psycopg2://ats_user:ats_password@localhost:5432/ats_insight
```

Apply migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at the address provided by the development server.

---

## 🔌 API Overview

The backend exposes a RESTful API under:

```text
/api/v1
```

### Authentication

```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/verify-email
POST /api/v1/auth/resend-verification
```

### Resumes

```http
POST /api/v1/resumes/upload
GET  /api/v1/resumes
GET  /api/v1/resumes/{id}
GET  /api/v1/resumes/{id}/versions
```

### Jobs

```http
POST   /api/v1/jobs
GET    /api/v1/jobs
GET    /api/v1/jobs/{id}
PUT    /api/v1/jobs/{id}
DELETE /api/v1/jobs/{id}
```

### Analysis

```http
POST /api/v1/analyses
GET  /api/v1/analyses
GET  /api/v1/analyses/{id}
GET  /api/v1/analyses/{id}/interview-tips
```

Protected endpoints require:

```http
Authorization: Bearer <JWT>
```

Full interactive documentation:

```text
http://localhost:8000/docs
```

---

## 🤖 AI Provider Architecture

AI functionality is implemented through a provider abstraction:

```text
BaseAIProvider
      │
      ├── GeminiProvider
      ├── OllamaProvider
      └── NoOpProvider
```

This allows the AI provider to be changed without coupling the core ATS logic to a specific model or API.

### Gemini

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
```

### Disable AI

```env
AI_PROVIDER=none
```

The application will still support:

- Resume parsing
- Skills extraction
- ATS scoring
- Keyword matching
- Resume/job analysis
- Analysis history
- Resume version comparison

---

## 📧 SMTP Configuration

Email verification can be configured through SMTP.

Example Gmail configuration:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=your_email@gmail.com
SMTP_USE_TLS=true
```

For Gmail, use a **Google App Password** instead of your normal account password.

For local development, SMTP can be left unconfigured. Verification links will then be logged to the backend console.

---

## 🗄️ Database & Migrations

Database schema changes are managed with Alembic.

Create a migration:

```bash
alembic revision --autogenerate -m "describe change"
```

Review the generated migration before applying it.

Apply migrations:

```bash
alembic upgrade head
```

Rollback the latest migration:

```bash
alembic downgrade -1
```

Check the current revision:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

---

## 🔒 Security

The project follows several security practices:

- Passwords are hashed using bcrypt
- Authentication uses JWT access tokens
- Protected endpoints require authentication
- Email verification is required before login
- Secrets are loaded through environment variables
- `.env` files are excluded from version control

Never commit API keys, passwords, SMTP credentials, or other secrets to Git.

---

## 📈 Roadmap

Planned improvements include:

- Advanced ATS scoring algorithms
- More detailed resume feedback
- Additional AI providers
- AI-powered bullet point rewriting
- Resume export to PDF/HTML/JSON
- Improved analytics dashboard
- More advanced resume version comparison
- Authentication rate limiting
- AI response caching
- Automated testing and CI/CD
- Production deployment configuration

---

## 🎯 Project Goals

ATS Insight demonstrates how a modern AI-assisted application can combine deterministic business logic with generative AI.

The project focuses on:

- Clean backend architecture
- REST API design
- Database modeling and migrations
- Authentication and authorization
- Document processing
- Rule-based scoring algorithms
- AI provider abstraction
- Full-stack development
- Dockerized development environments
- Practical AI integration

The goal is not to make the application completely dependent on AI, but to use AI where it provides the most value.

---

## 👨‍💻 Author

**Yaroslav Polinkin**

Python Developer & Instructor

GitHub:  
https://github.com/YaYaYaroslav

---

## 📄 License

This project is currently developed as a portfolio project.
