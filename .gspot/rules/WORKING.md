# Working in a repository

Read this rule before you change anything in the repository.

## Running processes

Check for a running instance before you start a dev server, a build watcher, an emulator, or a database. Reuse what
runs. Start a second instance only for a test that needs isolation, or when the user asks in this conversation. Stop
what you started when the task ends.

## Thinking before coding

When you change a function, update its doc comment. Trace the callers of what you change.

Fix the cause of a failure. Do not hide it with a special case. Special cases include a longer time limit for one test,
a budget for one suite or system, an environment switch, and an option for one caller.

Treat stored data and wire formats as contracts. Rename a stored key together with a migration of the stored data.
During a rolling deploy, readers accept both shapes until no old writer runs.

Delete a folder once neither it nor its subfolders hold a file. Before you add a module, folder, or helper, find the code that will call it. When you add a file, tell the user why that
code needs a new file.

## Open questions

- When a request, a plan, or a feature leaves a decision open, ask the user before you write code or a plan. Ask
  until no open point remains.
- Do not fill a gap with a guess, a default you chose, or an idea the user did not ask for.
- Ask only what the user decides: behavior, scope, names, wording, and trade-offs. Look up yourself what the code,
  the docs, or a command can answer.

## Scope discipline

- If you discover something unrelated that needs fixing, mention it to the user. Leave it unless the fix takes one small
  edit in a file you already change.
- Do not add features, refactor surrounding code, or make unrequested improvements.
- A request for a review, a plan, an analysis, or a discussion stays read-only until the user allows changes.
- Changes you did not make may belong to another agent or contributor working in parallel. Do not revert, stash, clean,
  or overwrite them. Keep working beside them, and ask the user only when your change overwrites or contradicts one.

## Verification and tests

Do not run verification broader than the change. Run no full test suite, build, scan, or Docker check unless the user
asks for it or the checks of the repository include it.

Write tests when the user asks or a check requires them. Fix each test that your change breaks.

Never pipe a test, a check, or a CI command into `head`, `tail`, or `grep` to read its result. A pipe reports the exit
code of its last command, so a failed run looks like a pass, and `head` can stop the run early. Write the output to a
file, read the exit code, then read the file.

## Rules and checks

Run `gspot explain <check>` to see what a check looks for and how to fix its findings. When a rule and a check conflict,
make the code pass the check, and name both to the user. A help line that makes a setting weaker still needs the
user's agreement.

## No defensive logic

Do not add guards, fallbacks, retries, defaults, or wrappers for states the public interface rules out. Handle known
failure modes where they can occur: user input, network calls, persistence, permissions, and external services. Trust an
internal invariant once the public interface establishes it. When you cannot tell whether a state can occur, trace the
code. Do not add a guard for it.

## Abstractions

Keep one implementation of each concept, and one copy of each table of values, in the module that uses it. Extract
shared code only when two or more callers need the same behavior now.

- Inline a function of `2` statements or fewer that has at most one caller, and
  delete it. When one must stay, such as a method that an interface requires, ask the user. Then suppress it with the reason,
  or run `gspot ignore` for a gspot check.
- Keep a function with one caller when it names a step and holds more statements than that limit. Do not split code into
  functions only to pass a size or complexity limit. Split it by the steps it performs.
- An abstraction that gains flags, modes, or caller-specific branches needs a different design. Do not combine loosely
  related behaviors in a function behind a parameter that picks one.
- A function takes no positional boolean.
- Prefer plain functions, values, and explicit data flow to classes, factories, strategies, and inheritance.

## No backward compatibility

Never introduce compatibility layers, wrapper functions, re-exports for renamed symbols, deprecated-but-kept code, or
other backward-compatible scaffolding. A published API follows the deprecation policy its project declares instead.

This covers code and APIs inside the repository. Stored data and wire formats follow the contract rule in Thinking
before coding.

## Structure

- Put private functions above the public function that calls them.
