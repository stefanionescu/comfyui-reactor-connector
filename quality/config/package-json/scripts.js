export const PACKAGE_SCRIPT_CD_REGEX = /^cd\s+([^;&|]+)$/u;
export const BUN_RUN_SCRIPT_REGEX = /\bbun\s+run\s+([A-Za-z0-9:_-]+)/gu;
export const MISE_RUN_SCRIPT_REGEX = /\bmise\s+run\s+([A-Za-z0-9:_-]+)/u;
export const SCRIPT_SECTION_PREFIX = '---';
export const ROOT_ALLOWED_SCRIPT_COMMANDS = {
  build: 'bun scripts/frontend.mjs',
  'check:build': 'bun scripts/frontend.mjs --check',
  typecheck: 'tsc --noEmit',
  lint: 'eslint --config quality/web/eslint/index.js web scripts/frontend.mjs quality',
  format: 'mise run format',
};
