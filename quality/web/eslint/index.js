import jsdoc from 'eslint-plugin-jsdoc';
import nodePlugin from 'eslint-plugin-n';
import sonarjs from 'eslint-plugin-sonarjs';
import unicorn from 'eslint-plugin-unicorn';
import security from 'eslint-plugin-security';
import tsParser from '@typescript-eslint/parser';
import { NODE_VERSION } from '#config/runtime.js';
import prettierConfig from 'eslint-config-prettier';
import sharedPolicy from '#shared/eslint/policy.mjs';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import { rules as localRules } from '#shared/eslint/plugin/index.js';
import eslintComments from '@eslint-community/eslint-plugin-eslint-comments';

import {
  ESLINT_BROWSER_GLOBALS,
  ESLINT_COMMONJS_GLOBALS,
  ESLINT_NODE_GLOBALS,
} from '#config/eslint.js';
import {
  BARREL_REEXPORTS_MAX,
  COGNITIVE_COMPLEXITY_THRESHOLD,
  IDENTICAL_FUNCTIONS_THRESHOLD,
  MAX_FILE_LINES,
  MAX_FUNCTION_LINES,
  MAX_TRIVIAL_FUNCTION_STATEMENTS,
  PREFIXED_FILES_THRESHOLD,
} from '#config/limits.js';

const ignores = [
  '**/node_modules/**',
  '.artifacts/**',
  'dist/**',
  'web/dist/**',
  '**/.venv/**',
  '**/.git/**',
];

const nodeScriptFiles = ['scripts/**/*.mjs'];
const browserFiles = ['web/**/*.ts'];
const qualityModuleFiles = ['quality/**/*.mjs', 'quality/**/*.js'];
const qualityCommonjsFiles = ['quality/**/*.cjs'];

const plugins = {
  '@eslint-community/eslint-comments': eslintComments,
  jsdoc,
  local: { rules: localRules },
  n: nodePlugin,
  security,
  sonarjs,
  unicorn,
};

