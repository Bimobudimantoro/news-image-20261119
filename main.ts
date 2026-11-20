// Entrypoint for news-image-20261119 — copies pre-generated entry.png to /output/entry.png
// Deterministic: same input file always produces same output bytes.
//
// Local test: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

copyFileSync(
  new URL('./entry.png', import.meta.url),
  join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png')
);