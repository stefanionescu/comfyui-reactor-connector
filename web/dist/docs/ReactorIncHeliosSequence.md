# Reactor Helios: Generate a Prompt Sequence

Generate a Helios video with prompt changes prepared before the run. Use
**Reactor Helios: Add a prompt** to build the sequence without writing commands.
You can also connect one starting image.

## Inputs

| Input                  | What to provide                                                                         |
| ---------------------- | --------------------------------------------------------------------------------------- |
| Scene prompt           | The opening scene and motion, from 1 to 20,000 characters.                              |
| Video length (seconds) | Recording length. Default: 5 seconds. Reactor settings limit the maximum.               |
| Seed                   | Integer from 0 to 4,294,967,295. Default: 42.                                           |
| Variation              | Change this number for another paid run with the same other inputs. Default: 0.         |
| Prompt sequence (JSON) | Connect the last Add a prompt node. `[]` keeps only the opening prompt.                 |
| Starting image         | Optional single RGB image. The same reference remains in place throughout the sequence. |

Give later prompts distinct, increasing chunk numbers. The sequence allows up
to 32 later prompts and 128 KB. The opening prompt is set at chunk zero. Each
Helios chunk contains 33 frames; chunk numbers are not seconds. The connector
sends all prompts before generation starts.

Choose a recording length that includes the changes you want. A prompt near the
end may have little visible effect, and a later prompt does not extend the file.
Use the [live workflow](/extensions/reactor-inc/guides/files/workflows/helios/helios-05-live-prompt.json) when you want to
choose changes while watching instead of preparing them in advance.

The text-sequence example starts on a forest path, adds sunlight at chunk 1,
and enters a clearing at chunk 3. Edit all three prompts to keep the scene
consistent. It records eight seconds; the optional image stays fixed.

## Run and save

1. Open the [text sequence](/extensions/reactor-inc/guides/files/workflows/helios/helios-03-prompt-sequence.json) or
   [image sequence](/extensions/reactor-inc/guides/files/workflows/helios/helios-04-image-sequence.json) template.
2. Edit the opening prompt and both later prompt builders. For the image
   example, upload your picture in **Upload your starting image**.
3. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
4. Select **Run**. Play the result in **Preview and save video**.

The node returns native `VIDEO` without audio and recording details as `STRING`.
Connect **Video** to ComfyUI's **Save Video** to keep the temporary result.
Seeds do not guarantee identical output after a provider update.

Preparing the prompt list is free. Generation, setup, and recording use Reactor
credits. Recording stops at **Video length (seconds)**; the separate host session limit
also applies. Use ComfyUI's cancel control to stop a run. Closing the ComfyUI window
does not cancel it. The connector disconnects after recording or failure and
does not automatically retry an uncertain session.

## Recovery

An invalid sequence fails before connection. Connect the prompt builders in
order and use an opening prompt that describes the same scene. For image input,
provide one image within the upload limit; batches are not accepted.

If a change is missing, check its chunk number and the recording length. If
generation fails, read the reported error and [troubleshooting guide](/extensions/reactor-inc/guides/ADVANCED.html#recovery)
before deciding to spend credits on another run.

[Helios command reference](https://docs.reactor.inc/model-api-reference/helios/schema)

## Credit rate

Select **View credit rate** to calculate a rate for your chosen session time.
Setup can add paid time beyond the video length; this is not a spending limit.
See [credit rates](/extensions/reactor-inc/guides/ADVANCED.html#credit-rates).

## Recording details

This output describes the saved file and model. See the
[field reference](/extensions/reactor-inc/guides/ADVANCED.html#recording-details) for timing, privacy, and cache behavior.
