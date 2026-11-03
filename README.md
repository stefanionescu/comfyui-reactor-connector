# ![comfyui-reactor-connector: a ComfyUI extension that runs Reactor's real-time video models](docs/images/banner.svg)

[![ComfyUI 0.34.6 or later](docs/images/badges/comfyui.svg)](#requirements)
[![Frontend 1.49.6 or later](docs/images/badges/frontend.svg)](#requirements)
[![Python 3.12 or later](docs/images/badges/python.svg)](#requirements)
[![MIT license](docs/images/badges/license.svg)](LICENSE.md)

Generate videos, edit clips, and explore interactive scenes with Reactor in ComfyUI.
Models run on Reactor; ComfyUI needs no local model weights.

## Requirements

- Python 3.12 or later.
- ComfyUI 0.34.6 or later, with frontend 1.49.6 or a later release below 2.0.0.
- A Reactor account with credits.

Generation uses your provider account and can incur charges.

## Install

Stop ComfyUI. From its `custom_nodes` folder, clone the extension:

```sh
git clone https://github.com/stefanionescu/comfyui-reactor-connector.git reactor-inc
```

In Comfy Desktop, use **Manage > About > Location** to find the installation's
`ComfyUI` folder. Its **Terminal** opens that instance's Python environment.

Install runtime dependencies with the Python that runs ComfyUI.
Choose the command for your installation:

**Comfy Desktop**, in its Terminal:

```sh title="Comfy Desktop terminal, in the ComfyUI folder"
pip install -r custom_nodes/reactor-inc/requirements.txt
```

**macOS or Linux**, from the ComfyUI folder:

```sh title="In the ComfyUI folder"
.venv/bin/python -m pip install -r custom_nodes/reactor-inc/requirements.txt
```

**Windows**, in PowerShell from the ComfyUI folder:

```powershell title="In the ComfyUI folder"
.\.venv\Scripts\python.exe -m pip install -r .\custom_nodes\reactor-inc\requirements.txt
```

**Windows portable**, in PowerShell from the folder containing ComfyUI:

```powershell title="Windows portable parent folder"
.\python_embeded\python.exe -m pip install -r .\ComfyUI\custom_nodes\reactor-inc\requirements.txt
```

Replace `.venv` if your environment has another name. Restart ComfyUI and
reload its window.

## First run

1. Open **Extensions > Reactor > Reactor settings** from the ComfyUI menu
   and save your Reactor API key.
2. Open **Browse Templates > reactor-inc > helios-01-text-to-video**.
3. Read **Start Here**, describe a scene, and choose the video length.
4. Select **Run**. **Save Video** plays and saves the result in ComfyUI's
   output folder. Reactor charges for session time, including setup.

Use ComfyUI's cancel control to stop a run. Closing a workflow tab does not
cancel a run without live controls. See [recovery](ADVANCED.md#recovery).

Change **run number** to run again with unchanged inputs. For remote or multi-user
setups, see the [access instructions](ADVANCED.md#keys-and-access).

## Example workflows

Open these from **Browse Templates > reactor-inc**, or load their JSON files.
Read **Start Here** before running. After an update, open examples in a new tab.

| Workflow JSON                                                                                                 | Input                                   |
| ------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| [Fast H3: Generate a Clip with Audio](example_workflows/fast-h3-01-text-to-video.json)                        | Scene and sound prompt                  |
| [Fast H3: Animate an Image](example_workflows/fast-h3-02-image-to-video.json)                                 | Image and prompt                        |
| [Fast H3: Connect Two Images with Motion](example_workflows/fast-h3-03-first-and-last-frames.json)            | First image, final image, and prompt    |
| [Fast H3: Continue a Scene](example_workflows/fast-h3-05-continue-scene.json)                                 | Prompts for continued clips             |
| [Helios: Generate Video](example_workflows/helios-01-text-to-video.json)                                      | Scene prompt                            |
| [Helios: Animate an Image](example_workflows/helios-02-image-to-video.json)                                   | Image and prompt                        |
| [Helios: Follow a Prompt Sequence](example_workflows/helios-03-prompt-sequence.json)                          | Scheduled prompts                       |
| [Helios: Change the Prompt While Recording](example_workflows/helios-05-live-prompt.json)                     | Live prompt                             |
| [LingBot: Explore an Image](example_workflows/lingbot-01-explore-image.json)                                  | Image and prompt                        |
| [LingBot: Explore an Image with Live Controls](example_workflows/lingbot-02-live-camera.json)                 | Image and prompt; live keys or buttons  |
| [LingBot World 2: Explore an Image](example_workflows/lingbot-world-2-01-explore-image.json)                  | Image and prompt                        |
| [LingBot World 2: Explore an Image with Live Controls](example_workflows/lingbot-world-2-02-live-camera.json) | Image and prompt; live keys or buttons  |
| [LongLive: Generate Video](example_workflows/longlive-v2-01-text-to-video.json)                               | Scene prompt                            |
| [LongLive: Generate Video with Shot Transitions](example_workflows/longlive-v2-02-storyboard.json)            | Opening prompt and two scheduled shots  |
| [LongLive: Change the Prompt While Recording](example_workflows/longlive-v2-03-live-prompt.json)              | Live prompt                             |
| [LTX: Make a Portrait Speak](example_workflows/ltx2-01-speaking-portrait.json)                                | Portrait and speech script              |
| [SANA: Edit Video](example_workflows/sana-streaming-01-edit-video.json)                                       | Video and edit prompt                   |
| [SANA: Change the Prompt While Recording](example_workflows/sana-streaming-02-live-prompt.json)               | Source video and live controls          |
| [SANA: Edit Webcam Video](example_workflows/sana-streaming-03-webcam.json)                                    | Webcam and live edit prompt             |
| [Visko: Generate Video with Audio](example_workflows/visko-01-text-to-video.json)                             | Scene and sound prompt                  |
| [Visko: Animate an Image with Audio](example_workflows/visko-02-image-to-video.json)                          | Image and prompt                        |
| [Visko: Change the Prompt While Recording](example_workflows/visko-03-live-prompt.json)                       | Live prompt                             |
| [X2: Edit Video](example_workflows/x2-01-edit-video.json)                                                     | Video and edit prompt                   |
| [X2: Edit with a Reference Image](example_workflows/x2-02-reference-edit.json)                                | Video, edit prompt, and reference image |
| [X2: Edit Webcam Video with Pointer Controls](example_workflows/x2-03-webcam.json)                            | Webcam and live edit prompt             |
| [X2: Drag and Edit a Video](example_workflows/x2-04-live-prompt.json)                                         | Source video and live controls          |

For interactive prompts, webcams, pointer control, and LingBot movement, see
[live controls](ADVANCED.md#live-controls).

Sample inputs: [forest path](example_workflows/assets/forest-path.png),
[forest illustration](example_workflows/assets/forest-illustration.png),
[fictional portrait](example_workflows/assets/fictional-portrait.png), and a
[five-second silent clip](example_workflows/assets/forest-motion.mp4).
Download a sample and select it in the matching input node.

Reactor output frames: [Fast H3 stream](example_workflows/fast-h3-01-text-to-video.jpg)
and [Helios forest](example_workflows/helios-02-image-to-video.jpg).
The input illustrations and zoom clip are synthetic samples; the output frames
come from Reactor generations.

## Nodes

Find the nodes under **Reactor**. Each linked help page explains its inputs,
outputs, and usage.

| Node                                                                            | Input                                                     | Output                            |
| ------------------------------------------------------------------------------- | --------------------------------------------------------- | --------------------------------- |
| [Fast H3: Generate Video](web/docs/ReactorIncFastGenerate.md)                   | Scene and sound prompt, optional first and last images    | Video with sound, separate audio  |
| [Fast H3: Continue a Scene](web/docs/ReactorIncFastContinue.md)                 | Clip count, prompts, and optional starting image          | Video with sound, separate audio  |
| [Helios: Generate Video](web/docs/ReactorIncHeliosGenerate.md)                  | Prompt, optional image, and optional prompt sequence      | Video without sound               |
| [Helios: Add a Prompt](web/docs/ReactorIncHeliosAddPrompt.md)                   | Chunk number, prompt, and optional earlier prompts        | A prompt sequence                 |
| [LingBot: Explore an Image](web/docs/ReactorIncLingBotExplore.md)               | Image, prompt, and camera directions                      | Video without sound               |
| [LingBot World 2: Explore an Image](web/docs/ReactorIncLingBotWorld2Explore.md) | Image, prompt, and camera directions                      | Video without sound               |
| [LongLive: Generate Video](web/docs/ReactorIncLongLiveGenerate.md)              | Opening shot prompt and optional scheduled shots          | Video without sound               |
| [LongLive: Add a Shot](web/docs/ReactorIncLongLiveAddShot.md)                   | Shot prompt, transition, and chunk number                 | A storyboard                      |
| [LTX: Make a Portrait Speak](web/docs/ReactorIncLtxSpeak.md)                    | Portrait, script, and speech pace                         | Video with speech, separate audio |
| [SANA: Edit Video](web/docs/ReactorIncSanaEditVideo.md)                         | Local video and edit prompt                               | Video without sound               |
| [SANA: Edit Webcam Video](web/docs/ReactorIncSanaWebcam.md)                     | Camera and live edit prompt                               | Video without sound               |
| [Visko: Generate Video](web/docs/ReactorIncViskoGenerate.md)                    | Model, scene prompt, sound controls, and optional image   | Video with sound, separate audio  |
| [X2: Edit Video](web/docs/ReactorIncX2EditVideo.md)                             | Local video, edit prompt, and optional reference image    | Video without sound               |
| [X2: Edit Webcam Video](web/docs/ReactorIncX2Webcam.md)                         | Camera, optional subject image, live prompt, and dragging | Video without sound               |

Connect the `video` output of a generation node to **Save Video**. Models with
sound also return separate `audio`. Prompt and shot builders run locally.
Open the native **Info** of a node for its inputs and limits.

Fast H3 and LTX can use additional paid recording time that is absent from the
saved clip. Read [recording overhead](ADVANCED.md#recording-overhead) before using them.

## Troubleshooting

| Problem                          | What to check                                                                            |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| Nodes or templates are missing   | Install the complete connector and its requirements with ComfyUI's Python, then restart. |
| `reactor_sdk` cannot be imported | Check the installation's Python version and reinstall runtime requirements.              |
| The key is rejected              | Check the saved key and any `REACTOR_API_KEY` environment value.                         |
| A session fails or times out     | Read [recovery](ADVANCED.md#recovery) before starting another paid session.              |
| Settings cannot be changed       | Use a direct local connection, or configure credentials on the ComfyUI server.           |

See the [advanced guide](ADVANCED.md#recovery) for request errors and recovery.

## License

[MIT](LICENSE.md).
