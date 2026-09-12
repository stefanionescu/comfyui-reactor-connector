# Reactor Cleanup and Public ComfyUI Distribution Plan

## Objective

Clean the complete Reactor connector around native ComfyUI extension contracts and the shared engineering standard used by Live Shopping. Remove duplicated platform responsibilities, correct runtime ownership and schema assumptions, and publish Reactor through the official Comfy Registry tools.

This is one coordinated cleanup, not a compatibility migration or a proposal for another framework. Keep useful Python domain modules, configuration, frontend compilation, workflow builders, and Reactor-specific session/media code. Replace the custom installer, archive implementation, duplicated help system, schema-mutating localization, and redundant metadata with their native or existing owners.

Reactor targets public distribution. Live Shopping currently runs from a linked checkout. Reactor therefore needs official publishing and published-installation acceptance, not a different internal architecture.

Status: the architectural migration passed its earlier local lint, type, build, and packaging checks. Official `comfy node pack` produced an inspected 249-member archive that passed its Gitleaks scan. Those results do not establish a complete cleanup: the file-by-file review in section 15 records 166 findings and policy proposals, with coverage modes for all 598 current files. Contradicted completion criteria have been reopened. This audit changes only the plan; none of its code or public-documentation fixes has been implemented.

Keep one `web/` directory, flat `workflows/`, native V3 registration, the isolated worker entrypoint, and public workflow contracts. The earlier localization/configuration findings remain open in sections 3 and 9. The complete English node catalog remains an unresolved decision. Registry identity and release-version selection are deferred. No publication, host workflow execution, paid generation, published-installation acceptance, license review, or complete pre-publication check suite was performed during this audit.

Browser source, the built `extension.js` and `extension.css`, and native `docs/` share one `web/` directory. Example workflows are flat JSON files in `workflows/` because ComfyUI's Templates menu reads only `<pack>/workflows/*.json`, not subfolders. The generated `workflows/README.md` lists them under one heading per model.

## Contents

