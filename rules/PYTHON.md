# Python rules

Use Python 3.12 or later, strict annotations, pathlib, context-managed resources,
and focused modules. Group related records when separating them would obscure
their contract. A file normally stays under 300 lines and a function under 60;
document a specific framework or schema exception when needed.

Treat decoded JSON as untrusted objects and validate it at entry. Keep vendor
SDK typing uncertainty in the transport boundary. Do not spread `Any`, blanket
type ignores, dynamic imports, or changes to `sys.path` across runtime code.

Keep blocking media and filesystem work off the host event loop. Bound queues,
threads, timeouts, and resource lifetimes. Own every created task; cancel and
await it during teardown. Propagate cancellation after cleanup finishes or reaches its timeout.

Keep ComfyUI imports at the host/media boundary.

Comments explain reasons, invariants, or limits. Follow
[plain language](PLAIN_LANGUAGE.md) for comments, docstrings, and messages.

