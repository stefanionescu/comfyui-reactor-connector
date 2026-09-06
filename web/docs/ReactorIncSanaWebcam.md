# Reactor SANA: Edit a webcam

Turn your camera video into an edited scene and save the result without sound.
Use a local, single-user ComfyUI installation with camera access.
Your camera remains off until you enable it in the live panel.

## Inputs

| Input | What to provide |
| --- | --- |
| Scene prompt | Describe the edit in up to 20,000 characters. Leave empty to reconstruct the camera input. |
| Video length (seconds) | Output length from 0.1 to 60 seconds, within your Reactor settings limit. Default: 5 seconds. |
| Seed | Number from 0 to 4,294,967,295. Default: 42. |
| Variation | Change this value for another paid run. Default: 0. |
| Anchor interval | Return to the camera source after this many groups of generated frames. Use 0 to turn this off. Range: 0–1,000. |

## Run and save

1. Open **sana-streaming-03-webcam** from the connector's templates.
2. Describe an edit, such as “Turn the scene into a watercolor painting.”
3. Select **Run**, then **Enable camera** in the live panel. Allow camera access.
4. Check the camera preview. To change cameras, choose one and select **Use selected camera**.
5. Select **Start session** within 60 seconds. This starts a paid Reactor session.
6. To change the edit, enter a live prompt and select **Apply prompt**.
7. Let recording finish. **Preview and save video** saves the result.

The node returns `VIDEO` and recording details as `STRING`. SANA may take one
or more groups of frames to apply a prompt change. Camera frames use up to
640 × 480 pixels. The browser sends at most ten new frames per second, and
the connector repeats the latest frame on the model's 24 fps input.
It sends no microphone audio and stores no separate camera recording.

**End session** discards the unfinished video. Camera input stops when the
panel closes or recording ends. Losing camera input for three seconds ends
the session. The session time limit also applies during setup and generation.

If camera access fails, use localhost or HTTPS, check camera permissions for Comfy Desktop or your browser, and
close other applications using the camera. This node requires a SANA deployment
with the `camera` video input. A deployment without that input cannot run it.

See the [live controls guide](/extensions/reactor-inc/guides/docs/live.html) for privacy and recovery steps.

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
