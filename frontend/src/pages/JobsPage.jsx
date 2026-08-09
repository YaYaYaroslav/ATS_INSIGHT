import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout.jsx";
import { Card, PrimaryButton, SecondaryButton, Spinner, ErrorBanner } from "../components/ui.jsx";
import { jobsApi } from "../api/endpoints.js";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState("url"); // "url" | "text"
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [rawText, setRawText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setJobs(await jobsApi.list());
    } catch {
      setError("Не вдалося завантажити список вакансій");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleDelete = async (id) => {
    if (!window.confirm("Видалити цю вакансію та всі пов'язані аналізи?")) return;
    await jobsApi.remove(id);
    await load();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (mode === "url") {
        await jobsApi.createFromUrl(url);
        setUrl("");
      } else {
        await jobsApi.createFromText(title || null, rawText);
        setTitle("");
        setRawText("");
      }
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Не вдалося обробити вакансію. Спробуй вставити текст вручну.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout>
      <h1 className="font-display text-2xl font-semibold mb-1">Вакансії</h1>
      <p className="text-text-muted text-sm mb-8">
        Встав посилання на вакансію з work.ua — ми самі витягнемо опис. Робота.ua блокує
        автоматичні запити, тож звідти опис доведеться вставити вручну (вкладка "Вручну").
      </p>

      <Card className="mb-8">
        <div className="flex gap-2 mb-5">
          <button
            onClick={() => setMode("url")}
            className={`px-3 py-1.5 rounded-md text-sm font-mono transition-colors ${
              mode === "url" ? "bg-signal text-base-bg" : "text-text-muted hover:text-text-primary"
            }`}
          >
            За посиланням
          </button>
          <button
            onClick={() => setMode("text")}
            className={`px-3 py-1.5 rounded-md text-sm font-mono transition-colors ${
              mode === "text" ? "bg-signal text-base-bg" : "text-text-muted hover:text-text-primary"
            }`}
          >
            Вручну
          </button>
        </div>

        <ErrorBanner message={error} />

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          {mode === "url" ? (
            <div>
              <label className="block text-xs text-text-muted mb-1.5">
                Посилання на вакансію (work.ua або інший сайт з коректною розміткою)
              </label>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.work.ua/jobs/..."
                className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none font-mono"
              />
              <p className="text-xs text-text-faint mt-1.5">
                robota.ua блокує автоматичні запити — для неї встав текст вакансії вручну.
              </p>
            </div>
          ) : (
            <>
              <div>
                <label className="block text-xs text-text-muted mb-1.5">Назва посади (необов'язково)</label>
                <input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none"
                  placeholder="Python Developer"
                />
              </div>
              <div>
                <label className="block text-xs text-text-muted mb-1.5">Текст вакансії</label>
                <textarea
                  required
                  rows={8}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none"
                  placeholder="Встав повний текст опису вакансії..."
                />
              </div>
            </>
          )}
          <PrimaryButton type="submit" disabled={submitting}>
            {submitting ? "Обробка..." : "Додати вакансію"}
          </PrimaryButton>
        </form>
      </Card>

      {loading ? (
        <Spinner label="Завантажую вакансії..." />
      ) : jobs.length === 0 ? (
        <Card className="text-center py-10">
          <p className="text-text-muted text-sm">Ще немає жодної вакансії.</p>
        </Card>
      ) : (
        <div className="grid gap-3">
          {jobs.map((job) => (
            <Card key={job.id} className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{job.title || "Без назви"}</div>
                <div className="text-xs text-text-muted font-mono mt-1">
                  {job.parsed_data?.required_skills?.length || 0} обов'язкових навичок ·{" "}
                  {job.parsed_data?.nice_to_have?.length || 0} бажаних
                </div>
                <div className="text-xs text-text-faint mt-1">
                  Додано {new Date(job.created_at).toLocaleDateString("uk-UA", { day: "numeric", month: "short", year: "numeric" })}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Link to={`/analyze?jobId=${job.id}`}>
                  <SecondaryButton>Аналізувати</SecondaryButton>
                </Link>
                <button
                  onClick={() => handleDelete(job.id)}
                  className="text-text-faint hover:text-gap text-sm px-2"
                  title="Видалити"
                >
                  ✕
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </Layout>
  );
}
