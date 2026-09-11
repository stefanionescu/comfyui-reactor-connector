# Reactor Connector Cleanup Plan

## Status and scope

This plan is based on the current working tree, including the unfinished model-registry,
recording-window, live-capability, and Valibot changes. It does not assume that `HEAD`
is the implementation baseline and it must not discard or overwrite unrelated uncommitted
work.

The goal is to finish the useful parts of the cleanup, remove the regressions and policy
violations introduced by it, and reduce repository machinery that is actively pushing the
runtime toward worse abstractions.

This is a planning artifact only. Creating this file is the only change made while writing
the plan.

One explicitly requested rules change has already been completed separately from the
implementation steps below: `rules/JAVASCRIPT.md` was removed and the user supplied the
current general-purpose `rules/TYPESCRIPT.md`. Treat that user-edited file as authoritative.
Do not adapt it to this repository or add ComfyUI-specific text to it.

## Invariants that must not change

- Keep every ComfyUI node identifier unchanged. Saved workflows depend on identifiers such
  as `ReactorIncViskoDynamicGenerate`.
- Keep every English node display name in `locales/en/nodeDefs.json` in the form
  `<model/action title> (reactor)`. All 18 current node titles already have the correct
  suffix and none has an extra `Reactor` prefix. In particular, keep
  `Visko Dynamic: Generate Video (reactor)` exactly as written.
- Do not edit `AGENTS.md` or the user-owned `rules/TYPESCRIPT.md`. The TypeScript migration may
  update stale JavaScript terminology and examples in `rules/NAMING.md`, as explicitly
  authorized by the request to make the authored repository TypeScript-only.
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
- Treat the connector's local HTTP endpoints as an internal API with no external
  compatibility promise. If that assumption is false, stop before Step 6 and version the
  response contract instead of silently removing fields.

## Final ownership model

| Concern | Owner after cleanup | Representation |
| --- | --- | --- |
| Declarative model facts | `config/models/identities.py` | One plain nested dictionary; no classes, calls, or comprehensions |
| Typed model capability view | `src/models.py` | Frozen, slotted `ModelDefinition` plus derived connection index |
| Provider-selected recording interval | `src/execution/operation.py` | Frozen, slotted `RecordingWindow` |
| Inputs needed to configure a provider | `src/execution/operation.py` | Frozen, slotted `OperationResources` |
| Provider-neutral live-control values | `src/execution/operation.py` | Frozen, slotted `ControlValues` |
| Browser/live options | `src/live/state.py` | Frozen, slotted `LiveOptions`, constructed at the Comfy/live boundary |
| Admission ticket | `src/execution/admission.py` | Mutable, non-value dataclass private to the queue owner |
| Catalog state and storage version | `src/discovery/store.py` and `config/discovery.py` | Store-private frozen dataclass and one format constant |
| Execution configuration snapshot | `src/settings/execution.py` | Frozen, slotted dataclass next to generation tracking |
| Process runtime owner | `src/runtime.py` | Ordinary lifecycle class next to initialization/access |
| Settings conflict | `src/settings/conflict.py` | Settings-owned exception used by the HTTP boundary |
| MiB-to-byte conversion | `src/media/units.py` | One pure function reused by runtime media boundaries |
| Frontend pricing exceptions | `config/web/pricing.ts` | One declarative metadata object |
| Runtime browser validation | domain `schema.ts` files | Valibot schemas and inferred output types |

The rule for classes and dataclasses is ownership, not file type. Keep a class when it owns
mutable state, a resource, or a lifecycle. Use a frozen/slotted dataclass for an immutable
cross-function value. Put an owner-private carrier beside its owner. Do not group unrelated
dataclasses merely because they are dataclasses.

## Sequential implementation

### Step 1: make the model registry declarative again

This must happen first because execution, discovery, and live controls all consume the
registry. The configuration file becomes data only; runtime typing and derived indexes move
to `src/`.

Replace `config/models/identities.py` completely with:

