# Working on Bash

These rules apply to executable shell scripts, sourced shell libraries, local
hooks, package builds, and quality commands,
package-coordinator script bodies,
Make recipes that invoke Bash, and one-off shell snippets committed to the
repository.

Service-specific commands stay in the owning rule file. Bash syntax, error
handling, quoting, process execution, pipeline-script safety, and shell review
standards live here.

## Contents

- [Core Bash philosophy](#core-bash-philosophy)
- [Source material decisions](#source-material-decisions)
- [When to use Bash](#when-to-use-bash)
- [File types and invocation](#file-types-and-invocation)
- [File encoding and line endings](#file-encoding-and-line-endings)
- [Runtime compatibility](#runtime-compatibility)
- [Deprecated and forbidden syntax](#deprecated-and-forbidden-syntax)
- [Script structure](#script-structure)
- [Module ownership and visibility](#module-ownership-and-visibility)
- [Shell options](#shell-options)
- [Output, logging, and errors](#output-logging-and-errors)
- [Literal text and here documents](#literal-text-and-here-documents)
- [Comments and documentation](#comments-and-documentation)
- [Formatting](#formatting)
- [Naming](#naming)
- [Functions](#functions)
- [Variables and constants](#variables-and-constants)
- [Quoting and expansion](#quoting-and-expansion)
- [Arrays and argument lists](#arrays-and-argument-lists)
- [Conditionals](#conditionals)
- [Arithmetic](#arithmetic)
- [Loops and input](#loops-and-input)
- [Delimited data and IFS](#delimited-data-and-ifs)
- [Paths, globs, and file names](#paths-globs-and-file-names)
- [Command substitution](#command-substitution)
- [Pipelines and redirection](#pipelines-and-redirection)
- [Calling commands](#calling-commands)
- [Process management and privilege boundaries](#process-management-and-privilege-boundaries)
- [Text, JSON, and structured data](#text-json-and-structured-data)
- [Network commands](#network-commands)
- [Secrets and environment](#secrets-and-environment)
- [Temporary files, locks, and cleanup](#temporary-files-locks-and-cleanup)
- [Publishing and long-running pipelines](#publishing-and-long-running-pipelines)
- [Local tasks and hooks](#local-tasks-and-hooks)
- [Security rules](#security-rules)
- [Portability rules](#portability-rules)
- [Linting and formatting](#linting-and-formatting)
- [No Bash tests](#no-bash-tests)
- [Debugging Bash](#debugging-bash)
- [Refactoring existing scripts](#refactoring-existing-scripts)
- [Review checklist](#review-checklist)
- [Pitfall audit](#pitfall-audit)
- [Anti-patterns](#anti-patterns)

## Core Bash philosophy

Rules:

- Bash is glue code. Use it to orchestrate commands, not to build complex
  application logic.
- Prefer small, boring scripts with explicit inputs, explicit outputs, and clear
  failure behavior.
- Treat every path, argument, environment value, command output, and user input
  as unsafe until quoted, validated, or parsed by a structured tool.
- A script that builds packages, publishes or deletes artifacts,
  uploads media, or changes secrets
  must be readable enough to audit line by line.
- ShellCheck warnings are design feedback. Fix them unless there is a documented
  reason not to.
- `set -euo pipefail` is not a substitute for checking dangerous commands.
- Do not hide publishing, runtime, or artifact
  behavior in package scripts. Move non-trivial orchestration into a
  reviewed Bash script.
- When writing shell orchestration, write Bash. Do not create another scripting
  language file as an escape hatch for shell work.
- If scripting logic is too complex for Bash, simplify the Bash workflow, split
  it into smaller Bash scripts, or move the behavior into product-owned
  application code as part of a deliberate feature change.

Good Bash:

```bash
#!/usr/bin/env bash
#
# Validate the configured model before starting the runtime.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 1
readonly SCRIPT_DIR

# fail - Prints a fatal error and exits.
fail() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

main() {
  [[ -f pyproject.toml ]] || fail 'Run this command from the repository root'
  mise run models:validate
}

main "$@"
```

Bad Bash:

```bash
#!/bin/sh
cd models
for file in $(ls); do
  python -m hf.push --model-dir $file
done
```

## Source material decisions

These rules adapt the pasted Google Shell Style Guide, BashGuide practices,
BashPitfalls, Shellharden guidance, BashFAQ entries, and Bash Hackers material
into one local standard.

| Topic               | Local decision                                                                                                                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Shell language      | Executable shell scripts use Bash, not `sh`, unless a constrained runtime explicitly requires POSIX `sh`.                                                                                                                |
| Shebang             | New cross-platform repo scripts use `#!/usr/bin/env bash`. Linux-only remote host scripts may use `#!/bin/bash` when the target guarantees that path. Follow the surrounding script family when editing.                 |
| Bash version        | Default to Bash 3.2-compatible syntax unless the script declares and checks a newer Bash requirement.                                                                                                                    |
| Script size         | Bash is acceptable for small utilities and orchestration. Over about 100 lines, complex branching, complex parsing, or nested data structures, split and simplify the Bash instead of adding another scripting language. |
| Quoting             | Quote variable expansions and command substitutions by default. Use arrays for argument lists.                                                                                                                           |
| Conditionals        | Prefer `[[ ... ]]` for Bash string/file conditionals and `(( ... ))` for trusted arithmetic comparisons. Validate untrusted numeric input before arithmetic contexts.                                                    |
| `set -euo pipefail` | Allowed for entrypoint scripts written for it, but never relied on as the only error handling around destructive, publishing, or artifact-mutating commands.                                                             |
| Deprecated syntax   | Ban legacy and ambiguous forms even when Bash still accepts them. Use the clearer replacement forms listed in this guide.                                                                                                |
| Function comments   | Every function gets a one-line header comment. Public, library, or non-obvious functions also document globals, arguments, outputs, and return behavior.                                                                 |
| Pipelines           | Split long pipelines one command per line. Understand `pipefail`, `PIPESTATUS`, and commands such as `grep -q` that may close the pipe early.                                                                            |
| External examples   | Translate generic examples into this repo's Python, ComfyUI, package builds, local hooks, and quality tasks.                                                                                                             |

## When to use Bash

Use Bash when the script mostly:

- calls other command-line tools;
- wires together install, lint, package builds, runtime setup, publishing,
  or cleanup steps;
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

Do not create non-Bash scripts as an escape hatch. If a workflow needs nested
maps, large arrays, state machines, non-trivial validation, complex retries,
concurrent work, or domain rules, reduce the scripting scope or implement the
behavior in the owning application code.

## File types and invocation

Executable scripts:

- Must start with a Bash shebang.
- Must be executable and directly invoked.
- Must own a `main` function and finish with `main "$@"`, except for
  externally defined hook and task entrypoints whose coordinator owns the
  invocation contract.
- Must not be sourced by another repository script.
- Follow [`NAMING.md`](NAMING.md) for shell filename and extension rules.

Libraries:

- Keep library files non-executable.
- Must be safe to `source` without running main program behavior.
- Must not contain a `main` function or a `main "$@"` call.
- Must not enable or disable shell options.
- Must not call `exit`.
- Must not perform workflow steps, start processes, mutate runtime state, or
  delete files while loading.
- Configuration libraries may assign documented configuration values while
  loading. Other libraries may only declare readonly owner constants, source
  direct dependencies, and define functions.
- Follow [`NAMING.md`](NAMING.md) for shell library filename rules.

Every file declares its runtime contract in the header:

```bash
#!/usr/bin/env bash
#
# Run the configured package checks.
# Runtime: Bash 3.2+, Linux.
```

Use `macOS and Linux` only when the file is supported and reviewed on both
platforms. A newer Bash requirement must name the minimum version and fail
before any other work.

Shebang rules:

```bash
#!/usr/bin/env bash
```

Use this for repo scripts that may run on macOS, Linux, local hooks, or developer
machines.

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

SUID and SGID are forbidden on shell scripts. Use `sudo` or a platform-specific
privilege boundary instead.

## File encoding and line endings

Rules:

- Store Bash files as UTF-8 without a byte-order mark.
- Use LF line endings. Do not commit CRLF shell scripts.
- Do not put binary data in shell variables. Bash variables cannot contain NUL.
- Do not use command substitution for content where exact trailing newlines
  matter.
- Keep generated shell snippets free of invisible prefix bytes before the
  shebang.

If a script has Windows line endings, convert it before review:

```bash
tr -d '\r' < "${script}" > "${script}.tmp"
mv -- "${script}.tmp" "${script}"
```

A file that starts with a BOM before `#!` may fail to execute as a script. Treat
that the same as a broken shebang.

## Runtime compatibility

macOS ships Bash 3.2 by default. Unless a script checks for a newer version,
avoid Bash 4+ and Bash 5+ features:

- associative arrays;
- `readarray` and `mapfile`;
- `globstar`;
- namerefs with `declare -n`;
- `${var@Q}` and other newer parameter transformations;
- `coproc`;
- `BASH_XTRACEFD`;
- `wait -n`;
- `local -n`;
- `shopt -s lastpipe`;
- process-substitution behavior that has not been verified on the target OS.

If a script requires a newer Bash:

```bash
require_bash_4() {
  if (( BASH_VERSINFO[0] < 4 )); then
    printf 'error: bash 4 or newer is required\n' >&2
    return 1
  fi
}
```

State the requirement in the file header and fail before doing work.

## Deprecated and forbidden syntax

Use the modern, explicit Bash form even when an older spelling still works.

Forbidden forms:

- Arithmetic expansion: do not use `$[ ... ]`. Use `$(( ... ))`.
- Command substitution: do not use legacy backtick substitution. Use `$(...)`.
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
- Legacy test composition: do not use `test -a`, `test -o`, `[ ... -a ... ]`,
  `[ ... -o ... ]`, or grouping operators inside `[ ... ]`. Use `[[ ... ]]`,
  explicit `if` branches, or `case`.
- `ERR` traps: do not use `trap ERR` as general error handling. Use explicit
  status checks where failure matters, and reserve traps for cleanup that is
  safe to run on the relevant exit path.
- `eval`: do not use casual `eval` to turn strings into code. Use arrays,
  direct validation, `case`, or fixed dispatch tables.

Bad:

```bash
function run() {
  if [ "$mode" = publish -o "$mode" = cleanup ]; then
    let count=count+1
    command &>"$log_file"
  fi
}
```

Good:

```bash
run() {
  if [[ "${mode}" == 'publish' || "${mode}" == 'cleanup' ]]; then
    count=$(( count + 1 ))
    command >"${log_file}" 2>&1
  fi
}
```

## Script structure

Order files like this:

1. Shebang.
2. File header comment.
3. Shell options.
4. `source` statements.
5. Constants and exported configuration.
6. Functions.
7. `main`.
8. `main "$@"` as the last non-comment line for executable scripts.

Example:

```bash
#!/usr/bin/env bash
#
# Run one runtime pipeline step from the repository root.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 1
readonly SCRIPT_DIR

REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)" || exit 1
readonly REPO_ROOT

source "${SCRIPT_DIR}/lib/log.sh"

# require_model_dir - Validates that the model directory exists.
# Arguments:
#   Model directory path.
# Returns:
#   0 when the directory exists, non-zero otherwise.
require_model_dir() {
  local model_dir="$1"

  [[ -d "${model_dir}" ]]
}

main() {
  local model_dir="${1:-}"

  require_model_dir "${model_dir}" || {
    printf 'error: model directory is required\n' >&2
    return 1
  }

  uv run --no-sync python -m scripts.models validate
}

main "$@"
```

Rules:

- Do not put executable program flow between function definitions.
- Do not mutate global state while loading a library unless that mutation is the
  documented purpose of the library.
- Source files with explicit paths based on `BASH_SOURCE[0]`, not the caller's
  current directory.
- Libraries may define constants, functions, and validation helpers. Entrypoints
  own argument parsing and `main`.
- Executable scripts must finish with a meaningful program status. Do not let a
  final diagnostic command, false condition, or optional cleanup check become
  the script status by accident.
- Use explicit `exit 0` only when the final command's status is not the program
  result and success has already been established.

## Module ownership and visibility

Each file owns one cohesive responsibility. Directory structure supplies the
family or domain name.

Rules:

- A sourced file containing only `source` statements is a barrel and is
  forbidden. Callers source the exact owner they use.
- A file and a sibling directory must not share a stem. Move the file into the
  directory and give it a role name.
- A function beginning with `_` is private to its defining file.
- Private functions appear before public functions.
- A private function must not be called from another file.
- An executable file exposes only `main`; every other function in that file is
  private.
- A sourced public function uses a family or domain namespace, such as
  `server_start`, `restart_read_state`, or `trt_prepare_checkpoint`.
- Library files explicitly source every repository file whose public functions
  they call. Do not rely on an entrypoint's source order or a transitive source.
- Shell configuration owners start with an owner-specific include guard before
  constants or dependency sources. The guard returns when its `_CFG_*_READY`
  marker is set, then immediately declares that marker readonly.
- Ordinary function libraries do not use blanket include guards. They remain
  safe when direct dependency diamonds source them more than once.
- Library-level behavioral constants use an owner-specific uppercase name and
  are readonly immediately after assignment. Source-path discovery variables
  are load-time values, not behavioral constants, and remain reassignable.
- Do not create a file for one function used by one caller. Keep that function
  with its caller unless the file owns a real executable, external-system,
  security, persistence, or destructive-operation boundary.
- A retained one-function, one-caller boundary includes a `Boundary:` header
  that states the concrete boundary. A comment is not sufficient when the
  implementation does not own that boundary.
- Do not split one concept across parallel directory owners, such as both
  `restart/` and `runtime/restart/`.

Preferred order inside the function section:

1. Private parsing and validation functions.
2. Private operation functions.
3. Public library functions.
4. `main` for executable scripts.

## Shell options

Use shell options deliberately.

Common entrypoint default:

```bash
set -euo pipefail
```

Rules:

- Use `set -euo pipefail` only when the script is written and reviewed for those
  semantics.
- Do not rely on `errexit` for critical safety. Explicitly check `cd`, `rm`,
  package builds, runtime setup, publishing, upload, and destructive
  commands.
- Treat `errexit` as a backstop, not command flow. It has exceptions in
  conditionals, pipelines, command substitutions, subshells, and functions.
- Do not enable shell options in sourced libraries unless the library is part of
  a script family that already owns those options.
- Do not toggle options globally around a small operation without restoring the
  prior state.
- Sourced libraries must not call `set` at all. Capture command status with
  `if`, `if !`, or an explicit conditional command instead.
- Do not change `IFS` as part of a fake strict-mode ritual. Set `IFS` locally
  only where reading or joining data requires it.
- Avoid `set -x` in committed code. If temporary tracing is necessary, keep it
  local and make sure secrets cannot be printed.

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
their status. When a function may be called in `if`, `while`, `&&`, or `||`,
write explicit checks inside the function instead of assuming `errexit` will
stop at the first failing command.

```bash
# Good: failure is explicit where it matters.
cleanup() {
  local target="$1"

  cd -- "${target}" || return 1
  rm -rf ./*
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
- Use `${name:-}` when an unset variable is acceptable.
- Use `${name:?message}` for required configuration at a clear boundary.
- Do not use unguarded `${1}` when an argument may be missing. Use `${1:-}`.
- Be careful with arrays under `set -u`; check lengths before indexing.
- If empty arrays are meaningful, require Bash 4.4 or newer before relying on
  their behavior under `set -u`. Bash 3.2-compatible scripts must guard array
  access explicitly.

## Output, logging, and errors

STDOUT is for script output that another command may consume. STDERR is for
status, warnings, prompts, and errors.

Use helpers:

```bash
# log - Prints an informational message to stderr.
log() {
  printf '%s\n' "$*" >&2
}

# fail - Prints a fatal error and exits.
fail() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}
```

Rules:

- Use `printf`, not `echo`, for predictable output.
- Error messages go to STDERR.
- Machine-readable output goes to STDOUT and excludes progress text.
- Pipeline scripts include enough context to diagnose the failing step.
- Long-running, cron, publishing, and multi-target scripts use timestamped
  diagnostics with stable fields instead of prose-only progress.
- Include the script name, function or step, host or target, attempt number, and
  status when those fields exist.
- Do not print secrets, tokens, cookies, connection strings, `.env` content, or
  provider payloads.
- Do not use colored output in local hooks unless the runner and logs support it.
- Do not make parsers depend on human log text.
- Use `logger` or journald only in Linux-only scripts that validate the command
  is available and document the runtime dependency.

Good:

```bash
printf 'Running %s for %s\n' "${step_name}" "${model_variant}" >&2
```

Structured diagnostic:

```bash
# log_status - Prints a timestamped diagnostic line to stderr.
# Arguments:
#   Step name.
#   Target name.
#   Status label.
log_status() {
  local step_name="$1"
  local target_name="$2"
  local status_label="$3"
  local timestamp

  timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')" || return 1
  printf 'ts=%s script=%s step=%s target=%s status=%s\n' \
    "${timestamp}" "${0##*/}" "${step_name}" "${target_name}" \
    "${status_label}" >&2
}
```

Bad:

```bash
echo "Publishing with token $REACTOR_API_KEY"
```

## Literal text and here documents

Rules:

- Use here documents only with commands that read from STDIN.
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
Running ${step_name} for ${model_variant}.
EOF
```

Bad:

```bash
echo <<EOF
This body is ignored by echo.
EOF
```

## Comments and documentation

Every Bash file starts with a short file header after the shebang:

```bash
#!/usr/bin/env bash
#
# Run runtime warmup for a configured model.
```

Every function requires a one-line header:

```bash
# normalize_env_name - Converts an environment alias to its canonical name.
normalize_env_name() {
  ...
}
```

For functions that are public, sourced by other files, non-obvious, or risky,
include the full header:

```bash
# upload_media - Uploads one media file to the selected endpoint.
# Globals:
#   REACTOR_API_KEY
# Arguments:
#   Model directory.
#   Destination identifier.
# Outputs:
#   Writes progress to stderr.
# Returns:
#   0 when upload succeeds, non-zero otherwise.
push_model() {
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

- Indent with 2 spaces. No tabs except tab-stripping here-documents with
  `<<-`.
- Keep Bash source lines within 80 columns where practical.
- Use blank lines between logical blocks.
- Keep `; then` and `; do` on the same line as `if`, `for`, `while`, `until`,
  and `select`.
- Put `else`, `elif`, `fi`, `done`, and `esac` on their own aligned lines.
- Prefer one command per line over dense semicolon chains.
- Follow [`NAMING.md`](NAMING.md) for function, variable, constant, and
  environment variable names.

Control flow:

```bash
for arg in "$@"; do
  if [[ -n "${arg}" ]]; then
    printf '%s\n' "${arg}"
  else
    printf 'empty argument\n' >&2
  fi
done
```

Case statements:

```bash
case "${environment}" in
  staging)
    run_local_pipeline
    ;;
  production)
    run_publish_pipeline
    ;;
  *)
    printf 'error: unknown environment: %s\n' "${environment}" >&2
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
generate_results \
  | jq -r '.items[] | .name' \
  | sort \
  | uniq
```

## Naming

Bash naming rules live in [`NAMING.md`](NAMING.md). Follow that file for shell
file stems, script extensions, function names, variable names, constants,
environment variables, loop variables, package-like function prefixes, and names
that would collide with shell builtins or common commands.

- Bash files in one directory must not share the first filename component before
  `_` or `-`.
- Put a related script family in an owning subdirectory and give the contained
  files role names such as `main.sh`, `state.sh`, `query.sh`, or `report.sh`.
- External hook families may use a configured shared prefix when the external
  interface owns those filenames.

The local linting tools under `quality/` and `mise run lint:quality` are also
authoritative for enforced naming policy.

## Functions

Rules:

- Use `name() { ... }` consistently for new code.
- Do not write `function name()`, `function name() { ... }`, or
  `function name { ... }`.
- Keep functions small and single-purpose.
- Declare function-local variables with `local`.
- Separate `local` declaration from command substitution assignment when the
  exit code matters.
- Return status codes with `return`. Print data to STDOUT only when the function
  is designed as a value-producing command.
- Do not make a function both print data and log progress to STDOUT.
- Keep a function within 40 non-comment statements, eight control-flow
  branches, and three levels of control-flow nesting.
- A function that coordinates enough flags, counters, mutable state, or status
  codes to resemble a state machine does not belong in Bash. Simplify the
  workflow or move the domain behavior to its existing application-code owner.
- Do not use a non-zero status to represent an ordinary result such as
  `unchanged`. Print or assign an explicit result and reserve non-zero statuses
  for failures.

Good:

```bash
# current_branch - Prints the current Git branch.
# Outputs:
#   Writes the branch name to stdout.
current_branch() {
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

Use `main` for every executable script that has functions:

```bash
main() {
  parse_args "$@"
  run
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
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)" || exit 1
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
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
declare -a scan_args
scan_args=(
  --root
  "${REPO_ROOT}"
)

uv run --no-sync python -m quality.python.runner "${scan_args[@]}"
```

Bad:

```bash
scan_args="--root ${REPO_ROOT}"
uv run --no-sync python -m quality.python.runner ${scan_args}
```

Rules:

- Expand arrays with `"${array[@]}"`.
- Do not populate arrays with raw `$(...)`.
- Use a `while read` loop or Bash 4+ `readarray` only when runtime support is
  guaranteed.
- Avoid arrays as ersatz nested data structures.
- On Bash 3.2-compatible scripts, indexed arrays are allowed; associative arrays
  are not.

Safe multi-line command output into an array on Bash 4+:

```bash
readarray -t files < <(find . -type f -name '*.sql' -print)
```

Bash 3.2-compatible line loop:

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
  load_config "${config_file}"
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
- Do not put untrusted strings into `(( ... ))`, `$(( ... ))`, `[[ value -gt n
]]`, array indices, or arithmetic `for` expressions.
- Avoid associative arrays in arithmetic contexts. Project-default Bash 3.2 does
  not support associative arrays, and newer Bash versions differ in expansion
  behavior.
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
  printf 'error: port must be numeric\n' >&2
  return 1
fi

if (( port < 1 || port > 65535 )); then
  printf 'error: port is out of range\n' >&2
  return 1
fi
```

Avoid:

```bash
if [[ "${port}" > 1024 ]]; then
  ...
fi
```

That is a lexicographical comparison.

Safer signed base-10 conversion:

```bash
if [[ "${value}" =~ ^[+-]?[0-9]+$ ]]; then
  value_base10=$(( ${value%%[!+-]*}10#${value#[-+]} ))
fi
```

Safer redirection target:

```bash
output_file="result$(( index + 1 )).txt"
index=$(( index + 1 ))
generate_result >"${output_file}"
```

Do not do:

```bash
generate_result >"result$(( index++ )).txt"
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
  process_line "${line}"
done < "${input_file}"
```

Good command output loop:

```bash
while IFS= read -r line; do
  process_line "${line}"
done < <(generate_lines)
```

Avoid this loop input form:

```bash
while IFS= read -r line; do
  process_line "${line}"
done <<< "$(generate_lines)"
```

It collects all output first, strips trailing newlines, discards NUL bytes, and
adds a final newline.

Good filename loop:

```bash
while IFS= LC_ALL=C read -r -d '' file; do
  process_file "${file}"
done < <(find "${root_dir}" -type f -print0)
```

Bad:

```bash
for file in $(find "${root_dir}" -type f); do
  process_file "${file}"
done
```

Counter loop:

```bash
for (( index = 0; index < count; index++ )); do
  run_case "${index}"
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
- Do not parse general CSV with `IFS=, read ...`; use product-owned application
  code with a real CSV parser.
- If a simple delimiter format is truly controlled, remember that `read` treats
  `IFS` as a terminator. A trailing empty field is discarded unless you account
  for it.
- Do not populate arrays from raw command substitution.

Good local `IFS`:

```bash
join_path_parts() {
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
  lint_sql "${file}"
done
```

Broken symlink-aware conditional:

```bash
if [[ -e "${path}" || -L "${path}" ]]; then
  process_path "${path}"
fi
```

Basename pattern conditional:

```bash
if [[ "${path##*/}" == *.* ]]; then
  process_file_with_extension "${path}"
fi
```

With `nullglob`, scope the option:

```bash
list_sql_files() {
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
  printf 'error: cannot enter target dir: %s\n' "${target_dir}" >&2
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

If trailing newlines matter, avoid command substitution or deliberately preserve
them with a sentinel.

Sentinel pattern:

```bash
content_with_sentinel="$(some_command; printf x)" || return 1
content="${content_with_sentinel%x}"
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

Check pipeline statuses:

```bash
tar -cf - ./* | (cd -- "${target_dir}" && tar -xf -)
statuses=( "${PIPESTATUS[@]}" )

if (( statuses[0] != 0 || statuses[1] != 0 )); then
  printf 'error: tar copy failed\n' >&2
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
  handle_success
else
  statusCode=$?
  handle_failure "${statusCode}"
fi
```

For parallel execution, write per-job output to separate files and combine them
after all jobs complete, or use a tool that serializes output.

## Calling commands

Rules:

- Check command availability before using non-standard tools.
- Check uncommon commands before long-running, destructive, publishing, or
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
- When shell features are genuinely required, use a static Bash snippet and pass
  configured values as positional arguments.
- Treat remote `ssh` command strings as a last resort. Prefer a reviewed script
  copied to the host or pass fixed commands plus deliberately quoted arguments.
- `bash -lc` is forbidden in repository scripts.
- Do not accept a command string parameter. Accept the command and its
  arguments after `shift`, then invoke `"$@"`.

Command requirement helper:

```bash
# require_command - Ensures a command exists on PATH.
# Arguments:
#   Command name.
require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'error: required command not found: %s\n' "${command_name}" >&2
    return 1
  fi
}
```

Good:

```bash
declare -a cmd
cmd=(python -m hf.push --model-dir "${model_dir}" --repo-id "${repo_id}")
"${cmd[@]}"
```

Bad:

```bash
cmd="python -m hf.push --model-dir $model_dir --repo-id $repo_id"
eval "$cmd"
```

Shell boundary:

```bash
bash -c 'printf "%s\n" "$1"' bash "${message}"
```

Do not interpolate the value into the script string:

```bash
bash -c "printf '%s\n' ${message}"
```

## Process management and privilege boundaries

Rules:

- Do not use `ps ... | grep name` as process command.
- Prefer service-coordinator commands, PID files owned by the script family,
  `pgrep`/`pkill` with exact matching, or platform-native process APIs.
- Ordinary stop and restart paths stop only PIDs recorded by the owning script
  family.
- Treat process names as advisory. They are not an authorization boundary.
- When starting background jobs, save each PID, `wait` for each PID, and capture
  each job's status explicitly.
- Scripts that start background work must clean up owned child processes on
  `INT`, `TERM`, and `EXIT`.
- Keep per-job output in separate files when concurrent jobs can interleave
  logs.
- Avoid unbounded fan-out. When targeting many hosts or files, use an explicit
  concurrency limit or a purpose-built tool such as Ansible or GNU Parallel.
- `sudo command > file` redirects as the current user, not as root.
- Globs in `sudo command /path/*` expand before `sudo` runs.
- Use `sudo tee` for privileged file writes when possible.
- Use a fixed `sudo sh -c '...'` wrapper only when root-owned shell expansion or
  redirection is genuinely required.
- Do not put user input inside privileged shell strings.

Privileged write:

```bash
generate_config | sudo tee /etc/service/config >/dev/null
```

Privileged glob, fixed string only:

```bash
sudo sh -c 'ls /root-owned-dir/*.conf'
```

Process lookup:

```bash
pgrep -x service_name >/dev/null
```

Small bounded background jobs:

```bash
declare -a child_pids

# cleanup_children - Stops child processes started by this script.
cleanup_children() {
  local pid

  for pid in "${child_pids[@]}"; do
    kill -0 "${pid}" >/dev/null 2>&1 || continue
    kill "${pid}" >/dev/null 2>&1 || true
  done
}

# run_remote_checks - Runs remote checks and returns non-zero on any failure.
# Arguments:
#   Small, already bounded host list to check.
run_remote_checks() {
  local host
  local pid
  local status=0

  trap 'cleanup_children' EXIT
  trap 'cleanup_children; exit 130' INT
  trap 'cleanup_children; exit 143' TERM

  for host in "$@"; do
    check_host "${host}" >"${tmp_dir}/${host}.log" 2>&1 &
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
- Use `jq` for JSON.
- Use `yq` or a project-owned parser for YAML when YAML structure matters.
- Do not parse JSON, YAML, XML, HTML, plist, or xcodebuild output with ad hoc
  `grep | sed | awk` unless the input is controlled and the format is trivial.
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
service_url="$(jq -r '.service.url // empty' "${config_file}")" || return 1
[[ -n "${service_url}" ]] || {
  printf 'error: service.url is required\n' >&2
  return 1
}
```

Bad JSON:

```bash
service_url="$(grep service_url "${config_file}" | cut -d: -f2)"
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
  and there is no safer package coordinator or checksum-based flow.
- Do not print response bodies that may contain secrets.
- Use retries only for known retryable network, provider, or service failures,
  with bounded attempts, delay, and attempt-count logging.
- Do not retry corrupt data, syntax errors, invalid credentials, missing
  required files, failed validation, or permission problems.
- Separate download, verification, and execution into visible steps.

Good:

```bash
download_file() {
  local url="$1"
  local output_file="$2"

  curl --fail --show-error --silent --location \
    --connect-timeout 10 \
    --max-time 60 \
    --output "${output_file}" \
    "${url}"
}
```

Remote timeout:

```bash
ssh \
  -o ConnectTimeout=10 \
  -o ServerAliveInterval=15 \
  -o ServerAliveCountMax=2 \
  -- "${host}" \
  systemctl is-active --quiet "${service_name}"
```

Installer pattern:

```bash
tmp_dir="$(mktemp -d)" || return 1
trap 'rm -rf "${tmp_dir}"' RETURN

installer="${tmp_dir}/install.sh"
curl --fail --show-error --silent --location \
  --connect-timeout 10 \
  --max-time 60 \
  --output "${installer}" \
  "${installer_url}"

printf '%s  %s\n' "${expected_sha256}" "${installer}" | shasum -a 256 -c -
bash "${installer}" --version "${tool_version}"
```

## Secrets and environment

Rules:

- Read secrets from the caller environment, a secret coordinator, or documented
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
# require_env - Ensures an environment variable is set and non-empty.
# Arguments:
#   Environment variable name.
require_env() {
  local name="$1"

  if [[ -z "${!name:-}" ]]; then
    printf 'error: %s is required\n' "${name}" >&2
    return 1
  fi
}
```

Do not pass untrusted env names to `${!name}` without validation:

```bash
if [[ ! "${name}" =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
  printf 'error: invalid env var name\n' >&2
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
- Full cleanup is opt-in. Stop commands preserve environments, caches, models,
  and unrelated runtime resources by default.
- Cleanup must be limited to repository-owned paths and PIDs. Do not delete
  whole home cache roots, arbitrary configured cache roots, shared `/tmp`
  families, or every process holding a GPU context.
- Before `rm -rf`, canonicalize or structurally validate the target against an
  explicit owner root. Reject empty paths, `/`, the repository root itself,
  `$HOME`, and any path outside the declared owner.
- Do not use `|| true` on destructive commands or required installation,
  publishing, package builds, or runtime commands.

Good:

```bash
tmp_dir="$(mktemp -d)" || return 1
trap 'rm -rf "${tmp_dir}"' EXIT
```

Atomic structured replacement:

```bash
tmp_file="$(mktemp "${config_file}.XXXXXX")" || return 1
trap 'rm -f "${tmp_file}"' RETURN

curl --fail --show-error --silent --location \
  --connect-timeout 10 \
  --max-time 60 \
  --output "${tmp_file}" \
  "${config_url}" || return 1

jq empty "${tmp_file}" >/dev/null || return 1
mv -- "${tmp_file}" "${config_file}" || return 1
trap - RETURN
```

Race-safe lock directory:

```bash
lock_dir="${state_dir}/publish.lock"

if ! mkdir "${lock_dir}"; then
  printf 'error: lock is already held: %s\n' "${lock_dir}" >&2
  return 1
fi

printf '%s\n' "$$" >"${lock_dir}/pid" || {
  rmdir "${lock_dir}"
  return 1
}

trap 'rm -rf "${lock_dir}"' EXIT
```

Function-scoped cleanup:

```bash
run_with_temp_dir() {
  local tmp_dir
  tmp_dir="$(mktemp -d)" || return 1
  trap 'rm -rf "${tmp_dir}"' RETURN

  generate_files "${tmp_dir}"
}
```

Destructive operations must validate the target:

```bash
remove_build_dir() {
  local build_dir="$1"

  [[ -n "${build_dir}" ]] || return 1
  [[ "${build_dir}" == */build ]] || return 1
  rm -rf -- "${build_dir}"
}
```

## Publishing and long-running pipelines

Package builds, installation, runtime setup, and publishing scripts need stricter structure than local utility scripts.

Rules:

- Separate validation, planning, confirmation, execution, readiness checks, and
  cleanup.
- Fail before doing work when required inputs, commands, files, model
  directories, or secrets are missing.
- Make the target explicit. Do not infer a destination or artifact path from a branch name.
  Require an explicit target before publishing.
- Make destructive or remote publishing actions require explicit authorization.
  Existing user authorization remains valid for its stated scope.
- Keep pipeline state readable: package name, output directory,
  destination, commit, and configuration path.
- Use idempotent commands where possible.
- Check readiness after publishing or long-running setup and surface actionable
  diagnostics on failure.
- Do not continue to later steps after a required pipeline step fails.
- Do not hide partial failure by using `|| true` around build, installation, scan, or publish commands.
- Use bounded retries only for known retryable operations.
- Keep cleanup commands explicit. Do not delete models, results, or checkpoints
  as an implicit side effect.
- Log enough to reconstruct what happened without printing secrets.

Recommended flow:

```text
parse args
read environment
validate required commands
validate required files
validate secrets without printing values
resolve target
show pipeline summary
confirm if interactive/destructive
build or locate artifact
build the package or prepare the runtime
upload or publish
verify published artifact
print final state
```

Confirmation helper:

```bash
# confirm_exact - Requires the user to type the expected value.
# Arguments:
#   Prompt label.
#   Expected response.
confirm_exact() {
  local label="$1"
  local expected="$2"
  local response

  printf '%s Type %s to continue: ' "${label}" "${expected}" >&2
  IFS= read -r response

  [[ "${response}" == "${expected}" ]]
}
```

Remote commands:

- Prefer copying a reviewed script to the remote host and invoking it with
  arguments.
- Avoid interpolating local variables into remote shell strings.
- If `ssh host command args...` is used, pass fixed commands and quoted
  arguments.
- Treat remote command strings as a last resort. Quote or escape every argument
  deliberately for the shell that will parse it.
- Do not build remote shell fragments from user input.
- Validate hostnames, usernames, service names, model variants, and remote paths
  before using them in remote commands.
- Use native connection and command timeouts for remote calls that can hang.

Bad:

```bash
ssh "$host" "cd $dir && bash scripts/main.sh --push"
```

Better:

```bash
ssh -- "${host}" bash -- "${remote_script}" "${dir}" "${model_variant}"
```

Checkpoint state:

- Use checkpoint files only for idempotent, resumable workflows where repeating
  a completed expensive step is wasteful.
- Scope checkpoint paths by script name, date or run ID, target environment, and
  input identity so stale success markers cannot skip required work.
- Mark a checkpoint successful only after validation and final replacement have
  completed.
- Invalidate or ignore checkpoint state on interruption unless partial progress
  is explicitly safe to resume.
- Do not use checkpoints to skip required validation, confirmation, or
  readiness checks.

Persisted runtime state:

- Never `source` generated state or pass it to `bash -c`.
- Use a fixed, non-executable data format with an exact key schema.
- Reject delimiters or newlines that the format cannot represent.
- Write state to a permission-restricted temporary file in the destination
  directory, then replace the previous state with an atomic `mv`.
- Readers treat malformed, duplicate, or unknown state keys as errors.

Retry pattern:

```bash
# retry_retryable - Runs a retryable command with bounded attempts.
# Arguments:
#   Step name for logs.
#   Attempt count.
#   Delay seconds.
#   Command and arguments.
retry_retryable() {
  local step_name="$1"
  local attempts="$2"
  local delay_seconds="$3"
  shift 3

  local attempt
  local status

  [[ "${attempts}" =~ ^[1-9][0-9]*$ ]] || return 2
  [[ "${delay_seconds}" =~ ^[0-9]+$ ]] || return 2

  for (( attempt = 1; attempt <= attempts; attempt++ )); do
    printf 'step=%s attempt=%s/%s status=running\n' \
      "${step_name}" "${attempt}" "${attempts}" >&2

    if "$@"; then
      printf 'step=%s attempt=%s/%s status=success\n' \
        "${step_name}" "${attempt}" "${attempts}" >&2
      return 0
    else
      status=$?
    fi

    printf 'step=%s attempt=%s/%s status=failed exit=%s\n' \
      "${step_name}" "${attempt}" "${attempts}" "${status}" >&2

    if (( attempt == attempts )); then
      return "${status}"
    fi

    sleep "${delay_seconds}"
  done
}
```

Use retries for:

- retryable network pulls;
- readiness polling;
- read-only provider requests with documented retry behavior;
- owned process readiness checks.

Do not use retries to mask:

- corrupt data;
- invalid credentials;
- failed artifact validation;
- syntax errors;
- missing files;
- failed validation;
- failing checks;
- permission problems.

## Local tasks and hooks

- Keep mise task wrappers small. Put reusable behavior in its owning script.
- Use pinned tools and existing dependencies. Hooks must not install packages.
- Keep checks read-only. Formatting and generation use separate tasks.
- Keep logs and scanner reports in ignored private directories.
- Preserve other hook owners. Configure hooks only for this repository.
- Propagate command failures. Never hide a failure behind a final message.
- Do not create hosted Git workflows, Docker tooling, or automated tests.

```bash
mise run lint:python
mise run lint:shell
```

## Security rules

Never:

- use `eval` with configured input;
- use `ERR` traps as a substitute for explicit status checks;
- build shell commands from user input;
- pass user input to `bash -c`;
- parse untrusted arithmetic expressions with `(( ... ))`;
- use unsanitized values as variable names, associative array keys in arithmetic
  contexts, model variants, repository names, remote paths, or remote shell
  fragments;
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
find . -type f -name '*.sql' -exec sh -c 'lint_sql "$1"' sh {} \;
```

Unsafe:

```bash
find . -type f -exec sh -c 'lint_sql {}' \;
```

Safe xargs:

```bash
find . -type f -name '*.sql' -print0 | xargs -0 shellcheck --
```

If a value must become a command argument, keep it as an argument. Do not turn it
into code.

## Portability rules

Rules:

- Default to Bash 3.2-compatible syntax unless runtime support is checked.
- Every file header declares the supported platform and minimum Bash version.
- The declared contract and syntax must agree. Bash 4+ features such as
  `mapfile`, `readarray`, associative arrays, and `${value,,}` require a
  checked Bash 4+ entry boundary; otherwise they are forbidden.
- Account for macOS/BSD and GNU differences in `sed`, `date`, `readlink`,
  `mktemp`, `stat`, `xargs`, and `grep`.
- Prefer project-provided wrappers for platform-specific behavior.
- Do not use `realpath` unless the target platform guarantees it.
- Use `pwd -P` after `cd` for physical paths when symlinks matter.
- Avoid `sed -i` unless platform-specific behavior is handled.
- Avoid `date` parsing that differs between GNU and BSD.
- Do not assume `/bin/bash` is a modern Bash on macOS.
- Do not use Linux-only utilities in macOS-compatible scripts without checks.
- Do not assume local hooks has the same PATH as a developer shell.

Portable-ish script directory:

```bash
SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly SCRIPT_DIR
```

When absolute path resolution must handle symlinks across platforms, prefer a
small verified Bash helper or product-owned application code.

## Linting and formatting

Rules:

- Run the owning project's shell lint command when touching Bash.
- Fix ShellCheck findings in the touched scope.
- Format touched scripts with the project formatter when one exists.
- Do not add broad or unexplained lint suppressions.
- Every suppression must explain why the warning is intentionally accepted.
- Prefer changing code to satisfy ShellCheck over adding disable comments.
- Project-wide ShellCheck exceptions belong in `quality/config/shellcheckrc` and
  require an explicit rule-level rationale. This repository disables SC2310 and
  SC2311 because libraries must check statuses explicitly and may not depend on
  inherited `errexit`; those diagnostics otherwise report each intentional
  conditional function call.

Expected tools:

- ShellCheck for correctness and safety.
- shfmt for formatting when the script family uses it.
- Additional security scanners only when requested or included in the requested project task.

Common commands by area:

```bash
mise run lint:shell
```

Run from the repository root.

ShellCheck suppression shape:

```bash
# lint:justify -- reason: The sourced configuration provides the recording limit -- ticket: configuration
# shellcheck disable=SC2154
printf '%s\n' "${MAX_RECORDING_SECONDS}"
```

Prefer a local comment that names the contract over a file-wide suppression.

## No Bash tests

Rules:

- Do not create Bash test suites.
- Do not add Bats, shunit2, ShellSpec, project Bash harnesses, PATH mock wrappers,
  or sample directories for Bash scripts.
- Do not add test-only branches, test-only flags, or test-only dependency
  injection to Bash scripts.
- Do not create sample files only to exercise Bash behavior.
- Do not move Bash orchestration into another scripting language only to make it
  easier to test.
- Bash verification is static review, ShellCheck, shfmt, and `bash -n`.
- Runtime trial runs are allowed only when they are part of the requested
  workflow or needed to verify a real publish/local command, not as a new test
  suite.

## Debugging Bash

Rules:

- Start with the exact error message and the line it names. Do not guess before
  checking the command Bash actually reports.
- Use `bash -n` and ShellCheck before tracing.
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
- `BASH_XTRACEFD` requires newer Bash than the project default. Gate it with a
  version check before use.
- Debug helpers must preserve or explicitly return the script status they are
  diagnosing. A helper that prints diagnostics must not accidentally turn a
  failure into success.

Tracing pattern:

```bash
PS4='+${BASH_SOURCE}:${LINENO}:${FUNCNAME[0]:-main}: '
set -x
run_non_secret_step
set +x
```

Verbose input tracing:

```bash
set -v
source "${config_file}"
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
2. Identify the caller contract: local dev, local hooks, remote host, or package script.
3. Preserve behavior before changing style.
4. Fix quoting and argument arrays near the touched logic.
5. Add explicit checks around dangerous commands.
6. Move duplicated shell helpers into the local script family only when the
   helper has a real shared contract.
7. Do not convert a large script in one pass unless the task is explicitly a
   script cleanup.
8. Do not change shebangs across a script family unless runtime compatibility is
   verified.
9. Run the narrow shell lint/format command first, then broader checks when the
   owning rule file requires them.

When a script is too complex:

- keep the Bash wrapper thin;
- move parsing or business logic into product-owned application code;
- keep command invocation and environment validation in Bash only if that is the
  simplest operational boundary.

## Review checklist

Before finishing Bash work, verify:

- The file has the correct shebang and header.
- The file is exactly one invocation type: executable entrypoint or
  non-executable library.
- Private functions precede public functions and are not called externally.
- Public library functions and constants use their owner namespace.
- Every repository function dependency is sourced directly.
- No source-only barrel or one-function, one-caller pseudo-module remains.
- The script uses Bash only where Bash is intended.
- Shell options are appropriate and not masking missing checks.
- The script exits with a meaningful final status.
- Every function has the required comment.
- Deprecated syntax such as `$[ ... ]`, backticks, `let`, `typeset`, `function`,
  `&>`, `|&`, and legacy `[ ... -a ... ]` forms is absent.
- Variables are quoted.
- Argument lists use arrays.
- User input and external data are validated before arithmetic or command use.
- No `eval`, configured `bash -c`, parsed `ls`, or untrusted shell fragments exist.
- `cd`, package builds, installation, publishing, upload, and
  destructive commands are checked explicitly.
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
- Long-running or multi-target scripts log stable status fields to STDERR
  without secrets.
- Secrets are not printed, traced, or left in files/layers.
- Filenames with spaces and leading dashes are safe.
- Broken symlinks, home-relative paths, and no-match globs are handled
  deliberately where relevant.
- `IFS`, `read`, and delimited-data handling do not drop meaningful data.
- Privileged redirection and globbing happen at the intended privilege level.
- Process command does not rely on `ps | grep`.
- Files have UTF-8 without BOM and LF endings.
- macOS/Linux portability is acceptable for the script's runtime.
- The owning shell lint command passes or remaining findings are documented.

## Pitfall audit

This guide covers the pasted BashPitfalls list as rules rather than as a copied
reference index.

| Pitfall group                                                              | Covered by                                                                                                                                                                             |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Deprecated syntax, legacy tests, old function forms, redirection shortcuts | [Deprecated and Forbidden Syntax](#deprecated-and-forbidden-syntax)                                                                                                                    |
| `ls`, raw `find`, word splitting, `$*`, quoting, leading dashes            | [Quoting and Expansion](#quoting-and-expansion), [Paths, Globs, and File Names](#paths-globs-and-file-names), [Loops and Input](#loops-and-input)                                      |
| `[ ... ]`, `[[ ... ]]`, missing spaces, pattern-vs-string matching         | [Conditionals](#conditionals)                                                                                                                                                          |
| `cd`, command substitution, here-strings, trailing newlines                | [Paths, Globs, and File Names](#paths-globs-and-file-names), [Command Substitution](#command-substitution), [Loops and Input](#loops-and-input)                                        |
| `echo`, `printf`, here documents, literal text, history expansion          | [Output, Logging, and Errors](#output-logging-and-errors), [Literal Text and Here Documents](#literal-text-and-here-documents)                                                         |
| assignments, `local`/`readonly`/`export`, tilde, `unset`                   | [Variables and Constants](#variables-and-constants), [Functions](#functions)                                                                                                           |
| arithmetic, `expr`, leading zeroes, array indices, date consistency        | [Arithmetic](#arithmetic)                                                                                                                                                              |
| pipes, `PIPESTATUS`, redirection order, same-file writes, parallel output  | [Pipelines and Redirection](#pipelines-and-redirection)                                                                                                                                |
| `read`, `IFS`, CSV-like data, NUL streams, Bash 5 read locale bug          | [Delimited Data and IFS](#delimited-data-and-ifs), [Loops and Input](#loops-and-input)                                                                                                 |
| `set -euo pipefail`, `errexit`, `pipefail`, `nounset`                      | [Shell Options](#shell-options)                                                                                                                                                        |
| `eval`, configured shells, `find -exec sh -c`, `xargs`, network-to-shell   | [Security Rules](#security-rules), [Network Commands](#network-commands)                                                                                                               |
| `sudo`, `su`, process matching, closed descriptors                         | [Process Management and Privilege Boundaries](#process-management-and-privilege-boundaries), [Pipelines and Redirection](#pipelines-and-redirection)                                   |
| BOM, CRLF, Bash version, macOS/GNU differences                             | [File Encoding and Line Endings](#file-encoding-and-line-endings), [Runtime Compatibility](#runtime-compatibility), [Portability Rules](#portability-rules)                            |
| ShellCheck, readability, structure, comments, debugging                    | [Script Structure](#script-structure), [Comments and Documentation](#comments-and-documentation), [Linting and Formatting](#linting-and-formatting), [Debugging Bash](#debugging-bash) |

## Anti-patterns

Avoid these unless there is a documented, reviewed exception:

```bash
for file in $(ls)
for file in $(find . -type f)
files=($(find . -type f))
cat file | grep pattern
grep pattern file | while read -r line; do count=$(( count + 1 )); done
while read line; do process "$line"; done <<< "$(command)"
cp $source $target
rm -rf "$dir/"*
cd "$dir"; run_step
cmd1 && cmd2 || cmd3
echo $value
echo <<EOF
printf "$value"
eval "$command"
value=`command`
$[count + 1]
let count=count+1
typeset value=1
function run_step() {
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
  process_file "${file}"
done

while IFS= LC_ALL=C read -r -d '' file; do
  process_file "${file}"
done < <(find . -type f -print0)

grep -q 'pattern' "${file}"
cp -- "${source}" "${target}"
generate_config | sudo tee /etc/service/config >/dev/null

if ! cd -- "${dir}"; then
  return 1
fi
run_step

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
run_step() {
  ...
}
command >"${log_file}" 2>&1
command 2>&1 | grep 'pattern'

find . -type f -exec sh -c 'process_file "$1"' sh {} \;
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
  process_line "${line}"
done < <(command)

unset -v 'files[0]'
tr '[:upper:]' '[:lower:]'

if [[ "${path##*/}" == *.* ]]; then
  process_path "${path}"
fi
```
