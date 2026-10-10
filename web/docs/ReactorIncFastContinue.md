# Fast H3: Continue a Scene (Reactor)

Makes several connected clips in one Reactor session and saves them as one video
with sound. Each clip starts from the previous clip's last frame.

## Inputs

| Input                   | What it takes                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------------- |
| scene prompt            | The opening scene and sound, 1 to 800 characters. Later clips without a prompt reuse it.      |
| clip duration (seconds) | Length of each clip, from 5.167 to 14.375 seconds. Default: 6. Fast H3 picks the nearest one. |
| seed                    | Integer from 0 to 4,294,967,295. Default: 42. Each later clip adds one.                       |
| run number              | Change it to run again with the same inputs.                                                  |
| aspect ratio            | `16:9`, `1:1`, `9:16`, or `4:3`. Default: `16:9`.                                             |
| number of clips         | From 2 to 8. Default: 3. Together the clips must be 60 seconds or less.                       |
| later clip prompts      | Optional. One prompt per line, starting with clip 2, each 1 to 800 characters.                |
| starting image          | Optional first frame for clip 1.                                                              |

The node builds one clip ahead while earlier clips play. If the next clip is
still building, the video holds the last frame, which can make it longer. Setup,
building, playback, and recording all count toward the session limit.

## Outputs

| Output | What it carries                         |
| ------ | --------------------------------------- |
| video  | All the clips as one video, with sound. |
| audio  | The same sound as 48 kHz samples.       |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **fast-h3-05-continue-scene** in **Browse Templates → reactor-inc**. To
   start from a picture, connect a **Load Image** node to **starting image**.
3. Set the opening prompt, the clip length and count, and any later prompts.
4. Check the maximum session duration in Reactor settings, then select **Run**.
5. Play the result in **Save Video**; **Save Audio** keeps the sound alone.

Saving needs one extra continuation of up to 14.375 seconds. It uses credits and
is not saved.

[Reactor Fast H3 schema](https://docs.reactor.inc/model-api-reference/fast-h3/schema)
