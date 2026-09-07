export const QUALITY_CONFIG_FORBIDDEN_PATTERNS = [
  { pattern: /^#!/u, message: 'config files must not be executable entrypoints' },
  {
    pattern: /\bnode:fs\b|\bfrom\s+['"]fs['"]|\brequire\(['"]fs['"]\)/u,
    message: 'config files must not import fs',
  },
  {
    pattern: /\bnode:child_process\b|\bchild_process\b/u,
    message: 'config files must not import child_process',
  },
  { pattern: /\bprocess(?:\.|\[)/u, message: 'config files must not read process state' },
  {
    pattern: /\bimport\.meta\.url\b|\bfileURLToPath\b/u,
    message: 'config files must not derive runtime paths',
  },
  {
    pattern: /\b(?:exec|execFile|spawn|spawnSync)\b/u,
    message: 'config files must not execute commands',
  },
  {
    pattern: /\bfunct\x69on\b|=>|\bclass\b/u,
    message: 'config files must not define executable logic',
  },
  {
    pattern: /\b(?:if|for|while|switch|try|catch)\s*[({]/u,
    message: 'config files must not contain control flow',
  },
];

export const SHELL_CONFIG_GUARDS = [
  {
    pattern: /^\s*(?:source|\.)\s+/mu,
    message: 'shell config files must not source other scripts',
  },
  {
    pattern: /^\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\)\s*\{/mu,
    message: 'shell config files must not define functions',
  },
  {
    pattern: /^\s*(?:if|for|while|case)\b/mu,
    message: 'shell config files must not contain control flow',
  },
  {
    pattern: /^\s*funct\x69on\s+/mu,
    message: 'shell config files must not define functions',
  },
  { pattern: /\$\(/u, message: 'shell config files must not run command substitutions' },
];