```python
"""Describe reviewed Reactor model identities and live capabilities."""

from ..generation.fast import MAX_PROMPT_CHARACTERS as MAX_FAST_PROMPT_CHARACTERS
from ..generation.session import MAX_PROMPT_CHARACTERS
from ..generation.video import MAX_EDIT_PROMPT_CHARACTERS
from ..generation.world import LINGBOT_CAMERA_AXES, LINGBOT_WORLD_CAMERA_AXES, MAX_WORLD_PROMPT_CHARACTERS


MODEL_IDENTITIES = {
    "fast-h3": {
        "guide_slug": "fast-h3",
        "connection_name": "reactor/fast-h3",
        "title": "Fast H3",
        "prompt_limit": MAX_FAST_PROMPT_CHARACTERS,
        "prompt_kind": "scene",
        "allow_empty_prompt": False,
        "camera_axes": (),
        "prompt_command": "set_prompt",
        "supports_audio_prompt": False,
        "supports_pointer": False,
        "supports_prompt_passthrough": False,
    },
    "visko-orbis-stable": {
        "guide_slug": "visko-orbis-stable",
        "connection_name": "reactor/visko-orbis-stable",
        "title": "Visko Stable",
        "prompt_limit": MAX_PROMPT_CHARACTERS,
        "prompt_kind": "scene",
        "allow_empty_prompt": False,
        "camera_axes": (),
        "prompt_command": "set_prompt",
        "supports_audio_prompt": True,
        "supports_pointer": False,
        "supports_prompt_passthrough": True,
    },
    "visko-orbis-dynamic": {
        "guide_slug": "visko-orbis-dynamic",
        "connection_name": "reactor/visko-orbis-dynamic",
        "title": "Visko Dynamic",
        "prompt_limit": MAX_PROMPT_CHARACTERS,
        "prompt_kind": "scene",
        "allow_empty_prompt": False,
        "camera_axes": (),
        "prompt_command": "set_prompt",
        "supports_audio_prompt": True,
        "supports_pointer": False,
        "supports_prompt_passthrough": True,
    },
    "helios": {
        "guide_slug": "helios",
        "connection_name": "reactor/helios",
        "title": "Helios",
        "prompt_limit": MAX_PROMPT_CHARACTERS,
        "prompt_kind": "scene",
        "allow_empty_prompt": False,
        "camera_axes": (),
        "prompt_command": "set_prompt",
        "supports_audio_prompt": False,
        "supports_pointer": False,
        "supports_prompt_passthrough": False,
    },
    "lingbot": {
        "guide_slug": "lingbot",
        "connection_name": "reactor/lingbot",
        "title": "LingBot",
        "prompt_limit": MAX_WORLD_PROMPT_CHARACTERS,
        "prompt_kind": "scene",
        "allow_empty_prompt": False,
        "camera_axes": LINGBOT_CAMERA_AXES,
        "prompt_command": "set_prompt",
        "supports_audio_prompt": False,
        "supports_pointer": False,
        "supports_prompt_passthrough": False,
    },
    "lingbot-world-2": {
        "guide_slug": "lingbot-world-2",
        "connection_name": "reactor/lingbot-world-2",
        "title": "LingBot World 2",
        "prompt_limit": MAX_WORLD_PROMPT_CHARACTERS,
        "prompt_kind": "scene",
        "allow_empty_prompt": False,
        "camera_axes": LINGBOT_WORLD_CAMERA_AXES,
        "prompt_command": "set_prompt",
        "supports_audio_prompt": False,
        "supports_pointer": False,
        "supports_prompt_passthrough": False,
    },
    "longlive-v2": {
        "guide_slug": "longlive-v2",
        "connection_name": "reactor/longlive-v2",
        "title": "LongLive",
        "prompt_limit": MAX_PROMPT_CHARACTERS,
        "prompt_kind": "scene",
        "allow_empty_prompt": False,
        "camera_axes": (),
        "prompt_command": "set_shot",
        "supports_audio_prompt": False,
        "supports_pointer": False,
        "supports_prompt_passthrough": False,
    },
    "sana-streaming": {
        "guide_slug": "sana-streaming",
        "connection_name": "reactor/sana-streaming",
        "title": "SANA",
        "prompt_limit": MAX_PROMPT_CHARACTERS,
        "prompt_kind": "edit",
        "allow_empty_prompt": True,
        "camera_axes": (),
        "prompt_command": "set_prompt",
        "supports_audio_prompt": False,
        "supports_pointer": False,
        "supports_prompt_passthrough": False,
    },
    "ltx2": {
        "guide_slug": "ltx",
        "connection_name": "reactor/ltx2",
        "title": "LTX",
        "prompt_limit": MAX_PROMPT_CHARACTERS,
        "prompt_kind": "scene",
        "allow_empty_prompt": False,
        "camera_axes": (),
        "prompt_command": "set_prompt",
        "supports_audio_prompt": False,
        "supports_pointer": False,
        "supports_prompt_passthrough": False,
    },
    "x2": {
        "guide_slug": "x2",
        "connection_name": "xmax/x2",
        "title": "X2",
        "prompt_limit": MAX_EDIT_PROMPT_CHARACTERS,
        "prompt_kind": "edit",
        "allow_empty_prompt": False,
        "camera_axes": (),
        "prompt_command": "set_prompt",
        "supports_audio_prompt": False,
        "supports_pointer": True,
        "supports_prompt_passthrough": False,
    },
}

__all__ = ["MODEL_IDENTITIES"]
```

Add `src/models.py` with exactly:

```python
"""Provide typed access to reviewed model identities and live capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, cast
from ..config.models.identities import MODEL_IDENTITIES

if TYPE_CHECKING:
    from typing import TypedDict

    class ModelRecord(TypedDict):
        """Static model fields declared in configuration."""

        guide_slug: str
        connection_name: str
        title: str
        prompt_limit: int
        prompt_kind: Literal["scene", "edit"]
        allow_empty_prompt: bool
        camera_axes: tuple[str, ...]
        prompt_command: str
        supports_audio_prompt: bool
        supports_pointer: bool
        supports_prompt_passthrough: bool


@dataclass(frozen=True, slots=True)
class ModelDefinition:
    """One reviewed model identity and its static live-control policy."""

    guide_slug: str
    connection_name: str
    title: str
    prompt_limit: int
    prompt_kind: Literal["scene", "edit"]
    allow_empty_prompt: bool
    camera_axes: tuple[str, ...]
    prompt_command: str
    supports_audio_prompt: bool
    supports_pointer: bool
    supports_prompt_passthrough: bool


MODELS = {
    name: ModelDefinition(**cast("ModelRecord", record))
    for name, record in MODEL_IDENTITIES.items()
}

MODELS_BY_CONNECTION = {
    definition.connection_name: definition for definition in MODELS.values()
}

__all__ = ["MODELS", "MODELS_BY_CONNECTION", "ModelDefinition"]
```

Apply these exact import/identifier changes:

| File | Replace |
| --- | --- |
| `scripts/nodes/schema.py` | import `MODEL_IDENTITIES` from `config.models.identities`; replace `model not in MODELS` with `model not in MODEL_IDENTITIES` |
| `src/comfy/interaction.py` | import `MODELS_BY_CONNECTION` from `src.models` |
| `src/discovery/views.py` | import `MODELS` from `src.models` |
| `src/live/control/lease.py` | import `MODELS_BY_CONNECTION, ModelDefinition` from `src.models` |
| every file under `src/execution/*` currently importing `MODELS` from `config.models.identities` | import `MODELS` from `src.models` using the correct relative path |

No consumer may import `ModelDefinition`, `MODELS`, or `MODELS_BY_CONNECTION` from
`config/` after this step. Only the schema-generation script reads the raw declarative
table.

### Step 2: colocate owner-private classes and dataclasses

Do these moves before changing their callers so each import transition has one destination.

#### AdmissionTicket

