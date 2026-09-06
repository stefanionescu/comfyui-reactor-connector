# Reactor rules

Use verified canonical model names and command schemas. Keep pricing names,
model UUIDs, connect names, and node IDs distinct. Discovery does not establish
support. Read the model contract before adding a node or operation.

Own the complete session lifetime, including connection, upload, commands,
capture, and teardown. Apply a server-enforced lifetime limit and local
deadlines. A dropped connection or paused track does not prove billing stopped.

Never retry session creation or state-changing commands after an ambiguous
result. Preserve the error and report whether cleanup finished before its timeout. Select tracks by their
verified names, kind, and direction; never guess from a result URL.

Treat schema/catalog updates as data. Validate a separate candidate, preserve
running contracts, promote atomically, and retain rollback data. Refresh must
not install code, open a paid session, or execute provider text.

Use the authorized test allowance across all probes and runs. Keep pending
charges reserved. Stop paid work when cost or termination is uncertain.
Never buy credits, enable auto-top-up, add a payment method, or raise the test
allowance. Do not open or check the user's Reactor dashboard or account.
Track authorized manual runs using existing private cost records and local
session cleanup evidence. Do not change billing settings.
