# Reactor Helios: Animate an image

Animate one RGB image with a prompt using your Reactor account. Connect **Load
Image** to **Starting image** and connect **Video** to **Save Video**.

## Inputs

| Input | What to provide |
| --- | --- |
| Starting image | One native RGB image. Image batches and non-finite pixels are rejected. |
| Scene prompt | Describe the intended scene and motion. Required; cannot be empty. |
| Video length (seconds) | Requested video duration within the video duration limit in Reactor settings. Default: 5 seconds. |
| Seed | Integer from 0 to 4,294,967,295. Zero is valid. Default: 42. |
| Variation | Change this number to request another paid run with identical prompt and seed. |
| Live controls | Open live controls in the ComfyUI window that runs the workflow. Default: false. |

The image is uploaded as PNG, then applied together with the prompt before
generation starts. Reactor may crop or resize it for the model. Images over
8192 pixels per side or the upload limit in Reactor settings are rejected.

## Run and save

1. Open [Helios image to video](/extensions/reactor-inc/guides/files/workflows/helios/helios-02-image-to-video.json).
2. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
3. Upload your picture in **Upload your starting image**. You can use the
   [forest illustration](/extensions/reactor-inc/guides/files/workflows/assets/forest-illustration.png).
4. Describe the motion in **Scene prompt**. For example: “The camera moves slowly
   along the forest path.” Choose **Video length (seconds)**, then select **Run**.
5. Play the result in **Preview and save video**. This node also saves the file.

The Reactor node returns **Video** without sound and **Recording details** as
text. In your own graph, connect **Video** to **Save Video** to keep the result
after ComfyUI clears its temporary storage. The model may change the image's
content or crop.

## Cost and cancellation

Setup and generation use Reactor credits. Session time can exceed the saved
video length. A seed does not guarantee identical results after a model update.
Unchanged inputs may reuse ComfyUI's cached result. Changing the key or execution
limits can cause another paid run when you next select **Run**.

Use ComfyUI's cancel control to stop a run. Closing the ComfyUI window does not
cancel a queued workflow. Failed runs do not return a video. If the session's
end is unconfirmed, wait for the stated session limit before trying again.
Do not restart ComfyUI to bypass this wait.

The connector runs one session at a time. Other runs wait and can be cancelled
before they connect. The default queue wait limit is 120 seconds. A rejected
command or lost connection ends the run; the connector does not retry it.

For invalid inputs, missing video, or connection errors, follow the
[troubleshooting guide](/extensions/reactor-inc/guides/docs/troubleshooting.html).

[Reactor Helios reference](https://docs.reactor.inc/model-api-reference/helios/overview)

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
