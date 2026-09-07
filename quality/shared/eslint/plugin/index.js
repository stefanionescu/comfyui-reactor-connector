import { importLayout } from '#shared/eslint/plugin/rules/import-layout.js';
import { noCallThrough } from '#shared/eslint/plugin/rules/no-call-through.js';
import { noIndexImports } from '#shared/eslint/plugin/rules/no-index-imports.js';
import { importPathStyle } from '#shared/eslint/plugin/rules/import-path-style.js';
import { noExportOnlyFiles } from '#shared/eslint/plugin/rules/no-export-only-files.js';
import { maxBarrelReexports } from '#shared/eslint/plugin/rules/max-barrel-reexports.js';
import { noPrefixCollisions } from '#shared/eslint/plugin/rules/no-prefix-collisions.js';
import { noTrivialFunctions } from '#shared/eslint/plugin/rules/no-trivial-functions.js';
import { newlineAfterImports } from '#shared/eslint/plugin/rules/newline-after-imports.js';
import { noSingleFileFolders } from '#shared/eslint/plugin/rules/no-single-file-folders.js';
import { noCrossFolderImports } from '#shared/eslint/plugin/rules/no-cross-folder-imports.js';
import { noReexportsOutsideIndex } from '#shared/eslint/plugin/rules/no-reexports-outside-index.js';
import { noDuplicateBarrelExports } from '#shared/eslint/plugin/rules/no-duplicate-barrel-exports.js';
import { noExportedAliasConstants } from '#shared/eslint/plugin/rules/no-exported-alias-constants.js';
import { noImportsAfterStatements } from '#shared/eslint/plugin/rules/no-imports-after-statements.js';
import { headerCommentsBeforeImports } from '#shared/eslint/plugin/rules/header-comments-before-imports.js';

export const rules = {
  'header-comments-before-imports': headerCommentsBeforeImports,
  'import-layout': importLayout,
  'import-path-style': importPathStyle,
  'max-barrel-reexports': maxBarrelReexports,
  'newline-after-imports': newlineAfterImports,
  'no-call-through': noCallThrough,
  'no-cross-folder-imports': noCrossFolderImports,
  'no-duplicate-barrel-exports': noDuplicateBarrelExports,
  'no-export-only-files': noExportOnlyFiles,
  'no-exported-alias-constants': noExportedAliasConstants,
  'no-index-imports': noIndexImports,
  'no-imports-after-statements': noImportsAfterStatements,
  'no-prefix-collisions': noPrefixCollisions,
  'no-reexports-outside-index': noReexportsOutsideIndex,
  'no-single-file-folders': noSingleFileFolders,
  'no-trivial-functions': noTrivialFunctions,
};
