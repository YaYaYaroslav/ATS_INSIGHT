import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Layout from "../components/Layout.jsx";
import { Card, Spinner, ErrorBanner, PrimaryButton } from "../components/ui.jsx";
import { resumesApi } from "../api/endpoints.js";

function scoreColor(score) {
  if (score == null) return "text-text-faint";
  if (score >= 75) return "text-match";
  if (score >= 50) return "text-signal";
  return "text-gap";
}

export default function ResumeVersionsPage() {
  const { id } = useParams();
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    resumesApi
      .versions(id)
      .then(setVersions)
      .catch(() => setError("Не вдалося завантажити версії резюме"))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <Layout>
      <h1 className="font-display text-2xl font-semibold mb-1">Порівняння версій</h1>
      <p className="text-text-muted text-sm mb-8">
        Прогрес твого резюме від версії до версії — завантаж нову версію на сторінці резюме
      </p>

      <ErrorBanner message={error} />

      {loading ? (
        <Spinner label="Завантажую версії..." />
      ) : (
        <Card className="p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-base-border text-text-muted text-xs uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-normal">Версія</th>
                <th className="text-left px-5 py-3 font-normal">ATS Score</th>
                <th className="text-left px-5 py-3 font-normal">Match</th>
                <th className="text-left px-5 py-3 font-normal">AI Score</th>
                <th className="text-left px-5 py-3 font-normal">Дата</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {versions.map((v) => (
                <tr key={v.resume_id} className="border-b border-base-border last:border-0">
                  <td className="px-5 py-3.5 font-medium">{v.label || `v${v.version}`}</td>
                  <td className={`px-5 py-3.5 font-mono ${scoreColor(v.ats_score)}`}>
                    {v.ats_score != null ? Math.round(v.ats_score) : "—"}
                  </td>
                  <td className="px-5 py-3.5 font-mono text-text-muted">
                    {v.match_percentage != null ? `${Math.round(v.match_percentage)}%` : "—"}
                  </td>
                  <td className="px-5 py-3.5 font-mono text-text-muted">
                    {v.ai_score != null ? `${v.ai_score.toFixed(1)}/10` : "—"}
                  </td>
                  <td className="px-5 py-3.5 text-text-faint text-xs">
                    {new Date(v.created_at).toLocaleDateString("uk-UA")}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Link to={`/analyze?resumeId=${v.resume_id}`}>
                      <PrimaryButton className="text-xs px-3 py-1.5">Аналізувати</PrimaryButton>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </Layout>
  );
}
