# Fast H3: Generate Video (Reactor)

Generates one clip with sound from Reactor's Fast H3 model. Optional images set
the first and last frames.

## Inputs

| Input                    | What it takes                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------- |
| scene prompt             | The scene, motion, and sound, up to 800 characters.                                               |
| video duration (seconds) | Clip length, from 5.167 to 14.375 seconds. Default: 6. Fast H3 picks the nearest length it takes. |
| seed                     | Integer from 0 to 4,294,967,295. Default: 42.                                                     |
| run number               | Change it to run again with the same inputs.                                                      |
| aspect ratio             | `16:9`, `1:1`, `9:16`, or `4:3`. Default: `16:9`.                                                 |
| starting image           | Optional first frame.                                                                             |
| final image              | Optional last frame, with or without a first frame.                                               |

Each image is one RGB frame, at most 8,192 pixels per side and within the upload
limit in Reactor settings. The model fits images to its canvas, so images in the
chosen shape crop less. If the length Fast H3 accepts does not fit the session
limit, the run stops before playback.

## Outputs

| Output | What it carries                   |
| ------ | --------------------------------- |
| video  | The clip, with sound.             |
| audio  | The same sound as 48 kHz samples. |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **fast-h3-01-text-to-video**, **fast-h3-02-image-to-video**, or
   **fast-h3-03-first-and-last-frames** in **Browse Templates → reactor-inc**.
3. Describe the scene, motion, and sound, then select **Run**.
4. Play the result in **Save Video**; **Save Audio** keeps the sound alone.

Saving needs one extra continuation of up to 14.375 seconds. It uses credits and
is not saved.

[Reactor Fast H3 schema](https://docs.reactor.inc/model-api-reference/fast-h3/schema)
