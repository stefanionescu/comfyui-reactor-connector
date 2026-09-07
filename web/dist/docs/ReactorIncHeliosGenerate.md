# Reactor Helios: Generate Video

Generate a short video from a prompt using your Reactor account. Connect **Video**
to ComfyUI's **Save Video** node to preview and save the result.

## Inputs

| Input                  | What to provide                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------------------------- |
| Scene prompt           | Describe the scene and motion. Empty prompts are rejected before a session starts.                      |
| Video length (seconds) | Requested video duration, from 0.1 to the video duration limit in Reactor settings. Default: 5 seconds. |
| Seed                   | Integer from 0 to 4,294,967,295. Zero is valid. Default: 42.                                            |
| Variation              | Change this number to request another paid run with otherwise identical inputs.                         |
| Live controls          | Open live controls in the ComfyUI window that runs the workflow. Default: false.                        |

## Run and save

1. Open [Helios text to video](/extensions/reactor-inc/guides/files/workflows/helios/helios-01-text-to-video.json).
2. Set your key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
3. Describe the scene in **Scene prompt**. For example: “A red ball rolls slowly
   across a wooden table. The camera stays still.”
4. Choose **Video length (seconds)**, then select **Run**.
5. Play the result in **Preview and save video**. This node also saves the file.

The Reactor node returns **Video** without sound and **Recording details** as
text. In your own graph, connect **Video** to **Save Video** to keep the result
after ComfyUI clears its temporary storage.

## Cost and cancellation

Setup and generation use Reactor credits. Session time can exceed the saved
video length. A seed does not guarantee identical results after a model update.
Unchanged inputs may reuse ComfyUI's cached result. Changing the key or execution
limits can cause another paid run when you next select **Run**.

Use ComfyUI's cancel control to stop a run. Closing the ComfyUI window does not
cancel a queued workflow. Failed runs do not return a video. If the session's
end is unconfirmed, wait for the stated session limit before trying again.
Do not restart ComfyUI to bypass this wait.

The connector runs one session at a time. Other runs wait and can be cancelled
before they connect. The default queue wait limit is 120 seconds. A rejected
command or lost connection ends the run; the connector does not retry it.

For invalid inputs, missing video, or connection errors, follow the
[troubleshooting guide](/extensions/reactor-inc/guides/ADVANCED.html#recovery).

[Reactor Helios reference](https://docs.reactor.inc/model-api-reference/helios/overview)

## Live controls

Turn **Live controls** on, select **Run**, then select **Start session** in the
live panel within 60 seconds. Use **Apply prompt** to change later frames.
Let recording finish to save the result. **End session** discards the unfinished
video. Panel prompt changes do not rewrite the saved workflow.

See the [live controls guide](/extensions/reactor-inc/guides/ADVANCED.html#live-controls) for input, privacy, and stopping rules.

## Credit rate

Select **View credit rate** to calculate a rate for your chosen session time.
Setup can add paid time beyond the video length; this is not a spending limit.
See [credit rates](/extensions/reactor-inc/guides/ADVANCED.html#credit-rates).

## Recording details

This output describes the saved file and model. See the
[field reference](/extensions/reactor-inc/guides/ADVANCED.html#recording-details) for timing, privacy, and cache behavior.
