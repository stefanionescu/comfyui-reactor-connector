# Generate video with sound using Visko

Choose Stable or Dynamic, then choose text generation or image animation:

| Model | Text workflow | Image workflow |
| --- | --- | --- |
| Stable | [Video with sound](../../workflows/visko-orbis-stable/visko-stable-01-text-to-video.json) | [Animate an image](../../workflows/visko-orbis-stable/visko-stable-02-image-to-video.json) |
| Dynamic | [Video with sound](../../workflows/visko-orbis-dynamic/visko-dynamic-01-text-to-video.json) | [Animate an image](../../workflows/visko-orbis-dynamic/visko-dynamic-02-image-to-video.json) |

Describe the scene in **Scene prompt** and its sound in **Sound prompt**. A short sound
description such as flowing water or quiet footsteps is more useful than repeating
the scene description. Leave **Sound prompt** blank to let the picture guide sound.
For an image workflow, upload one picture and describe its intended motion.

Leave **Resolution** blank for the first run to use the model's default size.
If you enter a size, it must be one the connected model supports. Checking this
requires a session and can use credits even if the size is rejected.

Select **Run**. **Preview and save video** stores synchronized video and sound. **Preview and save sound** stores the separate sound track. Compare their durations and play
both. Turning **Include sound** off requests silence; it still returns an audio track.
Turning **Use prompt unchanged** on sends the scene prompt without Reactor rewriting it.

Reactor may need more time to prepare the recording after generating your video.
If the session reaches its time limit, the workflow returns an error and removes
unfinished files. Review the time limit and cost before deciding to run again.

The live-prompt workflows let you change the scene and sound while recording.
Choose [Stable](../../workflows/visko-orbis-stable/visko-stable-03-live-prompt.json) or
[Dynamic](../../workflows/visko-orbis-dynamic/visko-dynamic-03-live-prompt.json). Select **Start
session**, then use **Apply prompt** and **Apply sound prompt**. The live preview
has no sound; play the saved video to hear the result. Turn **Include sound** on before running to use live sound prompts. Resolution and sound on/off stay
fixed for the recording. These workflows do not provide pause and resume.

See the [Stable](../nodes/ReactorIncViskoStableGenerate.md) and
[Dynamic](../nodes/ReactorIncViskoDynamicGenerate.md) node guides for limits.


See the [workflow index](../../workflows/README.md) for every example, including
[live controls](../live.md).
