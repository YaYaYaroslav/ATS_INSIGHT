import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout.jsx";
import { Card, Spinner, ErrorBanner } from "../components/ui.jsx";
import { analysesApi } from "../api/endpoints.js";

function scoreColor(score) {
  if (score >= 75) return "text-match";
  if (score >= 50) return "text-signal";
  return "text-gap";
}

export default function HistoryPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    analysesApi
      .list()
      .then(setItems)
      .catch(() => setError("Could not load history"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <h1 className="font-display text-2xl font-semibold mb-1">Analysis history</h1>
      <p className="text-text-muted text-sm mb-8">All past resume-vs-job checks</p>

      <ErrorBanner message={error} />

      {loading ? (
        <Spinner label="Loading..." />
      ) : items.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-text-muted text-sm">No analyses yet.</p>
        </Card>
      ) : (
        <div className="grid gap-2">
          {items.map((item) => (
            <Link key={item.id} to={`/analyses/${item.id}`}>
              <Card className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 hover:border-signal/40 transition-colors">
                <div className="text-sm">
                  <span className="text-text-muted font-mono">#{item.id}</span>{" "}
                  <span className="text-text-faint text-xs ml-2">
                    {new Date(item.created_at).toLocaleString("en-US")}
                  </span>
                </div>
                <div className="flex items-center gap-6 font-mono text-sm">
                  <span className="text-text-muted">Match {Math.round(item.match_percentage)}%</span>
                  <span className={scoreColor(item.overall_score)}>{Math.round(item.overall_score)}/100</span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  );
}
