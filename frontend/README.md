# ATS Insight — Frontend

React (Vite) SPA for the ATS Insight backend.

## Design

Theme: "scanning a resume" — a dark graphite palette with an amber accent
(signal color for CTAs and high scores), green/red for matched/missing
skills. The signature element is a circular gauge with a scan animation on
the analysis result page (`ScoreGauge.jsx`).

- Display font: Space Grotesk
- Body font: Inter
- Mono (scores, skills, data): JetBrains Mono

## Setup

From the repository root, see the top-level `README.md` for running the
whole stack via `docker-compose`. To run only the frontend locally:

```bash
cd frontend
npm install

cp .env.example .env
# adjust VITE_API_BASE_URL if the backend isn't on 127.0.0.1:8000

npm run dev
```

Runs on http://localhost:5173. The backend must be running (see its
README) — CORS is already open (`allow_origins=["*"]`).

## Linting & formatting

```bash
npm run lint
npm run format
```

## Project layout

```
src/
  api/          axios client + endpoint wrappers
  context/      AuthContext (JWT in localStorage)
  components/   Layout, ScoreGauge, ProtectedRoute, small UI kit
  pages/        Login, Register, VerifyEmail, Resumes, Jobs, NewAnalysis,
                AnalysisResult (dashboard), History, ResumeVersions
```

## User flow

1. `/register` → check inbox for the verification link → `/login`
2. `/` — upload a resume (PDF/DOCX); upload new versions (v2, v3...) later
3. `/jobs` — add a job: from a link (scraper) or manually as text
4. `/analyze` — pick a resume + job, run the analysis
5. `/analyses/:id` — dashboard: ATS score gauge, category breakdown chart,
   matched/missing skills, AI recommendations, rewritten summary, interview
   tips (on demand)
6. `/history` — all past analyses
7. `/resumes/:id/versions` — score comparison table across a resume's
   versions (v1 → v2 → v3)

## Production build

```bash
npm run build
```
Output goes to `dist/`; serve it as static files (nginx, Vercel, Netlify,
etc.). Set `VITE_API_BASE_URL` to the real backend URL at build time.
