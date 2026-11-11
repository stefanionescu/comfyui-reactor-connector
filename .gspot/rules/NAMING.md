# Naming

Read this rule when you name a file, folder, type, function, or variable.

## Casing across languages

- Acronyms: TypeScript and JavaScript treat them as words, such as `parseHttpUrl` and `userId`. Swift keeps them
  uppercase, such as `avatarURL`. Python, SQL, and Bash lowercase them, such as `http_url`.
- On the wire: camelCase JSON fields and kebab-case URL segments. Log event names and fields follow the property case of the
  language, unless an existing logging interface defines their spelling.
- Constants: a module-level constant bound to a literal or a frozen object uses `UPPER_SNAKE_CASE` in TypeScript,
  JavaScript, Python, and Bash, and camelCase in Swift.

## Principles

Name by role, responsibility, and domain meaning, never by storage type, UI framework type, collection shape, or
implementation accident: `users`, not `userArray`. Never hide a bad name in a string key, an alias, or a file name.
Prefer the shortest name that keeps its meaning at the use site. Add a qualifier only when the bare name has more than
one meaning there.

Do not repeat context the enclosing type, module, folder, or package already supplies, or encode every implementation
detail: `Car.make`, not `Car.carMake`.

Give each concept one word across the repository, and each word one meaning. Before you give a word to a new concept,
search the code for it. When the word already names another concept, choose a different one.

Pick one word for each concept the program shows, and use it everywhere.

Ask the user before you add a rejected word to `naming.terms` with its replacement, such as
`"config file" = "generated file"`. The naming check then reports the word in identifiers, and the prose check in
documentation, code comments, and commit messages.

## Functions and methods

A function name starts with the action and carries enough domain context to read at the call site without repeating the
enclosing type or module. `handle` exists only in a framework callback such as a React `handleSubmit` or a UIKit
`@objc handleConfirmButtonTapped`.

Each act has one verb. Use the verb below for each act, never a synonym:

- `get`: Take a value already in memory: a variable, a map entry, a cache, or a parsed structure. The return type says
  if it may be absent.
- `read`: Take data from outside memory: a file, Git, the environment, a child process, or the network. The return type
  says if it may be absent.
- `find`: Search for one item. Return nothing when it is absent.
- `list`: Return every item of a kind, such as the orders of a customer.
- `select`: Choose among known options.
- `detect`: Infer a fact from evidence, such as the language of a file.
- `build`: Construct a value in memory from other values, such as a message, a plan, or the text of a file.
- `create`: Make a new file, folder, or other resource on disk.
- `parse`, `decode`: Raw text to structured data; encoded bytes or payloads to typed values.
- `encode`, `serialize`: Typed values to bytes; values to the text of a file format.
- `format`: Return the text that people read for a value: terminal lines, Markdown, or a message.
- `print`: Write text that people read to a terminal or a log stream.
- `write`: Put data into a file or another store outside memory.
- `validate`: Return what makes one value invalid.
- `assert`: Throw an error on an invalid value.
- `check`: Run a check that reports findings, such as a lint check. Use `validate` or `assert` for one value.
- `run`: Start a named program, command, or step, such as `runMigrations`. Never a bare `run`.
- `spawn`: Start a child process.
- `set`: Assign a key or a field of a value in memory.
- `add`, `remove`: Put an item into a collection in memory, or take it out.
- `insert`, `update`, `delete`: Add, change, or destroy a row or item in persisted data, or a file on disk.
- `prepare`, `refresh`, `reset`: Set up local state before a workflow; replace presentation state from a source; return
  to an initial state.
- `is`, `has`, `can`: Predicates only: `is` for state, `has` for presence, and `can` for capability.

When none fits, pick another plain one that names the act.

## Booleans and predicates

A stored field or column takes no prefix, such as `enabled` or `webSearchEnabled`. A boolean variable or parameter, and
a predicate, starts with `is`, `has`, or `can`. Name an action for what it does even when it returns a boolean, such as
`sendInvite`.

## Files and folders

Name files and folders for the behavior or entity they contain, not for reuse.

- Name a file that holds one primary type after it, where the language does so. Name a module after the capability it
  implements. Prefer feature folders to top-level type buckets.

## External names

DTOs, SQL rows, generated types, wire payloads, and validation schemas keep the external field names. Renaming one
changes the public interface. Translate them into domain names through explicit mappings before the values reach domain
or presentation code. Keep provider, database, and HTTP mechanics out of domain names.
