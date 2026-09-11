# Creating Plans

These rules apply whenever an agent creates any implementation plan, refactor
plan, documentation plan, data change plan, workflow plan, script plan, or
other planned change sequence.

## Contents

- [Complete change content](#complete-change-content)
- [No automated tests or unrequested checks](#no-automated-tests-or-unrequested-checks)
- [Implementation order](#implementation-order)
- [Plan detail level](#plan-detail-level)

## Complete change content

A plan must contain the complete content of every change it proposes.

Rules:

- Include a complete code diff or text diff for every code, configuration,
  documentation, data, script, and text change.
- Do not summarize a change when the exact diff can be shown.
- Do not describe a future edit without including the exact patch that makes the
  edit.
- Include every new file's full contents.
- Include every deleted file's full removed contents or the full deletion diff.
- Include every command needed to create, transform, move, rename, resize,
  regenerate, or delete an artifact.
- Include changes to generated files when the plan expects generated files to
  change.
- For generated results, binary assets, and other non-text artifacts, list the
  exact source path, output path, and operation.
- Also list the dimensions or metadata changes and the command or tool needed to
  reproduce the result.
- If a binary diff cannot be represented as text, include enough exact
  reproduction detail that the asset change is part of the plan rather than an
  implied follow-up.

Bad:

```text
Change workflow generation and regenerate the documented workflow.
```

Good:

```diff
diff --git a/src/settings/settings.py b/src/settings/settings.py
--- a/src/settings/settings.py
+++ b/src/settings/settings.py
@@
-duration_seconds = requested_seconds
+duration_seconds = min(requested_seconds, maximum_seconds)
```

```bash
mise run workflows:build
```

```text
Artifact change:
- Path: workflows/
- Operation: generate the documented workflow JSON
- Command: mise run workflows:build
```

## No automated tests or unrequested checks

Do not create or run automated tests. Do not include test files or test commands
in plans.

Include linting, formatting, type checks, security scans, builds, or manual
verification only when the user explicitly requests that verification. Keep
requested checks limited to the affected behavior.

## Implementation order

Plans must define the exact order of implementation.

Rules:

- Break the work into sequential steps.
- Put dependency discovery before edits that depend on that discovery.
- Put shared contract or type changes before callers that use them.
- Put data shape changes before runtime, workflow, or publishing surfaces that consume the data.
- Put ownership moves before import or call-site updates.
- Put generated output after the source change that produces it.
- Put cleanup after all call sites have moved.
- Keep each step concrete enough that another agent can execute it without
  inventing missing decisions.
- State which files, symbols, assets, commands, and diffs belong to each step.
- Do not hide multiple unrelated edits inside one broad step.

Bad:

```text
1. Refactor the loader.
2. Update the workflow command.
```

Good:

```text
1. Add the new `ModelSettings` field shown in the diff.
2. Update `build_settings` to populate the field using the exact diff.
3. Replace runtime and workflow call sites using the exact diff.
4. Remove the old derived-value helper using the exact deletion diff.
```

## Plan detail level

Plans must be extensive and detailed enough to be directly executable.

Rules:

- Include the reasoning needed to understand why the steps are ordered that way.
- Include file paths for every planned edit.
- Include exact names for new files, functions, types, commands, assets, and
  configuration keys.
- Include expected intermediate states when a sequence temporarily changes
  contracts, generated outputs, or asset files.
- Include all constraints, assumptions, and dependencies that affect execution.
- Include edge cases or failure modes only when they are part of the real
  requested work.
- Do not leave placeholders such as "update as needed", "adjust imports", or
  "fix any errors".
- Do not rely on the implementer to infer omitted code, omitted commands, or
  omitted asset operations.
