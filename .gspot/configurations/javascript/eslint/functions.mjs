import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
export const root = fileURLToPath(new URL('../../../..', import.meta.url)).replace(/[\\/]$/u, '');
const importLookups = new WeakMap();
const componentParserOptions = { tsconfigRootDir: root, ecmaVersion: 'latest', sourceType: 'module' };
function pickRuleOptions(block, options) {
    const rules = block.rules === undefined ? [] : Object.entries(block.rules);
    const picked = rules.flatMap(([name, value]) => {
        const override = options.rules[name];
        const severity = Array.isArray(value) ? value[0] : value;
        return override === undefined || severity === 'off' || severity === 0 ? [] : [[name, [severity, ...override]]];
    });
    if (picked.length === 0)
        return [];
    const files = block.files?.flatMap((file) => options.paths.map((path) => [...[file].flat(), ...path]));
    return [
        {
            files: files ?? options.paths,
            ignores: [...(block.ignores ?? []), ...options.ignores],
            rules: Object.fromEntries(picked),
        },
    ];
}
function dropProjectService(languageOptions) {
    const parserOptions = languageOptions['parserOptions'];
    if (parserOptions === undefined)
        return languageOptions;
    const { project: _project, projectService: _projectService, ...parsing } = parserOptions;
    return { ...languageOptions, parserOptions: parsing };
}
function setRuleLevel(value, level) {
    const configured = Array.isArray(value) ? value : [value];
    const [severity, ...options] = configured;
    if (severity === 'off' || severity === 0)
        return value;
    return Array.isArray(value) ? [level, ...options] : level;
}
function listScriptLanguages(parsed) {
    const vueComponent = parsed.services?.getDocumentFragment?.();
    return vueComponent === undefined
        ? parsed.ast.body
            .filter((node) => node.type === 'SvelteScriptElement')
            .flatMap((script) => script.startTag.attributes)
            .filter((attribute) => attribute.key?.name === 'lang')
            .map((attribute) => attribute.value[0]?.value)
        : vueComponent.children
            .filter((node) => node.type === 'VElement' && node.name === 'script')
            .flatMap((script) => script.startTag.attributes)
            .filter((attribute) => attribute.key?.name === 'lang')
            .map((attribute) => attribute.value?.value);
}
/**
Remove host runtime globals and keep framework compiler and test names. Runtime APIs get their globals from blocks with
their own file selectors.
*/
export function stripRuntimeGlobals(preset, globalsByRuntime) {
    const names = new Set(Object.keys({
        ...globalsByRuntime['node'],
        ...globalsByRuntime['browser'],
        ...globalsByRuntime['worker'],
        ...globalsByRuntime['serviceworker'],
        ...globalsByRuntime['react-native'],
    }));
    return [preset].flat().map((config) => {
        const configGlobals = config.languageOptions?.globals;
        if (configGlobals === undefined)
            return config;
        return {
            ...config,
            languageOptions: {
                ...config.languageOptions,
                globals: Object.fromEntries(Object.entries(configGlobals).filter(([name]) => !names.has(name))),
            },
        };
    });
}
export function buildRuntimeMatcher(index, runtimes) {
    const matchers = runtimes.map(({ scopePath, includes, excludes }) => {
        const included = includes.map((source) => new RegExp(source, 's'));
        const excluded = excludes.map((source) => new RegExp(source, 's'));
        return (path) => (scopePath === '' || path.startsWith(`${scopePath}/`)) &&
            included.some((pattern) => pattern.test(path)) &&
            excluded.every((pattern) => !pattern.test(path));
    });
    return (file) => matchers.findLastIndex((matches) => matches(relative(root, file).split(sep).join('/'))) === index;
}
/**
Select Vue or Svelte files whose script element asks for TypeScript. The final parser reports syntax errors;
a file that does not parse counts as untyped.
*/
export function buildComponentMatcher(parser, typescriptParser) {
    const scriptParser = typescriptParser === undefined ? false : { ts: typescriptParser, typescript: typescriptParser };
    return (file) => {
        try {
            const parsed = parser.parseForESLint(readFileSync(file, 'utf8'), {
                ...componentParserOptions,
                filePath: file,
                parser: scriptParser,
            });
            return listScriptLanguages(parsed).some((language) => language === 'ts' || language === 'typescript');
        }
        catch (error) {
            if (error instanceof SyntaxError || (error instanceof Error && error.name === 'TSError'))
                return false;
            throw error;
        }
    };
}
export function importAstroPlugin(moduleUrl = import.meta.url) {
    const previousFolder = process.cwd();
    try {
        process.chdir(dirname(fileURLToPath(moduleUrl)));
        const require = createRequire(moduleUrl);
        const pluginRequire = createRequire(require.resolve('eslint-plugin-astro/package.json'));
        const plugin = pluginRequire('./lib/index.mjs');
        return typeof plugin === 'object' && plugin !== null && 'default' in plugin ? plugin.default : plugin;
    }
    finally {
        process.chdir(previousFolder);
    }
}
/**
Read Svelte's parser dependencies from the generated tool project.

@returns a component parser that restores the working folder after each parse.
*/
export function importSvelteParser(moduleUrl = import.meta.url) {
    const parser = createRequire(moduleUrl)('svelte-eslint-parser');
    return {
        ...parser,
        parseForESLint(code, options) {
            const previousFolder = process.cwd();
            try {
                process.chdir(dirname(fileURLToPath(moduleUrl)));
                return parser.parseForESLint(code, options);
            }
            finally {
                process.chdir(previousFolder);
            }
        },
    };
}
export function mergePresetRules(block, preset) {
    const rules = [preset, block]
        .flat()
        .flatMap((config) => (config.rules === undefined ? [] : Object.entries(config.rules)));
    return { ...block, rules: Object.fromEntries(rules) };
}
export function mergeRuleOptions(block, options) {
    const rules = { ...block.rules };
    for (const [name, added] of Object.entries(options)) {
        const value = rules[name];
        if (Array.isArray(value))
            rules[name] = [value[0], { ...value[1], ...added }];
    }
    return { ...block, rules };
}
/**
Give your rule options to each rule that a block turns on, in a block right after it that keeps its severity. Refuse
options for a rule that no block turns on.
*/
export function setRuleOptions(blocks, ruleOptions, level) {
    const pairs = blocks.map((block) => ({
        block,
        picked: ruleOptions.flatMap((options) => pickRuleOptions(block, options)),
    }));
    const applied = new Set(pairs.flatMap(({ picked }) => picked.flatMap((option) => Object.keys(option.rules))));
    const refused = new Set(ruleOptions.flatMap((options) => Object.keys(options.rules))).difference(applied);
    if (refused.size > 0)
        throw new Error(Array.from(refused, (name) => `gspot does not run ${name} at level ${level}, so it takes no options. For a rule of your own, add a [[tools.eslint.plugins]] record.`).join('\n'));
    return pairs.flatMap(({ block, picked }) => [block, ...picked]);
}
export function setLevelRules(block, plugin, config) {
    const rulePairs = block.rules === undefined ? [] : Object.entries(block.rules);
    const rules = Object.fromEntries(rulePairs);
    for (const [name, value] of rulePairs) {
        if (!name.startsWith('gspot/'))
            continue;
        const level = plugin.configs[config]?.rules?.[name] ?? 'off';
        rules[name] = setRuleLevel(value, level);
    }
    return { ...block, rules };
}
export function addPlugins(block, plugins) {
    return { ...block, plugins: { ...block.plugins, ...plugins } };
}
export function setRootFolder(block, keys, scopePath = '') {
    const result = { ...block };
    for (const path of keys) {
        let target = result;
        const parents = path.slice(0, -1);
        for (const key of parents) {
            const child = { ...target[key] };
            target[key] = child;
            target = child;
        }
        target[path.at(-1)] = join(root, scopePath);
    }
    return result;
}
export function setImportLookup(block, createImportLookup, projects) {
    const importLookup = importLookups.get(createImportLookup) ??
        createImportLookup({ project: projects.map((project) => join(root, project)), noWarnOnMultipleProjects: true });
    importLookups.set(createImportLookup, importLookup);
    return { ...block, settings: { ...block.settings, 'import-x/resolver-next': [importLookup] } };
}
export function setBoundaryLookup(block, projects) {
    return {
        ...block,
        settings: {
            ...block.settings,
            'import/resolver': {
                typescript: { project: projects.map((project) => join(root, project)), noWarnOnMultipleProjects: true },
            },
        },
    };
}
export function setRuntime(block, globals, names, sourceType) {
    const selected = globals[names];
    if (selected === undefined)
        throw new Error(`The globals package has no runtime named ${names}. Set tools.eslint.override.runtime to one of: ${Object.keys(globals).join(', ')}.`);
    return { ...block, languageOptions: { ...block.languageOptions, sourceType, globals: selected } };
}
export function setComponentParser(block, parser, typescriptParser) {
    const options = block.languageOptions?.['parserOptions'];
    return {
        ...block,
        languageOptions: {
            ...block.languageOptions,
            parser,
            parserOptions: {
                ...options,
                ...(typescriptParser !== undefined && {
                    parser: { ts: typescriptParser, typescript: typescriptParser },
                }),
            },
        },
    };
}
export function setScriptParser(block, parser) {
    return {
        ...block,
        languageOptions: {
            ...block.languageOptions,
            parserOptions: { ...block.languageOptions?.['parserOptions'], parser },
        },
    };
}
export function setJestGlobals(block, plugin) {
    return { ...block, languageOptions: { ...block.languageOptions, globals: plugin.environments.globals.globals } };
}
/**
Keep the parts of a block that import-x/no-cycle reads: its files, parser, processor, plugins, and import-x settings.
Leave out its rules and its other settings, which import-x hashes on every resolve, and the TypeScript project
service, whose type information the rule does not read.
*/
export function keepCycleFields(block) {
    const { rules: _rules, settings, languageOptions, ...kept } = block;
    const importSettings = settings === undefined ? [] : Object.entries(settings).filter(([key]) => key.startsWith('import-x/'));
    return {
        ...kept,
        ...(languageOptions !== undefined && { languageOptions: dropProjectService(languageOptions) }),
        ...(importSettings.length > 0 && { settings: Object.fromEntries(importSettings) }),
    };
}
