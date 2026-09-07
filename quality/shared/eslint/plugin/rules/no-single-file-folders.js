import path from 'node:path';
import { CODE_EXTENSIONS } from '#config/files.js';
import { DIRECTORY_IGNORE_PATHS } from '#config/folders.js';
import { readDirectory } from '#repository/integrity/directory-prefixes.js';

import {
  normalizeFilename,
  normalizePath,
} from '#shared/eslint/plugin/path-policy/normalization.js';

/**
 * Returns true if the path contains any of the ignored directory segments.
 * @param normalized - Absolute file path with forward slashes.
 * @param ignorePaths - Directory segments excluded by the configured policy.
 * @returns Whether the path contains a configured excluded directory.
 */
const isIgnoredPath = (normalized, ignorePaths) => {
  for (const segment of ignorePaths) {
    if (normalized.includes(`/${segment}/`)) {
      return true;
    }
  }
  return false;
};

/**
 * Returns true if the filename ends with one of the given code extensions (excluding .d.ts).
 * @param name - Filename to classify by its extension.
 * @param extensions - File suffixes that count as source files.
 * @returns Whether the filename is source code rather than a type declaration.
 */
const isCodeFile = (name, extensions) => {
  if (name.endsWith('.d.ts')) {
    return false;
  }
  return extensions.some((ext) => name.endsWith(ext));
};

const directoryCache = new Map();

/**
 * Returns the code file count and whether subdirectories exist for a directory (cached).
 * @param dirPath - Absolute directory path to inspect.
 * @param extensions - File suffixes that count as source files.
 * @returns Source file count and whether the directory has child directories.
 */
const getDirectorySummary = (dirPath, extensions) => {
  const cacheKey = `${dirPath}::${extensions.join(',')}`;
  if (directoryCache.has(cacheKey)) {
    return directoryCache.get(cacheKey);
  }

  let fileCount = 0;
  let hasSubdir = false;
  const entries = readDirectory(dirPath);
  for (const entry of entries) {
    if (entry.isDirectory()) {
      hasSubdir = true;
      continue;
    }
    if (entry.isFile() && isCodeFile(entry.name, extensions)) {
      fileCount += 1;
    }
  }

  const summary = { fileCount, hasSubdir };
  directoryCache.set(cacheKey, summary);
  return summary;
};

export const noSingleFileFolders = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow folders that contain only a single code file.',
    },
    schema: [
      {
        type: 'object',
        properties: {
          extensions: {
            type: 'array',
            items: { type: 'string' },
          },
          ignorePaths: {
            type: 'array',
            items: { type: 'string' },
          },
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
    const extensions =
      Array.isArray(options.extensions) && options.extensions.length > 0
        ? options.extensions
        : CODE_EXTENSIONS;
    const ignorePaths =
      Array.isArray(options.ignorePaths) && options.ignorePaths.length > 0
        ? options.ignorePaths
        : DIRECTORY_IGNORE_PATHS;

    if (isIgnoredPath(normalized, ignorePaths)) {
      return {};
    }

    const dirPath = path.dirname(normalized);

    return {
      Program(node) {
        const summary = getDirectorySummary(dirPath, extensions);
        if (summary.fileCount === 1 && !summary.hasSubdir) {
          context.report({
            node,
            message:
              'Avoid folders that contain only a single file. Flatten or regroup related code.',
          });
        }
      },
    };
  },
};
