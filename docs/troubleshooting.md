# Fix a connector problem

Read the node's error message first. Select the Reactor node and choose **Help**
for its input rules and recovery steps. Starting another generation uses
credits; refreshing help, settings, or the public model list does not.

## Nodes, templates, or help are missing

Confirm that the running ComfyUI instance contains
`custom_nodes/reactor-inc/__init__.py`. Check its startup log for an
import error, then follow the matching step:

| What you see | What to do |
| --- | --- |
| `reactor_sdk` cannot be imported | Install `requirements.txt` with the Python that runs this ComfyUI instance. |
| No matching Reactor SDK distribution | Check that Python is at least 3.12 and that the required SDK has a package for your operating system and processor. Keep the required SDK version range. |
| `comfy_api`, a native node type, or an input class is missing | Update ComfyUI using its normal update procedure, then restart it. |
| Nodes appear but Reactor menu items do not | Refresh the ComfyUI window. Confirm that the package includes `web/main.js`. |
| Node help is blank or a guide is missing | Restore the complete package, including `web/docs` and `web/guides`. |
| Templates are missing | Confirm that `workflows/` contains JSON files. Drag one onto the canvas to open it directly. |
| Duplicate Reactor nodes or menus | Keep one installed connector folder. Move backup copies outside `custom_nodes`, then restart. |

Use the [installation guide](installation.md) for commands and folder layouts.
Do not install the development environment over ComfyUI's Python environment.

## Settings or live controls are unavailable

Open your local installation in Comfy Desktop or at its local browser address,
such as `http://127.0.0.1:8188`. Private settings and live controls require a local,
single-user connection. In a browser, use the server's own address. A reverse
proxy or multi-user mode can prevent these controls from opening.

If a live panel expires, let its session finish closing before running again.
For webcam workflows, allow camera access and select **Enable camera** before
**Start session**. If another application owns the camera, release it there.
See [live controls](live.md) for input and connection limits.

## A run fails

| Problem | Next step |
| --- | --- |
| Missing or rejected key | Check the saved key in Reactor settings. An environment key takes precedence. A saved key is not proof that Reactor accepted it. |
| Rejected input | Check the node guide's text, image, video, duration, and size limits. Use the model's own workflow as a starting point. |
| Session unavailable or already active | Let the current session finish. Check Reactor Usage if termination was not confirmed. |
| Timed out before video arrived | Check Reactor's service status and the node's expected setup time. Review the time limit and cost before another run. |
| Recording could not be saved | Check free disk space, upload and capture limits, and the model guide. Some models also need Reactor's recording service. |
| Session cleanup could not be confirmed | Check Reactor Usage and wait for the configured session limit. Do not clear local wait records or repeatedly queue the workflow. |
| Model-list refresh failed | Keep using the current list. Follow the recovery steps in the model refresh guide. |

[Reactor status](https://status.reactor.inc/), [execution limits](settings.md),
and [model refresh](models.md) provide more detail. Pausing video playback does
not stop a paid session. Use **End session** in a live panel or ComfyUI's cancel
control; follow any cleanup message before starting another run.

## Report a problem

Include the node and model names, the error text, your operating system, and
the ComfyUI, Python, and connector versions. State what you expected and what
happened. If you used a packaged archive, its filename identifies the build.

Attach a small workflow only after reviewing its prompts, filenames, notes,
and world selections for private information. Replace personal inputs with
shareable examples. Do not post API keys, access tokens, private state folders,
raw account responses, or unreviewed logs. A screen recording is optional;
show only what is needed to explain the problem.

The private `last-failure.json` file can help identify a failed operation, but it
may still contain prompt or model details. Read the [diagnostic guidance](settings.md#inspect-a-failed-run)
before sharing an excerpt. Report suspected secret exposure privately to the
repository owner instead of opening a public issue with the sensitive data.
