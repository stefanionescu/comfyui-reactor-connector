# Read recording details

Generation nodes return **Recording details** alongside their video. Its saved
socket name is `metadata`, so existing connections keep working. This output
is a JSON string. Connect it to a text display node if you want to inspect it or
use it in another part of your workflow. Saving the video does not automatically
save this separate text output.

## Fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Format version of the report. Current value: `1`. |
| `run_id` | Random local identifier for the execution. It gives no access to a Reactor session. |
| `node_id` | The connector node that produced the result. |
| `model_name` | The model connection name used for this execution. |
| `connector_version` | Connector version from its project metadata. |
| `sdk_version` | Installed Python `reactor-sdk` version. |
| `package_identity` | Content identifier from the installed package manifest, or `null` for a source checkout without that manifest. |
| `frames` | Number of frames written by the connector's encoder. |
| `width`, `height` | Saved video dimensions in pixels. |
| `file_bytes` | Size of the completed MP4, including any embedded audio. |
| `has_audio` | Whether the MP4 contains an audio track. A track can contain silence. |
| `timestamp_mode` | How the connector timed the recorded frames; see below. |

## Requested and saved lengths

`requested_duration_seconds` is the requested recording length. For continued
Fast H3 scenes, it is the requested clip length multiplied by the clip count.

`duration_seconds` is the length reported by the completed MP4's video stream,
or `null` if its header gives no duration.

These facts describe the completed output. Its duration may differ from the
request because a model chooses a supported clip length or ends early.
Dimensions and duration come from the saved file, rather than the prompt or
preview. A header report does not assess the quality of the generated content.

## Timing methods

- `sender`: the connector preserved the received frame timestamps.
- `fallback_fps`: the stream supplied no initial sender timestamp, so the
  connector used the model adapter's frame rate.
- `recording_pts`: the connector used timestamps from a downloaded Reactor
  recording to align saved video and sound.

Live controls can add a `live` object with counts of acknowledged actions,
preview frames, and control timing. An acknowledged action does not prove that
the requested change is visible in the video.

## Privacy and reuse

Reports omit prompts, input images, API keys, session tokens, remote session
IDs and absolute file paths.

ComfyUI can reuse a cached result, including its original report and `run_id`.
The report describes the execution that created the file; it does not prove
that the latest press of **Run** started a new paid session. Older cached
results may contain only `frames`, `timestamp_mode`, and model-specific fields.
Consumers should check `schema_version` and allow missing fields in those
older results. Do not rerun a model just to update its report.

Recording length is not billable session time. Setup, waiting, and recording
preparation can also use credits. This report is not an invoice or a charge
estimate. Use your Reactor account for billing information.
