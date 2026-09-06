# Build shots with LongLive

Start with [longlive-v2-01-text-to-video](../../workflows/longlive-v2/longlive-v2-01-text-to-video.json).
Describe the opening shot and motion, then select **Run**. This example generates
one scene from your prompt and saves video without audio.

Use [longlive-v2-02-storyboard](../../workflows/longlive-v2/longlive-v2-02-storyboard.json) to
schedule later shots. **1. Soft transition** requests a camera pullback at chunk 1. **2. Hard cut**
requests a cut to a lake at chunk 2. Both connect to
**LongLive: Soft transition and hard cut**. Building the schedule uses no credits;
executing the video node does.

Connect the shot nodes in order, using increasing chunk numbers. A chunk contains
29 generated frames, about 1.2 seconds at 24 frames per second. The five-second
example should reach both scheduled changes. A shot scheduled after your chosen
video length will not appear. Add more recording time to include it.

A soft transition changes the prompt within the scene. A cut begins a new scene.
Play the video to see each change. The model may interpret a shot differently
from what you described.

If a shot is missing, check its chunk number and the video length. Describe shots
with text; this workflow does not accept a starting image.

See [Storyboard](../nodes/ReactorIncLongLiveStoryboard.md) and
[Reactor LongLive: Add a shot](../nodes/ReactorIncLongLiveAddShot.md) for schedule limits.


See the [workflow index](../../workflows/README.md) for every example, including
[live controls](../live.md).
