import fs from 'node:fs';
import path from 'node:path';
import { valid } from 'semver';
import { parseArgs } from 'node:util';

import {
  PACKAGE_JSON_DEFAULT_FILES,
  PACKAGE_JSON_DEPENDENCY_KEYS,
} from '#config/package-json/manifest.js';

const { positionals } = parseArgs({ allowPositionals: true });
const files = positionals.length ? positionals : PACKAGE_JSON_DEFAULT_FILES;
const errors = [];

/**
 * Require an exact dependency version without choosing a replacement for a range.
 * @param content - The manifest text.
 * @param file - The manifest path for diagnostics.
 * @returns Failures identified by dependency section and package name.
 */
function checkExactVersions(content, file) {
  const failures = [];
  const sections = new Map(Object.entries(JSON.parse(content)));
  for (const section of PACKAGE_JSON_DEPENDENCY_KEYS) {
    const dependencies = sections.get(section);
    if (!dependencies) continue;
    for (const [name, version] of Object.entries(dependencies)) {
      if (valid(version) !== null) continue;
      failures.push(
        `${file}: ${section}[${JSON.stringify(name)}]: Choose an exact version; found ${JSON.stringify(version)}.`,
      );
    }
  }
  return failures;
}

for (const file of files) {
  const relative = path.relative(process.cwd(), file);
  try {
    // eslint-disable-next-line security/detect-non-literal-fs-filename -- Read only the default manifests or paths explicitly supplied to this local CLI.
    const content = fs.readFileSync(file, 'utf8');
    errors.push(...checkExactVersions(content, relative));
  } catch (error) {
    if (error instanceof SyntaxError) errors.push(`${relative}: Correct the invalid JSON.`);
    else if (error instanceof Error && 'code' in error && error.code === 'ENOENT')
      errors.push(`${relative}: The manifest does not exist.`);
    else throw error;
  }
}

if (errors.length) {
  for (const error of errors) console.error(error);
  process.exitCode = 1;
} else console.log('Dependency versions are exact.');
