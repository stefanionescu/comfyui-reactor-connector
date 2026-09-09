import fs from 'node:fs';
import path from 'node:path';
import { PACKAGE_JSON_DEFAULT_FILES } from '#config/package-json/manifest.js';
import { SEMVER_PREFIX_REGEX, SEMVER_SUFFIX_REGEX, UNICORN_ESLINT_MIN } from '#config/eslint.js';

const repoRoot = process.cwd();
const errors = [];
const eslintVersions = [];

function semverParts(version) {
  const cleaned = String(version)
    .trim()
    .replace(SEMVER_PREFIX_REGEX, '')
    .replace(SEMVER_SUFFIX_REGEX, '');
  const segments = cleaned.split('.');
  return {
    major: Number(segments[0] ?? '0'),
    minor: Number(segments[1] ?? '0'),
    patch: Number(segments[2] ?? '0'),
  };
}

function compareSemver(left, right) {
  const leftParts = semverParts(left);
  const rightParts = semverParts(right);
  for (const component of ['major', 'minor', 'patch']) {
    if (leftParts[component] !== rightParts[component]) {
      return leftParts[component] > rightParts[component] ? 1 : -1;
    }
  }
  return 0;
}

for (const packageFile of PACKAGE_JSON_DEFAULT_FILES) {
  const absolutePath = path.join(repoRoot, packageFile);
  const pkg = JSON.parse(fs.readFileSync(absolutePath, 'utf8'));
  const deps = {
    ...pkg.dependencies,
    ...pkg.devDependencies,
    ...pkg.peerDependencies,
    ...pkg.optionalDependencies,
  };
  const eslintVersion = deps.eslint;
  const unicornVersion = deps['eslint-plugin-unicorn'];

  if (eslintVersion) {
    eslintVersions.push({ packageFile, version: eslintVersion });
    if (compareSemver(eslintVersion, UNICORN_ESLINT_MIN) < 0) {
      errors.push(
        `${packageFile}: eslint ${eslintVersion} is below required ${UNICORN_ESLINT_MIN}`,
      );
    }
  }

  if (unicornVersion && eslintVersion && semverParts(unicornVersion).major >= 63) {
    if (compareSemver(eslintVersion, UNICORN_ESLINT_MIN) < 0) {
      errors.push(
        `${packageFile}: eslint-plugin-unicorn ${unicornVersion} requires eslint >= ${UNICORN_ESLINT_MIN}`,
      );
    }
  }
}

const distinctVersionSet = new Set(eslintVersions.map((entry) => entry.version));
if (distinctVersionSet.size > 1) {
  errors.push(
    `ESLint versions are not aligned across package manifests: ${[...distinctVersionSet].join(', ')}`,
  );
}

if (errors.length > 0) {
  console.error('ESLint version policy failed:');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('ESLint version policy passed.');
