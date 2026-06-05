import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// Build output is written straight into the Python package so the wheel ships
// the compiled SPA. Students never run Node — Vite only runs at dev/CI time.
export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: "../src/ai9414/frontend/web",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:9414",
    },
  },
});
