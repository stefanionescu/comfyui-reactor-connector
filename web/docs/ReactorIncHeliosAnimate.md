# Helios: Animate an Image (Reactor)

Animate one RGB image with a prompt using your Reactor account. Connect **Load
Image** to **starting image** and connect **video** to **Save Video**.

## Inputs

| Input                  | What to provide                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------- |
| starting image         | One native RGB image. Image batches and non-finite pixels are rejected.                           |
| scene prompt           | Describe the intended scene and motion. Required; cannot be empty.                                |
| video duration (seconds) | Requested video duration within the video duration limit in Reactor settings. Default: 5 seconds. |
| seed                   | Integer from 0 to 4,294,967,295. Zero is valid. Default: 42.                                      |
| run number             | Change this number to request another run with identical prompt and seed.                         |
| live controls          | Open live controls in the ComfyUI window that runs the workflow. Default: false.                  |

The image is uploaded as PNG, then applied together with the prompt before
generation starts. Reactor may crop or resize it for the model. Images over
8192 pixels per side or the upload limit in Reactor settings are rejected.

Describe the subject already in your picture and the movement you want.
An unrelated scene prompt can give the model conflicting instructions.

## Run and save

1. Open **helios-02-image-to-video** in native **Browse Templates → reactor-inc**.
2. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
3. Upload your picture in **Load Starting Image**. You can use the
   forest illustration (`workflows/assets/forest-illustration.png` in the checkout).
4. Describe the motion in **scene prompt**. For example: “The camera moves slowly
   along the forest path.” Choose **video duration (seconds)**, then select **Run**.
5. Play the result in **Save Video**. This node also saves the file.

The Reactor node returns **video** without sound and **recording details** as
text. In your own graph, connect **video** to **Save Video** to keep the result
after ComfyUI clears its temporary storage. The model may change the image's
content or crop.

## Cancellation and recovery

Use ComfyUI's cancel control to stop a queued or running workflow. With **live controls** off, closing the browser does not cancel the workflow. With live
controls on, closing the live panel or losing its browser connection ends the
session and discards the unfinished video.

Failed runs do not return a video. Correct any reported input error before
running again. If video stops arriving, check your connection and Reactor
account. If the session's end is unconfirmed, wait for the stated session limit
before trying again. Do not restart ComfyUI to bypass this wait.

The connector runs one session at a time. Other runs wait and can be cancelled
before they connect. The default queue wait limit is 120 seconds. A rejected
command or lost connection ends the run; the connector does not retry it.

Unchanged inputs may reuse ComfyUI's cached result. Change **run number** for
another generation. Changing the key or execution limits can also cause another
run. A seed does not guarantee identical results after a model update.

[Reactor Helios reference](https://docs.reactor.inc/model-api-reference/helios/overview)

## Live controls

Turn **live controls** on, select **Run**, then select **Start session** in the
live panel within 60 seconds. Use **Apply prompt** to change later frames.
Let recording finish to save the result. **End session** discards the unfinished
video. Panel prompt changes do not rewrite the saved workflow.

Keep the live panel open until recording finishes. Closing it or losing its
browser connection ends the live session and discards the unfinished video.
The preview has no sound. Prompt changes are sent to Reactor but are not saved
in **recording details**.

For current session rates, open **Extensions → Reactor → Reactor models**.

## Recording details

**recording details** describes the saved file, model, and timing. It does not
measure visual quality or billed time. ComfyUI can reuse a cached report; do not
run another paid generation solely to refresh it.
