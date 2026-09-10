# ComfyUI Reactor Connector

Generate videos, edit local clips, and move through scenes with Reactor models
in ComfyUI. Models run on Reactor; no model weights are downloaded. You need
Python 3.12 or later, ComfyUI 0.34.6 or later, frontend 1.49.6 or later,
and a Reactor account with credits.

## Contents

- [Install](#install)
- [Make your first video](#make-your-first-video)
- [Choose a workflow](#choose-a-workflow)
- [Nodes](#nodes)
- [Find and refresh models](#find-and-refresh-models)
- [Fix a setup problem](#fix-a-setup-problem)

## Install

1. Stop ComfyUI after active work finishes.
2. Extract the connector package into `ComfyUI/custom_nodes/reactor-inc`.
   Place `__init__.py` and `requirements.txt` directly inside that folder.
3. Install `requirements.txt` using the Python environment that runs ComfyUI.
   Choose the command below for your installation.
4. Start ComfyUI, then refresh its window.

You do not need Bun, mise, or development dependencies to use the connector.

### Comfy Desktop

1. On the home screen, open the installation's **⋮** menu and select **Manage**.
2. Open **About** and copy **Location** to find the installation folder. Inside it,
   find the `ComfyUI` folder containing `main.py` and extract the connector into
   `custom_nodes/reactor-inc`.
3. Open **Terminal** in the same Manage panel. Desktop opens the ComfyUI folder
   and activates that installation's Python environment. Run:

```sh
pip install -r custom_nodes/reactor-inc/requirements.txt
```

Start the installation after the command finishes. See
[Comfy Desktop's Manage panel](https://docs.comfy.org/installation/desktop/usage/manage)
for the folder and terminal controls.

### Manual installation: macOS or Linux

Run from the ComfyUI directory. Replace `.venv` if your environment has another name:

```sh
.venv/bin/python -m pip install -r custom_nodes/reactor-inc/requirements.txt
```

For a uv environment without pip, use:

```sh
uv pip install --python .venv/bin/python -r custom_nodes/reactor-inc/requirements.txt
```

### Manual installation: Windows

Run in PowerShell from the ComfyUI directory. Replace `.venv` if your virtual
environment has another name or location:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\custom_nodes\reactor-inc\requirements.txt
```

### Windows portable

Run in PowerShell from the folder containing `ComfyUI` and `python_embeded`:

```powershell
.\python_embeded\python.exe -m pip install -r .\ComfyUI\custom_nodes\reactor-inc\requirements.txt
```

See [update, restore, or remove](ADVANCED.md#update-restore-or-remove) for later
package changes. Install only runtime requirements into ComfyUI's environment.

## Make your first video

1. Select the Comfy logo, then **Extensions → Reactor → Reactor settings**.
   Save your Reactor API key there. It stays on the server and out of workflows.
2. Open **Templates → reactor-inc** and select **helios-01-text-to-video**.
   You can also drag the [Helios text-to-video workflow](workflows/helios/helios-01-text-to-video.json)
   onto the canvas.
3. Read **Start Here**, describe a scene, and choose the video length.
4. Select **Run**.
5. Play the result in **Preview and Save Video**. It also saves the file under
   ComfyUI's output folder.

Use ComfyUI's cancel control to stop a run. Closing a workflow tab does not cancel
it. Change **Run number** to request another run with unchanged inputs.

## Choose a workflow

The [workflow index](workflows/README.md) lists all 33 examples and includes
[sample images and video](workflows/README.md#sample-inputs). Choose a JSON file
and drag it onto ComfyUI, or use Templates after installing a built package.
Examples need only native ComfyUI nodes and this connector.

Use live workflows for scene prompts, Visko sound prompts, X2 dragging, or SANA
and X2 webcams. LingBot workflows with scene controls let you move with keys or buttons;
saved video cannot reopen a world. Fast H3 can continue a chosen number of clips
in one run. See [live controls](ADVANCED.md#live-controls).

After updating, open an example in a new tab. Existing graphs keep their saved
notes, prompts, and layout. A source checkout can open grouped JSON files directly;
[packaging](ADVANCED.md#development-commands) also adds them to native Templates.

## Nodes

| Node                                                                                   | Input                                                     | Output                                                            |
| -------------------------------------------------------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------- |
| [SANA: Edit a Webcam](web/docs/ReactorIncSanaWebcam.md)                                | Camera and live edit prompt                               | Video and recording details                                       |
| [X2: Edit a Webcam](web/docs/ReactorIncX2Webcam.md)                                    | Camera, optional subject image, live prompt, and dragging | Video and recording details                                       |
| [Fast H3: Continue a Scene](web/docs/ReactorIncFastContinue.md)                        | Clip count, prompts, and optional starting image          | Video with sound, separate audio, and recording details           |
| [Fast H3: Generate Video](web/docs/ReactorIncFastGenerate.md)                          | Scene and sound prompt, optional first and last images    | Video with sound, a separate audio output, and recording details  |
| [LTX: Make a Portrait Speak](web/docs/ReactorIncLtxSpeak.md)                           | Portrait, script, and speech pace                         | Video with speech, a separate audio output, and recording details |
| [Helios: Generate Video](web/docs/ReactorIncHeliosGenerate.md)                         | Prompt                                                    | Video and recording details                                       |
| [Helios: Animate an Image](web/docs/ReactorIncHeliosAnimate.md)                        | One image and a prompt                                    | Video and recording details                                       |
| [Helios: Add a Prompt](web/docs/ReactorIncHeliosAddPrompt.md)                          | Chunk number, prompt, and optional earlier prompts        | A prompt sequence                                                 |
| [Helios: Generate Video from a Prompt Sequence](web/docs/ReactorIncHeliosSequence.md)  | Opening prompt, scheduled changes, and optional image     | Video and recording details                                       |
| [LingBot: Explore an Image](web/docs/ReactorIncLingBotExplore.md)                      | Image, prompt, and camera directions                      | Video and recording details                                       |
| [LingBot World 2: Explore an Image](web/docs/ReactorIncLingBotWorld2Explore.md)        | Image, prompt, and camera directions                      | Video and recording details                                       |
| [LongLive: Generate Video](web/docs/ReactorIncLongLiveGenerate.md)                     | Opening shot prompt                                       | Video and recording details                                       |
| [LongLive: Generate Video from a Storyboard](web/docs/ReactorIncLongLiveStoryboard.md) | Opening prompt and scheduled shots                        | Video and recording details                                       |
| [LongLive: Add a Shot](web/docs/ReactorIncLongLiveAddShot.md)                          | Shot prompt, transition, and chunk number                 | A storyboard; does not contact Reactor                            |
| [SANA: Edit Video](web/docs/ReactorIncSanaEditVideo.md)                                | Local video and edit prompt                               | Video and recording details                                       |
| [X2: Edit Video](web/docs/ReactorIncX2EditVideo.md)                                    | Local video, edit prompt, and optional reference image    | Video and recording details                                       |
| [Visko Stable: Generate Video](web/docs/ReactorIncViskoStableGenerate.md)              | Scene prompt, sound controls, and optional image          | Video with sound, a separate audio output, and recording details  |
| [Visko Dynamic: Generate Video](web/docs/ReactorIncViskoDynamicGenerate.md)            | Scene prompt, sound controls, and optional image          | Video with sound, a separate audio output, and recording details  |

Select a Reactor node and choose **Help** for inputs, limits, and examples.
The same guide appears in ComfyUI's native **Info** panel. If the selection
toolbar is hidden, use Info or enable **Selection toolbox** in ComfyUI settings.

In your own graph, connect **Video** to **Save Video**. Models with sound also
return a separate **Audio** output. [Recording details](ADVANCED.md#recording-details)
describes the saved file and its model. Prompt and shot builders work locally. HappyOyster is not supported.

## Find and refresh models

Installed models appear before the first refresh. Refresh the list to load public
prices and metadata. Saved metadata stays in Reactor's private application-data folder on the ComfyUI server.

Open **Extensions → Reactor → Reactor models** to search the list and select
**Refresh models** for the latest public prices and guides. HappyOyster is excluded.

**Refreshing the list does not install new nodes.** A model can run only when the
connector includes code and nodes that support it. Entries show whether nodes
are available. Your Reactor account determines access to each provider model.

Reactor settings can enable automatic checks. They report changes; select
**Refresh models** to save the updated list. See [model updates](ADVANCED.md#model-updates)
for how checks work and how to restore a previous list.

## Fix a setup problem

| Problem                                      | What to check                                                                                  |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Reactor nodes are missing                    | Confirm the running instance has `custom_nodes/reactor-inc/__init__.py`; read its startup log. |
| `reactor_sdk` cannot be imported             | Install runtime requirements with that instance's Python.                                      |
| No matching SDK distribution                 | Use Python 3.12 or later and a platform supported by the required SDK version.                 |
| `comfy_api` or a native node type is missing | Update ComfyUI through its normal update procedure, then restart.                              |
| Nodes appear but Reactor menus do not        | Refresh the window; confirm the package includes `web/dist/main.js` and `main.css`.            |
| Help is missing                              | Restore the complete package, including `web/dist/docs` and `web/dist/guides`.                 |
| Templates are missing                        | Open a grouped workflow JSON directly, or install the built package.                           |
| Duplicate nodes or menus appear              | Keep one connector folder; move backups outside `custom_nodes`.                                |
| Private settings are disabled                | Use a local, single-user connection. For remote access, set the server environment key.        |

For rejected inputs, timeouts, or session errors, read [recovery](ADVANCED.md#recovery)
and the node's Help before another run. [Advanced settings](ADVANCED.md)
explains keys, limits, credit calculations, and live controls.

Project-authored code, guides, workflows, and sample assets use the
[MIT license](LICENSE.md). Third-party components keep their own license terms.
