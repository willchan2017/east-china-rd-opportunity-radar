import type { Config } from "tailwindcss";
export default {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: { extend: { colors: { ink: "#17211b", paper: "#f5f7f4", forest: "#1e4936", lime: "#c7f17a", line: "#dce3dc" }, boxShadow: { panel: "0 1px 2px rgba(23,33,27,.04), 0 8px 30px rgba(23,33,27,.04)" } } },
  plugins: []
} satisfies Config;