const eslintNodeSettings = {
  node: {
    version: NODE_VERSION,
  },
};
const eslintNodeRules = {
  'n/no-deprecated-api': 'error',
  'n/no-process-exit': 'error',
  'n/no-unsupported-features/node-builtins': [
    'error',
    { version: NODE_VERSION, allowExperimental: true },
  ],
  'n/no-unsupported-features/es-builtins': ['error', { version: NODE_VERSION }],
  'n/no-unsupported-features/es-syntax': 'off',
  'n/prefer-global/buffer': ['error', 'always'],
  'n/prefer-global/console': ['error', 'always'],
  'n/prefer-global/process': ['error', 'always'],
  'n/prefer-global/url': ['error', 'always'],
  'n/prefer-global/url-search-params': ['error', 'always'],
  'n/prefer-promises/dns': 'error',
  'n/prefer-promises/fs': 'error',
  'n/no-sync': 'off',
  'n/no-callback-literal': 'error',
  'n/no-new-require': 'error',
  'n/no-path-concat': 'error',
  'n/no-missing-import': 'off',
  'n/no-missing-require': 'off',
  'n/no-unpublished-import': 'off',
  'n/no-unpublished-require': 'off',
  'n/no-extraneous-import': 'off',
  'n/no-extraneous-require': 'off',
};
const eslintBaseRules = {
  'no-useless-constructor': 'error',
  'no-useless-return': 'error',
  'no-useless-call': 'error',
  'no-useless-rename': 'error',
  'max-nested-callbacks': ['error', 3],
};
const eslintSpacingRules = {
  'padding-line-between-statements': [
    'error',
    { blankLine: 'always', prev: ['function', 'class'], next: ['function', 'class'] },
  ],
  'lines-between-class-members': ['error', 'always'],
};
const eslintScriptJsRules = {
  'no-unused-vars': [
    'error',
    {
      args: 'all',
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
      destructuredArrayIgnorePattern: '^_',
    },
  ],
};
const eslintCommentsRules = {
  '@eslint-community/eslint-comments/require-description': 'error',
};
const eslintJsdocRules = {
  'jsdoc/require-jsdoc': [
    'error',
    {
      publicOnly: true,
      require: {
        FunctionDeclaration: true,
        ArrowFunctionExpression: true,
        FunctionExpression: true,
        MethodDefinition: true,
      },
    },
  ],
  'jsdoc/require-description': 'error',
  'jsdoc/require-param': 'error',
  'jsdoc/require-param-description': 'error',
  'jsdoc/require-param-name': 'error',
  'jsdoc/require-param-type': 'off',
  'jsdoc/require-returns': 'error',
  'jsdoc/require-returns-description': 'error',
  'jsdoc/require-returns-type': 'off',
  'jsdoc/check-param-names': 'error',
  'jsdoc/check-tag-names': 'error',
  'jsdoc/check-types': 'off',
  'jsdoc/no-undefined-types': 'off',
  'jsdoc/valid-types': 'off',
};
const eslintSecurityRules = {
  'security/detect-buffer-noassert': 'error',
  'security/detect-child-process': 'error',
  'security/detect-disable-mustache-escape': 'error',
  'security/detect-eval-with-expression': 'error',
  'security/detect-new-buffer': 'error',
  'security/detect-no-csrf-before-method-override': 'error',
  'security/detect-non-literal-regexp': 'error',
  'security/detect-non-literal-require': 'error',
  'security/detect-possible-timing-attacks': 'error',
  'security/detect-pseudoRandomBytes': 'error',
  'security/detect-unsafe-regex': 'error',
  'security/detect-object-injection': 'off',
  'security/detect-non-literal-fs-filename': 'off',
};
const eslintSonarRules = {
  'sonarjs/no-all-duplicated-branches': 'error',
  'sonarjs/no-duplicated-branches': 'error',
  'sonarjs/no-identical-conditions': 'error',
  'sonarjs/no-identical-expressions': 'error',
  'sonarjs/no-element-overwrite': 'error',
  'sonarjs/no-empty-collection': 'error',
  'sonarjs/no-extra-arguments': 'error',
  'sonarjs/no-use-of-empty-return-value': 'error',
  'sonarjs/non-existent-operator': 'error',
  'sonarjs/no-gratuitous-expressions': 'error',
  'sonarjs/no-invariant-returns': 'error',
  'sonarjs/for-loop-increment-sign': 'error',
  'sonarjs/no-useless-increment': 'error',
  'sonarjs/no-unthrown-error': 'error',
  'sonarjs/cognitive-complexity': ['error', COGNITIVE_COMPLEXITY_THRESHOLD],
  'sonarjs/no-collapsible-if': 'error',
  'sonarjs/no-nested-switch': 'error',
  'sonarjs/no-nested-template-literals': 'error',
  'sonarjs/no-redundant-boolean': 'error',
  'sonarjs/no-redundant-jump': 'error',
  'sonarjs/no-same-line-conditional': 'error',
  'sonarjs/no-small-switch': 'error',
  'sonarjs/no-unused-collection': 'error',
  'sonarjs/no-useless-catch': 'error',
  'sonarjs/prefer-single-boolean-return': 'error',
  'sonarjs/prefer-while': 'error',
  'sonarjs/prefer-object-literal': 'error',
  'sonarjs/no-identical-functions': ['error', IDENTICAL_FUNCTIONS_THRESHOLD],
  'sonarjs/no-nested-conditional': 'error',
  'sonarjs/no-inverted-boolean-check': 'error',
  'sonarjs/no-nested-functions': 'error',
  'sonarjs/no-parameter-reassignment': 'error',
  'sonarjs/no-commented-code': 'error',
  'sonarjs/no-dead-store': 'error',
  'sonarjs/prefer-immediate-return': 'error',
  'sonarjs/updated-loop-counter': 'error',
  'sonarjs/no-equals-in-for-termination': 'error',
  'sonarjs/no-redundant-assignments': 'error',
};
const eslintUnicornRules = {
  'unicorn/prefer-node-protocol': 'error',
  'unicorn/no-useless-spread': 'error',
  'unicorn/no-useless-promise-resolve-reject': 'error',
  'unicorn/prefer-array-find': 'error',
  'unicorn/prefer-array-flat': 'error',
  'unicorn/prefer-array-flat-map': 'error',
  'unicorn/prefer-at': 'error',
  'unicorn/prefer-includes': 'error',
  'unicorn/prefer-number-properties': 'error',
  'unicorn/prefer-string-replace-all': 'error',
  'unicorn/prefer-string-slice': 'error',
  'unicorn/prefer-string-starts-ends-with': 'error',
  'unicorn/prefer-ternary': ['error', 'only-single-line'],
  'unicorn/no-typeof-undefined': 'error',
  'unicorn/no-lonely-if': 'error',
  'unicorn/no-array-for-each': 'error',
};
const eslintSourceLocalRules = {
  'max-lines': [
    'error',
    {
      max: MAX_FILE_LINES,
      skipBlankLines: true,
      skipComments: true,
    },
  ],
  'max-lines-per-function': [
    'error',
    {
      max: MAX_FUNCTION_LINES,
      skipBlankLines: true,
      skipComments: true,
      IIFEs: true,
    },
  ],
  'local/no-call-through': ['error', { allow: [] }],
  'local/no-duplicate-barrel-exports': 'error',
  'local/no-export-only-files': 'error',
  'local/no-trivial-functions': ['error', { maxStatements: MAX_TRIVIAL_FUNCTION_STATEMENTS }],
  'local/no-prefix-collisions': [
    'error',
    {
      threshold: PREFIXED_FILES_THRESHOLD,
      scope: ['web', 'scripts', 'quality'],
    },
  ],
  'local/max-barrel-reexports': ['error', { max: BARREL_REEXPORTS_MAX }],
  'local/no-reexports-outside-index': 'error',
  'local/no-single-file-folders': [
    'error',
    {
      extensions: ['.js', '.cjs', '.mjs', '.ts'],
      ignorePaths: ['node_modules', 'dist', '.artifacts'],
    },
  ],
  'local/header-comments-before-imports': ['error', { supportRequire: true }],
  'local/no-imports-after-statements': ['error', { supportRequire: true }],
  'local/import-layout': ['error', { supportRequire: true }],
  'local/import-path-style': ['error', { style: 'js' }],
  'local/no-cross-folder-imports': 'error',
  'local/newline-after-imports': ['error', { supportRequire: true }],
};
const eslintPracticalUnusedVarsRule = [
  'error',
  {
    args: 'all',
    argsIgnorePattern: '^_',
    caughtErrors: 'all',
    caughtErrorsIgnorePattern: '^_',
    destructuredArrayIgnorePattern: '^_',
    varsIgnorePattern: '^_',
  },
];
const eslintQualityTrivialFunctionRule = [
  'error',
  { maxStatements: MAX_TRIVIAL_FUNCTION_STATEMENTS },
];

