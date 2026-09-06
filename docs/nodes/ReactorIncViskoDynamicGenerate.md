# Reactor Visko Dynamic: Generate video

Generate a scene with synchronized sound. Connect **Video** to native **Save Video**
and **Audio** to **Save Audio (Advanced)**. To animate an existing picture, connect
one **Load Image** output to the optional **Starting image** input.

## Inputs

| Input | What to provide |
| --- | --- |
| Scene prompt | Describe the scene in 1 to 20,000 characters. This is the connector's input limit. |
| Video length (seconds) | Requested output length within the video duration limit in Reactor settings. Default: 5 seconds. |
| Seed | Integer from 0 to 4,294,967,295. Default: 42. |
| Variation | Change this integer for another paid run. Default: 0. |
| Sound prompt | A short description of sound, up to 1,000 characters. Blank uses the picture alone. |
| Resolution | Blank uses the model default. Otherwise, enter an exact offered resolution name. |
| Include sound | Generate sound when true. False asks the model to provide silence. Default: true. |
| Use prompt unchanged | Send your exact scene prompt when true. False lets Reactor rewrite it first. |
| Starting image | Optional single RGB image, at most 8192 pixels per side and within the upload limit. |
| Live controls | Open live controls in the ComfyUI window that runs the workflow. Default: false. |

Describe instruments, voices, materials, or ambience in **Sound prompt**. Keep it
to about one sentence: the provider uses roughly the first 128 tokens. An audio
prompt is not another scene description. Image batches and non-finite pixels are
rejected before connecting.

If you enter a resolution, the connector checks that the connected model supports
it. An unsupported name ends the session before generation, but connection time
can still use credits. Leave this field blank for a first run. The resolution
stays the same throughout the run.

## Run and save

1. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **visko-dynamic-01-text-to-video** in the native Templates browser.
3. Describe a scene and its sound, then select **Run**.
4. Play the saved video with sound. Use Save Audio to inspect or retain sound alone.

To start from an image, open **visko-dynamic-02-image-to-video** and upload one
starting picture. Describe what is in that picture and how it should move.
The example prompt describes a forest path. Replace it when you use another
subject. **Use prompt unchanged** is on in the image example, so Reactor does
not rewrite your scene description. The empty sound prompt lets the picture
guide the sound.

The connector checks the image, sound, and resolution settings reported when
Visko starts. If they differ from your choices, it stops the run. These checks
do not guarantee that the generated scene follows your prompt or image.

The saved video includes sound. The separate audio output contains the same
recording's sound at 48 kHz. Both use the recording's timestamps to stay aligned.
The result ends at the requested duration or the available video's end.

Preparing the recording can add paid time after generation. The session must
finish within the limit in Reactor settings. If recording fails, the node
returns an error and removes unfinished files.

## Cost and cancellation

A new execution uses Reactor credits. Session time includes connection, setup,
generation, and recording readiness; it can exceed the saved video's duration.
The configured session time limit applies throughout. Pausing playback or closing
the ComfyUI window does not stop generation. Use ComfyUI's cancel control to stop.

Unchanged inputs may reuse ComfyUI's cache. Change **Variation** for another paid
run. A seed does not guarantee identical results across model updates.
The connector does not automatically retry failed commands or uncertain sessions.

If the session reaches its limit before recording is ready, try a shorter recording
or review the host's session limit and expected cost. If a recording is unavailable,
check provider status before deciding whether to retry. A larger limit must remain
within your own cost constraints.

[Reactor Visko Dynamic schema](https://docs.reactor.inc/model-api-reference/visko-orbis-dynamic/schema)


## Live controls

Turn **Live controls** on, select **Run**, then select **Start session** in the
live panel within 60 seconds. Use **Apply prompt** to change later frames.
When sound is enabled, use **Apply sound prompt** to change later sound. Leave
it blank to let the picture guide sound. The preview is silent; play the saved
video to hear the result. Sound on/off and resolution stay fixed for the recording.
Let recording finish to save the result. **End session** discards the unfinished
video. Panel prompt changes do not rewrite the saved workflow.

See the [live controls guide](../../docs/live.md) for input, privacy, and stopping rules.

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
