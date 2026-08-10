import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import Layout from "../components/Layout.jsx";
import { Card, SkillBadge, Spinner, ErrorBanner, SecondaryButton } from "../components/ui.jsx";
import ScoreGauge from "../components/ScoreGauge.jsx";
import { analysesApi } from "../api/endpoints.js";

const BREAKDOWN_LABELS = {
  skills_score: "Skills",
  experience_score: "Experience",
  education_score: "Education",
  keywords_score: "Keywords",
  formatting_score: "Formatting",
};

export default function AnalysisResultPage() {
  const { id } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [tips, setTips] = useState(null);
  const [loadingTips, setLoadingTips] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    analysesApi
      .get(id)
      .then(setAnalysis)
      .catch(() => setError("Could not load this analysis"));
  }, [id]);

  const handleInterviewTips = async () => {
    setLoadingTips(true);
    try {
      const data = await analysesApi.interviewTips(id);
      setTips(data.tips || []);
    } catch {
      setTips([]);
    } finally {
      setLoadingTips(false);
    }
  };

  if (error) {
    return (
      <Layout>
        <ErrorBanner message={error} />
      </Layout>
    );
  }

  if (!analysis) {
    return (
      <Layout>
        <Spinner label="Loading result..." />
      </Layout>
    );
  }

  const chartData = Object.entries(BREAKDOWN_LABELS).map(([key, label]) => ({
    label,
    value: analysis[key],
  }));

  return (
    <Layout>
      <h1 className="font-display text-2xl font-semibold mb-8">Analysis result</h1>

      <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-8 mb-8">
        <Card className="flex flex-col items-center justify-center gap-3">
          <ScoreGauge score={analysis.overall_score} />
          <div className="text-xs text-text-muted font-mono">
            Match: <span className="text-text-primary">{Math.round(analysis.match_percentage)}%</span>
          </div>
        </Card>

        <Card>
          <div className="text-xs uppercase tracking-wider text-text-muted mb-4">Score breakdown</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#262B35" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} stroke="#5B606C" tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="label" stroke="#8B909C" tick={{ fontSize: 12 }} width={90} />
              <Tooltip
                contentStyle={{ background: "#171A21", border: "1px solid #262B35", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#EDEEF2" }}
              />
              <Bar dataKey="value" fill="#F5B700" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card>
          <div className="text-xs uppercase tracking-wider text-text-muted mb-3">
            Matched ({analysis.matched_skills.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {analysis.matched_skills.length ? (
              analysis.matched_skills.map((s) => <SkillBadge key={s} label={s} variant="match" />)
            ) : (
              <span className="text-text-faint text-sm">No matches</span>
            )}
          </div>
        </Card>
        <Card>
          <div className="text-xs uppercase tracking-wider text-text-muted mb-3">
            Missing ({analysis.missing_skills.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {analysis.missing_skills.length ? (
              analysis.missing_skills.map((s) => <SkillBadge key={s} label={s} variant="gap" />)
            ) : (
              <span className="text-text-faint text-sm">No gaps 🎉</span>
            )}
          </div>
        </Card>
      </div>

      {(analysis.ai_recommendations?.length > 0 || analysis.ai_summary_rewrite) && (
        <Card className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="text-xs uppercase tracking-wider text-text-muted">AI recommendations</div>
            {analysis.ai_score != null && (
              <div className="font-mono text-sm text-signal">{analysis.ai_score.toFixed(1)}/10</div>
            )}
          </div>

          {analysis.ai_summary_rewrite && (
            <div className="mb-5 p-4 bg-base-surfaceAlt rounded-md border border-base-border">
              <div className="text-xs text-text-muted mb-2">Rewritten summary</div>
              <p className="text-sm text-text-primary leading-relaxed">{analysis.ai_summary_rewrite}</p>
            </div>
          )}

          <ul className="space-y-2.5">
            {analysis.ai_recommendations.map((rec, i) => (
              <li key={i} className="flex gap-3 text-sm text-text-primary">
                <span className="text-signal font-mono shrink-0">{String(i + 1).padStart(2, "0")}</span>
                {rec}
              </li>
            ))}
          </ul>
        </Card>
      )}

      <Card>
        <div className="flex items-center justify-between mb-3">
          <div className="text-xs uppercase tracking-wider text-text-muted">Interview tips</div>
          {!tips && (
            <SecondaryButton onClick={handleInterviewTips} disabled={loadingTips}>
              {loadingTips ? "Generating..." : "Generate"}
            </SecondaryButton>
          )}
        </div>
        {tips && (
          <ul className="space-y-2.5 mt-3">
            {tips.length ? (
              tips.map((tip, i) => (
                <li key={i} className="flex gap-3 text-sm text-text-primary">
                  <span className="text-signal font-mono shrink-0">{String(i + 1).padStart(2, "0")}</span>
                  {tip}
                </li>
              ))
            ) : (
              <span className="text-text-faint text-sm">Could not generate tips</span>
            )}
          </ul>
        )}
      </Card>
    </Layout>
  );
}
