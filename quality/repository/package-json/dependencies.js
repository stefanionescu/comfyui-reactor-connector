import fs from 'node:fs';
import path from 'node:path';
import { PACKAGE_JSON_DEFAULT_FILES } from '#config/package-json/manifest.js';

import {
  BUN_TOOL_NAME,
  BUN_TOOL_REGEX,
  MISE_TOOL_FILE,
} from '#config/package-json/dependencies.js';

const repoRoot = process.cwd();
const errors = [];

function readMiseBunVersion() {
  const source = fs.readFileSync(path.join(repoRoot, MISE_TOOL_FILE), 'utf8');
  const match = source.match(BUN_TOOL_REGEX);
  if (!match) {
    errors.push(`${MISE_TOOL_FILE}: missing ${BUN_TOOL_NAME} tool version`);
    return '';
  }
  return match[1];
}

const expectedPackageSpec = `${BUN_TOOL_NAME}@${readMiseBunVersion()}`;

for (const packageFile of PACKAGE_JSON_DEFAULT_FILES) {
  const parsed = JSON.parse(fs.readFileSync(path.join(repoRoot, packageFile), 'utf8'));
  if (parsed.packageManager !== expectedPackageSpec) {
    errors.push(`${packageFile}: packageManager must be ${expectedPackageSpec}`);
  }
}

if (errors.length > 0) {
  console.error('package dependency policy failed:');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('package dependency policy passed.');