Move the complete `AdmissionTicket` definition into `src/execution/admission.py`, immediately
after imports and before `SessionAdmission`. Add `from dataclasses import dataclass`, remove
`from .state import AdmissionTicket`, then delete `src/execution/state.py` in full:

```python
"""Admission records shared by the session queue and its callers."""

import asyncio
from dataclasses import dataclass


@dataclass(eq=False, slots=True)
class AdmissionTicket:
    """A wake-up event owned only by the loop that requested admission."""

    loop: asyncio.AbstractEventLoop
    changed: asyncio.Event


__all__ = ["AdmissionTicket"]
```

The class remains mutable and identity-based because it is a live queue ticket held in a
`deque` and a `set`; converting it to a frozen value object would be incorrect.

#### ModelState

Move `ModelState` into `src/discovery/store.py` before `ModelStore`. Add the existing
`hashlib` and `dataclass` imports there, remove `from .state import ModelState`, and delete
`src/discovery/state.py` in full. Its `to_json()` implementation is changed in Step 7 to use
the shared catalog storage version.

#### ExecutionConfiguration

Move `ExecutionConfiguration` to the top of `src/settings/execution.py`, before
`ConfigurationGeneration`, with `from dataclasses import dataclass, field`. Update imports in
`src/settings/store.py`, `src/comfy/execution.py`, and `src/execution/session/run.py` to read it
from `src.settings.execution`. Delete `src/settings/state.py` in full:

```python
"""Private settings and credential snapshots used for execution."""

from .settings import Settings
from ..credentials import Credential
from dataclasses import field, dataclass


@dataclass(frozen=True, slots=True)
class ExecutionConfiguration:
    """One private settings and credential snapshot for an admitted operation."""

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str


__all__ = ["ExecutionConfiguration"]
```

#### Runtime

Move the complete `Runtime` class from `src/state.py` to the top of `src/runtime.py`, after
the service imports and before `_runtime`. Delete `src/state.py` in full. The final
`src/runtime.py` owns both construction and access to the process-wide services; it must not
re-export `Runtime` solely to recreate the removed module.

Keep `src/live/state.py`, `src/execution/session/state.py`, and `src/media/state.py`. Each has
multiple related values used throughout its subsystem, so merging those files elsewhere
would worsen ownership rather than simplify it. Also keep `src/settings/conflict.py`:
`SettingsConflictError` is settings-owned but intentionally crosses into the HTTP guard so
that stale writes receive status 409. Moving that exception into a global class dump would
make ownership less clear.

### Step 3: remove the execution-to-live domain dependency

Add these two carriers to `src/execution/operation.py`, before `VideoOperation`:

```python
@dataclass(frozen=True, slots=True)
class ControlValues:
    """Provider-neutral values used to construct optional browser controls."""

    prompt: str
    passthrough: bool = False
    audio_prompt: str = ""
    is_audio_enabled: bool = False


@dataclass(frozen=True, slots=True)
class OperationResources:
    """Session-owned services available while configuring one provider operation."""

    transport: Transport
    events: SessionEvents
    settings: Settings
```

Change the protocol method from:

```python
def live_options(self, *, webcam: WebcamFrames | None = None) -> LiveOptions:
```

to:

```python
def control_values(self) -> ControlValues:
```

Remove the `TYPE_CHECKING` imports of `LiveOptions` and `WebcamFrames` from
`src/execution/operation.py`. Export `ControlValues`, `OperationResources`,
`RecordingWindow`, and `VideoOperation` in `__all__`.

In `src/execution/inputs.py`, remove the `LiveOptions`, `WebcamFrames`, `TYPE_CHECKING`, and
future-annotations additions that existed only for `live_options()`. Replace that method with:

```python
def control_values(self) -> ControlValues:
    """Return the standard browser-control values for this operation."""
    return ControlValues(self.prompt)
```

In `src/execution/visko/request.py`, remove the live-state and webcam imports and replace the
Visko override with:

```python
def control_values(self) -> ControlValues:
    """Return sound and passthrough values selected for browser controls."""
    return ControlValues(
        self.prompt,
        passthrough=self.prompt_passthrough,
        audio_prompt=self.audio_prompt,
        is_audio_enabled=self.audio_enabled,
    )
```

Add this boundary constructor to `src/comfy/interaction.py`:

```python
def live_options(request: VideoOperation, *, webcam: WebcamFrames | None = None) -> LiveOptions:
    """Translate execution-owned control values into live-session options."""
    values = request.control_values()
    return LiveOptions(
        request.model_name,
        values.prompt,
        webcam,
        passthrough=values.passthrough,
        audio_prompt=values.audio_prompt,
        audio_enabled=values.is_audio_enabled,
    )
```

Add `from __future__ import annotations` to `src/comfy/interaction.py`, import
`TYPE_CHECKING` beside its existing typing imports, and import `WebcamFrames` only inside a
`TYPE_CHECKING` block. Change `prepare_interaction()` to call `live_options(request)` instead
of `request.live_options()`.

In `src/nodes/sana/webcam.py` and `src/nodes/x2/webcam.py`, import `live_options` from
`src.comfy.interaction` and pass `controls=live_options(request, webcam=camera)`.

After this step, `rg "live_options|live\.state|media\.webcam" src/execution` must find no
execution-to-live or execution-to-webcam import. This sentence defines the desired source
state; it is not an instruction to run a verification command while implementing this plan.

### Step 4: localize Fast recording limits without polluting every adapter

Change the protocol signature to:

```python
async def configure(self, resources: OperationResources) -> RecordingWindow:
    """Start generation and return the provider recording interval to save."""
```

In `src/execution/session/run.py`, construct the resources once at the configure boundary:

```python
recording_window = await session.request.configure(
    OperationResources(session.transport, session.events, session.settings)
)
```

Update every adapter's `configure()` signature to take `resources: OperationResources`.
Inside each implementation, use these exact local bindings only when that implementation
needs them:

