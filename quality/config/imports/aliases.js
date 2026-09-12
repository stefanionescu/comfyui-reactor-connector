export const DEFAULT_SCOPE = ['web', 'scripts/frontend.mjs', 'quality'];
export const PREFIXED_FILES_SCOPE = ['web', 'scripts', 'quality', '.githooks', '.mise/tasks'];
export const ALIAS_ROOTS = [
  { segment: 'quality/config', aliasPrefix: '#config/' },
  { segment: 'quality/web', aliasPrefix: '#web/' },
  { segment: 'quality/shared', aliasPrefix: '#shared/' },
  { segment: 'quality/repository', aliasPrefix: '#repository/' },
  { segment: 'web', aliasPrefix: '#web/' },
];
export const INTERNAL_PREFIXES = ['./', '../', '#config/', '#web/', '#shared/', '#repository/'];
