# JavaScript

Read this rule when you change JavaScript or TypeScript code.

## Modules

Do not convert existing CommonJS modules unless the task includes migrating them. Browser code imports no server
implementation.

### Module conventions

- When a library publishes its API through an index file, ask the user to set `structure.reexports` to `index-only`.
- Name a namespace import after its file or package, such as `fileOne` for `file-one.js`.
- Keep the exported name of an import. Add an alias only when two imports collide, and name it for its domain, such as
  `DomesticatedCat`.
- Use a default import only for a package that requires one, and name it for the exported value.

## Values

- Use `null` for a meaningful domain value and `undefined` for missing object properties.
- Use `??` when only `null` and `undefined` require a fallback. Do not use `||` when an empty string, zero, or false has
  a valid meaning.
- Name regular expressions after the value or contract they validate.

## Objects and functions

A function that mutates its input names and documents that effect.

Write a JSDoc comment as `/**` on its own line, then lines with no leading `*`, then `*/`.

### Function conventions

- Do not add optional parameters to hide a broken caller contract.
- Write `@param <name> <what it is>` only for a fact that the name and type do not state, such as the unit of a number.

## Asynchronous work

Release child processes, subscriptions, and other resources in `finally` or the cleanup mechanism of the API.

Check `response.ok` before parsing a `fetch` response, and never turn a failed read into an empty result.

## Workspaces

- Each workspace package builds itself. Its build file lives in it and imports only its own files.
- Pass a value between packages through a declared setting or a public API, never a file that a build writes.
