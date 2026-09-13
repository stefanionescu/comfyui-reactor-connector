# Reactor Workflows

This folder contains 33 editable ComfyUI workflows. Each graph has connected nodes and setup instructions.

## Open a workflow

1. Open an example from native **Browse Templates → reactor-inc**, or open a JSON file listed below.
2. Read **Start Here**. Media inputs start empty; select your own image or video or use the samples below.
3. Set your key in **Extensions → Reactor → Reactor settings**, then select **Run**.

## Available files

### Fast H3

| Workflow JSON | Input | Guide |
| --- | --- | --- |
| [Fast H3: Generate a Clip with Audio](fast-h3-01-text-to-video.json) | Scene and sound prompt | [Node guide](../web/docs/ReactorIncFastGenerate.md) |
| [Fast H3: Animate an Image](fast-h3-02-image-to-video.json) | Image and prompt | [Node guide](../web/docs/ReactorIncFastGenerate.md) |
| [Fast H3: Connect Two Images with Motion](fast-h3-03-first-and-last-frames.json) | First image, final image, and prompt | [Node guide](../web/docs/ReactorIncFastGenerate.md) |
| [Fast H3: Finish on a Chosen Image](fast-h3-04-ending-frame.json) | Final image and prompt | [Node guide](../web/docs/ReactorIncFastGenerate.md) |
| [Fast H3: Continue a Scene](fast-h3-05-continue-scene.json) | Prompts for continued clips | [Node guide](../web/docs/ReactorIncFastContinue.md) |
| [Fast H3: Continue from an Image](fast-h3-06-continue-image.json) | Starting image and continued clips | [Node guide](../web/docs/ReactorIncFastContinue.md) |

### Helios

| Workflow JSON | Input | Guide |
| --- | --- | --- |
| [Helios: Generate Video](helios-01-text-to-video.json) | Scene prompt | [Node guide](../web/docs/ReactorIncHeliosGenerate.md) |
| [Helios: Animate an Image](helios-02-image-to-video.json) | Image and prompt | [Node guide](../web/docs/ReactorIncHeliosAnimate.md) |
| [Helios: Follow a Prompt Sequence](helios-03-prompt-sequence.json) | Scheduled prompts | [Node guide](../web/docs/ReactorIncHeliosSequence.md) |
| [Helios: Animate an Image with a Prompt Sequence](helios-04-image-sequence.json) | Starting image and scheduled prompts | [Node guide](../web/docs/ReactorIncHeliosSequence.md) |
| [Helios: Change the Prompt While Recording](helios-05-live-prompt.json) | Live prompt | [Node guide](../web/docs/ReactorIncHeliosGenerate.md) |
| [Helios: Animate an Image with Live Prompts](helios-06-live-image.json) | Image and live prompt | [Node guide](../web/docs/ReactorIncHeliosAnimate.md) |

### LingBot

| Workflow JSON | Input | Guide |
| --- | --- | --- |
| [LingBot: Explore an Image](lingbot-01-explore-image.json) | Image and prompt | [Node guide](../web/docs/ReactorIncLingBotExplore.md) |
| [LingBot: Explore an Image with Live Controls](lingbot-02-live-camera.json) | Image and prompt; live keys or buttons | [Node guide](../web/docs/ReactorIncLingBotExplore.md) |

### LingBot World 2

| Workflow JSON | Input | Guide |
| --- | --- | --- |
| [LingBot World 2: Explore an Image](lingbot-world-2-01-explore-image.json) | Image and prompt | [Node guide](../web/docs/ReactorIncLingBotWorld2Explore.md) |
| [LingBot World 2: Explore an Image with Live Controls](lingbot-world-2-02-live-camera.json) | Image and prompt; live keys or buttons | [Node guide](../web/docs/ReactorIncLingBotWorld2Explore.md) |

### LongLive

| Workflow JSON | Input | Guide |
| --- | --- | --- |
| [LongLive: Generate Video](longlive-v2-01-text-to-video.json) | Scene prompt | [Node guide](../web/docs/ReactorIncLongLiveGenerate.md) |
| [LongLive: Generate Video with Shot Transitions](longlive-v2-02-storyboard.json) | Opening prompt and two scheduled shots | [Node guide](../web/docs/ReactorIncLongLiveStoryboard.md) |
| [LongLive: Change the Prompt While Recording](longlive-v2-03-live-prompt.json) | Live prompt | [Node guide](../web/docs/ReactorIncLongLiveGenerate.md) |

### LTX

| Workflow JSON | Input | Guide |
| --- | --- | --- |
| [LTX: Make a Portrait Speak](ltx2-01-speaking-portrait.json) | Portrait and speech script | [Node guide](../web/docs/ReactorIncLtxSpeak.md) |

### SANA

