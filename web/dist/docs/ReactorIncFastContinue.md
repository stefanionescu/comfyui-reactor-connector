# Reactor Fast H3: Continue a Scene

Create several connected clips in one Reactor session and save one video with
sound. Each clip starts from the previous clip's final frame. Choose a clip count
so the session has a clear stopping point.

## Inputs

| Input                 | What to provide                                                                                                                       |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Scene prompt          | Opening scene and sound, using 1 to 800 characters. Also used for later clips without their own prompt.                               |
| Clip length (seconds) | Requested length of each clip: 5.167–14.375 seconds. Default: 6. Fast H3 chooses the nearest supported length.                        |
| Seed                  | Starting number from 0 to 4,294,967,295. Each later clip adds one, wrapping to zero at the upper limit. Default: 42.                  |
| Run number            | Change this value for another run. Default: 0.                                                                                        |
| Aspect ratio          | Frame shape: 16:9, 1:1, 9:16, or 4:3. Default: 16:9.                                                                                  |
| Number of clips       | Total clips, from 2 to 8. Default: 3. Their combined length must fit your video duration limit.                                       |
| Later prompts         | Optional prompts, one per line, starting with clip 2. Each line allows 1 to 800 characters. Leave empty to repeat the opening prompt. |
| Starting image        | Optional RGB first frame for clip 1. Connect Load Image.                                                                              |

## Run and save

1. Open **fast-h3-05-continue-scene** or **fast-h3-06-continue-image** from Templates.
2. Set the opening prompt. For the image example, upload a starting image.
3. Choose a clip length and count. The examples request three clips of about six seconds.
4. Enter later prompts if you want the scene to change between clips.
5. Check the video duration and session limits in Reactor settings, then select **Run**.
6. **Preview and Save Video** saves the sequence with sound. **Preview and Save Audio** saves a separate audio file.

The node returns `VIDEO`, `AUDIO`, and recording details as `STRING`. It queues
one continuation ahead while earlier clips play. If the next clip is still
building, the output holds the previous frame. That wait can lengthen the saved
video. Allow room in your video duration limit for these waits.

See [recording overhead](/reactor-inc/v1/help/ADVANCED.html#recording-overhead) for the additional
continuation needed to finish saving.
Setup, clip building, playback, and recording cleanup all count toward the session
limit. A timeout discards the unfinished video; the connector does not start a
replacement session automatically.

Use ComfyUI's cancel control to stop early. Closing the ComfyUI window does not cancel
this ordinary workflow. The prompts and clip count are fixed when you select Run.

Select **View credit rate** for a [session estimate](/reactor-inc/v1/help/ADVANCED.html#credit-rates).

## Recording details

This output describes the saved file and model. See the
[field reference](/reactor-inc/v1/help/ADVANCED.html#recording-details) for timing, privacy, and cache behavior.
