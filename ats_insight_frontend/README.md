# ATS Insight — Frontend

React (Vite) SPA для ATS Insight backend.

## Дизайн

Тема — "сканування резюме": темна графітова палітра з амбер-акцентом
(сигнальний колір для CTA і високих скорів), зелений/червоний для
matched/missing навичок. Сигнатурний елемент — круговий gauge з
scan-анімацією на сторінці результату аналізу (`ScoreGauge.jsx`).

- Display font: Space Grotesk
- Body font: Inter
- Mono (скори, навички, дані): JetBrains Mono

## Швидкий старт

```bash
cd ats_insight_frontend
npm install

cp .env.example .env
# за потреби зміни VITE_API_BASE_URL, якщо backend не на 127.0.0.1:8000

npm run dev
```

Відкриється на http://localhost:5173

**Backend має бути запущений** (дивись README бекенду) і CORS вже дозволяє
`allow_origins=["*"]`, тож окремо нічого налаштовувати не треба.

## Структура

```
src/
  api/          # axios client + обгортки над ендпоінтами
  context/      # AuthContext (JWT в localStorage)
  components/   # Layout, ScoreGauge, ProtectedRoute, ui-кіт
  pages/        # Login, Register, Resumes, Jobs, NewAnalysis,
                # AnalysisResult (dashboard), History, ResumeVersions
```

## Flow користувача

1. `/register` → `/login`
2. `/` — завантажити резюме (PDF/DOCX), можна додавати нові версії (v2, v3...)
3. `/jobs` — додати вакансію: за посиланням (scraper) або вручну текстом
4. `/analyze` — обрати резюме + вакансію → запустити аналіз
5. `/analyses/:id` — dashboard: ATS score gauge, розбивка по категоріях
   (графік), matched/missing навички, AI-рекомендації, переписаний summary,
   поради до співбесіди (за запитом)
6. `/history` — всі минулі аналізи
7. `/resumes/:id/versions` — таблиця версій одного резюме з їхніми скорами
   (порівняння прогресу v1 → v2 → v3)

## Білд для продакшну

```bash
npm run build
```
Результат — у `dist/`, роздавай як статику (nginx, Vercel, Netlify тощо).
Не забудь виставити `VITE_API_BASE_URL` на реальний URL бекенду при білді.
