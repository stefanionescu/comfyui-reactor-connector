# Naming rules

Use names that describe domain meaning: model, catalog, track, capture, session,
file, and command. Keep one term per concept. Avoid generic managers,
processors, and helpers that hide ownership.

Use snake_case for Python modules/functions/variables and PascalCase for classes.
Keep required upstream identifiers, model digits, ComfyUI callback names, and
public exports exact. Prefix public node IDs with `ReactorInc`; display names
start with `Reactor`. Do not derive stable IDs from mutable display labels.

Use unit suffixes when needed, such as `duration_seconds` and `timestamp_us`.
Boolean names state a condition. Apply [plain language](PLAIN_LANGUAGE.md) to
human-readable names without rewriting protocol identifiers.

Use sentence case for parameter and socket labels. Keep the English labels in
`locales/en/nodeDefs.json` aligned with the schema display names so connected
inputs use the same names as widgets. Output labels may explain a technical name:
for example, display `metadata` as "Recording details". Keep saved input names,
output positions, and provider option values unchanged.
