# Reactor workflows

This folder contains 33 editable ComfyUI workflows. Examples are grouped in model folders. Each JSON file opens as a graph with connected nodes, a short setup note, and extra instructions where needed.

## Open a workflow

1. Download or locate a JSON file listed below.
2. Drag it onto the ComfyUI canvas. You can also open **Templates**, choose **reactor-inc**, and select the same example.
3. Read **Start here**. Upload your own image or video when the example needs one.
4. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**. Select **Run** when the inputs are ready.

Opening a workflow does not start generation. A new generation uses Reactor credits.
Use the [sample inputs](assets/README.md) if you need an image or short source clip.

## Open the latest example after an update

Updating Reactor does not replace graphs already open in ComfyUI. Save your own changes, create a new workflow tab, and open the example again from **Templates**. Keep the old tab until you have copied any prompts or settings you want to reuse.

## Available files

| Model | Workflow JSON | Input | Guide |
| --- | --- | --- | --- |
| Fast H3 | [Build a clip with sound](fast-h3/fast-h3-01-text-to-video.json) | Scene and sound prompt | [Steps](../docs/workflows/fast-h3.md) |
| Fast H3 | [Animate a starting image](fast-h3/fast-h3-02-image-to-video.json) | Image and prompt | [Steps](../docs/workflows/fast-h3.md) |
| Fast H3 | [Connect two images with motion](fast-h3/fast-h3-03-first-and-last-frames.json) | First image, final image, and prompt | [Steps](../docs/workflows/fast-h3.md) |
| Fast H3 | [Finish on a chosen image](fast-h3/fast-h3-04-ending-frame.json) | Final image and prompt | [Steps](../docs/workflows/fast-h3.md) |
| Fast H3 | [Continue a scene](fast-h3/fast-h3-05-continue-scene.json) | Prompts for continued clips | [Steps](../docs/workflows/fast-h3.md) |
| Fast H3 | [Continue from an image](fast-h3/fast-h3-06-continue-image.json) | Starting image and continued clips | [Steps](../docs/workflows/fast-h3.md) |
| Helios | [Text to video](helios/helios-01-text-to-video.json) | Scene prompt | [Steps](../docs/workflows/helios.md) |
| Helios | [Animate a local image](helios/helios-02-image-to-video.json) | Image and prompt | [Steps](../docs/workflows/helios.md) |
| Helios | [Follow a prompt sequence](helios/helios-03-prompt-sequence.json) | Scheduled prompts | [Steps](../docs/workflows/helios.md) |
| Helios | [Animate an image through prompt changes](helios/helios-04-image-sequence.json) | Starting image and scheduled prompts | [Steps](../docs/workflows/helios.md) |
| Helios | [Change the prompt while recording](helios/helios-05-live-prompt.json) | Live prompt | [Steps](../docs/workflows/helios.md) |
| Helios | [Animate an image with live prompts](helios/helios-06-live-image.json) | Image and live prompt | [Steps](../docs/workflows/helios.md) |
| LingBot | [Explore a local image](lingbot/lingbot-01-explore-image.json) | Image and prompt | [Steps](../docs/workflows/lingbot.md) |
| LingBot | [Move through an image](lingbot/lingbot-02-live-camera.json) | Image and prompt; live keys or buttons | [Steps](../docs/workflows/lingbot.md) |
| LingBot World 2 | [Explore a local image](lingbot-world-2/lingbot-world-2-01-explore-image.json) | Image and prompt | [Steps](../docs/workflows/lingbot.md) |
| LingBot World 2 | [Move and look independently](lingbot-world-2/lingbot-world-2-02-live-camera.json) | Image and prompt; live keys or buttons | [Steps](../docs/workflows/lingbot.md) |
| LongLive | [Opening shot](longlive-v2/longlive-v2-01-text-to-video.json) | Scene prompt | [Steps](../docs/workflows/longlive.md) |
| LongLive | [Soft transition and hard cut](longlive-v2/longlive-v2-02-storyboard.json) | Opening prompt and two scheduled shots | [Steps](../docs/workflows/longlive.md) |
| LongLive | [Change the prompt while recording](longlive-v2/longlive-v2-03-live-prompt.json) | Live prompt | [Steps](../docs/workflows/longlive.md) |
| LTX | [Make a portrait speak](ltx2/ltx2-01-speaking-portrait.json) | Portrait and speech script | [Steps](../docs/workflows/ltx.md) |
| SANA | [Edit a local video](sana-streaming/sana-streaming-01-edit-video.json) | Video and edit prompt | [Steps](../docs/workflows/sana.md) |
| SANA | [Change the prompt while recording](sana-streaming/sana-streaming-02-live-prompt.json) | Source video and live controls | [Steps](../docs/workflows/sana.md) |
| SANA | [Edit a webcam](sana-streaming/sana-streaming-03-webcam.json) | Webcam and live edit prompt | [Steps](../docs/workflows/sana.md) |
| Visko Dynamic | [Video with sound](visko-orbis-dynamic/visko-dynamic-01-text-to-video.json) | Scene and sound prompt | [Steps](../docs/workflows/visko.md) |
| Visko Dynamic | [Animate an image with sound](visko-orbis-dynamic/visko-dynamic-02-image-to-video.json) | Image and prompt | [Steps](../docs/workflows/visko.md) |
| Visko Dynamic | [Change the prompt while recording](visko-orbis-dynamic/visko-dynamic-03-live-prompt.json) | Live prompt | [Steps](../docs/workflows/visko.md) |
| Visko Stable | [Video with sound](visko-orbis-stable/visko-stable-01-text-to-video.json) | Scene and sound prompt | [Steps](../docs/workflows/visko.md) |
| Visko Stable | [Animate an image with sound](visko-orbis-stable/visko-stable-02-image-to-video.json) | Image and prompt | [Steps](../docs/workflows/visko.md) |
| Visko Stable | [Change the prompt while recording](visko-orbis-stable/visko-stable-03-live-prompt.json) | Live prompt | [Steps](../docs/workflows/visko.md) |
| X2 | [Edit a local video](x2/x2-01-edit-video.json) | Video and edit prompt | [Steps](../docs/workflows/x2.md) |
| X2 | [Edit with a reference image](x2/x2-02-reference-edit.json) | Video, edit prompt, and reference image | [Steps](../docs/workflows/x2.md) |
| X2 | [Edit and drag a webcam scene](x2/x2-03-webcam.json) | Webcam and live edit prompt | [Steps](../docs/workflows/x2.md) |
| X2 | [Drag and edit a video](x2/x2-04-live-prompt.json) | Source video and live controls | [Steps](../docs/workflows/x2.md) |

## Save, stop, and get help

**Preview and save video** previews the result and writes to `video/reactor/` under the ComfyUI output folder. Examples with sound also save a separate audio file.

Use ComfyUI's cancel control to stop a run. Closing a tab does not cancel an ordinary queued graph. In a live-camera panel, **End session** stops the session and discards the unfinished video.

Select a Reactor node, then choose **Help** for its inputs, limits, and recovery steps. Use **Fit View** to find all nodes, then zoom in to read or edit them.

## Current limits

These examples use native ComfyUI nodes and Reactor. Media inputs start empty; the graphs contain no private files, machine-specific paths, or API keys.

Live workflows stop at the chosen duration. Fast H3 can chain a chosen number of clips; the node guide explains recording length and credit use.
