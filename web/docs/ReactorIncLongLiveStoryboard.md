# LongLive: Generate Video from a Storyboard (Reactor)

Generate a short video from an opening shot prompt with LongLive.
Schedule later shots before generation starts. Connect one or more **LongLive: Add a Shot (Reactor)** nodes to the **shots (JSON)** input. Soft transitions change the prompt
within the scene; cuts start a new scene.

## Inputs

| Input                  | What to provide                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------- |
| scene prompt           | Describe the opening scene and motion. Use 1 to 20,000 characters.                    |
| video duration (seconds) | Video length; default: 5 seconds. The limit in Reactor settings applies.              |
| seed                   | Integer from 0 to 4,294,967,295; default: 42.                                         |
| run number             | Change this number for another run; default: 0.                                       |
| shots (JSON)           | Connect LongLive: Add a Shot (Reactor). An empty list `[]` means the opening shot only. |

LongLive generates frames in groups called **chunks**. Each chunk contains
29 frames, about 1.2 seconds at 24 frames per second. Count chunks from the start
of generation. Give each later shot a larger chunk number, starting at 1.
You can add up to 32 later shots. The JSON shot list must fit within 128 KB and
contain only the fields produced by LongLive: Add a Shot (Reactor).

Choose a video length that includes all scheduled shots. A later shot does not
automatically extend the recording. Timing follows the generated frames, so do
not count seconds from when you click Run.

Example: describe a forest path as the opening shot, add a soft camera pullback
at chunk 1, then a cut to a lake at chunk 2. Record 5 seconds and watch both
transitions in the saved result.

## Run and save

1. Open **longlive-v2-02-storyboard** in **Browse Templates → reactor-inc**.
2. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
3. Edit the opening prompt, **1. Soft Transition (Reactor)**, and **2. Hard Cut (Reactor)**.
4. Choose **video duration (seconds)**, then select **Run**.
5. Play the result in **Save Video**. This node also saves the file.

The node returns **video** without audio and **recording details** as text.
In your own graph, connect **video** to ComfyUI's **Save Video** to keep the
result after ComfyUI clears its temporary storage.

**video duration (seconds)** limits the recorded video. The session time limit in
Reactor settings also applies. Unchanged inputs may reuse ComfyUI's cached
result; change **run number** for another generation. Changing the account or
execution limits can also cause another run. Seeds do not guarantee identical
results after a model update.

## Cancellation

Use ComfyUI's cancel control to stop a queued or running workflow.
Closing the browser does not cancel this workflow.
The connector runs one session at a time and disconnects after recording or
failure. It does not retry failed commands or uncertain session creation. If
it cannot confirm that the session ended, wait for the stated time limit before
trying again.

## Recovery

An empty prompt or invalid storyboard fails before connection. If a later shot
is missing, check its chunk number and the chosen video length.
Do not enter seconds in the chunk field. LongLive uses text shots; this node
does not accept a starting image.

[LongLive schema](https://docs.reactor.inc/model-api-reference/longlive-v2/schema)

For current session rates, open **Extensions → Reactor → Reactor models**.

## Recording details

**recording details** describes the saved file, model, and timing. It does not
measure visual quality or billed time. ComfyUI can reuse a cached report; do not
run another paid generation solely to refresh it.
