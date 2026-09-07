# Reactor Fast H3: Generate Video

Build one video clip with sound. Connect **Video** to **Save Video** and **Audio**
to **Save Audio (Advanced)**. Optional images can set its first and last frames.

## Inputs

| Input                  | What to provide                                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Scene prompt           | Required scene and sound description, up to 800 characters.                                                              |
| Video length (seconds) | Requested clip length, from 5.167 to 14.375 seconds and within the video duration limit in Reactor settings. Default: 6. |
| Seed                   | Integer from 0 to 4,294,967,295. Default: 42.                                                                            |
| Variation              | Change this integer for another paid run. Default: 0.                                                                    |
| Aspect ratio           | Canvas shape: 16:9, 1:1, 9:16, or 4:3. Default: 16:9.                                                                    |
| Starting image         | Optional first frame from Load Image.                                                                                    |
| Final image            | Optional last frame from a second Load Image.                                                                            |

Each image must contain one RGB frame within the upload limit in Reactor settings and 8192 pixels
per side. The model fits images to its canvas. Use matching image shapes to reduce
cropping. You can provide the first frame, the last frame, both, or neither.
Prepare pictures with the selected shape when preserving proportions matters.

Fast H3 chooses a supported duration near your request. Its accepted duration
governs the saved clip. If that duration exceeds the host limit, the connector
ends the session before playback and reports an error. Choose a shorter request
with room below the limit. A previously unused length may take longer to build.

## Run and save

1. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **fast-h3-01-text-to-video** in the native Templates browser.
3. Describe the scene, motion, and sound in **Scene prompt**.
4. Select **Run**. Wait for the clip to build, play, and become available for saving.
5. Play the saved video and separate sound output.

Use **fast-h3-02-image-to-video** for a starting picture. Add a second Load Image
and connect it to **Final image** to set the final frame. Node help remains local
and does not require a Reactor connection.

Use **fast-h3-03-first-and-last-frames** for a prepared two-image graph, or
**fast-h3-04-ending-frame** to set only the final picture.

The saved result contains the selected clip without the idle video shown before
it. Video and sound use the same recording times to stay aligned. Native `VIDEO` contains
H.264 video and AAC sound; native `AUDIO` contains 48 kHz samples. AAC decoding
can include padding beyond the separate audio output's exact duration.

After the selected clip finishes, the connector builds and starts one additional
continuation. This advances the recording service so it can finish the selected
clip's media fragments. The continuation uses credits but is omitted from the
saved output. Its requested length is the deployment's longest clip, currently
14.375 seconds. The session ends as soon as the selected recording is ready,
even if that continuation has not finished. The host session cap still applies.

## Cost, failures, and cancellation

Every new execution uses Reactor credits. Building and recording readiness can
take longer than playback. The host session cap includes all those stages. If
the clip or recording is not ready in time, the node fails and removes partial
media. It does not retry an ambiguous queue or playback command.

Use ComfyUI's cancel control to end the session. Closing a tab or pausing
a preview does not cancel. Unchanged inputs can reuse ComfyUI's cache. Change
**Variation** to run again. A seed cannot guarantee identical results after provider
model updates.

[Reactor Fast H3 schema](https://docs.reactor.inc/model-api-reference/fast-h3/schema)

## Credit rate

Select **View credit rate** to calculate a rate for your chosen session time.
Setup can add paid time beyond the video length; this is not a spending limit.
See [credit rates](../../ADVANCED.md#credit-rates).

## Recording details

This output describes the saved file and model. See the
[field reference](../../ADVANCED.md#recording-details) for timing, privacy, and cache behavior.
