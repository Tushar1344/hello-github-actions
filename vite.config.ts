import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves this project under /hello-github-actions/.
// Allow overriding the base (e.g. "/") via VITE_BASE for local/Vercel builds.
const base = process.env.VITE_BASE ?? "/chip-design/";

export default defineConfig({
  base,
  plugins: [react()],
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