- [Shared standard and responsibility boundaries](#shared-standard-and-responsibility-boundaries)
- [Official sources](#official-sources)
- [Repository rules and retained infrastructure](#repository-rules-and-retained-infrastructure)
- [Scope and execution approvals](#scope-and-execution-approvals)
- [1. Keep native loading and ordinary Python ownership](#1-keep-native-loading-and-ordinary-python-ownership)
- [2. Put node contracts and metadata in their actual owners](#2-put-node-contracts-and-metadata-in-their-actual-owners)
- [3. Clean model operations and configuration](#3-clean-model-operations-and-configuration)
    - [Remaining configuration cleanup](#remaining-configuration-cleanup-from-the-audit)
- [4. Keep ComfyUI execution and Reactor session lifetimes distinct](#4-keep-comfyui-execution-and-reactor-session-lifetimes-distinct)
- [5. Consolidate media and worker ownership](#5-consolidate-media-and-worker-ownership)
- [6. Keep secure settings, HTTP, and discovery boundaries](#6-keep-secure-settings-http-and-discovery-boundaries)
- [7. Keep browser source in web and keep esbuild](#7-keep-browser-source-in-web-and-keep-esbuild)
- [8. Use native UI and retain necessary live controls](#8-use-native-ui-and-retain-necessary-live-controls)
- [9. Serve native help and simplify localization](#9-serve-native-help-and-simplify-localization)
    - [Native translation surfaces](#audit-evidence-and-native-translation-surfaces)
    - [Open English catalog decision](#open-decision-complete-english-node-locale-catalog)
    - [Pending localization corrections](#pending-localization-corrections)
- [10. Keep workflow builders and expose native templates](#10-keep-workflow-builders-and-expose-native-templates)
- [11. Delete custom distribution and use official publishing](#11-delete-custom-distribution-and-use-official-publishing)
- [12. Align tooling without another policy framework](#12-align-tooling-without-another-policy-framework)
- [13. Rewrite documentation for the final behavior](#13-rewrite-documentation-for-the-final-behavior)
- [14. Complete direct cleanup with no parallel implementation](#14-complete-direct-cleanup-with-no-parallel-implementation)
- [15. File-by-file readability and code review](#15-file-by-file-readability-and-code-review)
    - [Quality-tool findings](#quality-tool-findings)
    - [Runtime and configuration findings](#runtime-and-configuration-findings)
    - [Frontend findings](#frontend-findings)
    - [Workflow and task findings](#workflow-and-task-findings)
    - [Public writing findings](#public-writing-findings)
    - [Protected-rule findings and decisions](#protected-rule-findings-and-decisions)
    - [Remediation priorities](#remediation-priorities)
    - [File review ledger](#file-review-ledger)
    - [Follow-up acceptance](#follow-up-acceptance)
- [Implementation order](#implementation-order)
- [Acceptance and verification](#acceptance-and-verification)
- [Definition of done](#definition-of-done)

## Shared standard and responsibility boundaries

### Native contracts

Both planned targets follow these ComfyUI contracts. This is not a claim that either current implementation already conforms:

- Root `comfy_entrypoint`, one `ComfyExtension`, explicit node registration, V3 schemas, classmethod execution, and `io.NodeOutput`.
- Native Run, graph queue, cancellation, caching, graph expansion where applicable, media sockets, save nodes, and previews.
- An exported `WEB_DIRECTORY` for served runtime browser assets. The value `"./web"` is the shared project choice, not a mandatory literal in the loader.
- Authored node documentation at `<WEB_DIRECTORY>/docs/<NodeID>.md`, when a detailed page is useful.
- Native locale overrides/translations and node metadata defined directly in schemas.
- Native discovery of example JSONs. Reactor uses the supported `workflows/` folder name (ComfyUI recommends `example_workflows/` and reads both) with directly discoverable files.
- Host-owned Python dependencies installed into the ComfyUI environment, not runtime installation from node code.

### Shared project choices

These choices align the two projects where ComfyUI leaves the implementation open. They are not claimed as mandatory ComfyUI folder or build requirements.

| Area           | Decision for both repositories                                                                                                                                                                                                                                                                                                                                                                     |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Python         | Keep ordinary `src/` domain modules and explicit relative imports. Put runtime data records in domain modules under `src/state/`; they import only the standard library and each other. Keep behavior, and records that hold live connections, tasks, or webcam frames, with their operational owner. Consolidate real duplication, not directories merely because a scaffold has different names. |
| Configuration  | Keep useful `config/` ownership and one definition per setting, model fact, or bound. Do not remove the whole layer.                                                                                                                                                                                                                                                                               |
| Node modules   | Group by cohesive model/domain responsibility. No mandatory one-file-per-class rule and no giant catch-all node module.                                                                                                                                                                                                                                                                            |
| Browser source | Keep authored TypeScript/CSS in `web/` with the existing root `package.json` and root `tsconfig.json`.                                                                                                                                                                                                                                                                                             |
| Browser build  | Keep esbuild and `scripts/frontend.mjs`. Do not introduce Vite, a Bun workspace, a separate source directory, or another browser manifest.                                                                                                                                                                                                                                                         |
| Browser output | Use one `web/extension.js` registration entry. Reactor also emits `web/extension.css` for controls that genuinely need styling.                                                                                                                                                                                                                                                                    |
| Host types     | Use `@comfyorg/comfyui-frontend-types`, with only necessary local payload types or narrow host augmentations.                                                                                                                                                                                                                                                                                      |
| Metadata       | Use existing registrations and schemas. No generated runtime node catalog. English locale catalog completeness remains an explicit decision in section 9.                                                                                                                                                                                                                                          |
| Detailed help  | Optional by content. Native descriptions/tooltips cover simple nodes; detailed guides explain real multi-step behavior and limits.                                                                                                                                                                                                                                                                 |
| Workflows      | Keep one authority per workflow, flat native discovery, no duplicate runtime versions, and actual frontend inspection. Authoring methods and their necessary development tools are repository-specific.                                                                                                                                                                                            |
| Tooling        | Preserve quality/task infrastructure and security coverage. Checker changes require explicit scope and justification in the affected repository; approval in one project does not authorize the same change in the other.                                                                                                                                                                          |
| Dependencies   | Keep runtime requirements and development tools separate. Retain existing package managers and lockfiles.                                                                                                                                                                                                                                                                                          |

### Documented conventions and project choices

- Keep `web/`. The [official native-help documentation](https://docs.comfy.org/custom-nodes/help_page) uses a `web/` directory containing browser assets and `docs/`. The loader contract is `WEB_DIRECTORY`; that directory name is conventional, not mandatory.
- Keep authored TypeScript/CSS in `web/` beside the generated `web/extension.js` and `web/extension.css` and the authored `web/docs/` Markdown. ComfyUI serves only `.js` files from `WEB_DIRECTORY`, and `.comfyignore` excludes `web/**/*.ts` and `web/styles/` from the package.
- Root `__init__.py` and `comfy_entrypoint` implement native package loading. Root `__main__.py` is different: it is Reactor's existing Python directory entrypoint for the fixed isolated media workers. ComfyUI does not require or call it for node registration. Retain it because the parent launches the host interpreter with `-I`, the connector directory, and a fixed worker operation; do not describe it as standard custom-node boilerplate.
- The declaration file is `web/host.d.ts`. It associates externally served `scripts/app.js` and `scripts/api.js` with official `ComfyApp`/`ComfyApi` types and permits CSS imports. It emits no JavaScript and is not a mock, polyfill, or shipped host implementation. The filename is a project choice.
- English literals in V3 schema metadata are valid official fallbacks. A complete English locale catalog is also used by ComfyUI's own frontend. Our partial-English-override policy is not an official prohibition on full catalogs; keep that distinction explicit when resolving section 9.

### What belongs to ComfyUI

Do not reimplement node loading, package upload, node installation, template discovery, Markdown help rendering, graph scheduling, ordinary cache behavior, native save nodes, or the host frontend.

The official CLI already creates an inspectable package with `comfy node pack` and publishes with `comfy node publish`. The project supplies metadata, inclusion/exclusion rules, working code, and built assets. The project still owns its security scans, dependency review, licensing, and release acceptance.

### What legitimately belongs to Reactor

Keep direct SDK integration for behavior that a suitable installed native node does not supply:

- Reactor credentials and server-authoritative limits.
- Provider connection/session lifetime and remote termination.
- Streaming capture, recording retrieval, and media workers.
- Webcam/control leases and invitations targeted to the submitting browser.
- Provider-specific admission limits and protection against uncertain remote termination.
- Reviewed model capabilities, model operations, and public price/guide discovery.

These are provider responsibilities, not a replacement ComfyUI scheduler. Do not force Reactor through Comfy partner authentication, proxy endpoints, or billing to make it resemble core partner nodes.

Live Shopping retains its product/anatomy records, prompts, presets, product preparation, sheet composition, and Blender pose generation. Those domain differences do not justify divergent loaders, frontend toolchains, help systems, or workflow discovery.

### What differs for public distribution

Both projects can develop against a checkout through the same native loader. Reactor additionally maintains Registry metadata, `.comfyignore`, official pack/publish steps, and acceptance of the published installation. Live Shopping omits those publishing steps until public distribution is requested.

### Deliberate authoring and tooling differences

- Reactor keeps its development workflow builders, bounded serializer, builder text, generated index, and source/output comparisons for 33 examples. Live Shopping maintains its seven workflows as native-authored JSON and removes its builder-only machinery. These are explicit authoring choices, not different native discovery contracts or publishing requirements.
- Reactor inspects the core node/widget schemas needed by its builders and corrects those builders from actual frontend evidence. Shopping does not retain builder-only schema/bootstrap code after removing its consumers. Neither project needs a generated runtime node catalog.
- Reactor commits its generated JS/CSS for ready-to-run source and Registry delivery. Shopping builds its ignored JavaScript locally. Both use the same source location, esbuild toolchain, and native served-assets contract.
- Reactor retains its existing checker implementations unless separately authorized otherwise. Shopping's specifically scoped checker/CSS-tool removals do not apply automatically to Reactor. Security controls and protected rules remain authoritative in each project.
- Reactor preserves its public node IDs, parameter meanings/defaults/limits, output socket contracts, and private-state formats through this cleanup. The separately specified removal of custom package identity from recording-report metadata still applies. Shopping's explicitly planned public renames and product-format changes remain Shopping-only.

Do not reverse these decisions merely to make every file or task identical. Share structural conventions and integration contracts while keeping each project's necessary consumers and explicit scope.

No custom cross-repository framework, shared installer, loader package, or synchronization service is introduced to enforce this agreement.

## Official sources

| Source                                                                                                                                                                                                        | Evidence used by this plan                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [ComfyUI loader](https://github.com/Comfy-Org/ComfyUI/blob/master/nodes.py)                                                                                                                                   | Root loading, `WEB_DIRECTORY`, V3 registration, and extension lifecycle.                              |
| [Current custom-node example](https://github.com/Comfy-Org/ComfyUI/blob/master/custom_nodes/example_node.py.example)                                                                                          | Explicit V3 schemas, node classes, and entrypoint.                                                    |
| [V3 guide](https://docs.comfy.org/custom-nodes/v3_migration)                                                                                                                                                  | Schema ownership, execution methods, cache fingerprints, and versioned API semantics.                 |
| [Extension and progress API](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_api/latest/__init__.py)                                                                                                   | `on_load` resource initialization and native progress reporting.                                      |
| [Core video nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_video.py)                                                                                                              | Native video inputs/outputs, save contracts, host folders, and previews.                              |
| [Core provider example](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_api_nodes/nodes_minimax.py)                                                                                                    | Cohesive provider operations and native media outputs, not a requirement to copy Comfy billing.       |
| [JavaScript extensions](https://docs.comfy.org/custom-nodes/js/javascript_overview)                                                                                                                           | Browser assets and extension registration.                                                            |
| [Official frontend template](https://github.com/Comfy-Org/ComfyUI-React-Extension-Template)                                                                                                                   | The official frontend type package and external host imports; its framework/bundler are not required. |
| [Settings](https://docs.comfy.org/custom-nodes/js/javascript_settings) and [dialogs](https://docs.comfy.org/custom-nodes/js/javascript_dialog)                                                                | Native browser preferences and simple dialogs, not a private credential-store API.                    |
| [Native help](https://docs.comfy.org/custom-nodes/help_page) and [localization](https://docs.comfy.org/custom-nodes/i18n)                                                                                     | Direct Markdown help and native translations; a Markdown page is not required for every node.         |
| [Workflow templates](https://docs.comfy.org/custom-nodes/workflow_templates) and [discovery implementation](https://github.com/Comfy-Org/ComfyUI/blob/master/app/custom_node_manager.py)                      | Flat template discovery and actual locale loading.                                                    |
| [Registry metadata](https://docs.comfy.org/registry/specifications)                                                                                                                                           | Publisher, package version, host requirements, and optional asset inclusion.                          |
| [Publishing](https://docs.comfy.org/registry/publishing)                                                                                                                                                      | `.comfyignore`, standard publishing, and Manager distribution.                                        |
| [Official pack/publish commands](https://github.com/Comfy-Org/comfy-cli/blob/main/comfy_cli/command/custom_nodes/command.py)                                                                                  | `pack` creates an inspectable archive; `publish` creates and uploads an archive itself.               |
| [Official packaging implementation](https://github.com/Comfy-Org/comfy-cli/blob/main/comfy_cli/file_utils.py) and [archive filename](https://github.com/Comfy-Org/comfy-cli/blob/main/comfy_cli/constants.py) | Both commands use `zip_files`; the output is `node.zip`.                                              |
| [Registry standards](https://docs.comfy.org/registry/standards)                                                                                                                                               | No runtime package installation, `eval`/`exec`, or interference with other extensions.                |

Use current contracts and implementation when older tutorial examples disagree. The official Python scaffold is explicitly opinionated and still contains V1 examples in the inspected version. It does not require a new Python package hierarchy, wheels, a configuration migration, or a different bundler.

## Repository rules and retained infrastructure

The instructions under `rules/` remain authoritative for this implementation. Official ComfyUI integration contracts do not replace project naming, typing, source organization, documentation, security, or verification rules. The user-requested `src/state/` establishes ownership of runtime dataclasses within the existing architecture; it does not waive those rules.

- Keep `rules/`, `AGENTS.md`, and `CLAUDE.md` unchanged. Keep the existing Python import ordering, `__all__` placement, annotations, docstring requirements, file/function limits, filename-prefix rules, and configured single-module-package exceptions.
- Follow `rules/PYTHON.md`: dataclasses describe data, typed fields have documented contracts, mutable defaults use factories, and only data-contract methods belong on records. Keep operational behavior out of state modules.
- Follow `rules/NAMING.md`: use domain-based snake_case modules, do not create single-file subpackages or catch-all files, and do not fabricate files to meet a folder count. `src/state/` is an explicitly owned data layer, divided by domain.
- Follow `rules/TYPESCRIPT.md`: retain strict compiler options, named exports, type-only imports where appropriate, external-input validation, and the prohibition on project-owned barrel modules.
- Follow `rules/BASH.md`: keep shell entrypoints thin and native to the configured runtime. Do not embed Python implementations or create another setup/release framework.
- Follow `rules/DOCUMENTATION.md`, `rules/WRITING.md`, and `rules/PLANNING.md`: direct wording, concrete source/target operations, current behavior in maintained documentation, dependencies before callers, and generated artifacts after their sources.
- Follow `rules/GENERAL.md` for task scope, private data, approval boundaries, and verification. Do not add automated tests or run unrequested checks. A planning or implementation request does not itself authorize host mutation, publication, or paid execution.
- Keep the entire `quality/` infrastructure, its existing checker implementations, security scanners, dependency controls, and license checks. Retarget paths and accurately describe removed artifacts; do not delete a lint rule to make the refactor pass.
- Keep `mise.toml`, `.mise/`, the existing toolchain, Git hooks, and normal setup/lint/type/security/license/frontend/workflow tasks. These remain the development entrypoints.
- The planned obsolete task removals are exactly `.mise/tasks/comfy/install`, `.mise/tasks/docs/build`, and `.mise/tasks/docs/check`, after replacing their custom-install/generated-help responsibilities. Native Markdown/link checks remain. `.mise/tasks/release/package` may remain as thin delegation to official packing and existing scans, with no custom installer.
- Keeping infrastructure does not mean every path string stays unchanged: quality scopes and task calls must follow `web/`, `src/state/`, native help, and final example artifacts. Removing infrastructure or checker implementations requires a separate explicit decision, not a cleanup shortcut.
- If a concrete implementation conflicts with a protected rule or checker, report that conflict and request a narrowly defined decision. Do not broaden exceptions, add compatibility wrappers, change enforcement semantics, or assume the other repository's plan overrides this repository's rules.

Section 14 is the explicit implementation deletion list; user data, local environments, old release archives, and backups are not included in it.

## Scope and execution approvals

- Implementation proceeded under the section-14 deletion list and per-phase approvals. The user approved deleting `scripts/release.py`, `.mise/tasks/comfy/install`, the generated-help machinery, and `config/models/nodes.py`, and approved `compilerOptions.skipLibCheck` with a pinned Zod 3 development dependency. Live Shopping, protected rules, and installed extensions remain untouched by this repository's changes.
- Obtain the actual Registry publisher ID and canonical repository URL before filling publishing metadata; both remain deferred. Do not invent them or assume `reactor-inc` is available without checking the Registry.
- Select and record the actual supported ComfyUI/frontend pair and a released comfy-cli version that provides `node pack`, `node publish`, and the documented ignore behavior. Upstream source availability does not establish the installed CLI version.
- The existing README states ComfyUI `0.34.6`, frontend `1.49.6`, and Python `3.12`. Verify the final used APIs against the chosen baseline before publishing minimum requirements. Do not add old-host fallback chains.
- Select an exact reviewed version of the official frontend type dependency, published at least seven days earlier. Use the package manager during authorized implementation, not this planning task.
- Keep `AGENTS.md`, `CLAUDE.md`, and `rules/*` unchanged. If a targeted tooling correction conflicts with protected instructions, request that specific amendment instead of broadening exceptions or rewriting the entire rule set.
- Confirm exact paths before deleting existing files/directories, replacing an installed node folder, or removing old archives. No forced replacement, Git cleanup, or unattended deletion is authorized by this document.
- Builds, checks, host changes, publication, and paid generation are execution steps requiring their applicable authorization. Publishing must not happen as a build side effect. Paid operations require explicit agreement on scope and cost.
- Do not add automated tests or hosted Git workflows under the current project rules. Acceptance below uses the authorized existing checks and actual host/manual inspection.

## 1. Keep native loading and ordinary Python ownership

### Loader and package behavior

- [x] Keep root `__init__.py::comfy_entrypoint`, `src/extension.py::ReactorExtension`, explicit node registration, and `src/__init__.py`.
- [x] Change only the public asset root to `WEB_DIRECTORY = "./web"` when the frontend move is ready. Do not serve the new root while an old nested registration bundle still exists.
- [x] Give `comfy_entrypoint` a specific extension return annotation instead of `object`, using a type-only import where needed. Retain the lifecycle-scoped runtime import so standalone tools do not initialize host bindings.
- [x] Keep `src/__init__.py` import-light. Registration, network calls, private-state creation, and background work do not belong in that initializer.
- [x] Keep useful `src/nodes`, `src/comfy`, `src/execution`, `src/media`, `src/live`, `src/settings`, `src/discovery`, and `src/http` ownership. Do not rename them solely to resemble an example repository.
- [x] Keep explicit relative imports inside the extension and current development entrypoints that support the host's package-loading contract. Do not add application `sys.path` mutation, a second import loader, setuptools discovery, an editable-install requirement, or wheel distribution for publishing.
- [x] Preserve the runtime-to-development import prohibition. Node execution must not import `scripts` or `quality`.

### Paths and worker launch

- [x] Consolidate repeated extension-root calculation in `src/language.py`, `src/comfy/routes.py`, `src/execution/report.py`, and media worker launch sites into `src/paths.py::EXTENSION_ROOT`. This new module owns a demonstrated repeated path calculation, not a service registry.
- [x] Keep root `__main__.py` as the fixed isolated-worker dispatcher for `capture`, `video`, `metadata`, and `recording`. It is runtime code and must ship in the official archive.
- [x] Retain the host interpreter, the existing isolated directory-entrypoint launch, and its fixed operation names. Update `src/media/capture.py`, `src/media/video/{input,components}.py`, `src/media/recording/assemble.py`, and `src/media/metadata/read.py` to consume the central root path rather than repeat different parent-depth calculations.
- [x] Keep worker imports host-free, including their existing `config.media` constants. Do not make encoding depend on `server`, `folder_paths`, credentials, or extension initialization.
- [x] Keep worker executable/module choices fixed in code. No workflow input may choose a shell command, executable, module, or import path.

### Node grouping

- [x] Keep the current model-family grouping under `src/nodes`. Related schemas may share helpers within their model owner, as `src/nodes/lingbot/schema.py` already does.
- [x] Remove direct forwarding helpers when callers can use the actual implementation without losing a contract or resource lifetime. Do not merge unrelated operations merely to reduce file count.
- [x] Do not mandate a file rename for all 18 nodes, one module per model, or one class per file. A node-module consolidation needs an actual ownership/duplication reason, not the public-distribution requirement.

### Runtime dataclasses belong in src/state

The inspected runtime currently declares 43 dataclasses. Move their data records into `src/state/`, grouped by domain, and keep their operational behavior in the existing domain modules. Do not merely move provider methods into a data directory or remove decorators to evade the requested ownership.

- [x] Create `src/state/__init__.py` and the domain modules specified below. Keep the initializer import-light, with no aggregate imports that load every state record or worker dependency.
- [x] Keep project-owned runtime data records under `src/state/`, including private coordination records and isolated-worker records. `src/state/` imports only the standard library and its own modules. `SessionResources`, `LiveOptions`, and `RecordingAudio` hold live connections, tasks, webcam frames, or NumPy arrays, so they live in `src/execution/session/resources.py`, `src/live/options.py`, and `src/media/recording/worker.py`.
- [x] Keep development-only dataclasses in `scripts/` and `quality/` with their development owners. They are not runtime state; do not move tooling into the shipped runtime or introduce runtime imports of development packages.
- [x] Preserve each record's field meaning, defaults, mutability, `frozen`, `slots`, `eq`, redacted representations, and public serialization shape unless another named plan item changes that contract.
- [x] Keep field annotations, `Attributes:` documentation, mutable default factories, cheap invariant checks, and pure data serialization with records where they fit the rules. Keep file reads, network calls, clock/version lookup, resource acquisition, provider commands, and lifecycle control outside state.
- [x] Keep state modules independent of runtime initialization, ComfyUI host bindings, node classes, stores, and worker execution. Use existing neutral types or annotation-only `TYPE_CHECKING` references for resource handles where needed; do not load their operational owners at runtime or introduce import cycles. Do not add a generic protocol framework merely to move records.
- [x] Keep worker state modules importable through the existing explicit worker entrypoint without server/node/credential initialization. Workers import the exact state module they use, not a barrel importing unrelated records.

Move declarations as follows. These are exact declaration moves, not wholesale moves of their source modules:

| Existing declarations and source                                                                                                                                                                 | Destination                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `ModelDefinition` in `src/models.py`                                                                                                                                                             | `src/state/models.py`                                                                                                                     |
| `Settings` in `src/settings/schema.py`; `ExecutionConfiguration` in `src/settings/execution.py`                                                                                                  | `src/state/settings.py`                                                                                                                   |
| `Credential` in `src/credentials.py`; `SessionToken` in `src/execution/authentication.py`                                                                                                        | `src/state/credentials.py`                                                                                                                |
| `Price`, `Guide`, `Snapshot` in `src/discovery/contracts.py`; `_ModelState` in `src/discovery/store.py`                                                                                          | `src/state/discovery.py`; rename `_ModelState` to `CatalogState` because it is now a cross-module record                                  |
| `BrowserInput`, `CameraChange`, `LiveOptions` in `src/live/state.py`; `_BrowserExchange` in `src/live/lease.py`                                                                                  | `src/state/live.py`, except `LiveOptions` in `src/live/options.py`; rename `_BrowserExchange` to `BrowserExchange`                        |
| `RecordingWindow`, `ControlValues` in `src/execution/operation.py`; `SessionOutcome`, `SessionResources` in `src/execution/session/state.py`; `_AdmissionTicket` in `src/execution/admission.py` | `src/state/session.py`, except `SessionResources` in `src/execution/session/resources.py`; rename `_AdmissionTicket` to `AdmissionTicket` |
| `RunReport` in `src/execution/report.py`; `FailureReport` in `src/execution/diagnostics.py`                                                                                                      | `src/state/reports.py`                                                                                                                    |
| `VideoFrame`, `CaptureResult` in `src/media/state.py`                                                                                                                                            | `src/state/media.py`                                                                                                                      |
| `RecordingManifest` in `src/media/recording/manifest.py`; `RecordingAudio`, `RecordingVideo`, `RecordingSettings` in `src/media/recording/worker.py`                                             | `src/state/recording.py`, except `RecordingAudio`, which stays in `src/media/recording/worker.py`                                         |
| `EncoderSettings` in `src/media/encoding.py`; `SourceSettings` in `src/media/video/worker.py`                                                                                                    | `src/state/workers.py`                                                                                                                    |
| Data fields of `VideoInputs` in `src/execution/inputs.py`                                                                                                                                        | `src/state/generation/inputs.py`                                                                                                          |
| Data fields of `FastGenerateRequest`, `FastContinueRequest`, and `FastClip` in `src/execution/fast/{generate,continuation,clip}.py`                                                              | `src/state/generation/fast.py`                                                                                                            |
| Data fields of `HeliosRequest` and `ScheduledPrompt` in `src/execution/helios/{request,prompts}.py`                                                                                              | `src/state/generation/helios.py`                                                                                                          |
| Data fields of `LongLiveRequest` and `Shot` in `src/execution/longlive/{request,storyboard}.py`                                                                                                  | `src/state/generation/longlive.py`                                                                                                        |
| Data fields of `LingBotRequest` and `LingBotWorldRequest` in `src/execution/lingbot/request.py`                                                                                                  | `src/state/generation/lingbot.py`                                                                                                         |
| Data fields of `LtxSpeakRequest` in `src/execution/ltx/request.py`                                                                                                                               | `src/state/generation/ltx.py`                                                                                                             |
| Data fields of `SanaRequest` in `src/execution/sana/request.py`                                                                                                                                  | `src/state/generation/sana.py`                                                                                                            |
| Data fields of `ViskoStableRequest` and `ViskoDynamicRequest` in `src/execution/visko/request.py`                                                                                                | `src/state/generation/visko.py`                                                                                                           |
| Data fields of `X2Request` in `src/execution/x2/request.py`                                                                                                                                      | `src/state/generation/x2.py`                                                                                                              |

- [x] Keep `src/state/generation/__init__.py` import-light. The package contains the actual model-family modules above; do not add a package for each single model file.
- [x] Split the existing request dataclasses into state records retaining the listed request names and operational owners in their existing execution modules. Name the operational owners `FastGenerateOperation`, `FastContinueOperation`, `HeliosOperation`, `LongLiveOperation`, `LingBotOperation`, `LingBotWorldOperation`, `LtxSpeakOperation`, `SanaOperation`, `ViskoStableOperation`, `ViskoDynamicOperation`, and `X2Operation`.
- [x] Each operational owner receives its matching state record and retains actual validation, control construction, generation, upload, and release behavior. It implements the existing `VideoOperation` contract. The record must not import that operation to call back into it. Do not add a universal operation factory or forwarding wrappers for renamed imports.
- [x] Keep common capture validation in `src/execution/inputs.py` and operational contracts in `src/execution/operation.py`. Move only their data declarations. Use composition with state rather than mixing provider control flow into data inheritance.
- [x] Update every `src/nodes/{fast,helios,lingbot,longlive,ltx,sana,visko,x2}` execution method to construct the appropriate record and operation; update session/continuation callers to consume the operation. Schema IDs, sockets, defaults, and public operations remain unchanged by this separation.
- [x] Keep Fast clip readiness/event handling in `src/execution/fast/clip.py`; move only the clip result data into state. Keep prompt/shot parsing and scheduling in their existing execution owners and import their record types from state.
- [x] Keep provider-error interpretation in `src/execution/diagnostics.py`, token validation/authentication in `src/execution/authentication.py`, discovery input parsing in `src/discovery/contracts.py`, and recording-path validation in `src/media/recording/manifest.py`. Replace record methods that depend on these operational owners with named constructors/functions in those owners, updating their callers directly.
- [x] Move `RunReport.prepare`'s version/UUID/resource lookup to `src/execution/report.py::prepare_report`, which returns the state record. Keep its pure output serialization on `RunReport`; apply the separate removal of package identity there.
- [x] Keep credential loading/saving in `src/credentials.py`, settings parsing in `src/settings/schema.py`, and settings generation/snapshot creation in `src/settings/execution.py`. State holds their values, not their stores. Preserve credential redaction and all boundary validation.
- [x] Keep `MODEL_IDENTITIES` in `config/models.py` and runtime indexes in `src/models.py`; import `ModelDefinition` from `src/state/models.py` rather than defining it again.
- [ ] Finish removal of old-location state exports. Imports use the declaring state modules, but `src/settings/execution.py::__all__` still lists `ExecutionConfiguration` (R13).
- [x] Delete `src/media/state.py`, `src/live/state.py`, and `src/execution/session/state.py` after all their declarations/callers move. Retain the other source modules for their real behavior; do not delete an execution or validation module merely because its dataclass moved.
- [x] Enforce the data layer with the existing import-linter configuration: `src/state/` may not import other `src` packages, `config`, `scripts`, `quality`, or third-party and host packages. Keep state within runtime scan/type/documentation coverage and in the normal `src/` Registry payload. Do not create another checker framework or generated state catalog.

## 2. Put node contracts and metadata in their actual owners

### V3 schemas and public node behavior

- [x] Keep all 18 existing public `ReactorInc...` node IDs and their operations. Internal cleanup does not require renaming stable operations or adding aliases.
- [x] Move English display names, category, descriptions, search aliases, input labels, placeholders, output labels, and tooltips from `locales/en/nodeDefs.json` into the corresponding `io.Schema` and input/output declarations in `src/nodes/*`.
- [x] Remove every `translate_schema` call/import and delete `src/nodes/schema.py` after the schemas are complete.
- [x] Use `src/nodes/controls.py` for truly shared input/output definitions, returning fresh schema objects. Put model-specific defaults and labels in the relevant node/schema owner.
- [x] Standardize display-name branding to `(Reactor)` and retain the task categories `Reactor/Generate`, `Reactor/Edit`, `Reactor/Live`, `Reactor/Worlds`, and `Reactor/Plans`.
- [x] Use snake_case for Python names and input IDs, PascalCase for classes, and namespaced command/event IDs. Preserve exact required ComfyUI and provider API spellings.
- [x] Keep native `IMAGE`, `VIDEO`, `AUDIO`, scalar, and `STRING` contracts. Do not introduce proprietary media sockets or a new schema framework.
- [x] Keep the Helios prompt and LongLive shot builders local and credential-independent. Their validation and sequencing must not open provider sessions.
- [x] Keep schemas, execution signatures, output order, help, and generated example widget order synchronized. No old socket aliases or positional-layout compatibility reader is added.

### One registration and one derived model association

The current model association is authored twice: `src/extension.py::NODE_REGISTRATIONS` maps classes to models, and `config/models/nodes.py::NODE_MODELS` repeats the mapping with node IDs. Remove the repeated authored table without creating a generated runtime catalog.

- [x] Keep `NODE_REGISTRATIONS` as the explicit class-to-model association in `src/extension.py`. Keep `get_node_list()` returning its classes directly.
- [x] In `ReactorExtension.on_load`, derive an ordinary node-ID-to-model mapping from those registrations and the actual schemas. Pass it into `initialize_runtime`, then the existing `Runtime` constructor and `ModelStore`. Do not save it to disk or create another registration service.
- [x] Update `src/discovery/store.py::ModelStore` to retain that constructor-supplied mapping for catalog presentation. Update `src/discovery/views.py::model_views` to accept it instead of importing `NODE_MODELS`. Keep discovery independent of node and host imports.
- [x] When extracting `RunReport.prepare` into `src/execution/report.py::prepare_report`, remove its repeated membership check against the handwritten table. Its node ID is supplied by the registered node execution path; validate external inputs at their actual boundary instead of adding another runtime catalog dependency.
- [x] Keep `scripts/nodes/schema.py` exporting actual registration/schema facts to the existing development subprocess output, not a packaged JSON file.
- [x] Change `scripts/nodes/metadata.py::validate_metadata` to check registration uniqueness, valid model associations, signatures, and supplied translations directly. Remove its comparison with `NODE_MODELS`.
- [x] Remove `Example.model`'s import of `NODE_MODELS` in `scripts/workflows/example.py`. During workflow construction, obtain the model from `schemas[example.node_id]["model"]` and pass it to the existing note/layout functions that need it.
- [x] Update `scripts/workflows/{build,notes,layout,index}.py` so model-specific decisions consume that derived value. Do not add a separately authored model field to every example as a substitute duplicated table.
- [x] Delete `config/models/nodes.py` after discovery, reporting, documentation, and workflow consumers have moved to the actual registrations/schemas.
- [x] Do not add `resources/nodes.json` or another generated runtime registry. The existing model response and host node definitions supply browser information where needed. A translator-facing English locale catalog is a separate decision in section 9, not a replacement runtime registry.

## 3. Clean model operations and configuration

### Keep the model operation boundaries

- [x] Keep model implementations in `src/execution/{fast,helios,lingbot,longlive,ltx,sana,visko,x2}` and the shared request contracts in `inputs.py` and `operation.py`.
- [x] Keep distinct Fast H3 generation/continuation algorithms, Helios scheduled prompts, LongLive storyboards, LTX speech, SANA/X2 editing, world navigation, and Visko sound behavior. Do not flatten these into a universal request with unrelated flags.
- [x] Consolidate duplicated preparation only when the same operation and invariants are already shared by real callers. Keep provider command names, ordering, upload ownership, and release behavior explicit.
- [x] Keep model-specific input validation before the corresponding upload or paid request. Eliminate repeated checks of already-validated internal values, not checks on HTTP, media, provider responses, or user input.
- [x] Keep upload/track acquisition paired with cleanup in the owner that acquired it.
- [x] Keep HappyOyster unsupported. This cleanup does not introduce new models or providers.

### Keep configuration and remove actual duplication

- [x] Keep `config/models.py::MODEL_IDENTITIES` as the authored provider identity/capability table, `src/state/models.py::ModelDefinition` as its data record, and `src/models.py` as the runtime index builder. These are configuration, state, and derived indexes, not independently authored catalogs. The user approved flattening the `config/models/` package into `config/models.py` (historical move source: `config/models/identities.py`), removing the vacated `config/models/__init__.py`, and both scoped lint declarations: the `CatalogState` naming allowance and the deptry `DEP002` ignore for `comfyui-frontend-package`, whose assets ComfyUI consumes without any connector Python import.
- [x] Remove `scripts/workflows/index.py::GUIDES`; derive the model title from `MODEL_IDENTITIES` or `MODELS` and the model key obtained from actual node schemas.
- [x] Keep `config/generation`, `config/media`, `config/settings.py`, `config/discovery.py`, `config/live.py`, and `config/security.py` where they own shared facts. Remove unused constants and duplicated values individually after tracing consumers.
- [x] Keep provider instructions and reusable prompt defaults separate from UI translations. Keep `locales/en/workflows.json` for the existing workflow-builder text.
- [x] Keep server setting defaults/bounds authored in `config/settings.py`. Derive runtime validation and public field definitions from that owner rather than repeating bounds in the frontend.
- [x] Keep shared parent/worker protocol constants in the existing `config/media` owners. Do not add a new media-protocol framework merely to rename them.
- [x] Move TypeScript-only `config/web/browser.ts` to `web/browser.ts` and `config/web/routes.ts` to `web/routes.ts`. Merge `config/web/pricing.ts::nodePricingRules` and its types into the existing pricing owner as it moves to `web/discovery/pricing.ts`; update its rate-display consumers to import there. Do not create a parallel pricing-config module. Python configuration remains in `config`; browser configuration becomes browser source.
- [x] Remove only `HELP_PREFIX` from `config/routes.py` when custom help routing is removed. Preserve the existing settings/model route prefixes.
- [x] Remove package-manifest constants from `config/package.py` with the release identity code. Keep its actual version-reading limits while `connector_version()` uses them; do not delete live constants to remove a filename.
- [x] Do not replace named policy constants with magic literals or alter security limits to satisfy a cleanup rule.

### Remaining configuration cleanup from the audit

These are pending ownership corrections, not authorization to change limits, model behavior, or wire formats. Root `config/` remains Python configuration; browser-only policy stays in `web/browser.ts` as already planned.

- [ ] Add `MAX_SESSION_RECORD_BYTES = 1024` and `MAX_SESSION_RECORD_DEPTH = 2` to `config/generation/session.py`. Update both size-limit uses and the JSON-depth argument in `src/execution/session/reservation.py::_remaining` to consume them. Preserve the persisted record shape and damaged-record rejection.
- [ ] Reuse the existing `config/media/audio.py::PCM_SAMPLE_BYTES` in the recording worker's WAV size calculation and `setsampwidth` call. Preserve two-byte PCM, the 16-bit conversion, sample rate, channel layout, and output bytes.
- [ ] Name the recording worker's encoding and WAV-write block sizes in `config/media/audio.py`: `AUDIO_ENCODE_BLOCK_SAMPLES = 1024` and `AUDIO_WRITE_BLOCK_SAMPLES = 4096`. Update `AudioEncoder.through` and the WAV-writing loop in `src/media/recording/worker.py` without changing their chunk boundaries or timing.
- [ ] Add `browserLimits.minCalculatorSeconds = 0.1` in `web/browser.ts`. Replace the duplicated minimum strings in `web/discovery/rate.ts` and `web/discovery/dialog.ts` with that value. Keep credit calculations and the existing maximum unchanged.
- Keep compiled regex objects, fixed worker dispatch callables, mathematical unit conversions, serializer logic, and development diagnostics with their operational owners. Runtime validation pattern text already has configuration owners; do not move every literal into a global configuration file.
- Public English media-error prose is not configuration. Its locale move and parent-process translation belong to section 9; keep worker error codes stable.

## 4. Keep ComfyUI execution and Reactor session lifetimes distinct

### Native execution

- [x] Keep `io.ComfyNode`, native Run/queue behavior, native graph links and expansion where actually used, and `io.NodeOutput`. Never start paid work from a widget callback or a parallel browser execution route.
- [x] Keep `src/comfy/execution.py` as the host boundary for settings snapshots, operation validation, admission, interaction preparation, capture, output conversion, and ComfyUI cancellation.
- [x] Keep `wait_for_execution` forwarding the host interruption signal to its owned preparation/session task and awaiting its cleanup.
- [x] Use the public `ComfyAPI().execution.set_progress` API for actual stage/chunk/frame progress. Do not add a separate progress service or invented completion estimates.
- [x] Keep the repeat-run/variation input for a new paid run without changing the provider seed. Do not replace it with unconditional `NaN` cache invalidation.
- [x] Keep fingerprints limited to the adapter contract and execution-affecting settings. Trace `operation_fingerprint` and settings generation so a price-only refresh cannot unnecessarily force another paid execution.
- [x] Never put raw credentials into cache keys or logs. Do not blindly retry generation-start operations without a provider idempotency guarantee.

### Provider resources

- [x] Keep `Runtime` initialized by `ReactorExtension.on_load`, not on first execution or module import. Remove its preload of `nodeDefs` once schema construction no longer consumes it; keep actual message initialization.
- [x] Keep per-run mutable state outside V3 node class instances and class attributes. ComfyUI's class sanitization must not be bypassed.
- [x] Keep `src/execution/admission.py` limited to provider capacity and uncertainty constraints. It must not become another graph scheduler.
- [x] Keep the admission slot, cross-process session reservation, remote connection, browser lease, and media worker as distinct owned lifetimes.
- [x] Retain bounded cleanup and admission blocking after uncertain remote termination. Closing a UI panel is not evidence that remote billing stopped.
- [x] Keep background discovery under the host application lifecycle and cancel/await its owned work at shutdown.
- [x] Consolidate identical cancellation/cleanup implementations only when their ownership semantics match. Do not remove `shield`/await behavior because an ordinary file-processing node does not need it.
- [x] Preserve the original execution failure if redacted diagnostic storage fails. Keep diagnostic writing bounded and private.

## 5. Consolidate media and worker ownership

- [x] Keep native `io.Video.Input`, `io.Video.Output`, `Input.Video`, `InputImpl.VideoFromFile`, native image tensors, and native audio mappings at the node boundary.
- [x] Keep outputs consumable by core `SaveVideo` and audio-saving nodes. Do not add another Reactor save node, preview server, or media format.
- [x] Use `folder_paths.get_temp_directory()` for temporary capture. Native save nodes own final output names, output-folder placement, and supported workflow metadata.
- [x] Keep completed temporary video available to downstream nodes and cache reuse. Remove incomplete files on failure; do not delete a file immediately after returning `VideoFromFile`.
- [x] Keep `src/media/process.py::MediaProcess` as the process/pipe/reaping owner. Encoding, metadata inspection, source-video processing, and recording assembly own their respective worker algorithms, not additional supervisors.
- [x] Preserve the existing isolated worker boundary and host-free imports. Keep the readiness/result protocol bounded and defined through existing shared constants.
- [x] Consolidate duplicate conversions within `src/media/{audio,images,video,recording,metadata}` only where their tensor/channel/timestamp contracts are the same.
- [x] Retain `src/media/output.py::owned_io` where cancellation-safe resource acquisition is necessary. Do not replace it with an unawaited thread operation.
- [x] Preserve frame dimensions, monotonic timestamps, audio shape/sample rate, duration limits, queue bounds, decoded byte limits, output-size limits, and download bounds.
- [x] Keep recording download URL/redirect and destination validation at the download boundary. Do not relax SSRF, path, or symlink protections.
- [x] Keep incremental webcam capture and encoding because core file-based video nodes do not replace a live provider stream.
- [x] Keep recording details as bounded public JSON text separate from media outputs. Remove custom package identity from it, not actual model, duration, SDK-version, or media facts.
- [x] Keep credentials and sensitive provider data out of worker arguments, inherited Reactor environment variables, public diagnostics, and recording details.

## 6. Keep secure settings, HTTP, and discovery boundaries

### Routes and settings

- [x] Keep `src/http/{guard,request,security}.py` as the shared HTTP boundary, with feature handlers under settings, discovery, and live.
- [x] Keep explicit route registration in `src/comfy/routes.py`. Delete only the custom help static route and its imports when native help takes over.
- [x] Preserve actual settings, discovery, and live route namespaces. No legacy redirect/alias route is added for removed help or replaced endpoints.
- [x] Keep body limits, methods, origin/host checks, remote-access restrictions, and multi-user rules. Native extension APIs do not authenticate arbitrary custom routes on the connector's behalf.
- [x] Keep `src/credentials.py`, `src/storage.py`, and `src/settings/*` as the private credential/settings owners. Do not change their persistent location merely to match a code directory.
- [x] Expose credential status/source only, never the saved key. Keep environment credentials authoritative according to the existing contract.
- [x] Keep server-wide duration, cost, size, and concurrency limits server-authoritative. Browser preferences and workflow values must not raise those limits.
- [x] Derive form definitions from `config/settings.py`; remove copied browser bounds/defaults where the existing configuration response supplies them.
- [x] Preserve revision-based updates, atomic private writes, permission checks, and symlink defenses. These protect real concurrent/private state and are not installation recovery machinery.
- [x] Normalize public errors at the actual HTTP/provider boundary. Do not expose raw requests, tracebacks, or private paths.

### Model discovery

- [x] Keep `src/discovery/{sources,contracts,store,checker,navigation,views,routes}.py` for retrieval, validation, persistence, and presentation. Apply the constructor-injected registration mapping from section 2.
- [x] Keep refreshed metadata limited to prices and public descriptive information. It must not create node classes, install code, enable unsupported models, or change reviewed provider limits.
- [x] Keep the distinction between a background change check and an explicit refresh. Neither starts generation or spends model credits.
- [x] Keep one validated snapshot representation and one state-writing implementation. Do not add old-format fallback readers or redundant copies of node capabilities.
- [x] Preserve existing public catalog snapshot restore behavior if it remains part of the feature. It is not the custom installation backup/restore system being deleted.
- [x] Keep source URL restrictions and safe guide navigation. Do not interpret external documentation as instructions to download or execute code.
- [x] Use actual schema/registration data for node membership and `MODEL_IDENTITIES` for provider identity. Do not maintain another browser inventory or generated metadata file.

## 7. Keep browser source in web and keep esbuild

### Source layout

- [x] Keep authored TypeScript and `web/styles/interface.css` in `web/`, beside the built `web/extension.js` and `web/extension.css`. Keep the stylesheet for Reactor's live and settings controls.
- [ ] Remove the `.reactor-node-help` iframe styles and rebuild the served CSS (U01).
- [x] Keep authored `web/docs` in place; it becomes the directly served native help, not a build source copied elsewhere.
- [x] Update `config/web` callers to the new browser-owned configuration paths specified in section 3, then remove the vacated TypeScript-only directory.

### Existing build contract

- [x] Keep esbuild, root `package.json`, root `tsconfig.json`, `bun.lock`, Bun, and `scripts/frontend.mjs`. Do not create Vite configuration, a nested `package.json`, a workspace, or a separate source directory.
- [x] In `scripts/frontend.mjs`, set `entryPoints` to `['web/extension.ts']` and `outfile` to `web/extension.js`. Expect outputs `extension.js` and `extension.css`, and write/compare those exact files.
- [x] Retain browser ESM output, `bundle: true`, external `../../scripts/app.js` and `../../scripts/api.js`, and retained dependency license comments. Do not bundle the host app/API.
- [x] Keep the current in-memory `write: false` build and `--check` comparison mode. Build mode writes only the two generated assets; check mode changes neither assets nor documentation.
- [x] Update the stylesheet URL in `web/extension.ts` to `new URL('./extension.css', import.meta.url)`. Keep CSS insertion single-instance.
- [x] Keep `.mise/tasks/frontend/build` calling `bun scripts/frontend.mjs` and `.mise/tasks/frontend/check` calling it with `--check`. Keep root TypeScript checking in `.mise/tasks/type/frontend`.
- [ ] Keep required generated browser assets committed for Reactor's source/Registry distribution. Add only these intended outputs to source control, not nested development JavaScript or old bundles.
- [x] Remove `web/dist` after its required browser assets are rebuilt into `web` and native Markdown remains in `web/docs`. ComfyUI loads JavaScript beneath the served directory; leaving the old entry creates duplicate registration.
- [x] Never empty the entire `web` directory during a build. It contains authored help.

### Types and aliases

- [x] Add the official frontend type package as an exact reviewed root development dependency. Inspect its actual exports before replacing types.
- [x] Replace handwritten broad host declarations in `web/host.d.ts` and host-node approximations in `web/nodes/contracts.ts` with applicable official types. Keep only real connector payloads and narrow augmentations for missing host members.
- [x] Keep Valibot validation of HTTP and event payloads. TypeScript types do not validate incoming values at runtime.
- [x] Use the root `#web/* -> ./web/*` alias in package imports, TypeScript paths, and browser source imports.
- [x] Keep `#locales` for actual locale resources. Remove browser imports of `#config` after moving TypeScript configuration; retain any root alias only if a real remaining consumer uses it.
- [x] Do not blindly rewrite `quality/package.json` aliases: its `#web` refers to `quality/web`, not the browser application.
- [x] Set root TypeScript include to `web/**/*.ts`; preserve strictness, indexed-access checks, exact optional properties, unknown catches, and module settings. No new framework or type-adapter layer.

## 8. Use native UI and retain necessary live controls

### Native surfaces first

- [x] Register one extension from `web/extension.ts`, using existing feature modules rather than multiple setup paths.
- [x] Keep useful settings/model commands under `Extensions → Reactor`. Remove `HELP_COMMAND`, `helpCommands`, `openNodeHelp`, and the custom selection-toolbox help action.
- [x] Use native Info for node help and native Browse Templates for workflows. Delete the custom help dialog, iframe/page navigation, and HTML guide loading.
- [x] Replace schema-label repair in `web/nodes/labels.ts` with native schema labels and native localization. Remove `refreshWidgetLabels` and connection-change wrapping when their only purpose is repairing metadata the schema should supply.
- [x] Keep only dynamic widget behavior not expressible by the selected native schema/widget APIs. Bind required listeners once, preserve host callbacks, and release owned listeners on removal.
- [x] Rely on native Dialog and toast surfaces for ordinary confirmations and notices. No standalone custom confirmation or notice implementation remains to replace; existing domain forms keep their actionable local validation and status beside the relevant field.
- [x] Keep a password input and the protected server route for credential entry. The documented native text prompt is not a promised password/secret-storage control.
- [x] Keep a custom settings form only for credential management and server-authoritative configuration. Do not store those values as ordinary user/browser preferences.
- [x] Put genuine browser-only preferences in native settings with namespaced IDs. Do not invent preferences merely to populate the settings panel.
- [x] Never mutate server limits or credentials from a settings initialization callback. Native settings hydration is not authorization to change the server.
- [x] Keep the model list as product-specific metadata content, not another node/template browser. Keep the credit-rate display read-only and nonserialized.
- [x] Scope CSS to Reactor-owned elements and use host theme variables. No global style overrides or parallel theme system.

### Live behavior

- [x] Keep `web/live/{controls,scene,webcam,drag,pointer,input,sound,polling,state,commands,api,schema}.ts` for the actual live behaviors. Remove duplicated panel setup/cleanup in the existing owners rather than introducing a generic form or event framework.
- [x] Each active lease/controller owns its requests, polling, subscriptions, abort signal, media tracks, and focus restoration. Closing it releases those resources.
- [x] Keep invitations targeted to the browser that submitted the executing prompt. Never broadcast webcam/control invitations to all clients.
- [x] Keep browser ownership extraction in `src/comfy/interaction.py` as one version-bound host integration. Use a documented context field if the chosen host supplies it; otherwise retain the verified current extraction, not a ladder of compatibility fallbacks.
- [x] Validate event payloads and enforce server-side model capabilities. Do not trust arbitrary events merely because their names or node IDs have the expected prefix.
- [x] Distinguish panel dismissal, node removal, lease expiry, user stop, remote termination, and an unrelated workflow-tab close. They are not equivalent evidence of session completion.
- [x] Keep camera permission, lease expiry, monotonic controls, pointer bounds, and heartbeat/input limits.
- [x] Noninteractive generation must work without a browser. Webcam and interactive modes must explicitly require a browser owner and report a clear error when absent.
- [x] Use the current host's execution/node identifiers for targeting, including subgraphs. Do not assume every node ID is a top-level integer.
- [x] Stop media tracks and remove owned DOM/listeners after success, failure, cancellation, and dismissal. Do not launch another paid run when a panel reconnects.

## 9. Serve native help and simplify localization

### Metadata and locale ownership

- [x] Keep `locales/en/main.json`, `commands.json`, and `workflows.json` for their actual messages. Do not remove workflow text while retaining its builders.
- [x] Remove duplicate default schema text from `locales/en/nodeDefs.json` after moving it to V3 declarations. Keep only genuine native overrides, such as readable combo labels for stable option IDs. If no overrides remain, remove the unused file rather than generate a replacement.
- [x] In `scripts/nodes/translations.py`, change `validate_node_labels`, `validate_labels`, and `read_english` to allow omitted node/field overrides while validating supplied IDs, inputs, output indices, types, and option labels.
- [x] Validate non-English `nodeDefs` entries directly against actual schemas rather than requiring a complete duplicate English override document. Keep existing message-placeholder checks for general messages.
- [x] Update `quality/config/repository/translations.py` and its consuming checks so schema literals are legal and complete locale mirrors are not required. Do not weaken security checks or generate another catalog to satisfy a translation rule.
- [x] Keep `src/language.py` for actual backend errors and workflow text. Remove schema initialization from its responsibility.
- [x] Reduce `web/language.ts` and `web/localization.ts` to the connector's own messages and form/live text. ComfyUI owns native node, command, and settings translation.
- [x] Keep the existing i18n mechanism and shipped language set, with no dependency on a generated help-language manifest. Do not add catalog generation or new languages as part of the pending corrections without a separate decision.

### Audit evidence and native translation surfaces

The [official i18n guide](https://docs.comfy.org/custom-nodes/i18n) and [actual custom-node locale loader](https://github.com/Comfy-Org/ComfyUI/blob/master/app/custom_node_manager.py) recognize `main.json`, `nodeDefs.json`, `commands.json`, and `settings.json`. Arbitrary files such as Reactor's `workflows.json` are not automatically loaded by ComfyUI; that file belongs to the retained workflow builder.

The Comfy-owned frontend's [English node catalog](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.49.6/src/locales/en/nodeDefs.json), [collection script](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.49.6/scripts/collect-i18n-node-defs.ts), and [locale serializer](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.49.6/scripts/nodeDefLocaleSerializer.ts) provide more than backend input labels: they also cover frontend-created widget labels, node-category segments, and data-type labels. Core catalogs contain nullable tooltips. Reactor's stricter validator is not an exact copy of those accepted catalogs.

- Native node names, descriptions, input/output labels, placeholders, and combo display labels belong to `nodeDefs` overrides with schema fallbacks. English literals such as the Helios sequence display name are valid schema metadata, not misplaced runtime configuration.
- Category display translations belong to `main.json` under `nodeCategories`; native menu labels use `menuLabels`. Preserve stable category paths and command IDs.
- Native browser-setting translations use `settings.json` and `main.settingsCategories`. Reactor currently has private server-setting forms, not native browser-preference registrations. Keep those form messages under `main.reactorInc`; do not create unused native setting entries or move credentials into browser preferences.
- Reactor uses native media/scalar types, so it does not need duplicate `dataTypes` translations for host-owned types. Its own menu label is the brand `Reactor`; do not invent translated brand names merely to populate `menuLabels`.
- Localized detailed help uses `web/docs/<NodeID>/<locale>.md`, with `web/docs/<NodeID>.md` as fallback, rather than root locale JSON. Only English fallback guides currently ship.
- Provider command names, node/input IDs, worker error codes, regexes, file formats, and generation prompt defaults are not translatable interface text. Keep development diagnostics and code documentation separate from user-facing localization.

### Open decision: complete English node locale catalog

- [ ] Decide whether `locales/en/nodeDefs.json` should remain a partial override file or contain a complete translator-facing English catalog. The current implementation follows the partial-override choice; this plan update does not authorize reversing it. ComfyUI's own complete English catalog is valid precedent, not a requirement that every extension must copy.
- If a complete catalog is selected, settle its authoring and synchronization method before implementation. Keep native V3 schema fallbacks and do not restore `translate_schema`, make backend schema creation depend on locale files, or introduce a generated runtime registration catalog. Catalog completeness is independent of the browser source layout.

### Pending localization corrections

- [ ] Move all 18 English messages in `config/media/capture.py::ENCODER_ERRORS` to `locales/en/main.json` under `reactorInc.mediaErrors`, keyed by the existing worker error codes. Preserve every sentence and code. Keep `ENCODER_ERRORS` in the same configuration module as a code-to-message-key map, with values such as `mediaErrors.dimensions`, rather than English prose.
- [ ] Update `src/media/process.py::MediaProcess.run` and `_report` to resolve those messages through `src/language.py::translate` when constructing public errors. Unknown or malformed worker codes must still select the existing `encoder_failed` fallback. Worker processes continue to send fixed codes; they must not import locale loading, credentials, or host initialization.
- [ ] Add the Reactor category-segment defaults `Reactor`, `Generate`, `Edit`, `Live`, `Worlds`, and `Plans` under `locales/en/main.json::nodeCategories`. Keep schema category IDs unchanged. Do not use per-node locale `category` fields as a substitute for the native category surface.
- [ ] Align `scripts/nodes/translations.py` with native nullable input/output tooltips: treat `null` tooltip values as absent text while requiring strings for supplied names, descriptions, placeholders, and option labels. Dispatch native node resources to their specialized validator in `read_english` so the generic message validator does not reject valid native nulls. Keep general-message placeholder/type checks unchanged.
- [ ] Allow the native generated seed-control label in node translations only where the actual schema requests `control_after_generate`, using its declared control name or the standard generated name. Keep unknown nodes, unrelated input names, output indices, and combo choices rejected. Do not introduce another handwritten inventory of every frontend widget or duplicate host-owned seed-label rendering.
- [ ] Correct the translation contract documentation in `scripts/nodes/translations.py` and `quality/config/repository/translations.py`: permitting `category` or `search_aliases` keys locally is not proof that the frontend consumes them. Keep search aliases in native schemas; document the inspected host behavior without promising locale-driven alias translation.
- [ ] Extend `scripts/nodes/metadata.py::validate_metadata` to validate the node ID for optional `web/docs/<NodeID>/` localized-guide directories as well as root fallback guide filenames. Validate supplied locale filenames without requiring new translations or a page for every node.
- [ ] Document the language-selection boundary accurately in `ADVANCED.md`: connector HTTP routes use `Accept-Language`; queued node execution does not currently establish that locale scope, and only English resources ship. Do not claim localized execution errors or add a new workflow language parameter as an incidental fix.

### Detailed help by usefulness

- [x] Serve retained authored `web/docs/ReactorInc*.md` files directly under `WEB_DIRECTORY/docs`.
- [x] Keep detailed guides where they explain paid execution, webcam ownership, sequence/storyboard composition, continuation, speech, media limits, recovery, or output behavior. Do not require a page solely because a node exists.
- [x] Preserve useful multi-step content in the Helios Add Prompt and LongLive Add Shot guides; they explain chaining and chunk timing beyond basic tooltips. Small file size alone is not evidence that a guide is filler.
- [x] Remove a redundant guide only after its complete useful short instructions exist in native schema descriptions/tooltips. Validate retained guide IDs and links, not a mandatory 18-page count.
- [x] Keep essential operation and constraints readable offline. Optional external references must use verified real destinations.
- [x] Replace links depending on `HELP_PREFIX`, generated HTML, or old workflow locations with native template references or verified repository links appropriate to the native Markdown renderer. Do not assume a GitHub-relative link resolves from the canvas URL.
- [x] Use the actual canonical repository URL before writing absolute repository links; do not invent one.

### Delete duplicate documentation machinery

- [x] Delete `web/help/{command,dialog}.ts`, `web/help/template.html`, and `web/styles/docs.css` once native help covers their useful content.
- [x] Delete `scripts/docs/build.py`, `scripts/docs/pages.py`, and the obsolete docs package initializer.
- [x] Delete `.mise/tasks/docs/build` and `.mise/tasks/docs/check`; remove their callers from `.mise/tasks/check`, hooks, README, and ADVANCED. Keep Markdown/link checks through the existing documentation lint owners.
- [x] Remove `inventory_issues` imports/calls from `scripts/workflows/build.py`; workflow building must not require generated help or a guide for every node. Retained-guide ID/link checking belongs in the existing docs checks.
- [x] Delete generated `web/dist/docs` and `web/dist/guides`, including copied sample media, workflows, license, CSS, language manifests, and HTML pages. Preserve canonical authored documents/media before removing those copies.
- [x] Remove the `HELP_PREFIX` static route from `src/comfy/routes.py` and its constant/imports. No replacement documentation server or help-copy step.

## 10. Keep workflow builders and expose native templates

### Canonical outputs

- [x] Keep `scripts/workflows/{build,definitions,example,index,layout,live,notes,serialize}.py`, its model-specific example definitions, and the existing workflow build/check tasks as development tools.
- [x] Change `Example.path` in `scripts/workflows/example.py` to return `f"{self.slug}.json"`, not a model subdirectory. Remove its model lookup as specified in section 2.
- [x] Change `scripts/workflows/build.py::main`'s canonical destination to `workflows`. Update its output-directory/language constraints and error wording to that destination.
- [x] Produce all 33 distinct workflow JSONs directly inside `workflows/`. Keep exactly one canonical output per example and no packaging-time flattening or duplicate runtime copies.
- [x] Generate `workflows/README.md` through the existing index owner. Derive model titles and schema data instead of the repeated `GUIDES` table.
- [x] Update index sample paths, guide links, license links, model-specific notes, and README references to the final locations.
- [x] Retain optional developer language exports only outside the canonical runtime template directory. Do not ship a second parallel set or introduce more languages in this cleanup.
- [x] Never run workflow builders, schema inspection, frontend compilation, or asset generation during entrypoint loading or ordinary node execution.

### Correct schema assumptions without building another frontend

- [x] Keep the existing named-input builder representation and `scripts/workflows/serialize.py` as the bounded serializer for these maintained examples, not a generic ComfyUI replacement.
- [x] Keep `scripts/nodes/schema.py` and `read_schemas()` as development inspection of actual node definitions. Extend the inspection to the built-in node definitions these examples actually use: `LoadImage`, `LoadVideo`, `SaveVideo`, and `SaveAudioAdvanced`.
- [x] Keep separate registered-Reactor coverage and native-node schema facts so adding inspected native nodes does not incorrectly require Reactor guides or examples for every core node.
- [x] Replace the hardcoded `SaveVideo` array `[prefix, "auto", "auto"]` in `build_workflow` with values established from the selected native schema and static inspection of the installed frontend 1.49.6 serialization source. Correct `LoadVideo`, `LoadImage`, and audio-save fields the same way where their actual schemas differ.
- [x] Do not assume V3 input objects alone fully specify frontend-only widget serialization. Establish the concrete controls from static inspection of the selected frontend's serialization source, then keep that mapping explicit in the existing serializer. No invented universal schema-to-canvas framework.
- [ ] Inspect a frontend-saved specimen of these native controls in the actual selected ComfyUI frontend and compare the serialized widget values against builder output. This UI acceptance step was excluded from the authorized scope and remains unperformed.
- [x] Keep `control_after_generate` widget ordering, connected-widget bindings, socket types, output indices, and note/group positions consistent with the final frontend artifacts.
- [x] Keep schema comparisons in development checks. Remove redundant validation of values already established by the same builder, not checks that catch mismatched node IDs, sockets, or missing example coverage.
- [ ] Open every generated workflow in the actual selected ComfyUI frontend and inspect native controls, links, outputs, and notes. Fix builder source for any discovered mismatch and regenerate; do not hand-edit generated JSON into a second source of truth.
- [x] Keep sample inputs unbound until loaded/uploaded by the user unless a verified native mechanism supplies them. Extension assets are not automatically files in ComfyUI's input directory.
- [x] Keep all examples credential-free and free of machine-specific private paths. Notes must identify paid execution and browser-only modes.

### Existing assets

Keep the binary assets byte-for-byte. Do not resize, generate, transcode, or change their metadata.

| File                                       | Requirement                                                 |
| ------------------------------------------ | ----------------------------------------------------------- |
| `workflows/assets/fictional-portrait.png`  | Preserve bytes and dimensions.                              |
| `workflows/assets/forest-illustration.png` | Preserve bytes and dimensions.                              |
| `workflows/assets/forest-path.png`         | Preserve bytes and dimensions.                              |
| `workflows/assets/forest-motion.mp4`       | Preserve encoded video, duration, frame rate, and metadata. |
| `workflows/fast-h3-01-text-to-video.jpg`   | Preserve the matching template thumbnail.                   |
| `workflows/helios-02-image-to-video.jpg`   | Preserve the matching template thumbnail.                   |

- [x] Generate every example as `workflows/<slug>.json` with `mise run workflows:build`. Preserve every example operation and note.
- [x] Remove the model subfolders under `workflows/` and the generated HTML copies. Keep the builder source and text resources.
- [x] Keep `workflows/` as the only template directory. Do not add `example_workflows/`, another alias, or a static route.

## 11. Delete custom distribution and use official publishing

### Delete the duplicated implementation

- [x] Delete `scripts/release.py`, including `package_files`, custom ZIP construction, packaging-time workflow copying, hashes, custom manifest generation, `replace_package`, `install`, backup/restore handling, and the installer CLI.
- [x] Do not replace it with another Python release-preparation module, packer, uploader, installer, release state machine, wheel distribution, or manifest format.
- [x] Delete `.mise/tasks/comfy/install` and remove its references. Do not introduce `install.py`, automatic checkout copying, a link manager, or runtime dependency installation.
- [x] Remove `RunReport.package_identity` and its serialized field from the record as it moves to `src/state/reports.py`; remove the `package_identity()` call/function from `src/execution/report.py` and its new `prepare_report` factory. Keep connector version, SDK version, model identity, and actual run facts.
- [x] Remove `PACKAGE_IDENTITY_PATTERN`, `MAX_MANIFEST_BYTES`, and `MAX_MANIFEST_DEPTH` from `config/package.py`, plus obsolete error keys and imports used only by package identity. Keep actual version-reading bounds.
- [x] Stop creating or requiring `.reactor-package.json`. Do not rewrite or delete previously saved recording reports or user state to remove this field from future outputs.
- [x] Remove managed-package restore/backup instructions from user documentation. Existing `.reactor-package-backups` and `dist/*.zip` files remain untouched until their exact deletion is approved.
- [x] Keep the archive secret scan requirement, but call the existing scanner on the official archive rather than keeping a custom packer to produce it.

### Metadata and inclusion

- [ ] Keep `[project].name = "reactor-inc"` and one semantic release version in `pyproject.toml`. Choose the next version after checking actual publication history.
- [ ] Fill the real `[project.urls].Repository`, applicable documentation/issue URLs, `[tool.comfy].PublisherId`, and `DisplayName = "Reactor"`.
- [x] Declare the verified Python minimum in `[project].requires-python` and ComfyUI minimum in `[tool.comfy].requires-comfyui`. Use the documented `comfyui-frontend-package` dependency constraint for the verified frontend requirement after checking the supported host environment. Do not copy a lower core Python minimum or force replacement of host-managed libraries to make a constraint pass.
- [x] Keep valid license metadata and legal text.
- [ ] Review the selected publisher's accepted metadata shape rather than blindly copying an older license example. Deferred with publisher identity.
- [x] Maintain `requirements.txt` from `[project].dependencies` using `scripts/dependencies.py` and `mise run deps:export`. Do not add a second authored dependency list.
- [x] Add `.comfyignore` excluding development-only `web/**/*.ts`, `web/styles/`, `scripts/`, `quality/`, `.mise/`, `.githooks/`, `rules/`, agent instructions, `PLAN.md`, root frontend manifests/lockfiles, `uv.lock`, development tool configuration, old `dist/`, local environments, caches, logs, and private environment/state files.
- [x] Keep root `__init__.py`, runtime `__main__.py`, `src/`, Python `config/`, `pyproject.toml`, `requirements.txt`, license/user guides, `locales/`, public `web/` assets, and `workflows/` in the runtime payload.
- [x] Ignore generated `node.zip` in Git and exclude it from published content. Do not commit release archives or force-include an old archive directory.
- [ ] Build and commit required `web/extension.js`, `web/extension.css`, canonical workflow JSONs, thumbnails, and sample assets before publishing. Use `[tool.comfy].includes` only for a required intentionally git-ignored artifact, not as a blanket include of the checkout.
- [ ] Publish from a reviewed Git checkout with the intended files tracked. Do not rely on the CLI's non-Git fallback traversal as the release inclusion policy.
- [x] Keep credential/private state outside source and served assets. Review tracked symlinks and package members as well as names; an ignore file is not a complete secret or file-content audit.
- [x] Preserve attribution for bundled dependencies. Comfy packaging does not do project-specific license review.

### Official release sequence

Use the following sequence from the repository root when implementation and the relevant checks/publication are authorized:

1. Maintain and review Registry metadata and version in `pyproject.toml`.
2. Export changed runtime requirements and build the maintained example/frontend artifacts.
3. Complete the existing source, dependency, security, license, and artifact checks. Review the release inputs and make the intended source/artifact changes part of the reviewed release checkout; this is not permission for an agent to commit or push without the applicable request.
4. Run `comfy node pack` to create the official `node.zip`.
5. Inspect package members and scan the official archive with existing security tooling.
6. Run `comfy node publish` with the same publishing inputs.
7. Verify the published version through normal Manager/Registry installation and native ComfyUI loading.

The concrete existing build/check and official packaging commands are:

```sh
mise run deps:export
mise run workflows:build
mise run frontend:build
mise run check
comfy node pack
unzip -l node.zip
```

Preserve the archive scanner's existing redaction, rules, archive depth, and nonzero failure behavior. The direct scanner invocation, without creating another release implementation, is:

```sh
gitleaks dir node.zip \
  --config quality/config/security/gitleaks/config.toml \
  --max-archive-depth 3 \
  --no-banner \
  --redact \
  --ignore-gitleaks-allow
```

After successful review and explicit publication authorization:

```sh
comfy node publish
```

- [x] Either run those commands directly or keep `.mise/tasks/release/package` as a thin shell delegation to existing checks, `comfy node pack`, package inspection, and the scanner. It must not implement file selection, archive writing, upload, installation, or release state.
- [x] Remove the old task's invocation of `scripts.release` and its `--host`/`--install` behavior. Keep publishing separate; no build/check task uploads a package.
- [x] Let the CLI prompt securely for publishing authentication. Do not store a Registry token in workflows, project metadata, shell history, or a generated configuration file.
- [x] A scanner failure blocks publication. Do not disable scanning, weaken rules, broaden baselines, or bypass license/dependency controls to obtain a release.

### Repacking is not uploading the inspected ZIP

`comfy node publish` calls the official packer again. It does not accept and upload the earlier inspected `node.zip` in the inspected command implementation.

- [x] Keep source contents, tracked-file selection, built outputs, `.comfyignore`, inclusion settings, metadata, and the CLI version unchanged between package inspection and publishing.
- [x] If any of those inputs change, run official packing, inspection, and applicable scans again before publishing.
- [x] Do not rebuild artifacts, run generators, or change release configuration between inspection and publication.
- [x] Do not claim byte identity between the inspected ZIP and the uploaded ZIP. The reviewed guarantee is the unchanged packaging inputs; archive metadata can differ.
- [x] Do not write a private uploader or patch the official publisher to pretend it uploads the inspected ZIP. If a stronger compliance requirement is imposed, resolve it explicitly with supported tooling instead of claiming an unsupported guarantee.

### Installation and development

- [x] Use a checkout through the native `custom_nodes` loader for ordinary development, just as Live Shopping does. Keep one active loaded copy and install dependencies using the host interpreter.
- [ ] Make Registry/Manager installation the primary public-user path after an actual release exists. Verify with `comfy node install reactor-inc` or the Manager against the intended host and version; do not assume the CLI targets the correct installation without checking.
- [x] Keep one manual source-installation procedure using `custom_nodes/reactor-inc`; built assets are supplied, so public users do not need Bun.
- [x] Do not replace an installed directory, restart an active server, or remove an old version automatically as a build/publish side effect. Inspect and confirm any conflicting installed copy first.
- [x] Public release acceptance is additional to checkout acceptance. Do not make every development edit depend on publishing a package.

## 12. Align tooling without another policy framework

### Preserve enforcement and retarget its inputs

- [x] Keep `quality/shared/eslint/plugin/rules/no-trivial-functions.js`, `no-call-through`, their registrations, limits, and existing checker implementations. This plan does not authorize deleting or disabling them.
- [x] If a required ComfyUI callback produces a concrete conflict with a checker, identify the callback, rule, and violation and ask for a separate targeted decision. Do not preemptively remove rules, add exemptions, or infer permission from Live Shopping's plan.
- [x] Point browser prefix/source scopes at `web` and keep their quality-tooling scope separate. Update concrete paths affected by this plan, not unrelated rule semantics.
- [x] Keep existing Python formatting, import ordering, documentation requirements, file/function limits, filename/package checks, and useful `config` ownership. Enforce the same rules in `src/state/`.
- [x] Keep `rules/`, `AGENTS.md`, and `CLAUDE.md` intact. Any change to protected instructions or checker behavior requires an explicit separate request.

### What changed under quality

The audit compared the working tree with Git HEAD `c725410`: 20 tracked files under `quality/` differed, all within `quality/config/`. No checker implementation files were added, removed, or modified, and there were no untracked quality files. This is an audit snapshot, not a permanent file-count requirement.

- Scopes, aliases, naming paths, and generated-output exclusions cover `web/` source and exclude the built `web/extension.js` and `web/extension.css`.
- Obsolete generated-help aliases and vacated-folder exceptions were removed; existing function/naming exceptions follow the moved declarations.
- The user approved the scoped `CatalogState` naming allowance. The separately approved unused-Python-import declaration for `comfyui-frontend-package` is in `pyproject.toml`, outside `quality/`.
- Security scan inputs and the DOM-sink rule cover `web/`. The existing Bearer suppression's comment has updated paths, with its fingerprint unchanged. Detection patterns and severity/duplication thresholds were not relaxed.
- `AGENTS.md`, `CLAUDE.md`, and `rules/` remain unchanged.

Describe this accurately as preserved checker implementations with updated configuration, not an unchanged `quality/` directory. The pending native-locale validator corrections in section 9 are explicit follow-up scope; they are not permission to weaken unrelated checks.

### Follow the actual source moves

- [x] Update root `package.json` and `tsconfig.json`, `quality/config/imports/{aliases.js,knip.json,madge.cjs}`, and frontend source traversal for `web/**/*.ts`. Remove `config/web/*.ts`.
- [x] Update browser files, Node script files, external app/API import exceptions, source scopes, naming paths, duplication paths, and `.mise/tasks/{lint,type}/frontend` to cover `web` and the retained `scripts/frontend.mjs`.
- [x] Preserve the independent aliases in `quality/package.json`. Do not replace every occurrence of `#web` across unrelated packages.
- [x] Keep `pyrightconfig.json`, Ruff, deptry, import-linter, and Python quality roots for the retained `src`, `config`, `scripts`, and `quality` architecture. Update specific references to deleted modules only.
- [x] Keep runtime imports from `scripts` and `quality` forbidden. Keep discovery/settings independent of host nodes by passing the ordinary registration mapping at initialization.
- [x] Update CodeQL, Semgrep, Bearer, Gitleaks, dependency audits, and artifact scans for moved source and final runtime assets. Security coverage must follow the move immediately; do not exclude `web` source to make scans pass.
- [x] Keep generated-JavaScript source-lint exclusions narrow to `web/extension.js`, while retaining applicable security/license inspection of generated artifacts.
- [x] Retain Stylelint and CSS checks for `web/styles/interface.css`. Shopping may remove its CSS tools when its last authored stylesheet disappears; Reactor still has a real stylesheet.
- [x] Retarget the existing documentation, link, HTML/DOM, and artifact check configuration to the retained native guides and UI. Remove references to deleted generated HTML artifacts, not checker implementations or validation of surviving content.
- [x] Keep quality-tool dependencies, including Markdown/HTML tooling consumed by retained checks. Propose removal of a dependency only after proving that no runtime, script, or quality consumer remains and obtaining approval for that specific removal; do not assume deletion of the HTML renderer makes its libraries unused.
- [x] Remove `.mise/tasks/docs/{build,check}` callers from `.mise/tasks/check` and hooks. Retain workflow/frontend build comparisons, documentation lint, security, and license checks through their actual owners.
- [x] Update `.gitignore`, `.prettierignore`, `.markdownlint-cli2.yaml`, `.typos.toml`, and relevant quality exclusions for `web/extension.js`, `web/extension.css`, `workflows`, and `node.zip`. Do not leave obsolete `web/dist` paths.
- [x] Keep existing mise, Bun, uv, Git hooks, and lockfiles. Do not introduce another package manager, CI pipeline, setup framework, updater, or cross-repo synchronization tool.
- [x] Keep checks separate from dependency installation, host mutation, and publication. No check silently installs packages or spends credits.
- [x] Do not remove local environments, caches, old release artifacts, or user files as part of source cleanup. Disk cleanup requires separate exact-path confirmation.

## 13. Rewrite documentation for the final behavior

- [ ] Finish the README rewrite through D01-D06. The current source-installation procedure exists, but publication bookkeeping and unsupported parity wording remain.
- [ ] Keep available installation instructions separate from development and deferred publication work. Do not document a Registry installation as available before publication.
- [ ] Finish the advanced-guide cleanup through D07-D12. Retain useful settings, recovery, and maintenance instructions; remove implementation-report prose.
- [x] Remove custom ZIP names, package identities, managed-folder recovery, `comfy:install`, generated HTML help, and obsolete workflow/build paths from user procedures.
- [x] Explain which modes require a browser and which execute headlessly. Native node presence does not imply a webcam session can run through a bare API client.
- [x] Explain that model refresh neither installs node code nor grants provider access.
- [x] Explain repeat-run/cache behavior and that a fixed seed does not make execution free. Do not claim that closing the browser confirms remote termination.
- [x] Update the generated workflow index, notes, source examples, retained native guides, command labels, and tooltips together with their actual behavior.
- [x] Keep detailed guide links only where a guide exists. Use schema help or the relevant workflow guidance for simple nodes without a page.
- [x] Preserve legal text, attribution, sample asset provenance, and private-evidence handling.
- [ ] Complete D01-D39 so public documentation serves user tasks rather than describing the rewrite. The explicit file ledger belongs in this requested audit plan, not in product guides.

## 14. Complete direct cleanup with no parallel implementation

### Required removals

After their replacement consumers are ready, confirm and remove these implementation paths:

- `scripts/release.py` and `.mise/tasks/comfy/install`.
- Custom package identity fields/functions, manifest constants, obsolete installer arguments, and installation backup/restore code.
- `src/nodes/schema.py` after direct V3 metadata declarations.
- `config/models/nodes.py` after all consumers use actual registration/schema associations.
- `web/help/{command,dialog}.ts`, `web/help/template.html`, and `web/styles/docs.css`.
- `scripts/docs/{build,pages}.py`, obsolete docs initializer, and `.mise/tasks/docs/{build,check}`.
- The `ui/` source directory and the vacated `config/web` TypeScript directory.
- Broad handwritten host declarations covered by official types; retain only necessary narrow augmentations.
- Generated `web/dist` assets/help and their duplicate copied media/workflows/license.
- The model subfolders under `workflows/`, after the flat outputs and binary assets are in place.
- The old data-only `src/media/state.py`, `src/live/state.py`, and `src/execution/session/state.py` after their records and imports move to `src/state/`. Remove moved declarations from mixed behavior modules, not the behavior modules themselves.
- Unused imports, task calls, application aliases, and error keys whose only consumer was one of the deleted application systems. Retarget obsolete quality/task path references without deleting checker implementations or changing enforcement semantics. Any dependency removal requires proof of no remaining consumer and separate approval.

### Explicitly retained

Keep root `__init__.py` and runtime `__main__.py`, ordinary `src` with runtime data records under `src/state/`, useful Python `config`, `scripts/frontend.mjs`, workflow builders and workflow text, model-specific runtime behavior, all existing quality checker implementations, `mise.toml` and normal `.mise` tasks, protected `rules/` and agent instructions, existing package managers, security controls, useful native guides, and canonical sample assets. The three obsolete custom-install/generated-help tasks are the only task-file deletions specified above.

### Direct cutover requirements

- [x] Update affected imports, task calls, schemas, UI event consumers, docs, and generated artifacts in the same coordinated change.
- [ ] Finish R13, R18, and U01 so no stale state export, unused worker mode, or obsolete help CSS remains. Preserve the completed removal of V1 registration and custom distribution.
- [x] Keep current public node IDs for unchanged operations. This is not a compatibility implementation and does not require node-replacement mappings.
- [x] Preserve stored credentials, settings, catalog snapshots, session reservations, user workflows, and media. This structural cleanup does not require changing their formats or locations.
- [x] Do not delete existing recording reports because future reports omit package identity. No old-report reader is added solely for this cleanup.
- [x] Stop and specify a separately approved direct data operation if a genuine data-format change is discovered. Do not silently discard user state or add a permanent dual-format parser.
- [ ] Remove the remaining stale references identified in section 15 from code, comments, guides, and generated output. Do not claim complete removal until those items are resolved.

## 15. File-by-file readability and code review

### Scope and review status

This review covers the current Git-visible worktree, including untracked source. The initial inventory contains 598 existing files; 173 tracked paths are already deleted and are not current implementation files. Generated browser files, generated workflow JSON, lockfiles, binary assets, and legal text have distinct review responsibilities; they must not be rewritten as ordinary prose.

The source review and coverage record are complete within the ledger's stated modes. Findings below identify inspected declarations and passages. Generated/binary classifications are not claims of line-by-line review, playback, or runtime acceptance. No review can guarantee that every defect has been found. The 165 code, public-documentation, and policy items remain open. D40's plan-status correction is addressed by this update.

Apply `rules/WRITING.md` and ISO 24495-1:2023 to project-authored text: readers must get the information they need, find it, understand it, and use it. Judge names against the concepts understood by the intended developers. ISO 24495 does not prescribe a Python import sorter, a maximum function size, or particular folder names. The engineering findings below must stand on their own technical evidence, not an invented ISO clause. This is a source review, not certification or a claim that runtime behavior has been verified.

Keep exact external API names, workflow IDs and values, protocol keys, license text, security directives, and meaningful explanations of cancellation, resource ownership, units, or failure conditions. Remove repetition and unsupported claims, not necessary contracts. Changes to `rules/`, agent instructions, detection policy, or checker semantics require explicit approval for the specified change; audit scope is not blanket permission to weaken enforcement.

### Quality-tool findings

Each row is an open item. Locations refer to the reviewed worktree and include a declaration or search phrase so the finding remains usable after lines move. Correctness fixes take priority over cosmetic changes.

| ID  | File and location                                                                                                                                                                                         | Concrete finding and required correction                                                                                                                                                                                                                                                                                                                                                 |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q01 | `quality/repository/dependencies.py::read_toml`, lines 69-75                                                                                                                                              | The empty-mapping branch returns exactly the value already in `mapping`. Return the parsed mapping directly; remove the branch without changing validation.                                                                                                                                                                                                                              |
| Q02 | `quality/repository/dependencies.py::_relative`, lines 213-219                                                                                                                                            | `root_path = root` and the empty-parts branch add no behavior to `path.relative_to(root)`. Use that operation at the call site; do not preserve extra statements merely to satisfy a minimum-size rule.                                                                                                                                                                                  |
| Q03 | `quality/shared/eslint/plugin/path-policy/normalization.js::normalizePath`, lines 23-28                                                                                                                   | The alias `pathText = value` and the `includes` branch are unnecessary: replacing absent backslashes already leaves the value unchanged. Use the direct replacement. Resolve any trivial-function rule conflict explicitly rather than adding padding.                                                                                                                                   |
| Q04 | `quality/repository/naming/analyze.js::namingEntriesForFile`, lines 60-69                                                                                                                                 | The earlier return guarantees `language === 'javascript'`, so `if (!language)` is unreachable. Remove it and the repeated language dispatch in `sourceNamingEntries`; call the JavaScript extractor directly. Remove the `displayPath = relativePath` alias in `analyzeNaming`.                                                                                                          |
| Q05 | `quality/shell/scope.py::parse_scope_list`, lines 12-17                                                                                                                                                   | `str.split(',')` always returns at least one item, so `if not parts` is unreachable. Retain trimming and empty-item filtering in one expression.                                                                                                                                                                                                                                         |
| Q06 | `quality/lib/json_config.py::read_json_mapping`, lines 18-32                                                                                                                                              | It reimplements the mapping/key checks already owned by `require_mapping`. JSON object keys are strings, so its second key-type check does not add protection to `json.loads`. Reuse the existing validator; retain duplicate-key rejection and path-aware errors.                                                                                                                       |
| Q07 | `quality/repository/functions/policy.py::require_nonempty_text`, lines 135-140                                                                                                                            | This duplicates `quality/lib/json_config.py::require_string`. Use the existing validator and preserve error context. Do not create a third validation abstraction.                                                                                                                                                                                                                       |
| Q08 | `quality/repository/naming/policy.js::assertArray`, lines 21-27                                                                                                                                           | This duplicates `quality/shared/json.js::requireArray`. Use that existing owner while keeping policy-specific checks in this module.                                                                                                                                                                                                                                                     |
| Q09 | `quality/shared/json.js::requireDictionary`, lines 34-44                                                                                                                                                  | The docstring calls a JSON object a “plain item”; the error says “must be an item.” Use the familiar, exact term “JSON object.” Document the actual accepted shape rather than implying prototype validation that the function does not perform.                                                                                                                                         |
| Q10 | `quality/lib/json_config.py::require_string_list`, lines 87-93                                                                                                                                            | `is_nonempty` checks each string, not whether the array is nonempty. Rename the flag to `are_items_nonempty`, update its direct callers, and document that empty arrays remain allowed. Require a nonempty array separately only where the contract already requires it.                                                                                                                 |
| Q11 | `quality/repository/naming/extractors/python.py::PythonNameExtractor`, lines 12-144                                                                                                                       | The extractor does not collect `ast.TypeAlias.name`, so Python 3.12 `type Json = ...` declarations escape naming checks. Add explicit PEP 695 alias collection as `type_aliases`; preserve existing assignment-style alias handling.                                                                                                                                                     |
| Q12 | `quality/repository/naming/extractors/shell.py`, lines 12-40                                                                                                                                              | The declaration regexes miss names after flags such as `local -a names` and collect only the first name in a multiple declaration. Make collection match the supported Bash declaration forms; do not claim that the current scan covers every shell name.                                                                                                                               |
| Q13 | `quality/repository/package-json/json.js::checkExactVersions` and `fixExactVersions`, lines 30-73                                                                                                         | Checking or removing leading range characters is not exact-version validation. For example, `>1.0.0` becomes a version excluded by the original range, and `1.x` has no recognized prefix. Validate an exact version as a whole. Do not choose a replacement version by stripping text; require an explicitly selected version for unsupported ranges. Preserve exact dependency policy. |
| Q14 | `quality/repository/package-json/json.js::findDependencyLine`, lines 76-82                                                                                                                                | A substring search can identify the wrong section or a one-line manifest's wrong value. Locate the actual dependency member within its section before reporting or editing it. Do not claim a file was fixed without verifying the resulting dependency values.                                                                                                                          |
| Q15 | `quality/config/package-json/manifest.js::PACKAGE_JSON_LINT_MESSAGES`, lines 13-20                                                                                                                        | Error messages are assembled from fragments such as “Range prefix in” and “use.” Replace fragments with complete, actionable diagnostics owned by the dependency check. Preserve machine-readable locations.                                                                                                                                                                             |
| Q16 | `quality/repository/licenses/javascript.js::packageExemptions`, line 32                                                                                                                                   | `exemption.reason.trim()` runs before its type is validated. Validate the string first, then reject whitespace-only reasons, so malformed policy yields a useful error rather than an incidental TypeError.                                                                                                                                                                              |
| Q17 | `quality/security/codeql/frontend/paths.js`, lines 11-45                                                                                                                                                  | The hand-parsed YAML scan can report success when no `paths` section was read. Parse the configuration as YAML and require the intended nonempty path list before checking entries. Keep scan coverage unchanged.                                                                                                                                                                        |
| Q18 | `quality/security/codeql/python/paths.py::codeql_paths`, lines 23-37                                                                                                                                      | The separate line parser has different quoting behavior from the JavaScript reader and also accepts an absent path list. Use the existing Python YAML dependency with a safe loader and validate the same nonempty-list contract.                                                                                                                                                        |
| Q19 | `quality/shared/eslint/plugin/rules/import-layout.js::getImportEndComments` and `quality/shared/eslint/plugin/rules/newline-after-imports.js::getStatementEndComments`                                    | These functions repeat the same trailing-comment range walk. Give this exact operation one owner in the existing plugin import utilities; keep comment attachment and suppression placement intact.                                                                                                                                                                                      |
| Q20 | `quality/shared/eslint/plugin/rules/import-path-style.js::getQuote` and `quality/shared/eslint/plugin/rules/no-cross-folder-imports.js::getQuote`                                                         | The quote-selection function is duplicated. Use one existing plugin utility owner, preserving original quote style and fixer output.                                                                                                                                                                                                                                                     |
| Q21 | `quality/repository/functions/policy.py::function_names` and `quality/python/rules/function_length.py::FunctionCollector`                                                                                 | Both walk qualified function definitions with class/function scope stacks. Reuse the existing collector where its semantics match; avoid constructing a new `Collector` for every nested visit in `function_names`. Keep the resulting qualified names unchanged.                                                                                                                        |
| Q22 | `quality/python/rules/imports/boundary.py::runtime_imported_module_names`, lines 175-178                                                                                                                  | Returning at a bare `TYPE_CHECKING` guard skips its runtime `else` branch. The import-graph visitor handles that branch differently. Visit the runtime branch consistently so boundary checks do not silently miss it.                                                                                                                                                                   |
| Q23 | `quality/python/rules/imports/boundary.py::import_bindings`, lines 135-148                                                                                                                                | A whole-tree walk places imports from unrelated local scopes into one binding map. Local alias reuse can change interpretation of other scopes. Resolve bindings in the scope being checked; do not present this map as complete name resolution.                                                                                                                                        |
| Q24 | `quality/repository/functions/python.py::collect_size_violations`, lines 165-185, and `quality/repository/functions/references.py::ReferenceVisitor`                                                      | Missing static reference evidence is treated as a count of zero and then as evidence that a function is single-use. Instance and externally invoked callbacks are not fully resolved. Distinguish unknown usage from proven single-use; retain required callbacks. Any policy change needs separate approval.                                                                            |
| Q25 | `quality/shared/eslint/plugin/rules/no-trivial-functions.js::reportIfTrivial`, lines 39-50                                                                                                                | The checker rejects short functions without considering reuse, named predicates, or callback contracts; a complex expression still counts as one statement. Review that policy against actual useful short functions before changing it. Do not expand code or replace readable callbacks with obscure binding expressions just to pass. Approval-dependent.                             |
| Q26 | `quality/config/eslint/rules.js::eslintJsdocRules`, lines 68-94                                                                                                                                           | Mandatory descriptions plus parameter/return descriptions can require three statements of the same obvious fact. Review narrowly allowing omission of redundant prose for self-evident private helpers while retaining public contract and non-obvious behavior documentation. Do not disable documentation checks in this audit. Approval-dependent.                                    |
| Q27 | `quality/config/naming/terms.json`, especially `load`, `render`, `resolve`, `data`, `catalog`, and `resolution`                                                                                           | The vocabulary bans legitimate technical concepts along with vague names. That creates exceptions and substitute terminology rather than proving clarity. Review each affected term in domain context; keep exact external spellings. This is a policy decision, not evidence that every matching name is bad.                                                                           |
| Q28 | `quality/config/naming/javascript.json` and `quality/config/naming/policy.json`                                                                                                                           | Large sets of exceptions compensate for the vocabulary restrictions. Preserve required API exceptions. Replace the `CatalogState` reason “The plan names...” with the actual persisted-model-snapshot responsibility; a plan's preference is not a technical justification. Do not broaden exclusions.                                                                                   |
| Q29 | `quality/python/rules/imports/layout.py` and `quality/shared/eslint/plugin/rules/import-layout.js`                                                                                                        | Length-based import ordering mixes dependency categories and creates movement when names change. Record conventional dependency grouping as a readability alternative; do not call the current order an ISO requirement or change the protected convention without approval.                                                                                                             |
| Q30 | `quality/shell/checks/docs.py::has_meaningful_summary` and `quality/shell/checks/architecture.py::has_boundary_header`                                                                                    | A new word or a four-word minimum does not demonstrate a useful explanation. Retain mechanical checks only as mechanical checks; document that they do not assess plain-language quality. Review the enforced boilerplate separately from safety contracts.                                                                                                                              |
| Q31 | `quality/shell/parsers.py::strip_shell_comments`, lines 27-47                                                                                                                                             | The quote scanner processes backslashes before single-quote state and treats every unquoted `#` as a comment. Bash single quotes do not interpret backslashes, and embedded `#` is not always a comment opener. Correct supported lexical handling before using it to claim reliable safety, reference, or complexity results.                                                           |
| Q32 | `quality/shell/parsers.py::shell_identifier_references`, lines 74-84                                                                                                                                      | It counts words in quoted messages as identifier references. `check_unused_functions` can therefore treat a function named only in text as called. Distinguish command references from prose; name and document any remaining approximation.                                                                                                                                             |
| Q33 | `quality/repository/functions/shell.py::collect_shell_function_violations`, lines 21-37                                                                                                                   | Comment stripping is repeated for each line, and physical body lines are reported as “statements.” Compute each cleaned line once. Report the measured unit accurately; changing the policy from lines to parsed statements requires an explicit decision.                                                                                                                               |
| Q34 | `quality/shell/checks/duplicate_functions.py::collect_duplicate_function_bodies`, lines 19-24                                                                                                             | The same line is stripped twice. Clean each line once before filtering/joining; preserve the comparison and thresholds.                                                                                                                                                                                                                                                                  |
| Q35 | `quality/shared/eslint/plugin/path-policy/index-file.js::isIndexFile`, lines 9-24                                                                                                                         | Eight repetitive root/suffix checks obscure the simple basename-and-extension condition. Compare the normalized basename with the existing accepted index filenames; do not expand the accepted suffix set as part of cleanup.                                                                                                                                                           |
| Q36 | `quality/security/codeql/frontend/database.sh`                                                                                                                                                            | The file header says “Configure and run CodeQL database scans,” while the module relies on many caller globals and mutates argument arrays. Specify the exact inputs/outputs in its existing contract once; remove repeated “None” and restated return prose where the protected documentation rule permits it. Do not introduce a generic scan framework.                               |
| Q37 | `quality/config/repository/licenses/environment.sh` and `quality/config/security/{bearer,codeql/frontend,codeql/python,gitleaks,semgrep}/environment.sh`; `quality/config/security/codeql/python/scan.sh` | `-- ticket: quality-config` and `-- ticket: quality-security` are not traceable ticket references. Remove those invented-looking tokens; retain the real adjacent ShellCheck rationale and exact directive scope. Replace generic “Define python/frontend configuration values” descriptions with the actual scanner responsibility.                                                     |
| Q38 | `quality/security/codeql/cleanup.sh::runtime_remove_owned_path`                                                                                                                                           | The function is a development CodeQL cleanup operation, not Reactor runtime code. Rename it to `codeql_remove_database` only with all callers and the exact safety-check owner mapping updated together. Preserve root validation and rejection behavior; a name change must not weaken deletion controls. Approval-dependent.                                                           |
| Q39 | `quality/config/security/semgrep/markers.yml`                                                                                                                                                             | A text match for “compatibility” or “deprecated” cannot establish obsolete behavior; it also matches accurate comments about external APIs. Record this as a wording-policy limitation, distinct from security detection. Do not add obfuscated spellings or silently disable this rule. Approval-dependent.                                                                             |
| Q40 | `quality/config/repository/declarations.js::SHELL_CONFIG_GUARDS`, line 62                                                                                                                                 | The keyword `function` is written as `funct\x69on` without an explanatory need. Prefer the readable literal if the consuming scans permit it; if a scanner creates a false positive, report that conflict rather than hide the word. Preserve the regex match set.                                                                                                                       |

### Runtime and configuration findings

| ID  | File and declaration                                                                                                                                                                                                                                                                                                                                                                                                                                             | Concrete finding and required correction                                                                                                                                                                                                                                                                                                                                                                               |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R01 | `src/execution/cleanup.py::_release`                                                                                                                                                                                                                                                                                                                                                                                                                             | If `interaction.stop()` raises, event detachment and frame-listener removal are skipped. If `interaction.closed()` raises, awaiting the capture worker is skipped. Attempt each independently owned cleanup step even after another fails; preserve cancellation and the original execution failure. Keep disconnect deadlines and uncertain-termination blocking.                                                     |
| R02 | `src/comfy/interaction.py::_prepare_camera` and `_prepare_controls`                                                                                                                                                                                                                                                                                                                                                                                              | Registry insertion and `send_sync` occur before the cleanup-protected `try`. A send failure can leave a registered open lease. Protect all work after lease registration and close the lease on any setup failure, not just a wait failure.                                                                                                                                                                            |
| R03 | `src/live/interaction.py::CameraInteraction.stop`                                                                                                                                                                                                                                                                                                                                                                                                                | A failing `track.off_frame` prevents cancellation of the observer and command workers. Make those cleanup attempts independent. Retain the distinction between stopping controls and confirming remote termination.                                                                                                                                                                                                    |
| R04 | `src/execution/events.py::SessionEvents.close`                                                                                                                                                                                                                                                                                                                                                                                                                   | One failing `transport.off` skips later detachments, then `finally` discards their stored references. Attempt removal of each registered callback and retain the first failure for the caller. Do not replace a failure with a success result.                                                                                                                                                                         |
| R05 | `src/execution/events.py::on_message`                                                                                                                                                                                                                                                                                                                                                                                                                            | The message dictionary is checked/cast repeatedly and its type is read through different expressions. Reject non-dictionaries once, bind `envelope` and `kind` once, then process state, completion, and rejection explicitly. Keep all event kinds and failure behavior.                                                                                                                                              |
| R06 | `src/execution/events.py::SessionEvents`                                                                                                                                                                                                                                                                                                                                                                                                                         | “Ignore events after teardown starts” overstates the implementation: `active` protects `_fail`, not all state updates. Either guard all callbacks consistently or narrow the documentation to the actual guarantee; do not claim the existing code ignores every late event.                                                                                                                                           |
| R07 | `src/execution/authentication.py::mint_session_token`                                                                                                                                                                                                                                                                                                                                                                                                            | `payload` changes from an authorization dictionary to response bytes. Rename the two values to `request_body` and `response_bytes`; keep token validation, deadlines, no-redirect behavior, and the single mint attempt unchanged.                                                                                                                                                                                     |
| R08 | `src/comfy/execution.py`, `src/comfy/interaction.py`, `src/execution/session/capture.py`, `src/execution/cleanup.py`, and `src/execution/session/resources.py::SessionResources.request`                                                                                                                                                                                                                                                                         | These names now refer to a `VideoOperation`, not a request record. Rename the internal parameters/field to `operation` and update their callers directly. Keep `request` for the actual immutable request records. Do not rename workflow inputs or persisted fields.                                                                                                                                                  |
| R09 | `src/execution/helios/request.py`, `src/execution/lingbot/request.py`, `src/execution/longlive/request.py`, `src/execution/ltx/request.py`, `src/execution/sana/request.py`, `src/execution/visko/request.py`, `src/execution/x2/request.py`                                                                                                                                                                                                                     | These modules now contain operation classes; the request records moved to `src/state/generation/`. Rename each module to `operation.py` within its existing family and update imports and exact quality paths. Do not leave old-path re-exports. Confirm these exact file moves before implementation.                                                                                                                 |
| R10 | `src/state/generation/visko.py::ViskoStableRequest` and `ViskoDynamicRequest`; `src/execution/visko/request.py`; `src/nodes/visko/stable.py` and `dynamic.py`                                                                                                                                                                                                                                                                                                    | Dynamic uses the Stable-shaped request while an empty Dynamic subclass adds no fields or behavior. Use one accurately named `ViskoRequest` record and retain the two real operation identities. Preserve field defaults and output contracts; explicitly review the internal type-identity change before removing the empty subtype.                                                                                   |
| R11 | `src/state/generation/visko.py::prompt_passthrough`, `src/live/options.py::LiveOptions.is_passthrough_enabled`, and `src/state/session.py::ControlValues.is_passthrough_enabled`                                                                                                                                                                                                                                                                                 | The comments incorrectly describe immediate prompt changes. The node sends `passthrough` to control prompt preprocessing. Describe “send the prompt unchanged,” not timing or latency.                                                                                                                                                                                                                                 |
| R12 | `src/state/settings.py::Settings.to_json`                                                                                                                                                                                                                                                                                                                                                                                                                        | `dict(asdict(self).items())` copies a dictionary that is already a dictionary. Return `asdict(self)` with the existing return contract.                                                                                                                                                                                                                                                                                |
| R13 | `src/settings/execution.py::__all__`                                                                                                                                                                                                                                                                                                                                                                                                                             | It still exports the moved `ExecutionConfiguration` record from its old operational module. Remove that entry; callers already use `src/state/settings.py`. This is a stale export, not a compatibility API to retain.                                                                                                                                                                                                 |
| R14 | `src/settings/execution.py::ConfigurationGeneration.snapshot`                                                                                                                                                                                                                                                                                                                                                                                                    | Its docstring says it returns a random token, but it returns an `ExecutionConfiguration` and often reuses the token. Describe the snapshot and the exact conditions that replace its cache token.                                                                                                                                                                                                                      |
| R15 | `src/serialization.py::validate_json`                                                                                                                                                                                                                                                                                                                                                                                                                            | The docstring promises size limits, but this function checks types/depth and copies values; only `parse_json` checks encoded byte size. Correct the docstring and make callers responsible for the boundary they actually use. Do not invent a byte limit for in-memory objects.                                                                                                                                       |
| R16 | `src/discovery/sources.py::parse_sources` and `read_public_models`                                                                                                                                                                                                                                                                                                                                                                                               | `parse_sources` validates records, serializes them, then parses them again through `parse_snapshot`; the index regex is also run twice. Keep one parsed index result and separate record construction from whole-snapshot validation without dropping count, identity, timestamp, or unsupported-family checks. `read_public_models` does not replace a cache; correct that docstring.                                 |
| R17 | `src/discovery/store.py::_promote_owned`                                                                                                                                                                                                                                                                                                                                                                                                                         | Its cancellation loop differs from other owned-I/O code: an exception from the write can bypass the pending-cancellation branch. Define and preserve the intended error priority while always waiting for the write and releasing refresh admission. Do not import the media layer into discovery to share this helper.                                                                                                |
| R18 | `src/media/video/worker.py::read_settings`, `prepare`, `source_frames`, `copy_frames`; `src/state/workers.py::SourceSettings.browser_recording`; `config/media/video.py::BROWSER_RECORDING_FRAME_RATE`                                                                                                                                                                                                                                                           | No current caller supplies the eighth `browser` worker argument; webcam input uses JPEG frames. Remove the unused MediaRecorder mode, its field, rate fallback, special codec/timestamp branches, and obsolete comments. Keep the seven-argument local-video path, ordinary supported WebM input, and its existing rejection rules. This changes only the unused internal worker mode, not public workflow parameters. |
| R19 | `src/media/encoding.py`, `src/media/metadata/worker.py`, `src/media/video/worker.py`, and `src/media/recording/worker.py`                                                                                                                                                                                                                                                                                                                                        | `str(json.dumps(...))` repeats a conversion that already returns a string. Remove the outer `str`; keep one JSON message per line, explicit flushes, fixed error codes, and redaction boundaries. Do not add a generic worker framework for this edit.                                                                                                                                                                 |
| R20 | `src/media/encoding.py::read_settings`                                                                                                                                                                                                                                                                                                                                                                                                                           | Positional star-expansion hides which worker argument supplies each limit. Construct `EncoderSettings` with its named fields, as the other worker parsers do. Keep argument order and validation unchanged.                                                                                                                                                                                                            |
| R21 | `src/media/recording/worker.py::AudioEncoder.through`                                                                                                                                                                                                                                                                                                                                                                                                            | The method name hides its action and unit. Rename it to `encode_until` with a parameter such as `end_sample`; update its local callers and section-3 references during implementation. Keep sample boundaries and flushing unchanged.                                                                                                                                                                                  |
| R22 | `src/media/audio.py::read_audio`, `src/media/encoding.py`, `src/media/video/components.py`, and `src/media/recording/worker.py`                                                                                                                                                                                                                                                                                                                                  | Remaining PCM-width and RGB-channel literals repeat existing `PCM_SAMPLE_BYTES` and `RGB_CHANNELS`. Reuse those exact format constants. Explain temporary-buffer memory headroom where a limit is divided by two; do not misrepresent that budget as a measured process-memory cap.                                                                                                                                    |
| R23 | `src/media/video/input.py::_copy_source` and `_copy_file`                                                                                                                                                                                                                                                                                                                                                                                                        | The same 65,536-byte read/write chunk appears three times. Give source-copy chunk size one named owner under `config/media/video.py`, without coupling input preparation to recording-download settings merely because values match.                                                                                                                                                                                   |
| R24 | `src/media/video/components.py::feed`                                                                                                                                                                                                                                                                                                                                                                                                                            | The positive one-second timestamp offset has no explanation. State that the capture protocol uses zero to select fallback timing, so the offset preserves sender-timestamp mode. Keep the offset and relative frame times unchanged.                                                                                                                                                                                   |
| R25 | `src/media/video/worker.py` and `src/media/recording/worker.py::video_timing`                                                                                                                                                                                                                                                                                                                                                                                    | The HDR transfer codes `(16, 18)` are unexplained. Name them as the rejected PQ/HLG transfer-characteristic codes in the existing video configuration, preserving the exact set and behavior.                                                                                                                                                                                                                          |
| R26 | `src/live/interaction.py::CameraInteraction`, `src/live/control/interaction.py`, and their host callers                                                                                                                                                                                                                                                                                                                                                          | The base class is also used for non-LingBot editing controls, but its name/docstring claim a LingBot camera-only role. Rename the shared base to `BrowserInteraction` and describe its preview, client-lifetime, and optional camera responsibilities. Keep `ControlInteraction` and its real domain behavior; do not merge all panels or models.                                                                      |
| R27 | `src/live/registry.py` module docstring                                                                                                                                                                                                                                                                                                                                                                                                                          | It repeats the lease module's “limit queued input” description. This file bounds stored leases and expires closed ones; say that.                                                                                                                                                                                                                                                                                      |
| R28 | `src/media/video/frames.py` module docstring                                                                                                                                                                                                                                                                                                                                                                                                                     | It says the file publishes a clip with a task; it actually decodes prepared frames. Describe decoding and its one-frame memory contract. Keep publication documentation in `publish.py`.                                                                                                                                                                                                                               |
| R29 | `src/settings/conflict.py` module docstring                                                                                                                                                                                                                                                                                                                                                                                                                      | It claims ownership of settings/credential changes, but defines one stale-revision exception. Describe that exception; the store owns mutation.                                                                                                                                                                                                                                                                        |
| R30 | `src/live/commands.py::_axis`                                                                                                                                                                                                                                                                                                                                                                                                                                    | A diagnostic hardcodes “five seconds” while the deadline comes from `COMMAND_TIMEOUT_SECONDS`. Interpolate that constant into the private diagnostic so it remains accurate when policy changes.                                                                                                                                                                                                                       |
| R31 | `src/http/request.py::read_document`                                                                                                                                                                                                                                                                                                                                                                                                                             | Oversized requests use aiohttp's default English error text rather than the connector's locale messages. Supply an actionable localized message containing the byte limit while retaining HTTP 413 and the same read bounds.                                                                                                                                                                                           |
| R32 | `src/nodes/fast/continuation.py`, `src/nodes/fast/generate.py`, `src/nodes/helios/animate.py`, `src/nodes/helios/generate.py`, `src/nodes/helios/sequence.py`, `src/nodes/lingbot/explore.py`, `src/nodes/lingbot/world.py`, `src/nodes/longlive/generate.py`, `src/nodes/longlive/storyboard.py`, `src/nodes/ltx/speak.py`, `src/nodes/sana/edit.py`, `src/nodes/sana/webcam.py`, `src/nodes/visko/stable.py`, `src/nodes/x2/edit.py`, `src/nodes/x2/webcam.py` | Every declared cache-hook docstring incorrectly says model metadata is included. The helper uses an operation revision and private execution-generation token. Correct these 15 docstrings and do not add price/catalog data to the cache key to make the old wording true.                                                                                                                                            |
| R33 | `src/nodes/helios/animate.py` and `generate.py`; `src/nodes/longlive/generate.py`, `shot.py`, and `storyboard.py`                                                                                                                                                                                                                                                                                                                                                | Copy-pasted module descriptions do not identify each file's distinct role; the local shot builder even claims execution. Replace them with one accurate sentence per file: animate an image, generate from text, add a local shot, or execute a storyboard.                                                                                                                                                            |
| R34 | `src/nodes/lingbot/explore.py::execute` and `src/nodes/lingbot/world.py::execute`                                                                                                                                                                                                                                                                                                                                                                                | Long positional request constructors mix prompt, image, three directions, rotation, and lateral movement. Use named fields so the different model-axis mappings are visible. Preserve the fixed public execute signatures.                                                                                                                                                                                             |
| R35 | `src/state/generation/lingbot.py::rotation_speed_deg` and `src/nodes/lingbot/schema.py`                                                                                                                                                                                                                                                                                                                                                                          | The record says degrees per second; the UI says degrees per model step. Resolve this from the current provider contract and use the same unit in record documentation, tooltips, and both LingBot guides. Do not change the value, bounds, or wire key based on a wording guess.                                                                                                                                       |
| R36 | `src/nodes/lingbot/schema.py::_directions`                                                                                                                                                                                                                                                                                                                                                                                                                       | It separately authors movement choices already present in `config/generation/world.py::CAMERA_AXES`. Derive the selected model's choices from that owner, preserving option IDs and order.                                                                                                                                                                                                                             |
| R37 | `src/nodes/fast/continuation.py::define_schema` and `src/nodes/fast/generate.py::define_schema`                                                                                                                                                                                                                                                                                                                                                                  | `controls[1]` relies on an undocumented shared-list position. Let the existing shared controls owner accept the explicit duration input used by these two callers, preserving final input order. Do not build a generic schema transformation layer.                                                                                                                                                                   |
| R38 | `src/nodes/x2/edit.py` and `src/nodes/x2/webcam.py`, Run number tooltip                                                                                                                                                                                                                                                                                                                                                                                          | “This does not change the seed” refers to a control X2 does not expose or send. State only that changing Run number requests another run with the same inputs. Preserve the `variation` key and cache behavior.                                                                                                                                                                                                        |
| R39 | `src/nodes/fast/generate.py`, `src/nodes/helios/generate.py`, `src/nodes/ltx/speak.py`, and `src/nodes/x2/edit.py`, schema descriptions                                                                                                                                                                                                                                                                                                                          | “Help explains...” is navigation filler in descriptions meant to explain the operation. State the operation and its important input/output limitation directly. Keep detailed help discoverable through native Info.                                                                                                                                                                                                   |
| R40 | `src/media/recording/assemble.py`, `src/execution/session/capture.py`, and `src/comfy/execution.py::_temporary_video`                                                                                                                                                                                                                                                                                                                                            | Consecutive cleanup unlinks can stop at the first error and skip another owned output. Attempt cleanup of each owned output without hiding the primary failure. Do not broaden deletion to user files or directories.                                                                                                                                                                                                  |

### Frontend findings

| ID  | File and declaration                                                                                                          | Concrete finding and required correction                                                                                                                                                                                                                                                                                      |
| --- | ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| U01 | `web/styles/interface.css`, lines 217-229                                                                                     | `.reactor-node-help` and its iframe rules belong to the deleted custom help dialog. Remove this unused block and its obsolete Help comment, then rebuild `web/extension.css`. Keep native `web/docs/` and the live/settings styles.                                                                                           |
| U02 | `web/discovery/dialog.ts::ModelDialog` and `openModels`; `web/extension.ts`                                                   | The only current caller passes no node filter. Remove the unused `nodeId` parameter/property, filter branch, Show all button/reset logic, and its sole-use locale key. Keep the working search and model browser. Do not add a new caller to justify dead UI.                                                                 |
| U03 | `web/discovery/schema.ts` transforms                                                                                          | `identity`, `connection`, `schedule`, `result`, and `permissions` objects are immediately spread into another object. Write the output fields directly; preserve snake-to-camel mappings and optional-property omission. Resolve trivial-function policy conflicts without padding.                                           |
| U04 | `web/live/schema.ts::buildInvitation` and transforms                                                                          | The same temporary-object/spread pattern obscures straightforward field mapping. Return explicit fields, retaining shared invitation validation and the distinction between camera and editing invitations.                                                                                                                   |
| U05 | `web/discovery/schema.ts::isRetrievalTime`                                                                                    | It parses a date, constructs a second Date, and checks the same validity again. Use one finite parse check. Do not replace it with a stricter date grammar as an incidental readability edit.                                                                                                                                 |
| U06 | `web/localization.ts::bindings`; `web/discovery/dialog.ts::updateView`; `web/discovery/rate.ts::updateView`                   | Removed DOM targets are weakly referenced, but their binding records and message values remain in the global Set until a locale refresh. Repeated redraws accumulate records. Release bindings for removed owned subtrees on redraw/disposal, preserving live text updates and user-edited controls.                          |
| U07 | `web/live/scene.ts` constructor                                                                                               | Eight camera button labels are translated once into a parallel array, so existing buttons do not follow locale changes and their labels depend on array order. Use key-to-message bindings through `message`, with the existing exact keyboard values.                                                                        |
| U08 | `web/live/controls.ts::stop`                                                                                                  | Direct `textContent` assignment bypasses the message-binding owner for connector status text. Use `setText` and retain message identity for connector-owned reasons; keep server/native error strings plain and escaped.                                                                                                      |
| U09 | `web/live/controls.ts::ControlPanel.prior`                                                                                    | `prior` hides what is saved and differs from the other dialogs. Rename it to `previousFocus`; preserve the connected-element check before focus restoration.                                                                                                                                                                  |
| U10 | `web/settings/dialog.ts`, Reload and Clear key callbacks                                                                      | `.bind` calls with multiple `undefined` arguments make optional-argument plumbing dominate the action. Use named callbacks or an explicit request descriptor with only the fields used. Resolve Q25 rather than adding statements solely to satisfy it.                                                                       |
| U11 | `web/live/state.ts::CameraStates.update`                                                                                      | JSON serialization is used to compare a fixed camera-axis record, and an idle check uses `Object.is.bind(null, 'idle')`. Compare the known axis values directly and use a readable predicate. Preserve queue coalescing and explicit release semantics.                                                                       |
| U12 | `web/live/input.ts::CameraInput.nudge`                                                                                        | The timer rebuilds the held-key union already owned by `publish`. After removing the expired nudge, call `publish`; keep the existing short-press lifetime and release behavior.                                                                                                                                              |
| U13 | `web/live/input.ts::cameraAxes.direction`                                                                                     | `negative`, `positive`, `first`, and `second` hide which key maps to which direction. Use `firstKey`, `secondKey`, `firstDirection`, and `secondDirection`; keep the opposing-key behavior unchanged.                                                                                                                         |
| U14 | `web/live/controls.ts`, `web/live/scene.ts`, `web/live/api.ts`, and `web/live/commands.ts`                                    | Status/action requests use deadline signals without the panel lifetime signal. Make the intended lifecycle explicit: normal requests stop on disposal; any final end request has a separate bounded lifetime. Preserve the scene panel's deliberate wait for remote closure rather than blindly aborting all cleanup traffic. |
| U15 | `web/live/webcam.ts::send` and `frame`                                                                                        | A null canvas blob returns without uploading, but `frame` then reports success. Return an accurate uploaded-frame result or a localized capture failure so Start cannot proceed on a frame that was not sent.                                                                                                                 |
| U16 | `web/live/controls.ts::openControls` and `web/live/scene.ts::openSceneControls`                                               | The lease enters the deduplication Set before construction/show succeeds. Remove it on a construction/show failure and dispose any created resources; otherwise a failed opening suppresses later invitations for that lease.                                                                                                 |
| U17 | `web/settings/dialog.ts::populateLimits`                                                                                      | The first two properties are treated as primary limits by insertion order. Select `max_capture_seconds` and `max_session_seconds` by their stable names, retaining server-owned bounds and field labels.                                                                                                                      |
| U18 | `web/settings/api.ts::requestConfiguration`                                                                                   | Any non-OK response without a valid public message falls back to “save failed,” including a GET. Use action-appropriate read/save/remove fallback messages and keep the existing bounded public-error parser.                                                                                                                 |
| U19 | `web/live/api.ts::exchange` and `web/live/commands.ts::sendAction`                                                            | They discard safe, specific server error messages and show a generic unreachable/rejected message for every HTTP failure. Use the existing bounded `parsePublicError` path with a safe fallback; do not expose raw response bodies or retry provider operations.                                                              |
| U20 | `web/live/controls.ts`, `web/live/scene.ts`, `web/discovery/dialog.ts`, `web/discovery/rate.ts`, and `web/settings/dialog.ts` | Many private-method comments repeat their name and add a “When...” return description to a `Promise<void>`. Keep comments for ordering, cancellation, privacy, and non-obvious UI behavior; remove or condense literal restatements only after resolving the exact documentation-rule conflict in Q26.                        |
| U21 | `web/live/schema.ts::Controls` and `web/live/controls.ts::owner`                                                              | `Controls` is an invitation payload, not a control implementation. Rename the type to `ControlsInvitation` and update `Webcam` and panel imports. Keep `ControlPanel`/`SoundControls` for actual controls and leave wire fields unchanged.                                                                                    |
| U22 | `web/styles/interface.css::.reactor-models`, `.reactor-controls`, `.reactor-live`                                             | Each repeats `box-sizing: border-box` already supplied by the `reactor-dialog` class on the same elements. Remove those duplicate declarations; keep widths and responsive behavior.                                                                                                                                          |

### Workflow and task findings

| ID  | File and declaration                                                                             | Concrete finding and required correction                                                                                                                                                                                                                                                                                                                                      |
| --- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W01 | `scripts/workflows/build.py::main`, read/write loop                                              | `read_text()` and `write_text()` omit UTF-8 despite emitting non-ASCII text with `ensure_ascii=False`. Specify UTF-8 in both paths so output does not depend on the machine's default encoding.                                                                                                                                                                               |
| W02 | `scripts/workflows/build.py::main`                                                               | It collects validation issues, then writes generated files before reporting failure. Complete preflight validation before writing any artifact. Check mode must remain read-only.                                                                                                                                                                                             |
| W03 | `scripts/workflows/index.py::input_summary`                                                      | A large tuple eagerly translates every branch and embeds nested conditional expressions. Select one message key with explicit ordered conditions, then translate it. Preserve current branch priority.                                                                                                                                                                        |
| W04 | `scripts/workflows/index.py::workflow_rows`                                                      | `example.title.split(': ', 1)` derives presentation structure from translated punctuation. Use the complete title, or an explicitly authored short title if separately required; do not assume every language uses that delimiter.                                                                                                                                            |
| W05 | `scripts/workflows/notes.py::sections`                                                           | `notes.pop()` assumes the last note is always the source-video note. Pass that specific instruction to the setup section explicitly; keep other model instructions in their intended section.                                                                                                                                                                                 |
| W06 | `scripts/workflows/build.py` and `scripts/workflows/layout.py`                                   | Repeated node numbers encode roles such as generation, setup note, usage note, and save nodes across files. Name shared role IDs in the existing workflow definition owner, preserving emitted IDs and links. Do not introduce a generic graph builder.                                                                                                                       |
| W07 | `scripts/workflows/serialize.py::validate_connections`                                           | Its name suggests complete link validation, but it checks node socket declarations and never receives the link list. Rename it to `validate_node_sockets`, and describe the remaining link-integrity coverage accurately. Do not claim this check proves every graph link is valid.                                                                                           |
| W08 | `scripts/nodes/schema.py`, lines 21-22                                                           | A standalone comment and the adjacent type-suppression reason repeat the same host typing limitation. Keep the necessary scoped directive and its concise rationale; remove the duplicate prose.                                                                                                                                                                              |
| W09 | `scripts/workflows/models/lingbot.py`, `longlive.py`, `ltx.py`, and `sana.py`, module docstrings | Product names are inconsistently cased as Lingbot, Longlive, Ltx, and Sana. Use LingBot, LongLive, LTX, and SANA in prose; keep exact filenames, IDs, and provider spellings unchanged.                                                                                                                                                                                       |
| W10 | `scripts/nodes/translations.py::compare_messages`                                                | The list branch checks only string types, unlike the scalar branch's placeholder comparison. Its docstring therefore overstates placeholder protection. Validate list-message placeholders against corresponding English entries where lists are supported, or explicitly narrow that contract. Preserve partial-translation behavior.                                        |
| W11 | `.githooks/pre-commit` and `.githooks/pre-push`, header/function comments                        | “Check the staged change” and “Check the pushed revision” overstate the invoked commands: most checks inspect the working tree. Correct the comments to the actual scope; do not imply that the hook verifies a different Git revision.                                                                                                                                       |
| W12 | All 35 existing `.mise/tasks/` files                                                             | The file summary, `#MISE description`, and `main` summary often repeat the same sentence three times. Keep machine-consumed descriptions. Record a narrow policy change allowing one useful human explanation instead of duplicated comments, with explicit approval before changing the shell documentation rule. Preserve every task's command, scope, and safety controls. |
| W13 | `.mise/tasks/release/package`                                                                    | Its description implies a local packaging-only operation, but it first runs `mise run check`, which includes external links and network-backed security/dependency checks. Describe those prerequisites and side effects accurately; do not remove release checks merely to simplify the wording.                                                                             |
| W14 | `src/state/recording.py::RecordingSettings` and `src/media/recording/worker.py`                  | Recording fields inconsistently identify units. Rename internal `duration` to `duration_seconds`, `size_limit` to `max_output_bytes`, and `memory_limit` to `max_memory_bytes`, updating worker callers together. Preserve CLI order, field values, and public keys.                                                                                                          |

### Public writing findings

The criteria column identifies the affected ISO plain-language principle: needed information, finding information, understanding, or use. It is not a claim that ISO mandates a particular implementation or formatter setting.

| ID  | File and passage                                                                                                            | Criteria and correction                                                                                                                                                                                                                                                                                                                                                 |
| --- | --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D01 | `README.md`, Install opening, lines 19-23                                                                                   | Needed information: delete publisher/repository bookkeeping and the future Manager-installation narrative. The numbered source-installation procedure already gives the current action. Keep pending publication inputs in this plan. Do not replace the paragraph with another explanation of the cleanup.                                                             |
| D02 | `README.md`, lines 111-113                                                                                                  | Needed information, use: remove checkout-versus-published-package parity claims. Keep the instruction to open an updated example in a new tab. An inspected archive is not published-installation evidence.                                                                                                                                                             |
| D03 | `README.md`, Nodes table                                                                                                    | Finding information: order entries by model or user task rather than registration order. Move the repeated recording-details explanation below the table; retain the distinction between video-only, audio-capable, and local builder nodes.                                                                                                                            |
| D04 | `README.md`, Find and refresh models; `ADVANCED.md`, Model updates                                                          | Understanding: replace “Installed models” with “Models supported by the installed nodes.” We install connector code, not remote model weights. Keep one short explanation of saved prices; remove the duplicated storage-location paragraph from the README.                                                                                                            |
| D05 | `README.md`, Nodes and model refresh; `ADVANCED.md`, Model updates                                                          | Needed information: keep the unsupported HappyOyster statement once where readers check support. Do not repeat it in each explanation of refreshing. The exclusion behavior remains unchanged.                                                                                                                                                                          |
| D06 | `README.md`, prerequisites                                                                                                  | Understanding: align frontend-version wording with the declared `>=1.49.6,<2.0.0` range instead of implying every later major version is supported. Keep prerequisites concise and do not invent a new supported range.                                                                                                                                                 |
| D07 | `ADVANCED.md`, Development commands, lines 361-368                                                                          | Needed information: remove “explicit reviewed dev dependency, not a shim” and “no host workflows were executed.” These are implementation/acceptance notes, not operating instructions. Retain the source/build command and any prerequisite needed to run it.                                                                                                          |
| D08 | `ADVANCED.md`, Official packaging and publishing, lines 429-469                                                             | Finding information, use: keep one maintainer procedure using the actual package task and the separate publish command. Remove repeated pending-status paragraphs, agent-authorization narration, and duplicated manual pack/scan steps unless they explain a necessary alternative. Keep the fact that publish repacks source and requires unchanged inspected inputs. |
| D09 | `ADVANCED.md`, Update or remove, lines 310-314                                                                              | Needed information: remove “After a Registry release exists” planning prose. Describe the available source-update procedure; add Manager instructions only when the published route is available. Preserve the instruction to stop active sessions before replacing files.                                                                                              |
| D10 | `ADVANCED.md`, Keys and access, line 27                                                                                     | Understanding: “Configured” is presented as an exact UI label, but the UI uses separate saved/environment/missing-key messages. Say that saving a key does not validate it with Reactor.                                                                                                                                                                                |
| D11 | `ADVANCED.md`, Language, lines 330-348                                                                                      | Use: the French build example requires resources not supplied by the repository. Present it as an explicitly parameterized translator procedure with its required locale files, not a ready-to-run example of shipped French support. Correct the blanket claim that all custom labels follow locale changes until U07/U08 are implemented.                             |
| D12 | `ADVANCED.md`, Recording details, lines 249-252                                                                             | Needed information: retain cache reuse and the warning against rerunning solely to refresh a report. Remove old-format migration advice from the current field reference; this does not authorize deleting old reports or adding an old-report reader.                                                                                                                  |
| D13 | `__init__.py`, section comments; `__main__.py`, Imports/selection/entrypoint comments                                       | Understanding: section banners restate obvious code in 20- and 33-line entrypoints. Remove them while keeping concise module/function documentation and the host-import suppression rationale. Both entrypoints remain.                                                                                                                                                 |
| D14 | `web/docs/ReactorIncFastContinue.md`, lines 34-35, 43-48                                                                    | Needed information, use: state the extra billable continuation before Run rather than sending users to an unlinked “bundled ADVANCED.md.” Condense the credit/report footer into useful output facts.                                                                                                                                                                   |
| D15 | `web/docs/ReactorIncFastGenerate.md`, lines 18-21, 36-40, 48-49, 65-70                                                      | Understanding, use: “within ... 8192 pixels” is ambiguous; say “at most 8192 pixels per side.” Remove the unrelated local-help assurance from the image procedure. Put extra billable generation before Run and replace the unlinked boilerplate footer.                                                                                                                |
| D16 | `web/docs/ReactorIncHeliosAddPrompt.md`, Build a sequence and input table                                                   | Use: identify the destination input when connecting the final builder, and say to keep `[]` in the first builder rather than relying only on “unconnected.” Keep the useful chunk explanation and the warning that LongLive uses another format.                                                                                                                        |
| D17 | `web/docs/ReactorIncHeliosAnimate.md`, Cancellation, Live controls, Recording details                                       | Finding information, understanding: the Cancellation heading contains seed/cache/queue policy before cancellation steps. Put cancellation first, keep the live-panel disconnection distinction explicit, and replace four unlinked advanced-guide referrals with the short facts needed here.                                                                           |
| D18 | `web/docs/ReactorIncHeliosGenerate.md`, Cancellation and footer                                                             | Finding information, understanding: apply D17 to this text-generation guide. Its blanket “closing the ComfyUI window does not cancel” must be scoped to noninteractive runs; losing the owning live browser does end a live session.                                                                                                                                    |
| D19 | `web/docs/ReactorIncHeliosSequence.md`, lines 25-26, 57-58, 62-67                                                           | Finding information: keep the alternative live-workflow pointer, but remove repeated “native” and unlinked footer referrals. Name the actual prompt-builder node titles and keep chunk numbers distinct from seconds.                                                                                                                                                   |
| D20 | `web/docs/ReactorIncLingBotExplore.md`, setup, Outputs, Stop and recover                                                    | Use: name the exact example instead of “a LingBot template,” and use its visible upload/save titles. Replace unlinked field/recovery referrals with short applicable instructions. Retain the forward/back priority and coordinate-control explanation. Resolve the rotation-unit conflict through R35.                                                                 |
| D21 | `web/docs/ReactorIncLingBotWorld2Explore.md`, setup, Outputs, Stop and recover                                              | Use: name the exact World 2 example and its visible nodes. Shorten duplicate cache/credit/recovery text, retaining independent lateral movement and live stop behavior. Resolve R35 without changing the rotation parameter.                                                                                                                                            |
| D22 | `web/docs/ReactorIncLongLiveAddShot.md`, Transition row and connection steps                                                | Understanding, use: use visible “Soft transition” and “Hard cut” labels, with `soft`/`cut` only where documenting raw JSON. Name the final generation node's **Shots (JSON)** input. Keep chunk-zero and schedule-length instructions.                                                                                                                                  |
| D23 | `web/docs/ReactorIncLongLiveGenerate.md`, opening and Run and save                                                          | Understanding, use: use the same LongLive product name as the node and provider identity, not an unexplained “LongLive-2.0” variant. Replace “matching template” with `longlive-v2-01-text-to-video`. Scope browser-closing advice to interactive versus noninteractive runs.                                                                                           |
| D24 | `web/docs/ReactorIncLongLiveStoryboard.md`, opening, Run and save, footer                                                   | Finding information, use: name `longlive-v2-02-storyboard`; separate template use from wiring a graph manually. Condense repeated cache/session boilerplate and remove the unlinked report footer. Keep scheduled-shot timing and no-image restrictions.                                                                                                                |
| D25 | `web/docs/ReactorIncLtxSpeak.md`, lines 24-31, 53-58, 67-72                                                                 | Needed information, use: state the possible 20 seconds of extra billable generation before Run. Distinguish the connector's supported speech bounds from a provider's reported range; do not imply the “usual 80-220” range is guaranteed. Condense repeated recording-limit prose and unlinked footer referrals.                                                       |
| D26 | `web/docs/ReactorIncSanaEditVideo.md`, lines 5-10, 17, 29-32, 60-68, 80-92                                                  | Needed information: blank-prompt reconstruction is explained three times. Keep it in the input reference and one relevant instruction. Separate template use from manual wiring and scope browser-closing advice to live/noninteractive mode. Keep source formats, preparation limits, and no-audio behavior.                                                           |
| D27 | `web/docs/ReactorIncSanaWebcam.md`, Run and save and footer                                                                 | Use: state the API-key prerequisite before Run. Replace the unlinked advanced-guide referrals with the local-access, permission, and recovery facts required by this node. Preserve the actual webcam and timeout limits.                                                                                                                                               |
| D28 | `web/docs/ReactorIncViskoStableGenerate.md`, Resolution, Stop and recover, footer                                           | Use: “an exact offered resolution name” gives no way to find the names. Keep blank as the normal path and link the actual provider reference that lists options before recommending a custom name. Scope closing-window behavior to live mode and condense the unlinked footer. Do not invent model choices.                                                            |
| D29 | `web/docs/ReactorIncViskoDynamicGenerate.md`, same passages as D28                                                          | Use: make the same correction for Dynamic while keeping its own node identity, examples, and provider link. Shared behavior does not authorize replacing this native guide with a forwarding implementation.                                                                                                                                                            |
| D30 | `web/docs/ReactorIncX2EditVideo.md`, input table and lines 59-95                                                            | Understanding, use: define SDR on first use, match the `(0-1)` UI labels exactly, and put keyboard pointer instructions beside the drag instructions rather than in an unlinked parenthesis. Consolidate repeated live-start/cancel/save paragraphs.                                                                                                                    |
| D31 | `web/docs/ReactorIncX2Webcam.md`, Run and save and lines 39-51                                                              | Use: state the key and local single-user prerequisites before Run. Keep the keyboard alternative. Replace the unlinked credit/report/recovery footer with concise applicable instructions.                                                                                                                                                                              |
| D32 | `locales/en/main.json`, `errors.audioLimit`, `errors.encoderPipes`, `errors.imageUploadLimit`, `errors.sourceVideoRequired` | Understanding, use: “native limits,” “encoder pipes,” “image bytes,” and “prepared source” describe internals rather than the user's next action. Name the failed media operation and the relevant input or setting. Keep developer-only facts out of public text.                                                                                                      |
| D33 | `locales/en/main.json`, `errors.keyEmpty`, `errors.speechPace`, `errors.shotChunk`, `errors.resolutionName`                 | Use: messages omit conditions that actually cause failure, including maximum length/range. Supply the relevant bound through named placeholders and the existing configuration owner. Do not tell users to truncate a real key or alter stable API fields.                                                                                                              |
| D34 | `locales/en/main.json`, `errors.captureQueueFull` and `errors.videoArrivalRate`                                             | Use: shortening a recording is not a reliable remedy for an encoder that cannot keep up with incoming frames. Describe the throughput problem and direct readers to available CPU/disk capacity and applicable media limits instead of asserting that duration is the cause.                                                                                            |
| D35 | `locales/en/workflows.json`, `limits.fast` and `limits.ltx`                                                                 | Needed information: example notes omit extra billable recording generation. Add a short notice before execution in all six Fast examples and the LTX example, through the existing builder. Keep graph IDs, links, prompts, and widget values unchanged.                                                                                                                |
| D36 | `locales/en/workflows.json`, `nodes`, `setup`, `notes`; `scripts/workflows/notes.py`                                        | Understanding: setup strings repeat authored node titles literally, so independent translation/renaming can break instructions. Interpolate the title from its existing message key instead of maintaining another copy. Keep titles short and task-specific.                                                                                                           |
| D37 | `locales/en/workflows.json::index.update`; `workflows/README.md`, lines 11-13                                               | Finding information: update advice precedes the workflow list on a first-use index. Move it below the list/save instructions. Regenerate the index from its owner rather than editing generated Markdown.                                                                                                                                                               |
| D38 | `locales/en/workflows.json::index.limits` and `limitsTitle`; generated workflow index                                       | Finding information: the Limits section mixes capabilities, empty media inputs, and language behavior. Put required media selection with opening steps and put saved-language behavior with update guidance. Keep actual limits under the limits heading.                                                                                                               |
| D39 | `locales/en/main.json`, `live.recordingNotice`, `controls.recordingNotice`, and `controls.dragInstructions`                 | Needed information: split long mixed-purpose notices into the relevant control help and one compact save/stop notice. Retain silent-preview and discarded-output warnings; use `aria-describedby` to associate visible keyboard instructions with the image instead of maintaining a second copy. Preserve keyboard accessibility.                                      |
| D40 | `PLAN.md`, status and completed-cleanup claims                                                                              | Understanding: earlier checkboxes overstate removal of obsolete browser help and complete cleanup. Record the earlier implementation as historical local verification, reopen the contradicted criteria, and link this remediation inventory from Contents. Do not relabel audit findings as implemented fixes.                                                         |

### Protected-rule findings and decisions

These are findings about the supplied rules, not edits authorized by this audit. Keep the files unchanged until the user approves the exact correction.

| ID  | File and passage                                                                                                                                                      | Finding and proposed decision                                                                                                                                                                                                                                                                     |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P01 | `rules/BASH.md`, Arithmetic, lines 1059-1068                                                                                                                          | The “Validate external input” example accepts arbitrary digit strings and evaluates them using Bash's default numeric base. `09` fails and very long numbers can overflow. Bound length and explicitly handle decimal input before arithmetic. Do not execute the example against real resources. |
| P02 | `rules/BASH.md`, Function-scoped cleanup, lines 1725-1733                                                                                                             | The RETURN trap is not restored, so calling the function changes the caller's trap state. Replace the example with a genuinely scoped cleanup pattern or explicitly preserve/restore the prior trap.                                                                                              |
| P03 | `rules/BASH.md`, safe rewrite examples at lines 1382-1389 and 2099-2101                                                                                               | The later “preferred” rewrite omits the checked `sed` failure path shown earlier and can move failed output over the original. Keep one checked pattern and link to it instead of maintaining contradictory copies.                                                                               |
| P04 | `rules/PYTHON.md`, string-formatting HTML example, lines 2533-2537                                                                                                    | The “Good” example inserts names into HTML without escaping them. Use a plain-text example for string joining, or escape the values explicitly if teaching HTML construction. It should not teach an unsafe pattern incidentally.                                                                 |
| P05 | `rules/PYTHON.md::_trim_history_messages` example, lines 1657-1663                                                                                                    | A zero limit returns all messages because `[-0:]` equals `[0:]`. State and enforce a positive-limit precondition or handle zero explicitly. Do not present the current snippet as a correct general history limiter.                                                                              |
| P06 | `rules/DOCUMENTATION.md`, guarantee example, lines 1130-1134                                                                                                          | A request timing out after 30 seconds is not a guarantee that it completes successfully within 30 seconds. Distinguish the timeout trigger from successful completion and from cancellation/cleanup time.                                                                                         |
| P07 | `rules/BASH.md`, line-ending conversion, lines 194-197                                                                                                                | `tr -d '\r'` removes every carriage return, not only CRLF endings, writes to a predictable sidecar path, and replacement can lose the script's executable mode. Recommend the configured formatter or a checked conversion that preserves content and file mode.                                  |
| P08 | `rules/GENERAL.md`, Required comments; `rules/PYTHON.md`, Docstrings; `rules/BASH.md`, Comments; `quality/config/eslint/rules.js`; `pyproject.toml::tool.interrogate` | Universal documentation coverage can demand restatements where names/types already express the entire contract. Decide whether to retain concise mandatory summaries or permit narrowly defined omissions. Do not resolve the conflict by padding code/comments or lowering all coverage targets. |
| P09 | `rules/NAMING.md`, vocabulary and folder rules; `quality/config/naming/terms.json`; Q24-Q29                                                                           | Mechanical vocabulary, size, and directory counts can conflict with recognizable domain terminology and useful callbacks. Review exact examples together with enforcement. Do not replace a meaningful name with a less familiar synonym just to evade the rule.                                  |
| P10 | `rules/PYTHON.md`, no-inline-import guidance; root loader and `src/execution/session/reservation.py::_lock`                                                           | The rule wording is absolute, while current host initialization and mutually exclusive Windows/POSIX imports have justified scoped exceptions. Make the exception contract explicit if changing the rule. Do not import unavailable platform modules unconditionally to satisfy prose.            |

### Remediation priorities

1. **Correctness and consequential instructions:** R01-R04, R17, R40, U06, U15-U16, W01-W02, Q11-Q18, Q22-Q24, Q31-Q32; D14-D15, D25, and D35 for billable overhead. These have concrete failure paths or materially affect a user's decision.
2. **Remove obsolete or misleading material:** D01-D13, R11-R15, R18-R19, R27-R33, R38-R39, U01-U02, and W11-W13. Keep current installation instructions and real resource-safety explanations.
3. **Simplify and name existing code accurately:** remaining R/U/W/Q findings. Implement internal type/owner changes before callers, and regenerate browser/workflow output only after source edits. Keep each domain's behavior and public contracts intact.
4. **Resolve protected policy decisions:** P01-P10 and approval-dependent Q items. Correctness fixes in checkers must preserve or improve detection. No rule removal, broader exemption, or security-policy change is approved by this review.

Writing changes can proceed independently of most code changes once authorized. W10 and the native-locale validator work depend on explicitly settling the supported locale shape. R35 depends on provider-unit evidence. The complete English node catalog and Registry identity remain separate unresolved decisions.

### File review ledger

The ledger accounts for all 598 files in the audit inventory, not the 173 already-deleted paths. Findings are recorded above by file and declaration. An entry without a finding means no additional issue was recorded, not a guarantee of defect-free code.

Review modes:

- `S`: authored source, configuration, or prose read directly, including adjacent contracts where needed.
- `P`: protected instructions read; proposed corrections require separate approval.
- `G`: generated artifact reviewed through its maintained source. Workflow titles and note text were also inspected in all 33 JSON outputs; the generated index was read directly. This is not a host/rendered workflow check.
- `B`: binary asset classified by its references and documented purpose; no replacement, playback, visual-quality claim, or new provenance verification.
- `L`: dependency lockfile classified against its owning manifest; no line-by-line package/security audit or dependency update in this writing review.
- `H`: legal text read and preserved, not rewritten for style or legally certified.
- `M`: pinned upstream-rule manifest reviewed for its structure and consumer; individual upstream rules are not project-authored prose and were not audited here.

```text
S .githooks/commit-msg
S .githooks/pre-commit
S .githooks/pre-push
S .mise/tasks/audit/frontend
S .mise/tasks/audit/python
S .mise/tasks/check
S .mise/tasks/deps/_default
S .mise/tasks/deps/export
S .mise/tasks/deps/verify
S .mise/tasks/format/_default
S .mise/tasks/format/check
S .mise/tasks/frontend/build
S .mise/tasks/frontend/check
S .mise/tasks/hook/commit-msg
S .mise/tasks/hook/pre-commit
S .mise/tasks/hook/pre-push
S .mise/tasks/licenses/_default
S .mise/tasks/links/external
S .mise/tasks/lint/_default
S .mise/tasks/lint/docs
S .mise/tasks/lint/frontend
S .mise/tasks/lint/hooks
S .mise/tasks/lint/mise
S .mise/tasks/lint/policy
S .mise/tasks/lint/python
S .mise/tasks/lint/quality
S .mise/tasks/lint/shell
S .mise/tasks/models/check
S .mise/tasks/models/validate
S .mise/tasks/release/package
S .mise/tasks/security/_default
S .mise/tasks/security/rules
S .mise/tasks/setup
S .mise/tasks/type/_default
S .mise/tasks/type/frontend
S .mise/tasks/type/python
S .mise/tasks/workflows/build
S .mise/tasks/workflows/check
S config/__init__.py
S config/diagnostics.py
S config/discovery.py
S config/generation/__init__.py
S config/generation/fast.py
S config/generation/prompts.py
S config/generation/session.py
S config/generation/speech.py
S config/generation/video.py
S config/generation/world.py
S config/live.py
S config/media/__init__.py
S config/media/audio.py
S config/media/capture.py
S config/media/images.py
S config/media/recording.py
S config/media/video.py
S config/media/webcam.py
S config/media/workers.py
S config/models.py
S config/nodes.py
S config/package.py
S config/routes.py
S config/security.py
S config/serialization.py
S config/settings.py
G workflows/README.md
B workflows/assets/fictional-portrait.png
B workflows/assets/forest-illustration.png
B workflows/assets/forest-motion.mp4
B workflows/assets/forest-path.png
B workflows/fast-h3-01-text-to-video.jpg
G workflows/fast-h3-01-text-to-video.json
G workflows/fast-h3-02-image-to-video.json
G workflows/fast-h3-03-first-and-last-frames.json
G workflows/fast-h3-04-ending-frame.json
G workflows/fast-h3-05-continue-scene.json
G workflows/fast-h3-06-continue-image.json
G workflows/helios-01-text-to-video.json
B workflows/helios-02-image-to-video.jpg
G workflows/helios-02-image-to-video.json
G workflows/helios-03-prompt-sequence.json
G workflows/helios-04-image-sequence.json
G workflows/helios-05-live-prompt.json
G workflows/helios-06-live-image.json
G workflows/lingbot-01-explore-image.json
G workflows/lingbot-02-live-camera.json
G workflows/lingbot-world-2-01-explore-image.json
G workflows/lingbot-world-2-02-live-camera.json
G workflows/longlive-v2-01-text-to-video.json
G workflows/longlive-v2-02-storyboard.json
G workflows/longlive-v2-03-live-prompt.json
G workflows/ltx2-01-speaking-portrait.json
G workflows/sana-streaming-01-edit-video.json
G workflows/sana-streaming-02-live-prompt.json
G workflows/sana-streaming-03-webcam.json
G workflows/visko-dynamic-01-text-to-video.json
G workflows/visko-dynamic-02-image-to-video.json
G workflows/visko-dynamic-03-live-prompt.json
G workflows/visko-stable-01-text-to-video.json
G workflows/visko-stable-02-image-to-video.json
G workflows/visko-stable-03-live-prompt.json
G workflows/x2-01-edit-video.json
G workflows/x2-02-reference-edit.json
G workflows/x2-03-webcam.json
G workflows/x2-04-live-prompt.json
S locales/en/commands.json
S locales/en/main.json
S locales/en/nodeDefs.json
S locales/en/workflows.json
S quality/__init__.py
S quality/config/__init__.py
S quality/config/duplication/bash.json
S quality/config/duplication/css.json
S quality/config/duplication/javascript.json
S quality/config/duplication/python.json
S quality/config/eslint/base.mjs
S quality/config/eslint/index.js
S quality/config/eslint/limits.js
S quality/config/eslint/options.js
S quality/config/eslint/rules.js
S quality/config/eslint/runtime.js
S quality/config/html/generated.json
S quality/config/html/links.js
S quality/config/html/templates.json
S quality/config/imports/aliases.js
S quality/config/imports/knip.json
S quality/config/imports/madge.cjs
S quality/config/naming/__init__.py
S quality/config/naming/identifiers.js
S quality/config/naming/javascript.json
S quality/config/naming/policy.json
S quality/config/naming/rules.py
S quality/config/naming/schema.py
S quality/config/naming/terms.json
S quality/config/package-json/dependencies.js
S quality/config/package-json/manifest.js
S quality/config/python/__init__.py
S quality/config/python/imports.json
S quality/config/python/limits.py
S quality/config/python/packages.json
S quality/config/python/rules.py
S quality/config/python/schema.py
S quality/config/repository/__init__.py
S quality/config/repository/commitlint.json
S quality/config/repository/declarations.js
S quality/config/repository/dependencies.py
S quality/config/repository/directories.js
S quality/config/repository/extensions.js
S quality/config/repository/folders.py
S quality/config/repository/functions.json
S quality/config/repository/functions.py
S quality/config/repository/integrity.py
S quality/config/repository/licenses/environment.sh
S quality/config/repository/licenses/javascript.json
S quality/config/repository/licenses/policy.json
S quality/config/repository/paths.py
S quality/config/repository/scopes.js
S quality/config/repository/translations.py
S quality/config/security/__init__.py
S quality/config/security/bearer/environment.sh
S quality/config/security/bearer/false-positives.json
S quality/config/security/codeql/frontend/environment.sh
S quality/config/security/codeql/frontend/paths.js
S quality/config/security/codeql/frontend/scan.yml
S quality/config/security/codeql/python/environment.sh
S quality/config/security/codeql/python/scan.sh
S quality/config/security/codeql/python/scan.yml
S quality/config/security/gitleaks/baseline.json
S quality/config/security/gitleaks/config.toml
S quality/config/security/gitleaks/environment.sh
S quality/config/security/gitleaks/reasons.json
S quality/config/security/osv/config.toml
S quality/config/security/osv/environment.sh
S quality/config/security/semgrep/checksums.txt
S quality/config/security/semgrep/environment.sh
S quality/config/security/semgrep/frontend.yml
S quality/config/security/semgrep/hooks.yml
S quality/config/security/semgrep/markers.yml
M quality/config/security/semgrep/packs.json
S quality/config/security/semgrep/python.yml
S quality/config/security/semgrep/secrets.yml
S quality/config/shell.py
S quality/config/shellcheckrc
S quality/lib/__init__.py
S quality/lib/comfy.py
S quality/lib/diagnostics.py
S quality/lib/files.py
S quality/lib/json_config.py
S quality/lib/languages.py
S quality/lib/output.py
S quality/lib/process.py
S quality/lib/source.py
S quality/package.json
S quality/python/__init__.py
S quality/python/policy.py
S quality/python/rules/__init__.py
S quality/python/rules/all_at_bottom.py
S quality/python/rules/function_length.py
S quality/python/rules/imports/__init__.py
S quality/python/rules/imports/boundary.py
S quality/python/rules/imports/cycles.py
S quality/python/rules/imports/deferred.py
S quality/python/rules/imports/exports.py
S quality/python/rules/imports/graph.py
S quality/python/rules/imports/layout.py
S quality/python/rules/module_length.py
S quality/python/rules/prefix_collisions.py
S quality/python/rules/runtime_singletons.py
S quality/python/rules/single_file_folders.py
S quality/python/runner.py
S quality/python/typecheck.py
S quality/repository/__init__.py
S quality/repository/dependencies.py
S quality/repository/environment.py
S quality/repository/functions/__init__.py
S quality/repository/functions/policy.py
S quality/repository/functions/python.py
S quality/repository/functions/references.py
S quality/repository/functions/runner.py
S quality/repository/functions/semantics.py
S quality/repository/functions/shell.py
S quality/repository/hooks/__init__.py
S quality/repository/hooks/setup.py
S quality/repository/hooks/staged.py
S quality/repository/hooks/steps.sh
S quality/repository/integrity/__init__.py
S quality/repository/integrity/config.js
S quality/repository/integrity/config.py
S quality/repository/integrity/directory-prefixes.js
S quality/repository/integrity/folder-policy.js
S quality/repository/integrity/folder.py
S quality/repository/integrity/gitleaks.py
S quality/repository/integrity/policies.py
S quality/repository/integrity/suppressions.py
S quality/repository/integrity/typecheck.py
S quality/repository/licenses/__init__.py
S quality/repository/licenses/check.py
S quality/repository/licenses/check.sh
S quality/repository/licenses/javascript.js
S quality/repository/licenses/policy.py
S quality/repository/naming/__init__.py
S quality/repository/naming/analyze.js
S quality/repository/naming/analyze.py
S quality/repository/naming/cases.py
S quality/repository/naming/check.js
S quality/repository/naming/checks/__init__.py
S quality/repository/naming/checks/folders.py
S quality/repository/naming/checks/shell.py
S quality/repository/naming/extractors/__init__.py
S quality/repository/naming/extractors/files.js
S quality/repository/naming/extractors/javascript.js
S quality/repository/naming/extractors/paths.py
S quality/repository/naming/extractors/python.py
S quality/repository/naming/extractors/shell.py
S quality/repository/naming/parts.py
S quality/repository/naming/policy.js
S quality/repository/naming/policy.py
S quality/repository/naming/runner.py
S quality/repository/naming/scope.js
S quality/repository/naming/types.py
S quality/repository/naming/validate.py
S quality/repository/package-json/dependencies.js
S quality/repository/package-json/json.js
S quality/security/__init__.py
S quality/security/bandit/run.sh
S quality/security/bearer/run.sh
S quality/security/codeql/__init__.py
S quality/security/codeql/cleanup.sh
S quality/security/codeql/frontend/database.sh
S quality/security/codeql/frontend/paths.js
S quality/security/codeql/frontend/run.sh
S quality/security/codeql/frontend/sarif.js
S quality/security/codeql/frontend/scan.sh
S quality/security/codeql/python/__init__.py
S quality/security/codeql/python/paths.py
S quality/security/codeql/python/sarif.py
S quality/security/codeql/python/scan.sh
S quality/security/gitleaks/run.sh
S quality/security/osv/run.sh
S quality/security/pip-audit/run.sh
S quality/security/semgrep/__init__.py
S quality/security/semgrep/download.py
S quality/security/semgrep/install.py
S quality/security/semgrep/run.sh
S quality/security/worktree.py
S quality/shared/eslint/plugin/imports.js
S quality/shared/eslint/plugin/index.js
S quality/shared/eslint/plugin/path-policy/index-file.js
S quality/shared/eslint/plugin/path-policy/normalization.js
S quality/shared/eslint/plugin/rules/header-comments-before-imports.js
S quality/shared/eslint/plugin/rules/import-layout.js
S quality/shared/eslint/plugin/rules/import-path-style.js
S quality/shared/eslint/plugin/rules/max-barrel-reexports.js
S quality/shared/eslint/plugin/rules/newline-after-imports.js
S quality/shared/eslint/plugin/rules/no-call-through.js
S quality/shared/eslint/plugin/rules/no-cross-folder-imports.js
S quality/shared/eslint/plugin/rules/no-duplicate-barrel-exports.js
S quality/shared/eslint/plugin/rules/no-export-only-files.js
S quality/shared/eslint/plugin/rules/no-exported-alias-constants.js
S quality/shared/eslint/plugin/rules/no-imports-after-statements.js
S quality/shared/eslint/plugin/rules/no-prefix-collisions.js
S quality/shared/eslint/plugin/rules/no-reexports-outside-index.js
S quality/shared/eslint/plugin/rules/no-single-file-folders.js
S quality/shared/eslint/plugin/rules/no-trivial-functions.js
S quality/shared/files.js
S quality/shared/json.js
S quality/shared/naming/cases.js
S quality/shared/naming/identifier-parts.js
S quality/shared/naming/validate-name.js
S quality/shell/__init__.py
S quality/shell/checks/__init__.py
S quality/shell/checks/architecture.py
S quality/shell/checks/bash.py
S quality/shell/checks/complexity.py
S quality/shell/checks/config.py
S quality/shell/checks/config_guards.py
S quality/shell/checks/disable_justification.py
S quality/shell/checks/docs.py
S quality/shell/checks/duplicate_functions.py
S quality/shell/checks/embeds.py
S quality/shell/checks/heredocs.py
S quality/shell/checks/length.py
S quality/shell/checks/prefix_collisions.py
S quality/shell/checks/safety.py
S quality/shell/checks/unused_functions.py
S quality/shell/parsers.py
S quality/shell/runner.py
S quality/shell/scope.py
S quality/shell/syntax.py
S quality/shell/tools.py
S quality/web/links/check.mjs
S .comfyignore
S .gitattributes
S .gitignore
S .markdownlint-cli2.yaml
S .prettierignore
S .prettierrc.json
S .stylelintrc.json
S .typos.toml
S ADVANCED.md
P AGENTS.md
P CLAUDE.md
H LICENSE.md
S PLAN.md
S README.md
S __init__.py
S __main__.py
L bun.lock
S bunfig.toml
S mise.toml
S package.json
S pyproject.toml
S pyrightconfig.json
G requirements.txt
S tsconfig.json
L uv.lock
P rules/BASH.md
P rules/DOCUMENTATION.md
P rules/GENERAL.md
P rules/NAMING.md
P rules/PLANNING.md
P rules/PYTHON.md
P rules/TYPESCRIPT.md
P rules/WRITING.md
S scripts/__init__.py
S scripts/dependencies.py
S scripts/frontend.mjs
S scripts/models.py
S scripts/nodes/__init__.py
S scripts/nodes/metadata.py
S scripts/nodes/native.py
S scripts/nodes/schema.py
S scripts/nodes/translations.py
S scripts/workflows/__init__.py
S scripts/workflows/build.py
S scripts/workflows/definitions.py
S scripts/workflows/example.py
S scripts/workflows/index.py
S scripts/workflows/layout.py
S scripts/workflows/live.py
S scripts/workflows/models/__init__.py
S scripts/workflows/models/fast.py
S scripts/workflows/models/helios.py
S scripts/workflows/models/lingbot.py
S scripts/workflows/models/longlive.py
S scripts/workflows/models/ltx.py
S scripts/workflows/models/sana.py
S scripts/workflows/models/visko.py
S scripts/workflows/models/x2.py
S scripts/workflows/notes.py
S scripts/workflows/serialize.py
S src/__init__.py
S src/comfy/__init__.py
S src/comfy/execution.py
S src/comfy/interaction.py
S src/comfy/routes.py
S src/credentials.py
S src/discovery/__init__.py
S src/discovery/checker.py
S src/discovery/contracts.py
S src/discovery/navigation.py
S src/discovery/routes.py
S src/discovery/sources.py
S src/discovery/store.py
S src/discovery/views.py
S src/errors.py
S src/execution/__init__.py
S src/execution/admission.py
S src/execution/authentication.py
S src/execution/cleanup.py
S src/execution/diagnostics.py
S src/execution/events.py
S src/execution/failures.py
S src/execution/fast/__init__.py
S src/execution/fast/clip.py
S src/execution/fast/continuation.py
S src/execution/fast/generate.py
S src/execution/helios/__init__.py
S src/execution/helios/prompts.py
S src/execution/helios/request.py
S src/execution/inputs.py
S src/execution/interaction.py
S src/execution/lingbot/__init__.py
S src/execution/lingbot/request.py
S src/execution/longlive/__init__.py
S src/execution/longlive/request.py
S src/execution/longlive/storyboard.py
S src/execution/ltx/__init__.py
S src/execution/ltx/request.py
S src/execution/operation.py
S src/execution/report.py
S src/execution/sana/__init__.py
S src/execution/sana/contract.py
S src/execution/sana/request.py
S src/execution/session/__init__.py
S src/execution/session/capture.py
S src/execution/session/reservation.py
S src/execution/session/resources.py
S src/execution/transport.py
S src/execution/visko/__init__.py
S src/execution/visko/request.py
S src/execution/x2/__init__.py
S src/execution/x2/request.py
S src/extension.py
S src/http/__init__.py
S src/http/guard.py
S src/http/request.py
S src/http/security.py
S src/language.py
S src/live/__init__.py
S src/live/commands.py
S src/live/control/__init__.py
S src/live/control/interaction.py
S src/live/control/lease.py
S src/live/interaction.py
S src/live/lease.py
S src/live/options.py
S src/live/preview.py
S src/live/registry.py
S src/live/routes.py
S src/media/__init__.py
S src/media/audio.py
S src/media/capture.py
S src/media/encoding.py
S src/media/images.py
S src/media/metadata/__init__.py
S src/media/metadata/read.py
S src/media/metadata/worker.py
S src/media/output.py
S src/media/process.py
S src/media/recording/__init__.py
S src/media/recording/assemble.py
S src/media/recording/download.py
S src/media/recording/manifest.py
S src/media/recording/streams.py
S src/media/recording/worker.py
S src/media/units.py
S src/media/video/__init__.py
S src/media/video/components.py
S src/media/video/frames.py
S src/media/video/input.py
S src/media/video/publish.py
S src/media/video/worker.py
S src/media/webcam.py
S src/models.py
S src/nodes/__init__.py
S src/nodes/controls.py
S src/nodes/fast/__init__.py
S src/nodes/fast/continuation.py
S src/nodes/fast/generate.py
S src/nodes/helios/__init__.py
S src/nodes/helios/animate.py
S src/nodes/helios/generate.py
S src/nodes/helios/prompt.py
S src/nodes/helios/sequence.py
S src/nodes/lingbot/__init__.py
S src/nodes/lingbot/explore.py
S src/nodes/lingbot/schema.py
S src/nodes/lingbot/world.py
S src/nodes/longlive/__init__.py
S src/nodes/longlive/generate.py
S src/nodes/longlive/shot.py
S src/nodes/longlive/storyboard.py
S src/nodes/ltx/__init__.py
S src/nodes/ltx/speak.py
S src/nodes/sana/__init__.py
S src/nodes/sana/edit.py
S src/nodes/sana/webcam.py
S src/nodes/visko/__init__.py
S src/nodes/visko/dynamic.py
S src/nodes/visko/stable.py
S src/nodes/x2/__init__.py
S src/nodes/x2/edit.py
S src/nodes/x2/webcam.py
S src/paths.py
S src/runtime.py
S src/serialization.py
S src/settings/__init__.py
S src/settings/conflict.py
S src/settings/execution.py
S src/settings/routes.py
S src/settings/schema.py
S src/settings/store.py
S src/state/__init__.py
S src/state/credentials.py
S src/state/discovery.py
S src/state/documents.py
S src/state/generation/__init__.py
S src/state/generation/fast.py
S src/state/generation/helios.py
S src/state/generation/inputs.py
S src/state/generation/lingbot.py
S src/state/generation/longlive.py
S src/state/generation/ltx.py
S src/state/generation/sana.py
S src/state/generation/visko.py
S src/state/generation/x2.py
S src/state/live.py
S src/state/media.py
S src/state/models.py
S src/state/recording.py
S src/state/reports.py
S src/state/session.py
S src/state/settings.py
S src/state/workers.py
S src/storage.py
S web/browser.ts
S web/discovery/api.ts
S web/discovery/dialog.ts
S web/discovery/pricing.ts
S web/discovery/rate.ts
S web/discovery/row.ts
S web/discovery/schema.ts
S web/dom.ts
S web/extension.ts
S web/host.d.ts
S web/http.ts
S web/language.ts
S web/live/api.ts
S web/live/commands.ts
S web/live/controls.ts
S web/live/drag.ts
S web/live/input.ts
S web/live/pointer.ts
S web/live/polling.ts
S web/live/scene.ts
S web/live/schema.ts
S web/live/sound.ts
S web/live/state.ts
S web/live/webcam.ts
S web/localization.ts
S web/nodes/contracts.ts
S web/nodes/inputs.ts
S web/routes.ts
S web/schema.ts
S web/settings/api.ts
S web/settings/dialog.ts
S web/settings/schema.ts
S web/styles/interface.css
G web/extension.css
G web/extension.js
S web/docs/ReactorIncFastContinue.md
S web/docs/ReactorIncFastGenerate.md
S web/docs/ReactorIncHeliosAddPrompt.md
S web/docs/ReactorIncHeliosAnimate.md
S web/docs/ReactorIncHeliosGenerate.md
S web/docs/ReactorIncHeliosSequence.md
S web/docs/ReactorIncLingBotExplore.md
S web/docs/ReactorIncLingBotWorld2Explore.md
S web/docs/ReactorIncLongLiveAddShot.md
S web/docs/ReactorIncLongLiveGenerate.md
S web/docs/ReactorIncLongLiveStoryboard.md
S web/docs/ReactorIncLtxSpeak.md
S web/docs/ReactorIncSanaEditVideo.md
S web/docs/ReactorIncSanaWebcam.md
S web/docs/ReactorIncViskoDynamicGenerate.md
S web/docs/ReactorIncViskoStableGenerate.md
S web/docs/ReactorIncX2EditVideo.md
S web/docs/ReactorIncX2Webcam.md
```

The existing narrow host declarations, typed records, credential redaction, bounded media workers, native V3 registration, `web/`/`web/` split, schema-owned English defaults, and useful cancellation comments are retained. Short helpers are not inherently defective. Separate model contracts, input/output validation boundaries, and independently useful native help pages are not duplicates merely because some statements resemble each other.

### Follow-up acceptance

- [ ] Implement the authorized findings, recording any declined policy proposals separately rather than silently omitting them.
- [ ] Preserve all public node IDs, parameter names/order/defaults/limits, output order, provider command semantics, and persistent private-state formats.
- [ ] Regenerate `web/extension.js` and `web/extension.css` from their `web/` sources with `mise run frontend:build`; regenerate the 33 workflow JSONs and index with `mise run workflows:build` after their text sources change. Do not rebuild or replace the six binary assets for prose cleanup.
- [ ] Review changed public text against the four plain-language principles and remove internal status/approval narration. This requires reading the text, not a new readability-score checker.
- [ ] Within the user's requested local verification scope, run the existing relevant lint/type/build checks after implementation. Do not add automated tests, run ComfyUI workflows, install into a host, publish, or make paid requests for this audit.

## Implementation order

### Audit follow-up order

The completed migration stages below remain the record of the main implementation. The newly unchecked audit items require a separate implementation request; this plan update does not execute them.

1. Resolve the complete-English-catalog decision before changing catalog completeness or adding extraction tooling. That decision does not block the independent media-error and configuration ownership corrections.
2. Add the locale messages and named constants specified in sections 9 and 3 before updating `src/media/process.py`, the reservation reader, the recording worker, and the two browser calculators. Preserve public node parameters, error codes, message text, media output, and all existing limits.
3. Align the existing native translation/guide validators with the explicitly listed nullable-tooltip, generated seed-control, and localized-guide contracts. Add category defaults through the native `main.nodeCategories` surface and document the queued-execution language limitation.
4. Regenerate `web/extension.js` and `web/extension.css` after browser or bundled message changes, using `mise run frontend:build`. Regenerate examples only if their maintained builder text changes; do not rewrite generation prompts or alter workflow parameters as a localization side effect.
5. When verification is requested, use the existing scoped lint, type, `models:validate`, frontend, and workflow artifact checks. Before publication, repack and re-inspect the official archive after any packaged source changes. Retain the separate approval requirements for host execution, full release checks, publishing, and paid runs.

### Stage A: Confirm boundaries and supported tools

Inspect the current installed host/frontend and CLI capabilities, actual Registry identity/publication history, dataclass dependencies, and current dependency/asset consumers. Confirm the exact application/obsolete-task deletion set. Keep protected rules and checker implementations intact; report concrete conflicts rather than planning a lint-rule deletion.

Publishing credentials and final Registry details block publication, not unrelated schema, frontend, or runtime cleanup. Do not invent an ordering dependency that prevents those independent changes.

### Stage B: Establish schemas and metadata ownership

Implement sections 1 through 3: establish the domain dataclasses under `src/state/` first, separate provider operations and record factories from those records, and update every runtime/worker caller to the declaring state modules. Keep the existing package roots and rule-compliant import boundaries. Then centralize repeated root calculation, declare English schemas directly, pass the registration-derived mapping into discovery, and update development/schema consumers.

Update state records and operation contracts before node/session callers. Update `src/runtime.py`, `ModelStore`, and discovery presentation signatures before their callers. Update workflow note/layout/index callers in the same stage. Remove vacated data-only modules only after imports have moved. Delete the repeated `config/models/nodes.py` table only after stage D removes its remaining legacy help-builder consumers; do not leave a forwarding alias.

### Stage C: Complete execution and provider-boundary cleanup

Implement sections 4 through 6, preserving provider session/media/security lifetimes while removing redundant internal validation or forwarding code. Confirm the actual native media and cache contracts before changing their callers.

Do not publish an intermediate state. Do not replace real lifecycle code with a generic framework.

### Stage D: Clean frontend source and remove duplicate UI/help

Implement sections 7 through 9. Keep TypeScript in `web`, retain esbuild, adopt official types, remove metadata-repair hooks and custom help, retain live controls, and retarget source/security scopes in the same change.

Backend model/settings contracts precede their changed UI consumers. Pure source relocation/build changes can proceed independently of unrelated provider cleanup once those contracts are fixed.

### Stage E: Regenerate native artifacts from retained builders

Implement section 10. Correct the selected native-node widget serialization, generate all 33 flat examples and the index, move binary assets byte-for-byte, and build `web/extension.js` plus `web/extension.css`.

Inspect generated workflows in ComfyUI when authorized and fix builder source for defects. Do not replace builders with hand-maintained output edits. Remove old grouped outputs and nested bundles before the final host loads the new served root.

### Stage F: Remove custom distribution and finish tooling/docs

Implement sections 11 through 14: delete the old release implementation, configure official publishing metadata/ignores, preserve archive scanning through tool delegation, finish targeted tooling cleanup, and rewrite user procedures.

Distribution deletion and metadata configuration can proceed independently of model algorithms. Packing waits for the final runtime assets. Security coverage changes accompany each source move rather than being deferred until this stage.

### Stage G: Verify checkout, pack, publish, and verify the public installation

Run the authorized final checks and actual checkout acceptance. Use official `comfy node pack`, inspect/scan its payload, keep inputs unchanged, and publish only after explicit authorization. Verify the selected published version through Manager/Registry installation without leaving a second loaded checkout copy.

This is one direct replacement, with no intermediate compatibility release, custom installer, or parallel release process.

## Acceptance and verification

The user requested the final release/build/security/artifact process in this plan. These are planned execution requirements, not a claim that those operations have run during the documentation update. Use the existing local tools when execution is authorized. No automated test files or commands are proposed.

### Source and generated artifacts

- [x] Exactly 18 existing Reactor public operations register once through V3.
- [x] Schemas contain readable English defaults without reading a complete locale mirror.
- [x] Native locale overrides may be partial; no generated node/English catalog is required.
- [x] Discovery and workflow metadata use actual registrations and schemas without circular host imports or a second authored node/model table.
- [x] `src`, useful Python `config`, worker entrypoints, esbuild, and workflow builders remain usable. Runtime imports do not pull in development tools.
- [x] Runtime data records are declared under domain modules in `src/state/`, which imports only the standard library and its own modules; no duplicate old definitions or re-export aliases remain. Records that hold live resources stay with their owners. Development-only dataclasses stay with development tooling.
- [x] State modules contain data contracts, not provider execution, file/version lookup, host initialization, stores, or worker control. Isolated-worker imports remain host-free and private records retain redacted representations.
- [x] `rules/`, agent instructions, quality checker implementations, `mise.toml`, normal mise tasks, and security controls are preserved. Only the three named obsolete custom-install/generated-help task files are removed; required path/coverage updates do not weaken enforcement.
- [x] Browser source lives in `web`, the existing root manifest/compiler own it, and esbuild produces exactly one registration entry plus Reactor's stylesheet.
- [x] Retained native help is served directly; nodes without detailed pages have usable schema help. No generated help copy is required by a build or check.
- [x] All 33 flat workflows, the generated index, existing thumbnails, and unchanged sample media are present under `workflows`.
- [x] Workflow/frontend check modes compare artifacts without rewriting canonical files. Generated artifacts match their maintained sources.
- [x] No obsolete package identity, custom ZIP writer, uploader, installer, recovery machinery, nested old bundle, or template copy remains.
- [x] Existing dependency, security, license, documentation, type, lint, and artifact checks cover the final sources and package inputs. No detection/control is weakened to pass.

### Audit follow-up acceptance

- [ ] All 18 public media-error sentences have locale ownership and parent-process translation, with unchanged worker codes and fallback behavior. No worker imports localization or host bindings.
- [ ] The named reservation, PCM, audio-block, and browser-calculator values replace the listed literals without changing their values or behavior.
- [ ] Native category coverage and translation/guide validation match the reviewed contracts. Complete English catalog coverage is claimed only if that decision is approved and implemented; English-only execution and missing translations are not described as fully localized.
- [ ] Scoped checks and affected generated artifacts are reverified after implementation. Earlier passing lint/build/archive results remain evidence for the earlier source state, not proof that these newly identified gaps are fixed.

### Checkout acceptance in ComfyUI

With authorized host/browser access:

- [ ] Load the checkout through the native loader with one active node copy. Confirm that the browser assets are the new `web/extension.js` and `extension.css`.
- [ ] Confirm native node search/categories, schema labels, Parameters controls, native Info, commands, and template discovery.
- [ ] Open every generated example without missing nodes, malformed widget values, or connection warnings. Confirm the built-in save/load controls match the selected host.
- [ ] Inspect both templates with thumbnails and the canonical sample paths. Do not queue generation merely to check that a workflow opens.
- [ ] Confirm settings endpoints expose only credential status, enforce mutation restrictions, and keep server limits authoritative.
- [ ] Confirm catalog refresh updates metadata without generation or dynamic node registration.
- [ ] Confirm normal workflow/node lifecycle does not duplicate menus, subscriptions, stylesheets, or dialogs.

### Public package acceptance

- [x] The selected released comfy-cli (1.20.0) `node pack` creates `node.zip` with the intended members (249 files verified).
- [ ] The selected released comfy-cli's `publish` behavior is verified. `comfy node publish` has not run.
- [x] The official payload includes runtime `__main__.py`, `src`, Python `config`, requirements, locales, built browser assets, retained guides, examples, and sample assets.
- [x] The payload excludes development tools, TypeScript source, private state, local environments, obsolete archives/manifests, and generated duplicate help/media.
- [x] Archive member inspection and gitleaks secret scanning of the official `node.zip` succeed before publication.
- [ ] License review and the existing release-input check suite succeed before publication. These were not run against this archive.
- [ ] Publishing inputs remain unchanged between inspection and `comfy node publish`. No claim is made that publishing uploads the earlier ZIP bytes.
- [ ] The actual published version installs through Manager/Registry and loads using the same root entrypoint as the checkout. End users need no frontend build tools or custom installer.
- [ ] Repeat native node/help/template checks against that published installation. A successful source import or upload is not sufficient public-release evidence.

### Reactor execution acceptance

Paid operations require separately agreed scope and cost. Use the real installed distribution for final release evidence, not simulated provider results.

- [ ] Noninteractive text/image generation returns usable native video and optional audio; core Save Video/audio nodes consume the results.
- [ ] Local prompt-sequence and storyboard composition works without credentials or provider calls.
- [ ] Approved SANA/X2 file editing, Fast H3 continuation, LTX speech, LingBot/world navigation, and Visko sound paths preserve their actual model contracts.
- [ ] Approved live prompts, pointer controls, world controls, and webcams are owned by the submitting browser and release their tracks/leases.
- [ ] Noninteractive API execution does not depend on frontend callbacks. Browser-required modes fail clearly without an owner.
- [ ] Native cancellation during preparation, upload, remote execution, encoding, and cleanup leaves no orphaned local worker or silently reused uncertain remote session.
- [ ] Completed cached media remains readable. Changed execution settings/repeat controls invalidate the appropriate output; a price-only refresh does not trigger an unnecessary paid rerun.
- [ ] Failure reports remain actionable and redacted. Closing an unrelated workflow does not silently stop or restart paid work.

Any unexecuted acceptance item remains explicitly unverified. A successful build, source inspection, package upload, or model API response is not evidence that the whole workflow behaves correctly.

## Definition of done

- [ ] Complete the newly opened configuration and localization audit items, and record the explicit English-catalog decision without treating it as an official ComfyUI mandate. Retain the single `web/` directory, the justified worker entrypoint, public contracts, and protected tooling boundaries.
- [ ] Reactor and Live Shopping follow the same native extension and shared structural conventions. The explicitly documented workflow-authoring, generated-asset tracking, authorized checker changes, product responsibilities, and public-distribution differences remain; neither project gains or loses machinery merely for symmetry.
- [x] Ordinary `src`, useful `config`, root dependency/compiler files, esbuild, and workflow builders remain; runtime data records have one domain-based home under `src/state/`. There is no new packaging hierarchy, bundler/workspace migration, or generated runtime catalog.
- [x] All existing Reactor operations are accounted for and their runtime, media, security, and live-control lifetimes remain explicit.
- [x] V3 schemas, native locale overrides, direct Markdown help, native save/media behavior, and flat example discovery replace duplicated platform behavior.
- [x] Custom distribution code is deleted, not replaced: official `comfy node pack` and `comfy node publish` own packing/upload, and Manager/CLI own installation.
- [x] Security scanning and licensing remain project responsibilities applied to official package content, with unchanged-input publishing discipline.
- [x] Protected rules, existing quality checker implementations, mise tooling, and security controls remain. Configuration follows moved source and retired artifacts without changing enforcement semantics; no lint checker is deleted as a shortcut.
- [ ] Resolve section 15's obsolete-code and stale-export findings before claiming complete removal of unused paths and artifacts.
- [ ] Complete the authorized readability and maintainability remediation, with explicit dispositions for approval-dependent policy proposals. Passing lint alone does not meet the plain-language requirement.
- [x] User settings, credentials, catalog state, reservations, saved workflows, media, backups, and old reports have not been silently deleted or rewritten.
- [x] Checkout and published-installation evidence, paid-run approvals, remaining external inputs, and unverified acceptance items are reported accurately.
