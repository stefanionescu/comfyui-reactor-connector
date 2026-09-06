# Reactor Fast H3: Continue a scene

Create several connected clips in one Reactor session and save one video with
sound. Each clip starts from the previous clip's final frame. Choose a clip count
so the session has a clear stopping point.

## Inputs

| Input | What to provide |
| --- | --- |
| Scene prompt | Opening scene and sound, using 1 to 800 characters. Also used for later clips without their own prompt. |
| Clip length (seconds) | Requested length of each clip: 5.167–14.375 seconds. Default: 6. Fast H3 chooses the nearest supported length. |
| Seed | Starting number from 0 to 4,294,967,295. Each later clip adds one, wrapping to zero at the upper limit. Default: 42. |
| Variation | Change this value for another paid run. Default: 0. |
| Aspect ratio | Frame shape: 16:9, 1:1, 9:16, or 4:3. Default: 16:9. |
| Number of clips | Total clips, from 2 to 8. Default: 3. Their combined length must fit your video duration limit. |
| Later prompts | Optional prompts, one per line, starting with clip 2. Each line allows 1 to 800 characters. Leave empty to repeat the opening prompt. |
| Starting image | Optional RGB first frame for clip 1. Connect Load Image. |

## Run and save

1. Open **fast-h3-05-continue-scene** or **fast-h3-06-continue-image** from Templates.
2. Set the opening prompt. For the image example, upload a starting image.
3. Choose a clip length and count. The examples request three clips of about six seconds.
4. Enter later prompts if you want the scene to change between clips.
5. Check the video duration and session limits in Reactor settings, then select **Run**.
6. **Preview and save video** saves the sequence with sound. **Preview and save sound** saves a separate audio file.

The node returns `VIDEO`, `AUDIO`, and recording details as `STRING`. It queues
one continuation ahead while earlier clips play. If the next clip is still
building, the output holds the previous frame. That wait can lengthen the saved
video. Allow room in your video duration limit for these waits.

Fast H3 also builds up to 14.375 seconds of continuation to finish the recording.
Those extra seconds use credits and are not included in the saved result.
Setup, clip building, playback, and recording cleanup all count toward the session
limit. A timeout discards the unfinished video; the connector does not start a
replacement session automatically.

Use ComfyUI's cancel control to stop early. Closing the ComfyUI window does not cancel
this ordinary workflow. The prompts and clip count are fixed when you select Run.

## Check the credit rate

Select **View credit rate** on this node to open its model rate. The time starts with this node's requested video length. Enter a different session
time to include setup or other paid time. Session time includes setup and can
exceed the saved video length. This calculation does not limit spending.
Open **ComfyUI menu → Extensions → Reactor → Reactor models** and select **Refresh models** for current rates. See [settings](../settings.md#check-the-credit-rate)
for details.

## Recording details

The **Recording details** output identifies the model and describes the saved file. See
[recording details](../recording-details.md) for dimensions, duration, audio
presence, and cache behavior. It contains no prompts or session credentials.
