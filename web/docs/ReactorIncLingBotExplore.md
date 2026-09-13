# LingBot: Explore an Image (Reactor)

Move through a scene from your image and save a video. Choose a direction for
the camera to follow, or turn on **live controls** to steer with keys and buttons.
Recording stops after the duration you choose.

## Set up and run

1. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **lingbot-01-explore-image** in **Browse Templates → reactor-inc**.
   Upload one picture in **Load Starting Image**.
3. Describe the scene in **scene prompt** and choose the video length in **video duration (seconds)**.
4. Choose camera directions, or turn on **live controls** to use keys and buttons.
5. Select **Run**.
6. Play the result in **Save Video**. It also saves the file.

For a first run, use a picture of a path or room with clear depth. Set **movement**
to `forward`, set **turn left or right** and **look up or down** to `idle` (stop),
and record two seconds.

## Inputs

| Input                   | What it does                                                                                                            |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| starting image          | Starting picture. Connect one image from Load Image; batches are not supported.                                         |
| scene prompt            | Describe the scene and motion in 1 to 1,000 characters.                                                                 |
| video duration (seconds)  | Video length in seconds. Default: 5. The limit in Reactor settings applies.                                             |
| seed                    | Number sent to the model. Range: 0–4,294,967,295; default: 42. It does not guarantee identical results.                 |
| run number              | Change this number to request another run with the same other settings. Default: 0.                                     |
| movement                | `forward`, `back`, `strafe_left` (move left), `strafe_right` (move right), or `idle` (stop).                            |
| turn left or right      | `left` or `right` keeps turning the camera. Choose `idle` to stop turning.                                              |
| look up or down         | `up` or `down` keeps tilting the camera. Choose `idle` to stop tilting. Combine with horizontal look if needed.         |
| turn per step (degrees) | Degrees per latent frame (an internal model step). Larger values turn faster; 0 stops turning. Range: 0–30; default: 5. |
| live controls           | Open the live controls. Default: off. The camera starts still; the panel controls replace the direction inputs above.   |

Choose one movement direction at a time. In the live panel, forward or back takes priority over sideways movement.
Camera changes take time to appear because the model applies them as it generates
new frames. Once set, a direction stays active until you change or release it.

## Live controls

Select Run with **live controls** on. Wait for the live picture, then click it to use
**W, A, S, D** to move and the **arrow keys** to look around. Click a direction
button for a short movement, or hold it to keep moving.

Edit **scene prompt** and select **Apply prompt** to change later frames. Use
up to 1,000 characters. For example: “A sunny clearing opens ahead.” The starting
image stays fixed, and the saved workflow keeps its original prompt. Clicking
the text field releases held camera movement.

**Escape**, changing window focus, or hiding the tab releases held movement.
Let recording finish to save the video. **End session** stops early and discards
the video from that run. These controls work in the ComfyUI window that started the workflow. Multi-user mode is not supported.

The preview shows up to ten frames per second at up to 640 × 360 pixels.
The saved video keeps the model's original resolution. This operation has no sound.

## Outputs

**video** connects to **Save Video** or another ComfyUI video node.
**recording details** describes the saved file and model. For live runs, it also
lists camera commands the model confirmed receiving and the number of preview
frames. Receiving a command does not prove that the requested movement is visible.

Unchanged inputs may reuse ComfyUI's cached video and report. Change **run number**
for another generation. Setup also uses session time, so the saved video length
is not the billed duration.

## Stop and recover

Use ComfyUI's cancel control to stop a queued or running workflow. With **live controls** off, closing the browser does not cancel it. With live controls on,
closing the live panel ends the session. A lost browser connection ends the
session after five seconds without contact. Both discard unfinished video. Cleanup has its own
time limit. Wait for confirmation that the session ended before trying again.
If confirmation is missing, check Reactor Usage and wait for the session limit.

If video stops arriving, check your connection and Reactor account. Correct
reported input errors before trying again.

A saved video cannot reopen the scene on Reactor. Playing it again only repeats
the recording.

[Reactor LingBot schema](https://docs.reactor.inc/model-api-reference/lingbot/schema)

For current session rates, open **Extensions → Reactor → Reactor models**.
