# Comments

Read this rule when you write or change a comment.

## What a comment says

A comment explains why, not what, and describes the code in its current form.

Bad: `# Removed the old cache loader.` Good: `# The provider limits requests per hour, so read the cache first.`

## When to comment

A doc comment says what the signature does not. Never write a comment that only repeats a name or a type. Add other
comments only when a function:

- handles a failure that its public interface does not explain
- has concurrency, cancellation, or isolation requirements
- makes a security or privacy decision
- encodes a domain invariant such as `idempotent` or `retry-safe`
- sits on a hot path
- takes more than ten seconds to understand from its signature and body

## Keep comments true

Rewrite or delete a comment that describes behavior the code lacks, or the reason for a decision you undo.

- When you move or delete a declaration, do the same to its comment.
- Do not write work status in a comment. For example, do not describe a paused job or a temporary choice.
- Track unfinished work in the issue tracker, not in a comment.