| Workflow JSON | Input | Guide |
| --- | --- | --- |
| [SANA: Edit Video](sana-streaming-01-edit-video.json) | Video and edit prompt | [Node guide](../web/docs/ReactorIncSanaEditVideo.md) |
| [SANA: Change the Prompt While Recording](sana-streaming-02-live-prompt.json) | Source video and live controls | [Node guide](../web/docs/ReactorIncSanaEditVideo.md) |
| [SANA: Edit Webcam Video](sana-streaming-03-webcam.json) | Webcam and live edit prompt | [Node guide](../web/docs/ReactorIncSanaWebcam.md) |

### Visko Dynamic

| Workflow JSON | Input | Guide |
| --- | --- | --- |
| [Visko Dynamic: Generate Video with Audio](visko-dynamic-01-text-to-video.json) | Scene and sound prompt | [Node guide](../web/docs/ReactorIncViskoDynamicGenerate.md) |
| [Visko Dynamic: Animate an Image with Audio](visko-dynamic-02-image-to-video.json) | Image and prompt | [Node guide](../web/docs/ReactorIncViskoDynamicGenerate.md) |
| [Visko Dynamic: Change the Prompt While Recording](visko-dynamic-03-live-prompt.json) | Live prompt | [Node guide](../web/docs/ReactorIncViskoDynamicGenerate.md) |

### Visko Stable

| Workflow JSON | Input | Guide |
| --- | --- | --- |
| [Visko Stable: Generate Video with Audio](visko-stable-01-text-to-video.json) | Scene and sound prompt | [Node guide](../web/docs/ReactorIncViskoStableGenerate.md) |
| [Visko Stable: Animate an Image with Audio](visko-stable-02-image-to-video.json) | Image and prompt | [Node guide](../web/docs/ReactorIncViskoStableGenerate.md) |
| [Visko Stable: Change the Prompt While Recording](visko-stable-03-live-prompt.json) | Live prompt | [Node guide](../web/docs/ReactorIncViskoStableGenerate.md) |

### X2

| Workflow JSON | Input | Guide |
| --- | --- | --- |
| [X2: Edit Video](x2-01-edit-video.json) | Video and edit prompt | [Node guide](../web/docs/ReactorIncX2EditVideo.md) |
| [X2: Edit with a Reference Image](x2-02-reference-edit.json) | Video, edit prompt, and reference image | [Node guide](../web/docs/ReactorIncX2EditVideo.md) |
| [X2: Edit Webcam Video with Pointer Controls](x2-03-webcam.json) | Webcam and live edit prompt | [Node guide](../web/docs/ReactorIncX2Webcam.md) |
| [X2: Drag and Edit a Video](x2-04-live-prompt.json) | Source video and live controls | [Node guide](../web/docs/ReactorIncX2EditVideo.md) |

## Save, stop, and get help

**Save Video** writes to `video/reactor/` under the ComfyUI output folder. Examples with sound also save a separate audio file.

Use ComfyUI's cancel control to stop a queued run. Closing a tab does not cancel it. In a live panel, **End Session** stops early and discards the unfinished video.

Select a Reactor node and open native **Info** for inputs, limits, and recovery steps. Use **Fit View** to find all nodes.

## Limits

Live workflows stop at the chosen duration. Fast H3 can create a chosen number of consecutive clips.

## Open an updated example

Updates do not replace graphs already open in ComfyUI. Save your changes, then open the new example in another tab. Copy any prompts or settings you want to keep.

Only English examples are included. Notes and custom node titles are saved in the graph; changing the interface language does not translate them.

## Sample inputs

Download a sample, then select it in the matching image or video input node.

| File | Use it for |
| --- | --- |
| [Forest path](./assets/forest-path.png) | Animate an image, explore a scene, or continue a clip. |
| [Forest illustration](./assets/forest-illustration.png) | Animate a landscape or use it as a reference image. |
| [Fictional portrait](./assets/fictional-portrait.png) | Make a portrait speak with LTX. |
| [Forest motion](./assets/forest-motion.mp4) | Edit a five-second clip with SANA or X2. |

### Origin and reuse

The sample images are generated illustrations. The portrait depicts a fictional adult. Project rights in the samples are licensed under [MIT](../LICENSE.md). They are inputs, not examples of Reactor output.

The sample video adds a slow zoom to the forest image: 120 frames at 24 fps, 640 × 360 pixels, standard dynamic range, and no sound. It uses the same license as the images.

### Workflow previews

These images show frames from Reactor output. Your results can differ. Project rights in the previews use the same MIT license.

| Preview | Workflow |
| --- | --- |
| [Stream over rocks](./fast-h3-01-text-to-video.jpg) | [Fast H3: Generate a Clip with Audio](fast-h3-01-text-to-video.json) |
| [Animated forest](./helios-02-image-to-video.jpg) | [Helios: Animate an Image](helios-02-image-to-video.json) |