```python
transport = resources.transport
events = resources.events
```

Apply the following matrix:

| Adapter | Required resource use |
| --- | --- |
| `src/execution/fast/generate.py` | `transport`, `events`, and one local `capture_limit = resources.settings.max_capture_seconds`; pass `capture_limit` to `_queue_clip()` |
| `src/execution/fast/continuation.py` | `transport`, `events`, and one local `capture_limit = resources.settings.max_capture_seconds`; use `capture_limit` in both `_validate_recording_limit()` calls and the final duration check |
| `src/execution/visko/request.py` | `transport` and `events` only |
| `src/execution/helios/request.py` | `transport` and `events` only |
| `src/execution/lingbot/request.py` | `transport` and `events` only |
| `src/execution/longlive/request.py` | `events` only; do not bind `transport` |
| `src/execution/ltx/request.py` | `transport` and `events` only |
| `src/execution/sana/request.py` | `transport` and `events` only |
| `src/execution/x2/request.py` | `transport` and `events` only |

Delete every `del max_capture_seconds` and the `del transport, max_capture_seconds` pair.
Only the two Fast operations may read `resources.settings.max_capture_seconds`.

Keep `RecordingWindow` exactly as an immutable return value. It represents an actual
provider-selected interval and avoids mutating frozen request objects after the provider has
resolved clip timing.

### Step 5: assign request validation to the public execution boundary

Keep `request.validate(snapshot.settings)` in `src/comfy/execution.py:execute_video()`. This
rejects bad input before report creation, admission, transport construction, or billable
provider work.

Delete these two lines from `src/execution/session/run.py:run_video()`:

```diff
-    settings = configuration.settings
-    request.validate(settings)
+    settings = configuration.settings
```

Change its docstring from:

```python
"""Validate before billing and clean up after every execution outcome."""
```

to:

```python
"""Run an already validated operation and clean up every execution outcome."""
```

Do not add a `validated` flag or a second wrapper type. `run_video()` has one caller and is
an internal continuation of the already validated `execute_video()` path.

### Step 6: make routes own response presentation and remove dead fields

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
def _view(self, result: dict[str, Json]) -> dict[str, Json]:
    """Add the settings editor permission to one configuration response."""
    result["mutation_allowed"] = not self.multi_user
    return result
```

Return `self._view(...)` from `status`, `settings`, `credential`, and `clear_credential`, so
all four successful settings responses retain the field the settings UI consumes.

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

Rename `ModelRoutes._check_status()` to `_view()` and make it add both route-owned fields:

```python
def _view(self, result: dict[str, Json]) -> dict[str, Json]:
    """Add catalog permissions and scheduled-check status to one response."""
    result["mutation_allowed"] = not self.multi_user
    if self.checker:
        result["automatic_check"] = self.checker.status(str(result["revision"]))
    return result
```

Use `_view()` from `status`, `refresh`, and `rollback`. Delete the route-level
`result["refreshing"] = False` assignment.

Replace `ModelStore._view()`'s result with:

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
CATALOG_STORAGE_VERSION = 1
```

and export it in `__all__`.

Use `CATALOG_STORAGE_VERSION` for both `ModelState.to_json()["version"]` and both storage
version checks in `ModelStore._read()`. This is separate from `FORMAT_VERSION`, which owns
the public source snapshot format.

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

### Step 8: replace repeated MiB arithmetic with one unit conversion

Add `src/media/units.py` with exactly:

```python
"""Convert configured media size units at runtime boundaries."""

BYTES_PER_MEBIBYTE = 1_048_576


def megabytes_to_bytes(megabytes: int) -> int:
    """Convert the connector's configured whole-megabyte limit to bytes."""
    return megabytes * BYTES_PER_MEBIBYTE
```

Import and use `megabytes_to_bytes()` at every current runtime multiplication site:

| File | Values to convert |
| --- | --- |
| `src/comfy/execution.py` | `max_capture_megabytes`, `max_queue_megabytes` |
| `src/execution/fast/generate.py` | `max_upload_megabytes` |
| `src/execution/inputs.py` | `max_upload_megabytes` |
| `src/execution/ltx/request.py` | `max_upload_megabytes` |
| `src/execution/session/run.py` | `max_capture_megabytes`, `max_queue_megabytes` |
| `src/media/recording/assemble.py` | `max_capture_megabytes`, `max_queue_megabytes` |
| `src/media/video/components.py` | `max_queue_megabytes`, `max_upload_megabytes` |
| `src/media/video/input.py` | `max_upload_megabytes`, `max_queue_megabytes` |

For example, replace:

```python
settings.max_capture_megabytes * 1_048_576
```

with:

```python
megabytes_to_bytes(settings.max_capture_megabytes)
```

Do not replace the already named byte constants in `config/serialization.py`,
`config/discovery.py`, or `config/package.py`. Those are byte-valued policy constants, not
runtime unit conversions.

### Step 9: put frontend node pricing behavior in one metadata table

Add `config/web/pricing.ts` with exactly:

```typescript
/** Node-specific behavior used by the local credit-rate interface. */
export const nodePricingRules = {
  excludedNodeIds: ['ReactorIncHeliosAddPrompt', 'ReactorIncLongLiveAddShot'] as readonly string[],
  multipliedDurationInputs: {
    ReactorIncFastContinue: ['clip_seconds', 'clip_count'],
  } as Readonly<Record<string, readonly [string, string]>>,
} as const;
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

Keep `valibot` in `package.json` and `bun.lock`. The current line count does not justify the
dependency by itself, but runtime parsing at four untrusted browser boundaries and inferred
output types do. The cleanup target is duplicated schema/error machinery, not an artificial
minimum line count.

Add `web/schema.ts` with exactly:

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

### Step 11: remove the most counterproductive quality machinery

Retire the repository-owned function-policy engine. Its single-use/trivial-function and
call-through heuristics require a large exception registry, perform approximate whole-repo
reference analysis, and pressure code toward inlining or false abstraction. Ruff, vulture,
ESLint, SonarJS, knip, madge, and jscpd remain responsible for established language and
dependency checks.

Delete these files in full:

```text
quality/config/repository/functions.py
quality/config/repository/functions.json
quality/repository/functions/__init__.py
quality/repository/functions/policy.py
quality/repository/functions/python.py
quality/repository/functions/references.py
quality/repository/functions/runner.py
quality/repository/functions/semantics.py
quality/repository/functions/shell.py
```

The exact deletion operation is:

```bash
git rm quality/config/repository/functions.py \
  quality/config/repository/functions.json \
  quality/repository/functions/__init__.py \
  quality/repository/functions/policy.py \
  quality/repository/functions/python.py \
  quality/repository/functions/references.py \
  quality/repository/functions/runner.py \
  quality/repository/functions/semantics.py \
  quality/repository/functions/shell.py
