#!/usr/bin/env node

import { PACKAGE_SCOPES } from '#config/repository.js';
import { readJsonFile, requireArray, requireDictionary } from '#shared/json.js';

import {
  LICENSE_CHECKER_ALLOW_MODE,
  LICENSE_CHECKER_EXCLUDE_MODE,
  LICENSE_CHECKER_MODES,
} from '#config/package-json/licenses/modes.js';

const usage = `Usage: node read-policy.js <config-path> <${PACKAGE_SCOPES.join('|')}> <${LICENSE_CHECKER_MODES.join('|')}>`;
const [configPath, project, mode] = process.argv.slice(2);
const projects = new Set(PACKAGE_SCOPES);
const modes = new Set(LICENSE_CHECKER_MODES);

if (!configPath || !projects.has(project) || !modes.has(mode)) {
  console.error(usage);
  process.exit(2);
}

const config = requireDictionary(
  readJsonFile(configPath, 'license checker config'),
  'license checker config',
);

if (mode === LICENSE_CHECKER_ALLOW_MODE) {
  process.stdout.write(requireArray(config.onlyAllow, 'onlyAllow').join(';'));
} else if (mode === LICENSE_CHECKER_EXCLUDE_MODE) {
  const excludePackages = requireDictionary(config.excludePackages ?? {}, 'excludePackages');
  process.stdout.write(
    requireArray(excludePackages[project] ?? [], `excludePackages.${project}`).join(';'),
  );
}
