# Host type declarations

These declarations cover only the ComfyUI symbols used by this connector. They
were checked against the installed v0.34.3 source. They are development inputs,
not runtime replacements, and must not be included in the installed package.

ComfyUI node execution signatures depend on each node's schema. The declaration
therefore leaves `ComfyNode` as the nominal base and checks the connector's own
typed methods. Actual node schema registration and execution are validated in
the real host as described in the development guide.

Expand declarations only when a real host operation needs them. Recheck them
against supported host releases and keep installation tests authoritative.

