import { posix } from 'node:path';
import { normalizePath } from '#shared/eslint/plugin/path-policy/normalization.js';

/**
 * Determines whether the given path points to an `index` module.
 *
 * @param filename The file path to inspect.
 * @returns `true` when the file is an `index` entry file; otherwise, `false`.
 */
export const isIndexFile = (filename) => {
  const filenameOnly = posix.basename(normalizePath(filename));
  return ['index.ts', 'index.tsx', 'index.js', 'index.jsx'].includes(filenameOnly);
};