```

Then apply these exact removals:

```diff
diff --git a/.mise/tasks/lint/policy b/.mise/tasks/lint/policy
@@
-  uv run --no-sync python -m quality.repository.functions.runner --scope "${policy_scope}"

diff --git a/quality/config/repository/paths.py b/quality/config/repository/paths.py
@@
-FUNCTION_POLICY_EXCLUDED_DIRS = {
-    ".artifacts",
-    ".git",
-    ".ruff_cache",
-    ".venv",
-    "__pycache__",
-}

diff --git a/quality/repository/integrity/policies.py b/quality/repository/integrity/policies.py
@@
-from quality.repository.functions.policy import read_function_policy
@@
-        ("function", read_function_policy),

diff --git a/quality/config/python/rules.py b/quality/config/python/rules.py
@@
-DOCSTRING_SOURCE_PREFIXES = ("src/", "config/", "scripts/", "quality/")
-PLACEHOLDER_DOCSTRING_PREFIXES = ("Handle ", "Provide ")
```

Remove the equivalent local ESLint heuristics as part of the same decision. Delete these
files in full:

```text
quality/shared/eslint/plugin/rules/no-call-through.js
quality/shared/eslint/plugin/rules/no-trivial-functions.js
```

Apply these exact removals:

```diff
diff --git a/quality/shared/eslint/plugin/index.js b/quality/shared/eslint/plugin/index.js
@@
-import { noCallThrough } from '#shared/eslint/plugin/rules/no-call-through.js';
@@
-import { noTrivialFunctions } from '#shared/eslint/plugin/rules/no-trivial-functions.js';
@@
-  'no-call-through': noCallThrough,
@@
-  'no-trivial-functions': noTrivialFunctions,

diff --git a/quality/config/eslint/limits.js b/quality/config/eslint/limits.js
@@
-export const MAX_TRIVIAL_FUNCTION_STATEMENTS = 2;

diff --git a/quality/config/eslint/rules.js b/quality/config/eslint/rules.js
@@
-  MAX_TRIVIAL_FUNCTION_STATEMENTS,
@@
-  'local/no-call-through': ['error', { allow: [] }],
@@
-  'local/no-trivial-functions': ['error', { maxStatements: MAX_TRIVIAL_FUNCTION_STATEMENTS }],
@@
-const trivialFunctionRule = ['error', { maxStatements: MAX_TRIVIAL_FUNCTION_STATEMENTS }];
@@
-export { sourceRules, nodeSourceRules, eslintSpacingRules, unusedVarsRule, trivialFunctionRule };
+export { sourceRules, nodeSourceRules, eslintSpacingRules, unusedVarsRule };

diff --git a/quality/config/eslint/index.js b/quality/config/eslint/index.js
@@
-  trivialFunctionRule,
@@
-    'local/no-trivial-functions': trivialFunctionRule,
```

In `quality/config/naming/javascript.json`, remove the now-dead string entries
`local/no-call-through`, `local/no-trivial-functions`, `no-call-through`, and
`no-trivial-functions` from their existing `names` arrays. Do not rewrite or reorder the
rest of that currently modified policy file.

Also remove the custom Python code-line counters. Ruff already constrains complexity,
branches, arguments, locals, returns, and statements; raw line count is a poor additional
proxy and is currently implemented by another AST traversal.

Delete these files in full:

```text
quality/python/rules/function_length.py
quality/python/rules/module_length.py
```

Apply:

```diff
diff --git a/quality/python/runner.py b/quality/python/runner.py
@@
-from quality.python.rules import all_at_bottom, function_length, module_length, runtime_singletons
+from quality.python.rules import all_at_bottom, runtime_singletons
@@
-    diagnostics.extend(module_length.collect_module_length_violations(valid_sources))
-    diagnostics.extend(function_length.collect_function_length_violations(valid_sources))

