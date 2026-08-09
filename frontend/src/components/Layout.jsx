import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const NAV_ITEMS = [
  { to: "/", label: "Резюме", icon: "▤" },
  { to: "/jobs", label: "Вакансії", icon: "◨" },
  { to: "/analyze", label: "Новий аналіз", icon: "◎" },
  { to: "/history", label: "Історія", icon: "≣" },
];

export default function Layout({ children }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex bg-base-bg text-text-primary font-body">
      <aside className="w-60 shrink-0 border-r border-base-border flex flex-col">
        <div className="px-6 py-6">
          <div className="font-display text-lg font-semibold tracking-tight">
            ATS <span className="text-signal">Insight</span>
          </div>
          <div className="text-xs text-text-faint mt-1 font-mono">резюме ↔ вакансія</div>
        </div>

        <nav className="flex-1 px-3 space-y-1">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-colors ${
                  isActive
                    ? "bg-base-surfaceAlt text-text-primary"
                    : "text-text-muted hover:text-text-primary hover:bg-base-surface"
                }`
              }
            >
              <span className="font-mono text-signal">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 pb-6">
          <button
            onClick={handleLogout}
            className="w-full text-left px-3 py-2.5 rounded-md text-sm text-text-muted hover:text-gap hover:bg-base-surface transition-colors"
          >
            Вийти
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-8 py-10">{children}</div>
      </main>
    </div>
  );
}
