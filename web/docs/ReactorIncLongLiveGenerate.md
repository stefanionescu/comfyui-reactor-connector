# LongLive: Generate Video (Reactor)

Generates a video from an opening shot prompt with Reactor's LongLive model. You
can schedule later shots and cuts, or change the prompt while it records.

## Inputs

| Input                    | What it takes                                                                          |
| ------------------------ | -------------------------------------------------------------------------------------- |
| scene prompt             | The opening scene and motion, 1 to 20,000 characters.                                  |
| video duration (seconds) | Recording length, up to 60 seconds. Default: 5.                                        |
| seed                     | Integer from 0 to 4,294,967,295. Default: 42.                                          |
| run number               | Change it to run again with the same inputs.                                           |
| shots (JSON)             | Optional. Connect the last **LongLive: Add a Shot** node. `[]` keeps the opening shot. |
| live controls            | Change the prompt while it records. Off by default; not with scheduled shots.          |

A soft transition changes the prompt within the scene; a cut starts a new scene.
LongLive counts in chunks of 29 frames, about 1.2 seconds. Give each later shot
a larger chunk number, starting at 1. Up to 32 later shots fit in 128 KB, and a
later shot does not extend the recording. This model takes no starting image.

## Outputs

| Output | What it carries                    |
| ------ | ---------------------------------- |
| video  | The recorded video, without sound. |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **longlive-v2-01-text-to-video**, **longlive-v2-02-storyboard**, or
   **longlive-v2-03-live-prompt** in **Browse Templates → reactor-inc**.
3. Describe the opening shot, choose the length, and select **Run**.
4. Play the result in **Save Video**, which also saves the file.

## Live controls

Turn **live controls** on, select **Run**, then select **Start Session** in the
live panel within 60 seconds. **Apply Prompt** changes later frames with a soft
transition. Let recording finish to save the result; **End Session** discards
it. Closing the panel or losing its browser connection ends the session. The
preview has no sound, and panel changes do not rewrite the saved workflow.

[LongLive schema](https://docs.reactor.inc/model-api-reference/longlive-v2/schema)