diff --git a/quality/config/python/limits.py b/quality/config/python/limits.py
@@
-MAX_FILE_LINES = 300
-MAX_FUNCTION_LINES = 60
```

Do not remove the following repository-owned checks in this cleanup:

- declarative configuration integrity;
- runtime/development import boundaries and cycle detection;
- private-header, suppression-rationale, and security invariants;
- ComfyUI node-schema/registration agreement;
- generated documentation/workflow consistency;
- shell safety, compatibility, and embedded-runtime checks.

Those checks express repository-specific contracts that the off-the-shelf tools do not.
Removing the naming engine, folder policy, import policy, or shell analyzers requires a
separate rule-by-rule equivalence audit; deleting them wholesale is not justified by file
count alone.

### Step 12: migrate all remaining authored JavaScript to strict TypeScript

There are currently 58 tracked `.js`, `.mjs`, or `.cjs` files. They divide into four exact
groups:

- 54 authored modules that must be renamed and typed as TypeScript;
- `quality/config/imports/madge.cjs`, which can be deleted by using Madge's TypeScript-config
  support instead of a webpack/CommonJS resolver;
- the two local ESLint heuristic files deleted by Step 11;
- `web/dist/main.js`, which remains as the generated browser artifact and is never edited as
  source.

The end state is therefore TypeScript-only authored source, not the dishonest claim that a
browser can execute `.ts` directly. `web/dist/main.js` is compiled output. References to
ComfyUI's external `../../scripts/app.js` and `../../scripts/api.js`, executable files inside
`node_modules`, CodeQL's externally defined `javascript` database language, and upstream
Semgrep rule IDs are protocol/tool identifiers rather than repository-authored JavaScript.
They keep their required spelling.

#### Rename every surviving authored module

Run this exact rename set after the Step 11 deletions:

```bash
git mv quality/config/eslint/base.mjs quality/config/eslint/base.ts
git mv quality/config/eslint/index.js quality/config/eslint/index.ts
git mv quality/config/eslint/limits.js quality/config/eslint/limits.ts
git mv quality/config/eslint/options.js quality/config/eslint/options.ts
git mv quality/config/eslint/rules.js quality/config/eslint/rules.ts
git mv quality/config/eslint/runtime.js quality/config/eslint/runtime.ts
git mv quality/config/html/links.js quality/config/html/links.ts
git mv quality/config/imports/aliases.js quality/config/imports/aliases.ts
git mv quality/config/naming/identifiers.js quality/config/naming/identifiers.ts
git mv quality/config/package-json/dependencies.js quality/config/package-json/dependencies.ts
git mv quality/config/package-json/manifest.js quality/config/package-json/manifest.ts
git mv quality/config/repository/declarations.js quality/config/repository/declarations.ts
git mv quality/config/repository/directories.js quality/config/repository/directories.ts
git mv quality/config/repository/extensions.js quality/config/repository/extensions.ts
git mv quality/config/repository/scopes.js quality/config/repository/scopes.ts
git mv quality/config/security/codeql/frontend/paths.js quality/config/security/codeql/frontend/paths.ts
git mv quality/repository/integrity/config.js quality/repository/integrity/config.ts
git mv quality/repository/integrity/directory-prefixes.js quality/repository/integrity/directory-prefixes.ts
git mv quality/repository/integrity/folder-policy.js quality/repository/integrity/folder-policy.ts
git mv quality/repository/licenses/javascript.js quality/repository/licenses/frontend.ts
git mv quality/repository/naming/analyze.js quality/repository/naming/analyze.ts
git mv quality/repository/naming/check.js quality/repository/naming/check.ts
git mv quality/repository/naming/extractors/files.js quality/repository/naming/extractors/files.ts
git mv quality/repository/naming/extractors/javascript.js quality/repository/naming/extractors/typescript.ts
git mv quality/repository/naming/policy.js quality/repository/naming/policy.ts
git mv quality/repository/naming/scope.js quality/repository/naming/scope.ts
git mv quality/repository/package-json/dependencies.js quality/repository/package-json/dependencies.ts
git mv quality/repository/package-json/json.js quality/repository/package-json/json.ts
git mv quality/security/codeql/frontend/paths.js quality/security/codeql/frontend/paths.ts
git mv quality/security/codeql/frontend/sarif.js quality/security/codeql/frontend/sarif.ts
git mv quality/shared/eslint/plugin/imports.js quality/shared/eslint/plugin/imports.ts
git mv quality/shared/eslint/plugin/index.js quality/shared/eslint/plugin/index.ts
git mv quality/shared/eslint/plugin/path-policy/index-file.js quality/shared/eslint/plugin/path-policy/index-file.ts
git mv quality/shared/eslint/plugin/path-policy/normalization.js quality/shared/eslint/plugin/path-policy/normalization.ts
git mv quality/shared/eslint/plugin/rules/header-comments-before-imports.js quality/shared/eslint/plugin/rules/header-comments-before-imports.ts
git mv quality/shared/eslint/plugin/rules/import-layout.js quality/shared/eslint/plugin/rules/import-layout.ts
git mv quality/shared/eslint/plugin/rules/import-path-style.js quality/shared/eslint/plugin/rules/import-path-style.ts
git mv quality/shared/eslint/plugin/rules/max-barrel-reexports.js quality/shared/eslint/plugin/rules/max-barrel-reexports.ts
git mv quality/shared/eslint/plugin/rules/newline-after-imports.js quality/shared/eslint/plugin/rules/newline-after-imports.ts
git mv quality/shared/eslint/plugin/rules/no-cross-folder-imports.js quality/shared/eslint/plugin/rules/no-cross-folder-imports.ts
git mv quality/shared/eslint/plugin/rules/no-duplicate-barrel-exports.js quality/shared/eslint/plugin/rules/no-duplicate-barrel-exports.ts
git mv quality/shared/eslint/plugin/rules/no-export-only-files.js quality/shared/eslint/plugin/rules/no-export-only-files.ts
git mv quality/shared/eslint/plugin/rules/no-exported-alias-constants.js quality/shared/eslint/plugin/rules/no-exported-alias-constants.ts
git mv quality/shared/eslint/plugin/rules/no-imports-after-statements.js quality/shared/eslint/plugin/rules/no-imports-after-statements.ts
git mv quality/shared/eslint/plugin/rules/no-prefix-collisions.js quality/shared/eslint/plugin/rules/no-prefix-collisions.ts
git mv quality/shared/eslint/plugin/rules/no-reexports-outside-index.js quality/shared/eslint/plugin/rules/no-reexports-outside-index.ts
git mv quality/shared/eslint/plugin/rules/no-single-file-folders.js quality/shared/eslint/plugin/rules/no-single-file-folders.ts
git mv quality/shared/files.js quality/shared/files.ts
git mv quality/shared/json.js quality/shared/json.ts
git mv quality/shared/naming/cases.js quality/shared/naming/cases.ts
git mv quality/shared/naming/identifier-parts.js quality/shared/naming/identifier-parts.ts
git mv quality/shared/naming/validate-name.js quality/shared/naming/validate-name.ts
git mv quality/web/links/check.mjs quality/web/links/check.ts
git mv scripts/frontend.mjs scripts/frontend.ts
```

Also rename the three language/ecosystem policy documents whose current names would preserve
the wrong ownership vocabulary:

```bash
git mv quality/config/duplication/javascript.json quality/config/duplication/typescript.json
git mv quality/config/naming/javascript.json quality/config/naming/typescript.json
git mv quality/config/repository/licenses/javascript.json quality/config/repository/licenses/frontend.json
```

Delete the CommonJS-only Madge configuration:

```bash
git rm quality/config/imports/madge.cjs
```

#### Make TypeScript real rather than changing suffixes only

Add these compiler options to the root `tsconfig.json`:

```json
"noImplicitOverride": true,
"forceConsistentCasingInFileNames": true
```

Keep its existing browser-only `include` and DOM libraries. Add
`quality/tsconfig.json` with exactly:

```json
{
    "extends": "../tsconfig.json",
    "compilerOptions": {
        "baseUrl": "..",
        "lib": ["ES2022"],
        "types": ["node"],
        "paths": {
            "#config/*": ["quality/config/*"],
            "#web/*": ["quality/web/*"],
            "#shared/*": ["quality/shared/*"],
            "#repository/*": ["quality/repository/*"]
        }
    },
    "include": ["./**/*.ts", "../scripts/**/*.ts"]
}
```

Add `jiti` version `2.7.0` as a direct development dependency. ESLint 10 uses Jiti to load a
TypeScript flat-config file; relying on Knip's transitive Jiti installation is not a stable
contract. Regenerate `bun.lock` from the manifest with:

```bash
bun install
```

For all renamed modules:

- change repository-owned imports to extensionless specifiers, matching the Bun/tsx policy in
  the user-owned TypeScript rules; retain explicit suffixes only for JSON imports and external
  contracts that require them;
- add explicit parameter and return types to exported functions;
- type parsed JSON and filesystem input as `unknown`, then narrow it;
- type sets, maps, arrays, rule options, and diagnostic records instead of allowing implicit
  `any`;
- use `import type` for type-only imports;
- use ESLint's published rule/context/node types in local plugin rules;
- keep the existing runtime algorithms and error messages unchanged;
- do not use `allowJs`, `checkJs`, `skipLibCheck`, `@ts-nocheck`, broad `any`, or blanket
  suppression to make the conversion pass;
- do not create `.d.ts` shims for repository modules merely to avoid typing their real
  contracts.

Rename `collectJavaScriptNames` to `collectTypeScriptNames`, rename the internal language
profile value from `javascript` to `typescript`, and update its imports/callers in
`quality/repository/naming/analyze.ts`, `quality/repository/naming/extractors/files.ts`, and
`quality/repository/naming/policy.ts`.

Replace `quality/config/repository/extensions.ts` with the TypeScript-only source policy:

```typescript
export const TYPESCRIPT_EXTENSIONS = ['.ts'];
export const JSX_EXTENSIONS: string[] = [];

