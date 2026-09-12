# Reactor Helios: Generate Video

Generate a short video from a prompt using your Reactor account. Connect **Video**
to ComfyUI's **Save Video** node to preview and save the result.

## Inputs

| Input                  | What to provide                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------------------------- |
| Scene prompt           | Describe the scene and motion. Empty prompts are rejected before a session starts.                      |
| Video length (seconds) | Requested video duration, from 0.1 to the video duration limit in Reactor settings. Default: 5 seconds. |
| Seed                   | Integer from 0 to 4,294,967,295. Zero is valid. Default: 42.                                            |
| Run number             | Change this number to request another run with otherwise identical inputs.                              |
| Live controls          | Open live controls in the ComfyUI window that runs the workflow. Default: false.                        |

## Run and save

1. Open **helios-01-text-to-video** in native **Browse Templates → reactor-inc**.
2. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
3. Describe the scene in **Scene prompt**. For example: “A red ball rolls slowly
   across a wooden table. The camera stays still.”
4. Choose **Video length (seconds)**, then select **Run**.
5. Play the result in **Preview and Save Video**. This node also saves the file.

The Reactor node returns **Video** without sound and **Recording details** as
text. In your own graph, connect **Video** to **Save Video** to keep the result
after ComfyUI clears its temporary storage.

## Cancellation and recovery

Use ComfyUI's cancel control to stop a queued or running workflow. With **Live
controls** off, closing the browser does not cancel the workflow. With live
controls on, closing the live panel or losing its browser connection ends the
session and discards the unfinished video.

Failed runs do not return a video. Correct any reported input error before
running again. If video stops arriving, check your connection and Reactor
account. If the session's end is unconfirmed, wait for the stated session limit
before trying again. Do not restart ComfyUI to bypass this wait.

The connector runs one session at a time. Other runs wait and can be cancelled
before they connect. The default queue wait limit is 120 seconds. A rejected
command or lost connection ends the run; the connector does not retry it.

Unchanged inputs may reuse ComfyUI's cached result. Change **Run number** for
another generation. Changing the key or execution limits can also cause another
run. A seed does not guarantee identical results after a model update.

[Reactor Helios reference](https://docs.reactor.inc/model-api-reference/helios/overview)

## Live controls

Turn **Live controls** on, select **Run**, then select **Start session** in the
live panel within 60 seconds. Use **Apply prompt** to change later frames.
Let recording finish to save the result. **End session** discards the unfinished
video. Panel prompt changes do not rewrite the saved workflow.

Keep the live panel open until recording finishes. Closing it or losing its
browser connection ends the live session and discards the unfinished video.
The preview has no sound. Prompt changes are sent to Reactor but are not saved
in **Recording details**.

For current session rates, open **Extensions → Reactor → Reactor models**.

## Recording details

**Recording details** describes the saved file, model, and timing. It does not
measure visual quality or billed time. ComfyUI can reuse a cached report; do not
run another paid generation solely to refresh it.
