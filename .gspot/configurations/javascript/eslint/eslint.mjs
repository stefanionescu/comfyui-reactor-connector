import { setLevelRules, mergePresetRules, addPlugins, setRuntime, setRootFolder, setBoundaryLookup, buildRuntimeMatcher, setRuleOptions } from "./functions.mjs";
import eslintJs from "@eslint/js";
import gspothqEslintPlugin from "@gspothq/eslint-plugin";
import eslintPluginUnicorn from "eslint-plugin-unicorn";
import eslintPluginImportX from "eslint-plugin-import-x";
import eslintPluginJsdoc from "eslint-plugin-jsdoc";
import eslintPluginN from "eslint-plugin-n";
import eslintPluginRegexp from "eslint-plugin-regexp";
import eslintPluginSecurity from "eslint-plugin-security";
import eslintPluginPerfectionist from "eslint-plugin-perfectionist";
import eslintPluginBoundaries from "eslint-plugin-boundaries";
import globals from "globals";
import eslintPluginPackageJson from "eslint-plugin-package-json";
import eslintConfigPrettier from "eslint-config-prettier";
import { defineConfig } from "eslint/config";
import typescriptBlocks from "../../typescript/eslint.mjs";
const maxLinesList = [
    "error",
    {
        "max": 300,
        "skipBlankLines": true,
        "skipComments": true
    }
];
const maxLinesPerFunctionList = [
    "error",
    {
        "max": 60,
        "skipBlankLines": true,
        "skipComments": true,
        "IIFEs": true
    }
];
const maxParamsList = [
    "error",
    7
];
const maxDepthList = [
    "error",
    3
];
const maxStatementsList = [
    "error",
    30
];
const complexityList = [
    "error",
    {
        "max": 8,
        "variant": "modified"
    }
];
const importBoundaryFolders = [
    "*/*"
];
const gspotImportBoundariesList = [
    "error",
    {
        "folders": importBoundaryFolders,
        "aliases": {
            "#web/*": "web/scripts/*"
        }
    }
];
const tryExtensionsList = [
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".mjs",
    ".mts",
    ".cjs",
    ".cts",
    ".json",
    ".node"
];
const nFileExtensionInImportList = [
    "error",
    "always"
];
const patternList = [
    "**/test/**",
    "**/tests/**",
    "**/__tests__/**",
    "**/*.test.*",
    "**/*.spec.*",
    "**/Tests/**"
];
const noneOfList = [
    "rule \"page",
    "rule \"settings-dialog",
    "rule \"live-controls",
    "rule \"extension",
    "rule \"config",
    "rule \"state",
    "rule \"basics",
    "rule \"records",
    "rule \"settings",
    "rule \"routing",
    "rule \"execution",
    "rule \"media",
    "rule \"live",
    "rule \"runtime",
    "rule \"comfy",
    "rule \"nodes",
    "rule \"entry",
    "rule \"scripts"
];
const runtimeDeclarations = [
    {
        "scopePath": "",
        "runtime": "node",
        "includes": [
            "^(?:(?:(?!(?:^|\\/)\\.{1,2}(?:\\/|$))(?:(?:(?!(?:^|\\/)\\.{1,2}(?:\\/|$)).)*?)\\/)?(?!\\.{1,2}(?:\\/|$))(?=.)[^/]*?\\/?)$"
        ],
        "excludes": []
    },
    {
        "scopePath": "",
        "runtime": "commonjs",
        "includes": [
            "^(?:(?:^|\\/|(?:(?:(?!(?:^|\\/)\\.{1,2}(?:\\/|$)).)*?)\\/)(?!\\.{1,2}(?:\\/|$))(?=.)[^/]*?\\.(cjs|cts))$"
        ],
        "excludes": []
    },
    {
        "scopePath": "",
        "runtime": "browser",
        "includes": [
            "^(?:web\\/scripts(?:\\/(?!\\.{1,2}(?:\\/|$))(?:(?:(?!(?:^|\\/)\\.{1,2}(?:\\/|$)).)*?)|$))$"
        ],
        "excludes": []
    }
];
export default setRuleOptions(defineConfig([
    {
    "ignores": [
        "**/build/**",
        ".gspot/**",
        ".gspot-copies/**",
        ".editorconfig",
        ".github/workflows/gspot.yml",
        ".markdownlint.jsonc",
        ".prettierignore",
        ".stylelintrc.yml",
        "eslint.config.mjs",
        "prettier.config.mjs",
        "pyrightconfig.json",
        "ruff.toml",
        "web/extension.js",
        "web/extension.css",
        "example_workflows/*.json",
        "**/requirements.txt",
        "example_workflows/assets/*.png",
        "**/node_modules/**",
        "**/bower_components/**",
        "**/.venv/**",
        "**/venv/**",
        "**/__pycache__/**",
        "**/.pytest_cache/**",
        "**/.ruff_cache/**",
        "**/.mypy_cache/**",
        "**/coverage/**",
        "**/.env",
        "**/.env.*",
        "**/.dev.vars",
        "**/.dev.vars.*",
        "**/bun.lock",
        "**/uv.lock",
        "**/*.py[cod]",
        "dist/**",
        "**/.artifacts/**",
        "**/.import_linter_cache/**",
        "**/.mise.local.toml",
        "**/*.log",
        "**/.DS_Store"
    ]
},
    setLevelRules({"extends": [eslintJs["configs"]["recommended"]],
    "files": ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"]}, gspothqEslintPlugin, "all"),
    setLevelRules({"extends": [eslintPluginUnicorn["configs"]["recommended"]],
    "files": ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"]}, gspothqEslintPlugin, "all"),
    setRootFolder(setRuntime(addPlugins(setLevelRules(mergePresetRules({"linterOptions": {
        "reportUnusedDisableDirectives": "error"
    },
    "languageOptions": {
        "ecmaVersion": "latest"
    },
    "settings": {
        "import-x/ignore": [
            "[/\\\\]build[/\\\\]",
            "[/\\\\]\\.gspot[/\\\\]",
            "[/\\\\]\\.gspot-copies[/\\\\]",
            "[/\\\\]node_modules[/\\\\]",
            "[/\\\\]bower_components[/\\\\]",
            "[/\\\\]\\.venv[/\\\\]",
            "[/\\\\]venv[/\\\\]",
            "[/\\\\]__pycache__[/\\\\]",
            "[/\\\\]\\.pytest_cache[/\\\\]",
            "[/\\\\]\\.ruff_cache[/\\\\]",
            "[/\\\\]\\.mypy_cache[/\\\\]",
            "[/\\\\]coverage[/\\\\]",
            "[/\\\\]dist[/\\\\]",
            "[/\\\\]\\.artifacts[/\\\\]",
            "[/\\\\]\\.import_linter_cache[/\\\\]"
        ]
    },
    "rules": {
        "array-callback-return": "error",
        "block-scoped-var": "error",
        "no-const-assign": "error",
        "no-loop-func": "error",
        "no-labels": "error",
        "no-new": "error",
        "no-nested-ternary": "error",
        "default-case-last": "error",
        "no-void": "error",
        "no-constructor-return": "error",
        "no-new-func": "error",
        "no-promise-executor-return": "error",
        "no-return-assign": "error",
        "no-self-compare": "error",
        "no-template-curly-in-string": "error",
        "no-unmodified-loop-condition": "error",
        "no-unreachable-loop": "error",
        "no-var": "error",
        "no-empty-character-class": "off",
        "no-useless-constructor": "error",
        "no-useless-return": "error",
        "no-useless-call": "error",
        "no-useless-rename": "error",
        "no-duplicate-imports": "off",
        "eqeqeq": "error",
        "prefer-const": "error",
        "no-param-reassign": "error",
        "no-warning-comments": [
            "error",
            {
                "terms": [
                    "todo",
                    "fixme",
                    "xxx",
                    "hack"
                ],
                "location": "anywhere"
            }
        ],
        "perfectionist/sort-imports": [
            "error",
            {
                "type": "alphabetical",
                "ignoreCase": false,
                "groups": [
                    "builtin",
                    "external",
                    "internal",
                    [
                        "parent",
                        "sibling",
                        "index"
                    ],
                    "unknown"
                ],
                "newlinesBetween": 1,
                "useExperimentalDependencyDetection": false
            }
        ],
        "perfectionist/sort-named-imports": [
            "error",
            {
                "type": "alphabetical",
                "ignoreCase": false
            }
        ],
        "perfectionist/sort-exports": [
            "error",
            {
                "type": "line-length",
                "groups": [
                    "singleline-export",
                    "multiline-export"
                ],
                "newlinesBetween": 1,
                "ignoreCase": false
            }
        ],
        "perfectionist/sort-named-exports": [
            "error",
            {
                "type": "line-length",
                "ignoreCase": false
            }
        ],
        "unicorn/name-replacements": "off",
        "unicorn/filename-case": "off",
        "unicorn/no-null": "off",
        "unicorn/no-useless-undefined": "off",
        "unicorn/import-style": "off",
        "unicorn/prefer-export-from": "off",
        "unicorn/no-unnecessary-array-flat-map": "off",
        "unicorn/no-abusive-eslint-disable": "off",
        "unicorn/prefer-ternary": "off",
        "unicorn/prefer-await": "off",
        "unicorn/no-negated-array-predicate": "off",
        "unicorn/prefer-simple-condition-first": "off",
        "unicorn/prefer-combined-guards": "off",
        "unicorn/expiring-todo-comments": "off",
        "unicorn/consistent-boolean-name": [
            "error",
            {
                "checkFunctions": "never",
                "ignore": [
                    "^_",
                    "^(?:enabled|active|retryable)$"
                ],
                "prefixes": {
                    "are": false,
                    "have": false,
                    "should": false,
                    "was": false,
                    "were": false,
                    "does": false,
                    "did": false,
                    "will": false,
                    "requires": false
                }
            }
        ],
        "security/detect-disable-mustache-escape": "error",
        "security/detect-eval-with-expression": "off",
        "security/detect-new-buffer": "off",
        "security/detect-non-literal-regexp": "off",
        "security/detect-non-literal-require": "off",
        "security/detect-pseudoRandomBytes": "off",
        "import-x/no-dynamic-require": "error",
        "security/detect-unsafe-regex": "off",
        "security/detect-object-injection": "off",
        "security/detect-non-literal-fs-filename": "off",
        "security/detect-child-process": "error",
        "security/detect-possible-timing-attacks": "error",
        "jsdoc/require-param-name": "error",
        "jsdoc/check-param-names": [
            "error",
            {
                "checkDestructured": false,
                "disableMissingParamChecks": true
            }
        ],
        "jsdoc/check-tag-names": "error",
        "jsdoc/no-types": "off",
        "jsdoc/match-name": [
            "error",
            {
                "match": [
                    {
                        "tags": [
                            "param"
                        ],
                        "disallowName": "/^root\\d+$/",
                        "message": "Name the parameter for its role, such as options."
                    }
                ]
            }
        ],
        "jsdoc/informative-docs": "error",
        "jsdoc/tag-lines": [
            "error",
            "any",
            {
                "startLines": 1
            }
        ],
        "regexp/no-super-linear-backtracking": "error",
        "regexp/no-empty-alternative": "error",
        "regexp/no-empty-capturing-group": "error",
        "regexp/no-empty-character-class": "error",
        "regexp/no-empty-group": "error",
        "regexp/no-empty-lookarounds-assertion": "error",
        "regexp/no-useless-assertions": "error",
        "regexp/no-useless-backreference": "error",
        "regexp/no-useless-character-class": "error",
        "regexp/no-useless-dollar-replacements": "error",
        "regexp/no-useless-lazy": "error",
        "regexp/no-useless-quantifier": "error",
        "regexp/no-useless-range": "error",
        "regexp/no-lazy-ends": [
            "error",
            {
                "ignorePartial": false
            }
        ],
        "regexp/no-optional-assertion": "error",
        "regexp/no-invalid-regexp": "error",
        "regexp/no-misleading-capturing-group": "error",
        "regexp/no-contradiction-with-assertion": "error",
        "regexp/strict": "error",
        "regexp/no-super-linear-move": "error",
        "regexp/no-dupe-characters-character-class": "error",
        "regexp/prefer-character-class": [
            "error",
            {
                "minAlternatives": 2
            }
        ],
        "regexp/prefer-d": "error",
        "regexp/prefer-w": "error",
        "regexp/prefer-question-quantifier": "error",
        "regexp/prefer-star-quantifier": "error",
        "regexp/prefer-plus-quantifier": "error",
        "regexp/no-useless-two-nums-quantifier": "error",
        "regexp/no-zero-quantifier": "error",
        "regexp/match-any": "error",
        "regexp/prefer-result-array-groups": "error",
        "regexp/prefer-named-replacement": "error",
        "regexp/prefer-named-backreference": "error",
        "regexp/no-unused-capturing-group": "error",
        "import-x/export": "error",
        "import-x/no-self-import": "error",
        "import-x/no-useless-path-segments": "error",
        "import-x/no-empty-named-blocks": "error",
        "import-x/no-duplicates": "error",
        "import-x/no-mutable-exports": "error",
        "import-x/no-relative-packages": "error",
        "import-x/no-default-export": "error",
        "max-lines": maxLinesList,
        "max-lines-per-function": maxLinesPerFunctionList,
        "max-params": maxParamsList,
        "max-depth": maxDepthList,
        "max-statements": maxStatementsList,
        "max-nested-callbacks": maxDepthList,
        "complexity": complexityList,
        "gspot/no-identical-functions": [
            "error",
            {
                "minLines": 8
            }
        ],
        "gspot/import-boundaries": gspotImportBoundariesList,
        "import-x/first": "error",
        "import-x/newline-after-import": [
            "error",
            {
                "count": 1,
                "considerComments": true
            }
        ]
    },
    "files": ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"]}, gspothqEslintPlugin["configs"]["all"]), gspothqEslintPlugin, "all"), { "gspot": gspothqEslintPlugin, "import-x": eslintPluginImportX, "jsdoc": eslintPluginJsdoc, "n": eslintPluginN, "regexp": eslintPluginRegexp, "security": eslintPluginSecurity, "perfectionist": eslintPluginPerfectionist, "boundaries": eslintPluginBoundaries }), globals, "es2024", "module"), [
        [
            "settings",
            "gspot",
            "root"
        ],
        [
            "settings",
            "boundaries/root-path"
        ]
    ]),
    setLevelRules({"rules": {
        "no-implied-eval": "error",
        "no-throw-literal": "error",
        "no-unused-expressions": "error",
        "no-unused-vars": [
            "error",
            {
                "args": "all",
                "argsIgnorePattern": "^_",
                "varsIgnorePattern": "^_",
                "destructuredArrayIgnorePattern": "^_"
            }
        ],
        "jsdoc/require-param-type": "error",
        "jsdoc/require-returns-type": "error",
        "jsdoc/check-types": "error",
        "jsdoc/no-undefined-types": "error",
        "jsdoc/valid-types": "error"
    },
    "files": ["**/*.{js,mjs,cjs,jsx}"]}, gspothqEslintPlugin, "all"),
    setLevelRules({"settings": {
        "n": {
            "tryExtensions": tryExtensionsList,
            "typescriptExtensionMap": []
        }
    },
    "rules": {
        "n/file-extension-in-import": nFileExtensionInImportList
    },
    "files": [["**/*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"settings": {
        "n": {
            "tryExtensions": tryExtensionsList,
            "typescriptExtensionMap": []
        }
    },
    "rules": {
        "n/file-extension-in-import": nFileExtensionInImportList,
        "gspot/import-boundaries": gspotImportBoundariesList
    },
    "files": ["**/*.mjs", "**/*.cjs"]}, gspothqEslintPlugin, "all"),
    setBoundaryLookup(setLevelRules({"settings": {
        "boundaries/files": [
            {
                "category": "tests",
                "pattern": patternList,
                "stopMatching": true
            },
            {
                "category": "rule \"page",
                "pattern": [
                    "web/scripts/browser.ts",
                    "web/scripts/dom.ts",
                    "web/scripts/host.d.ts",
                    "web/scripts/http.ts",
                    "web/scripts/routes.ts",
                    "web/scripts/schema.ts",
                    "web/scripts/text.ts"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"settings-dialog",
                "pattern": [
                    "web/scripts/settings/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"live-controls",
                "pattern": [
                    "web/scripts/live/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"extension",
                "pattern": [
                    "web/scripts/extension.ts"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"config",
                "pattern": [
                    "src/config/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"state",
                "pattern": [
                    "src/state/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"basics",
                "pattern": [
                    "src/errors.py",
                    "src/paths.py",
                    "src/tasks.py"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"records",
                "pattern": [
                    "src/credentials.py",
                    "src/models.py",
                    "src/serialization.py",
                    "src/storage.py"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"settings",
                "pattern": [
                    "src/settings/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"routing",
                "pattern": [
                    "src/routing/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"execution",
                "pattern": [
                    "src/execution/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"media",
                "pattern": [
                    "src/media/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"live",
                "pattern": [
                    "src/live/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"runtime",
                "pattern": [
                    "src/runtime.py"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"comfy",
                "pattern": [
                    "src/comfy/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"nodes",
                "pattern": [
                    "src/nodes/**"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"entry",
                "pattern": [
                    "__init__.py",
                    "__main__.py",
                    "src/__init__.py",
                    "src/extension.py"
                ],
                "stopMatching": true
            },
            {
                "category": "rule \"scripts",
                "pattern": [
                    "scripts/**"
                ],
                "stopMatching": true
            },
            {
                "category": "other",
                "pattern": [
                    "**/*"
                ]
            }
        ],
        "boundaries/ignore": [],
        "boundaries/elements": [
            {
                "type": "other",
                "pattern": "**",
                "partialMatch": false
            }
        ],
        "boundaries/dependency-nodes": [
            "require",
            "dynamic-import"
        ],
        "boundaries/additional-dependency-nodes": [
            {
                "selector": "ImportDeclaration:not([importKind=type]):matches([specifiers.length=0], :has(ImportSpecifier:not([importKind=type]), ImportDefaultSpecifier, ImportNamespaceSpecifier)) > Literal",
                "kind": "value",
                "name": "import"
            },
            {
                "selector": "ImportDeclaration:matches([importKind=type], [specifiers.length>0]:not(:has(ImportSpecifier:not([importKind=type]), ImportDefaultSpecifier, ImportNamespaceSpecifier))) > Literal",
                "kind": "type",
                "name": "import"
            },
            {
                "selector": ":matches(ExportAllDeclaration:not([exportKind=type]), ExportNamedDeclaration:not([exportKind=type]):matches([specifiers.length=0], :has(ExportSpecifier:not([exportKind=type])))) > Literal",
                "kind": "value",
                "name": "export"
            },
            {
                "selector": ":matches(ExportAllDeclaration[exportKind=type], ExportNamedDeclaration:matches([exportKind=type], [specifiers.length>0]:not(:has(ExportSpecifier:not([exportKind=type]))))) > Literal",
                "kind": "type",
                "name": "export"
            }
        ]
    },
    "rules": {
        "boundaries/dependencies": [
            "error",
            {
                "default": "disallow",
                "policies": [
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"page"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"page\" may import only its own files, not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"page"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"page"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"settings-dialog"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"settings-dialog\" may import its own files and \"page\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"settings-dialog"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"settings-dialog",
                                            "rule \"page"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"live-controls"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"live-controls\" may import its own files and \"page\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"live-controls"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"live-controls",
                                            "rule \"page"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"extension"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"extension\" may import its own files and \"page\", \"settings-dialog\", \"live-controls\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"extension"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"extension",
                                            "rule \"page",
                                            "rule \"settings-dialog",
                                            "rule \"live-controls"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"config"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"config\" may import only its own files, not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"config"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"config"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"state"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"state\" may import only its own files, not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"state"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"state"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"basics"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"basics\" may import only its own files, not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"basics"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"basics"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"records"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"records\" may import its own files and \"config\", \"state\", \"basics\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"records"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"records",
                                            "rule \"config",
                                            "rule \"state",
                                            "rule \"basics"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"settings"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"settings\" may import its own files and \"config\", \"state\", \"basics\", \"records\", \"routing\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"settings"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"settings",
                                            "rule \"config",
                                            "rule \"state",
                                            "rule \"basics",
                                            "rule \"records",
                                            "rule \"routing"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"routing"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"routing\" may import its own files and \"config\", \"state\", \"basics\", \"records\", \"settings\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"routing"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"routing",
                                            "rule \"config",
                                            "rule \"state",
                                            "rule \"basics",
                                            "rule \"records",
                                            "rule \"settings"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"execution"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"execution\" may import its own files and \"config\", \"state\", \"basics\", \"records\", \"media\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"execution"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"execution",
                                            "rule \"config",
                                            "rule \"state",
                                            "rule \"basics",
                                            "rule \"records",
                                            "rule \"media"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"media"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"media\" may import its own files and \"config\", \"state\", \"basics\", \"records\", \"execution\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"media"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"media",
                                            "rule \"config",
                                            "rule \"state",
                                            "rule \"basics",
                                            "rule \"records",
                                            "rule \"execution"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"live"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"live\" may import its own files and \"config\", \"state\", \"basics\", \"records\", \"routing\", \"execution\", \"media\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"live"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"live",
                                            "rule \"config",
                                            "rule \"state",
                                            "rule \"basics",
                                            "rule \"records",
                                            "rule \"routing",
                                            "rule \"execution",
                                            "rule \"media"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"runtime"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"runtime\" may import its own files and \"config\", \"basics\", \"records\", \"settings\", \"live\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"runtime"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"runtime",
                                            "rule \"config",
                                            "rule \"basics",
                                            "rule \"records",
                                            "rule \"settings",
                                            "rule \"live"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"comfy"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"comfy\" may import its own files and \"config\", \"state\", \"basics\", \"records\", \"settings\", \"execution\", \"media\", \"live\", \"runtime\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"comfy"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"comfy",
                                            "rule \"config",
                                            "rule \"state",
                                            "rule \"basics",
                                            "rule \"records",
                                            "rule \"settings",
                                            "rule \"execution",
                                            "rule \"media",
                                            "rule \"live",
                                            "rule \"runtime"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"nodes"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"nodes\" may import its own files and \"config\", \"state\", \"basics\", \"settings\", \"execution\", \"media\", \"runtime\", \"comfy\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"nodes"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"nodes",
                                            "rule \"config",
                                            "rule \"state",
                                            "rule \"basics",
                                            "rule \"settings",
                                            "rule \"execution",
                                            "rule \"media",
                                            "rule \"runtime",
                                            "rule \"comfy"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"entry"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"entry\" may import its own files and \"media\", \"runtime\", \"comfy\", \"nodes\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"entry"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"entry",
                                            "rule \"media",
                                            "rule \"runtime",
                                            "rule \"comfy",
                                            "rule \"nodes"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"scripts"
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        },
                        "message": "Import rule \"scripts\" may import its own files and \"state\", \"records\", \"nodes\", \"entry\", not {{dependency.source}} from {{#each to.file.categories}}{{#if @last}}{{this}}{{/if}}{{/each}}\". Move the code, move that rule above this one, or list the rules it may import in can_import."
                    },
                    {
                        "from": {
                            "file": {
                                "categories": "rule \"scripts"
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "anyOf": [
                                            "rule \"scripts",
                                            "rule \"state",
                                            "rule \"records",
                                            "rule \"nodes",
                                            "rule \"entry"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "isUnknown": true
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        }
                    },
                    {
                        "allow": {
                            "to": {
                                "file": {
                                    "isUnknown": true
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "path": patternList
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        }
                    },
                    {
                        "allow": {
                            "to": {
                                "file": {
                                    "path": patternList
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": {
                                    "noneOf": noneOfList
                                }
                            }
                        },
                        "allow": {
                            "to": {
                                "file": {
                                    "path": "**/*"
                                }
                            }
                        }
                    },
                    {
                        "allow": {
                            "to": {
                                "file": {
                                    "categories": {
                                        "noneOf": noneOfList
                                    }
                                }
                            }
                        }
                    },
                    {
                        "from": {
                            "file": {
                                "categories": {
                                    "noneOf": [
                                        "tests"
                                    ]
                                }
                            }
                        },
                        "disallow": {
                            "to": {
                                "file": {
                                    "categories": "tests"
                                }
                            }
                        }
                    }
                ],
                "checkInternals": true
            }
        ]
    },
    "files": ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"]}, gspothqEslintPlugin, "all"), [
        "tsconfig.json"
    ]),
    ...typescriptBlocks,
    setRuntime(setLevelRules({"rules": {},
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", buildRuntimeMatcher(0, runtimeDeclarations)]]}, gspothqEslintPlugin, "all"), globals, "nodeBuiltin", "module"),
    setRuntime(setLevelRules({"rules": {
        "unicorn/prefer-module": "off"
    },
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", buildRuntimeMatcher(1, runtimeDeclarations)]]}, gspothqEslintPlugin, "all"), globals, "node", "commonjs"),
    setRuntime(setLevelRules({"rules": {},
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", buildRuntimeMatcher(2, runtimeDeclarations)]]}, gspothqEslintPlugin, "all"), globals, "browser", "module"),
    setLevelRules({"rules": {
        "n/no-unsupported-features/node-builtins": [
            "error",
            {
                "allowExperimental": true
            }
        ],
        "n/no-unsupported-features/es-builtins": "error",
        "n/no-deprecated-api": "error",
        "unicorn/no-process-exit": "off",
        "n/no-unsupported-features/es-syntax": "off",
        "n/no-sync": "off",
        "n/no-callback-literal": "error",
        "n/no-new-require": "error",
        "n/no-path-concat": "error",
        "n/no-missing-import": "off",
        "n/no-missing-require": "off",
        "n/no-unpublished-import": [
            "error",
            {
                "ignoreTypeImport": true
            }
        ],
        "n/no-unpublished-require": "error",
        "n/hashbang": "error",
        "n/no-extraneous-import": "error",
        "n/no-extraneous-require": "error",
        "n/prefer-global/url-search-params": "error",
        "n/prefer-global/url": "error",
        "n/prefer-global/process": "error",
        "n/prefer-global/console": "error",
        "n/prefer-global/buffer": "error",
        "n/no-process-exit": "error",
        "n/prefer-promises/dns": "error",
        "n/prefer-promises/fs": "error"
    },
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", buildRuntimeMatcher(0, runtimeDeclarations)], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", buildRuntimeMatcher(1, runtimeDeclarations)]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "gspot/restricted-syntax": [
            "error",
            {
                "selector": ":matches(Program, BlockStatement, StaticBlock) > BlockStatement",
                "message": "A block that stands alone hides a step. Name the step as a function, or remove the braces."
            },
            {
                "selector": "TSEnumDeclaration",
                "message": "Use a literal union or an as-const object instead of an enum."
            },
            {
                "selector": ":matches(TSAsExpression[expression.type=\"TSAsExpression\"], TSTypeAssertion[expression.type=\"TSTypeAssertion\"])",
                "message": "Do not assert twice. Narrow the value, fix its type, or check it at run time."
            },
            {
                "selector": ":matches(TSAsExpression, TSTypeAssertion) > TSNeverKeyword",
                "message": "Do not assert to never to silence the type system."
            },
            {
                "selector": "Program:has(> :matches(ExportNamedDeclaration:not([exportKind=\"type\"]), ExportDefaultDeclaration, ExportAllDeclaration:not([exportKind=\"type\"]))) > :matches(ForStatement, ForOfStatement, ForInStatement, WhileStatement, DoWhileStatement, IfStatement, TryStatement)",
                "message": "A module that exports values runs no statements when it loads. Move this statement into a function that the entry point calls.",
                "ignores": [
                    "**/*.config.*"
                ]
            },
            {
                "selector": "NewExpression[callee.name=/Error$/]:matches([arguments.length=1], [arguments.1.type=\"ObjectExpression\"]) > :matches(Literal.arguments:first-child[value=/^[a-z]/], TemplateLiteral.arguments:first-child[quasis.0.value.raw=/^[a-z]/])",
                "message": "Start an error message with a capital letter."
            },
            {
                "selector": "LabeledStatement:not([body.type=/^(?:WhileStatement|DoWhileStatement|ForStatement|ForInStatement|ForOfStatement|SwitchStatement)$/])",
                "message": "Use a label only on a loop or switch statement. Remove this label."
            },
            {
                "selector": "ForStatement[init=null][update=null][test!=null]",
                "message": "This loop has no initializer or update. Use a while loop for its condition."
            },
            {
                "selector": "UnaryExpression[operator='delete']:not([argument.type='MemberExpression']):not([argument.type='ChainExpression']):not([argument.type='Identifier'])",
                "message": "The delete operator removes properties. Pass a property access instead of this expression."
            },
            {
                "selector": "AssignmentExpression:not(ExpressionStatement > AssignmentExpression):not(AssignmentExpression > AssignmentExpression):not(BinaryExpression[operator=/^(?:==|!=|===|!==|<|<=|>|>=)$/] > AssignmentExpression):not(SequenceExpression > AssignmentExpression):not(VariableDeclarator > AssignmentExpression):not(ArrowFunctionExpression > AssignmentExpression.body):not(LogicalExpression > AssignmentExpression.right):not(WhileStatement > AssignmentExpression.test):not(DoWhileStatement > AssignmentExpression.test):not(ForStatement > AssignmentExpression.init):not(ForStatement > AssignmentExpression.update)",
                "message": "Move this assignment into a separate statement before using its value."
            },
            {
                "selector": "CallExpression[callee.type=/^(?:ArrayExpression|ClassExpression|ObjectExpression|Literal|TemplateLiteral)$/]",
                "message": "Call a function or method instead of a literal value."
            },
            {
                "selector": "TaggedTemplateExpression[tag.type=/^(?:ArrayExpression|ClassExpression|ObjectExpression|Literal|TemplateLiteral)$/]",
                "message": "Use a function as the template tag instead of a literal value."
            },
            {
                "selector": "ImportDeclaration[source.value=/node_modules/]",
                "message": "Use the package's public name instead of a node_modules path."
            },
            {
                "selector": "CallExpression[callee.type='Identifier'][callee.name='require'][arguments.length=1][arguments.0.type='Literal'][arguments.0.value=type(string)][arguments.0.value=/node_modules/]",
                "message": "Use the package's public name instead of a node_modules path."
            },
            {
                "selector": ":matches(WhileStatement, DoWhileStatement, ForStatement, ForInStatement, ForOfStatement) > BlockStatement[body.length>1] > ContinueStatement[label=null]:last-child",
                "message": "This continue ends the loop body, so it does nothing. Remove it."
            },
            {
                "selector": ":matches(WhileStatement, DoWhileStatement, ForStatement, ForInStatement, ForOfStatement) > BlockStatement > IfStatement:last-child > BlockStatement[body.length>1] > ContinueStatement[label=null]:last-child",
                "message": "This continue ends the loop body, so it does nothing. Remove it."
            },
            {
                "selector": "Literal[regex.flags=/s/][regex.pattern=/\\[(?:\\\\s\\\\S|\\\\S\\\\s)\\]/]",
                "message": "The s flag makes . match every character. Write . instead of this character class."
            },
            {
                "selector": "LogicalExpression[operator=/^(\\|\\||\\?\\?)$/][right.type=\"ObjectExpression\"][right.properties.length=0]",
                "message": "An empty-object fallback hides a missing value. Handle the missing case."
            },
            {
                "selector": "CallExpression:matches([callee.property.name=/^(debug|info|warn|error|fatal|trace)$/], [callee.property.name=\"log\"][callee.object.name!=\"console\"]) > TemplateLiteral.arguments:first-child[expressions.length>0]",
                "message": "Log a stable message and pass the values as fields."
            },
            {
                "selector": "CallExpression[callee.property.name='waitForLoadState'] > Literal:first-child[value='networkidle']",
                "message": "Network inactivity does not prove that the page is ready. Wait for the visible state, response, or URL."
            },
            {
                "selector": "Program:has(ImportDeclaration[source.value='@playwright/test']) CallExpression[callee.name='expect'] > AwaitExpression:first-child",
                "message": "Pass the locator to expect, so that the assertion retries, such as await expect(locator).toHaveText(text)."
            },
            {
                "selector": "AssignmentExpression[left.property.name=/^(?:innerHTML|outerHTML)$/]:not([right.type=\"Literal\"])",
                "message": "Writing HTML into the page allows XSS. Set textContent, create the nodes, or write fixed markup."
            },
            {
                "selector": "CallExpression:matches([callee.property.name=\"insertAdjacentHTML\"][arguments.1.type!=\"Literal\"], [callee.object.name=\"document\"][callee.property.name=\"write\"][arguments.0.type!=\"Literal\"])",
                "message": "Writing HTML into the page allows XSS. Set textContent, create the nodes, or write fixed markup."
            },
            {
                "selector": "CallExpression[callee.name=\"fetch\"]:matches([arguments.0.object.object.name=\"req\"], [arguments.0.callee.object.property.name=\"searchParams\"][arguments.0.callee.property.name=\"get\"])",
                "message": "fetch() takes its URL from the request, which allows server-side request forgery. Allow only known hosts."
            },
            {
                "selector": "CallExpression[callee.property.name=/^(?:log|trace|debug|info|warn|error|fatal)$/][arguments.length=1]:matches([arguments.0.object.object.name=\"process\"][arguments.0.object.property.name=\"env\"][arguments.0.property.name=/KEY|SECRET|PASSWORD|TOKEN|CREDENTIAL/], [arguments.0.callee.object.object.name=\"Deno\"][arguments.0.callee.object.property.name=\"env\"][arguments.0.callee.property.name=\"get\"][arguments.0.arguments.0.value=/KEY|SECRET|PASSWORD|TOKEN|CREDENTIAL/])",
                "message": "The log writes a secret from the environment. Remove the value, or mask it."
            },
            {
                "selector": "CallExpression[callee.name=/^(?:execSync|exec)$/] > TemplateLiteral.arguments:first-child[expressions.length>0]",
                "message": "Interpolation in execSync() or exec() allows command injection. Use execFileSync() or execFile() with an argument array."
            },
            {
                "selector": ":matches(ImportDeclaration, ExportAllDeclaration, ExportNamedDeclaration, ImportExpression)[source.value=/^(#[^/]+\\/|@\\/)/][source.value!=/\\.[^/?.]+$/]:not([source.value=/\\?/]):not(:has(ImportAttribute:matches([key.name='type'],[key.value='type'])[value.value='json']))",
                "message": "Give an alias import its file extension."
            }
        ]
    },
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "**/*"]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "no-console": "error"
    },
    "ignores": [
        "**/test/**",
        "**/tests/**",
        "**/__tests__/**",
        "**/*.test.*",
        "**/*.spec.*",
        "**/Tests/**",
        "scripts/**",
        "**/*.config.{js,mjs,cjs,ts}",
        "{mise-tasks,.mise-tasks,mise/tasks,.mise/tasks,.config/mise/tasks}/**"
    ],
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "**/*"]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "n/no-process-exit": "off",
        "unicorn/no-process-exit": "off"
    },
    "files": [["scripts/**", "**/*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"], ["**/*.config.{js,mjs,cjs,ts}", "**/*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"], ["{mise-tasks,.mise-tasks,mise/tasks,.mise/tasks,.config/mise/tasks}/**", "**/*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "n/no-unpublished-import": "off",
        "n/no-unpublished-require": "off",
        "no-template-curly-in-string": "off",
        "unicorn/no-incorrect-template-string-interpolation": "off"
    },
    "files": [["**/test/**", "**/*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"], ["**/tests/**", "**/*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"], ["**/__tests__/**", "**/*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"], ["**/*.test.*", "**/*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"], ["**/*.spec.*", "**/*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"], ["**/Tests/**", "**/*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"extends": [eslintPluginPackageJson["configs"]["recommended"]],
    "files": ["**/package.json"]}, gspothqEslintPlugin, "all"),
    setLevelRules({"extends": [eslintConfigPrettier],
    "files": ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "package-json/restrict-dependency-ranges": [
            "error",
            {
                "forDependencyTypes": [
                    "devDependencies"
                ],
                "rangeType": "pin"
            }
        ],
        "package-json/scripts-name-casing": "error",
        "package-json/valid-contributors": "off"
    },
    "files": ["**/package.json"]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "package-json/restrict-dependency-ranges": [
            "error",
            {
                "rangeType": "pin"
            }
        ]
    },
    "files": ["package.json"]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "package-json/require-packageManager": "error"
    },
    "files": ["package.json"]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "max-lines": maxLinesList,
        "max-lines-per-function": maxLinesPerFunctionList,
        "max-params": maxParamsList,
        "max-depth": maxDepthList,
        "max-statements": maxStatementsList,
        "max-nested-callbacks": maxDepthList,
        "complexity": complexityList
    },
    "files": ["**/*.{js,mjs,cjs,jsx}"]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "gspot/no-trivial-files": [
            "error",
            {
                "reexports": "none",
                "indexExports": 20
            }
        ],
        "gspot/no-trivial-functions": [
            "error",
            {
                "trivialFunctionStatements": 2
            }
        ]
    },
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "**/*.{js,mjs,cjs,jsx}"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "**/*.{ts,mts,cts,tsx,vue,svelte,astro}"]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "import-x/no-default-export": "off",
        "unicorn/no-top-level-side-effects": "off"
    },
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "**/*.config.*"]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "@typescript-eslint/consistent-type-definitions": "off"
    },
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "**/*.d.ts"]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "import-x/no-default-export": "off"
    },
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "**/*.d.ts"]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "gspot/import-boundaries": "off"
    },
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/extension.ts"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/extension.ts/**"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/http.ts"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/http.ts/**"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/text.ts"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/text.ts/**"]]}, gspothqEslintPlugin, "all"),
    setLevelRules({"rules": {
        "n/file-extension-in-import": "off"
    },
    "files": [["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/extension.ts"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/extension.ts/**"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/http.ts"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/http.ts/**"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/text.ts"], ["**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*", "web/scripts/text.ts/**"]]}, gspothqEslintPlugin, "all"),
]), [
    {
        "paths": [
            [
                "**/*",
                "**/*"
            ]
        ],
        "ignores": [],
        "rules": {}
    }
], "all");
