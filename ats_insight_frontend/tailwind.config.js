/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          bg: "#0F1115",
          surface: "#171A21",
          surfaceAlt: "#1E222B",
          border: "#262B35",
        },
        text: {
          primary: "#EDEEF2",
          muted: "#8B909C",
          faint: "#5B606C",
        },
        signal: {
          DEFAULT: "#F5B700",
          dim: "#B98600",
        },
        match: "#2FD9A8",
        gap: "#FF6B5E",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
