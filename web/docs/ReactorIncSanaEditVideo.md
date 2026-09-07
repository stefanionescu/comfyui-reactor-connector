# Reactor SANA: Edit Video

Apply an edit prompt to a local video clip. Connect native **Load Video** or
**Create Video** to **Source video**, then connect **Video** to **Save Video**. The output
contains video without audio. Leave the prompt empty to recreate the source without
requesting an edit.

Start with a clear subject and simple movement. For example, ask for a watercolor
painting that keeps the clip’s composition and motion. Leave the prompt empty
to compare SANA’s reconstruction with the original before asking for an edit.

## Inputs

| Input                  | What to provide                                                                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Source video           | One standard dynamic range (SDR) color video with at least 33 frames. Use MP4, MOV, WebM, or AVI from Load Video, or native Create Video output. |
| Scene prompt           | Describe the change to apply, using up to 20,000 characters. Leave empty to recreate the source without requesting an edit.                      |
| Video length (seconds) | Maximum output length, within the configured video duration limit in Reactor settings. Default: 5 seconds.                                       |
| Seed                   | Integer from 0 to 4,294,967,295. Default: 42.                                                                                                    |
| Variation              | Change this value for another paid run. Default: 0.                                                                                              |
| Anchor interval        | Return to the source image after this many groups of generated frames (chunks). Use 0 to turn this off. Range: 0–1,000; default: 0.              |
| Live controls          | Open live controls in the ComfyUI window that runs the workflow. Default: false.                                                                 |

Use a clip with even dimensions, no more than 4096 pixels on either side, and a
frame rate from 1 to 120 fps. HDR, multiple video streams, unsupported containers,
and fewer than 33 usable frames are rejected before connecting. File size and
frame memory must fit the host upload and queue limits.

The connector prepares a temporary video-only MP4 before connecting. It respects
native file trim windows and limits source length to the video duration limit in Reactor settings.
The source keeps its frame timing. Audio and file metadata are not sent to Reactor.
Preparation stops if it takes more than 60 seconds. You can cancel it in ComfyUI.

## Run and save

1. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **sana-streaming-01-edit-video** in the native Templates browser.
3. Upload a short source clip in Load Video and describe the edit.
4. Select **Run**, then play the output in Save Video.

Start with a three- to five-second landscape clip. For example, enter
“Change the scene to a soft watercolor painting. Keep the movement and composition.”
To change the prompt while recording, use the live panel. Editing the prompt on
the node and selecting **Run** starts another session.

The source clip plays once. If recording continues after the clip ends, SANA
keeps using the last input frame. This node uses your uploaded file; it does not
open your webcam.

Recording stops at the chosen video length or when Reactor reports that the clip
has finished. The output can be shorter than requested. The session time limit
in Reactor settings also applies.

The node returns native `VIDEO` and recording details as `STRING`. Save Video
retains the temporary result under its relative output prefix. Input copies are
removed after the session ends or the operation fails.

## Cost and cancellation

A new execution uses Reactor credits. Session time includes upload and setup,
so it can exceed the output duration. The host recording and session limits apply.
The connector disconnects after recording, failure, or cancellation and does not
automatically retry rejected commands or uncertain session creation.

Use ComfyUI's cancel control to stop. Closing the ComfyUI window does not cancel
a queued workflow. Unchanged inputs may reuse ComfyUI's cache; change **Variation**
to request another paid run. Seeds do not guarantee identical output after a
provider update.

## Recovery

If source preparation fails, use a shorter SDR MP4 with one video stream and at
least 33 frames. Read the error shown in ComfyUI before running again. If Reactor
rejects the clip or prompt, the session ends without an automatic retry.

[Reactor SANA schema](https://docs.reactor.inc/model-api-reference/sana-streaming/schema)

## Live controls

Turn **Live controls** on, select **Run**, then select **Start session** in the
live panel within 60 seconds. Use **Apply prompt** to change later frames.
Let recording finish to save the result. **End session** discards the unfinished
video. Panel prompt changes do not rewrite the saved workflow.

See the [live controls guide](../../ADVANCED.md#live-controls) for input, privacy, and stopping rules.

## Credit rate

Select **View credit rate** to calculate a rate for your chosen session time.
Setup can add paid time beyond the video length; this is not a spending limit.
See [credit rates](../../ADVANCED.md#credit-rates).

## Recording details

This output describes the saved file and model. See the
[field reference](../../ADVANCED.md#recording-details) for timing, privacy, and cache behavior.
