# Use live controls

Live controls let you change a running Reactor session from the ComfyUI window
that started it, in Comfy Desktop or a browser. Choose a recording duration first. Every session has a time
limit; leaving a panel open does not extend it.

## Choose a workflow

| Task | Workflow or node |
| --- | --- |
| Move through an image with keys or buttons | LingBot and LingBot World 2 live-camera workflows |
| Change a scene prompt while recording | Helios, LongLive, and Visko live-prompt workflows; LingBot live-camera workflows |
| Change an edit while a local clip plays | SANA live-prompt workflow |
| Drag on an edited video | X2 live-prompt workflow |
| Edit your camera input | SANA and X2 webcam workflows |
| Continue a scene across connected clips | Fast H3 continued-scene workflows |

Find all files in the [workflow index](../workflows/README.md). Ordinary Helios,
LongLive, Visko, SANA, and X2 nodes also have a **Live controls** switch. Turn it
on to use the live panel. It is off by default. LongLive storyboards keep their
scheduled shot sequence.

## Change prompts and use a webcam

1. Set the prompt and duration, then select **Run**.
2. For a webcam node, select **Enable camera** and allow camera access.
3. Check the input preview. To switch cameras, choose one and select **Use selected camera**.
4. Select **Start session** within 60 seconds. Reactor credits start being used when the session connects.
5. Once controls are ready, enter a live prompt and select **Apply prompt**.
6. Let recording finish to save the result.

Prompt changes affect later frames; they do not rewrite recorded video. LongLive
uses a soft shot transition. Visko keeps the node's **Use prompt unchanged** choice.
The initial image or reference stays fixed for the session. Changes made in the
panel do not rewrite the saved workflow's prompt.

Webcam input requires localhost or HTTPS, camera permission, and a local,
single-user ComfyUI installation. The panel requests video only. It sends camera
frames to the local host before you start, and the host sends them to Reactor
only during the paid session. No microphone audio or separate camera recording
is saved. Camera access stops when the panel closes or the recording ends.

Camera input uses up to 640 × 480 pixels and at most ten new frames per second.
The connector repeats the latest frame on a 24 fps input. The saved output uses
the model's output resolution. The separate output preview uses up to ten frames
per second at up to 640 × 360 pixels and has no sound.

## Change sound in Visko

Turn **Include sound** on before running a Visko live-prompt workflow. Once
recording starts, describe the sound in **Sound prompt** and select **Apply sound
prompt**. Leave it blank to let the picture guide sound. Changes affect later
sound in the saved video. The live preview has no sound.

Resolution and sound on/off are fixed when generation starts. Set them on the
node before running. Changing them requires a new run, which uses credits.

## Drag in X2

Drag on the output picture to steer the edited subject. Release to stop.
For keyboard control, focus the picture, use arrow keys to position the pointer,
and hold Space to activate it. Escape releases the pointer. Losing focus also
releases it. X2 applies input to later groups of frames, so its response can lag.

A circle marks the point you choose. Its position is measured from the left and
top edges of the picture. **Pointer held** or **Pointer released** confirms that
the control was accepted; watch later frames to judge its effect.

## Move in LingBot

Open a LingBot live-camera workflow, upload an image, and select Run. Click the
picture. W and S move forward and back; A and D move sideways. Arrow keys turn
the camera. Click a direction button for a brief movement or hold it to keep
moving. Escape releases movement. LingBot World 2 supports independent sideways
and forward movement.

Rapid direction changes can skip earlier movements. The controls release old
movement before applying your latest direction.

To change the scene, edit **Scene prompt** and select **Apply prompt**. Both
LingBot models apply the new text to later frames. For example, change a forest
path to “A sunny clearing opens ahead.” The starting image remains fixed. Editing
the prompt releases held camera movement and does not rewrite the saved workflow.

## Save or stop

Let the chosen duration finish. The connected **Preview and save video** node
saves the result under ComfyUI's output folder. **End session** stops early and
discards the unfinished video. ComfyUI cancellation also ends the run.

Live controls release held input after the ComfyUI window loses contact. Five seconds
without a panel heartbeat ends the session; webcam input also ends after three
seconds without a new frame. Provider cleanup can take longer. Wait for the
session-end message. If termination cannot be confirmed, check Reactor Usage
and wait for the session time limit before trying again.

Running an unchanged workflow may reuse a cached result. Change **Variation** to
request another paid session. The connector does not automatically reconnect.
Your Reactor API key stays on the ComfyUI server. The live panel receives access
only to its own session, and multi-user mode is not supported.

## Continue a scene

Fast H3 can [chain a chosen number of clips](nodes/ReactorIncFastContinue.md)
without another ComfyUI run. It uses the previous clip's final frame to continue
the scene. It does not provide unlimited recording.

