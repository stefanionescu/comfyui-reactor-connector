export const LINK_ALIASES = [
  ['web/', 'extensions/reactor-inc'],
  ['web/', 'extensions/comfyui-reactor-connector'],
];

export const LINK_TEMPLATES = [];

export const LINK_MODES = ['--local', '--external'];
export const LINK_USAGE = 'Usage: bun quality/web/links/check.mjs [--local|--external]';
export const LINK_OPTIONS = {
  markdown: true,
  recurse: false,
  checkCss: true,
  checkFragments: true,
  timeout: 15000,
  concurrency: 10,
  redirects: 'allow',
  requireHttps: 'error',
};
