# Advanced guide

Use this guide for session limits, live controls, recording costs, and recovery.
For installation, see the [README](README.md). Native node **Info** covers
each model's inputs and limits.

## Keys and access

Add your key in **ComfyUI menu > Extensions > Reactor > Reactor settings**. It
stays on your ComfyUI server, and the connector sends it only to Reactor. The
connector never returns it to the window or writes it into a workflow.

`REACTOR_API_KEY` in the ComfyUI server environment takes precedence over a saved
key. Change it where you launch ComfyUI, then restart ComfyUI.

Private settings and live controls require a local, single-user connection.
Open the ComfyUI window on the computer running its server and connect directly
to the local address. Remote connections and reverse proxies cannot change
credentials. Set the server environment key for those setups.

The default state locations are:

| Platform | Directory                                         |
| -------- | ------------------------------------------------- |
| macOS    | `~/Library/Application Support/ReactorComfyUI`    |
| Linux    | `${XDG_STATE_HOME:-~/.local/state}/reactor-comfy` |
| Windows  | `%LOCALAPPDATA%\ReactorComfyUI`                   |

`REACTOR_COMFY_STATE_DIRECTORY` can select another absolute private path. It must
be outside the package, ComfyUI source, and configured input, output, temporary,
and user folders. Files use owner-only permissions where supported. They are
not encrypted; other code running as the same operating-system user can read them.

## Session limits

Change limits in **Reactor settings**. New sessions use the saved values;
active sessions keep their original key and limits.

| Setting                                | Default | Range     | Scope                                                                     |
| -------------------------------------- | ------- | --------- | ------------------------------------------------------------------------- |
| **maximum session duration (seconds)** | 180     | 1 to 3600 | The whole session, setup included; choose more time than the video needs. |
| **maximum upload size (MiB)**          | 100     | 1 to 4096 | Each uploaded image or video. One MiB is 1,048,576 bytes.                 |

