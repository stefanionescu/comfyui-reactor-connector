# Helios: Generate Video (Reactor)

Generates a video from a prompt with Reactor's Helios model. You can start from
an image, schedule later prompts, or change the prompt while it records.

## Inputs

| Input                    | What it takes                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------------- |
| scene prompt             | The opening scene and motion, 1 to 20,000 characters.                                    |
| video duration (seconds) | Recording length, from 0.1 to 60 seconds. Default: 5.                                    |
| seed                     | Integer from 0 to 4,294,967,295. Default: 42.                                            |
| run number               | Change it to run again with the same inputs.                                             |
| prompt sequence (JSON)   | Optional. Connect the last **Helios: Add a Prompt** node. `[]` keeps the opening prompt. |
| starting image           | Optional. One RGB image, applied with the prompt. Reactor may crop or resize it.         |
| live controls            | Change the prompt while it records. Off by default; not with a prompt sequence.          |

Later prompts need increasing chunk numbers; the opening prompt is chunk 0. A
Helios chunk is 33 frames, not a second. A sequence holds up to 32 later prompts
and 128 KB, and a later prompt does not extend the recording. A starting image
must be at most 8,192 pixels per side and within the upload limit in Reactor
settings. Describe what is already in the image and how it should move.

## Outputs

| Output | What it carries                    |
| ------ | ---------------------------------- |
| video  | The recorded video, without sound. |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **helios-01-text-to-video**, **helios-02-image-to-video**,
   **helios-03-prompt-sequence**, or **helios-05-live-prompt** in **Browse
   Templates → reactor-inc**.
3. Describe the scene, choose the length, and select **Run**.
4. Play the result in **Save Video**, which also saves the file.

## Live controls

Turn **live controls** on, select **Run**, then select **Start Session** in the
live panel within 60 seconds. **Apply Prompt** changes later frames. Let
recording finish to save the result; **End Session** discards it. Closing the
panel or losing its browser connection ends the session. The preview has no
sound, and panel changes do not rewrite the saved workflow.

[Reactor Helios reference](https://docs.reactor.inc/model-api-reference/helios/overview)
