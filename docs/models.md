# Find and refresh Reactor models

Open ComfyUI's main menu using the Comfy logo. Choose
**Extensions → Reactor → Reactor models**.

The dialog shows the included model list or the last list you saved.
Opening it does not contact Reactor. Search by model name or the name used to
connect to Reactor. Each entry shows its last checked price, a guide link when
available, and whether the connector has a node for it.

Choose **Refresh models** to check Reactor's public prices and model guides.
Refresh does not use your key, spend credits, start generation, or install
anything. The list includes models with a published price or guide. A listing
does not guarantee that your account can run the model.

The list uses public sources. Your Reactor account determines which models
you can use.

HappyOyster is not supported. It is excluded from the displayed model list,
including after a refresh or restoration of an older list.

## Read a model's status

- **Nodes available** means this connector includes nodes for the model.
- **No connector node available** means the model cannot be run through this connector.
- **Not observed in the latest source check** means the previous entry was
  retained. Its old rate is not a current quote and its absence does not prove
  that Reactor removed the model.

When a model has node IDs, find those nodes in ComfyUI's Node Library. Select a
node and select **Help** for its local guide. Refreshing the model list does not
change existing node IDs, sockets, or running workflows.

## If a refresh fails

All three public sources must pass validation. If a source times out, returns
invalid data, gives conflicting model names, or omits too many entries, the
connector keeps your previous list.
Descriptions remain text; catalog data cannot execute Python or JavaScript.

**Restore previous list** brings back the model list saved before your last refresh. It does not restore a model on Reactor, reverse a billed run, or change
the connector package. Your search stays in place when you refresh or restore
the list. Only the local ComfyUI user can change the list or settings.

## Automatic checks

Open **Reactor settings → Model updates** to enable or disable automatic checks
and choose an interval in hours. New installations check at startup, then every
24 hours while ComfyUI runs. Your saved preference is preserved during updates.
The scheduler reads preference changes within one minute. A check already in
progress can take up to 25 seconds to finish.

Checks use the same public sources as manual refresh. They do not use credentials,
start sessions, install code, or replace the current list. In **Reactor models**,
expand **Model sources and automatic checks** to see whether the model list
has changed. Choose **Refresh models** to
save the checked list. Reopen the model dialog to see a check that finished
after the dialog opened. Failed checks retain the list and retry at the configured
interval; manual refresh remains available. Closing ComfyUI stops the check.

## Maintainer tasks

Run these tasks from the repository with its development dependencies installed:

| Task | Effect |
| --- | --- |
| `mise run models:check` | Check public prices and model guides without changing the snapshot. |
| `mise run models:refresh` | Build the next public bundled snapshot for review. |
| `mise run models:validate` | Validate the bundled snapshot offline. |

Keep private account listings and authenticated schemas outside the public
snapshot. Validate every new model's adapter, node, guide, example, and required
media through the installed package in the local ComfyUI before release.
