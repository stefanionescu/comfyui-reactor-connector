import { stripRuntimeGlobals, mergePresetRules, addPlugins, setRootFolder, setImportLookup } from "../javascript/eslint/functions.mjs";
import typescriptEslint from "typescript-eslint";
import globals from "globals";
import { createTypeScriptImportResolver } from "eslint-import-resolver-typescript";
export default [
    {"extends": [stripRuntimeGlobals(typescriptEslint["configs"]["base"], globals)],
    "files": [["**/*.{ts,mts,cts,tsx}", "**/*"]]},
    mergePresetRules({"files": [["**/*.{ts,mts,cts,tsx}", "**/*"]]}, typescriptEslint["configs"]["strictTypeChecked"]),
    setImportLookup(setRootFolder(addPlugins({"rules": {
        "no-const-assign": "error",
        "@typescript-eslint/no-misused-spread": [
            "error",
            {
                "allow": [
                    "string"
                ]
            }
        ],
        "jsdoc/require-param-type": "off",
        "jsdoc/require-returns-type": "off",
        "jsdoc/check-types": "off",
        "jsdoc/no-undefined-types": "off",
        "jsdoc/valid-types": "off",
        "jsdoc/no-types": "error",
        "jsdoc/check-tag-names": [
            "error",
            {
                "typed": true
            }
        ],
        "@typescript-eslint/consistent-type-definitions": [
            "error",
            "type"
        ],
        "@typescript-eslint/consistent-type-imports": "error",
        "import-x/no-duplicates": [
            "error",
            {
                "prefer-inline": true
            }
        ],
        "@typescript-eslint/consistent-type-exports": "error",
        "@typescript-eslint/switch-exhaustiveness-check": [
            "error",
            {
                "considerDefaultExhaustiveForUnions": true
            }
        ],
        "@typescript-eslint/prefer-readonly": "error",
        "@typescript-eslint/require-array-sort-compare": "error",
        "unicorn/require-array-sort-compare": "off",
        "unicorn/no-useless-coercion": "off",
        "@typescript-eslint/no-floating-promises": [
            "error",
            {
                "ignoreVoid": false
            }
        ],
        "@typescript-eslint/no-unused-vars": [
            "error",
            {
                "args": "all",
                "argsIgnorePattern": "^_",
                "varsIgnorePattern": "^_",
                "destructuredArrayIgnorePattern": "^_",
                "ignoreUsingDeclarations": true
            }
        ],
        "@typescript-eslint/no-require-imports": "off",
        "@typescript-eslint/strict-boolean-expressions": "error",
        "@typescript-eslint/restrict-template-expressions": [
            "error",
            {
                "allowAny": false,
                "allowBoolean": false,
                "allowNever": false,
                "allowNullish": false,
                "allowNumber": true,
                "allowRegExp": false
            }
        ],
        "@typescript-eslint/explicit-module-boundary-types": "error",
        "@typescript-eslint/prefer-optional-chain": "error",
        "@typescript-eslint/array-type": [
            "error",
            {
                "default": "array-simple"
            }
        ],
        "@typescript-eslint/consistent-type-assertions": [
            "error",
            {
                "assertionStyle": "as",
                "objectLiteralTypeAssertions": "never",
                "arrayLiteralTypeAssertions": "never"
            }
        ],
        "@typescript-eslint/prefer-nullish-coalescing": "error",
        "gspot/no-magic-numbers": [
            "error",
            {
                "ignoreEnums": true,
                "ignoreArrayIndexes": true,
                "ignoreReadonlyClassProperties": true,
                "ignoreTypeIndexes": true,
                "ignore": [
                    -1,
                    0,
                    1
                ]
            }
        ],
        "@typescript-eslint/ban-ts-comment": [
            "error",
            {
                "ts-expect-error": false
            }
        ]
    },
    "settings": {
        "import-x/parsers": {
            "@typescript-eslint/parser": [
                ".ts",
                ".tsx",
                ".mts",
                ".cts"
            ]
        }
    },
    "files": [["**/*.{ts,mts,cts,tsx}", "**/*"]]}, { "@typescript-eslint": typescriptEslint["plugin"] }), [
        [
            "languageOptions",
            "parserOptions",
            "tsconfigRootDir"
        ]
    ]), createTypeScriptImportResolver, [
        "tsconfig.json"
    ]),
    {"languageOptions": {
        "parserOptions": {
            "projectService": true
        }
    },
    "ignores": [
        "**/*.astro"
    ],
    "files": [["**/*.{ts,mts,cts,tsx}", "**/*"]]},
    {"rules": {
        "gspot/no-magic-numbers": "off",
        "@typescript-eslint/no-non-null-assertion": "off"
    },
    "files": [["**/test/**", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*"], ["**/tests/**", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*"], ["**/__tests__/**", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*"], ["**/*.test.*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*"], ["**/*.spec.*", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*"], ["**/Tests/**", "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}", "**/*"]]},
];
