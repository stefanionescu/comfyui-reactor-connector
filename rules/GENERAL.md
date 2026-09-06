# General rules

Keep one owner for each behavior. Read its callers before changing it.
Use small records and explicit data flow. Add an abstraction only when it removes
complexity demonstrated by actual callers.

Validate user input, files, provider responses, and host boundaries. Trust
validated internal records. Handle known errors without inventing silent
fallbacks, guessed defaults, or retries for side effects.

Keep imports free of network calls, installation, background work, and mutable
runtime initialization. Preserve saved workflow contracts through explicit,
tested migrations. Never overwrite unrelated user work.

Use formatting, linting, type checks, and asset builds. Do not create or run
tests. Fix reported source errors before continuing.

Never put credentials in source, commands, workflows, logs, or public evidence.
Use [plain language](PLAIN_LANGUAGE.md) for all project text.

