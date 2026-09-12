# ComfyUI Reactor Connector

Generate videos, edit local clips, and move through scenes with Reactor models
in ComfyUI. Models run on Reactor; no model weights are downloaded. You need
Python 3.12 or later, ComfyUI 0.34.6 or later, frontend 1.49.6 or later within the 1.x series,
and a Reactor account with credits.

## Contents

- [Install](#install)
- [Make your first video](#make-your-first-video)
- [Choose a workflow](#choose-a-workflow)
- [Nodes](#nodes)
- [Find and refresh models](#find-and-refresh-models)
- [Fix a setup problem](#fix-a-setup-problem)

## Install

The connector includes its built browser assets. You do not need Bun, mise, or
development dependencies to use it.

1. Stop ComfyUI after active work finishes.
2. Place the connector at `ComfyUI/custom_nodes/reactor-inc`. Put `__init__.py`
   and `requirements.txt` directly inside that folder.
3. Install `requirements.txt` using the Python environment that runs ComfyUI.
   Choose the command below for your installation.
4. Start ComfyUI, then refresh its window.

### Comfy Desktop

1. On the home screen, open the installation's **⋮** menu and select **Manage**.
2. Open **About** and copy **Location** to find the installation folder. Inside it,
   find the `ComfyUI` folder containing `main.py` and place the connector at
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

See [update or remove](ADVANCED.md#update-or-remove) for later
package changes. Install only runtime requirements into ComfyUI's environment.

## Make your first video

1. Select the Comfy logo, then **Extensions → Reactor → Reactor settings**.
   Save your Reactor API key there. It stays on the server and out of workflows.
2. Open native **Browse Templates → reactor-inc** and select
   **helios-01-text-to-video**. You can also drag the
   [Helios text-to-video workflow](workflows/helios-01-text-to-video.json)
   onto the canvas.
3. Read **Start Here**, describe a scene, and choose the video length.
4. Select **Run**.
5. Play the result in **Preview and Save Video**. It also saves the file under
   ComfyUI's output folder.

Use ComfyUI's cancel control to stop a run. Closing a workflow tab does not cancel
it. Change **Run number** to request another run with unchanged inputs.

## Choose a workflow

The [workflow index](workflows/README.md) lists all 33 examples and includes
[sample images and video](workflows/README.md#sample-inputs). Open an
example from native **Browse Templates → reactor-inc**, or drag a JSON file onto
ComfyUI. Examples need only native ComfyUI nodes and this connector.

Use live workflows for scene prompts, Visko sound prompts, X2 dragging, or SANA
and X2 webcams. LingBot workflows with scene controls let you move with keys or buttons;
saved video cannot reopen a world. Fast H3 can continue a chosen number of clips
in one run. See [live controls](ADVANCED.md#live-controls).

After updating, open an example in a new tab. Existing graphs keep their saved
notes, prompts, and layout.

## Nodes

| Node                                                                                   | Input                                                     | Output                            |
| -------------------------------------------------------------------------------------- | --------------------------------------------------------- | --------------------------------- |
| [Fast H3: Generate Video](web/docs/ReactorIncFastGenerate.md)                          | Scene and sound prompt, optional first and last images    | Video with sound, separate audio  |
| [Fast H3: Continue a Scene](web/docs/ReactorIncFastContinue.md)                        | Clip count, prompts, and optional starting image          | Video with sound, separate audio  |
| [Helios: Generate Video](web/docs/ReactorIncHeliosGenerate.md)                         | Prompt                                                    | Video without sound               |
| [Helios: Animate an Image](web/docs/ReactorIncHeliosAnimate.md)                        | One image and a prompt                                    | Video without sound               |
| [Helios: Add a Prompt](web/docs/ReactorIncHeliosAddPrompt.md)                          | Chunk number, prompt, and optional earlier prompts        | A prompt sequence                 |
| [Helios: Generate Video from a Prompt Sequence](web/docs/ReactorIncHeliosSequence.md)  | Opening prompt, scheduled changes, and optional image     | Video without sound               |
| [LingBot: Explore an Image](web/docs/ReactorIncLingBotExplore.md)                      | Image, prompt, and camera directions                      | Video without sound               |
| [LingBot World 2: Explore an Image](web/docs/ReactorIncLingBotWorld2Explore.md)        | Image, prompt, and camera directions                      | Video without sound               |
| [LongLive: Generate Video](web/docs/ReactorIncLongLiveGenerate.md)                     | Opening shot prompt                                       | Video without sound               |
| [LongLive: Add a Shot](web/docs/ReactorIncLongLiveAddShot.md)                          | Shot prompt, transition, and chunk number                 | A storyboard                      |
| [LongLive: Generate Video from a Storyboard](web/docs/ReactorIncLongLiveStoryboard.md) | Opening prompt and scheduled shots                        | Video without sound               |
| [LTX: Make a Portrait Speak](web/docs/ReactorIncLtxSpeak.md)                           | Portrait, script, and speech pace                         | Video with speech, separate audio |
| [SANA: Edit Video](web/docs/ReactorIncSanaEditVideo.md)                                | Local video and edit prompt                               | Video without sound               |
| [SANA: Edit a Webcam](web/docs/ReactorIncSanaWebcam.md)                                | Camera and live edit prompt                               | Video without sound               |
| [Visko Stable: Generate Video](web/docs/ReactorIncViskoStableGenerate.md)              | Scene prompt, sound controls, and optional image          | Video with sound, separate audio  |
| [Visko Dynamic: Generate Video](web/docs/ReactorIncViskoDynamicGenerate.md)            | Scene prompt, sound controls, and optional image          | Video with sound, separate audio  |
| [X2: Edit Video](web/docs/ReactorIncX2EditVideo.md)                                    | Local video, edit prompt, and optional reference image    | Video without sound               |
| [X2: Edit a Webcam](web/docs/ReactorIncX2Webcam.md)                                    | Camera, optional subject image, live prompt, and dragging | Video without sound               |

Select a Reactor node and open its native **Info** for inputs, limits, and
examples. Nodes with detailed behavior show their bundled guide there.

In your own graph, connect **Video** to **Save Video**. Models with sound also
return a separate **Audio** output. Generation nodes also return [Recording details](ADVANCED.md#recording-details),
which describes the saved file and its model. Prompt and shot builders work
locally without contacting Reactor. HappyOyster is not supported.

## Find and refresh models

Models supported by the installed nodes appear before the first refresh.
Refresh the list to load public prices and guides.

Open **Extensions → Reactor → Reactor models** to search the list and select
**Refresh models** for the latest public prices and guides.

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
| Nodes appear but Reactor menus do not        | Refresh the window; confirm the package includes `web/extension.js` and `web/extension.css`.   |
| Node help is missing                         | Restore the complete package, including the native guides under `web/docs`.                    |
| Templates are missing                        | Confirm the package includes `workflows`; you can also open a JSON file there.                 |
| Duplicate nodes or menus appear              | Keep one connector folder; move backups outside `custom_nodes`.                                |
| Private settings are disabled                | Use a local, single-user connection. For remote access, set the server environment key.        |

For rejected inputs, timeouts, or session errors, read [recovery](ADVANCED.md#recovery)
and the node's native **Info** before another run. [Advanced settings](ADVANCED.md)
explains keys, limits, credit calculations, and live controls.

Project-authored code, guides, workflows, and sample assets use the
[MIT license](LICENSE.md). Third-party components keep their own license terms.
