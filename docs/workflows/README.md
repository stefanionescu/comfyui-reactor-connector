# Choose a Reactor workflow

The editable graphs are in the top-level [workflows folder](../../workflows/README.md).
This folder contains their written guides.

Use these guides with the JSON files in the native **Templates** browser.
Choose **reactor-inc**, then select the named example. Opening a template
does not start a paid session. Set your key once in **ComfyUI menu → Extensions → Reactor → Reactor
settings**; never put it in a node or workflow note.

| Task | Guide |
| --- | --- |
| Change prompts while recording or drag in X2 | [Live controls](../live.md) |
| Edit a webcam | [SANA](../nodes/ReactorIncSanaWebcam.md) or [X2](../nodes/ReactorIncX2Webcam.md) |
| Continue a scene across clips | [Fast H3](../nodes/ReactorIncFastContinue.md) |
| Build a clip with sound and optional first or last images | [Fast H3](fast-h3.md) |
| Generate from text or animate a picture | [Helios](helios.md) |
| Prepare a sequence of prompt changes | [Helios sequences](helios.md#prepare-prompt-changes) |
| Explore an image with fixed camera directions | [LingBot models](lingbot.md) |
| Move the camera with keys or buttons while recording | [LingBot live examples](lingbot.md) |
| Schedule a camera change or a new shot | [LongLive](longlive.md) |
| Edit a local video or reconstruct it | [SANA](sana.md) |
| Edit a video with an optional subject reference | [X2](x2.md) |
| Generate video with sound | [Visko models](visko.md) |
| Make a portrait speak a script | [LTX](ltx.md) |

All examples use native ComfyUI nodes and this connector. They do not require
other custom node packages. Read the **Start here** note, supply local media
where needed, and select **Run**. Select **Help** on the Reactor node for its complete input guide. Use **Fit View** to see the graph, then zoom in to read.

**Preview and save video** writes under `video/reactor/` in the ComfyUI output folder. Examples
with sound also use **Save Audio (Advanced)** under `audio/reactor/`. Those prefixes
are relative paths that you can change. The supplied graphs contain no private
files or machine-specific paths. Choose your own input files after importing them.

Video and audio save nodes have separate space, so the video preview does
not cover the audio controls. Use Fit View after importing, then zoom to the node
you need. The node's Info panel keeps its guide readable at any canvas zoom.

The generation node shows the requested video length. Webcam and
live-prompt examples request twenty seconds. Continued-scene examples request
three clips of about six seconds each. Connection, preparation, and recording readiness also use session
time and credits. Check the host limits before a run.
Change **Variation** for another paid run with otherwise unchanged inputs.
Use ComfyUI's cancel control to stop a run; closing a tab does not cancel it.
