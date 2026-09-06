# Explore an image with LingBot

Choose the example for the model you want:

- [lingbot-01-explore-image](../../workflows/lingbot/lingbot-01-explore-image.json)
- [lingbot-world-2-01-explore-image](../../workflows/lingbot-world-2/lingbot-world-2-01-explore-image.json)
- [lingbot-02-live-camera](../../workflows/lingbot/lingbot-02-live-camera.json)
- [lingbot-world-2-02-live-camera](../../workflows/lingbot-world-2/lingbot-world-2-02-live-camera.json)

Upload one landscape, room, or path image in **Upload your starting image**. Describe that scene.
For the first run, use `forward` movement and leave both look directions at `idle`.
Select **Run** and inspect the saved clip for camera motion and scene consistency.

World 2 lets you move forward or back and sideways at the same time. Combine
`forward` with `strafe_left` or `strafe_right` to move diagonally. Choose a look
direction to keep turning; **Turn per step (degrees)** controls how fast you turn. Change one control at a time
when comparing results so you can identify its effect.

The `explore-image` graphs keep moving in your chosen directions while recording.
Clicking or dragging the saved video does not control the camera. Replaying a clip
does not reopen its world. The session ends when recording finishes.

The `live-camera` examples enable **Live controls** and request ten seconds of
video. Run opens the camera panel. Click its picture to use W A S D and arrow keys,
or hold its buttons. Let recording finish to save it. End session discards an
unfinished video. See [live controls](../live.md) for controls, connection errors,
and preview limits. You cannot drag the mouse to steer or reopen a saved world.

The live panel also has a **Scene prompt** field. Enter up to 1,000 characters
and select **Apply prompt** to change later frames. For example, use “A sunny
clearing opens ahead.” The initial image remains fixed, and the saved workflow
keeps its original prompt. Clicking the text field releases held camera movement.

Use one starting image. If you cannot see the camera move, try an image with clear
depth, such as a path or room, and allow more time for the model to show movement.

See the [LingBot node](../nodes/ReactorIncLingBotExplore.md) and
[World 2 node](../nodes/ReactorIncLingBotWorld2Explore.md) for exact controls.
