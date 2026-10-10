# SANA: Edit Video (Reactor)

Applies an edit prompt to a local video clip with Reactor's SANA model. You can
change the prompt while it records.

## Inputs

| Input                            | What it takes                                                                             |
| -------------------------------- | ----------------------------------------------------------------------------------------- |
| source video                     | One SDR color clip with at least 33 frames, from **Load Video** or **Create Video**.      |
| edit prompt                      | The change to apply, up to 20,000 characters. Empty recreates the source without an edit. |
| video duration (seconds)         | Longest output, up to 60 seconds. Default: 5.                                             |
| seed                             | Integer from 0 to 4,294,967,295. Default: 42.                                             |
| run number                       | Change it to run again with the same inputs.                                              |
| source refresh interval (chunks) | Return to the source after this many chunks of frames; 0 turns it off. Default: 0.        |
| live controls                    | Change the prompt while it records. Default: off.                                         |

The clip must be MP4, MOV, WebM, or AVI, with even dimensions, at most 4,096
pixels per side, and 1 to 120 frames per second. HDR clips and clips with
several video streams are rejected. The connector sends a temporary video-only
copy of up to 60 seconds, without sound or metadata, and stops if preparing it
takes over 60 seconds. The clip plays once; after its last frame SANA keeps the
last input frame. The output can be shorter than requested.

## Outputs

| Output | What it carries                  |
| ------ | -------------------------------- |
| video  | The edited video, without sound. |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **sana-streaming-01-edit-video** or **sana-streaming-02-live-prompt** in
   **Browse Templates → reactor-inc**, and upload a clip in **Load Source Video**.
3. Describe the edit, such as “Change the scene to a soft watercolor painting.
   Keep the movement and composition.”, then select **Run**.
4. Play the result in **Save Video**, which also saves the file.

Start with a three- to five-second landscape clip. An empty prompt shows SANA's
reconstruction, which helps judge an edit.

## Live controls

Turn **live controls** on, select **Run**, then select **Start Session** in the
live panel within 60 seconds. **Apply Prompt** changes later frames. Let
recording finish to save the result; **End Session** discards it. The preview has
no sound, and panel changes do not rewrite the saved workflow.

[Reactor SANA schema](https://docs.reactor.inc/model-api-reference/sana-streaming/schema)
