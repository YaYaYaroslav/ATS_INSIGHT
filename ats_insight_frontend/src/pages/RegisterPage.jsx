import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { PrimaryButton, ErrorBanner, Card } from "../components/ui.jsx";

export default function RegisterPage() {
  const { register } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, fullName);
      setDone(true);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Не вдалося зареєструватись");
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-base-bg text-text-primary font-body px-4">
        <div className="w-full max-w-sm text-center">
          <div className="font-display text-2xl font-semibold mb-4">
            ATS <span className="text-signal">Insight</span>
          </div>
          <Card>
            <div className="text-signal text-2xl mb-3">✓</div>
            <p className="text-sm text-text-primary mb-2">Перевір пошту</p>
            <p className="text-sm text-text-muted">
              Ми надіслали лист на <span className="text-text-primary font-mono">{email}</span> з посиланням для
              підтвердження акаунта. Перейди за ним, щоб мати змогу увійти.
            </p>
          </Card>
          <div className="text-sm text-text-muted mt-4">
            <Link to="/login" className="text-signal hover:underline">
              До входу
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-bg text-text-primary font-body px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="font-display text-2xl font-semibold">
            ATS <span className="text-signal">Insight</span>
          </div>
          <div className="text-text-muted text-sm mt-2">Створи акаунт</div>
        </div>

        <form onSubmit={handleSubmit} className="bg-base-surface border border-base-border rounded-lg p-6 space-y-4">
          <ErrorBanner message={error} />
          <div>
            <label className="block text-xs text-text-muted mb-1.5">Ім'я (необов'язково)</label>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none"
              placeholder="Твоє ім'я"
            />
          </div>
          <div>
            <label className="block text-xs text-text-muted mb-1.5">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-xs text-text-muted mb-1.5">Пароль (мінімум 8 символів)</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none"
              placeholder="••••••••"
            />
          </div>
          <PrimaryButton type="submit" disabled={loading} className="w-full">
            {loading ? "Реєстрація..." : "Зареєструватись"}
          </PrimaryButton>
        </form>

        <div className="text-center text-sm text-text-muted mt-4">
          Вже є акаунт?{" "}
          <Link to="/login" className="text-signal hover:underline">
            Увійти
          </Link>
        </div>
      </div>
    </div>
  );
}