export const CODE_EXTENSIONS = [...TYPESCRIPT_EXTENSIONS];
export const EXPORT_FILE_EXTENSIONS = ['.ts'];

export const SHELL_EXTENSIONS = ['.sh', '.bash', '.zsh'];
export const SHELL_SHEBANG_REGEX = /^#!.*\b(?:bash|sh|zsh)\b/u;

export const GENERATED_SOURCE_FILES = ['web/dist/main.js'];
```

Update consumers of `JAVASCRIPT_EXTENSIONS` to import and use
`TYPESCRIPT_EXTENSIONS`. The generated-file entry prevents the authored-source policy from
mistaking the compiled browser bundle for source.

In `quality/config/naming/typescript.json`:

- rename the `languages.javascript` key to `languages.typescript`;
- change governed path regexes from `.js`/`.mjs`/`.cjs` to their renamed `.ts` paths;
- remove entries belonging to the Step 11 deleted ESLint rules;
- change explanatory prose from JavaScript to TypeScript where it describes repository
  source;
- retain external rule IDs and protocol spellings exactly.

In `quality/config/duplication/typescript.json`, change `format` to
`["typescript"]` and change `output` from `.artifacts/cpd/js` to
`.artifacts/cpd/typescript`.

In `rules/NAMING.md`, rename the JavaScript headings to TypeScript, use `ts` code fences,
replace authored `.js`/`.mjs` examples with `.ts`, and update the source-material language
to TypeScript. Do not edit or contextualize the user-owned `rules/TYPESCRIPT.md`.

#### Update tool entry points and configuration references

Apply these path changes without altering third-party executable paths under `node_modules`:

| Owner | Required change |
| --- | --- |
| `.mise/tasks/frontend/build` and `.mise/tasks/frontend/check` | execute `scripts/frontend.ts` |
| `.mise/tasks/links/external` and `.mise/tasks/lint/docs` | execute `quality/web/links/check.ts` |
| `.mise/tasks/deps/verify` | execute the two renamed `quality/repository/package-json/*.ts` files |
| `.mise/tasks/lint/frontend` | point ESLint at `index.ts`, source scope at `scripts/frontend.ts`, naming at `check.ts`, jscpd at `typescript.json`, and Madge at `--ts-config tsconfig.json`; remove `--webpack-config` |
| `.mise/tasks/lint/quality` | point ESLint at `index.ts` and both quality entry points at `.ts` |
| `quality/repository/licenses/check.sh` | execute `quality/repository/licenses/frontend.ts` |
| `quality/security/codeql/frontend/run.sh` and `scan.sh` | execute `paths.ts` and `sarif.ts`; update human-readable comments to TypeScript while retaining CodeQL's required `language=javascript` |
| `quality/config/security/codeql/frontend/scan.yml` | change the display name to `Reactor connector TypeScript` and list `scripts/frontend.ts` |
| `quality/config/imports/aliases.ts` and `quality/config/repository/scopes.ts` | replace `scripts/frontend.mjs` with `scripts/frontend.ts` |
| `quality/config/repository/declarations.ts` | replace `quality/config/eslint/index.js` with `.ts` and remove the deleted Madge config path |
| `quality/config/html/links.ts`, `quality/repository/naming/scope.ts`, and all usage messages | display the renamed `.ts` entry points |

Replace the Madge command with exactly:

```bash
bun --bun node_modules/madge/bin/cli.js --circular --extensions ts --ts-config tsconfig.json --exclude '^(?:dist/|\.\./\.\./scripts/(?:app|api)\.js$)' web
```

The exclusion names the two external ComfyUI host modules, so deleting the webpack alias
configuration does not make Madge traverse or report files the connector does not own.

Replace `quality/package.json`'s source import map with:

```json
"imports": {
    "#config/*.json": "./config/*.json",
    "#config/*": "./config/*.ts",
    "#web/*": "./web/*.ts",
    "#shared/*": "./shared/*.ts",
    "#repository/*": "./repository/*.ts"
}
```

In `quality/config/imports/knip.json`:

- replace `scripts/frontend.mjs` with `scripts/frontend.ts`;
- replace every quality `.js`/`.mjs` entry with its `.ts` destination above;
- remove the deleted `config/imports/madge.cjs` entry;
- replace the quality project glob with `["**/*.ts"]`;
- update `ignoreIssues` paths to `.ts`;
- point the ESLint config at `quality/config/eslint/index.ts`.

