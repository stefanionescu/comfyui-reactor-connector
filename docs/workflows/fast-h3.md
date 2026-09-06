# Make a Fast H3 clip

Open the native Templates browser and choose **reactor-inc**. These
examples use core ComfyUI nodes and the installed Reactor connector.

## Start from text

1. Open **fast-h3-01-text-to-video**.
2. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
3. Keep the six-second request for the first run. Describe visible motion and sound.
4. Select **Run**. The clip must finish building before playback begins.
5. Review **Preview and save video** and **Preview and save sound**.

The saved length follows the model's accepted duration, which can differ from
the requested value. The video contains sound. The separate audio output lets
you save a lossless audio file or connect other audio processing nodes.

The connector also builds an additional continuation to let the recording service
finish the selected clip. That extra generation uses credits and is not saved.
The same session cap still applies to setup, both builds, playback, and recording.
The continuation requests the deployment's maximum clip length, currently 14.375 seconds.

## Start or end with an image

1. Open **fast-h3-02-image-to-video** for a first frame,
   **fast-h3-03-first-and-last-frames** for both frames, or
   **fast-h3-04-ending-frame** for the final frame alone.
2. Upload the first picture in **Upload your starting image**, when that node is present.
3. Describe how the picture should move and what should be heard.
4. Upload the last picture in **Choose the final frame**, when that node is present.
   The first-frame example can also accept a second Load Image connected to **Final image**.
5. Select **Run** and review the first and last frames as well as sound.

Use images with the selected canvas shape. The model can crop or resize them.
The final image can also be used alone by disconnecting the starting image.

## Recover from a failed run

Read the node error before running again. If the model chooses a clip length
above the host limit, request a shorter clip. Build and recording timeouts still use
credits. Use ComfyUI's cancel control when you want to stop; closing the workflow
tab does not stop its session.

The first four examples produce one clip per run. To connect several clips,
open [Continue a scene](../../workflows/fast-h3/fast-h3-05-continue-scene.json) or
[Continue from an image](../../workflows/fast-h3/fast-h3-06-continue-image.json).
Set **Number of clips** and put one prompt per line in **Later prompts**.
The examples request three six-second clips. Check that **Maximum video duration
(seconds)** in Reactor settings allows at least 18 seconds. The model may round
each clip up; allow for its accepted length as well.
The output combines the clips into one video with sound. See the
[continued-scene guide](../nodes/ReactorIncFastContinue.md) for length and cost limits.


See the [workflow index](../../workflows/README.md) for every example, including
[live controls](../live.md).
