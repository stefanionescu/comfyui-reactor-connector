# Reactor Connector Cleanup Plan

## Status and scope

This plan starts from the current repository state. Before implementation, inspect the
working tree and preserve any unrelated changes that appear after this plan is updated.

The goal is to give each value and operation one clear owner, remove duplicated or unused
behavior, and keep provider-specific requirements inside their provider implementation.

The cleanup covers runtime ownership, request execution, route responses, configuration,
media-unit conversion, frontend pricing metadata, and browser response validation.
`quality/` and every task or configuration entry point that governs it remain unchanged.

## Contents

- [Invariants that must not change](#invariants-that-must-not-change)
- [Existing quality policy](#existing-quality-policy)
- [Final ownership model](#final-ownership-model)
- [Sequential implementation](#sequential-implementation)
- [Resulting source-shape expectations](#resulting-source-shape-expectations)
- [Out-of-scope work](#out-of-scope-work)

## Invariants that must not change

- Keep every ComfyUI node identifier unchanged. Saved workflows depend on identifiers such
  as `ReactorIncViskoDynamicGenerate`.
- Keep every English node display name in `locales/en/nodeDefs.json` in the form
  `<model/action title> (reactor)`. All 18 current node titles already have the correct
  suffix and none has an extra `Reactor` prefix. In particular, keep
  `Visko Dynamic: Generate Video (reactor)` exactly as written.
- Do not edit `AGENTS.md`, `rules/`, `quality/`, or any quality task or configuration entry
  point while implementing this plan.
- Do not weaken the declarative-config checker and do not add a path-specific exclusion for
  the model registry.
- Preserve the security and resource-lifetime behavior of authentication, cancellation,
  media preparation, recording download, reservation, and cleanup code.
- Do not replace the connector's bounded Reactor authentication/download or killable media
  workers with the less constrained Reactor SDK or ComfyUI helpers.
- Do not introduce a global `dataclasses.py`, `types.py`, `common.py`, `helpers.py`, or
  `utils.py`. Data carriers stay with the subsystem that owns them.
- Do not introduce frontend dialog base classes. The dialogs have different state and
  lifecycle behavior, and inheritance would hide rather than remove that difference.
- Do not deduplicate `NODE_REGISTRATIONS` and `NODE_MODELS` by making one runtime-derived.
  Their deliberate agreement is checked against the real ComfyUI schemas.
- Replace internal response contracts directly and update their consumers together. Do not
  add compatibility versions, aliases, forwarding wrappers, or parallel response paths.

## Existing quality policy

Use the existing rules and checks under `quality/` to assess the planned changes. Keep
numeric limits in their current configuration owners; do not duplicate or redefine them in
this plan.

- Python and Bash naming policy: `quality/config/naming/policy.json`.
- TypeScript naming policy: `quality/config/naming/javascript.json`.
- Banned naming terms: `quality/config/naming/terms.json`.
- Python file and function limits: `quality/config/python/limits.py`.

Keep the Python and Bash private-name conventions in `rules/`. A private prefix does not
exempt a name from the configured character, word-count, or vocabulary checks. TypeScript
keeps its separate naming convention.

Use existing scoped checks during implementation. Fix failures caused by the planned
changes in the affected source, not by changing quality rules, thresholds, exceptions,
exclusions, suppressions, or task configuration. Report unrelated existing failures
separately; do not expand the cleanup to make them disappear.

The naming checks for the affected runtime and frontend scopes are:

```bash
uv run --no-sync python -m quality.repository.naming.runner --scope src
bun quality/repository/naming/check.js --scope frontend
```

Run these after the source changes, not while editing this plan. A naming-check pass does
not establish that every quality check or runtime behavior passes. Report the checks
actually run and their results without claiming broader verification.

## Final ownership model

| Concern | Owner after cleanup | Representation |
| --- | --- | --- |
| Declarative model facts | `config/models/identities.py` | One plain nested dictionary; no classes, calls, or comprehensions |
| Typed model capability view | `src/model_registry.py` | Frozen, slotted `ModelDefinition` plus derived connection index |
| Provider-selected recording interval | `src/execution/operation.py` | Frozen, slotted `RecordingWindow` |
| Provider-neutral live-control values | `src/execution/operation.py` | Frozen, slotted `ControlValues` |
| Browser/live options | `src/live/state.py` | Frozen, slotted `LiveOptions`, constructed at the Comfy/live boundary |
| Admission ticket | `src/execution/admission.py` | Mutable, identity-based `_AdmissionTicket` private to the queue owner |
| Catalog state and storage version | `src/discovery/store.py` and `config/discovery.py` | Store-private `_ModelState` and one format constant |
| Execution configuration snapshot | `src/settings/execution.py` | Frozen, slotted dataclass next to generation tracking |
| Process runtime owner | `src/runtime.py` | Ordinary lifecycle class next to initialization/access |
| Settings conflict | `src/settings/conflict.py` | Settings-owned exception used by the HTTP boundary |
| Configured media-limit conversion | `src/media/units.py` | One pure function reused by runtime media boundaries |
| Frontend pricing exceptions | `config/web/pricing.ts` | One declarative metadata object |
| Runtime browser validation | domain `schema.ts` files | Valibot schemas and inferred output types |

The rule for classes and dataclasses is ownership, not file type. Keep a class when it owns
mutable state, a resource, or a lifecycle. Use a frozen/slotted dataclass for an immutable
cross-function value. Put an owner-private carrier beside its owner. Do not group unrelated
dataclasses merely because they are dataclasses.

## Sequential implementation

Apply the ownership and contract changes before deleting obsolete modules. Regenerate the
tracked browser artifact only after its TypeScript sources are complete.

### Step 1: make the model registry declarative again

This must happen first because execution, discovery, and live controls all consume the
registry. The configuration file becomes data only; runtime typing and derived indexes move
to `src/`.

Replace the runtime objects in `config/models/identities.py` with one declarative
`MODEL_IDENTITIES` dictionary. Preserve the current ten model keys and every current field
value. Each record contains `guide_slug`, `connection_name`, `title`, `prompt_limit`,
`prompt_kind`, `is_empty_prompt_allowed`, `camera_axes`, `prompt_command`,
`has_audio_prompt`, `has_pointer`, and `has_prompt_passthrough`. Rename the existing boolean
fields to these predicate names while preserving their values. Keep only
configuration imports, the literal table, and `__all__` in that module. Order the imports
using the configured Python import policy. Do not leave a class, constructor call, or
comprehension under `config/`.

Add `src/model_registry.py` as the typed runtime owner. It contains:

- an internal `_ModelRecord` `TypedDict` with the same fields as each configuration record;
- a frozen, slotted `ModelDefinition` dataclass with typed fields and an `Attributes:`
  section documenting every public field;
- `MODELS`, built by converting every declarative record to `ModelDefinition`;
- `MODELS_BY_CONNECTION`, derived from `MODELS` by connection name;
- `__all__ = ["MODELS", "MODELS_BY_CONNECTION", "ModelDefinition"]`.

Use `from __future__ import annotations` in the new runtime module and give `_ModelRecord`
a docstring describing the configuration record. Keep `_ModelRecord` inside the top-level
`TYPE_CHECKING` block. Order imported names by the
configured import policy, including `cast`, `Literal`, and `TYPE_CHECKING` in that order.
Use a quoted type expression if `cast()` refers to `_ModelRecord`; the type does not exist
at runtime. Do not add runtime validation of this trusted, repository-owned literal table.

Apply these import and identifier changes:

| File | Replace |
| --- | --- |
| `scripts/nodes/schema.py` | `from ...config.models.identities import MODEL_IDENTITIES`; replace `model not in MODELS` with `model not in MODEL_IDENTITIES` |
| `src/comfy/interaction.py` | `from ..model_registry import MODELS_BY_CONNECTION` |
| `src/discovery/views.py` | `from ..model_registry import MODELS` |
| `src/live/control/lease.py` | `from ...model_registry import MODELS_BY_CONNECTION, ModelDefinition` |
| every file under `src/execution/*` currently importing `MODELS` from `config.models.identities` | import `MODELS` from the runtime `model_registry` module using the corresponding relative path |

No consumer may import `ModelDefinition`, `MODELS`, or `MODELS_BY_CONNECTION` from
`config/` after this step. Only the schema-generation script reads the raw declarative
table.

Update definition attribute reads in `src/live/control/lease.py` from `allow_empty_prompt`,
`supports_audio_prompt`, and `supports_pointer` to `is_empty_prompt_allowed`,
`has_audio_prompt`, and `has_pointer`. In `src/live/control/interaction.py`, replace
`definition.supports_prompt_passthrough` with `definition.has_prompt_passthrough`.
Keep current invitation wire keys and `LiveOptions` keyword arguments unchanged: these
internal model-field renames must not alter the browser contract.

### Step 2: colocate owner-private classes and dataclasses

Do these moves before changing their callers so each import transition has one destination.

#### Admission ticket

Move `AdmissionTicket` into `src/execution/admission.py` immediately before
`SessionAdmission` and rename it `_AdmissionTicket`. Update the queue, set, method
annotations, and construction site to use the private name. Remove the
`.state` import and delete `src/execution/state.py` in Step 11.

Keep `_AdmissionTicket` mutable, slotted, and identity-based because the queue owner stores
the same live ticket in a `deque` and a `set`. Do not export it. Declare only
`SessionAdmission` in the module's `__all__`. Rename its internal `capacity` attribute
to `_capacity` and update the two capacity checks.

#### Model state

Move `ModelState` into `src/discovery/store.py` before `ModelStore` and rename it
`_ModelState`. Update its annotations and construction sites. Add the
required `hashlib` and `dataclass` imports, remove the `.state` import, and delete
`src/discovery/state.py` in Step 11. Keep the state private to the store and do not export it.
Rename `ModelStore.path` to `_storage_path` and update its three uses to identify the
filesystem path explicitly.

Rename the store-private `merge_observations()` to `_merge_observations()` and update
its two callers. Step 7 changes
`_ModelState.to_json()` to use the shared catalog
storage version.

#### ExecutionConfiguration

Move `ExecutionConfiguration` to the top of `src/settings/execution.py`, before
`ConfigurationGeneration`, with `from dataclasses import field, dataclass`. Update imports in
`src/settings/store.py`, `src/comfy/execution.py`, and the renamed
`src/execution/session/capture.py` to read it from the settings execution module using
`from .execution import ExecutionConfiguration`,
`from ..settings.execution import ExecutionConfiguration`, and
`from ...settings.execution import ExecutionConfiguration`, respectively. Apply the session
import change to `run.py` first; Step 5 moves that file. Delete
`src/settings/state.py` in Step 11.

Keep `ExecutionConfiguration` frozen and slotted. Expand its class docstring with an
`Attributes:` section for `settings`, `credential`, and `generation`. Rename the module-private
`execution_settings()` to `_execution_settings()` and update both calls.
`src/settings/execution.py` exports `ConfigurationGeneration` and
`ExecutionConfiguration` only.

#### Runtime

Move the complete `Runtime` class from `src/state.py` to the top of `src/runtime.py`, after
the service imports and before `_runtime`. Delete `src/state.py` in Step 11. The final
`src/runtime.py` owns both construction and access to the process-wide services; it must not
re-export `Runtime` solely to recreate the removed module.

Keep `Runtime` public because it is the return contract of `get_runtime()`. Add an
`Attributes:` section for `sessions`, `browsers`, `configuration`, and `discovery`. Declare
`Runtime`, `get_runtime`, and `initialize_runtime` in the module's `__all__`.

Keep `src/live/state.py`, `src/execution/session/state.py`, and `src/media/state.py`. Each has
multiple related values used throughout its subsystem, so merging those files elsewhere
would worsen ownership rather than simplify it. Also keep `src/settings/conflict.py`:
`SettingsConflictError` is settings-owned but intentionally crosses into the HTTP guard so
that stale writes receive status 409. Moving that exception into a global class dump would
make ownership less clear.

### Step 3: remove the execution-to-live domain dependency

Add `ControlValues` to `src/execution/operation.py` before `VideoOperation`:

```python
@dataclass(frozen=True, slots=True)
class ControlValues:
    """Provider-neutral values used to construct optional browser controls.

    Attributes:
        prompt: Text shown in the live prompt control.
        is_passthrough_enabled: Whether prompt changes continue to the provider immediately.
        audio_prompt: Text shown in the optional audio prompt control.
        is_audio_enabled: Whether the audio prompt control starts enabled.
    """

    prompt: str
    is_passthrough_enabled: bool = False
    audio_prompt: str = ""
    is_audio_enabled: bool = False
```

Change the protocol method from:

```python
def live_options(self, *, webcam: WebcamFrames | None = None) -> LiveOptions:
```

to:

```python
def build_control_values(self) -> ControlValues:
```

Remove the `TYPE_CHECKING` imports of `LiveOptions` and `WebcamFrames` from
`src/execution/operation.py`. Export `ControlValues`, `RecordingWindow`, and
`VideoOperation` in `__all__`.

Add an `Attributes:` section to `VideoOperation` for `model_name`, `fallback_fps`, and
`requires_audio`. Add an `Attributes:` section to `VideoInputs` for `prompt`,
`duration_seconds`, `seed`, and `image`; subclasses document only the public fields they add.

In `src/execution/inputs.py`, remove the `LiveOptions`, `WebcamFrames`, `TYPE_CHECKING`, and
future-annotations additions that existed only for `live_options()`. Replace that method with:

```python
def build_control_values(self) -> ControlValues:
    """Return the standard browser-control values for this operation."""
    return ControlValues(self.prompt)
```

In `src/execution/visko/request.py`, remove the live-state and webcam imports and replace the
Visko override with:

```python
def build_control_values(self) -> ControlValues:
    """Return sound and passthrough values selected for browser controls."""
    return ControlValues(
        self.prompt,
        is_passthrough_enabled=self.prompt_passthrough,
        audio_prompt=self.audio_prompt,
        is_audio_enabled=self.audio_enabled,
    )
```

Add this boundary constructor to `src/comfy/interaction.py`:

```python
def build_live_options(request: VideoOperation, *, webcam: WebcamFrames | None = None) -> LiveOptions:
    """Translate execution-owned control values into live-session options."""
    values = request.build_control_values()
    return LiveOptions(
        request.model_name,
        values.prompt,
        webcam,
        passthrough=values.is_passthrough_enabled,
        audio_prompt=values.audio_prompt,
        audio_enabled=values.is_audio_enabled,
    )
```

Add `from __future__ import annotations` to `src/comfy/interaction.py`, import
`TYPE_CHECKING` beside its existing typing imports, and import `WebcamFrames` only inside a
`TYPE_CHECKING` block. Change `prepare_interaction()` to call
`build_live_options(request)` instead of `request.live_options()`.

Rename the module-private `BrowserSender`, `wait_for_controls()`, `prepare_camera()`, and
`prepare_controls()` declarations with one leading underscore and update all internal uses,
including quoted type references. Export only `build_live_options` and `prepare_interaction`
through `__all__`.

In `src/nodes/sana/webcam.py` and `src/nodes/x2/webcam.py`, use
`from ...comfy.interaction import build_live_options` and pass
`controls=build_live_options(request, webcam=camera)`.

The resulting execution package has no import from `src.live` or `src.media.webcam`.

### Step 4: preserve Fast recording behavior

Keep the existing `max_capture_seconds` argument and provider-response checks in
`VideoOperation.configure()`, the session caller, and all adapters. Keep `RecordingWindow`
as the immutable provider-selected interval.

Do not substitute `request.duration_seconds` for the configured maximum. Those bounds are
not equivalent: that substitution could reject a provider response currently accepted within
the configured maximum. A stricter bound is a behavior change, not just interface cleanup.

The Fast-only argument on the common interface remains a known cleanup target, deferred from
this implementation plan until a behavior-preserving design is specified. Do not introduce
`OperationResources`, pass every adapter `Settings`, or mutate a frozen request to hide it.

### Step 5: assign request validation and use precise execution names

Move the session implementation with:

```bash
git mv src/execution/session/run.py src/execution/session/capture.py
```

Rename the public Comfy boundary `execute_video()` to `generate_video()` and update every
node import and call under `src/nodes/`. This is an internal source rename; required ComfyUI
class methods named `execute` remain unchanged.

In `src/comfy/execution.py`, rename `_admitted_run()` to `_generate_admitted_video()`. In the
renamed `src/execution/session/capture.py`, rename `run_video()` to `capture_video()`, `_run()`
to `_capture_session()`, and `_generate()` to `_capture_generation()`. Update imports and
calls with each rename; do not leave aliases or forwarding wrappers.

Keep `request.validate(snapshot.settings)` in `generate_video()`. It rejects bad input before
report creation, admission, transport construction, or billable provider work. Remove the
second validation call from `capture_video()` and update its docstring to state that it
captures an already validated operation and cleans up every outcome.

Do not add a `validated` flag or a second wrapper type. `capture_video()` has one caller and
is the internal continuation of the validated `generate_video()` path.

### Step 6: make routes own response presentation and remove dead fields

Keep authorization in the generic guard and put response fields in the route or store that
owns their meaning.

#### Generic route guard

Delete this line from `src/http/guard.py:local_route()`:

```python
result["mutation_allowed"] = not multi_user
```

The guard continues to own local authorization, language scope, safe exception mapping, and
private headers. It no longer changes successful domain payloads.

#### Settings routes and response

Add this method to `ConfigurationRoutes`:

```python
def _add_mutation_permission(self, result: dict[str, Json]) -> dict[str, Json]:
    """Add the settings editor permission to one configuration response."""
    result["mutation_allowed"] = not self.multi_user
    return result
```

Return `self._add_mutation_permission(...)` from `status`, `settings`, `credential`, and
`clear_credential`, so all four successful settings responses retain the field the settings
UI consumes.

In `ConfigurationStore._status()`, delete the local `editable` variable and return only:

```python
return {
    "settings": settings.to_json(),
    "integer_settings": {
        name: {
            "label": translate("main", "settings.limit." + name),
            "minimum": definition["minimum"],
            "maximum": definition["maximum"],
        }
        for name, definition in INTEGER_SETTINGS.items()
    },
    "credential_limit": MAX_CREDENTIAL_CHARACTERS,
    "revision": settings_revision(settings),
    "credential": {"source": source},
}
```

This removes `credential.configured`, `credential.verified`, `editable_settings`, and
`catalog_available`; none is read by the repository frontend.

#### Discovery routes and response

Rename `ModelRoutes._check_status()` to `_add_route_fields()` and make it add both
route-owned fields:

```python
def _add_route_fields(self, result: dict[str, Json]) -> dict[str, Json]:
    """Add catalog permissions and scheduled-check status to one response."""
    result["mutation_allowed"] = not self.multi_user
    if self.checker:
        result["automatic_check"] = self.checker.status(str(result["revision"]))
    return result
```

Use `_add_route_fields()` from `status`, `refresh`, and `rollback`. Delete the
route-level `result["refreshing"] = False` assignment.

Rename `ModelStore._view()` to `_build_status()`, update its callers, and return:

```python
return {
    "revision": state.revision,
    "retrieved_at": state.current.retrieved_at if state.current else None,
    "models": models,
    "can_rollback": state.previous is not None,
}
```

In `ModelStore.refresh()`, return `_promote_owned()` directly and delete the store-level
`result["refreshing"] = False` assignment. Keep `_refreshing` and `_is_refreshing()` as
internal concurrency state used by refresh admission and rollback; only remove its dead
wire representation.

Delete `availability` from both model dictionaries in `src/discovery/views.py`. Delete
`credits_per_dollar`, `refreshing`, `source`, and `scope` from the catalog response. The
Valibot frontend schemas already omit all of these fields, so no browser consumer changes
are required for their removal.

### Step 7: centralize actual constants and remove dead configuration

In `config/discovery.py`, add:

```python
STORAGE_VERSION = 1
```

and export it in `__all__`.

Use `STORAGE_VERSION` for `_ModelState.to_json()["version"]` and the version equality
check in `ModelStore._read()`. Keep the separate integer-type check. This remains separate
from `FORMAT_VERSION`, which owns the
public source snapshot format.

In `src/discovery/contracts.py`, import `MAX_PRICE_AMOUNT` and replace:

```python
not 1 <= conversion <= 10**9
```

with:

```python
not 1 <= conversion <= MAX_PRICE_AMOUNT
```

In `src/discovery/sources.py`, import `FORMAT_VERSION` and replace the snapshot document's
literal `"version": 1` with `"version": FORMAT_VERSION`.

Delete `WORLD_AXES` from `config/generation/world.py` and remove `"WORLD_AXES"` from
`__all__`. Keep `CAMERA_AXES`, `LINGBOT_CAMERA_AXES`, and
`LINGBOT_WORLD_CAMERA_AXES`; those are used by runtime model metadata and controls.

Do not move protocol command strings, error translation keys, HTTP header names, wire field
names, or media format names into config merely because they are literals. They are owned by
the protocol or implementation that interprets them. Configuration is for policy/data that
can vary independently, not a dumping ground for every string.

### Step 8: replace repeated media-limit arithmetic with one unit conversion

Add `src/media/units.py` with this small conversion owner:

```python
"""Convert configured media size units at runtime boundaries."""

_BYTES_PER_MEBIBYTE = 1_048_576


def convert_mebibytes_to_bytes(mebibytes: int) -> int:
    """Return bytes for a configured size measured in mebibytes."""
    return mebibytes * _BYTES_PER_MEBIBYTE


__all__ = ["convert_mebibytes_to_bytes"]
```

Import and use `convert_mebibytes_to_bytes()` at every current runtime multiplication site.
The existing settings call these values megabytes but use binary units; preserve that
conversion and the existing setting names.

| File | Values to convert |
| --- | --- |
| `src/comfy/execution.py` | `max_capture_megabytes`, `max_queue_megabytes` |
| `src/execution/fast/generate.py` | `max_upload_megabytes` |
| `src/execution/inputs.py` | `max_upload_megabytes` |
| `src/execution/ltx/request.py` | `max_upload_megabytes` |
| `src/execution/session/capture.py` | `max_capture_megabytes`, `max_queue_megabytes` |
| `src/media/recording/assemble.py` | `max_capture_megabytes`, `max_queue_megabytes` |
| `src/media/video/components.py` | `max_queue_megabytes`, `max_upload_megabytes` |
| `src/media/video/input.py` | `max_upload_megabytes`, `max_queue_megabytes` |

For example, replace:

```python
settings.max_capture_megabytes * 1_048_576
```

with:

```python
convert_mebibytes_to_bytes(settings.max_capture_megabytes)
```

Do not replace the already named byte constants in `config/serialization.py`,
`config/discovery.py`, or `config/package.py`. Those are byte-valued policy constants, not
runtime unit conversions.

### Step 9: put frontend node pricing behavior in one metadata table

Add `config/web/pricing.ts` with this typed metadata shape:

```typescript
type DurationInputs = readonly [string, string];
type NodePricingRules = Readonly<{
  excludedNodeIds: readonly string[];
  multipliedDurationInputs: Readonly<Record<string, DurationInputs>>;
}>;

/** Node-specific behavior used by the local credit-rate interface. */
export const nodePricingRules: NodePricingRules = {
  excludedNodeIds: ['ReactorIncHeliosAddPrompt', 'ReactorIncLongLiveAddShot'],
  multipliedDurationInputs: {
    ReactorIncFastContinue: ['clip_seconds', 'clip_count'],
  },
};
```

In `web/discovery/rate.ts`, import `nodePricingRules`. Replace the Fast class-name branch in
`requestedSeconds()` with:

```typescript
const factors = node.comfyClass
  ? nodePricingRules.multipliedDurationInputs[node.comfyClass]
  : undefined;
if (factors) {
  const first = value(factors[0]);
  const second = value(factors[1]);
  return first !== undefined && second !== undefined ? first * second : undefined;
}
```

Replace the three-condition exclusion in `bindCreditRate()` with:

```typescript
if (!id?.startsWith('ReactorInc') || nodePricingRules.excludedNodeIds.includes(id)) return;
```

This is intentionally frontend configuration: the rate button must be bound when a ComfyUI
node is created, before a successful discovery response is guaranteed. Do not add another
backend endpoint or make the pricing dialog depend on live-session invitation data.

### Step 10: keep Valibot, but finish the consolidation

Keep `valibot` in `package.json` and `bun.lock`. It provides runtime parsing at four
untrusted browser boundaries and derives TypeScript output types from the validated shapes.
Remove the duplicated schema and error-parsing machinery around it.

Add `web/schema.ts` with this shared error-parser shape:

```typescript
import * as v from 'valibot';
import { browserLimits } from '#config/web/browser.ts';

const publicErrorSchema = v.object({
  error: v.optional(
    v.pipe(v.string(), v.minLength(1), v.maxLength(browserLimits.maxErrorCharacters)),
  ),
});

/**
 * Read a bounded message from a failed local API response.
 * @param value - The untrusted JSON response.
 * @returns The reviewed server message, or undefined for a malformed error response.
 */
export function parsePublicError(value: unknown): string | undefined {
  const result = v.safeParse(publicErrorSchema, value);
  return result.success ? result.output.error : undefined;
}
```

Delete `errorDocumentSchema`, `errorTextSchema`, and `parseModelError()` from
`web/discovery/schema.ts`. Delete their settings equivalents and
`parseSettingsError()` from `web/settings/schema.ts`. Import `parsePublicError` in both API
modules and use it for non-OK responses. A malformed error document falls back to the
existing domain message (`models.requestFailed` or `settings.saveFailed`) instead of throwing
a second, misleading response-shape error.

In `web/settings/schema.ts`, declare one `settingNameSchema` next to
`settingDefinitionSchema`, reuse it inside the loop, and validate `raw` directly with
`settingDefinitionSchema`; remove the redundant `unknownRecordSchema` parse of each field.

In `web/live/schema.ts`, replace the handwritten `InvitationDocument` property list with:

```typescript
const invitationSchema = v.object(invitationEntries);
type InvitationDocument = v.InferOutput<typeof invitationSchema>;
```

Keep the cross-field checks for prompt length, audio-prompt length, unique model keys, and
camera-axis membership. A schema library does not eliminate domain policy, and hiding those
checks inside generic helpers would make them harder to understand.

Do not add Pydantic on the backend. The Python validation is dominated by strict key sets,
resource bounds, localized errors, and cross-field policy; Pydantic would move rather than
remove that code.

### Step 11: remove obsolete source files only after every import has moved

The final deletion set for runtime ownership cleanup is exactly:

```bash
git rm src/discovery/state.py \
  src/execution/state.py \
  src/settings/state.py \
  src/state.py
```

Do not run these deletions before the ownership moves and all affected import updates are
present. Do not retain compatibility modules at the deleted paths.

### Step 12: regenerate the tracked frontend artifact

The TypeScript source changes in Steps 9 and 10 require the tracked bundle to be regenerated.
Do not hand-edit `web/dist/main.js`. The rules require explicit authorization to run a build.
Obtain that authorization before this step; without it, report the generated artifact as
pending rather than claiming the implementation is complete. The required command is:

```bash
mise run frontend:build
```

Artifact change:

- Source inputs: `config/web/pricing.ts`, `web/discovery/rate.ts`, `web/schema.ts`,
  `web/discovery/schema.ts`, `web/discovery/api.ts`, `web/settings/schema.ts`,
  `web/settings/api.ts`, and `web/live/schema.ts`.
- Output path: `web/dist/main.js`.
- Operation: deterministic project frontend bundle generation through
  `.mise/tasks/frontend/build` and `scripts/frontend.mjs`.
- Regenerate from the final source tree without editing or restoring the bundle by hand.

This command generates the affected artifact only. It does not authorize the repository's
check suite, and no build is run while editing this plan.

## Resulting source-shape expectations

After implementation:

- `config/models/identities.py` contains imports, one literal table, and `__all__`; it has no
  dataclass, constructor call, or comprehension.
- `src/model_registry.py` is the only owner of `ModelDefinition`, `MODELS`, and
  `MODELS_BY_CONNECTION`.
- `src/execution` has no import from `src.live` or `src.media.webcam`.
- `VideoOperation.configure()` and Fast provider-response checks retain the configured
  capture maximum and their existing acceptance behavior. Their interface cleanup is deferred.
- Requests are validated once, in `generate_video()`, before admission and transport work.
- The session implementation lives in `src/execution/session/capture.py` and uses precise
  capture-oriented function names.
- `local_route()` authorizes and maps errors but never mutates successful payloads.
- Only settings and catalog routes add `mutation_allowed`; live polling payloads do not carry
  it.
- Catalog payloads do not carry `availability`, `credits_per_dollar`, `refreshing`, `source`,
  or `scope`.
- Settings payloads do not carry `credential.configured`, `credential.verified`,
  `editable_settings`, or `catalog_available`.
- The catalog storage version and public snapshot format each have one named owner.
- Runtime source contains no direct `* 1_048_576` size conversions.
- Frontend pricing behavior has no exact node-ID branches outside
  `config/web/pricing.ts`.
- Valibot schemas remain the single browser response/event validation layer; parallel manual
  response types are not reintroduced.
- Every file under `quality/`, every quality configuration file, and every quality task entry
  point remains byte-for-byte unchanged.
- All 18 node display names remain unchanged and end in ` (reactor)`.

## Out-of-scope work

Do not modify, remove, rename, or replace anything under `quality/`. Do not change the tasks,
manifests, import maps, TypeScript configuration, or other entry points that operate on
`quality/`. Existing scoped quality checks may be used as described above; their
implementation and configuration remain unchanged. Do not add tests, replacement checkers,
or a new scoring system. Editing this plan does not run the implementation checks.

No SDK, HLS, file-lock, Pydantic, ComfyUI dialog, ComfyUI video-input, or frontend
type package replacement is planned. The inspected alternatives do not replace the
connector's important security, cancellation, bounded-I/O, or UI behavior and would not be
a net simplification.
