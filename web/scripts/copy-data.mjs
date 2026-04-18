#!/usr/bin/env node
// Copy data/characters/*.json into web/public/data/ so Vite serves them.

import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "..", "..");
const srcDir = path.join(repoRoot, "data", "characters");
const destDir = path.join(repoRoot, "web", "public", "data");

async function main() {
  await fs.rm(destDir, { recursive: true, force: true });
  await fs.mkdir(destDir, { recursive: true });
  const entries = await fs.readdir(srcDir);
  for (const name of entries) {
    if (!name.endsWith(".json")) continue;
    await fs.copyFile(path.join(srcDir, name), path.join(destDir, name));
  }
  console.log(`copied ${entries.filter((n) => n.endsWith(".json")).length} files → ${path.relative(repoRoot, destDir)}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
