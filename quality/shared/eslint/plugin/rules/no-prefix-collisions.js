import path from 'node:path';
import { PREFIXED_FILES_SCOPE } from '#config/paths.js';
import { DIRECTORY_IGNORE_PATHS } from '#config/folders.js';
import { PREFIXED_FILES_THRESHOLD } from '#config/limits.js';
import { isIndexFile } from '#shared/eslint/plugin/path-policy/index-file.js';
import { analyzeDirectory, getPrefix } from '#repository/integrity/directory-prefixes.js';

import {
  normalizeFilename,
  normalizePath,
} from '#shared/eslint/plugin/path-policy/normalization.js';

export const noPrefixCollisions = {
  meta: {
    type: 'problem',
    docs: {
      description:
        'Disallow repeated filename or directory-name prefixes in the same folder; group them in a subfolder instead.',
    },
    schema: [
      {
        type: 'object',
        properties: {
          threshold: { type: 'number', minimum: 2 },
          scope: { type: 'array', items: { type: 'string' } },
        },
        additionalProperties: false,
      },
    ],
  },
  create(context) {
    const filename = context.getFilename?.() ?? '';
    const normalized = normalizePath(normalizeFilename(filename));
    if (!normalized || normalized === '<input>') {
      return {};
    }

    const options = context.options?.[0] ?? {};
    const scope =
      Array.isArray(options.scope) && options.scope.length > 0
        ? options.scope
        : PREFIXED_FILES_SCOPE;
    const threshold =
      typeof options.threshold === 'number' && options.threshold >= PREFIXED_FILES_THRESHOLD
        ? options.threshold
        : PREFIXED_FILES_THRESHOLD;

    const inScope = scope.some((segment) => normalized.includes(`/${segment}/`));
    if (!inScope) {
      return {};
    }

    const fileName = path.posix.basename(normalized);
    if (isIndexFile(fileName)) {
      return {};
    }

    const fileStem = fileName.replace(/\.[^.]+$/, '');
    const prefix = getPrefix(fileStem);
    if (!prefix) {
      return {};
    }

    const dirPath = path.dirname(normalized);

    return {
      Program(node) {
        const { prefixMap } = analyzeDirectory(dirPath, {
          ignorePaths: DIRECTORY_IGNORE_PATHS,
          skipIndexFiles: true,
        });
        const peers = prefixMap.get(prefix) ?? [];
        if (peers.length >= threshold) {
          const hasFiles = peers.some((p) => p.type === 'file');
          const hasDirs = peers.some((p) => p.type === 'dir');
          const names = peers.map((p) => (p.type === 'dir' ? `${p.name}/` : p.name)).join(', ');

          let message;
          if (hasFiles && hasDirs) {
            message = `Entries in this folder share the "${prefix}" stem/prefix (${names}). Resolve the collision by renaming or reorganizing.`;
          } else if (hasDirs) {
            message = `Directories in this folder share the "${prefix}" prefix (${names}). Resolve the collision by renaming or reorganizing.`;
          } else {
            message = `Files in this folder share the "${prefix}" prefix (${peers.length} files). Group them in a subfolder and rename to remove the prefix.`;
          }

          context.report({ node, message });
        }
      },
    };
  },
};
