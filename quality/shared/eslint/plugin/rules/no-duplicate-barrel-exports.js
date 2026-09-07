import fs from 'node:fs';
import path from 'node:path';
import { visibleFiles } from '#shared/files.js';
import { EXPORT_FILE_EXTENSIONS } from '#config/files.js';
import { parse } from '@typescript-eslint/typescript-estree';
import { isIndexFile } from '#shared/eslint/plugin/path-policy/index-file.js';

import {
  normalizeFilename,
  normalizePath,
} from '#shared/eslint/plugin/path-policy/normalization.js';

const exportNameCache = new Map();
let publicModuleFiles;

/**
 * Resolves a relative import source to an absolute file path, trying direct matches and index files.
 * @param importerFile - Absolute path of the importing file.
 * @param source - Module path written in the import.
 * @returns The resolved file path, or null when the module cannot be found.
 */
const findModulePath = (importerFile, source) => {
  if (!source.startsWith('.')) {
    return null;
  }

  publicModuleFiles ??= new Set(
    visibleFiles(process.cwd()).map((file) => path.resolve(process.cwd(), file)),
  );
  const importerDir = path.dirname(importerFile);
  // reason: Candidates are read only after membership in the Git-visible regular-file set is checked.
  // bearer:disable javascript_lang_path_traversal
  const sourcePath = path.resolve(importerDir, source);

  const candidates = [
    sourcePath,
    ...EXPORT_FILE_EXTENSIONS.map((ext) => `${sourcePath}${ext}`),
    // reason: Candidates are read only after membership in the Git-visible regular-file set is checked.
    // bearer:disable javascript_lang_path_traversal
    ...EXPORT_FILE_EXTENSIONS.map((ext) => path.join(sourcePath, `index${ext}`)),
  ];
  for (const candidate of candidates) {
    if (publicModuleFiles.has(candidate)) return candidate;
  }

  return null;
};

/**
 * Recursively collects all exported names from a file, following `export *` re-exports.
 * @param filePath - Absolute path of the module whose exports are needed.
 * @param visited - Module paths already followed in this branch.
 * @returns Set of named exports, including reachable wildcard exports.
 */
const getExportForFile = (filePath, visited = new Set()) => {
  const normalizedFile = normalizePath(filePath);
  if (visited.has(normalizedFile)) {
    return new Set();
  }
  visited.add(normalizedFile);

  const cacheKey = `${normalizedFile}::${Array.from(visited).sort().join('|')}`;
  const cached = exportNameCache.get(cacheKey);
  if (cached) {
    return cached;
  }

  let content;
  try {
    content = fs.readFileSync(filePath, 'utf8');
  } catch {
    const empty = new Set();
    exportNameCache.set(cacheKey, empty);
    return empty;
  }

  const statements = parse(content, { jsx: /\.[jt]sx$/u.test(filePath) }).body;
  const names = new Set(statements.flatMap(exportedNames));
  const sources = statements
    .filter((statement) => statement.type === 'ExportAllDeclaration')
    .map((statement) => statement.source.value);
  for (const source of sources) {
    const resolved = findModulePath(filePath, source);
    if (!resolved) {
      continue;
    }
    const childNames = getExportForFile(resolved, new Set(visited));
    for (const name of childNames) {
      names.add(name);
    }
  }

  exportNameCache.set(cacheKey, names);
  return names;
};

function exportedNames(statement) {
  if (statement.type !== 'ExportNamedDeclaration') return [];
  return [
    ...collectDeclarationNames(statement.declaration),
    ...statement.specifiers.map((specifier) =>
      specifier.exported.type === 'Identifier' ? specifier.exported.name : specifier.exported.value,
    ),
  ];
}

/**
 * Records an export name, or reports a lint error if the name was already exported.
 * @param context - ESLint rule context used to report violations.
 * @param seen - Map from exported names to their first declaration.
 * @param node - Syntax-tree node to report.
 * @param name - Exported symbol name.
 */
const addNameReport = (context, seen, node, name) => {
  if (!name) {
    return;
  }
  const previous = seen.get(name);
  if (previous) {
    context.report({
      node,
      message: `Duplicate barrel export "${name}" detected. Use explicit aliases or remove conflicting re-exports.`,
    });
    return;
  }
  seen.set(name, node);
};

/**
 * Extracts declared names from an AST declaration node (function, class, variable, type, etc.).
 * @param declaration - Declaration node that may introduce exported names.
 * @returns Names introduced by the declaration, or an empty array.
 */
const collectDeclarationNames = (declaration) => {
  if (!declaration) {
    return [];
  }

  if (
    declaration.type === 'FunctionDeclaration' ||
    declaration.type === 'ClassDeclaration' ||
    declaration.type === 'TSTypeAliasDeclaration' ||
    declaration.type === 'TSInterfaceDeclaration' ||
    declaration.type === 'TSEnumDeclaration'
  ) {
    return declaration.id?.name ? [declaration.id.name] : [];
  }

  if (declaration.type !== 'VariableDeclaration') {
    return [];
  }

  return declaration.declarations
    .map((item) => (item.id.type === 'Identifier' ? item.id.name : null))
    .filter(Boolean);
};

/**
 * Processes an ExportNamedDeclaration, tracking each exported name and reporting duplicates.
 * @param context - ESLint rule context used to report violations.
 * @param seen - Map from exported names to their first declaration.
 * @param statement - Export declaration to inspect.
 */
const processNamedDeclaration = (context, seen, statement) => {
  for (const name of collectDeclarationNames(statement.declaration)) {
    addNameReport(context, seen, statement, name);
  }

  for (const specifier of statement.specifiers) {
    if (specifier.type !== 'ExportSpecifier') {
      continue;
    }
    const exportedName =
      specifier.exported.type === 'Identifier' ? specifier.exported.name : specifier.exported.value;
    addNameReport(context, seen, statement, exportedName);
  }
};

/**
 * Processes an ExportAllDeclaration by resolving the source module and checking for duplicate names.
 * @param context - ESLint rule context used to report violations.
 * @param seen - Map from exported names to their first declaration.
 * @param statement - Export declaration to inspect.
 * @param normalized - Absolute source path with forward slashes.
 */
const processAllDeclaration = (context, seen, statement, normalized) => {
  if (!statement.source || typeof statement.source.value !== 'string') {
    return;
  }

  const resolved = findModulePath(normalized, statement.source.value);
  if (!resolved) {
    return;
  }
  const names = getExportForFile(resolved);
  for (const name of names) {
    addNameReport(context, seen, statement, name);
  }
};

export const noDuplicateBarrelExports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow duplicate exported names within barrel index files.',
    },
    schema: [],
  },
  create(context) {
    const filename = normalizeFilename(context.getFilename?.() ?? '');
    if (!filename || filename === '<input>' || !isIndexFile(filename)) {
      return {};
    }

    const normalized = normalizePath(filename);

    return {
      Program(node) {
        const seen = new Map();

        for (const statement of node.body) {
          if (statement.type === 'ExportNamedDeclaration') {
            processNamedDeclaration(context, seen, statement);
          } else if (statement.type === 'ExportAllDeclaration') {
            processAllDeclaration(context, seen, statement, normalized);
          }
        }
      },
    };
  },
};
