# Git

Read this rule before you commit, push, tag, or open a pull request.

## Commits

- Commit only when the user asks.
- One change per commit. Put a rename and a behavior change in two commits.
- The body says what changed and why.
- Leave out counts of tests, files, or bytes.
- A commit message names only files, commands, and issues that exist in the repository. It names no finding ID, audit
  label, or plan step.
- Never bypass hooks with `--no-verify`.
- Never force-push the default branch or a protected branch.

### Commit message format

Write `<type>: <subject>` or `<type>(<scope>): <subject>`, with the subject in lowercase, and keep every line within 72
characters. A `feat` or `fix` subject says what changes for a user.

## Branches and pull requests

When changes go straight to the default branch, skip these steps.

- Name branches `<type>/<kebab-summary>`, such as `feat/order-export` or `fix/session-expiry`.
- Force-push your own branch only after a rebase you performed.
- Rebase onto the default branch before you open a pull request. Do not merge the default branch into a feature branch.
- Use the commit subject as the title for a single-commit branch. Otherwise, write one sentence for the whole change.
- The description states what changed, why, and which checks verified it. It links the issue.

## Releases

- Publish a package only through the release task or workflow, from a commit that CI tested.
