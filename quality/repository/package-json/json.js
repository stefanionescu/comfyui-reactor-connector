import fs from 'node:fs';
import path from 'node:path';

import {
  PACKAGE_JSON_DEFAULT_FILES,
  PACKAGE_JSON_DEPENDENCY_KEYS,
  PACKAGE_JSON_FIX_FLAG,
  PACKAGE_JSON_LINT_MESSAGES,
  PACKAGE_JSON_RANGE_PATTERN,
} from '#config/package-json/manifest.js';

const repoRoot = process.cwd();
const defaultFiles = PACKAGE_JSON_DEFAULT_FILES.map((relativeFile) =>
  path.join(repoRoot, relativeFile),
);

const fix = process.argv.includes(PACKAGE_JSON_FIX_FLAG);
const explicitFiles = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const files = explicitFiles.length ? explicitFiles.map((f) => path.resolve(f)) : defaultFiles;

/**
 * Checks that dependency versions do not use range prefixes (^, ~, >=, etc.).
 * @param lines - Manifest text split into lines.
 * @param file - Manifest path used to locate dependency failures.
 * @returns Dependency version failures with manifest locations.
 */
const checkExactVersions = (lines, file) => {
  const errors = [];
  const parsed = JSON.parse(lines.join('\n'));

  for (const key of PACKAGE_JSON_DEPENDENCY_KEYS) {
    const deps = parsed[key];
    if (!deps) continue;

    for (const [pkg, version] of Object.entries(deps)) {
      if (PACKAGE_JSON_RANGE_PATTERN.test(version)) {
        const lineNum = lines.findIndex((l) => l.includes(`"${pkg}"`));
        errors.push({
          file: path.relative(repoRoot, file),
          line: lineNum + 1,
          message: `${PACKAGE_JSON_LINT_MESSAGES.rangePrefixIntro} ${key}: "${pkg}": "${version}" ${PACKAGE_JSON_LINT_MESSAGES.rangePrefixReplacement} "${version.replace(PACKAGE_JSON_RANGE_PATTERN, '')}"`,
        });
      }
    }
  }

  return errors;
};

/**
 * Strips range prefixes from dependency versions, pinning them to exact versions.
 * @param lines - Manifest text split into lines.
 * @returns The same line array with version range prefixes removed.
 */
const fixExactVersions = (lines) => {
  const parsed = JSON.parse(lines.join('\n'));

  const dependencies = PACKAGE_JSON_DEPENDENCY_KEYS.flatMap((key) =>
    Object.entries(parsed[key] ?? {}),
  );
  for (const [pkg, version] of dependencies) {
    if (!PACKAGE_JSON_RANGE_PATTERN.test(version)) continue;
    const pinned = version.replace(PACKAGE_JSON_RANGE_PATTERN, '');
    const index = lines.findIndex(
      (line) => line.includes(`"${pkg}"`) && line.includes(`"${version}"`),
    );
    if (index !== -1) lines[index] = lines[index].replace(`"${version}"`, `"${pinned}"`);
  }

  return lines;
};

let allErrors = [];

for (const file of files) {
  let content;
  try {
    content = fs.readFileSync(file, 'utf8');
  } catch (error) {
    if (error instanceof Error && 'code' in error && error.code === 'ENOENT') {
      console.error(
        `${PACKAGE_JSON_LINT_MESSAGES.fileNotFoundPrefix} ${path.relative(repoRoot, file)}`,
      );
      process.exitCode = 1;
      continue;
    }
    throw error;
  }

  let lines = content.split('\n');

  if (fix) {
    lines = fixExactVersions(lines);
    fs.writeFileSync(file, lines.join('\n'), 'utf8');
    console.log(`${PACKAGE_JSON_LINT_MESSAGES.fixedPrefix} ${path.relative(repoRoot, file)}`);
  } else {
    const versionErrors = checkExactVersions(lines, file);
    allErrors.push(...versionErrors);
  }
}

if (!fix) {
  if (allErrors.length) {
    console.error(PACKAGE_JSON_LINT_MESSAGES.violationsHeader);
    for (const err of allErrors) {
      console.error(`  ${err.file}:${err.line}: ${err.message}`);
    }
    console.error(`\n${allErrors.length} ${PACKAGE_JSON_LINT_MESSAGES.violationsSuffix}`);
    process.exitCode = 1;
  } else {
    console.log(PACKAGE_JSON_LINT_MESSAGES.pass);
  }
}
