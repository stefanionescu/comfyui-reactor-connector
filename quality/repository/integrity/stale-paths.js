import fs from 'node:fs';
import path from 'node:path';
import { visibleFiles } from '#shared/files.js';

import {
  STALE_TOOLING_PATHS,
  STALE_TEXT_EXEMPTS,
  STALE_PATH_TEXT_ROOTS,
  STALE_SECURITY_PATHS,
} from '#config/folders.js';

const repoRoot = process.cwd();
const textExemptFiles = new Set(STALE_TEXT_EXEMPTS);
const errors = [];

const publicFiles = visibleFiles(repoRoot);

for (const entryPath of STALE_PATH_TEXT_ROOTS) {
  for (const relativePath of publicFiles) {
    if (relativePath !== entryPath && !relativePath.startsWith(`${entryPath}/`)) continue;
    const absolutePath = path.join(repoRoot, relativePath);
    if (textExemptFiles.has(relativePath)) {
      continue;
    }
    if (
      relativePath.endsWith('.png') ||
      relativePath.endsWith('.jpg') ||
      relativePath.endsWith('.jpeg')
    ) {
      continue;
    }
    const bytes = fs.readFileSync(absolutePath);
    if (bytes.includes(0)) continue;
    const content = bytes.toString('utf8');
    for (const stalePath of [...STALE_TOOLING_PATHS, ...STALE_SECURITY_PATHS]) {
      if (content.includes(stalePath)) {
        errors.push(`${relativePath}: stale path reference to ${stalePath}`);
      }
    }
  }
}

for (const staleToolingPath of STALE_TOOLING_PATHS) {
  if (fs.existsSync(path.join(repoRoot, staleToolingPath))) {
    errors.push(`legacy tooling path still exists: ${staleToolingPath}`);
  }
}

if (errors.length > 0) {
  console.error('stale path integrity failed:');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('stale path integrity passed.');
