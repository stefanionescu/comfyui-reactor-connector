export const PACKAGE_JSON_DEFAULT_FILES = ['package.json', 'quality/package.json'];

export const PACKAGE_JSON_DEPENDENCY_KEYS = [
  'dependencies',
  'devDependencies',
  'peerDependencies',
  'optionalDependencies',
  'overrides',
];

// A git dependency is exact only when it names a full commit hash.
export const PACKAGE_JSON_COMMIT_PATTERN = /^github:[\w.-]+\/[\w.-]+#[0-9a-f]{40}$/u;
