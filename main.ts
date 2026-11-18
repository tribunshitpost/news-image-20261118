// World News One Page — make.fun entry for news-image-20261118.
//
// The entry is a program that writes one image to /output/entry.png.
// The image is the pre-rendered poster held in this repository
// (entry.png, 1024x1024, drawn by draw_poster.py from reporting verified
// on 18 November 2026), so this program copies it there byte for byte.
// Node 22, standard library only, no network, deterministic: every run
// writes exactly the bytes this repository holds.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
// /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { createHash } from "node:crypto";
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const PNG_SIGNATURE = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);
const MAX_BYTES = 1024 * 1024;
const EXPECTED_WIDTH = 1024;
const EXPECTED_HEIGHT = 1024;

function readPoster() {
  const source = new URL("./entry.png", import.meta.url);
  const bytes = readFileSync(source);
  if (bytes.length > MAX_BYTES) {
    throw new Error(
      `entry.png is ${bytes.length} bytes, over the 1 MiB cap`,
    );
  }
  if (!bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
    throw new Error("entry.png is not a PNG file");
  }
  if (bytes.subarray(12, 16).toString("ascii") !== "IHDR") {
    throw new Error("entry.png has no IHDR chunk where one is expected");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== EXPECTED_WIDTH || height !== EXPECTED_HEIGHT) {
    throw new Error(
      `entry.png is ${width}x${height}, expected 1024x1024`,
    );
  }
  return bytes;
}

const poster = readPoster();
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(new URL("./entry.png", import.meta.url), target);

// Confirm the copy is byte-identical to the source, so both grader runs
// see exactly the image this repository holds.
const copied = readFileSync(target);
if (!copied.equals(poster)) {
  throw new Error("copied entry.png differs from the repository image");
}
const written = statSync(target).size;
const digest = createHash("sha256").update(copied).digest("hex");
console.log(
  `Wrote ${target} (${written} bytes, 1024x1024, sha256 ${digest}, verified)`,
);
