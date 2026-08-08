import React, { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { authApi } from "../api/endpoints.js";
import { Card } from "../components/ui.jsx";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState("loading"); // loading | success | error
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Посилання неповне — відсутній токен підтвердження.");
      return;
    }
    authApi
      .verifyEmail(token)
      .then((data) => {
        setStatus("success");
        setMessage(data.message || "Email підтверджено.");
      })
      .catch((err) => {
        setStatus("error");
        setMessage(err.response?.data?.detail || "Не вдалося підтвердити email.");
      });
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-bg text-text-primary font-body px-4">
      <div className="w-full max-w-sm text-center">
        <div className="font-display text-2xl font-semibold mb-4">
          ATS <span className="text-signal">Insight</span>
        </div>
        <Card>
          {status === "loading" && <p className="text-sm text-text-muted">Підтверджую email...</p>}
          {status === "success" && (
            <>
              <div className="text-match text-2xl mb-3">✓</div>
              <p className="text-sm text-text-primary">{message}</p>
            </>
          )}
          {status === "error" && (
            <>
              <div className="text-gap text-2xl mb-3">✕</div>
              <p className="text-sm text-text-primary">{message}</p>
            </>
          )}
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
