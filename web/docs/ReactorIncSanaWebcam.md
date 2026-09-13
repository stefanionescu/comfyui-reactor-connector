# SANA: Edit Webcam Video (Reactor)

Turn your camera video into an edited scene and save the result without sound.
Use a local, single-user ComfyUI installation with camera access.
Your camera remains off until you enable it in the live panel.

## Inputs

| Input                            | What to provide                                                                                                 |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| edit prompt                      | Describe the edit in up to 20,000 characters. Leave empty to reconstruct the camera input.                      |
| video duration (seconds)           | Output length from 0.1 to 60 seconds, within your Reactor settings limit. Default: 5 seconds.                   |
| seed                             | Number from 0 to 4,294,967,295. Default: 42.                                                                    |
| run number                       | Change this value for another run. Default: 0.                                                                  |
| source refresh interval (chunks) | Return to the camera source after this many groups of generated frames. Use 0 to turn this off. Range: 0–1,000. |

## Run and save

1. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **sana-streaming-03-webcam** in **Browse Templates → reactor-inc**.
3. Describe an edit, such as “Turn the scene into a watercolor painting.”
4. Select **Run**, then **Enable Camera** in the live panel. Allow camera access.
5. Check the camera preview. To change cameras, choose one and select **Switch Camera**.
6. Select **Start Session** within 60 seconds.
7. To change the edit, enter a live prompt and select **Apply Prompt**.
8. Let recording finish. **Save Video** saves the result.

The node returns **video** without sound and **recording details** as text. SANA may take one
or more groups of frames to apply a prompt change. Camera frames use up to
640 × 480 pixels. The browser sends at most ten new frames per second, and
the connector repeats the latest frame on the model's 24 fps input.
It sends no microphone audio and stores no separate camera recording.

**End Session** discards the unfinished video. Camera input stops when the
panel closes or recording ends. Losing camera input for three seconds ends
the session. The session time limit also applies during setup and generation.

If camera access fails, use localhost or HTTPS, check camera permissions for Comfy Desktop or your browser, and
close other applications using the camera. This node requires a SANA deployment
with the `camera` video input. A deployment without that input cannot run it.

If the session end is unconfirmed, wait for its stated time limit before trying
again. Correct the reported error before starting another session.

For current session rates, open **Extensions → Reactor → Reactor models**.

## Recording details

**recording details** describes the saved file, model, and timing. It does not
measure visual quality or billed time. ComfyUI can reuse a cached report; do not
run another paid generation solely to refresh it.
