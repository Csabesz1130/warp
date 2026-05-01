import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forge: {
          bg: "#0b0f14",
          panel: "#11171f",
          panel2: "#161e29",
          border: "#1f2a37",
          text: "#e6edf3",
          muted: "#7d8898",
          accent: "#22d3a8",
          accent2: "#7c8cf8",
          warn: "#f5a524",
          danger: "#f0506e",
          ok: "#22d3a8",
        },
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
