export const PACKAGE_SCOPES = ['frontend'];
export const VALID_SCOPES = ['all', ...PACKAGE_SCOPES, 'hooks', 'quality', 'mise'];
export const VALID_SCOPE_USAGE = VALID_SCOPES.join('|');

export const SCOPE_PREFIXES = {
  all: '',
  frontend: 'web/',
  hooks: '.githooks/',
  quality: 'quality/',
  mise: '.mise/',
};
