import React from "react";

/** Signature UI element: a circular gauge that "scans" the resume score, radar-style. */
export default function ScoreGauge({ score = 0, size = 168, label = "ATS Score" }) {
  const clamped = Math.max(0, Math.min(100, score));
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - clamped / 100);

  const color = clamped >= 75 ? "#2FD9A8" : clamped >= 50 ? "#F5B700" : "#FF6B5E";

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="scan-sweep" style={{ transformOrigin: "50% 50%" }}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#262B35" strokeWidth="10" />
      </svg>
      <svg width={size} height={size} className="absolute top-0 left-0 -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          style={{ transition: "stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1), stroke 0.6s" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-mono text-3xl font-semibold text-text-primary">{Math.round(clamped)}</span>
        <span className="text-xs uppercase tracking-wider text-text-muted mt-1">{label}</span>
      </div>
    </div>
  );
}
