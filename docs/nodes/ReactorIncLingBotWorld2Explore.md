# Reactor LingBot World 2: Explore an image

Move through a scene from your image and save a video. Choose a direction for
the camera to follow, or turn on **Live controls** to steer with keys and buttons.
Recording stops after the duration you choose.

## Set up and run

1. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open a LingBot World 2 template and upload one picture in **Load Image**.
3. Describe the scene in **Scene prompt** and choose the video length in **Video length (seconds)**.
4. Choose camera directions, or turn on **Live controls** to use keys and buttons.
5. Connect **Video** to **Save Video**, then select **Run**.
6. Play the result in Save Video. It also saves the file in ComfyUI's output folder.

For a first run, use a picture of a path or room with clear depth. Choose
`forward`, leave look directions at `idle`, and record two seconds.

## Inputs

| Input | What it does |
| --- | --- |
| Starting image | Starting picture. Connect one image from Load Image; batches are not supported. |
| Scene prompt | Describe the scene and motion in 1 to 1,000 characters. |
| Video length (seconds) | Video length in seconds. Default: 5. The limit in Reactor settings applies. |
| Seed | Number sent to the model. Range: 0–4,294,967,295; default: 42. It does not guarantee identical results. |
| Variation | Change this number to request another paid run with the same other settings. Default: 0. |
| Movement | Forward, back, or idle. Choose idle to stay in place. |
| Sideways movement | Sideways movement: strafe left, strafe right, or idle. Combine it with forward or back to move diagonally. |
| Turn left or right | Keep looking left or right. Choose idle to stop turning. |
| Look up or down | Keep looking up or down. You can combine it with horizontal look. |
| Turn per step (degrees) | Turn amount per model step, in degrees. Larger values turn faster; 0 stops turning. Range: 0–30; default: 5. This is not degrees per second. |
| Live controls | Open the live controls. Default: off. The camera starts still; the panel controls replace the direction inputs above. |

You can move forward or back and sideways at the same time.
Camera changes take time to appear because the model applies them as it generates
new frames. Once set, a direction stays active until you change or release it.

## Live controls

Select Run with **Live controls** on. Wait for the live picture, then click it to use
**W, A, S, D** to move and the **arrow keys** to look around. Click a direction
button for a short movement, or hold it to keep moving.

Edit **Scene prompt** and select **Apply prompt** to change later frames. Use
up to 1,000 characters. For example: “A sunny clearing opens ahead.” The starting
image stays fixed, and the saved workflow keeps its original prompt. Clicking
the text field releases held camera movement.

**Escape**, changing window focus, or hiding the tab releases held movement.
Let recording finish to save the video. **End session** stops early and discards
the video from that run. These controls work in the ComfyUI window that started the workflow. Multi-user mode is not supported.

The preview shows up to ten frames per second at up to 640 × 360 pixels.
The saved video keeps the model's original resolution. This operation has no sound.

## Outputs and cost

**Video** connects to Save Video or another ComfyUI video node. **Recording details** is text
with recording details. For live runs, it also lists camera commands the model
confirmed receiving and the number of preview frames. Receiving a command does
not prove that the requested movement is visible.

A new run uses Reactor credits. Setup and connection time also count toward the
session time limit, so billed time can exceed video length. Running the same
workflow again may reuse ComfyUI's cached result. Change **Variation** for another
paid run. Changing the account or execution limits also prevents reuse.

## Stop and recover

Use ComfyUI's cancel control to stop a run. Closing an ordinary workflow tab does
not cancel it. If the live panel disconnects, the connector releases movement
and asks Reactor to stop after five seconds without contact. Cleanup has its own
time limit. Wait for confirmation that the session ended before trying again.
If confirmation is missing, check Reactor Usage and wait for the session limit.

The connector runs one session at a time. It does not automatically repeat a
rejected command or create a replacement session after a connection failure.
A missing image, invalid direction, or oversized prompt is rejected before a
paid session starts. If video stops arriving, check Reactor availability and
your account, then consider a shorter recording.

A saved video cannot reopen the scene on Reactor. Playing it again only repeats
the recording.

[Reactor LingBot World 2 schema](https://docs.reactor.inc/model-api-reference/lingbot-world-2/schema)

## Check the credit rate

Select **View credit rate** on this node to open its model rate. The time starts with this node's requested video length. Enter a different session
time to include setup or other paid time. Session time includes setup and can
exceed the saved video length. This calculation does not limit spending.
Open **ComfyUI menu → Extensions → Reactor → Reactor models** and select **Refresh models** for current rates. See [settings](../settings.md#check-the-credit-rate)
for details.

## Recording details

The **Recording details** output identifies the model and describes the saved file. See
[recording details](../recording-details.md) for dimensions, duration, audio
presence, and cache behavior. It contains no prompts or session credentials.
