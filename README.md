# Reactor for ComfyUI

Use Reactor's hosted video and world models from ComfyUI workflows.

## Install

Use a current ComfyUI installation with Python 3.12 or later. Download the built package
and place its folder at `ComfyUI/custom_nodes/reactor-inc`.
Install `requirements.txt` with the Python environment that runs ComfyUI, then
restart ComfyUI. Do not install the dependencies into a separate system Python.

For a ComfyUI virtual environment, run its Python from the ComfyUI folder:

```sh
.venv/bin/python -m pip install \
  -r custom_nodes/reactor-inc/requirements.txt
```

On Windows, use `.venv\Scripts\python.exe` for a virtual environment or your
portable installation's `python_embeded\python.exe`.

The [installation guide](docs/installation.md) gives complete commands for each
layout, including uv environments, updates, restoring a previous package, and removal.
Use [troubleshooting](docs/troubleshooting.md) for missing nodes or failed runs.

Select the Comfy logo to open the main menu. Choose
**Extensions → Reactor → Reactor settings** and save your Reactor API key.
The key stays on your ComfyUI server and is not saved in workflows. Reactor uses
its own account and credits. Download a workflow below to start.

## Find the workflows

Open the [workflow folder and file list](workflows/README.md). The editable graphs
are the `.json` files grouped by model under `workflows/`.
`docs/workflows/` contains their guides; `web/docs/` contains node help.

To use a graph, drag its JSON file onto ComfyUI. After installing the built package,
you can also open **Templates → reactor-inc** and choose the example.
Opening a workflow does not start generation.

After an update, open the example again in a new tab. Existing tabs and saved
graphs keep their old notes and layout; updating the package does not replace them.

