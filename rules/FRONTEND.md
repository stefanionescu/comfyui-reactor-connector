# Frontend rules

Use TypeScript and documented ComfyUI extension APIs. Compile and bundle assets
for ordinary installation. Do not load runtime scripts from a CDN.

Use the Bun version pinned in mise.toml for dependencies and commands. Keep
bun.lock as the only frontend lockfile. Install dependencies through `mise run deps`.
Keep automatic dependency installation disabled in bunfig.toml so checks and
hooks cannot install missing packages.

Namespace routes, settings, events, and styles. Release listeners, timers, and
object URLs when their owner closes. Support keyboard use, focus return, themes,
tabs, and the supported renderer.

Use one compact help action per node and the native help surface where possible.
Each extra control must support a concrete task. Avoid decorative animation,
duplicate previews/help systems, unsolicited tours, and global canvas patches.

Render provider text safely as text. Keep secrets on the server. All labels,
tooltips, accessibility text, and messages follow [plain language](PLAIN_LANGUAGE.md).
