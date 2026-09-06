# Edit a local video with SANA

Open [sana-streaming-01-edit-video](../../workflows/sana-streaming/sana-streaming-01-edit-video.json).
In **Upload your source video**, upload a short standard dynamic range (SDR) clip with at least 33 frames. Start
with a clear subject and simple motion. Describe the edit, such as changing the
scene to a watercolor painting while retaining its composition and movement.

Select **Run** and play the result in **Preview and save video**. The connector prepares your
clip, checks how the connected model accepts video, and sends it to Reactor.
The output has no sound.

Leave the prompt empty to ask SANA to recreate the original video. Use this to see
how closely the result follows your clip before asking for changes.
**Anchor interval** controls how often the model returns to the source image;
read the node guide before changing it. Keep both video lengths within the limits
in Reactor settings. If the source clip ends before recording stops, its last
frame stays on screen as the model's input.

If the source is too short or unsupported, the node rejects it before connection.
If the model no longer accepts the input, read the error and check for a connector
update. This example uses a local clip; use the webcam workflow to edit a camera instead.

See [SANA Edit Video](../nodes/ReactorIncSanaEditVideo.md) for format, frame,
memory, source completion, and cancellation details.


See the [workflow index](../../workflows/README.md) for every example, including
[live controls](../live.md).
