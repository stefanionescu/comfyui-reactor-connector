# Reactor X2: Edit video

Edit a local video through X2. Connect native **Load Video** or **Create Video**
to **Source video**, and connect **Video** to **Save Video**. To replace or insert a subject,
connect one **Load Image** output to **Reference image** and describe the change.
The result contains video without audio.

## Inputs

| Input | What to provide |
| --- | --- |
| Source video | One SDR RGB clip with at least 33 frames. Use native Load Video or Create Video. |
| Scene prompt | An editing instruction of 1 to 1,000 characters. A blank prompt is rejected. |
| Video length (seconds) | Requested output length within the video duration limit in Reactor settings. Default: 5 seconds. |
| Variation | Change this integer to request another paid run. Default: 0. |
| Keep queued frames | Keep source frames in order when true. False favors recent frames and limits delay. |
| Hold pointer | Hold the pointer at the chosen position while true. Default: false. |
| Pointer X | Horizontal position: 0 is left, 1 is right. Default: 0.5. |
| Pointer Y | Vertical position: 0 is top, 1 is bottom. Default: 0.5. |
| Reference image | Optional single RGB image of the subject to insert or replace. Batches are rejected. |
| Live controls | Open live controls in the ComfyUI window that runs the workflow. Default: false. |

X2 has no seed command. **Variation** controls ComfyUI caching; it is not a model
seed and does not guarantee reproducibility.

Source clips must have even dimensions, at most 4096 pixels per side, and a frame
rate from 1 to 120 fps. The connector supports MP4, MOV, WebM, and AVI. It rejects
HDR, multiple video streams, and fewer than 33 usable frames before connecting.
Files and frames must fit the configured upload and memory limits.

Preparation creates a temporary video-only MP4, respects native file trim
windows, and limits source length to the video duration limit in Reactor settings. Source audio and
metadata are omitted. Preparation has a 60-second deadline and supports cancel.

## Run and save

1. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **x2-01-edit-video** in the native Templates browser.
3. Upload a short local video. Keep the example watercolor prompt for a first run.
4. Select **Run**, then play the result in Save Video.

Use **x2-02-reference-edit** to provide a subject image as well. Choose an image
with a clear subject and describe what to replace in the source clip.

The local clip is published at its original frame rate. After its last frame, the
input holds that frame until recording ends. The clip does not loop.
Keeping queued source frames can delay the model's response; it does not guarantee that the
saved video includes every source frame. X2 controls output resolution.

The pointer refers to the output frame. This node holds one position during a
run when **Live controls** is off. Turn **Live controls** on for live dragging
and prompt changes. The reference image stays fixed. Release the pointer to stop steering; cleanup also releases it.

In the live panel, a circle marks the point you choose. **Pointer held** or
**Pointer released** confirms that the control was accepted. The position is
measured from the picture's left and top edges. See [live controls](/extensions/reactor-inc/guides/docs/live.html#drag-in-x2)
for keyboard use.

The outputs are native `VIDEO` and recording details as `STRING`. Save Video
retains the temporary result under its relative output prefix. Input copies
are removed when the session ends or execution fails.

## Cost and cancellation

A new execution uses Reactor credits. Session time includes setup and can
exceed output duration. The configured recording and server session limits apply.
Use ComfyUI's cancel control to stop; closing a tab does not cancel a workflow.
The connector disconnects after recording, failure, or cancellation. It does not
automatically retry failed commands or uncertain session creation.

Unchanged inputs may reuse ComfyUI's cache. Change **Variation** for another paid
run. If preparation fails, use a shorter SDR clip. If the provider rejects a
reference or prompt, review those inputs before deciding to run again.

[Reactor X2 schema](https://docs.reactor.inc/model-api-reference/x2/schema)


## Live controls

Turn **Live controls** on, select **Run**, then select **Start session** in the
live panel within 60 seconds. Use **Apply prompt** to change later frames.
Let recording finish to save the result. **End session** discards the unfinished
video. Panel prompt changes do not rewrite the saved workflow.

See the [live controls guide](/extensions/reactor-inc/guides/docs/live.html) for input, privacy, and stopping rules.

## Check the credit rate

Select **View credit rate** on this node to open its model rate. The time starts with this node's requested video length. Enter a different session
time to include setup or other paid time. Session time includes setup and can
exceed the saved video length. This calculation does not limit spending.
Open **ComfyUI menu → Extensions → Reactor → Reactor models** and select **Refresh models** for current rates. See [settings](/extensions/reactor-inc/guides/docs/settings.html#check-the-credit-rate)
for details.

## Recording details

The **Recording details** output identifies the model and describes the saved file. See
[recording details](/extensions/reactor-inc/guides/docs/recording-details.html) for dimensions, duration, audio
presence, and cache behavior. It contains no prompts or session credentials.
