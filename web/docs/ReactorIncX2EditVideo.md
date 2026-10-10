# X2: Edit Video (Reactor)

Edits a local video clip with Reactor's X2 model. A reference image can replace
or insert a subject, and you can drag on the output to steer it.

## Inputs

| Input                    | What it takes                                                                        |
| ------------------------ | ------------------------------------------------------------------------------------ |
| source video             | One SDR color clip with at least 33 frames, from **Load Video** or **Create Video**. |
| edit prompt              | The edit, 1 to 1,000 characters.                                                     |
| video duration (seconds) | Recording length, from 0.1 to 60 seconds. Default: 5.                                |
| run number               | Change it to run again with the same inputs. X2 has no seed.                         |
| keep queued frames       | On keeps source frames in order; off favors recent frames and less delay.            |
| hold pointer             | Hold the pointer at the position below for the whole run. Default: off.              |
| pointer x (0-1)          | Horizontal position: 0 is the left edge, 1 the right. Default: 0.5.                  |
| pointer y (0-1)          | Vertical position: 0 is the top edge, 1 the bottom. Default: 0.5.                    |
| reference image          | Optional. One RGB image of the subject to insert or replace.                         |
| live controls            | Change the prompt and drag the subject while it records. Default: off.               |

The clip must be MP4, MOV, WebM, or AVI, with even dimensions, at most 4,096
pixels per side, and 1 to 120 frames per second. HDR clips and clips with
several video streams are rejected. The connector sends a temporary video-only
copy of up to 60 seconds and stops if preparing it takes over 60 seconds. The
clip plays once at its own frame rate, then holds its last frame. With a
reference, describe what to replace and what to keep.

## Outputs

| Output | What it carries                  |
| ------ | -------------------------------- |
| video  | The edited video, without sound. |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **x2-01-edit-video**, **x2-02-reference-edit**, or **x2-04-live-prompt**
   in **Browse Templates → reactor-inc**, and upload a clip in **Load Source
   Video**.
3. Keep the example prompt for a first run and select **Run**.
4. Play the result in **Save Video**, which also saves the file.

## Live controls

Turn **live controls** on, select **Run**, then select **Start Session** in the
live panel within 60 seconds. **Apply Prompt** changes later frames. Drag on the
output to steer the subject; a circle marks the point, and **Pointer held** or
**Pointer released** confirms each change. With the keyboard, focus the picture,
move the pointer with the arrow keys, and hold Space; Escape or leaving the
picture releases it. X2 works on groups of frames, so changes can lag. Let
recording finish to save the result; **End Session** discards it.

[Reactor X2 schema](https://docs.reactor.inc/model-api-reference/x2/schema)
