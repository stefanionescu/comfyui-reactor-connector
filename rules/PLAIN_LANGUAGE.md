# Strict plain-language requirement

All project-authored, adapted, and generated human-readable text must strictly
conform to ISO 24495-1:2023 and other published parts where their scope applies.
This includes comments, docstrings, plans, rules, tests, logs, errors, CLI output,
UI text, guides, workflow notes, release notes, and translations.

Identify the reader and task. Include necessary information, arrange it so the
reader can find it, use clear and consistent terms, and verify that the reader
can act on it. Keep technical detail that affects correct use. Remove filler,
hype, repetition, and comments that repeat obvious code.

Use sentence case for headings, node titles, notes, buttons, and labels: capitalize
the first word and proper names, not every word. In a model title such as
"Reactor Helios: Generate video", the task after the colon starts with a capital.
Keep model names, acronyms, protocol identifiers, and quoted ComfyUI controls in
their exact form. Workflow instructions must use the node titles visible in that
workflow. Do not change socket names or saved identifiers to change their casing.

Describe the user's action and result in familiar words. For example, write
"Move the camera while recording a video" and "Choose how long to record."
State an actual limit where it affects use. Explain an essential technical term
when it first appears; do not assume the reader knows model internals.

Name features by what the reader can do: "Move through a scene from your image"
or "Record a video." Explain a time limit as "Recording stops after the duration
you choose." Do not invent abstract names for ordinary actions.

Apply this to every label, tooltip, workflow note, guide, comment, and docstring.
Say what the user can do, what they need, and what happens next. Use the same
wording in source templates and generated files. Read the result in ComfyUI;
do not rely on a word search alone to decide whether it is clear.

Use direct verbs such as upload, choose, move, record, and save. Describe limits
with numbers and units. Replace an abstract feature name with the action it
allows. Do not make readers learn implementation terms to use a node.

Use a review checklist based on an authorized copy of the applicable standard.
Record the review with existing change/release evidence. Review rendered and
generated text as well as source. Resolve known failures before acceptance.
Spelling, terminology, and readability checks support this review; a passing
linter must never be described as proof of ISO conformance or certification.

Preserve exact protocol identifiers, syntax, required third-party notices, and
verbatim evidence. User input and provider output remain data. All surrounding
authored explanations must conform.

See the [ISO catalog](https://www.iso.org/standard/78907.html) for the governing
edition. Keep detailed text-review evidence privately.
