import fs from 'node:fs';
import path from 'node:path';
import { CODEQL_PROJECT_SCANS } from '#config/security/codeql/frontend/projects.js';

const REPO_ROOT = process.cwd();
const errors = [];

for (const { file, sourceRoot = '.' } of CODEQL_PROJECT_SCANS) {
  const scanPolicyPath = path.join(REPO_ROOT, file);
  const sourceRootPath = path.join(REPO_ROOT, sourceRoot);
  const lines = fs.readFileSync(scanPolicyPath, 'utf8').split('\n');
  let inPathsSection = false;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (line.startsWith('paths-ignore:')) {
      break;
    }
    if (line.startsWith('paths:')) {
      inPathsSection = true;
      continue;
    }
    if (!inPathsSection || !line.startsWith('- ')) {
      continue;
    }

    const scanPath = line
      .slice(2)
      .trim()
      .replaceAll(/^['"]|['"]$/gu, '');
    const absolutePath = path.join(sourceRootPath, scanPath);
    if (!fs.existsSync(absolutePath)) {
      errors.push(`${file}: paths entry "${scanPath}" does not exist under ${sourceRoot}/`);
    }
  }
}

if (errors.length > 0) {
  console.error('CodeQL project path policy failed:');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('CodeQL project path policy passed.');
