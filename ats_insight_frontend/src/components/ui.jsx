import React from "react";

export function SkillBadge({ label, variant = "neutral" }) {
  const styles = {
    match: "bg-match/10 text-match border-match/30",
    gap: "bg-gap/10 text-gap border-gap/30",
    neutral: "bg-base-surfaceAlt text-text-muted border-base-border",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono border ${styles[variant]}`}>
      {label}
    </span>
  );
}

export function Card({ children, className = "" }) {
  return (
    <div className={`bg-base-surface border border-base-border rounded-lg p-6 ${className}`}>{children}</div>
  );
}

export function Spinner({ label = "Завантаження..." }) {
  return (
    <div className="flex items-center gap-3 text-text-muted text-sm">
      <span className="w-4 h-4 border-2 border-signal border-t-transparent rounded-full animate-spin" />
      {label}
    </div>
  );
}

export function PrimaryButton({ children, className = "", as: Component = "button", ...props }) {
  return (
    <Component
      className={`inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-md bg-signal text-base-bg font-medium text-sm hover:bg-signal-dim transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
}

export function SecondaryButton({ children, className = "", as: Component = "button", ...props }) {
  return (
    <Component
      className={`inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-md border border-base-border text-text-primary font-medium text-sm hover:bg-base-surfaceAlt transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
}

export function ErrorBanner({ message }) {
  if (!message) return null;
  return (
    <div className="border border-gap/30 bg-gap/10 text-gap text-sm rounded-md px-4 py-3">{message}</div>
  );
}
