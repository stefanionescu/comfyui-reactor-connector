# ComfyUI Reactor Connector: Advanced Guide

Use this guide for settings, live controls, model updates, and recovery. For
installation and your first run, see [the setup guide](README.md). Each node's **Help**
action explains its inputs and model-specific limits.

## Contents

- [Keys and access](#keys-and-access)
- [Execution limits](#execution-limits)
- [Credit rates](#credit-rates)
- [Model updates](#model-updates)
- [Live controls](#live-controls)
- [Recording details](#recording-details)
- [Recording overhead](#recording-overhead)
- [Recovery](#recovery)
- [Update, restore, or remove](#update-restore-or-remove)
- [Language](#language)
- [Development commands](#development-commands)

## Keys and access

Open **ComfyUI menu → Extensions → Reactor → Reactor settings**. Saving a key
clears the entry field and stores the value in the private server state directory.
The saved value is never returned to the window or written into a workflow.
**Configured** means a key is present; it does not mean Reactor has accepted it.

`REACTOR_API_KEY` in the ComfyUI server environment takes precedence over a saved
key. **Clear saved key** removes only the saved value. Change an environment key
where ComfyUI is launched, then restart ComfyUI.

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

## Execution limits

**Maximum video duration** limits the requested output length. **Maximum session
duration** limits the whole Reactor session and must allow additional time for
setup. **Advanced limits** controls connection, first-frame, disconnect, and queue
timeouts, plus media size limits. One MiB is 1,048,576 bytes.

The connector runs one session at a time. Other runs wait; the default queue
wait limit is 120 seconds. You can cancel while waiting, before connection.
A rejected command or uncertain connection is not retried automatically.

New runs use saved settings. A running session keeps its original key and limits.
Changing the effective key or execution limits prevents reuse of an earlier
ComfyUI result on the next run.
Model-update settings do not affect reuse of saved results. Change **Run number** to
request a new run with otherwise unchanged inputs. A seed does not guarantee
identical results after a provider update.

If another window saves settings first, reload before making your changes again.
Invalid settings leave the previous file intact. Saving settings does not cancel
active work or remove saved media.

## Credit rates

Select **View credit rate** on a generation node. The dialog starts with its
requested video length; continued clips use clip length multiplied by clip count.
For a connected duration input, enter the time yourself.

**Session time to calculate (seconds)** multiplies a public rate by your chosen
time. Setup, waiting, and recording preparation can add time beyond the
video length. The calculation is not a quote or spending limit. Refer to Reactor
for actual charges. A missing or unconfirmed rate produces no calculation.

The dialog shows when rates were checked. Refresh the model list for current
public prices. To compare models, open **Reactor models** and expand **Calculate
credits for session time**. Help and credit controls are not saved as node inputs.

## Model updates

Open **ComfyUI menu → Extensions → Reactor → Reactor models** to search the
included list or your last saved list. Opening the dialog reads local information.
Each entry shows its last checked rate, any available guide, and node support.

Installed models appear before the first refresh. Refresh the list to load public
prices and metadata. Saved metadata stays in Reactor's private application-data folder on the ComfyUI server.

**Refresh models** reads Reactor's public prices and model guides. Entries come from
published prices or guides; your account determines which models you can run.
HappyOyster is excluded, including when an older list is restored.

| Status                                              | Meaning                                                                                                            |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Nodes available                                     | This connector includes nodes for the model.                                                                       |
| No connector node available                         | The model cannot run through this connector.                                                                       |
| This rate was not found in the latest source check. | The earlier entry was retained. Its old rate is not a current quote. Absence does not prove the model was removed. |

Refreshing does not add nodes, change their connections, or change active
workflows. New models need support in the connector before they can run.

A failed refresh leaves the current list intact. **Restore previous list** restores
the list saved before the latest refresh. Both actions keep your search text.
Only the local ComfyUI user can change the list.

### Automatic checks

Under **Reactor settings → Model updates**, enable checks and choose an interval
in hours. New installations check at startup and every 24 hours while ComfyUI
runs. Existing saved preferences are preserved. Changes take effect within one
minute; an active check can take up to 25 seconds to finish.

Checks use the same public sources as refresh. They report changes without
replacing the saved list. Expand **Model sources and automatic checks** in the
model dialog, then select **Refresh models** to save the checked list. Reopen the
dialog to see a check that finished after you opened it. Failed checks keep the
list and retry at the configured interval. Closing ComfyUI stops checking.

## Live controls

Choose a recording duration before running. The live panel belongs to the
ComfyUI window that started the workflow. Leaving it open does not extend the
session. Find the examples in the [workflow index](workflows/README.md).

| Task                                     | Use                                                     |
| ---------------------------------------- | ------------------------------------------------------- |
| Change the scene while recording         | Helios, LongLive, or Visko live-prompt workflow         |
| Change an edit while a source clip plays | SANA or X2 live-prompt workflow                         |
| Drag an edited subject                   | X2 live-prompt or webcam workflow                       |
| Edit a camera feed                       | SANA or X2 webcam workflow                              |
| Move through an image                    | LingBot or LingBot World 2 workflow with scene controls |
| Continue several clips                   | Fast H3 continued-scene workflow                        |

Ordinary Helios, LongLive, Visko, SANA, and X2 generation nodes have a **Live
controls** switch, off by default. LongLive storyboards keep their prepared shots.

### Change prompts or use a webcam

1. Set the prompt and video length, then select **Run**.
2. For a webcam node, select **Enable camera** and allow camera access. Check the
   preview. To switch cameras, choose one and select **Use selected camera**.
3. Select **Start session** within 60 seconds.
4. When controls are ready, edit the prompt and select **Apply prompt**.
5. Let the chosen recording duration finish to save the result.

Changes affect later frames and leave the saved workflow prompt unchanged.
LongLive uses a soft shot transition; Visko keeps **Use prompt unchanged** as set
on the node. Starting and reference images stay fixed throughout the session.

Webcams need localhost or HTTPS, camera permission, and local single-user access.
The panel requests video only. Frames go to the local host before starting and
to Reactor only during the session. There is no microphone input or separate
camera recording. Camera access stops when the panel closes or recording ends.

Input uses up to 640 × 480 pixels and ten new frames per second. The latest frame
is repeated on a 24 fps input. Saved output uses the model's resolution. The
separate preview uses up to 640 × 360 pixels at ten frames per second without sound.

### Change Visko sound

Turn **Include sound** on before running. During recording, edit **Sound prompt**
and select **Apply sound prompt**. Leave it blank to let the picture guide sound.
Changes affect later sound; play the saved video to hear it. Resolution and sound
on/off stay fixed during the session. Changing them requires a new run.

### Drag in X2

Drag on the output to steer the subject; release to stop. For keyboard control,
focus the picture, use arrow keys to position the pointer, and hold Space to
activate it. Escape or losing focus releases the pointer. A circle marks your
chosen point, measured from the picture's left and top edges.

**Pointer held** and **Pointer released** confirm that input was accepted. Watch
later frames to judge its effect. X2 processes groups of frames, so changes can lag.

### Move in LingBot

Upload an image and run a workflow with scene controls. Click the picture: W and S move
forward and back, A and D move sideways, and arrow keys turn. Click a direction
button briefly or hold it to keep moving. Escape releases movement. World 2 can
combine forward and sideways movement.

Rapid changes can skip earlier movements; old movement is released before the
latest direction is applied. Edit **Scene prompt** and select **Apply prompt**
to change later frames. Editing the prompt releases held movement. The starting
image and saved workflow prompt stay unchanged. Saved video cannot reopen a world,
and clicking its playback does not move the camera.

### Save or stop

Let recording finish. **Preview and Save Video** writes the result under ComfyUI's
output folder. **End session** stops early and discards the unfinished video.
ComfyUI cancellation also ends the run. Closing a workflow tab does not cancel it.

The session ends if the live panel stops responding for five seconds. Webcam input
also ends after three seconds without a new frame. Cleanup can take longer; wait for
the end message. If termination is unconfirmed, wait for the session limit before
another run. The connector does not reconnect automatically.

### Continue a scene

[Fast H3 continued scenes](web/docs/ReactorIncFastContinue.md) use the previous
clip's final frame to build the next clip. Choose a clip count and later prompts.
The result is one video with sound. Recording ends after the chosen number of
clips. Set the video duration limit high enough for their combined length.

## Recording details

The **Recording details** output is a JSON string describing the saved media.
Its serialized socket name remains `metadata`. Connect it to a text display or
another node to inspect it; saving the video does not save this text separately.

| Field                              | Meaning                                                            |
| ---------------------------------- | ------------------------------------------------------------------ |
| `schema_version`                   | Report format version, currently `1`.                              |
| `run_id`                           | Random local execution ID; grants no session access.               |
| `node_id`, `model_name`            | Node ID and model connection name used for the run.                |
| `connector_version`, `sdk_version` | Connector and installed Reactor SDK versions.                      |
| `package_identity`                 | Package content ID, or `null` for a checkout without a manifest.   |
| `frames`                           | Number of encoded video frames.                                    |
| `width`, `height`                  | Saved dimensions in pixels.                                        |
| `file_bytes`                       | Completed MP4 size, including embedded audio.                      |
| `has_audio`                        | Whether the MP4 has an audio track; the track may contain silence. |
| `requested_duration_seconds`       | Requested length; clip length times count for continued scenes.    |
| `duration_seconds`                 | Duration reported by the MP4 video stream, or `null` if absent.    |
| `timestamp_mode`                   | Frame-timing method described below.                               |

`sender` preserves received timestamps. `fallback_fps` uses the adapter's frame
rate when the stream supplies no initial timestamp. `recording_pts` uses the
downloaded Reactor recording's timestamps to align video and sound.

A `live` object can include acknowledged action counts, preview frames, and
control timing. Acknowledgment does not prove the requested change is visible.
Saved length can differ from the request when the model chooses another accepted
length or ends early. File details do not assess visual quality or billed time.

Reports omit prompts, images, keys, tokens, remote session IDs, and absolute paths.
ComfyUI may reuse a cached report and its `run_id`; pressing **Run** does not prove
a new session started. Older reports may have fewer fields and no schema version.
Allow missing fields when reading them. Do not rerun solely to update a report.

## Recording overhead

### Fast H3

After the selected clip finishes, the connector builds and starts one additional
continuation. This advances the recording service so it can finish the selected
clip's media fragments. The continuation uses credits but is omitted from the
saved output. Its requested length is the deployment's longest clip, currently
14.375 seconds. The session ends as soon as the selected recording is ready,
even if that continuation has not finished. The host session cap still applies.

### LTX

LTX may generate up to 20 extra seconds while Reactor prepares the recording.
These seconds can use credits and are not saved. The session time limit applies
to the whole run.

## Recovery

Read the error and the node's **Help** before trying again. Pausing a video preview does not stop its session.

| Problem                      | Next step                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------------ |
| Missing or rejected key      | Check Reactor settings and any server environment key, which takes precedence.                   |
| Rejected input               | Check the node's prompt, image, video, duration, and size limits.                                |
| Another session is active    | Let it finish. Wait for confirmed cleanup before another run.                                    |
| Video did not arrive in time | Check [Reactor status](https://status.reactor.inc/) and the session limit before retrying.       |
| Recording cannot be saved    | Check disk space and media limits. Some models also need Reactor's recording service.            |
| Session end is unconfirmed   | Wait for the configured session limit; do not repeatedly queue or clear wait records.            |
| Model refresh fails          | Keep the current list and retry the public-source refresh later.                                 |
| A live panel expires         | Let cleanup finish before running again.                                                         |
| Camera is unavailable        | Allow access, select **Enable camera**, and release the camera in another application if needed. |

### Recover after a restart

If ComfyUI closes before session termination is confirmed, a private record
keeps the required wait time. New runs show the remaining seconds. Restarting,
changing keys, or lowering limits does not bypass it. Processes sharing the
same state directory cannot run Reactor sessions at the same time.

Do not delete `session.json` or `session.lock` to skip a wait. If a record is
damaged, confirm that no session remains active in Reactor before repairing it.

### Private diagnostics

`last-failure.json` in the state directory records the latest failed operation,
error code, and a short message. Recognizable keys, tokens, the configured
credential, and URLs are removed. The file is replaced by the next failure.
It is not served to the window or included in workflow results, but it can contain
private prompt or model details. Review any excerpt before sharing it.

## Update, restore, or remove

Finish or cancel active work, wait for sessions to end, then stop ComfyUI.
Keep a backup of the connector folder outside `custom_nodes`. Replace the whole
folder with the new package, install its runtime requirements using ComfyUI's
Python, and restart. Refresh the ComfyUI window.

Keep only one installed copy in `custom_nodes` to avoid duplicate nodes and menus.

Open an updated example in a new workflow tab. Existing tabs and saved graphs
keep their own notes, prompts, and layout. Copy settings you want to reuse before
closing the old graph.

Restore a previous package by replacing the whole folder with its backup and
installing that version's requirements. Back up private state before changing
versions. An older package may not understand newer state or nodes. Restore a
matching state backup only after all sessions end; never remove a wait record
to force a run.

To remove the connector, move its folder outside `custom_nodes` and restart.
Keep shared Python dependencies that other packs may use. Removing or updating
the package preserves private state, media, and saved workflows. To remove state
too, confirm all sessions ended and delete only its [state directory](#keys-and-access).
Deleting a saved key does not revoke it in Reactor.

## Language

This release includes English text and guides. Installed translations use the
language selected in ComfyUI. Custom panel labels follow language changes;
English remains the fallback when a message or guide is missing.

Saved workflow notes and custom titles keep the language used when the workflow
was built. Example prompts and speech scripts stay in English. Changing ComfyUI's
language does not rewrite your graph or translate model inputs. Node search
aliases, categories, placeholders, and errors from queued execution currently
use English. An error already returned by the server keeps its original text.

To build workflow text from an installed locale, choose a separate output folder:

```sh
mise run workflows:build -- --language fr --output-directory .artifacts/workflows/fr
```

Add reviewed French resources before using this example; only English resources
are supplied. The output index links to the repository's shared guides and sample
files. Keep it with that checkout. It is not a standalone translated package.

## Development commands

Run `mise run setup` to install the pinned tools and dependencies and enable local
Git hooks. Bun manages frontend dependencies; uv manages Python dependencies.
Development tools use the repository environment, separate from ComfyUI.

Development scripts run as modules of the checkout package through mise.
Quality tools run from the repository root. ComfyUI starts media workers through
the root launcher in isolated Python processes; those workers use only the media
modules and static configuration.

Python checks read types from your actual ComfyUI installation. Set its source
directory in your terminal before running development commands:

```sh
export COMFYUI_PATH="/path/to/ComfyUI"
```

That directory must contain `main.py` and `comfy_api`. Checks use its `.venv`
Python by default. If ComfyUI uses another environment or Windows portable,
also set `COMFYUI_PYTHON` to that installation's Python executable:

```sh
export COMFYUI_PYTHON="/path/to/ComfyUI/python"
```

Replace these example paths with your installation's paths. The variables apply
to commands run from that terminal; they are not stored in the repository.

Setup downloads the pinned Semgrep rules into ignored local storage and verifies
their content hashes. To restore those files, run `mise run security:rules`.
The downloaded rules retain their upstream license notices and are not included
in the connector package.

| Command                    | Purpose                                                                                           |
| -------------------------- | ------------------------------------------------------------------------------------------------- |
| `mise run deps`            | Install locked development dependencies.                                                          |
| `mise run setup`           | Install tools and dependencies, then enable local hooks. Stops if another project owns the hooks. |
| `mise run format`          | Format source files.                                                                              |
| `mise run check`           | Check source, types, generated files, dependencies, security, licenses, and links.                |
| `mise run type:python`     | Check Python types against the selected ComfyUI installation.                                     |
| `mise run frontend:build`  | Build the shipped JavaScript and CSS.                                                             |
| `mise run workflows:build` | Build the example graphs and workflow index.                                                      |
| `mise run docs:build`      | Build native node help and local HTML guides.                                                     |
| `mise run deps:export`     | Generate runtime requirements from project metadata.                                              |
| `mise run models:check`    | Read public prices and guides without saving them.                                                |
| `mise run models:validate` | Check node registrations and translations.                                                        |
| `mise run audit:python`    | Check Python dependencies against advisory services.                                              |
| `mise run audit:frontend`  | Check frontend dependencies against advisory services.                                            |
| `mise run security:rules`  | Download and verify the pinned Semgrep rule packs.                                                |
| `mise run release:package` | Check and build a ComfyUI archive without publishing it.                                          |

Pre-commit checks scan staged changes for secrets and reject staged private
settings files. They also check source files, frontend types, and generated output
in the working directory. Pre-push runs `mise run check` against the working
directory. Hooks do not stash or rewrite your work.

Builds write generated assets; checks and hooks do not install dependencies or
start generation. Dependency audits need network access and do not apply fixes.
Archives include only the public runtime files, with a content hash in their
filename and a manifest recording their hashes.

To install an archive built from this checkout, pass the actual ComfyUI source
directory containing `main.py` and `comfy_api`:

```sh
mise run comfy:install -- --host "/path/to/ComfyUI"
```

Stop that instance first. The installer preserves a managed previous copy in
`.reactor-package-backups` beside ComfyUI and refuses to replace an unmanaged
folder. Install runtime requirements with the host's Python, then restart.

The package includes top-level copies of grouped workflow files because ComfyUI's
Templates browser reads that level. Source checkouts can open the grouped JSON
files directly. Rebuild examples before packaging.

Python checks use actual ComfyUI and dependency types. Where an upstream API lacks
complete annotations, the code defines only the interface it consumes. Check
changed host calls manually in the installed ComfyUI as well.
