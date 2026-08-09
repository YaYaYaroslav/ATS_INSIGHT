import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Layout from "../components/Layout.jsx";
import { Card, PrimaryButton, Spinner, ErrorBanner } from "../components/ui.jsx";
import { resumesApi, jobsApi, analysesApi } from "../api/endpoints.js";

export default function NewAnalysisPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [resumeId, setResumeId] = useState(searchParams.get("resumeId") || "");
  const [jobId, setJobId] = useState(searchParams.get("jobId") || "");
  const [useAi, setUseAi] = useState(true);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([resumesApi.list(), jobsApi.list()])
      .then(([r, j]) => {
        setResumes(r);
        setJobs(j);
        if (!resumeId && r.length) setResumeId(String(r[0].id));
        if (!jobId && j.length) setJobId(String(j[0].id));
      })
      .catch(() => setError("Не вдалося завантажити резюме/вакансії"))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRun = async (e) => {
    e.preventDefault();
    if (!resumeId || !jobId) return;
    setRunning(true);
    setError("");
    try {
      const analysis = await analysesApi.create(Number(resumeId), Number(jobId), useAi);
      navigate(`/analyses/${analysis.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Не вдалося запустити аналіз");
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Spinner label="Завантажую дані..." />
      </Layout>
    );
  }

  if (!resumes.length || !jobs.length) {
    return (
      <Layout>
        <Card className="text-center py-12">
          <p className="text-text-muted text-sm">
            Потрібно щонайменше одне резюме і одна вакансія, щоб запустити аналіз.
          </p>
        </Card>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="font-display text-2xl font-semibold mb-1">Новий аналіз</h1>
      <p className="text-text-muted text-sm mb-8">Обери резюме і вакансію для порівняння</p>

      <Card>
        <ErrorBanner message={error} />
        <form onSubmit={handleRun} className="space-y-5 mt-2">
          <div>
            <label className="block text-xs text-text-muted mb-1.5">Резюме</label>
            <select
              value={resumeId}
              onChange={(e) => setResumeId(e.target.value)}
              className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none"
            >
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.parsed_data?.name || r.original_filename} ({r.label})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-text-muted mb-1.5">Вакансія</label>
            <select
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none"
            >
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title || `Вакансія #${j.id}`}
                </option>
              ))}
            </select>
          </div>

          <label className="flex items-center gap-2 text-sm text-text-muted">
            <input type="checkbox" checked={useAi} onChange={(e) => setUseAi(e.target.checked)} className="accent-signal" />
            Отримати AI-рекомендації (Gemini)
          </label>

          <PrimaryButton type="submit" disabled={running} className="w-full">
            {running ? "Аналізую..." : "Запустити аналіз"}
          </PrimaryButton>
        </form>
      </Card>
    </Layout>
  );
}
