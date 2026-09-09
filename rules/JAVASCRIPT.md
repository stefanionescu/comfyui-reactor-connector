# Working With JavaScript and TypeScript

These rules apply to the ComfyUI browser extension, TypeScript declarations,
build scripts, configuration modules, and JavaScript quality tools.

## Contents

- [Core JavaScript philosophy](#core-javascript-philosophy)
- [Project standards](#project-standards)
- [Scope](#scope)
- [Runtime standard](#runtime-standard)
- [Source files](#source-files)
- [Modules, imports, and exports](#modules-imports-and-exports)
- [ComfyUI boundaries](#comfyui-boundaries)
- [Templates and browser assets](#templates-and-browser-assets)
- [Naming](#naming)
- [Values, literals, and coercion](#values-literals-and-coercion)
- [Objects, arrays, and destructuring](#objects-arrays-and-destructuring)
- [Functions and parameters](#functions-and-parameters)
- [Classes](#classes)
- [Null, undefined, and optional values](#null-undefined-and-optional-values)
- [Runtime boundaries](#runtime-boundaries)
- [Errors and async code](#errors-and-async-code)
- [Comments and JSDoc](#comments-and-jsdoc)
- [Generated code](#generated-code)
- [Verification commands](#verification-commands)

## Core JavaScript philosophy

TypeScript extends the ComfyUI interface. Build code produces deterministic
browser assets. Quality tooling checks the repository and must not enter the
installed runtime package.

Prefer plain values, small functions, explicit module boundaries, and readable control flow. Avoid clever runtime indirection, implicit globals, hidden side-effects, and abstractions that obscure the owner of browser behavior.

If a checker and a rule disagree, report the conflict. Do not weaken either to
bypass it. Change tooling or rules only when the user requests that work.

## Project standards

Use these defaults for modules, imports, browser code, and runtime checks.

| Topic              | Adopted Rule                                                                                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Formatting         | Let Prettier and ESLint own formatting. Do not copy external formatting rules manually.                                                                                |
| Modules            | Use ES modules. Keep CommonJS only where a tool requires its configuration format.                                                                                     |
| Browser scripts    | Keep browser TypeScript under `web/`. Do not put executable inline scripts in generated help.                                                                          |
| Exports            | Prefer named exports for module code. Allow default exports only where ecosystem config files require them.                                                            |
| Naming             | Use purpose-based names and consistent casing for identifiers, files, and modules.                                                                                                 |
| Runtime boundaries | Treat configuration, Markdown, provider responses, user input, and generated paths as runtime boundaries that require explicit escaping, validation, or normalization. |

Project-specific rules are authoritative when they deliberately choose a stricter or clearer standard.

## Scope

Apply this guide to:

- `web/**/*.ts`, including `.d.ts` declarations.
- `scripts/frontend.mjs`.
- JavaScript development tools and their configuration modules.

Keep generated browser assets and help under `web/dist/`.

Use strict TypeScript checks. Narrow unknown input at the API boundary instead
of spreading `any` or unchecked assertions through the UI. Keep declarations
for ComfyUI's supplied APIs in the host declaration file. Declarations describe
the host contract; they must not create runtime shims.

## Runtime standard

Run development scripts with the Bun version pinned in `mise.toml`. Keep
`bun.lock` as the only frontend dependency lock. Browser code runs as ES modules
in ComfyUI and must not require Node or Bun at runtime. Disable automatic package
installation in checks and hooks.

Rules:

- Use APIs available in the declared runtime.
- Do not rely on implicit globals except the browser globals explicitly allowed by ESLint for `web/`.
- Keep package versions exact; do not use range prefixes.
- Do not add a build step that requires a runtime outside the repo's declared tooling without updating `mise.toml`, package policy, and documentation.

## Source files

Use UTF-8 source files. Put imports before implementation and keep a blank line
after the complete import block, including before comments.

Rules:

- Use `const` by default.
- Use `let` only for reassignment.
- Never use `var` in module code.
- Keep side-effect imports rare and explicit.
- Do not add file-level history comments, stale path references, or generated examples that are not part of working code.
- Prefer direct, searchable code over clever indirection.

If a module needs a short explanation, document the purpose, not how it changed.

## Modules, imports, and exports

Follow the owner boundary of the file you are editing.

Rules:

- Keep the Madge configuration in CommonJS because its configuration loader requires that format.
- Use ES modules for development tools. Use the package's configured imports
  directly; do not add alias or forwarding modules.
- Prefer named imports and named exports for module code.
- Avoid mutable exports such as `export let`.
- Avoid default exports in app modules.
- Allow default exports for ecosystem-owned config files when the tool expects them.
- Do not create container classes or exported objects only to simulate a namespace.
- Avoid root mega-barrels. Keep re-exports small and intentional.

Browser code must not import quality tooling, Python runtime modules, or Node-only
code. Preserve the exact host module imports supplied by ComfyUI.

## ComfyUI boundaries

- `web/` owns authored browser code, styles, and node guides.
- `web/dist/` contains generated browser files and help served by ComfyUI.

Keep configuration declarative. Do not import executable tooling into policy
configuration. Keep generated paths within their declared output directory.

Namespace extension commands, settings, routes, styles, and events. Release
listeners, timers, media streams, and object URLs when their owner closes.
Support keyboard use, focus return, themes, tabs, and the supported renderer.
Keep credentials on the server. Do not copy them into widgets, workflow files,
browser storage, or messages sent to other windows.

Use one compact help action per node and native help where possible. Every extra
control must support a concrete task. Do not add duplicate previews, tours,
decorative animation, or global canvas patches. Ordinary execution must work
without opening a custom panel. Bundle scripts locally; do not load runtime code
from a CDN. Render provider text as text, never executable markup.

## Templates and browser assets

Generated node help should stay declarative. Put interactive controls in the
extension modules that own their lifecycle.

Rules:

- Do not add executable inline scripts to templates.
- Do not use `document.write`.
- Do not use inline event handler attributes.
- Do not use `javascript:` URLs.
- Put browser behavior in the relevant `web/` module.
- Prefer safe DOM mutation: `textContent`, attributes, class changes, and created nodes.
- Avoid `innerHTML`, `outerHTML`, and `insertAdjacentHTML` unless a reviewed static, trusted markup path is the real contract.
- Keep visible copy with its node, control, locale entry, or authored guide. Do not duplicate instructions in build-script template literals.

Browser scripts should be defensive at DOM boundaries without swallowing real programming errors. Check that required elements exist before binding behavior.

## Naming

Use camelCase for functions, variables, and parameters; PascalCase for classes and
types; and UPPER_SNAKE_CASE for constants that use the repository's constant
convention. Name modules for their behavior. Avoid generic names such as helper,
manager, or utils, and keep external API names exact at the boundary.

## Values, literals, and coercion

Prefer explicit, unsurprising values.

Rules:

- Use `const` for values that do not change.
- Use frozen objects or plain constant objects for fixed value sets.
- Avoid implicit coercion for user input, environment values, request values, model settings, and build placeholders.
- Use explicit parsing for strings, numbers, booleans, dates, and URLs that cross a runtime boundary.
- Do not use truthiness checks when `0`, `''`, `false`, `null`, and `undefined` have different meanings.
- Keep regular expressions close to the policy they enforce and name them by the contract they validate.

## Objects, arrays, and destructuring

Keep object and array handling readable.

Rules:

- Use object literals for grouped data instead of positional parameter lists.
- Use destructuring when it clarifies the fields being used.
- Give destructured values clear local names without repeating their context.
- Avoid mutation of input objects unless the function name and owner contract make mutation explicit.
- Prefer array methods when they improve clarity, but do not contort simple loops only to satisfy style preference.
- Narrow indexed reads before use when the value may be absent.

## Functions and parameters

Make function contracts obvious from names, parameters, and call sites.

Rules:

- Keep functions small and focused.
- Avoid parameter reassignment.
- Prefer options objects once a function takes several related values.
- Do not use optional parameters to avoid fixing a caller contract.
- Keep callback nesting shallow.
- Use early returns to keep error and missing-state handling readable.
- Avoid pass-through functions that only rename another call.

Export public tool functions directly. Do not add wrapper modules or automated
tests. Use the existing runner only when verification is requested.

## Classes

Use classes only when instance identity or encapsulated state is real.

Rules:

- Do not create static container classes for namespacing.
- Prefer plain functions and objects for stateless behavior.
- Keep constructors simple.
- Do not use decorators.
- Do not add inheritance unless it represents a real runtime relationship.

If a class has no meaningful instance state, it probably should be a module with named exports.

## Null, undefined, and optional values

Handle absent values deliberately.

Rules:

- Use `null` only when it is a meaningful domain value.
- Let missing object properties be `undefined`.
- Use `??` when only `null` and `undefined` should trigger a fallback.
- Do not use `||` as a fallback when empty strings, zero, or false are valid.
- Check DOM lookups and optional browser APIs before use.
- Keep fallback values local and explicit.

## Runtime boundaries

Runtime boundaries must be validated or escaped before use.

Boundary examples:

- Markdown rendered into node help.
- Provider text displayed in dialogs.
- URLs and public paths.
- Environment variables.
- Live controls and webcam frames.
- File paths supplied to quality tooling.

Rules:

- Escape HTML attributes and text through the local helper APIs.
- Normalize public paths before writing generated assets.
- Validate URLs before using them in generated markup.
- Do not log sensitive environment values.
- Avoid dynamic `require` or dynamic `import` for repo-owned modules.
- Prefer `spawn`/`execFile` with argument arrays over shell command strings.

## Errors and async code

Async code should make failure modes visible.

Rules:

- Await promises that must complete before the next step.
- Handle expected failures at the owner boundary.
- Do not catch and ignore errors unless the ignored failure is explicitly safe and documented by the local contract.
- Preserve useful error messages in build tooling.
- Do not expose internal stack traces in HTTP responses.
- Clean up spawned servers or child processes in `finally` blocks.
- Cancel owned requests and release media resources when dialogs close.
- Handle late camera permission responses by stopping streams whose owner has closed.

## Comments and JSDoc

Use comments to explain non-obvious intent, constraints, or policy. Do not describe syntax that is already clear from the code.

Rules:

- Prefer short comments near the surprising decision.
- Do not add history comments.
- Do not leave commented-out code.
- Keep shellcheck and lint disable comments justified with a nearby reason and ticket marker when policy requires it.
- JSDoc is useful for exported quality helpers, but routine private functions do not need boilerplate comments.

## Generated code

Generated browser output belongs in `web/dist/`. Release archives belong in root
`dist/`, and private quality reports belong in ignored artifact directories.

Rules:

- Do not edit generated files as the source of truth.
- Keep generated asset names deterministic and content-hashed where the build pipeline expects hashes.
- Generate native Markdown help and dialog HTML from the same authored guide.
- Escape generated help and copy only the public assets linked by its guides.

## Verification commands

Run linting, formatting, type checks, builds, scans, and browser checks only when
the user explicitly requests them. A code or documentation edit does not request
verification. Use the existing task for the affected scope; do not create a new
runner, workflow, or automated test.

Write comments and user-visible text in plain language. Explain what readers
need to know and what action they can take.