const sourceRules = {
  ...eslintSourceLocalRules,
  ...eslintCommentsRules,
  ...eslintScriptJsRules,
  ...eslintSonarRules,
  ...eslintSecurityRules,
  ...eslintUnicornRules,
  ...eslintBaseRules,
  ...eslintJsdocRules,
};

const nodeSourceRules = {
  ...eslintNodeRules,
  ...sourceRules,
};

const boundaryOverrides = [
  {
    files: browserFiles,
    rules: {
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['node:*', '#config/**', '#shared/**', '#repository/**', '**/quality/**'],
              message: 'ComfyUI browser code must not import build or quality tools.',
            },
          ],
        },
      ],
    },
  },
];

const qualityToolingOverrides = {
  files: [...qualityModuleFiles, ...qualityCommonjsFiles],
  rules: {
    'local/no-trivial-functions': eslintQualityTrivialFunctionRule,
    'max-lines': 'off',
    'max-lines-per-function': 'off',
    'n/no-process-exit': 'off',
    'sonarjs/no-collapsible-if': 'off',
    'sonarjs/no-identical-functions': 'off',
    'sonarjs/no-duplicated-branches': 'off',
    'sonarjs/no-nested-conditional': 'off',
    'sonarjs/prefer-single-boolean-return': 'off',
    'sonarjs/prefer-immediate-return': 'off',
    'unicorn/no-lonely-if': 'off',
    'unicorn/no-useless-spread': 'off',
    'unicorn/prefer-array-find': 'off',
  },
};

export default [
  { ignores },
  {
    settings: eslintNodeSettings,
  },
  ...sharedPolicy,
  {
    files: [...nodeScriptFiles, ...qualityModuleFiles],
    plugins,
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: ESLINT_NODE_GLOBALS,
    },
    rules: nodeSourceRules,
  },
  {
    files: browserFiles,
    plugins: { ...plugins, '@typescript-eslint': tsPlugin },
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: ESLINT_BROWSER_GLOBALS,
    },
    rules: {
      ...sourceRules,
      ...tsPlugin.configs['eslint-recommended'].overrides[0].rules,
      ...tsPlugin.configs.recommended.rules,
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': eslintPracticalUnusedVarsRule,
      'local/import-path-style': ['error', { style: 'ts' }],
    },
  },
  {
    files: qualityCommonjsFiles,
    plugins,
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'commonjs',
      globals: ESLINT_COMMONJS_GLOBALS,
    },
    rules: nodeSourceRules,
  },
  qualityToolingOverrides,
  ...boundaryOverrides,
  {
    files: ['web/extension.ts', 'web/help/command.ts'],
    rules: {
      // ComfyUI serves these modules outside the connector's bundled directory.
      'local/import-path-style': [
        'error',
        {
          style: 'ts',
          externalSources: ['../../scripts/app.js', '../../scripts/api.js'],
        },
      ],
      'local/no-cross-folder-imports': [
        'error',
        {
          externalSources: ['../../scripts/app.js', '../../scripts/api.js'],
        },
      ],
    },
  },
  prettierConfig,
  { rules: eslintSpacingRules },
];
