# Reactor LongLive: Create a Storyboard

Generate a short video from an opening shot prompt with LongLive-2.0.
Schedule later shots before generation starts. Connect one or more **Reactor LongLive: Add a Shot** nodes to the **Shots (JSON)** input. Soft transitions change the prompt
within the scene; cuts start a new scene.

## Inputs

| Input                  | What to provide                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------- |
| Scene prompt           | Describe the opening scene and motion. Use 1 to 20,000 characters.                    |
| Video length (seconds) | Video length; default: 5 seconds. The limit in Reactor settings applies.              |
| Seed                   | Integer from 0 to 4,294,967,295; default: 42.                                         |
| Variation              | Change this number for another run; default: 0.                                       |
| Shots (JSON)           | Connect Reactor LongLive: Add a Shot. An empty list `[]` means the opening shot only. |

LongLive generates frames in groups called **chunks**. Each chunk contains
29 frames, about 1.2 seconds at 24 frames per second. Count chunks from the start
of generation. Give each later shot a larger chunk number, starting at 1.
You can add up to 32 later shots. The JSON shot list must fit within 128 KB and
contain only the fields produced by Reactor LongLive: Add a Shot.

Choose a video length that includes all scheduled shots. A later shot does not
automatically extend the recording. Timing follows the generated frames, so do
not count seconds from when you click Run.

Example: describe a forest path as the opening shot, add a soft camera pullback
at chunk 1, then a cut to a lake at chunk 2. Record 5 seconds and watch both
transitions in the saved result.

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

An empty prompt or invalid storyboard fails before connection. If a later shot
is missing, check its chunk number and the chosen video length.
Do not enter seconds in the chunk field. LongLive uses text shots; this node
does not accept a starting image.

[LongLive schema](https://docs.reactor.inc/model-api-reference/longlive-v2/schema)

Select **View credit rate** for a [session estimate](../../ADVANCED.md#credit-rates).

## Recording details

This output describes the saved file and model. See the
[field reference](../../ADVANCED.md#recording-details) for timing, privacy, and cache behavior.
