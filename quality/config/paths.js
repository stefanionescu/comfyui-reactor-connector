export const DEFAULT_SCOPE = ['config', 'web', 'scripts/frontend.mjs', 'quality'];
export const PREFIXED_FILES_SCOPE = [
  'config',
  'web',
  'scripts',
  'quality',
  '.githooks',
  '.mise/tasks',
];
export const ALIAS_ROOTS = [
  { segment: 'quality/config', aliasPrefix: '#config/' },
  { segment: 'quality/web', aliasPrefix: '#web/' },
  { segment: 'quality/shared', aliasPrefix: '#shared/' },
  { segment: 'quality/repository', aliasPrefix: '#repository/' },
  { segment: 'web', aliasPrefix: '#web/' },
  { segment: 'config', aliasPrefix: '#config/' },
];
export const INTERNAL_PREFIXES = ['./', '../', '#config/', '#web/', '#shared/', '#repository/'];

export const NAMING_POLICY_PATH = 'quality/config/naming/javascript.json';
