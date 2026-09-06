# Reactor LTX: Make a portrait speak

Animate one portrait speaking a script. Connect **Load Image** to **Starting image**, **Video**
to **Save Video**, and **Audio** to **Save Audio (Advanced)**. The video includes
sound; the separate audio output lets you save or process the speech alone.

## Inputs

| Input | What to provide |
| --- | --- |
| Starting image | One clear RGB portrait, with the whole head visible in a wide frame. Required. |
| Scene prompt | Optional scene description, up to 800 characters. |
| Spoken words | Spoken words, from 1 to 10,000 characters. Required. |
| Video length (seconds) | Requested saved video length, at least 4 seconds and within the video duration limit in Reactor settings. Default: 5. |
| Words per minute | Speech pace. Default: 140. Reactor checks the supported range before generation. |
| Seed | Integer from 0 to 4,294,967,295. Default: 42. |
| Variation | Change this integer to request another paid run. Default: 0. |

Use a front-facing portrait of one person. LTX fits the picture to a wide canvas;
a tall portrait can lose the top of the head. Frame the image before uploading.
Image batches, invalid pixels, and files above the upload limit in Reactor settings are rejected
before connection. The image limit is 8192 pixels per side.

Keep the script short enough for the chosen duration. At 140 words per minute,
five seconds allows about 11 words. A longer script may be cut off. This node
sets an explicit take length; it does not infer a longer duration from the script.
The connector may generate up to twenty extra seconds so Reactor can finish
preparing the recording. Those seconds can use credits and are not saved.
The session time limit applies to the whole run.
The usual speech range is 80–220 words per minute. The range reported by the
connected model applies to your run.

## Run and save

1. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **ltx2-01-speaking-portrait** in the native Templates browser.
3. Upload a portrait in Load Image and edit **Spoken words**.
4. Select **Run**, then play the video and inspect the separate sound output.

The connector uploads the portrait and sends the script, speech pace, duration,
seed, and optional scene description before starting. These settings stay the
same throughout the run. Each run generates one video.

Native `VIDEO` contains H.264 video and AAC audio. Native `AUDIO` contains 48 kHz
mono or stereo samples. The **Recording details** output contains recording details. Both media outputs
use the provider recording timestamps, starting at the first video frame. Leading
audio is trimmed; a later audio start retains silence. Output ends at the requested
duration or the available video end. AAC decoding can include codec padding beyond
the exact length of the separate audio output.

## Cost, failures, and cancellation

Each new run uses Reactor credits. Connecting, setting up, and preparing the
recording can make session time longer than the saved video. The recording must
be ready within the session time limit in Reactor settings, even if generation
has finished. A timeout returns an error and
removes partial media. The connector never substitutes a silent video for a failed
recording.

Use ComfyUI's cancel control to stop. Closing a tab or pausing playback does not
end generation. Unchanged inputs may reuse the host cache. Change **Variation** for
another paid run; seeds do not guarantee identical output across model revisions.
The connector does not retry ambiguous session creation or model commands.

[Reactor LTX schema](https://docs.reactor.inc/model-api-reference/ltx/schema)

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