If you downloaded a source checkout, drag an example from its model folder onto
the canvas, or [build and install the package](docs/development.md#build-and-install-a-package)
to populate native Templates.

Start with [Helios text to video](workflows/helios/helios-01-text-to-video.json),
[Fast H3 with two images](workflows/fast-h3/fast-h3-03-first-and-last-frames.json), or
[LingBot World 2 live camera](workflows/lingbot-world-2/lingbot-world-2-02-live-camera.json).
Read the graph's **Start here** note before selecting **Run**.
Use the [sample inputs](workflows/assets/README.md) if you need a starting image.

## Available operations

The connector provides the nodes listed below, native ComfyUI video and audio
outputs, local help, and 33 editable workflow examples. Generation runs on Reactor
and uses your Reactor account and credits.

Use the live workflows for scene prompts, Visko sound prompts, X2 dragging, and
SANA or X2 webcam input.
Fast H3 can continue a scene across a chosen number of clips in one session.
See each node's guide for its supported inputs and limits.
HappyOyster is not supported and is excluded from the model list.

Never paste an API key into a workflow, issue, screenshot, or source file.
Use the private server environment or the [Reactor settings dialog](docs/settings.md).

Read the [workflow guides](docs/workflows/README.md) for input preparation and model controls.

## Nodes

| Node | Input | Output |
| --- | --- | --- |
| [SANA webcam](docs/nodes/ReactorIncSanaWebcam.md) | Camera and live edit prompt | Video and recording details |
| [X2 webcam](docs/nodes/ReactorIncX2Webcam.md) | Camera, optional subject image, live prompt, and dragging | Video and recording details |
| [Fast H3 continued scene](docs/nodes/ReactorIncFastContinue.md) | Clip count, prompts, and optional starting image | Video with sound, separate audio, and recording details |
| [Fast H3: Generate video](docs/nodes/ReactorIncFastGenerate.md) | Scene and sound prompt, optional first and last images | Video with sound, a separate audio output, and recording details |
| [LTX: Make a portrait speak](docs/nodes/ReactorIncLtxSpeak.md) | Portrait, script, and speech pace | Video with speech, a separate audio output, and recording details |
| [Helios: Generate video](docs/nodes/ReactorIncHeliosGenerate.md) | Prompt | Video and recording details |
| [Helios: Animate an image](docs/nodes/ReactorIncHeliosAnimate.md) | One image and a prompt | Video and recording details |
| [Helios: Add a prompt](docs/nodes/ReactorIncHeliosAddPrompt.md) | Chunk number, prompt, and optional earlier prompts | A prompt sequence; uses no credits |
| [Helios: Generate a prompt sequence](docs/nodes/ReactorIncHeliosSequence.md) | Opening prompt, scheduled changes, and optional image | Video and recording details |
| [LingBot: Explore an image](docs/nodes/ReactorIncLingBotExplore.md) | Image, prompt, and camera directions | Video and recording details |
| [LingBot World 2: Explore an image](docs/nodes/ReactorIncLingBotWorld2Explore.md) | Image, prompt, and camera directions | Video and recording details |
| [LongLive: Generate video](docs/nodes/ReactorIncLongLiveGenerate.md) | Opening shot prompt | Video and recording details |
| [LongLive: Create a storyboard](docs/nodes/ReactorIncLongLiveStoryboard.md) | Opening prompt and scheduled shots | Video and recording details |
| [LongLive: Add a shot](docs/nodes/ReactorIncLongLiveAddShot.md) | Shot prompt, transition, and chunk number | A storyboard; does not contact Reactor |
| [SANA: Edit video](docs/nodes/ReactorIncSanaEditVideo.md) | Local video and edit prompt | Video and recording details |
| [X2: Edit video](docs/nodes/ReactorIncX2EditVideo.md) | Local video, edit prompt, and optional reference image | Video and recording details |
| [Visko Stable: Generate video](docs/nodes/ReactorIncViskoStableGenerate.md) | Scene prompt, sound controls, and optional image | Video with sound, a separate audio output, and recording details |
| [Visko Dynamic: Generate video](docs/nodes/ReactorIncViskoDynamicGenerate.md) | Scene prompt, sound controls, and optional image | Video with sound, a separate audio output, and recording details |

Connect a generation node's video output to ComfyUI's **Save Video** node. A new
generation uses Reactor credits; preparing a storyboard, opening settings, and
reading node help do not. Select a Reactor node, then choose **Help** to open its local
guide, including inputs, limits, and recovery steps. The same guide is available
through ComfyUI's native **Info** panel. If the selection toolbar is hidden,
use **Info** or enable **Selection toolbox** in ComfyUI settings.

The **Recording details** output identifies the model and records the saved video's
dimensions, duration, file size, and audio presence. See
[recording details](docs/recording-details.md) for its fields and cache behavior.

The LingBot nodes can hold fixed directions or open the live camera
panel while recording a video. Use a `live-camera` template to move through a
scene and change its prompt. Use Save Video to play the finished recording.
These nodes cannot reopen a saved world.

Open **ComfyUI menu → Extensions → Reactor → Reactor models**
to search and refresh the model list. The list includes every
observed pricing entry and unmatched model guide, except HappyOyster. Refresh sends no API key and
does not start generation. See [model refresh](docs/models.md).

Automatic checks can notify you when the model list changes. Choose how often
to check in Reactor settings. Select **Refresh models** to save the updated list.

A model needs a compatible connector node to run. Refreshing the list does not
install new nodes.

For development, install the pinned tools with mise, run `mise run deps`, then
`mise run check`. Build native help with `mise run docs:build` and example graphs
with `mise run workflows:build`. Both generated outputs are checked for drift. The help
check also rejects missing guides, and every implemented node needs an example.
No normal check opens a paid session. Local hooks replace Git-hosted workflows.

For contribution requirements, see [the development guide](docs/development.md).
All authored text must follow the [plain-language rule](rules/PLAIN_LANGUAGE.md).
See the [changelog](CHANGELOG.md) for the feature summary.

Project-authored code, guides, workflows, and sample assets use
[MIT](LICENSE.md). Third-party components keep their separate license terms.
