# Reactor LongLive: Generate Video

Generate a short video from an opening shot prompt with LongLive-2.0.

## Inputs

| Input                  | What to provide                                                                  |
| ---------------------- | -------------------------------------------------------------------------------- |
| Scene prompt           | Describe the opening scene and motion. Use 1 to 20,000 characters.               |
| Video length (seconds) | Video length; default: 5 seconds. The limit in Reactor settings applies.         |
| Seed                   | Integer from 0 to 4,294,967,295; default: 42.                                    |
| Variation              | Change this number for another run; default: 0.                                  |
| Live controls          | Open live controls in the ComfyUI window that runs the workflow. Default: false. |

Example prompt: “A fox walks along a forest path. The camera follows slowly.”
Use 2 seconds for a first video. For later shots and cuts, open the
separate LongLive storyboard workflow.

## Run and save

1. Configure the key privately in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open the matching template and provide the inputs described above.
3. Connect **Video** to the native **Save Video** node, then select **Run**.
4. Play the result in Save Video. Saved files use the workflow's relative output prefix.

The node returns native `VIDEO` and recording details as `STRING`. This operation
records video without audio. Use Save Video to retain the temporary result.

**Video length (seconds)** limits the captured video; connection and setup also use
session time. The host recording and session limits both apply. Changing **Variation** requests another execution with the
same other inputs. Unchanged inputs may reuse the host cache; changing the
account or execution limits invalidates that reuse. Seeds do not guarantee
identical results after a provider update.

Use ComfyUI's cancel control to stop a queued or running operation. Closing a
browser tab does not cancel the workflow. The connector owns one session at a
time, applies a session time limit, and disconnects after recording or failure.
It does not retry rejected commands or uncertain session creation. If the connector cannot confirm
that the session ended, wait for its time limit before trying again.

## Recovery

Enter a prompt before running. If video stops arriving, check Reactor and your
account before trying again. Use LongLive Storyboard to schedule later shots.
This node does not accept a starting image.

[LongLive schema](https://docs.reactor.inc/model-api-reference/longlive-v2/schema)

## Live controls

Turn **Live controls** on, select **Run**, then select **Start session** in the
live panel within 60 seconds. Use **Apply prompt** to change later frames.
Let recording finish to save the result. **End session** discards the unfinished
video. Panel prompt changes do not rewrite the saved workflow.

See the [live controls guide](../../ADVANCED.md#live-controls) for input, privacy, and stopping rules.

Select **View credit rate** for a [session estimate](../../ADVANCED.md#credit-rates).

## Recording details

This output describes the saved file and model. See the
[field reference](../../ADVANCED.md#recording-details) for timing, privacy, and cache behavior.
