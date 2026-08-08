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
      .catch(() => setError("Не вдалося завантажити історію"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <h1 className="font-display text-2xl font-semibold mb-1">Історія аналізів</h1>
      <p className="text-text-muted text-sm mb-8">Всі попередні перевірки резюме проти вакансій</p>

      <ErrorBanner message={error} />

      {loading ? (
        <Spinner label="Завантажую..." />
      ) : items.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-text-muted text-sm">Ще немає жодного аналізу.</p>
        </Card>
      ) : (
        <div className="grid gap-2">
          {items.map((item) => (
            <Link key={item.id} to={`/analyses/${item.id}`}>
              <Card className="flex items-center justify-between hover:border-signal/40 transition-colors">
                <div className="text-sm">
                  <span className="text-text-muted font-mono">#{item.id}</span>{" "}
                  <span className="text-text-faint text-xs ml-2">
                    {new Date(item.created_at).toLocaleString("uk-UA")}
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
