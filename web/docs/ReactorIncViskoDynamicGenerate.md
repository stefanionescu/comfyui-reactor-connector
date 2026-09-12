# Reactor Visko Dynamic: Generate Video

Generate a scene with synchronized sound. Connect **Video** to native **Save Video**
and **Audio** to **Save Audio (Advanced)**. To animate an existing picture, connect
one **Load Image** output to the optional **Starting image** input.

## Inputs

| Input                  | What to provide                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| Scene prompt           | Describe the scene in 1 to 20,000 characters. This is the connector's input limit.               |
| Video length (seconds) | Requested output length within the video duration limit in Reactor settings. Default: 5 seconds. |
| Seed                   | Integer from 0 to 4,294,967,295. Default: 42.                                                    |
| Run number             | Change this integer for another run. Default: 0.                                                 |
| Sound prompt           | A short description of sound, up to 1,000 characters. Blank uses the picture alone.              |
| Resolution             | Leave blank to use the model default. See the resolution guidance below for custom names.        |
| Include sound          | Generate sound when true. False asks the model to provide silence. Default: true.                |
| Use prompt unchanged   | Send your exact scene prompt when true. False lets Reactor rewrite it first.                     |
| Starting image         | Optional single RGB image, at most 8192 pixels per side and within the upload limit.             |
| Live controls          | Open live controls in the ComfyUI window that runs the workflow. Default: false.                 |

Describe instruments, voices, materials, or ambience in **Sound prompt**. Keep it
to about one sentence: the provider uses roughly the first 128 tokens. An audio
prompt is not another scene description. Image batches and non-finite pixels are
rejected before connecting.

Leave **Resolution** blank for the model default. For a custom value, check the
[Visko Dynamic resolution reference](https://docs.reactor.inc/model-api-reference/visko-orbis-dynamic/schema) and use an exact name supported
by your deployment. The connector checks that name against the connected
model's offered resolutions before generation. An unsupported name ends the
session. Resolution stays fixed throughout the recording.

## Run and save

1. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **visko-dynamic-01-text-to-video** in **Browse Templates → reactor-inc**.
3. Describe a scene and its sound, then select **Run**.
4. Play the result in **Preview and Save Video**. Use **Preview and Save Audio**
   to inspect or retain sound alone.

To start from an image, open **visko-dynamic-02-image-to-video** and upload one
starting picture in **Upload Your Starting Image**. Describe the subject and
how it should move.
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

Preparing the recording can add time after generation. The session must
finish within the limit in Reactor settings. If recording fails, the node
returns an error and removes unfinished files.

## Stop and recover

Use ComfyUI's cancel control to stop a queued or running workflow. Pausing video
playback does not stop generation. With **Live controls** off, closing the browser
does not cancel the workflow. With live controls on, closing the live panel or
losing its browser connection ends the session and discards unfinished video.

Unchanged inputs may reuse ComfyUI's cached result. Change **Run number** for
another generation. If the session limit expires before recording is ready,
try a shorter video or increase **Maximum session duration (seconds)** in Reactor
settings. Correct reported input errors before trying again. If the session end
is unconfirmed, wait for its stated time limit before starting another run.

[Reactor Visko Dynamic schema](https://docs.reactor.inc/model-api-reference/visko-orbis-dynamic/schema)

## Live controls

Turn **Live controls** on, select **Run**, then select **Start session** in the
live panel within 60 seconds. Use **Apply prompt** to change later frames.
When sound is enabled, use **Apply sound prompt** to change later sound. Leave
it blank to let the picture guide sound. The preview is silent; play the saved
video to hear the result. Sound on/off and resolution stay fixed for the recording.
Let recording finish to save the result. **End session** discards the unfinished
video. Panel prompt changes do not rewrite the saved workflow.

For current session rates, open **Extensions → Reactor → Reactor models**.

## Recording details

**Recording details** describes the saved file, model, and timing. It does not
measure visual quality or billed time. ComfyUI can reuse a cached report; do not
run another paid generation solely to refresh it.
