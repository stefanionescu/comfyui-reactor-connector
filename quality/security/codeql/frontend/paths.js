import fs from 'node:fs';
import path from 'node:path';
import { parse } from 'yaml';
import { CODEQL_SCAN_FILE } from '#config/security/codeql/frontend/paths.js';

const repoRoot = process.cwd();
const errors = [];

const scanPolicyPath = path.join(repoRoot, CODEQL_SCAN_FILE);
// eslint-disable-next-line security/detect-non-literal-fs-filename -- CODEQL_SCAN_FILE selects the repository-owned scanner configuration.
const policy = parse(fs.readFileSync(scanPolicyPath, 'utf8'));
if (!Array.isArray(policy?.paths) || !policy.paths.length) {
  throw new Error('CodeQL configuration must include a nonempty paths list.');
}
for (const scanPath of policy.paths) {
  if (typeof scanPath !== 'string' || !scanPath.trim()) {
    throw new Error('Each CodeQL paths entry must be a nonempty string.');
  }
  const absolutePath = path.join(repoRoot, scanPath);
  // eslint-disable-next-line security/detect-non-literal-fs-filename -- Only check whether a path declared in the scanner configuration exists.
  if (!fs.existsSync(absolutePath)) {
    errors.push(`${CODEQL_SCAN_FILE}: paths entry "${scanPath}" does not exist in the repository`);
  }
}

if (errors.length > 0) {
  console.error('CodeQL scan path policy failed:');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('CodeQL scan path policy passed.');
