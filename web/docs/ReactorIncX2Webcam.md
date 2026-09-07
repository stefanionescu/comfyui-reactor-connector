# Reactor X2: Edit a Webcam

Edit a live camera scene and drag on the output to steer the subject. Save the
result as a video without sound. X2 requires a non-empty edit prompt.

## Inputs

| Input                  | What to provide                                                                                |
| ---------------------- | ---------------------------------------------------------------------------------------------- |
| Scene prompt           | Describe the edit in 1 to 1,000 characters.                                                    |
| Video length (seconds) | Output length from 0.1 to 60 seconds, within your Reactor settings limit. Default: 10 seconds. |
| Variation              | Change this value for another paid run. Default: 0.                                            |
| Reference image        | Optional single RGB image of a subject to insert or replace. Connect Load Image.               |

X2 has no seed control. The reference image is set before generation and stays
fixed during the session. The node returns `VIDEO` and recording details as `STRING`.

## Run and save

1. Open **x2-03-webcam** from the connector's templates.
2. Describe the edit. Optionally connect a subject image to **Reference image**.
3. Select **Run**, then **Enable camera** in the live panel. Allow camera access.
4. Check the preview. Choose another camera and select **Use selected camera** if needed.
5. Select **Start session** within 60 seconds. This starts a paid Reactor session.
6. Drag on the output picture to steer the subject. A circle marks your chosen
   point. **Pointer held** or **Pointer released** confirms that the control was
   accepted. Release to stop.
7. Use **Apply prompt** to change the edit. Let recording finish to save the video.

For keyboard use, focus the output picture. Arrow keys position the pointer;
Space holds it and Escape releases it. The pointer also releases when the
picture loses focus. X2 applies controls to later groups of generated frames,
so motion may lag behind your input.

Camera frames use up to 640 × 480 pixels and at most ten new frames per second.
The connector repeats the latest frame on the model's 24 fps input. No microphone
audio is sent and no separate camera recording is saved.

**End session** discards the unfinished video. Closing the panel stops camera
access and causes the session to end. Losing camera input for three seconds also
ends the session. Check browser camera permissions and use localhost or HTTPS
if the camera cannot start.

See the [live controls guide](../../ADVANCED.md#live-controls) for session limits and recovery.

## Credit rate

Select **View credit rate** to calculate a rate for your chosen session time.
Setup can add paid time beyond the video length; this is not a spending limit.
See [credit rates](../../ADVANCED.md#credit-rates).

## Recording details

This output describes the saved file and model. See the
[field reference](../../ADVANCED.md#recording-details) for timing, privacy, and cache behavior.
