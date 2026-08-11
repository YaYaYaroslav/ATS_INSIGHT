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
      setError("Could not load your jobs");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this job and all related analyses?")) return;
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
      setError(err.response?.data?.detail || "Could not process this job. Try pasting the text manually.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout>
      <h1 className="font-display text-2xl font-semibold mb-1">Jobs</h1>
      <p className="text-text-muted text-sm mb-8">
        Paste a work.ua job link and we'll pull the description automatically. robota.ua blocks
        automated requests, so for that site paste the description manually (the "Manual" tab).
      </p>

      <Card className="mb-8">
        <div className="flex gap-2 mb-5">
          <button
            onClick={() => setMode("url")}
            className={`px-3 py-1.5 rounded-md text-sm font-mono transition-colors ${
              mode === "url" ? "bg-signal text-base-bg" : "text-text-muted hover:text-text-primary"
            }`}
          >
            From link
          </button>
          <button
            onClick={() => setMode("text")}
            className={`px-3 py-1.5 rounded-md text-sm font-mono transition-colors ${
              mode === "text" ? "bg-signal text-base-bg" : "text-text-muted hover:text-text-primary"
            }`}
          >
            Manual
          </button>
        </div>

        <ErrorBanner message={error} />

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          {mode === "url" ? (
            <div>
              <label className="block text-xs text-text-muted mb-1.5">
                Job posting link (work.ua, or any other site with proper markup)
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
                robota.ua blocks automated requests — paste that description manually instead.
              </p>
            </div>
          ) : (
            <>
              <div>
                <label className="block text-xs text-text-muted mb-1.5">Job title (optional)</label>
                <input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none"
                  placeholder="Python Developer"
                />
              </div>
              <div>
                <label className="block text-xs text-text-muted mb-1.5">Job description</label>
                <textarea
                  required
                  rows={8}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none"
                  placeholder="Paste the full job description..."
                />
              </div>
            </>
          )}
          <PrimaryButton type="submit" disabled={submitting}>
            {submitting ? "Processing..." : "Add job"}
          </PrimaryButton>
        </form>
      </Card>

      {loading ? (
        <Spinner label="Loading jobs..." />
      ) : jobs.length === 0 ? (
        <Card className="text-center py-10">
          <p className="text-text-muted text-sm">No jobs yet.</p>
        </Card>
      ) : (
        <div className="grid gap-3">
          {jobs.map((job) => (
            <Card key={job.id} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <div className="font-medium text-sm">{job.title || "Untitled"}</div>
                <div className="text-xs text-text-muted font-mono mt-1">
                  {job.parsed_data?.required_skills?.length || 0} required skills ·{" "}
                  {job.parsed_data?.nice_to_have?.length || 0} nice-to-have
                </div>
                <div className="text-xs text-text-faint mt-1">
                  Added{" "}
                  {new Date(job.created_at).toLocaleDateString("en-US", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                  })}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Link to={`/analyze?jobId=${job.id}`}>
                  <SecondaryButton>Analyze</SecondaryButton>
                </Link>
                <button
                  onClick={() => handleDelete(job.id)}
                  className="text-text-faint hover:text-gap text-sm px-2"
                  title="Delete"
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
