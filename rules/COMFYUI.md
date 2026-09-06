# ComfyUI rules

Use documented V3 node and frontend APIs. Keep root registration small and free
of network activity. Use native image, audio, and video types. Declare batching,
optional values, output lifetime, and caching behavior explicitly.

Every public node needs stable sockets/widgets, a task-specific guide, one
accessible help action, and an executable example. Keep credential values out
of widgets and workflow serialization. Ordinary execution must work without
opening a custom panel.

Build the actual distributable for installation in ComfyUI. Do not create or run
tests. Keep development evidence private and describe only available behavior in
public guides.

Preserve host dependencies, unrelated packs, unsaved graphs, and user media.
Resolve dependencies with the host's own interpreter.


Use the installed Comfy Desktop app for all manual ComfyUI interaction. Use a
separate Chrome session for other web work. Leave the user's browser tabs alone.
