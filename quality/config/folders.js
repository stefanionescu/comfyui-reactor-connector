export const DIRECTORY_IGNORE_PATHS = ['node_modules', 'dist', '.artifacts', '.venv', '.git'];

export const SINGLE_FILE_FOLDER_ALLOWLIST = [];
export const PREFIX_COLLISION_ALLOWLIST = [];

export const STALE_TOOLING_PATHS = [
  'reactor_comfy/',
  'frontend/catalog.ts',
  'frontend/extension.ts',
  'quality/frontend-build.mjs',
  'scripts/node_docs.py',
  'scripts/help_pages.py',
  'scripts/workflow_definitions.py',
  'biome.json',
  'CHANGELOG.md',
];
export const STALE_SECURITY_PATHS = [];
export const STALE_PATH_TEXT_ROOTS = [
  'package.json',
  'pyproject.toml',
  '__init__.py',
  '.githooks',
  '.mise',
  'README.md',
  'ADVANCED.md',
  'src',
  'web',
  'scripts',
  'quality',
  'rules',
  'locales',
  'workflows',
];
export const STALE_TEXT_EXEMPTS = ['quality/config/folders.js'];
export const DISALLOWED_RUNTIME_FOLDERS = ['bash', 'javascript'];
