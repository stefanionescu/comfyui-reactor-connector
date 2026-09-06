# Work on the connector

Install the tools pinned in `mise.toml`, then run `mise run deps` to install the
locked development dependencies. Run `mise run setup` to configure the three
repository-local Git hooks. Setup preserves conflicting existing hooks and
reports that they need review. It does not change global Git settings.

Bun manages frontend dependencies and runs frontend commands. `bun.lock` records
the dependency versions. `mise run deps` installs those versions with install
scripts disabled. Checks do not install missing dependencies automatically.
After changing frontend code, run `mise run frontend:build` to update the browser
assets shipped with the connector. People installing the connector in ComfyUI
do not need Bun.

Declare runtime dependencies in `pyproject.toml`, then run `mise run deps:export`
to update `requirements.txt`. `mise run deps:check` checks that they match without
changing files or installing packages. The normal checks and package builder
reject a stale dependency file. Keep development tools in the development group.

Use `mise run check` for formatting, lint, types, local links, and generated-file
consistency. Hooks use the same static checks. They do not run test suites,
generate media, open provider sessions, or modify ComfyUI. Use separate formatting
and generation tasks when files need updating.

Keep run journals, account details, and temporary plans outside the public
repository. Workflows and node help contain user instructions and relevant limits.
They must not contain implementation history. Never buy credits or enable
automatic top-up as part of development.

## Commit messages

Use `type(scope): description`, with an optional scope and optional `!` before
the colon for a breaking change. Accepted types are feat, fix, docs, style,
refactor, perf, test, build, ci, chore, and revert. For example:

```text
fix(video): preserve source timing
docs: explain model refresh
feat(worlds)!: revise session controls
```

The `ci` type is accepted for compatibility with the reference convention; this
repository uses local hooks and does not add Git-hosted workflows. Git-generated
merge subjects, `Revert "..."`, and nonempty `fixup!`, `squash!`, or `amend!`
subjects are also accepted. The hook never rewrites a message.

## What the hooks check

`mise run lint:secrets` scans files Git can include, including new untracked files.
It uses the pinned gitleaks rules plus a Reactor key rule. Ignored private files
and account state are excluded. The check copies public files into a private
temporary directory, scans them locally, then removes the copy and report.
Output contains only file names, line numbers, and rule names; values stay hidden.
Secret detection supports review but cannot prove that a file contains no secrets.

The check runs through the normal local hooks and before package tasks. Inline
allow comments, ignore files, and environment overrides cannot skip a finding.
Any false-positive exception belongs in `.gitleaks.toml` and must match the
specific rule, file, and non-secret expression. Keep other matches active.

Pre-commit checks staged filenames with NUL-safe Git output. If an affected file
also has unstaged edits, the hook asks you to stage or separate those edits. It
then runs the normal checks against the matching worktree. It does not stash,
format, install dependencies, or stage files.

Commit-msg checks the subject convention and rejects recognized Reactor
credentials anywhere in the message. This check supports the broader secret
review; it does not detect every possible secret format.

Pre-push validates that every non-deleted ref being pushed names the checked-out
HEAD and that the worktree is clean. It runs the normal checks, then verifies
that HEAD and the worktree stayed unchanged. To push another revision, check it
out and validate it first. Ref deletion alone does not run source checks.

Hooks can be bypassed through Git's explicit `--no-verify` option when an urgent
maintenance task requires it. Record the reason and run the skipped checks
before accepting or publishing the change. A bypass never establishes release
acceptance. Do not add automatic bypasses to scripts or silently use one to make
a failing change pass.

Native Info links open the installed HTML guides. `mise run docs:build` generates
those pages and linked workflow downloads from the same authored Markdown and
workflow JSON files. Markdown rendering is a development dependency; installing
the connector does not add it to ComfyUI.

## Organize workflows

Edit the workflow definitions and notes under `scripts/`, then run
`mise run workflows:build`. The generated JSON files live in
`workflows/<model>/`. Each workflow has a unique filename, connected inputs and
outputs, and aligned notes. Run `mise run docs:build` after changing the examples.

The package builder includes the model folders and adds identical top-level JSON
copies inside the installed `workflows/` folder. ComfyUI's template browser reads
only top-level files. Its [template guide](https://docs.comfy.org/custom-nodes/workflow_templates)
supports `workflows/`, and its [template loader](https://github.com/Comfy-Org/ComfyUI/blob/master/app/custom_node_manager.py)
defines that discovery behavior. Do not edit the installed copies; rebuild them
from the source definitions. Use the built package to populate native Templates.
From a source checkout, drag an example from its model folder onto the canvas.

## Build and install a package

Run `mise run audit` before preparing a release or after changing dependencies.
It queries public advisory services with dependency names and versions. The
Python task audits the exact lockfile pins that apply to the current platform,
including development tools. Bun audits `bun.lock`. Neither task runs package
code, generates media, applies fixes, or changes the user's ComfyUI environment.

Audits are separate from `mise run check` and the offline hooks because they
need network access. A failed query or an advisory needs review; do not treat
it as a pass. These checks do not cover every package in a user's ComfyUI or
prove that a dependency is safe. Review code embedded inside vendor bundles
separately: overriding a dependency version does not replace an embedded copy.

Run `mise run release:package` to write a ComfyUI archive under `dist/`. Its name
contains the project version and a hash of the packaged files. The included
manifest lists every runtime file and its hash. This task does not publish anything.
It requires both static checks and dependency audits to pass. If an audit fails,
the release task stops before building the archive.

Package and help generation use the public file list from Git. Ignored files
inside a runtime or documentation directory are not added to the package or
rendered as help. A help link to an excluded file must be fixed before building.

To install that source into a local ComfyUI instance, pass its source directory:

```sh
mise run comfy:install -- --host "/path/to/ComfyUI"
```

Replace the example path with the directory containing `main.py` and `comfy_api`.
Finish active work and stop the instance before replacing its package. The task
builds an archive and installs it into `custom_nodes/reactor-inc`.
This local install task runs static build checks; it does not replace the
release task's dependency audit.
Install runtime dependencies using the [host's Python environment](installation.md),
then restart ComfyUI and refresh the browser to load changed code.

The installer preserves a managed previous package in `.reactor-package-backups`
beside the ComfyUI directory. It refuses to replace an existing connector folder
that has no package manifest. Move an unmanaged copy outside `custom_nodes`
yourself if you want to replace it. Private settings, user workflows, and media
are not part of the package. The [installation guide](installation.md) explains
manual restoration and removal.

The local installer also moves a managed `reactor-inc-connector` installation
to the backup folder when installing `reactor-inc`. It preserves saved node IDs
and private settings. Keep only one Reactor package in `custom_nodes`.