In `quality/config/eslint/index.ts`, lint `scripts/**/*.ts` and `quality/**/*.ts`; remove the
CommonJS file group and `ESLINT_COMMONJS_GLOBALS`. In `quality/config/eslint/options.ts`,
remove the corresponding unused CommonJS globals export.

#### Add strict typechecking for the converted tooling

Add `.mise/tasks/type/quality` with exactly:

```bash
#!/usr/bin/env bash
#
# Check quality-tool and build-script TypeScript without running it.
# Runtime: Bash 3.2+, macOS and Linux.
#MISE description="Check quality-tool and build-script TypeScript."
set -euo pipefail

# main - Check quality-tool and build-script TypeScript.
main() {
  REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
  cd "${REPO_ROOT}" || exit 1

  exec bun --bun node_modules/typescript/bin/tsc --project quality/tsconfig.json --noEmit "$@"
}

main "$@"
```

Add `mise run type:quality` after `mise run type:frontend` in `.mise/tasks/type/_default`,
and add it after the frontend type step in `.mise/tasks/check`.

Do not add a JavaScript fallback task. Bun executes the TypeScript entry points directly,
ESLint loads its `.ts` config through the direct Jiti dependency, and Madge reads the root
TypeScript config.

### Step 13: remove obsolete source files only after every import has moved

The final deletion set for runtime ownership cleanup is exactly:

```bash
git rm src/discovery/state.py \
  src/execution/state.py \
  src/settings/state.py \
  src/state.py
```

Do not run these deletions before Steps 1-4 and the import updates in Step 2 are present.

### Step 14: regenerate the tracked frontend artifact

The TypeScript source changes in Steps 9 and 10 require the tracked bundle to be regenerated.
Do not hand-edit `web/dist/main.js`.

```bash
mise run frontend:build
```

Artifact change:

- Source inputs: `config/web/pricing.ts`, `web/discovery/rate.ts`, `web/schema.ts`,
  `web/discovery/schema.ts`, `web/discovery/api.ts`, `web/settings/schema.ts`,
  `web/settings/api.ts`, and `web/live/schema.ts`.
- Output path: `web/dist/main.js`.
- Operation: deterministic project frontend bundle generation through
  `.mise/tasks/frontend/build` and `scripts/frontend.ts`.
- Preserve the current uncommitted Valibot-generated bundle changes; regenerate from the
  final source tree rather than restoring the `HEAD` bundle first.

This is an artifact-generation command required by the source change, not a request to run
the repository's build/check suite while producing this plan.

## Resulting source-shape expectations

After implementation:

- `config/models/identities.py` contains imports, one literal table, and `__all__`; it has no
  dataclass, constructor call, or comprehension.
- `src/models.py` is the only owner of `ModelDefinition`, `MODELS`, and
  `MODELS_BY_CONNECTION`.
- `src/execution` has no import from `src.live` or `src.media.webcam`.
- `VideoOperation.configure()` has one coherent `OperationResources` argument; no adapter
  accepts or deletes a Fast-only scalar parameter.
- Only Fast generation/continuation reads the configured capture maximum during provider
  clip validation.
- Requests are validated once, in `execute_video()`, before admission and transport work.
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
- The custom repository function-policy engine and Python raw-line counters are gone, while
  the equivalent local ESLint heuristics are also gone; security and repository-specific
  integrity checks remain.
- No tracked authored source file ends in `.js`, `.mjs`, or `.cjs`. The sole tracked `.js`
  file is generated `web/dist/main.js`.
- Browser code and quality/build tooling are checked by separate strict TypeScript projects;
  renamed quality files are typed implementations, not JavaScript with a `.ts` suffix.
- `rules/TYPESCRIPT.md` remains exactly as last edited by the user and receives no
  connector-specific additions.
- All 18 node display names remain unchanged and end in ` (reactor)`.

## Explicitly deferred work

The audit correctly identified the absence of first-party tests for cancellation, cleanup,
reservation expiry/damage handling, media bounds, discovery promotion/rollback, and browser
validation. This plan does not invent a test framework, test files, or test commands because
the current request asks for the cleanup implementation plan and the repository planning
rules prohibit adding unrequested test/verification work to a plan. That work should be the
next separately authorized plan, before any broader deletion of custom quality systems.

Likewise, no SDK, HLS, file-lock, Pydantic, ComfyUI dialog, ComfyUI video-input, or frontend
type package replacement is planned. The inspected alternatives do not replace the
connector's important security, cancellation, bounded-I/O, or UI behavior and would not be
a net simplification.
