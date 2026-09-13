# X2: Edit Video (Reactor)

Edit a local video through X2. Connect native **Load Video** or **Create Video**
to **source video**, and connect **video** to **Save Video**. To replace or insert a subject,
connect one **Load Image** output to **reference image** and describe the change.
The result contains video without audio.

Start with **keep queued frames** and **hold pointer** disabled. When using a
reference, describe what to replace and what to preserve. Review the subject
and background at the beginning, middle, and end; the model may apply only part
of the requested change.

## Inputs

| Input                     | What to provide                                                                                             |
| ------------------------- | ----------------------------------------------------------------------------------------------------------- |
| source video              | One standard dynamic range (SDR) color clip with at least 33 frames. Use native Load Video or Create Video. |
| edit prompt               | An editing instruction of 1 to 1,000 characters. A blank prompt is rejected.                                |
| video duration (seconds)    | Requested output length within the video duration limit in Reactor settings. Default: 5 seconds.            |
| run number                | Change this integer to request another run. Default: 0.                                                     |
| keep queued frames        | Keep source frames in order when true. False favors recent frames and limits delay.                         |
| hold pointer              | Hold the pointer at the chosen position while true. Default: false.                                         |
| pointer x (0-1) | Horizontal position: 0 is left, 1 is right. Default: 0.5.                                                   |
| pointer y (0-1)   | Vertical position: 0 is top, 1 is bottom. Default: 0.5.                                                     |
| reference image           | Optional single RGB image of the subject to insert or replace. Batches are rejected.                        |
| live controls             | Open live controls in the ComfyUI window that runs the workflow. Default: false.                            |

X2 has no seed command. **run number** controls ComfyUI caching; it is not a model
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
2. Open **x2-01-edit-video** in **Browse Templates → reactor-inc**.
3. Upload a short clip in **Load Source Video**. Keep the example watercolor prompt for a first run.
4. Select **Run**. **Save Video** saves the result and lets you play it.

Use **x2-02-reference-edit** to provide a subject image as well. Choose an image
with a clear subject and describe what to replace in the source clip.

The local clip is published at its original frame rate. After its last frame, the
input holds that frame until recording ends. The clip does not loop.
Keeping queued source frames can delay the model's response; it does not guarantee that the
saved video includes every source frame. X2 controls output resolution.

The pointer refers to the output frame. This node holds one position during a
run when **live controls** is off. Turn **live controls** on for live dragging
and prompt changes. The reference image stays fixed. Release the pointer to stop steering; cleanup also releases it.

In the live panel, a circle marks the point you choose. **Pointer held** or
**Pointer released** confirms that the control was accepted. The position is
measured from the picture's left and top edges. For keyboard use, focus the
output picture and position the pointer with the arrow keys. Hold Space to hold
the pointer; release Space or press Escape to release it. Losing focus also
releases the pointer.

The outputs are **video** without sound and **recording details** as text. In
your own graph, connect **video** to ComfyUI's **Save Video** to keep the result
after ComfyUI clears its temporary storage. Input copies
are removed when the session ends or execution fails.

## Cancellation

Session time includes setup and can
exceed output duration. The configured recording and server session limits apply.
Use ComfyUI's cancel control to stop a queued or running workflow. With **live controls** off, closing the browser does not cancel it. With live controls on,
losing the live panel ends the session and discards unfinished video.
The connector disconnects after recording, failure, or cancellation. It does not
automatically retry failed commands or uncertain session creation.

Unchanged inputs may reuse ComfyUI's cache. Change **run number** for another run. If preparation fails, use a shorter SDR clip. If the provider rejects a
reference or prompt, review those inputs before deciding to run again.

[Reactor X2 schema](https://docs.reactor.inc/model-api-reference/x2/schema)

## Live controls

Turn **live controls** on, select **Run**, then select **Start session** in the
live panel within 60 seconds. Use **Apply prompt** to change later frames.
Let recording finish to save the result. **End session** discards the unfinished
video. Panel prompt changes do not rewrite the saved workflow.

Keep the live panel open until recording finishes. Closing it or losing its
browser connection ends the session and discards the unfinished video. The
preview has no sound.

For current session rates, open **Extensions → Reactor → Reactor models**.

## Recording details

**recording details** describes the saved file, model, and timing. It does not
measure visual quality or billed time. ComfyUI can reuse a cached report; do not
run another paid generation solely to refresh it.
