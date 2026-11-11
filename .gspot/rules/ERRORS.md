# Errors

Read this rule when you write code that raises, catches, or reports an error.

## Error taxonomy

- Return a typed result or throw a typed error for an expected operational failure. Invalid input, missing resources,
  denied permission, and provider timeouts need results the caller can act on.
- Never catch a programmer error, such as a broken invariant, to keep going. Log its stack and show a generic failure.

## Raising and catching

- Catch the narrowest type. Never a bare catch-all unless the block re-raises or deliberately isolates an operation and
  records the failure.
- Keep the try block around the one operation that can fail.
- Do not swallow failures. Handle, record, or re-raise each caught error.
- Run required cleanup in `finally` or the language's equivalent.

## Async work

- Capture the identity of the resource when async work starts. A late result never overwrites a newer resource or
  another session.
- Retry a write only when the operation has an idempotency key.

## Error messages

A developer tool may name the file, line, and setting that the user must fix. Keep unrelated private data out of every
output.

- Make messages actionable: tell the user what went wrong, not how the system works.
- In an API error response or a log entry, put the failing value in its own field.
- Keep message text stable so readers can search for it.
- Convert technical errors to user-facing messages in the code that displays them.
