import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { authApi } from "../api/endpoints.js";
import { PrimaryButton, SecondaryButton, ErrorBanner } from "../components/ui.jsx";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [needsVerification, setNeedsVerification] = useState(false);
  const [resendStatus, setResendStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setNeedsVerification(false);
    setResendStatus("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      if (err.response?.status === 403) {
        setNeedsVerification(true);
        setError(err.response?.data?.detail || "Email не підтверджено");
      } else {
        setError(err.response?.data?.detail || "Невірний email або пароль");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResendStatus("sending");
    try {
      await authApi.resendVerification(email);
      setResendStatus("sent");
    } catch {
      setResendStatus("sent"); // відповідь бекенду навмисно завжди нейтральна
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-bg text-text-primary font-body px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="font-display text-2xl font-semibold">
            ATS <span className="text-signal">Insight</span>
          </div>
          <div className="text-text-muted text-sm mt-2">Увійди, щоб перевірити своє резюме</div>
        </div>

        <form onSubmit={handleSubmit} className="bg-base-surface border border-base-border rounded-lg p-6 space-y-4">
          <ErrorBanner message={error} />

          {needsVerification && (
            <div className="text-sm">
              {resendStatus === "sent" ? (
                <p className="text-text-muted">Якщо акаунт існує — новий лист вже надісланий.</p>
              ) : (
                <SecondaryButton type="button" onClick={handleResend} disabled={resendStatus === "sending"} className="w-full">
                  {resendStatus === "sending" ? "Надсилаю..." : "Надіслати лист підтвердження ще раз"}
                </SecondaryButton>
              )}
            </div>
          )}

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
            <label className="block text-xs text-text-muted mb-1.5">Пароль</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-base-surfaceAlt border border-base-border rounded-md px-3 py-2.5 text-sm focus:border-signal outline-none"
              placeholder="••••••••"
            />
          </div>
          <PrimaryButton type="submit" disabled={loading} className="w-full">
            {loading ? "Вхід..." : "Увійти"}
          </PrimaryButton>
        </form>

        <div className="text-center text-sm text-text-muted mt-4">
          Немає акаунта?{" "}
          <Link to="/register" className="text-signal hover:underline">
            Зареєструватись
          </Link>
        </div>
      </div>
    </div>
  );
}
