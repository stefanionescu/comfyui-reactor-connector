# Generate or animate with Helios

## Start with one prompt

Open [helios-01-text-to-video](../../workflows/helios/helios-01-text-to-video.json) for a
text-only scene. Describe one subject, its movement, and the camera. For example:
“A red ball rolls slowly across a wooden table. The camera follows the ball.”
Select **Run**, then play the five-second result in **Preview and save video**.

Open [helios-02-image-to-video](../../workflows/helios/helios-02-image-to-video.json) to
animate your picture. In **Upload your starting image**, select **choose file to upload**. Describe
the existing subject and the movement you want. A prompt that describes an unrelated
scene gives the model conflicting instructions. Connect one image, not a batch.

Both workflows save video without audio. Inspect the beginning and end for subject
identity and motion. Changing the seed changes generation; it is not a guarantee
of identical results after a provider revision. Change **Variation** to request a
new paid execution with the same seed.

If the graph reports a missing image, choose a local file. If generation times out,
check provider status and the host session limit before deciding to spend credits
on a retry. The connector does not automatically retry uncertain sessions.

See the [text node](../nodes/ReactorIncHeliosGenerate.md) and
[image node](../nodes/ReactorIncHeliosAnimate.md) for limits and cleanup behavior.

## Prepare prompt changes

Open [helios-03-prompt-sequence](../../workflows/helios/helios-03-prompt-sequence.json)
to change the scene automatically. The opening prompt describes a forest path.
**1. Let sunlight through** adds sunlight at chunk 1; **2. Enter a clearing**
changes the scene at chunk 3. Edit all three prompts to keep the scene consistent.

Helios groups output into chunks of 33 frames. The two builder nodes prepare
their changes locally, then the generation node sends the complete sequence
before starting. The example records eight seconds without audio. Choose
increasing chunk numbers; later changes do not extend the recording.

Open [helios-04-image-sequence](../../workflows/helios/helios-04-image-sequence.json)
to start the sequence from your own picture. Upload it in **Upload your starting
image** and adapt the prompts to match. The reference stays the same for the
whole sequence. The loader sits below the generation node; use **Fit View** if it
is outside your current view.

Read the [prompt builder](../nodes/ReactorIncHeliosAddPrompt.md) and
[sequence node](../nodes/ReactorIncHeliosSequence.md) guides for all inputs.

## Change prompts while watching

See the [workflow index](../../workflows/README.md) for every example, including
[live controls](../live.md).
