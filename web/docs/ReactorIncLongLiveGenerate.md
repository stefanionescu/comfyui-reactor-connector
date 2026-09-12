# Reactor LongLive: Generate Video

Generate a short video from an opening shot prompt with LongLive.

## Inputs

| Input                  | What to provide                                                                  |
| ---------------------- | -------------------------------------------------------------------------------- |
| Scene prompt           | Describe the opening scene and motion. Use 1 to 20,000 characters.               |
| Video length (seconds) | Video length; default: 5 seconds. The limit in Reactor settings applies.         |
| Seed                   | Integer from 0 to 4,294,967,295; default: 42.                                    |
| Run number             | Change this number for another run; default: 0.                                  |
| Live controls          | Open live controls in the ComfyUI window that runs the workflow. Default: false. |

Example prompt: “A fox walks along a forest path. The camera follows slowly.”
Use 2 seconds for a first video. For later shots and cuts, open the
separate LongLive storyboard workflow.

## Run and save

1. Open **longlive-v2-01-text-to-video** in **Browse Templates → reactor-inc**.
2. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
3. Enter **Scene prompt** in **LongLive: Opening Shot**.
4. Choose **Video length (seconds)**, then select **Run**.
5. Play the result in **Preview and Save Video**. This node also saves the file.

The node returns **Video** without audio and **Recording details** as text.
In your own graph, connect **Video** to ComfyUI's **Save Video** to keep the
result after ComfyUI clears its temporary storage.

**Video length (seconds)** limits the recorded video. The session time limit in
Reactor settings also applies. Unchanged inputs may reuse ComfyUI's cached
result; change **Run number** for another generation. Changing the account or
execution limits can also cause another run. Seeds do not guarantee identical
results after a model update.

## Cancellation

Use ComfyUI's cancel control to stop a queued or running workflow.
With **Live controls** off, closing the browser does not cancel the workflow.
With live controls on, losing the live panel ends the session and discards the
unfinished video.
The connector runs one session at a time and disconnects after recording or
failure. It does not retry failed commands or uncertain session creation. If
it cannot confirm that the session ended, wait for the stated time limit before
trying again.

## Recovery

Enter a prompt before running. If video stops arriving, check Reactor and your
account before trying again. Use LongLive Storyboard to schedule later shots.
This node does not accept a starting image.

[LongLive schema](https://docs.reactor.inc/model-api-reference/longlive-v2/schema)

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
