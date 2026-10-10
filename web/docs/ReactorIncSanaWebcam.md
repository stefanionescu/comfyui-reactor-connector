# SANA: Edit Webcam Video (Reactor)

Edits your camera video live with Reactor's SANA model and saves the result
without sound. It needs a local, single-user ComfyUI with camera access, and the
camera stays off until you turn it on in the live panel.

## Inputs

| Input                            | What it takes                                                           |
| -------------------------------- | ----------------------------------------------------------------------- |
| edit prompt                      | The edit, up to 20,000 characters. Empty reconstructs the camera input. |
| video duration (seconds)         | Recording length, from 0.1 to 60 seconds. Default: 5.                   |
| seed                             | Integer from 0 to 4,294,967,295. Default: 42.                           |
| run number                       | Change it to run again with the same inputs.                            |
| source refresh interval (chunks) | Return to the camera after this many chunks of frames; 0 turns it off.  |

The browser sends up to ten frames per second at up to 640 × 480 pixels, and the
connector repeats the latest frame on the model's 24 fps input. No microphone
sound is sent and no camera recording is kept. The session ends after three
seconds without a new camera frame. The SANA deployment must offer a `camera`
video input.

## Outputs

| Output | What it carries                  |
| ------ | -------------------------------- |
| video  | The edited video, without sound. |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **sana-streaming-03-webcam** in **Browse Templates → reactor-inc** and
   describe an edit, such as “Turn the scene into a watercolor painting.”
3. Select **Run**, then **Enable Camera** in the live panel and allow access. To
   change cameras, choose one and select **Switch Camera**.
4. Select **Start Session** within 60 seconds. **Apply Prompt** changes the edit.
5. Let recording finish; **Save Video** saves the result. **End Session**
   discards it.

If the camera does not start, use localhost or HTTPS, check camera permissions
for Comfy Desktop or your browser, and close other apps using the camera.

[Reactor SANA schema](https://docs.reactor.inc/model-api-reference/sana-streaming/schema)