Reactor bills session time, including setup. See its
[Pricing & Billing](https://docs.reactor.inc/resources/billing) for rates.

Changing the effective key or execution limits invalidates cached results.
Change **run number** to generate again with unchanged inputs. A seed does not
guarantee identical results after a model update.

If another window saves settings first, reload before saving your changes.
Invalid settings leave the previous file intact.

## Live controls

Choose a recording duration before running. The live panel belongs to the
ComfyUI window that started the workflow. Leaving it open does not extend the
session. Find the examples in [Choose a workflow](README.md#example-workflows).

Noninteractive generation can run through the ComfyUI API without a browser.
Interactive and webcam modes require the browser that submitted the workflow; a
bare API client cannot supply their controls. A browser is not required for the
local prompt-sequence and storyboard builders.

| Task                                     | Use                                                     |
| ---------------------------------------- | ------------------------------------------------------- |
| Change the scene while recording         | Helios, LongLive, or Visko live-prompt workflow         |
| Change an edit while a source clip plays | SANA or X2 live-prompt workflow                         |
| Drag an edited subject                   | X2 live-prompt or webcam workflow                       |
| Edit a camera feed                       | SANA or X2 webcam workflow                              |
| Move through an image                    | LingBot or LingBot World 2 workflow with scene controls |
| Continue several clips                   | Fast H3 continued-scene workflow                        |

Helios, LongLive, Visko, SANA, and X2 generation nodes have a **live controls**
switch, off by default. You cannot combine it with a Helios prompt sequence or
LongLive shots.

### Change prompts or use a webcam

1. Set the prompt and video length, then select **Run**.
2. On a webcam node, select **Enable Camera**, then allow camera access. Check
   the preview. To switch cameras, choose one, then select **Switch Camera**.
3. Select **Start Session** within 60 seconds.
4. When controls are ready, edit the prompt and select **Apply Prompt**.
5. Let the chosen recording duration finish to save the result.

Changes affect later frames and leave the saved workflow prompt unchanged.
LongLive uses a soft shot transition; Visko keeps **use prompt unchanged** as set
on the node. Starting and reference images stay fixed throughout the session.

Webcams need localhost or HTTPS, camera permission, and local single-user access.
The panel requests video only. Frames go to the local host before starting and
to Reactor only during the session. The connector takes no microphone input and
keeps no separate camera recording. Camera access stops when the panel closes or recording ends.

Input uses up to 640 × 480 pixels and ten new frames per second. The connector
repeats the latest frame on a 24 fps input. Saved output uses the model's resolution. The
separate preview uses up to 640 × 360 pixels at ten frames per second without sound.

### Change Visko audio

Turn **generate audio** on before running. During recording, edit **audio prompt**
and select **Apply Audio Prompt**. Leave it blank to let the picture guide sound.
Changes affect later sound; play the saved video to hear it. Resolution and sound
on/off stay fixed during the session. Changing them requires a new run.

### Drag in X2

Drag on the output to steer the subject; release to stop. For keyboard control,
focus the picture, use arrow keys to position the pointer, and hold Space to
activate it. Escape or losing focus releases the pointer. A circle marks your
chosen point, measured from the picture's left and top edges.

**Pointer held** and **Pointer released** confirm that Reactor accepted the input. Watch
later frames to judge its effect. X2 processes groups of frames, so changes can lag.

### Move in LingBot

Upload an image and run a workflow with scene controls. Click the picture: W and
S move forward and back, A and D move sideways, and arrow keys turn. Click a direction
button briefly or hold it to keep moving. Escape releases movement. World 2 can
combine forward and sideways movement.

Rapid changes can skip earlier movements; the panel releases old movement before
it applies the latest direction. Edit **scene prompt** and select **Apply Prompt**
to change later frames. Editing the prompt releases held movement. The starting
image and saved workflow prompt stay unchanged. Saved video cannot reopen a world,
and clicking its playback does not move the camera.

### Save or stop

Let recording finish. **Save Video** writes the result under ComfyUI's
output folder. **End Session** stops early and discards the unfinished video.
ComfyUI cancellation also ends the run. Closing a workflow tab does not cancel it.

The session ends if the live panel stops responding for five seconds. Webcam input
also ends after three seconds without a new frame. Cleanup can take longer; wait for
the end message. The connector does not reconnect automatically.

### Continue a scene

[Fast H3 continued scenes](web/docs/ReactorIncFastContinue.md) use the previous
clip's final frame to build the next clip. Choose a clip count and later prompts.
The result is one video with sound. Recording ends after the chosen number of
clips; their combined length must be 60 seconds or less.

## Recording overhead

### Fast H3

After the selected clip finishes, the connector builds and starts one additional
continuation. This advances the recording service so it can finish the selected
clip's media fragments. The continuation uses credits, but the saved output
leaves it out. Its requested length is the deployment's longest clip, currently
14.375 seconds. The session ends as soon as the selected recording is ready,
even if that continuation has not finished. The host session cap still applies.

### LTX

LTX may generate up to 20 extra seconds while Reactor prepares the recording.
These seconds can use credits and are not saved. The session time limit applies
to the whole run.

## Recovery

Read the error and the native **Info** of the node before trying again. When Reactor
refuses a run, the error ends with **Reactor said:** and Reactor's own reason.
A failed run returns no video. The connector does not retry a rejected command
or a lost connection.

Use ComfyUI's cancel control to stop a queued or running workflow. Closing the
browser or a workflow tab does not cancel a run without live controls, and
pausing a video preview does not stop its session. With live controls on,
closing the live panel or losing its browser connection ends the session and
discards the unfinished video.

| Problem                      | Next step                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------------ |
| Missing or rejected key      | Check Reactor settings and any server environment key, which takes precedence.                   |
| Rejected input               | Check the node's prompt, image, video, duration, and size limits.                                |
| Video did not arrive in time | Check [Reactor status](https://status.reactor.inc/) and the session limit before retrying.       |
| Recording cannot be saved    | Check disk space and media limits. Some models also need Reactor's recording service.            |
| A live panel expires         | Let cleanup finish before running again.                                                         |
| Camera is unavailable        | Allow access, select **Enable Camera**, and release the camera in another application if needed. |

## Update or remove

Finish or cancel active work, wait for sessions to end, then stop ComfyUI
before changing the connector.

To update a source checkout, replace the whole `custom_nodes/reactor-inc` folder
with the new source, install its runtime requirements using ComfyUI's Python,
and restart. Refresh the
ComfyUI window.

Keep only one installed copy in `custom_nodes` to avoid duplicate nodes and menus.

Open an updated example in a new workflow tab. Existing tabs and saved graphs
keep their own notes, prompts, and layout. Copy settings you want to reuse before
closing the old graph.

To remove the connector, move its folder outside `custom_nodes` and restart.
Keep shared Python dependencies that other packs may use. Removing or updating
the package preserves private state, media, and saved workflows. To remove state
too, first confirm that all sessions ended. Then delete only its
[state directory](#keys-and-access).
Deleting a saved key does not revoke it in Reactor.
