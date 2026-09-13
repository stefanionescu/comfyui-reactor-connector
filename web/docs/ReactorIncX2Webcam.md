# X2: Edit Webcam Video (Reactor)

Edit a live camera scene and drag on the output to steer the subject. Save the
result as a video without sound. X2 requires a non-empty edit prompt.
Use a local, single-user ComfyUI installation with camera access. Your camera
remains off until you enable it in the live panel.

## Inputs

| Input                  | What to provide                                                                                |
| ---------------------- | ---------------------------------------------------------------------------------------------- |
| edit prompt            | Describe the edit in 1 to 1,000 characters.                                                    |
| video duration (seconds) | Output length from 0.1 to 60 seconds, within your Reactor settings limit. Default: 10 seconds. |
| run number             | Change this value for another run. Default: 0.                                                 |
| reference image        | Optional single RGB image of a subject to insert or replace. Connect Load Image.               |

X2 has no seed control. The reference image is set before generation and stays
fixed during the session. The node returns **video** without sound and **recording details** as text.

## Run and save

1. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **x2-03-webcam** in **Browse Templates → reactor-inc**.
3. Describe the edit. Optionally connect a subject image to **reference image**.
4. Select **Run**, then **Enable camera** in the live panel. Allow camera access.
5. Check the preview. Choose another camera and select **Use selected camera** if needed.
6. Select **Start session** within 60 seconds.
7. Drag on the output picture to steer the subject. A circle marks your chosen
   point. **Pointer held** or **Pointer released** confirms that the control was
   accepted. Release to stop.
8. Use **Apply prompt** to change the edit. Let recording finish to save the video.

For keyboard use, focus the output picture. Arrow keys position the pointer;
Hold Space to hold the pointer; release Space or press Escape to release it. The pointer also releases when the
picture loses focus. X2 applies controls to later groups of generated frames,
so motion may lag behind your input.

Camera frames use up to 640 × 480 pixels and at most ten new frames per second.
The connector repeats the latest frame on the model's 24 fps input. No microphone
audio is sent and no separate camera recording is saved.

**End session** discards the unfinished video. Closing the panel stops camera
access and causes the session to end. Losing camera input for three seconds also
ends the session. Check browser camera permissions and use localhost or HTTPS
if the camera cannot start.

The session time limit in Reactor settings applies during setup and generation.
If the session end is unconfirmed, wait for its stated time limit before trying
again. If camera access fails, check permissions for Comfy Desktop or your
browser and close other applications using the camera.

For current session rates, open **Extensions → Reactor → Reactor models**.

## Recording details

**recording details** describes the saved file, model, and timing. It does not
measure visual quality or billed time. ComfyUI can reuse a cached report; do not
run another paid generation solely to refresh it.
