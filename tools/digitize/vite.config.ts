import { defineConfig } from "vite";
import path from "node:path";

const repoRoot = path.resolve(__dirname, "..", "..");

export default defineConfig({
  base: "./",
  // Allow the digitizer to load reference SVGs directly from the repo's data/reference/.
  server: {
    fs: {
      allow: [repoRoot],
    },
    port: 5174,
  },
  resolve: {
    alias: {
      "@repo": repoRoot,
    },
  },
});
