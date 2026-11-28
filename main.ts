// Black Friday Deal Finder: hands the site in.
//
// The site is this directory's app/ folder (plain static files: an
// index, a stylesheet, the deal data and the code that renders it),
// and screenshots/ holds three or four renders of it in a browser.
// This program copies both into the output directory and writes
// dossier.json, the summary the judge reads, with the vendored
// make.fun library. Nothing here is fetched over the network, and
// the library file vendor/makefun-frontend.ts is the kit's own copy,
// unchanged: the scorer rebuilds the dossier with its copy and the
// two must match byte for byte.
//
// Run it from this directory (Node 22, standard library only):
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
// Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output.

import { copyFileSync, existsSync, mkdirSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildDossier } from "./vendor/makefun-frontend.ts";

const here = fileURLToPath(new URL(".", import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

// The scorer's own caps: only text_max_bytes shapes the bytes, the
// rest refuse an entry the scorer would refuse (more than 4
// screenshots or one over 256 KiB; more than 993 entries in app/ or
// 16 MiB of app files).
const CAPS = {
  text_max_bytes: 163840,
  screenshots: { max: 4, max_bytes: 262144 },
  app_max_files: 993,
  app_max_bytes: 16777216,
};

function copyTree(from: string, to: string): number {
  let copied = 0;
  mkdirSync(to, { recursive: true });
  for (const name of readdirSync(from)) {
    const source = join(from, name);
    const target = join(to, name);
    if (statSync(source).isDirectory()) {
      copied += copyTree(source, target);
    } else {
      copyFileSync(source, target);
      copied += 1;
    }
  }
  return copied;
}

function fail(message: string): never {
  throw new Error("hand-in refused: " + message);
}

const appDir = join(here, "app");
const shotsDir = join(here, "screenshots");
if (!existsSync(join(appDir, "index.html"))) fail("app/index.html is missing");
if (!existsSync(shotsDir)) fail("screenshots/ is missing");
const shots = readdirSync(shotsDir).filter((name) => /\.(png|jpe?g)$/i.test(name));
if (shots.length < 3 || shots.length > 4) {
  fail("screenshots/ must hold 3 or 4 images, found " + shots.length);
}

mkdirSync(outDir, { recursive: true });
const appFiles = copyTree(appDir, join(outDir, "app"));
const shotFiles = copyTree(shotsDir, join(outDir, "screenshots"));
const dossier = buildDossier(outDir, CAPS);
writeFileSync(join(outDir, "dossier.json"), dossier);

console.log(
  "handed in %d app files and %d screenshots to %s (%d dossier bytes)",
  appFiles,
  shotFiles,
  outDir,
  dossier.length,
);
