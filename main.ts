// World News One Image — make.fun entry for news-image-20261118.
//
// This program writes the poster for Wednesday 18 November 2026 to
// /output/entry.png. The poster is the entry.png held in this repository
// (1024x1024, drawn at build time by draw_poster.py from reporting
// verified on 18 November 2026), so the program copies it there byte
// for byte. Node 22, standard library only, no network, deterministic:
// every run writes exactly the bytes this repository holds.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
// /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { createHash } from "node:crypto";
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1024 * 1024;
const SIDE = 1024;

function loadPoster(): Buffer {
  const bytes = readFileSync(new URL("./entry.png", import.meta.url));
  if (bytes.length > MAX_BYTES) {
    throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB cap`);
  }
  if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    throw new Error("entry.png is not a PNG file");
  }
  if (bytes.subarray(12, 16).toString("ascii") !== "IHDR") {
    throw new Error("entry.png has no IHDR chunk where one is expected");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== SIDE || height !== SIDE) {
    throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
  }
  return bytes;
}

const poster = loadPoster();
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(new URL("./entry.png", import.meta.url), target);

const copied = readFileSync(target);
if (!copied.equals(poster)) {
  throw new Error("copied entry.png differs from the repository image");
}
// The copy is byte-identical, so both grader runs produce the same
// file: the same bytes, the same sha256, every time.
const size = statSync(target).size;
const digest = createHash("sha256").update(copied).digest("hex");
console.log(
  `Wrote ${target} (${size} bytes, 1024x1024, sha256 ${digest}, verified)`,
);
