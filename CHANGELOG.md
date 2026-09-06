# Changelog

## Initial version

- Use Reactor's video and world models through native ComfyUI nodes. The
  [README](README.md#nodes) lists the available nodes.
- Generate from prompts and images, edit uploaded videos, and make a portrait
  speak. Save video and, where supported, a separate audio file.
- Prepare Helios prompt sequences and LongLive storyboards with connected
  builder nodes. Continue a Fast H3 scene across a chosen number of clips.
- Change prompts while watching, move through LingBot scenes, drag in X2,
  and use a webcam with SANA or X2.
- Search and refresh Reactor's model list. Optional automatic checks notify
  you of catalog changes; they do not install new node code.
- Store the API key privately on the ComfyUI server and set recording and
  session limits. Credentials stay out of workflow exports.
- Open model examples from ComfyUI's Templates browser. Each graph has setup,
  run, and save instructions, with native help for its Reactor nodes.
- Read each saved video's dimensions, duration, audio presence, and model
  identity from its separate recording-details output.

See the [README](README.md) for installation and links to the workflows.

## Workflow organization and credit rates

- Group examples by model and include native Templates copies in the installed package.
- Use `reactor-inc` as the installed package name and preserve saved node IDs.
- Add a credit-rate button to generation nodes and a session-time calculation.
- Use sentence case for workflow titles, controls, and notes.
