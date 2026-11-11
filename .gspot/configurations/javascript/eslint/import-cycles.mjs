import config from './eslint.mjs';
import { keepCycleFields } from './functions.mjs';

export default [
    ...config.map((block) => keepCycleFields(block)),
    {
        linterOptions: { reportUnusedDisableDirectives: 'off' },
        settings: { 'import-x/cache': { lifetime: Infinity } },
        rules: { 'import-x/no-cycle': ['error', { ignoreExternal: true }] },
    },
];
