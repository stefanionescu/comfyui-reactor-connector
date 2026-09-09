# Naming

This is the single source of truth for naming in this repository. It covers
general naming principles plus Python, Bash, TypeScript, JavaScript, CSS,
ComfyUI node contracts, and Reactor model identifiers.

Use names that make the purpose and scope clear without reading the implementation.

## Contents

- [Authority and local enforcement](#authority-and-local-enforcement)
- [General naming rules](#general-naming-rules)
- [Vocabulary and role words](#vocabulary-and-role-words)
- [Functions and methods](#functions-and-methods)
- [Booleans and predicates](#booleans-and-predicates)
- [Files and directories](#files-and-directories)
- [Python](#python)
- [Bash](#bash)
- [JavaScript](#javascript)
- [HTML, CSS, and content](#html-css-and-content)
- [Data, models, and external boundaries](#data-models-and-external-boundaries)
- [Review checklist](#review-checklist)

## Authority and local enforcement

Apply these naming rules to files, directories, declarations, CLI flags,
environment variables, workflow examples, and documentation examples.

- Keep the existing naming, folder, file-size, and function-size limits.
- Do not weaken a check or hide a name in a string key or alias to bypass policy.
- Keep exact names required by the current host or provider API at that boundary.
  Use domain names for code owned by this project.
- When a guide and a checker disagree, report the conflict. Change the checker
  only when the user requests a tooling change.
- Running naming checks requires an explicit verification request.

## General naming rules

Names are a design tool. A name should let a reader understand the concept,
scope, role, and expected value without reading the implementation first.

Rules:

- Name by role, responsibility, and domain meaning.
- Do not name by storage type, library type, collection shape, or implementation
  accident.
- Use English unless representing an external identifier that must keep another
  spelling.
- Prefer the shortest name that is still clear at the use site.
- Add qualifiers only when the unqualified name is ambiguous.
- Avoid private shorthand that only the original author understands.
- Avoid contractions created by deleting letters from a word.
- Do not duplicate context already supplied by the enclosing module, directory,
  class, or package.
- Do not encode every implementation detail in a name.
- Use the same vocabulary for the same concept across the repository.
- Use singular names for single values and plural names for collections.
- Name collections by their contents, not by the collection type.
- Use role words when primitive or weak types do not carry enough meaning.
- Preserve required external names at boundaries, but translate them into domain
  names before they move inward.
- Do not use banned generic verbs or role words in local names. These include `load`, `loader`,
  `loaded`, `loading`, `resolve`, `resolving`, `resolution`, `manager`, `handler`,
  `helper`, `util`, `utils`, `processor`, `service`, `common`, `core`, and
  `data`. Use precise verbs such as `read`, `choose`, `derive`, `build`, `create`,
  `parse`, `validate`, `sanitize`, or `format` only when the verb describes the
  real operation.

Bad:

```python
string = "reactor/helios"
array = examples
data = build_examples()
tmp = choose_duration(settings, source, requested)
```

Good:

```python
model_name = "reactor/helios"
recording_jobs = jobs
request_messages = parse_messages(payload)
duration_seconds = choose_duration(settings, source, requested_seconds)
```

### Role instead of type

Names should explain what the value means in the domain.

Bad:

```python
data = encode_prompt(text)
dict_value = compute_latency_stats(examples)
bool_value = camera.is_available()
```

Good:

```python
encoded_input = encode_prompt(text)
latency_stats = compute_latency_stats(examples)
is_camera_available = camera.is_available()
```

### Avoid redundant context

Let the owner provide context. Add context only when the name would otherwise be
ambiguous outside the owner.

Bad:

```python
@dataclass
class PromptMessage:
    prompt_message_text: str
    prompt_message_role: str
```

Good:

```python
@dataclass
class PromptMessage:
    text: str
    role: str
```

### Avoid type and shape duplication

Do not repeat information already expressed by the type system or declaration.

Bad:

```python
name_string: str = variant.name
messages_list: list[Message] = parse_messages(payload)
config_dict: dict[str, object] = build_config()
```

Good:

```python
name: str = variant.name
messages: list[Message] = parse_messages(payload)
runtime_config: dict[str, object] = build_config()
```

### Avoid vague and inflated words

Do not use vague words to avoid naming the real responsibility.

Bad:

```text
model_utils.py
data_helper.py
runtime_manager.py
common.py
base_processor.py
```

Good:

```text
capture.py
credentials.py
runtime.py
paths.py
latency_stats.py
```

Avoid `Helper`, `Helpers`, `Utility`, `Utilities`, `Util`, `Utils`, `Common`,
`Shared`, `Base`, `Core`, `Manager`, and `Processor` unless the name is a
platform term or the role is truly exact.

## Vocabulary and role words

Choose role words deterministically. A deterministic suffix tells a reader what
kind of boundary or owner they are looking at.

Use these meanings consistently:

| Role word   | Use when                                          |
| ----------- | ------------------------------------------------- |
| `Config`    | Configuration for one area.                       |
| `Example`   | One documented workflow or sample input.          |
| `Model`     | A supported model name or its public metadata.    |
| `Variant`   | A documented version of a Reactor model.          |
| `Client`    | A caller at an external API or platform boundary. |
| `Parser`    | Converts raw input into structured values.        |
| `Validator` | Checks a value and reports invalidity.            |
| `Formatter` | Converts a value into display, log, or wire text. |
| `Runner`    | Owns a top-level command.                         |
| `Result`    | A completed operation's structured output.        |
| `Stats`     | Aggregated measurements or counters.              |

Do not use a suffix just because a name feels too short. If the role is not
real, rename the symbol to the concrete domain concept.

Bad:

```python
class RuntimeManager: ...


def process(data): ...
```

Good:

```python
class RecordingSession: ...


def build_examples(source_items): ...
```

## Functions and methods

Function and method names should describe the action and the domain item being
acted on without repeating context already supplied by the owner.

Rules:

- Start with the action unless a framework convention requires another shape.
- Include enough domain context to read clearly at the call site.
- Do not use generic names such as `process`, `handle`, `run`, `execute`,
  `manage`, `perform`, or `do_work` when the action can be named.
- Use `handle` only for callbacks, framework/event boundaries, or signal
  handlers.
- Use `read` for reading values from a source into memory.
- Use `get` for immediate access that does not imply work, mutation, or I/O.
- Use `set` only for assigning a value directly.
- Use `reset` only for returning to an initial state.
- Use `build` for constructing a value from existing values.
- Use `create` when making a new independent durable or domain value.
- Use `choose` when selecting the final value from inputs, defaults, and
  constraints.
- Use `parse` for raw input to structured data.
- Use `decode` for encoded bytes or serialized payloads into typed values.
- Use `encode` for typed values into bytes or serialized payloads.
- Use `validate` for checking and reporting invalidity.
- Use `sanitize` only when the function actually transforms input into a safe
  external representation.
- Avoid positional boolean parameters. Use options, enums, or explicit function
  names when a boolean would be ambiguous.

Bad:

```python
def process(value): ...


def handle_data(data): ...


def run(model_name, output_dir): ...
```

Good:

```python
def validate_prompt(text, max_length): ...


def build_examples(source_items): ...


def record_video(model_name, output_dir): ...
```

### One concept per function name

If the function name needs `and`, `or`, `with`, `plus`, or a vague umbrella verb,
the function may own too many concepts.

Bad:

```python
def validate_and_upload_image(image, session): ...
```

Good:

```python
def validate_image(image): ...


def upload_image(image, session): ...
```

### Boundary names

At boundaries, name the conversion explicitly.

Bad:

```python
def transform(item): ...
```

Good:

```python
def build_example(raw_item): ...


def parse_model_name(candidate): ...
```

## Booleans and predicates

Boolean names must read as assertions at the use site.

Rules:

- Use `is_` for state or characteristics.
- Use `has_` for possession or presence.
- Use `can_` for capability.
- Do not introduce `should_` in new local names unless an external framework owns
  that spelling.
- Avoid negative names such as `is_not_ready` when the positive form is clearer.
- Do not name booleans like nouns that could be non-boolean values.
- Prefer the boolean name that matches the branch without double negation.

Bad:

```python
remote = args.remote
token = credential.is_available()
not_ready = status != "ready"
```

Good:

```python
is_remote = args.remote
has_credential = credential.is_available()
is_ready = status == "ready"
```

Bad:

```bash
ready='false'
if [[ "${ready}" != 'true' ]]; then
  fail 'not ready'
fi
```

Good:

```bash
is_ready='false'
if [[ "${is_ready}" != 'true' ]]; then
  fail 'not ready'
fi
```

## Files and directories

Files and directories define ownership. Name them for the behavior or entity
they own, not for reuse intent.

Rules:

- Python source filenames use `snake_case.py`, except Python-owned files such as
  `__init__.py` and `__main__.py`.
- Python sibling filename prefixes must be unique unless the quality policy
  explicitly configures an exception.
- Shell scripts use lowercase `.sh` names. Mise tasks and Git hooks keep their
  extensionless entrypoint names.
- Bash files in the same directory must not share the first filename component
  before `_` or `-`.
- Related script families own a subdirectory instead of accumulating prefixed
  sibling files.
- Source modules under `src/` are named for cohesive capabilities:
  configuration, discovery, execution, live controls, media, and host nodes.
- Name development-check modules for the rule or workflow they enforce.
- Do not create catch-all files or directories for unrelated code.
- Do not move code into shared locations just because a future caller might
  appear.
- Promote shared code only when there is a repeated concept and a stable owner.
- A directory named by a broad layer is acceptable only when the project
  architecture explicitly owns that layer.

Bad:

```text
src/helpers.py
src/utils.py
src/models.py
src/misc.py
scripts/do_stuff.sh
```

Good:

```text
src/media/capture.py
src/discovery/store.py
src/execution/helios/request.py
.mise/tasks/docs/build
```

## Python

Use the Python casing and structure rules below.

### Python case rules

Rules:

- Modules and packages use `snake_case`.
- Functions, methods, variables, and parameters use `snake_case`.
- Classes, dataclasses, and exception types use `PascalCase`.
- Constants use `UPPER_SNAKE_CASE`.
- CLI flags use lowercase kebab case, such as `--model-name` and
  `--output-dir`.
- Environment variables use `UPPER_SNAKE_CASE`.
- Avoid one-letter names except tiny conventional scopes such as `i` in a short
  loop.
- Preserve provider capitalization in external names such as `REACTOR_API_KEY` and
  Reactor model IDs.

Bad:

```python
class recording_details: ...


MAXLEN = 512


def BuildExamples(data): ...
```

Good:

```python
class ExecutionConfig: ...


MAX_LENGTH = 512


def build_examples(source_items): ...
```

### Python modules and imports

Rules:

- Keep import aliases rare. Use aliases only for standard, widely understood
  conventions or real collision avoidance.
- Named imports keep their exported name unless a collision forces an alias.
- If aliasing is required, use a domain or module component that explains the
  collision.
- Do not create package-level re-export layers only to preserve old names.
- Keep `__all__` names accurate and ordered according to local lint rules.

Bad:

```python
from src.settings.settings import Settings as Thing
```

Good:

```python
from src.settings.settings import Settings
```

### Python types and dataclasses

Rules:

- Dataclass names describe the domain value they represent.
- Field names describe the value inside the owning type without repeating the
  type name.
- Use `Path` variables with names that reveal whether they point to a directory,
  file, model, result, or repository root.
- Use `*_path` for filesystem paths and `*_dir` only for directories.
- Use `*_id` only for real identifiers, not arbitrary names or labels.
- Use `*_name` for display or provider names.
- Use `*_key` for dictionary keys and supported variant keys.

Bad:

```python
@dataclass
class WorkflowExample:
    workflow_example_text: str
    workflow_example_result: str
```

Good:

```python
@dataclass
class WorkflowExample:
    text: str
    output: str
```

### Python boundary names

Rules:

- Keep raw provider or CLI names at the boundary.
- Translate external names into domain names before passing values inward when
  the external name is not the domain concept.
- Keep Reactor credential lookup inside the credential boundary.
- Keep path construction in config/path owners rather than rebuilding paths in
  business logic.
- Name functions that cross boundaries for the operation they perform.

Bad:

```python
def data(value): ...


token = os.environ["REACTOR_API_KEY"]
```

Good:

```python
def build_workflow(model_name, prompt, duration_seconds): ...


token = read_token(cli_token)
```

## Bash

Bash naming follows Google shell guidance where it fits this repository, with
local overrides for mise tasks and Git hooks.

### Bash case rules

Rules:

- Shell source file stems use lowercase words separated by hyphens or
  underscores.
- Mise tasks and Git hooks keep the names their tools require.
- Other executable shell scripts use `.sh`.
- Sourced libraries use `.sh` and are not executable.
- Functions and mutable variables use `lower_snake_case`.
- Function-local variables use `lower_snake_case`.
- Constants, readonly values, exported environment variables, and externally
  configured values use `UPPER_SNAKE_CASE`.
- Do not use the `function` keyword for new functions. Use `name() { ...; }`.

Bad:

```text
TrainScript.sh
build-script.sh
helpers.sh
```

Good:

```text
main.sh
lint.sh
quality.sh
report.sh
```

Bad:

```bash
function Train() {
  local TMP="$1"
}
```

Good:

```bash
recording_prepare() {
  local output_dir="$1"
}
```

### Bash variables

Rules:

- Loop variables describe the item being iterated.
- Use `tmp_dir` or `tmp_file` only for actual temporary filesystem paths.
- Avoid vague names when a domain name is available.
- Avoid shell-reserved and shell-special names for unrelated values.
- Initialize variables before use.
- Prefer explicit empty strings or arrays over relying on unset variables.
- Declare function-specific variables with `local`.
- Separate `local`, `declare`, `readonly`, and `export` from command
  substitutions when the command status matters.

Bad:

```bash
X=/tmp/a
for i in "${things[@]}"; do
  do_it "${i}"
done

local output="$(generate_results)"
```

Good:

```bash
readonly WORKFLOWS_DIR="${ROOT_DIR}/workflows"

for workflow_file in "${workflow_files[@]}"; do
  validate_workflow "${workflow_file}"
done

local result_output
result_output="$(generate_results)" || return 1
```

### Bash functions

Rules:

- Private functions begin with `_` and are callable only inside their defining
  file.
- Public sourced functions begin with their family or domain namespace,
  followed by the action, such as `server_start`, `restart_read_state`, or
  `package_prepare`.
- Entrypoint-local functions are private except for `main`.
- Within the owner namespace, function names use verb phrases when the function
  has side effects.
- Functions that print data to STDOUT should be named for the data printed.
- Functions that validate should return status and log errors deliberately.
- Do not name scripts or functions after shell builtins or common commands.
- Do not make function names so generic that logs and stack traces lose context.

Bad:

```bash
test() {
  ...
}

run() {
  ...
}

process() {
  ...
}
```

Good:

```bash
venv_python() {
  ...
}

recording_prepare() {
  ...
}

validate_model_dir() {
  ...
}
```

### Bash environment names

Rules:

- Environment variables are `UPPER_SNAKE_CASE`.
- Export only variables child processes need.
- Do not overwrite important shell environment names casually.
- Validate configured environment variable names before using indirect
  expansion.
- Name required environment values by the external contract when the runtime or
  provider platform owns the name.

Bad:

```bash
export token="${TOKEN}"
name="$1"
printf '%s\n' "${!name}"
```

Good:

```bash
export COMFYUI_PATH="${COMFYUI_PATH}"

env_name="$1"
if [[ ! "${env_name}" =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
  printf 'error: invalid environment variable name\n' >&2
  return 1
fi
printf '%s\n' "${!env_name}"
```

## JavaScript

TypeScript owns the ComfyUI browser extension. JavaScript owns build commands,
configuration, and quality tooling. These naming rules apply to both languages.

### JavaScript case rules

Rules:

- Functions, parameters, mutable variables, and normal constants use `lowerCamelCase`.
- Classes use `PascalCase` only when instance identity is real.
- Static constant properties and environment-owned names may use `UPPER_SNAKE_CASE`.
- Object properties use `lowerCamelCase` unless they mirror an external contract.
- Unused parameters start with `_`.
- Do not use leading underscores for privacy. Keep private values local to the module.
- Do not use all-caps variables for ordinary local constants.

Bad:

```js
const SETTINGS = readSettings();
function Build_Dialog(settings_value) {}
const _privateValue = true;
```

Good:

```js
const settings = readSettings();
function buildDialog(settings) {}
const isEnabled = true;
```

### JavaScript files

Rules:

- Name module files for the concept they own.
- Prefer nouns for data/config modules and verbs for small executable scripts only when the file is command-like.
- Avoid generic file names such as `helpers.js`, `utils.js`, `index.js`, `common.js`, and `misc.js`.
- Keep settings, live controls, help rendering, discovery, and build paths in their existing owners.

Bad:

```text
web/utils.ts
web/shared/helpers.ts
web/settings/helpers.ts
src/misc/index.js
```

Good:

```text
web/help/links.ts
web/settings/api.ts
web/live/controls.ts
src/workflows/validate-links.js
```

### JavaScript functions

Rules:

- Use verbs for functions that perform work: `build`, `copy`, `display`, `validate`, `write`.
- Use nouns for values returned by functions only when the function name still reads as an action, such as `readPackageName`.
- Use `is`, `has`, or `can` for boolean-returning functions.
- Name boundary functions by the boundary they own: `readSettings`, `buildHelp`, `sendCommand`.
- Avoid pass-through names that only restate another function.

Bad:

```js
function doStuff(input) {}
function process(data) {}
function check(value) {}
```

Good:

```js
function buildHelp(page) {}
function buildNodeHelp(markdown) {}
function isConnected(session) {}
```

### JavaScript modules and exports

Rules:

- Prefer named exports for reusable module code.
- Avoid default exports in repo-owned modules unless a tool requires one.
- Do not create namespace objects only to group functions.
- Do not export mutable variables as a module contract.
- Import the owning leaf module instead of a broad barrel.

Bad:

```js
export default {
    buildPage() {},
};
```

Good:

```js
export function buildPage(page) {
    return page;
}
```

## HTML, CSS, and content

Name ComfyUI controls, styles, and help files for the component or task they describe.

Rules:

- Data attributes use kebab-case because they are HTML attributes.
- CSS classes should describe the component or state they style.
- CSS custom properties use kebab-case and should identify the value's role.
- Node help filenames use the exact registered node ID.
- Do not hide user-visible copy in variable names or comments. Put copy in the owning component, localization file, or authored guide.

Bad:

```html
<div data-deviceClass="phone"></div>
```

Good:

```html
<div data-device-class="phone"></div>
```

## Data, models, and external boundaries

Keep identifiers required by the current ComfyUI and Reactor APIs exact.
Project-owned node IDs, saved keys, routes, and settings may change as part of a
requested replacement. Update affected callers and examples together and migrate
required stored data directly. Do not keep old aliases or discard user data.

Rules:

- Keep Reactor model identifiers and provider spellings exact.
- Prefix public node IDs with `ReactorInc`; display names start with `Reactor`.
  Do not derive stable IDs from mutable display labels.
- Keep ComfyUI callback names and required provider method names exact.
- Use title case for node names, workflow titles, and note titles. Capitalize
  major words and preserve model names and acronyms, such as
  `Reactor Helios: Generate Video`. Use sentence case for parameters, sockets,
  buttons, tooltips, status messages, and note body text.
- Keep visible labels in schemas, `locales/en/nodeDefs.json`, and workflow notes
  consistent. A label-only change must not alter saved keys or output positions.
  Change stored structures only when the requested behavior requires it.
- Name example workflows for the model and the user task. When renaming an
  example, update its links and affected connections in the same change.
- Add units where needed, such as `duration_seconds` and `timestamp_us`.
- Never include prompts, tokens, private identifiers, or machine paths in public
  artifact names.
- Keep narrow, documented exceptions for names imposed by ComfyUI or Reactor.

Bad:

```python
model_key = "myNewThing"
workflow_name = "example_1"
result_field = "thing"
```

Good:

```python
model_name = "reactor/helios"
workflow_name = "text-to-video"
result_field = "duration_seconds"
```

## Review checklist

Before accepting a new name, ask:

- Does the name describe the role or domain concept instead of the type shape?
- Is the name clear at the call site?
- Is context supplied by the owner omitted from the local name?
- Does the name avoid vague role words unless the role is real?
- Does the name use the correct Python, Bash, or frontend case rule?
- Does the file or directory name describe ownership?
- Does the function name describe the action and domain item?
- Does each boolean read as a positive assertion?
- Are external names isolated to boundary modules?
- Are model, data, and result names treated as contracts?
- Does the name meet the casing, vocabulary, prefix, and folder rules?
