# Helios: Generate Video from a Prompt Sequence (Reactor)

Generate a Helios video with prompt changes prepared before the run. Use
**Helios: Add a Prompt (Reactor)** to build the sequence without writing commands.
You can also connect one starting image.

## Inputs

| Input                  | What to provide                                                                         |
| ---------------------- | --------------------------------------------------------------------------------------- |
| scene prompt           | The opening scene and motion, from 1 to 20,000 characters.                              |
| video duration (seconds) | Recording length. Default: 5 seconds. Reactor settings limit the maximum.               |
| seed                   | Integer from 0 to 4,294,967,295. Default: 42.                                           |
| run number             | Change this number for another run with the same other inputs. Default: 0.              |
| prompt sequence (JSON) | Connect the last Add a Prompt node. `[]` keeps only the opening prompt.                 |
| starting image         | Optional single RGB image. The same reference remains in place throughout the sequence. |

Give later prompts distinct, increasing chunk numbers. The sequence allows up
to 32 later prompts and 128 KB. The opening prompt is set at chunk zero. Each
Helios chunk contains 33 frames; chunk numbers are not seconds. The connector
sends all prompts before generation starts.

Choose a recording length that includes the changes you want. A prompt near the
end may have little visible effect, and a later prompt does not extend the file.
Use **helios-05-live-prompt** in **Browse Templates → reactor-inc** when you want to
choose changes while watching instead of preparing them in advance.

The text-sequence example starts on a forest path, adds sunlight at chunk 1,
and enters a clearing at chunk 3. Edit all three prompts to keep the scene
consistent. It records eight seconds; the optional image stays fixed.

## Run and save

1. Open **helios-03-prompt-sequence** or **helios-04-image-sequence** in
   **Browse Templates → reactor-inc**.
2. Edit the opening prompt, **1. Let Sunlight Through (Reactor)**, and **2. Enter a Clearing (Reactor)**. For the image
   example, upload your picture in **Load Starting Image**.
3. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
4. Select **Run**. Play the result in **Save Video**.

The node returns **video** without audio and **recording details** as text.
Connect **video** to ComfyUI's **Save Video** to keep the temporary result.
Seeds do not guarantee identical output after a provider update.

Recording stops at **video duration (seconds)**; the separate host session limit
also applies. Use ComfyUI's cancel control to stop a run. Closing the ComfyUI window
does not cancel it. The connector disconnects after recording or failure and
does not automatically retry an uncertain session.

## Recovery

An invalid sequence fails before connection. Connect the prompt builders in
order and use an opening prompt that describes the same scene. For image input,
provide one image within the upload limit; batches are not accepted.

If a change is missing, check its chunk number and the recording length. If
generation fails, correct the reported input error or check your connection and
Reactor account. If the session end is unconfirmed, wait for its stated time
limit before running again.

[Helios command reference](https://docs.reactor.inc/model-api-reference/helios/schema)

For current session rates, open **Extensions → Reactor → Reactor models**.

## Recording details

**recording details** describes the saved file, model, and timing. It does not
measure visual quality or billed time. ComfyUI can reuse a cached report; do not
run another paid generation solely to refresh it.
