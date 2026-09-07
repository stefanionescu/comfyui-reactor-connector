export const UNICORN_ESLINT_MIN = '9.38.0';
export const SEMVER_PREFIX_REGEX = /^[^0-9]*/u;
export const SEMVER_SUFFIX_REGEX = /[^0-9.].*$/u;

export const INDEX_IMPORT_MESSAGE = 'Import the owning leaf module instead of an index barrel.';
export const INDEX_IMPORT_ALLOWLIST = [];
export const INDEX_IMPORT_PATTERNS = [/^\.{1,2}\/index\.js$/u];

export const ESLINT_NODE_GLOBALS = {
  AbortSignal: 'readonly',
  Buffer: 'readonly',
  URL: 'readonly',
  clearInterval: 'readonly',
  clearTimeout: 'readonly',
  console: 'readonly',
  fetch: 'readonly',
  performance: 'readonly',
  process: 'readonly',
  setInterval: 'readonly',
  setTimeout: 'readonly',
};
export const ESLINT_BROWSER_GLOBALS = {
  CustomEvent: 'readonly',
  HTMLDialogElement: 'readonly',
  HTMLElement: 'readonly',
  clearInterval: 'readonly',
  clearTimeout: 'readonly',
  console: 'readonly',
  document: 'readonly',
  localStorage: 'readonly',
  navigator: 'readonly',
  setInterval: 'readonly',
  setTimeout: 'readonly',
  sessionStorage: 'readonly',
  window: 'readonly',
};
export const ESLINT_COMMONJS_GLOBALS = {
  ...ESLINT_NODE_GLOBALS,
  __dirname: 'readonly',
  __filename: 'readonly',
  require: 'readonly',
  module: 'readonly',
  exports: 'readonly',
};
