# Install, update, or remove the connector

Use ComfyUI with Python 3.12 or later. Reactor runs the models remotely; this
connector does not download model weights. You need a Reactor account and credits
to generate media. You do not need Bun, mise, or the development dependencies
to use the installed connector.

## Install the package

1. Stop ComfyUI after its current work finishes.
2. Extract the connector into `ComfyUI/custom_nodes/reactor-inc`.
3. Check that `__init__.py`, `requirements.txt`, `web/`, and `workflows/` are directly inside that folder. Avoid an extra nested repository folder.
4. Install `requirements.txt` using the Python environment that runs ComfyUI. Choose the command below for your installation.
5. Start ComfyUI. In Desktop, select **Refresh**; in a browser, reload the page.

For Desktop, use the instance's own ComfyUI directory and Python environment.
An installation in a different ComfyUI folder will not appear in that instance.

### macOS or Linux virtual environment

Run this from the ComfyUI directory. Replace `.venv` if your environment has a
different name:

```sh
.venv/bin/python -m pip install \
  -r custom_nodes/reactor-inc/requirements.txt
```

If the environment uses uv and has no pip, use its uv command with the same Python:

```sh
uv pip install --python .venv/bin/python \
  -r custom_nodes/reactor-inc/requirements.txt
```

### Windows virtual environment

Run this in PowerShell from the ComfyUI directory:

```powershell
.\.venv\Scripts\python.exe -m pip install `
  -r .\custom_nodes\reactor-inc\requirements.txt
```

### Windows portable

Run this in PowerShell from the portable directory containing both `ComfyUI`
and `python_embeded`:

```powershell
.\python_embeded\python.exe -m pip install `
  -r .\ComfyUI\custom_nodes\reactor-inc\requirements.txt
```

ComfyUI's [custom-node installation guide](https://docs.comfy.org/installation/install_custom_node)
explains these installation layouts. Install only the connector's runtime
requirements into ComfyUI. Its `uv.lock` and `package.json` belong to development.

## Open your first workflow

Select the Comfy logo to open the main menu, then choose
**Extensions → Reactor → Reactor settings**.
Save your key there. Open **Templates → reactor-inc**, choose a workflow,
and read its **Start here** note. You can also drag a JSON file from the connector's
[workflows folder](../workflows/README.md) onto the canvas.

Opening a template or reading help does not start generation. Selecting **Run**
can use credits. Live workflows also explain their start control in the notes.
See [settings](settings.md) for time limits and private key storage.

## Update or restore a previous package

Finish or cancel active work, confirm that Reactor sessions have ended, and stop
ComfyUI. Keep a copy of the current connector folder outside `custom_nodes`.
Replace the whole connector folder with the new package; do not merge old and
new runtime files. Install the new package's `requirements.txt`, restart ComfyUI,
and refresh the ComfyUI window.

Open the latest example from **Templates** in a new workflow tab. An update does
not replace graphs that are already open or saved. Keep your old graph until
you have copied any prompts and settings you want to reuse.

If your previous folder was named `reactor-inc-connector`, move it outside
`custom_nodes` before installing `reactor-inc`. Loading both copies creates
duplicate nodes and routes. The local package installer handles managed copies
as described in the [development guide](development.md#build-and-install-a-package).

An older copy can be restored the same way: replace the connector folder with
your backup and install that copy's requirements. Keep a private backup of the
[state directory](settings.md#supported-access) before changing versions. An older
package might not understand state or nodes created by a newer one. Restore a
matching backup only after all sessions have ended; never remove a session wait
record to force a new run.

Settings, keys, and model-list history live outside the
package. Replacing the connector folder preserves them. ComfyUI's input, output,
and saved workflows also stay separate. Model-list refresh updates metadata;
it does not update this package.

## Remove the connector

End active Reactor sessions and stop ComfyUI. Move the connector folder out of
`custom_nodes`, then restart ComfyUI. Other packs may use the same dependencies,
so do not remove shared Python packages as part of this step.

Removing the connector preserves its private state. To remove that state too,
first confirm that no Reactor session remains active, then remove only its
[state directory](settings.md#supported-access). This removes saved keys, settings,
catalog history. It does not revoke your API key. Manage keys separately in
your Reactor account.

For missing nodes or import errors, use the [troubleshooting guide](troubleshooting.md).
