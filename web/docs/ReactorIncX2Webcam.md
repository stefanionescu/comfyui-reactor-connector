# X2: Edit Webcam Video (Reactor)

Edits your camera video live with Reactor's X2 model, and you drag on the output
to steer the subject. It saves the result without sound. It needs a local,
single-user ComfyUI with camera access, and the camera stays off until you turn
it on in the live panel.

## Inputs

| Input                    | What it takes                                                |
| ------------------------ | ------------------------------------------------------------ |
| edit prompt              | The edit, 1 to 1,000 characters.                             |
| video duration (seconds) | Recording length, from 0.1 to 60 seconds. Default: 10.       |
| run number               | Change it to run again with the same inputs. X2 has no seed. |
| reference image          | Optional. One RGB image of a subject to insert or replace.   |

The browser sends up to ten frames per second at up to 640 × 480 pixels, and the
connector repeats the latest frame on the model's 24 fps input. No microphone
sound is sent and no camera recording is kept. The session ends after three
seconds without a new camera frame. The reference image stays fixed.

## Outputs

| Output | What it carries                  |
| ------ | -------------------------------- |
| video  | The edited video, without sound. |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **x2-03-webcam** in **Browse Templates → reactor-inc** and describe the
   edit.
3. Select **Run**, then **Enable Camera** in the live panel and allow access. To
   change cameras, choose one and select **Switch Camera**.
4. Select **Start Session** within 60 seconds.
5. Drag on the output to steer the subject; a circle marks the point, and
   **Pointer held** or **Pointer released** confirms each change. **Apply
   Prompt** changes the edit.
6. Let recording finish; **Save Video** saves the result. **End Session**
   discards it.

With the keyboard, focus the picture, move the pointer with the arrow keys, and
hold Space; Escape or leaving the picture releases it. X2 works on groups of
frames, so changes can lag. If the camera does not start, use localhost or
HTTPS, check camera permissions, and close other apps using the camera.

[Reactor X2 schema](https://docs.reactor.inc/model-api-reference/x2/schema)
