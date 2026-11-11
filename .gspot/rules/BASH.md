# Bash

Read this rule when you write or change a shell script.

## Bash scope

Use Bash to run commands and wire tools together. Parsing, data structures, long-running work, and typed contracts
belong in application code.

## Deprecated and forbidden syntax

Do not use `function` or `&>`. Use `name() { ...; }` and explicit redirections instead. `trap ERR` does not provide
general error handling. Check failure where it matters, and reserve traps for cleanup that can run safely on the
relevant exit path.

## Options

Do not rely on `errexit` for control flow. It does not stop the script inside conditionals, pipelines, command
substitutions, subshells, and some functions. Check the status of `cd`, `rm`, builds, publishing, uploads, and
destructive commands explicitly. Do not toggle options around a small operation without restoring the prior state. Keep
`set -x` out of committed code.

Put explicit checks inside a function called in `if`, `while`, `&&`, or `||`, because `errexit` does not stop it there.

Process substitution hides producer failures. When the producer status matters, write to a checked temporary file, use
`PIPESTATUS`, or call it separately. Under `pipefail`, short readers such as `head` and `grep -q` can make the producer
receive SIGPIPE and fail the pipeline. Consume input predictably or handle the known status. Under `nounset`, use
`${name:-}` where the public interface accepts an unset variable and `${name:?message}` for a required value at a clear
boundary. Use `${1:-}` where callers can omit an argument.

## Functions

Declare function-local variables with `local`. Preserve the documented status contract: a predicate may return 1 for
false, distinct from an execution error. Delete a function that no script calls.

## Variables and constants

Mark constants `readonly` immediately after assignment, and `export` only what child processes need. Do not overwrite
`PATH`, `HOME`, `IFS`, `CDPATH`, `SHELL`, `PWD`, or `BASH_ENV` without a clear need. Never export `CDPATH`.

Compute a folder constant with `CDPATH='' cd -- <path> && pwd -P`.

## Arrays and argument lists

Command arguments live in arrays, expanded with `"${array[@]}"` and never populated from raw `$(...)`. Read lines with a
`while read` loop or `readarray`, and filenames from `NUL`-delimited streams. `readarray` needs Bash 4, and macOS ships
`/bin/bash` 3.2.

## Conditionals and arithmetic

`[[ ... ]]` holds string, pattern, and file tests. `<` and `>` inside `[[ ... ]]` compare strings. Compare numbers in
`(( ... ))` after you validate them.

Arithmetic uses `$(( ... ))` and `(( ... ))`. `(( i++ ))` returns false when the expression equals zero, so under
`errexit` increment with `retry_count=$(( retry_count + 1 ))`. Untrusted strings never enter `(( ... ))`, `$(( ... ))`,
`[[ value -gt n ]]`, array indices, or arithmetic `for` expressions: validate with a pattern first. `10#${value}`
converts unsigned base-10 strings.

## Loops and delimited data

Iterate arguments with `for arg in "$@"; do`, globs directly, and files with
`while IFS= read -r line || [[ -n ${line} ]]; do ... done <"${file}"`, which keeps the last unterminated line. A pipe
into `while` runs the loop in a subshell, so variables set inside it vanish; read from a redirected file, as the example
shows. Counter loops use `for (( index = 0; index < count; index++ ))`, not `seq`.

```bash
root_folder="$(CDPATH='' cd -- "${1:?Root folder is required}" && pwd -P)" || exit 1
file_list="$(mktemp)" || exit 1
trap 'rm -f -- "${file_list}"' EXIT
find "${root_folder}" -type f -print0 >"${file_list}" || exit 1

while IFS= LC_ALL=C read -r -d '' file; do
    printf 'file: %q\n' "${file}"
done <"${file_list}"
```

Set `IFS` only with `local IFS` inside a function or in a subshell. `read` treats `IFS` as a terminator, so a controlled
delimited line keeps its trailing empty field only with an appended delimiter. Parse general CSV in application code
with a real parser, never with `IFS=, read`.

## Paths, globs, and file names

Filenames can hold spaces, newlines, quotes, brackets, and leading dashes. Never assume the current folder; compute it,
and check `cd` explicitly. A broken symlink needs `-L` beside `-e` when existence matters, and a basename pattern reads
`"${path##*/}"`. Handle the no-match glob deliberately, either with `[[ -e ${file} ]] || continue` or with `nullglob`
scoped to a subshell.

## Pipelines and redirection

Read `PIPESTATUS` immediately when individual statuses matter. Never close a standard descriptor as a shortcut for
`/dev/null`. Parallel `xargs` jobs do not produce ordered, unmixed output: write per-job files and combine them, or use
a tool that serializes. Check a command directly or capture its status in a named variable.

## Output, logging, and errors

Write messages with `printf`, not `echo`. Return or exit with the intended status: printing an error does not make a
command fail.

Do not let a final message, a false condition, or an optional cleanup check set the exit status.

## Naming

Do not name scripts or functions after shell builtins or common commands.
