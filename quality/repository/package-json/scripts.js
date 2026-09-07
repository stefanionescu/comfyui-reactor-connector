import fs from 'node:fs';
import path from 'node:path';

import {
  PACKAGE_JSON_DEFAULT_FILES,
  PACKAGE_JSON_DIRECTORIES,
} from '#config/package-json/manifest.js';
import {
  BUN_RUN_SCRIPT_REGEX,
  PACKAGE_SCRIPT_CD_REGEX,
  ROOT_ALLOWED_SCRIPT_COMMANDS,
  MISE_RUN_SCRIPT_REGEX,
  SCRIPT_SECTION_PREFIX,
} from '#config/package-json/scripts.js';

const REPO_ROOT = process.cwd();
const errors = [];
const packageByDirectory = new Map([
  ...PACKAGE_JSON_DIRECTORIES.map((directory) => [directory, directory || '.']),
]);
const packageScripts = new Map();

for (const packageFile of PACKAGE_JSON_DEFAULT_FILES) {
  const absolutePath = path.join(REPO_ROOT, packageFile);
  const parsed = JSON.parse(fs.readFileSync(absolutePath, 'utf8'));
  const packageName = packageFile === 'package.json' ? '.' : path.dirname(packageFile);
  packageScripts.set(packageName, parsed.scripts ?? {});
}

function projectFromDirectory(currentPackage, targetDirectory) {
  if (!targetDirectory) {
    return currentPackage;
  }
  // reason: This normalizes a package name for a fixed Map lookup; it does not access the filesystem.
  // bearer:disable javascript_lang_path_traversal
  const normalized = path.normalize(
    path.join(currentPackage === '.' ? '' : currentPackage, targetDirectory),
  );
  const firstSegment = normalized.split(path.sep).filter(Boolean)[0] ?? '.';
  return packageByDirectory.get(firstSegment) ?? currentPackage;
}

function validateBunRunReferences(origin, packageName, command) {
  let activePackage = packageName;
  for (const rawSegment of String(command).split('&&')) {
    const segment = rawSegment.trim();
    const cdMatch = segment.match(PACKAGE_SCRIPT_CD_REGEX);
    if (cdMatch) {
      activePackage = projectFromDirectory(activePackage, cdMatch[1].trim());
      continue;
    }

    for (const match of segment.matchAll(BUN_RUN_SCRIPT_REGEX)) {
      const scriptName = match[1];
      const scripts = packageScripts.get(activePackage);
      if (!scripts || !Object.hasOwn(scripts, scriptName)) {
        errors.push(
          `${origin}: bun run ${scriptName} does not exist in ${activePackage}/package.json`,
        );
      }
    }
  }
}

function validateRootScripts(scripts) {
  for (const [scriptName, command] of Object.entries(scripts)) {
    const expected = ROOT_ALLOWED_SCRIPT_COMMANDS[scriptName];
    if (!expected) {
      errors.push(
        `package.json:scripts.${scriptName}: root package scripts must be approved mise/build wrappers`,
      );
      continue;
    }
    if (command !== expected) {
      errors.push(`package.json:scripts.${scriptName}: expected "${expected}"`);
    }
  }

  for (const scriptName of Object.keys(ROOT_ALLOWED_SCRIPT_COMMANDS)) {
    if (!Object.hasOwn(scripts, scriptName)) {
      errors.push(`package.json:scripts.${scriptName}: required root wrapper script is missing`);
    }
  }
}

for (const [packageName, scripts] of packageScripts) {
  if (packageName === '.') {
    validateRootScripts(scripts);
  }

  for (const [scriptName, command] of Object.entries(scripts)) {
    if (scriptName.startsWith(SCRIPT_SECTION_PREFIX)) {
      errors.push(`${packageName}:scripts.${scriptName}: section marker scripts are not allowed`);
    }
    if (packageName !== '.' && MISE_RUN_SCRIPT_REGEX.test(command)) {
      errors.push(`${packageName}:scripts.${scriptName}: package scripts must not wrap mise tasks`);
    }
    validateBunRunReferences(`${packageName}:scripts.${scriptName}`, packageName, command);
  }
}

if (errors.length > 0) {
  console.error('package script policy failed:');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('package script policy passed.');
