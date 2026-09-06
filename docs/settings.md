# Set up Reactor

Open ComfyUI's main menu using the Comfy logo, then choose
**Extensions → Reactor → Reactor settings**. Opening settings reads local
configuration; it does not authenticate with Reactor or start generation.

## Save or clear a key

Enter your Reactor API key and select **Save key**. The field clears when you
submit it. The connector stores the key in its private server state directory,
outside the package and media folders. It never returns the saved value to the
browser or writes it into a workflow.

The **configured** state means that a key is present. It does not mean Reactor
has accepted the key. Saving a key does not buy credits or change billing.

If `REACTOR_API_KEY` is set in the ComfyUI server environment, it takes precedence
over a saved key. **Clear saved key** removes only the saved value. Change an
environment key where ComfyUI is launched and restart the server to apply it.

## Set execution limits

**Maximum video duration** limits the requested output length. **Maximum session
duration** limits how long a Reactor session can run and must be longer than the video
limit because setup also takes time. New executions use the saved values.

Open **Advanced limits** to set connection, first-frame, disconnect, and queue
timeouts or media size limits. File and memory limits use MiB, where 1 MiB equals
1,048,576 bytes. These controls do not change the account's credit balance.

Settings saves include the revision that the dialog loaded. If another tab saves
first, reload the current settings before making your change again. Invalid
values are rejected without replacing the previous file.

Changing the effective key or execution limits prevents normal ComfyUI cache
reuse on the next queued run. Queuing that workflow can therefore start another
paid session. Catalog check preferences do not invalidate generated results.
A run that has already started keeps the settings and key it started with. Changing
settings does not cancel it or delete previously saved media.

## Recover after a restart

If ComfyUI closes before Reactor confirms that a session ended, the connector
keeps a wait time in its private settings folder. A new run shows how many seconds
remain. Restarting ComfyUI, changing the key, or lowering the time limits does not
clear that wait. It allows time for setup and the earlier session to end.

ComfyUI processes that share the same connector settings folder cannot run Reactor
sessions at the same time. Let the other run finish before starting another one.
Do not delete `session.json` or `session.lock` to skip a wait. If the session record
is damaged, check Reactor Usage and confirm that no session remains active before
repairing it.

## Check for model updates

In **Model updates**, choose whether ComfyUI checks public prices and model guides
automatically and set the interval in hours. Select **Save model check settings**.
The scheduler reads changes within one minute. Existing installations keep their
saved preference; the default for a new installation is a check every 24 hours.

Automatic checks report changes in **Reactor models**. Use **Refresh models**
there to apply the latest validated list. A check does not use an API key, start
generation, or replace node code. See [model refresh](models.md) for details.

## Check the credit rate

Select **View credit rate** on a generation node. The time starts with that
node's requested video length. For continued clips, it uses clip length times
clip count. A connected duration input is not guessed: enter a time yourself.
The **Add a prompt** and **Add a shot** nodes work locally and use no credits.

Change **Session time to calculate (seconds)** to multiply the listed rate by
another duration. Setup, pauses, and recording can add paid time beyond the video
length. The result is neither a spending limit nor a quote. Check Reactor Usage
for actual charges.

The dialog shows when rates were checked. Open **ComfyUI menu → Extensions → Reactor → Reactor
models** and select **Refresh models** for current public prices. This does not
start a paid session. Missing or unconfirmed rates do not produce a calculation.
Help buttons and credit calculations are not saved as workflow inputs.

To compare models, open **Reactor models** and expand **Calculate credits for
session time**. Enter a time to show the calculation beside each matching model.

## Supported access

Credential and settings changes require a direct loopback connection to ComfyUI
with a matching browser origin. Changes are disabled in ComfyUI's multi-user
mode. You cannot change credentials through a remote connection or reverse proxy.
For those setups, set the key in the server environment instead.

Saved files use owner-only permissions where supported. They are not encrypted
by being placed in a private directory. Other trusted code running as the same
operating-system user can access them.

The default state locations are:

| Platform | Directory |
| --- | --- |
| macOS | `~/Library/Application Support/ReactorComfyUI` |
| Linux | `${XDG_STATE_HOME:-~/.local/state}/reactor-comfy` |
| Windows | `%LOCALAPPDATA%\ReactorComfyUI` |

An administrator can set `REACTOR_COMFY_STATE_DIRECTORY` to an absolute private
path. The connector rejects a location inside the installed package, ComfyUI's
source directory, or its configured input, output, temporary, and user folders.

## Inspect a failed run

The latest provider failure is recorded as `last-failure.json` in the private
state directory. It contains the operation, error code, and a short error message.
The connector removes the configured credential, recognizable key and token
forms, and URLs before writing. The file is replaced on the next recorded failure.

This diagnostic is not served to the browser or included in a workflow result.
It can still contain private prompt or model details. Review it before sharing
any excerpt. Ordinary node errors show a safe explanation and operation stage.

## Read node help

Select a Reactor node and choose **Node Info** in its floating toolbar, or open
the **Info** tab in the properties panel. The matching guide is bundled with the
package and needs no credential or generation. It describes inputs, outputs,
costs, limits, and an example.
