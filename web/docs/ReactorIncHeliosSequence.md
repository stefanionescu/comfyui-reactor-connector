# Reactor Helios: Generate Video from a Prompt Sequence

Generate a Helios video with prompt changes prepared before the run. Use
**Reactor Helios: Add a Prompt** to build the sequence without writing commands.
You can also connect one starting image.

## Inputs

| Input                  | What to provide                                                                         |
| ---------------------- | --------------------------------------------------------------------------------------- |
| Scene prompt           | The opening scene and motion, from 1 to 20,000 characters.                              |
| Video length (seconds) | Recording length. Default: 5 seconds. Reactor settings limit the maximum.               |
| Seed                   | Integer from 0 to 4,294,967,295. Default: 42.                                           |
| Run number             | Change this number for another run with the same other inputs. Default: 0.              |
| Prompt sequence (JSON) | Connect the last Add a Prompt node. `[]` keeps only the opening prompt.                 |
| Starting image         | Optional single RGB image. The same reference remains in place throughout the sequence. |

Give later prompts distinct, increasing chunk numbers. The sequence allows up
to 32 later prompts and 128 KB. The opening prompt is set at chunk zero. Each
Helios chunk contains 33 frames; chunk numbers are not seconds. The connector
sends all prompts before generation starts.

Choose a recording length that includes the changes you want. A prompt near the
end may have little visible effect, and a later prompt does not extend the file.
Use **helios-05-live-prompt** in native **Browse Templates → reactor-inc** when you want to
choose changes while watching instead of preparing them in advance.

The text-sequence example starts on a forest path, adds sunlight at chunk 1,
and enters a clearing at chunk 3. Edit all three prompts to keep the scene
consistent. It records eight seconds; the optional image stays fixed.

## Run and save

1. Open **helios-03-prompt-sequence** or **helios-04-image-sequence** in native
   **Browse Templates → reactor-inc**.
2. Edit the opening prompt and both later prompt builders. For the image
   example, upload your picture in **Upload Your Starting Image**.
3. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
4. Select **Run**. Play the result in **Preview and Save Video**.

The node returns native `VIDEO` without audio and recording details as `STRING`.
Connect **Video** to ComfyUI's **Save Video** to keep the temporary result.
Seeds do not guarantee identical output after a provider update.

Recording stops at **Video length (seconds)**; the separate host session limit
also applies. Use ComfyUI's cancel control to stop a run. Closing the ComfyUI window
does not cancel it. The connector disconnects after recording or failure and
does not automatically retry an uncertain session.

## Recovery

An invalid sequence fails before connection. Connect the prompt builders in
order and use an opening prompt that describes the same scene. For image input,
provide one image within the upload limit; batches are not accepted.

If a change is missing, check its chunk number and the recording length. If
generation fails, read the reported error and troubleshooting guide (**Recovery** in the bundled `ADVANCED.md`)
before running again.

[Helios command reference](https://docs.reactor.inc/model-api-reference/helios/schema)

Select **View credit rate** for a session estimate (**Credit rates** in the bundled `ADVANCED.md`).

## Recording details

This output describes the saved file and model. See the
field reference (**Recording details** in the bundled `ADVANCED.md`) for timing, privacy, and cache behavior.
