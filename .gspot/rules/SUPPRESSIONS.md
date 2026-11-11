# Suppressions

Read this rule before you add a suppression comment or run `gspot ignore`.

A suppression turns a lint rule off for one place, and it carries a reason.

- Write the reason as `reason: <sentence>.` directly above the suppression, or after the tool's separator on the same
  line. For example: `// eslint-disable-next-line no-console -- reason: the command prints its result`. The reason says
  why the lint rule misjudges this place.
- A reason states a fact that a reader can check in the repository today. Never cite a plan, a table, a conversation, or
  a decision that the repository does not hold.
- Scope a suppression to the narrowest thing that works: one lint rule, one line, one symbol. A file-wide suppression
  needs a reason that holds for every line.
- Suppress only when the lint rule misjudges this line. When the code breaks the lint rule, fix it.
- Never suppress a maximum, such as `complexity`, `max-lines`, or `max-statements`. Split the code by its steps, or ask
  the user to raise the limit in `gspot.toml`.
- Widen an import boundary or an import rule only after the user agrees.
- Never add filler statements to pass a check.

Never remove a configuration or lower the level to stop a finding.
