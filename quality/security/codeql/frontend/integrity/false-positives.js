#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { readJsonFile, requireArray, requireDictionary, requireString } from '#shared/json.js';

import {
  CODEQL_FALSE_POSITIVE_FILE,
  CODEQL_FALSE_POSITIVE_PROJECTS,
  CODEQL_PROJECT_ROOT,
} from '#config/security/codeql/frontend/false-positives.js';

const REPO_ROOT = process.cwd();

function isInsideProject(projectRoot, targetPath) {
  const relativePath = path.relative(projectRoot, targetPath);
  if (relativePath === '') {
    return true;
  }
  return !relativePath.startsWith('..') && !path.isAbsolute(relativePath);
}

function validateFalsePositiveFile(project, configPath) {
  const errors = [];
  const parsed = requireDictionary(
    readJsonFile(configPath, `${project} CodeQL false positives`),
    'CodeQL config',
  );
  const ignoredEntries = requireArray(parsed.ignored, `${project}.ignored`);

  for (const [index, entry] of ignoredEntries.entries()) {
    const ignored = requireDictionary(entry, `${project}.ignored[${index}]`);
    const uri = requireString(ignored.uri, `${project}.ignored[${index}].uri`);
    // reason: The next guard rejects paths outside the repository before any file access.
    // bearer:disable javascript_lang_path_traversal
    const targetPath = path.resolve(REPO_ROOT, uri);

    if (!isInsideProject(REPO_ROOT, targetPath)) {
      errors.push(`${project}: ignored URI escapes repository root: ${uri}`);
      continue;
    }

    if (!fs.existsSync(targetPath)) {
      errors.push(`${project}: ignored URI does not exist: ${uri}`);
    }
  }

  return errors;
}

/**
 * Check that each CodeQL exception names an existing file inside the repository.
 * @returns Configuration failures, or an empty array when all entries are valid.
 */
function validateFalsePositives() {
  const errors = [];

  for (const project of CODEQL_FALSE_POSITIVE_PROJECTS) {
    // reason: Every path component comes from the fixed local CodeQL policy.
    // bearer:disable javascript_lang_path_traversal
    const configPath = path.join(
      REPO_ROOT,
      CODEQL_PROJECT_ROOT,
      project,
      CODEQL_FALSE_POSITIVE_FILE,
    );
    if (!fs.existsSync(configPath)) {
      errors.push(`${project}: required CodeQL finding policy is missing`);
      continue;
    }

    errors.push(...validateFalsePositiveFile(project, configPath));
  }

  return errors;
}

const errors = validateFalsePositives();
if (errors.length > 0) {
  console.error('CodeQL false-positive integrity failed:');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('CodeQL false-positive integrity passed.');

export { validateFalsePositives };
