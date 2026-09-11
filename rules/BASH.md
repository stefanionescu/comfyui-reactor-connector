# Working on Bash

These rules apply to Git hooks, mise task files, committed Bash scripts, sourced
libraries, and CI steps that use Bash in this single-project repository.

Use [NAMING.md](NAMING.md) for names and [GENERAL.md](GENERAL.md) for working rules.
Use the existing commands for the affected scripts.

## Contents

Choose the section that matches the work you are doing:

| Task                                 | Sections                                                                                                                                                                              |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Choose where script logic belongs    | [Use Bash for command tasks](#use-bash-for-command-tasks), [when to use Bash](#when-to-use-bash)                                                                                      |
| Create a hook, task, or script       | [File types and invocation](#file-types-and-invocation), [script structure](#script-structure), [functions](#functions)                                                               |
| Handle failures                      | [Shell options](#shell-options), [output and errors](#output-logging-and-errors), [pipelines](#pipelines-and-redirection)                                                             |
| Pass arguments and read input        | [Quoting](#quoting-and-expansion), [arrays](#arrays-and-argument-lists), [loops](#loops-and-input), [delimiters](#delimited-data-and-ifs)                                             |
| Compare or calculate values          | [Conditionals](#conditionals), [arithmetic](#arithmetic), [variables](#variables-and-constants)                                                                                       |
| Read or replace files                | [Paths](#paths-globs-and-file-names), [command substitution](#command-substitution), [temporary files](#temporary-files-locks-and-cleanup)                                            |
| Call tools and manage processes      | [Calling commands](#calling-commands), [processes and privileges](#process-management-and-privilege-boundaries), [network commands](#network-commands)                                |
| Handle sensitive or structured input | [Structured data](#text-json-and-structured-data), [secrets](#secrets-and-environment), [security rules](#security-rules)                                                             |
| Support developer machines and CI    | [Portability](#portability-rules), [CI scripts](#ci-scripts)                                                                                                                          |
| Review or repair a script            | [Comments](#comments-and-documentation), [linting](#linting-and-formatting), [verification](#verification-scope), [debugging](#debugging-bash), [review checklist](#review-checklist) |

## Shell terms used here

- A **shebang** is the first line, such as `#!/usr/bin/env bash`, that selects the interpreter.
- **Standard input** (`stdin`) supplies input to a command. **Standard output** (`stdout`)
  carries its result. **Standard error** (`stderr`) carries errors and diagnostic messages.
- An **exit status** is the number a command returns: zero means success; nonzero means failure
  or another condition defined by that command.
- **Expansion** replaces shell syntax with values. For example, `${name}` expands a variable.
- **Command substitution**, `$(command)`, captures a command's output as text.
- **Process substitution**, `<(command)`, makes a command's output available as a file-like input.
- A **glob**, such as `*.ts`, matches paths. A **NUL delimiter** separates filenames with a
  zero byte so spaces and newlines in a name do not split it.
- A **trap** runs a command when the shell receives a selected signal or exits.

## Use Bash for command tasks

Rules:

- Use Bash to call commands and pass values between them. Keep complex application
  logic in the application modules.
- Prefer small scripts with explicit inputs, explicit outputs, and clear
  failure behavior.
- Treat every path, argument, environment value, command output, and user input
  as unsafe until quoted, validated, or parsed by a structured tool.
- A script that deploys, deletes, migrates, uploads, modifies infrastructure, or
  changes secrets must be readable enough to audit line by line.
- ShellCheck warnings are design feedback. Fix them unless there is a documented
  reason not to.
- `set -euo pipefail` is not a substitute for checking dangerous commands.
- Keep mise tasks, hooks, and CI entries focused on calling the commands they need.
  Put more complex behavior in the module responsible for it.
- Keep structured-data parsing and source-code analysis in their existing owner
  modules.
- If logic is too complex for Bash, put it in its existing application or tooling
  module. Do not add another scripting runtime or put a Node program inline in a shell task.

A Git hook entry point forwards its arguments to the existing mise task:

```bash
#!/usr/bin/env bash
#
# Check the staged change without rewriting it.
# Runtime: Bash 3.2+, macOS and Linux.

set -euo pipefail

# main - Checks the staged change without rewriting it.
main() {
  local repo_root

  repo_root="$(git rev-parse --show-toplevel)" || return 1
  cd "${repo_root}" || return 1
  mise run hook:pre-commit
}

main "$@"
```

The examples below isolate shell behaviors. Apply the repository's naming,
function-size, documentation, and formatting policies when using them in a real
script; an abbreviated example does not create a policy exception.

Bad Bash:

```bash
#!/bin/sh
cd dist
for file in $(ls); do
  scp $file $HOST:$DIR
done
```

## When to use Bash

Use Bash when the script mostly:

- calls other command-line tools;
- wires together build, lint, deploy, or cleanup steps;
- validates environment and then dispatches to project commands;
- performs simple file movement, process checks, or retry loops.

Do not use Bash for:

- complex business logic;
- complex text parsing;
- JSON, YAML, XML, or HTML transformations beyond simple extraction with a
  dedicated parser;
- large mutable data structures;
- long-lived daemons;
- high-performance work;
- security-sensitive parsing of untrusted input;
- behavior that needs typed contracts.

If a workflow needs nested maps, large arrays, complex validation, or domain
rules, implement that behavior in the owning application or quality module.
Keep mise tasks and Git hooks focused on calling those modules and forwarding arguments.

## File types and invocation

Executable scripts:

- Must start with a Bash shebang.
- Must be executable only when directly invoked.
- Must include a purpose comment and runtime declaration after the shebang.
- Must define exactly one `main` function and end with `main "$@"`.
- Must keep every other function private with a leading underscore.
- Follow [`NAMING.md`](NAMING.md) for shell filename and extension rules.

Libraries:

- Keep library files non-executable.
- Must be safe to `source` without running main program behavior.
- Follow [`NAMING.md`](NAMING.md) for shell library filename rules.
- Must not define or invoke `main`.
- Must not call `exit` or change the caller's shell options.
- Must not execute workflow logic while loading.

Shebang rules:

```bash
#!/usr/bin/env bash
```

Use this for repository scripts that may run on macOS, Linux, CI, or developer
machines.

Repository scripts target Bash 3.2. Do not use `mapfile`, `readarray`,
associative arrays, case-conversion expansion, `coproc`, or `wait -n`.

```bash
#!/bin/bash
```

Use this only when the target runtime deliberately relies on system Bash at that
path, such as a controlled Linux remote host.

Do not use:

```bash
#!/bin/sh
#!/usr/bin/env sh
```

unless the file is intentionally POSIX `sh`. If a file uses `sh`, this Bash
guide does not apply except for general quoting and security principles.

Do not set the set-user-ID (SUID) or set-group-ID (SGID) permission bits on
shell scripts. Use `sudo` or a platform-specific privilege boundary instead.

## File encoding and line endings

Rules:

- Store Bash files as UTF-8 without a byte-order mark (BOM).
- Use LF line endings. Do not commit CRLF shell scripts.
- Do not put binary data in shell variables. Bash variables cannot contain NUL.
- Do not use command substitution for content where exact trailing newlines
  matter.
- Keep generated shell snippets free of invisible bytes before the
  shebang.

If a script has Windows line endings, convert it before review:

```bash
tr -d '\r' < "${script}" > "${script}.tmp"
mv -- "${script}.tmp" "${script}"
```

A file that starts with a BOM before `#!` may fail to execute as a script. Treat
that the same as a broken shebang.

## Forbidden syntax

Use the explicit Bash forms in this section.

Forbidden forms:

- Arithmetic expansion: do not use `$[ ... ]`. Use `$(( ... ))`.
- Command substitution: do not use backtick substitution. Use `$(...)`.
- Arithmetic command: do not use `let`. Use `(( ... ))` or assignment with
  `$(( ... ))`.
- Declarations: do not use `typeset`. Use `local`, `declare`, `readonly`, or
  `export` according to the value's real scope.
- Function definitions: do not use the `function` keyword, including
  `function name()`, `function name() { ... }`, or `function name { ... }`.
  Use `name() { ...; }`.
- Compact loop syntax: do not use `for arg; { ...; }`. Use
  `for arg in "$@"; do ... done`.
- Combined redirection shortcuts: do not use `&>file` or `>&file`. Use
  `>file 2>&1`.
- Combined pipeline shorthand: do not use `cmd |& other`. Use
  `cmd 2>&1 | other`.
- Compound test syntax: do not use `test -a`, `test -o`, `[ ... -a ... ]`,
  `[ ... -o ... ]`, or grouping operators inside `[ ... ]`. Use `[[ ... ]]`,
  explicit `if` branches, or `case`.
- `ERR` traps: do not use `trap ERR` as general error handling. Use explicit
  status checks where failure matters, and reserve traps for cleanup that is
  safe to run on the relevant exit path.
- `eval`: do not use `eval` to turn strings into code. Use arrays,
  direct validation, `case`, or fixed dispatch tables.

Bad:

```bash
function run() {
  if [ "$mode" = deploy -o "$mode" = rollback ]; then
    let count=count+1
    command &>"$log_file"
  fi
}
```

Good:

```bash
# _deploy - Runs the selected deployment operation.
_deploy() {
  if [[ "${mode}" == 'deploy' || "${mode}" == 'rollback' ]]; then
    count=$(( count + 1 ))
    command >"${log_file}" 2>&1
  fi
}
```

## Script structure

Use this order. Omit sections that the script does not need.

1. Shebang.
1. File header comment.
1. Shell options.
1. `source` statements.
1. Constants and exported configuration.
1. Functions.
1. `main`.
1. `main "$@"` as the last non-comment line.

Example:

```bash
#!/usr/bin/env bash
#
# Build and publish the report bundle.
# Runtime: Bash 3.2+, macOS and Linux.

set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)" || exit 1
readonly SCRIPT_DIR

REPO_ROOT="$(CDPATH= cd -- "${SCRIPT_DIR}/../.." && pwd -P)" || exit 1
readonly REPO_ROOT

# shellcheck source=lib/log.sh
source "${SCRIPT_DIR}/lib/log.sh"

# _require_report_dir - Validates that the report directory exists.
# Arguments:
#   Report directory path.
# Returns:
#   0 when the directory exists, non-zero otherwise.
_require_report_dir() {
  local report_dir="$1"

  [[ -d "${report_dir}" ]]
}

# main - Builds and publishes the report bundle.
main() {
  local report_dir="${1:-}"

  _require_report_dir "${report_dir}" || {
    printf 'Error: report directory is required\n' >&2
    return 1
  }

  tar -czf report.tar.gz -C "${report_dir}" .
}

main "$@"
```

Rules:

- Do not put executable program flow between function definitions.
- Do not mutate global state while loading a library. Configuration libraries
  may declare the readonly values allowed by the configured shell policy.
- Source files with explicit paths based on `BASH_SOURCE[0]`, not the caller's
  current directory.
- Put an exact `# shellcheck source=...` repository path immediately before each
  `source` statement.
- Libraries may define constants, functions, and validation helpers. Entrypoints
  own argument parsing and `main`.
- Executable scripts must finish with a meaningful program status. Do not let a
  final diagnostic command, false condition, or optional cleanup check become
  the script status by accident.
- Use explicit `exit 0` only when the final command's status is not the program
  result and success has already been established.

## Shell options

Check what each shell option changes before enabling it:

- `set -e` (`errexit`) exits after some command failures, with exceptions described below.
- `set -u` (`nounset`) treats an unset variable as an error when expanded.
- `set -o pipefail` makes a pipeline fail if one of its commands fails.

Common entrypoint default:

```bash
set -euo pipefail
```

Rules:

- Use `set -euo pipefail` only when the script is written and reviewed for those
  behaviors.
- Do not rely on `errexit` for critical safety. Explicitly check `cd`, `rm`,
  deploy, migration, upload, sync, and destructive commands.
- Do not use `errexit` as the only way to handle failures. It has exceptions in
  conditionals, pipelines, command substitutions, subshells, and functions.
- Do not enable or disable `set` options in sourced libraries. Isolate a local
  `shopt` change in a subshell so it cannot change the caller.
- Do not toggle options globally around a small operation without restoring the
  prior state.
- Do not change `IFS` globally to enable a so-called strict mode. Set `IFS` locally
  only where reading or joining data requires it.
- Avoid `set -x` in committed code. If temporary tracing is necessary, keep it
  local and prevent it from printing secrets.

`errexit` pitfalls:

```bash
# Bad: this can keep running when called in a conditional context.
cleanup() {
  cd "${1}"
  rm -rf ./*
}

cleanup "${target}" || exit 1
```

Functions, subshells, and groups behave differently when their caller checks
their status. Write explicit checks inside a function that can run in `if`,
`while`, `&&`, or `||`. Do not assume that `errexit` will stop at the first
failing command.

```bash
# Good: failure is explicit where it matters.
# _cleanup - Removes files from the validated target.
_cleanup() {
  local target="$1"

  cd -- "${target}" || return 1
  runtime_remove_owned_path "${target}"
}
```

Command substitution inside another command's arguments does not reliably stop
the script:

```bash
# Bad: printf can succeed even when generate_version fails.
printf 'version=%s\n' "$(generate_version)"
```

```bash
# Good: the producer status is checked before the value is consumed.
version="$(generate_version)" || return 1
printf 'version=%s\n' "${version}"
```

`local`, `export`, `readonly`, and `declare` can mask command-substitution
failures. Declare first, then assign and check the command status.

Process substitution hides producer failures from the consumer's status:

```bash
# Risky: sort can succeed even when generate_lines fails.
sort < <(generate_lines)
```

When the producer matters, write to a checked temporary file, use a checked
pipeline with `PIPESTATUS`, or call the producer separately.

`pipefail` pitfalls:

```bash
# Risky with pipefail: grep -q can exit early and make the producer see SIGPIPE.
if produce_large_output | grep -q 'ready'; then
  printf 'ready\n'
fi
```

Prefer a command that consumes input predictably, or handle the known status
explicitly. Short readers such as `head`, `grep -q`, and commands that stop
after the first match can create false failures under `pipefail`.

`nounset` rules:

- Do not enable `set -u` blindly in an existing script. The script must be
  reviewed for unset positional parameters, optional environment variables, and
  arrays.
- Put configured default values in configuration owners. Outside those owners,
  use only the default expansions allowed by the configured shell policy.
- Do not use unguarded `${1}` when an argument may be missing. Use `${1:-}`.
- Be careful with arrays under `set -u`; check lengths before indexing.
- Handle empty arrays correctly under the configured Bash version and `set -u`.

## Output, logging, and errors

`stdout` is for script output that another command may consume. `stderr` is for
status, warnings, prompts, and errors.

When several callers need the same logging behavior, a sourced function can
format it:

```bash
# report_log - Prints a report message to stderr.
# Globals:
#   None.
# Arguments:
#   Message text.
# Outputs:
#   Writes the message to stderr.
# Returns:
#   0 when `printf` succeeds, non-zero otherwise.
report_log() {
  printf '%s\n' "$*" >&2
}
```

Rules:

- Use `printf`, not `echo`, for predictable output.
- Error messages go to `stderr`.
- Machine-readable output goes to `stdout` and excludes progress text.
- Deployment scripts include enough public context to diagnose the failing
  operation.
- Long-running, cron, deployment, and multi-host scripts use timestamped
  diagnostics with stable fields instead of prose-only progress.
- Include the public operation, a non-sensitive target label, the attempt
  number, and the status when those fields exist. Do not expose internal script
  or function names.
- Do not print secrets, tokens, cookies, connection strings, `.env` content, or
  provider payloads.
- Do not use colored output in CI unless the runner and logs support it.
- Do not make parsers depend on human log text.
- Use `logger` or journald only in Linux-only scripts that validate the command
  is available and document the runtime dependency.

Good:

```bash
printf 'Deploying %s to %s\n' "${target_name}" "${environment}" >&2
```

Structured diagnostic:

```bash
# deploy_log_status - Prints a timestamped deployment status to stderr.
# Globals:
#   None.
# Arguments:
#   Public operation name.
#   Target name.
#   Status label.
# Outputs:
#   Writes the status fields to stderr.
# Returns:
#   0 when the status is written, non-zero otherwise.
deploy_log_status() {
  local operation_name="$1"
  local target_name="$2"
  local status_label="$3"
  local timestamp

  timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')" || return 1
  printf 'Timestamp=%s operation=%s target=%s status=%s\n' \
    "${timestamp}" "${operation_name}" "${target_name}" "${status_label}" >&2
}
```

Bad:

```bash
echo "Deploying with token $TOKEN"
```

## Literal text and here documents

Rules:

- Use here documents only with commands that read from `stdin`.
- Do not use `echo <<EOF`; `echo` does not read the here document body.
- Quote the here-document delimiter when the body must remain literal.
- Use unquoted delimiters only when parameter, command, or arithmetic expansion
  is intended.
- Use `<<-` only when tab-stripping is deliberate. The body must be indented
  with tabs, not spaces.
- Use `printf`, not `echo`, for short literal output.
- Use `$HOME` for home-relative paths in quoted strings. Quoted `~` does not
  expand.
- In interactive shell snippets, quote `!` or disable history expansion with
  `set +H`. Scripts do not use interactive history expansion.

Good:

```bash
cat <<'EOF'
This text is literal.
$HOME is not expanded here.
EOF
```

Good with expansion:

```bash
cat <<EOF
Deploying ${target_name} to ${environment}.
EOF
```

Bad:

```bash
echo <<EOF
This body is ignored by echo.
EOF
```

## Comments and documentation

For a substantive Bash script, put a short purpose comment after the shebang.
Keep existing brief hook and mise entry points consistent with the project policy:

```bash
#!/usr/bin/env bash
#
# Sync generated storage assets to the configured project.
# Runtime: Bash 3.2+, macOS and Linux.
```

Document every function immediately above its declaration. Use the required
`# function_name - description` form. `main` needs this summary but does not
need the full contract block:

```bash
# _normalize_env_name - Converts an environment alias to the configured name.
_normalize_env_name() {
  ...
}
```

For sourced public functions and risky functions other than `main`,
include the full header:

```bash
# storage_upload_asset - Uploads one asset to remote storage.
# Globals:
#   STORAGE_API_URL
#   STORAGE_API_KEY
# Arguments:
#   Bucket name.
#   Local file path.
# Outputs:
#   Writes progress to stderr.
# Returns:
#   0 when upload succeeds, non-zero otherwise.
storage_upload_asset() {
  ...
}
```

Rules:

- Document behavior, not history.
- Comments explain why a shell pattern is needed when the code is not obvious.
- Do not comment every line.
- TODOs must include `TODO(identifier):`.
- Suppressions must explain the real constraint and stay as narrow as
  possible.

## Formatting

Rules:

- Let the owning formatter control indentation, line wrapping, blank lines, and
  alignment.
- Do not hand-format scripts in a way that fights the formatter.
- Prefer readable command structure over dense semicolon chains.
- Follow [`NAMING.md`](NAMING.md) for function, variable, constant, and
  environment variable names.

Control flow:

```bash
for arg in "$@"; do
  if [[ -n "${arg}" ]]; then
    printf '%s\n' "${arg}"
  else
    printf 'Error: empty argument\n' >&2
  fi
done
```

Case statements:

```bash
case "${environment}" in
  staging)
    deploy_staging
    ;;
  production)
    deploy_production
    ;;
  *)
    printf 'Error: unknown environment: %s\n' "${environment}" >&2
    return 1
    ;;
esac
```

Short option parsing may keep simple branches on one line:

```bash
while getopts ':f:v' flag; do
  case "${flag}" in
    f) file="${OPTARG}" ;;
    v) verbose='true' ;;
    *) usage >&2; exit 2 ;;
  esac
done
```

Long pipelines:

```bash
generate_report \
  | jq -r '.items[] | .name' \
  | sort \
  | uniq
```

## Naming

Bash naming rules live in [`NAMING.md`](NAMING.md). Follow that file for shell
file stems, script extensions, function names, variables, constants, and
environment variables. Also follow it for loop variables, package-like function
prefixes, and names that would collide with shell builtins or common commands.

Automated naming checks are authoritative when they exist for the touched
scope.

## Functions

Rules:

- Use `name() { ... }` consistently for new code.
- Do not write `function name()`, `function name() { ... }`, or
  `function name { ... }`.
- Keep functions small and single-purpose.
- Declare function-local variables with `local`.
- Separate `local` declaration from command substitution assignment when the
  exit code matters.
- Return status codes with `return`. Print data to `stdout` only when the function
  is designed as a value-producing command.
- Do not make a function both print data and log progress to `stdout`.

Good:

```bash
# _current_branch - Prints the current Git branch.
# Outputs:
#   Writes the branch name to stdout.
_current_branch() {
  local branch

  branch="$(git rev-parse --abbrev-ref HEAD)" || return 1
  printf '%s\n' "${branch}"
}
```

Bad:

```bash
current_branch() {
  local branch="$(git rev-parse --abbrev-ref HEAD)"
  echo "branch is $branch"
}
```

Use `main` for every executable entry point. Executable files expose only
`main`; prefix every other function with `_`. Follow the configured shell file
and function limits. Every function needs a `# function_name - description`
summary. Sourced public functions and risky functions other than `main` also
need the full contract block shown above.

When an entry point needs several steps, use this structure:

```bash
# main - Builds the requested report.
main() {
  _parse_args "$@"
  _build_report
}

main "$@"
```

Libraries must not call `main`.

## Variables and constants

Rules:

- Quote variable expansions unless a specific shell mechanism requires unquoted
  expansion.
- Prefer `${name}` over `$name` for normal variables.
- Do not brace single-character positional or shell-special parameters unless it
  avoids confusion.
- Positional parameters above 9 must be braced. Use `${10}`, not `$10`.
- Use `readonly` for constants immediately after assignment.
- Use `export` only for variables that child processes need.
- Do not overwrite important environment variables casually, especially `PATH`,
  `HOME`, `IFS`, `CDPATH`, `SHELL`, `PWD`, or `BASH_ENV`.
- Do not export `CDPATH`.
- Do not put spaces around `=`.
- Use `$HOME`, not quoted `~`, inside paths.
- Assign a home-relative value before exporting it, or use `$HOME`.
- Quote array elements passed to `unset`, and prefer `unset -v`.

Good:

```bash
PROJECT_ROOT="$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd -P)" || exit 1
readonly PROJECT_ROOT
export PROJECT_ROOT

tool_home="${HOME%/}/.tool"
export tool_home

unset -v 'files[0]'
```

Bad:

```bash
PROJECT_ROOT = $(pwd)
export CDPATH=.:~/project
export tool_home=~/tool
unset files[0]
```

When assigning from commands:

```bash
local output
output="$(some_command)" || return 1
```

Separate `local`, `declare`, `readonly`, and `export` from command substitution
when the command status matters. These declarations can report their own status
instead of the command substitution's status:

```bash
local output="$(some_command)"
declare output="$(some_command)"
readonly output="$(some_command)"
export output="$(some_command)"
```

The exit code is the `local` builtin's status, not reliably the command
substitution status.

## Quoting and expansion

Rules:

- Always quote variable expansions, command substitutions, and strings with
  spaces or shell metacharacters.
- Use `"$@"` when forwarding arguments.
- Do not use `$*` except when intentionally joining arguments into one string.
- Prefer single quotes for literal strings with no expansion.
- Prefer double quotes when expansion is required.
- Do not use unquoted command substitution output as an argument list.
- Do not depend on word splitting for data parsing.
- Do not use `eval`. Use arrays, direct validation, explicit `case` branches,
  or fixed dispatch tables.
- Do not use aliases in scripts. Use functions.
- Do not rely on backslash-escaped words for readability when quotes work.

Good:

```bash
cp -- "${source_file}" "${target_dir}/"
printf '%s\n' "${message}"
command --flag "${value}" "$@"
```

Bad:

```bash
cp $source_file $target_dir
echo $message
command $flags $*
```

Quoted command substitution:

```bash
version="$(node --version)"
```

Nested quoting is normal:

```bash
script_dir="$(CDPATH= cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
```

Use parameter expansion instead of external tools for simple string operations:

```bash
filename="archive.tar.gz"
base="${filename%.tar.gz}"
```

## Arrays and argument lists

Use arrays for command arguments.

Good:

```bash
declare -a rsync_args
rsync_args=(
  -az
  --delete
  --exclude '.DS_Store'
)

rsync "${rsync_args[@]}" "${source_dir}/" "${target_dir}/"
```

Bad:

```bash
rsync_args='-az --delete --exclude ".DS_Store"'
rsync ${rsync_args} "${source_dir}/" "${target_dir}/"
```

Rules:

- Expand arrays with `"${array[@]}"`.
- Do not populate arrays with raw `$(...)`.
- Use a `while read` loop for line-based input.
- Do not simulate nested maps or records with shell arrays. Use the module that
  owns that structured data.

This example assumes paths cannot contain newlines. For arbitrary filenames,
use the NUL-delimited example below. Also check the producer status when its
failure matters:

```bash
while IFS= read -r file; do
  files+=("${file}")
done < <(find . -type f -name '*.sql' -print)
```

For filenames, prefer NUL delimiters:

```bash
while IFS= LC_ALL=C read -r -d '' file; do
  files+=("${file}")
done < <(find . -type f -name '*.sql' -print0)
```

## Conditionals

Use `[[ ... ]]` for Bash conditionals:

```bash
if [[ -f "${config_file}" ]]; then
  _read_config "${config_file}"
fi
```

Rules:

- Prefer `[[ ... ]]` over `[ ... ]` in Bash scripts.
- Do not use `test -a`, `test -o`, `[ ... -a ... ]`, `[ ... -o ... ]`, or
  grouping operators inside `[ ... ]`. Use `[[ ... ]]`, explicit `if`
  branches, or `case`.
- Use `==` for string equality.
- Quote the right-hand side when string equality is intended and the value may
  contain glob characters.
- Leave the right-hand side unquoted only when pattern matching is intended.
- Store regular expressions in variables and use them unquoted with `=~`.
- Use `-z` and `-n` for empty and non-empty string checks.
- Use `(( ... ))` for trusted numeric comparisons.
- Validate untrusted numbers before arithmetic evaluation.

String equality:

```bash
if [[ "${actual}" == "${expected}" ]]; then
  printf 'match\n'
fi
```

Pattern matching:

```bash
if [[ "${file}" == *.sql ]]; then
  lint_sql "${file}"
fi
```

Regular expressions:

```bash
readonly version_re='^[0-9]+\.[0-9]+\.[0-9]+$'

if [[ "${version}" =~ ${version_re} ]]; then
  printf 'valid version\n'
fi
```

Do not write:

```bash
if [ $name = value ]; then
  ...
fi
```

Do not use `cmd1 && cmd2 || cmd3` as an `if/else` replacement when `cmd2` can
fail:

```bash
if cmd1; then
  cmd2
else
  cmd3
fi
```

## Arithmetic

Rules:

- Use `$(( ... ))` for arithmetic expansion.
- Use `(( ... ))` for trusted arithmetic comparisons and assignments.
- Do not use `expr`, `$[ ... ]`, or `let`.
- Do not use `<` or `>` inside `[[ ... ]]` for numeric comparisons.
- Validate untrusted numeric input before arithmetic contexts.
- Be careful with `(( i++ ))` under `errexit`; it returns false when the
  expression evaluates to zero.
- Avoid array subscripts inside arithmetic contexts unless both the array name
  and index are trusted.
- Do not put untrusted strings into `(( ... ))`, `$(( ... ))`,
  `[[ value -gt n ]]`, array indices, or arithmetic `for` expressions.
- Keep untrusted associative-array keys out of arithmetic expressions.
- Convert base-10 strings with care. `10#${value}` only works for unsigned
  numbers.
- Call `date` one time when multiple fields must describe the same instant.
- Compute redirection paths before a command if the path expression mutates a
  variable.

Good:

```bash
if (( retry_count < max_retries )); then
  (( retry_count += 1 ))
fi
```

Safer increment under `errexit`:

```bash
retry_count=$(( retry_count + 1 ))
```

Validate external input:

```bash
if [[ ! "${port}" =~ ^[0-9]+$ ]]; then
  printf 'Error: port must be numeric\n' >&2
  return 1
fi

if (( port < 1 || port > 65535 )); then
  printf 'Error: port is out of range\n' >&2
  return 1
fi
```

Avoid:

```bash
if [[ "${port}" > 1024 ]]; then
  ...
fi
```

That compares text order, not numeric value. Use `(( ... ))` for numbers.

Safer signed base-10 conversion:

```bash
if [[ "${value}" =~ ^[+-]?[0-9]+$ ]]; then
  value_base10=$(( ${value%%[!+-]*}10#${value#[-+]} ))
fi
```

Safer redirection target:

```bash
output_file="report$(( index + 1 )).txt"
index=$(( index + 1 ))
generate_report >"${output_file}"
```

Do not do:

```bash
generate_report >"report$(( index++ )).txt"
```

## Loops and input

Rules:

- Iterate over arguments with `for arg in "$@"; do`.
- Do not use compact loop forms such as `for arg; { ...; }`.
- Iterate over globs directly, not over `ls`.
- Read files with `while IFS= read -r line; do ... done < file`.
- Do not use `for line in $(cat file)`.
- Avoid piping into `while` when variables set inside the loop must survive.
- Use process substitution for current-shell loops.
- Use NUL-delimited streams for filenames.
- Use `read` with a bare variable name, not `$variable`.
- Do not use a here-string containing command substitution as loop input.

Good line reading:

```bash
while IFS= read -r line; do
  _parse_line "${line}"
done < "${input_file}"
```

Good command output loop:

```bash
while IFS= read -r line; do
  _parse_line "${line}"
done < <(generate_lines)
```

Avoid this loop input form:

```bash
while IFS= read -r line; do
  _parse_line "${line}"
done <<< "$(generate_lines)"
```

It collects all output first, strips trailing newlines, discards NUL bytes, and
adds a final newline.

Good filename loop:

```bash
while IFS= LC_ALL=C read -r -d '' file; do
  _validate_file "${file}"
done < <(find "${root_dir}" -type f -print0)
```

Bad:

```bash
for file in $(find "${root_dir}" -type f); do
  _validate_file "${file}"
done
```

Counter loop:

```bash
for (( index = 0; index < count; index++ )); do
  _evaluate_case "${index}"
done
```

Do not use `seq` for simple Bash counters.

## Delimited data and IFS

Rules:

- Use `IFS= read -r` for line input to prevent trimming and backslash handling.
- Use `IFS= LC_ALL=C read -r -d ''` for NUL-delimited filename streams.
- Do not save and restore `IFS` with `old_ifs="${IFS}"`; that loses the
  distinction between unset and empty.
- Prefer function-local `IFS` or a subshell when a temporary separator is
  needed.
- Do not parse general CSV with `IFS=, read ...`; use an owned module with a real
  CSV parser.
- If a simple delimiter format is truly controlled, remember that `read` treats
  `IFS` as a terminator. A trailing empty field is discarded unless you account
  for it.
- Do not populate arrays from raw command substitution.

Good local `IFS`:

```bash
# _join_path_parts - Prints path parts joined by slashes.
_join_path_parts() {
  local IFS='/'
  printf '%s\n' "$*"
}
```

Controlled trailing field:

```bash
input='name,value,'
IFS=, read -r -a fields <<< "${input},"
```

Bad:

```bash
old_ifs="${IFS}"
IFS=,
read -r first second rest <<< "${line}"
IFS="${old_ifs}"
```

Command output into arrays:

```bash
declare -a hosts
while IFS= read -r host; do
  hosts+=("${host}")
done < <(aws_command_that_prints_one_host_per_line)
```

## Paths, globs, and file names

Rules:

- Quote paths.
- Use `--` before path arguments when a command supports it.
- Prefer globs with explicit path prefixes such as `./*.mp3`.
- Do not parse `ls`.
- Do not filter filenames with `grep`; use globs or `[[ ... == pattern ]]`.
- Handle no-match glob behavior deliberately.
- Do not assume filenames cannot contain spaces, newlines, quotes, brackets, or
  leading dashes.
- Do not assume the current directory. Set or compute it.
- Check `cd` explicitly.
- Test broken symlinks with `-e` or `-L` when existence matters.
- Match path basenames deliberately when using globs against paths that include
  `./`.
- Do not use `grep` to decide whether a path has an extension.

Good:

```bash
for file in ./*.sql; do
  [[ -e "${file}" ]] || continue
  sql_lint_file "${file}"
done
```

Broken symlink-aware conditional:

```bash
if [[ -e "${path}" || -L "${path}" ]]; then
  _validate_path "${path}"
fi
```

Basename pattern conditional:

```bash
if [[ "${path##*/}" == *.* ]]; then
  _validate_extension_file "${path}"
fi
```

With `nullglob`, scope the option:

```bash
# _list_sql_files - Prints SQL files in the current directory.
_list_sql_files() {
  (
    shopt -s nullglob

    declare -a files
    files=( ./*.sql )
    printf '%s\n' "${files[@]}"
  )
}
```

Prefer simpler local use when possible:

```bash
shopt -s nullglob
sql_files=( ./*.sql )
shopt -u nullglob
```

If changing directories:

```bash
if ! cd -- "${target_dir}"; then
  printf 'Error: cannot enter the target directory\n' >&2
  return 1
fi
```

When using `cd` in command substitution, clear `CDPATH`:

```bash
repo_root="$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd -P)" || return 1
```

## Command substitution

Rules:

- Use `$(...)`, not backticks.
- Quote command substitutions.
- Remember command substitution strips trailing newlines.
- Do not use command substitution to carry binary data.
- Do not use command substitution to create argument lists.
- Capture the exit status immediately when needed.
- Use `$(<file)` only when stripping trailing newlines is acceptable.

Good:

```bash
commit_sha="$(git rev-parse HEAD)" || return 1
```

Bad:

```bash
commit_sha=`git rev-parse HEAD`
for file in $(ls); do
  ...
done
```

If trailing newlines matter, avoid command substitution or preserve
them by appending a marker and removing it after capture.

The final `x` keeps command substitution from removing preceding newlines. Check
the producer first so the marker does not hide its failure:

```bash
marked_content="$(some_command || exit "$?"; printf x)" || return "$?"
content="${marked_content%x}"
```

## Pipelines and redirection

Rules:

- Split long pipelines one command per line.
- Know whether each command consumes all input before enabling `pipefail`.
- Use `PIPESTATUS` immediately if individual pipeline statuses matter.
- Redirect stdout and stderr in the correct order.
- Do not use `&>file` or `>&file`. Use `>file 2>&1` so ordering is visible.
- Do not use `cmd |& other`. Use `cmd 2>&1 | other`.
- Do not close standard file descriptors as a shortcut for `/dev/null`.
- Do not read from and write to the same file in a pipeline.
- Use temp files plus atomic rename for file replacement.
- Do not rely on parallel `xargs` jobs writing ordered, unmixed output.
- Do not use `cmd; (( ! $? )) || die`; check the command directly or capture
  the status in a named variable.

Redirect both stdout and stderr:

```bash
some_command >>"${log_file}" 2>&1
```

Do not write:

```bash
some_command 2>&1 >>"${log_file}"
```

Capture `PIPESTATUS` immediately in both branches. The `if` lets the script
inspect a failed pipeline before `set -e` would exit:

```bash
if tar -cf - ./* | (cd -- "${target_dir}" && tar -xf -); then
  statuses=( "${PIPESTATUS[@]}" )
else
  statuses=( "${PIPESTATUS[@]}" )
fi

if (( statuses[0] != 0 || statuses[1] != 0 )); then
  printf 'Error: tar copy failed\n' >&2
  return 1
fi
```

Safe file rewrite:

```bash
tmp_file="$(mktemp "${file}.XXXXXX")" || return 1
sed 's/foo/bar/g' "${file}" >"${tmp_file}" || {
  rm -f -- "${tmp_file}"
  return 1
}
mv -- "${tmp_file}" "${file}"
```

Do not do:

```bash
sed 's/foo/bar/g' "${file}" >"${file}"
```

Command status with cases:

```bash
if command_may_fail; then
  _report_success
else
  status_code=$?
  _report_failure "${status_code}"
fi
```

For parallel execution, write per-job output to separate files and combine them
after all jobs complete, or use a tool that serializes output.

## Calling commands

Rules:

- Check command availability before using non-standard tools.
- Check uncommon commands before long-running, destructive, deployment, or
  error-handling paths depend on them.
- Use fixed command names and argument arrays.
- Do not build shell commands as strings.
- Do not pass untrusted input to a shell.
- Use `command -v` for command discovery.
- `hash` is acceptable for simple PATH availability checks when no path output
  is needed.
- Use `builtin` or Bash parameter expansion instead of external commands for
  simple string and arithmetic work.
- Use `grep -q` only when early pipe closure will not cause false failures under
  `pipefail`.
- Use `--` before user-controlled positional arguments when supported.
- Pass a file directly to a command instead of using `cat file | command` unless
  concatenation or a pipeline-only interface is required.
- Do not run `su -c 'command'` without the target username. Prefer `sudo` or the
  platform's service owner tools.
- For multiple date fields, get one timestamp and derive fields from it.
- Application code that invokes commands must pass an argument array to the
  process API, not a shell string.
- Do not invoke `bash -c` or `bash -lc`. Put required shell behavior in an owned
  script or function and pass values as arguments.
- Treat remote `ssh` command strings as a last resort. Prefer a reviewed script
  copied to the host or pass fixed commands plus deliberately quoted arguments.

Command requirement helper:

```bash
# _require_command - Ensures a command exists on PATH.
# Arguments:
#   Command name.
_require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'Error: required command not found\n' >&2
    return 1
  fi
}
```

## Process management and privilege boundaries

Rules:

- Do not use `ps ... | grep name` as process control.
- Prefer service-manager commands, PID files owned by the script family,
  or `pgrep`/`pkill` with exact matching.
- Treat process names as advisory. They are not an authorization boundary.
- When starting background jobs, save each PID, `wait` for each PID, and capture
  each job's status explicitly.
- Scripts that start background work must clean up owned child processes on
  `INT`, `TERM`, and `EXIT`.
- Keep per-job output in separate files when concurrent jobs can interleave
  logs.
- Limit how many jobs run at once. When targeting many hosts or files, use an
  explicit concurrency limit.
- `sudo command > file` redirects as the current user, not as root.
- Globs in `sudo command /path/*` expand before `sudo` runs.
- Use `sudo tee` when only the file write requires elevated privileges.
- Use a fixed `sudo sh -c '...'` wrapper only when root-owned shell expansion or
  redirection is required.
- Do not put user input inside privileged shell strings.

Privileged write:

```bash
deployment_config | sudo tee /etc/service/config >/dev/null
```

Privileged glob, fixed string only:

```bash
sudo sh -c 'ls /root-owned-dir/*.conf'
```

Process lookup:

```bash
pgrep -x worker_name >/dev/null
```

Small bounded background jobs:

```bash
declare -a child_pids

# _cleanup_children - Stops child processes started by this script.
# Globals:
#   child_pids
# Arguments:
#   None.
# Outputs:
#   Writes a warning to stderr when an owned process cannot be stopped.
# Returns:
#   0 after attempting to stop each owned process.
_cleanup_children() {
  local pid

  for pid in "${child_pids[@]}"; do
    kill -0 "${pid}" >/dev/null 2>&1 || continue
    if ! kill "${pid}" >/dev/null 2>&1; then
      printf 'Warning: could not stop an owned child process\n' >&2
    fi
  done
  return 0
}

# _check_hosts - Checks remote hosts and returns nonzero on any failure.
# Arguments:
#   Small, already bounded host list to check.
_check_hosts() {
  local host
  local pid
  local status=0

  trap '_cleanup_children' EXIT
  trap '_cleanup_children; exit 130' INT
  trap '_cleanup_children; exit 143' TERM

  for host in "$@"; do
    _check_host "${host}" >"${tmp_dir}/${host}.log" 2>&1 &
    pid=$!
    child_pids+=( "${pid}" )
  done

  for pid in "${child_pids[@]}"; do
    if ! wait "${pid}"; then
      status=1
    fi
  done

  trap - EXIT INT TERM
  return "${status}"
}
```

Bad:

```bash
ps ax | grep service_name
sudo mycmd > /etc/service/config
sudo ls /root-owned-dir/*
sudo sh -c "systemctl restart ${unit_name}"
```

## Text, JSON, and structured data

Rules:

- Use Bash parameter expansion for simple string edits.
- Use an existing structured parser for JSON. Use `jq` only when the workflow
  declares it as a prerequisite; this guide does not add it to the toolchain.
- Use a project-owned parser for YAML when YAML structure matters. Treat `yq`
  as an explicit prerequisite only for workflows that already require it.
- Do not parse JSON, YAML, XML, or HTML with ad hoc
  `grep | sed | awk` unless the input is controlled and the format is simple and
  documented.
- Prefer command output modes intended for machines, such as JSON, NUL, or
  explicit format flags.
- Avoid parsing human-oriented command output such as `ls`, pretty tables,
  progress bars, or localized text.
- Quote `tr` character classes and account for locale when converting case.
- Use double quotes only when shell expansion is intended in `sed` expressions,
  and escape replacement values correctly.
- Do not parse process lists, table columns, or localized command output with
  fixed field numbers unless the producer has a machine-readable contract.

Good JSON:

```bash
endpoint_url="$(jq -r '.endpoint.url // empty' "${config_file}")" || return 1
[[ -n "${endpoint_url}" ]] || {
  printf 'Error: enter an endpoint URL\n' >&2
  return 1
}
```

Bad JSON:

```bash
endpoint_url="$(grep endpoint_url "${config_file}" | cut -d: -f2)"
```

Use `awk`, `sed`, and `perl` when they are the right text-processing tool, but
keep shell quoting clear and avoid in-place editing portability traps.

macOS and GNU `sed -i` differ. Prefer temp files for committed scripts unless a
script is platform-specific and documented.

Case conversion:

```bash
tr '[:upper:]' '[:lower:]'
LC_COLLATE=C tr A-Z a-z
```

Bad:

```bash
tr [A-Z] [a-z]
sed 's/$name/replacement/'
```

## Network commands

Rules:

- Use `curl --fail --show-error --silent --location` for downloads unless the
  endpoint requires different behavior.
- Use bounded timeouts for commands that can hang, including `ssh`, `scp`,
  `curl`, `find` over mounted filesystems, and remote service checks.
- Prefer tool-native timeout options first, such as SSH `ConnectTimeout` and
  curl `--connect-timeout` plus `--max-time`.
- Wrap with `timeout` only when GNU/coreutils availability has been validated
  for the script's runtime. macOS does not provide GNU `timeout` by default.
- Write downloads to explicit files.
- Verify checksums or signatures for executable downloads.
- Do not pipe network content into `bash` unless the source is pinned, trusted,
  and there is no safer package manager or checksum-based flow.
- Do not print response bodies that may contain secrets.
- Use retries only for known retryable network, provider, or service failures,
  with bounded attempts, delay, and attempt-count logging.
- Do not retry corrupt data, syntax errors, invalid credentials, missing
  required files, failed validation, or permission problems.
- Separate download, verification, and execution into visible steps.

Good:

```bash
# _download_file - Downloads one file within fixed time limits.
_download_file() {
  local url="$1"
  local output_file="$2"

  curl --fail --show-error --silent --location \
    --connect-timeout "${HTTP_CONNECT_TIMEOUT_SECONDS}" \
    --max-time "${HTTP_TRANSFER_TIMEOUT_SECONDS}" \
    --output "${output_file}" \
    "${url}"
}
```

Remote timeout:

```bash
ssh \
  -o "ConnectTimeout=${SSH_CONNECT_TIMEOUT_SECONDS}" \
  -o "ServerAliveInterval=${SSH_KEEPALIVE_INTERVAL_SECONDS}" \
  -o "ServerAliveCountMax=${SSH_KEEPALIVE_COUNT}" \
  -- "${host}" \
  systemctl is-active --quiet "${unit_name}"
```

Installer pattern:

```bash
tmp_dir="$(mktemp -d)" || return 1
trap 'runtime_remove_owned_path "${tmp_dir}"' RETURN

installer="${tmp_dir}/install.sh"
curl --fail --show-error --silent --location \
  --connect-timeout "${HTTP_CONNECT_TIMEOUT_SECONDS}" \
  --max-time "${HTTP_TRANSFER_TIMEOUT_SECONDS}" \
  --output "${installer}" \
  "${installer_url}"

printf '%s  %s\n' "${expected_sha256}" "${installer}" | shasum -a 256 -c -
bash "${installer}" --version "${tool_version}"
```

## Secrets and environment

Rules:

- Read secrets from the caller environment, a secret manager, or documented
  ignored env files.
- Validate required secrets at the boundary.
- Do not echo, trace, write, commit, or include secrets in command-line
  arguments when the process table could expose them.
- Prefer files or stdin for tools that accept sensitive values that way.
- Do not use `set -x` around secret handling.
- Do not write `.env` files from scripts unless the script owns that lifecycle
  and the path is ignored.
- Do not include secret values in failure messages.
- Redact secrets before logging external command output.

Required env helper:

```bash
# _require_env - Ensures an environment variable is set and non-empty.
# Arguments:
#   Environment variable name.
_require_env() {
  local name="$1"
  local value

  value="$(printenv "${name}")" || {
    printf 'Error: required environment value is missing\n' >&2
    return 1
  }
  [[ -n "${value}" ]]
}
```

Do not pass untrusted env names to `${!name}` without validation:

```bash
if [[ ! "${name}" =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
  printf 'Error: invalid env var name\n' >&2
  return 1
fi
```

## Temporary files, locks, and cleanup

Rules:

- Use `mktemp` or `mktemp -d`.
- Put temporary files under the system temp directory or an explicit project
  temp directory.
- Quote temp paths.
- Register cleanup immediately after creation.
- Use `trap` carefully and restore traps when needed.
- Do not use predictable names in `/tmp`.
- Download, copy, or generate into a temporary file first, validate it, then
  replace the destination with `mv`.
- Validate structured data with the real parser before replacing known-good
  data, such as `jq` for JSON.
- Remove failed or corrupt temporary artifacts unless the script explicitly
  documents that they are kept for inspection.
- Acquire locks atomically with `mkdir` lock directories or `noclobber`
  redirection. Do not check with `test` and then create the lock later.
- For lock directories, write the owner PID and recover stale locks explicitly.
- Do not delete broad globs under variable paths without validation.

Good:

```bash
tmp_dir="$(mktemp -d)" || return 1
trap 'runtime_remove_owned_path "${tmp_dir}"' EXIT
```

Atomic structured replacement:

```bash
tmp_file="$(mktemp "${config_file}.XXXXXX")" || return 1
trap 'rm -f "${tmp_file}"' RETURN

curl --fail --show-error --silent --location \
  --connect-timeout "${HTTP_CONNECT_TIMEOUT_SECONDS}" \
  --max-time "${HTTP_TRANSFER_TIMEOUT_SECONDS}" \
  --output "${tmp_file}" \
  "${config_url}" || return 1

jq empty "${tmp_file}" >/dev/null || return 1
mv -- "${tmp_file}" "${config_file}" || return 1
trap - RETURN
```

Race-safe lock directory:

```bash
lock_dir="${state_dir}/deploy.lock"

if ! mkdir "${lock_dir}"; then
  printf 'Error: another operation already holds the lock\n' >&2
  return 1
fi

printf '%s\n' "$$" >"${lock_dir}/pid" || {
  runtime_remove_owned_path "${lock_dir}"
  return 1
}

trap 'runtime_remove_owned_path "${lock_dir}"' EXIT
```

Function-scoped cleanup:

```bash
# _generate_in_temp_dir - Generates files in an owned temporary directory.
_generate_in_temp_dir() {
  local tmp_dir
  tmp_dir="$(mktemp -d)" || return 1
  trap 'runtime_remove_owned_path "${tmp_dir}"' RETURN

  _write_output_files "${tmp_dir}"
}
```

Recursive deletion belongs to its single configured owner. Call that owner
after validating the target:

```bash
[[ -n "${build_dir}" ]] || return 1
[[ "${build_dir}" == */build ]] || return 1
runtime_remove_owned_path "${build_dir}"
```

## CI scripts

Rules:

- Keep CI YAML thin. Put reusable logic in scripts.
- CI scripts must be non-interactive by default.
- Use explicit environment variables for CI-only behavior.
- Print the versions of important tools when diagnosing setup issues.
- Keep cache key creation deterministic.
- Do not install global tools without pinning versions.
- Do not mutate source files in verification jobs unless the job is explicitly a
  formatter or codegen job.
- Capture logs and reports to predictable artifact paths.
- Do not call broad, expensive, or mutating checks from a narrow task unless the
  owning rule file requires it.

## Security rules

Never:

- use `eval`;
- use `ERR` traps as a substitute for explicit status checks;
- build shell command strings from user input;
- invoke `bash -c` or `bash -lc`;
- parse untrusted arithmetic expressions with `(( ... ))`;
- use unsanitized values as variable names, associative array keys in arithmetic
  contexts or remote shell fragments;
- use unquoted variables in paths or arguments;
- run destructive commands against unchecked variables;
- parse `ls`;
- use `find -exec sh -c '...'` with `{}` embedded in the script string;
- use `xargs` without `-0` for filenames;
- pipe unverified network data to an interpreter;
- log secrets;
- keep debug tracing enabled around credentials.

Safe `find -exec sh -c`:

```bash
find . -type f -name '*.sql' -exec sh -c 'printf "%s\n" "$1"' sh {} \;
```

Unsafe:

```bash
find . -type f -exec sh -c 'printf "%s\n" "{}"' \;
```

Safe xargs:

```bash
find . -type f -name '*.sh' -print0 | xargs -0 shellcheck --
```

If a value must become a command argument, keep it as an argument. Do not turn it
into code.

## Portability rules

Target the actual development and deployment environments. Use the configured command versions
directly. Do not add portability wrappers, platform-selection branches, or fallback implementations
for environments the project does not support.

Keep paths quoted, use physical paths when symlinks matter, and make executable dependencies
explicit. When a required tool is missing, fix the environment setup instead of adding an alternate
implementation.

## Linting and formatting

Rules:

- Run the owning project's shell lint command only when linting is explicitly requested.
- Fix ShellCheck findings in the touched scope.
- Use the existing formatter when formatting is explicitly requested.
- Do not add broad lint suppressions.
- Every suppression needs a nearby `lint:justify` comment with a concrete reason
  and tracking reference, using the form shown below.
- Prefer changing code to satisfy ShellCheck over adding disable comments.

Expected tools:

- ShellCheck for correctness and safety.
- shfmt for formatting when the script family uses it.
- Semgrep or CodeQL only when the user explicitly requests the check.

Run requested checks from the location expected by the project.

ShellCheck suppression shape:

```bash
# shellcheck disable=SC2154
# lint:justify -- reason: variable is supplied by the deployment environment -- ticket: OPS-123
printf '%s\n' "${DEPLOY_ENVIRONMENT}"
```

Keep a suppression next to the affected command and explain the requirement that
causes the warning. Avoid suppressing a warning for the whole file.

## Verification scope

Run syntax checks, ShellCheck, shfmt, naming checks, or other verification commands only when the
user explicitly requests verification. Keep requested checks limited to the affected scripts.

Do not create Bash test suites, mock command wrappers, test-only flags, or test-only abstractions.
Never run a deployment or destructive command merely to check syntax.

## Debugging Bash

Rules:

- Start with the exact error message and the line it names. Do not guess before
  checking the command Bash actually reports.
- When debugging commands are requested, use `bash -n` and ShellCheck before tracing.
- Reduce the failing script to the smallest command block that reproduces the
  problem.
- Use `printf '%q\n'` to expose whitespace, CRLF, quoting, and invisible
  characters in suspicious values.
- Use `bash -x script.sh`, a local `set -x` block, or `set -v` only while
  diagnosing. `set -v` prints input as Bash reads it and can expose surprising
  line continuations.
- Set `PS4` to include file, line, and function context when tracing complex
  scripts.
- Never trace secret handling.
- Do not commit broad `set -x`, `trap DEBUG`, or interactive stepping code.
- `BASH_XTRACEFD` requires Bash 4.1 or later. Check the configured runtime before
  using it.
- Debug helpers must preserve or explicitly return the script status they are
  diagnosing. A helper that prints diagnostics must not accidentally turn a
  failure into success.

Tracing pattern:

```bash
PS4='+${BASH_SOURCE}:${LINENO}:${FUNCNAME[0]}: '
set -x
_write_public_report
set +x
```

Verbose input tracing:

```bash
set -v
# shellcheck source=config.sh
source "${SCRIPT_DIR}/config.sh"
set +v
```

Expose invisible characters:

```bash
printf '%q\n' "${path}"
```

Gate newer trace-file support:

```bash
if (( BASH_VERSINFO[0] > 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] >= 1) )); then
  exec 9>"${trace_file}"
  BASH_XTRACEFD=9
fi
```

Syntax and lint checks:

```bash
bash -n path/to/script.sh
shellcheck path/to/script.sh
```

Common failure causes:

- `unexpected EOF`: unmatched quotes, unterminated here documents, missing
  `fi`, `done`, `esac`, or a CRLF line ending hiding the delimiter.
- `too many arguments`: unquoted expansion inside `[ ... ]`, or data that
  belongs in `[[ ... ]]`.
- `event not found`: interactive history expansion from `!`; quote the value or
  disable history expansion in the interactive snippet.
- Command runs differently than expected: alias, function, shell builtin, or
  PATH collision. Check with `type -a command_name`.
- Script fails before the shebang: UTF-8 BOM or CRLF line endings.

## Refactoring existing scripts

When fixing or refactoring Bash:

1. Read the whole script and sourced libraries first.
1. Identify the caller and environment.
1. Preserve behavior before changing style.
1. Fix quoting and argument arrays near the touched logic.
1. Add explicit checks around dangerous commands.
1. Move duplicated shell helpers into the local script family only when the
   callers need the same behavior and error handling.
1. Do not convert a large script in one pass unless the task is explicitly a
   script cleanup.
1. Use the configured Bash runtime. Change shebangs only when the requested implementation needs it.
1. Run lint or formatting only when explicitly requested, limited to the affected scripts.

When a script is too complex:

- keep the Bash wrapper thin;
- move parsing into the owning quality module and business logic into application code;
- keep command invocation and environment validation in Bash only if that is the
  simplest operational boundary.

## Review checklist

Before finishing Bash work, verify:

- The file has the correct shebang and header.
- The script uses Bash only where Bash is intended.
- Shell options match the script's needs and do not mask missing checks.
- The script exits with a meaningful final status.
- Every function has the required comment.
- Forbidden syntax such as `$[ ... ]`, backticks, `let`, `typeset`, `function`,
  `&>`, `|&`, and compound `[ ... -a ... ]` forms is absent.
- Variables are quoted.
- Argument lists use arrays.
- User input and external data are validated before arithmetic or command use.
- No `eval`, `bash -c`, `bash -lc`, parsed `ls`, or untrusted shell fragments exist.
- `cd`, deployment, destructive, migration, upload, and sync commands are
  checked explicitly.
- Pipelines behave correctly with or without `pipefail`.
- Redirections are ordered correctly.
- Temporary files are created with `mktemp` and cleaned up.
- Downloads, generated files, and structured replacements validate temporary
  data before replacing known-good files.
- Locks are acquired atomically, not with separate check-then-create steps.
- Network, remote, mounted-filesystem, and readiness commands have bounded
  timeouts where they can hang.
- Retries are limited to known retryable failures and have bounded attempts.
- Background jobs are tracked by PID, waited on, and cleaned up on interruption.
- Concurrent jobs keep output separated or use a tool that serializes output.
- Checkpoint files cannot skip required work after inputs, targets, or runs
  change.
- Long-running or multi-target scripts log stable status fields to `stderr`
  without secrets.
- Secrets are not printed, traced, or left in files.
- Filenames with spaces and leading dashes are safe.
- Broken symlinks, home-relative paths, and no-match globs are handled
  deliberately where relevant.
- `IFS`, `read`, and delimited-data handling do not drop meaningful data.
- Privileged redirection and globbing happen at the intended privilege level.
- Process command does not rely on `ps | grep`.
- Files have UTF-8 without BOM and LF endings.
- macOS/Linux portability is acceptable for the script's runtime.
- If linting was requested, the owning shell lint command passes or remaining
  findings are documented.

## Anti-patterns

Do not use these forms:

```bash
for file in $(ls)
for file in $(find . -type f)
files=($(find . -type f))
cat file | grep pattern
grep pattern file | while read -r line; do count=$(( count + 1 )); done
while read line; do process "$line"; done <<< "$(command)"
cp $source $target
rm -rf "$dir/"*
cd "$dir"; deploy
cmd1 && cmd2 || cmd3
echo $value
echo <<EOF
printf "$value"
eval "$command"
value=`command`
$[count + 1]
let count=count+1
typeset value=1
function deploy() {
for arg; { printf '%s\n' "$arg"; }
command &>"$log_file"
command |& grep pattern
if [ "$a" = x -o "$b" = y ]; then
trap 'handle_error' ERR
bash -c "$user_input"
sudo command > /root/file
sudo ls /root-owned-dir/*
ps ax | grep service
find . -exec sh -c 'echo {}' \;
xargs command
xargs -P4 command > merged-output.txt
sed 's/foo/bar/' file > file
local value="$(command)"
export path=~/bin
if [ $value = expected ]; then
if [[ "${number}" > 10 ]]; then
for index in {1..$count}; do
IFS=, read -ra fields <<< "$csv_line"
unset files[0]
tr [A-Z] [a-z]
set -x
curl -fsSL "$url" | bash
```

Preferred replacements:

```bash
for file in ./*; do
  [[ -e "${file}" ]] || continue
  _validate_file "${file}"
done

while IFS= LC_ALL=C read -r -d '' file; do
  _validate_file "${file}"
done < <(find . -type f -print0)

grep -q 'pattern' "${file}"
cp -- "${source}" "${target}"
deployment_config | sudo tee /etc/service/config >/dev/null

if ! cd -- "${dir}"; then
  return 1
fi
deploy

if cmd1; then
  cmd2
else
  cmd3
fi

printf '%s\n' "${value}"

declare -a command_args
command_args=(tool --flag "${value}")
"${command_args[@]}"

value="$(command)" || return 1
count=$(( count + 1 ))
# _deploy - Runs the selected deployment operation.
_deploy() {
  ...
}
command >"${log_file}" 2>&1
command 2>&1 | grep 'pattern'

find . -type f -exec sh -c 'printf "%s\n" "$1"' sh {} \;
find . -type f -print0 | xargs -0 command --

tmp_file="$(mktemp "${file}.XXXXXX")" || return 1
sed 's/foo/bar/' "${file}" >"${tmp_file}"
mv -- "${tmp_file}" "${file}"

local value
value="$(command)" || return 1

if [[ "${value}" == 'expected' ]]; then
  ...
fi

if (( number > 10 )); then
  ...
fi

for (( index = 1; index <= count; index++ )); do
  ...
done

while IFS= read -r line; do
  _parse_line "${line}"
done < <(command)

unset -v 'files[0]'
tr '[:upper:]' '[:lower:]'

if [[ "${path##*/}" == *.* ]]; then
  _validate_path "${path}"
fi
```
