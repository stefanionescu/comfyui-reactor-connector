# Reactor Helios: Add a Prompt

Add a later prompt to a Helios sequence. This node prepares text locally.

## Build a sequence

Connect **Add a prompt** nodes in order. **Previous steps (JSON)** is an advanced
control for entering a list directly. To show it, right-click the node and
choose **Show Advanced**. The examples do not require editing JSON.

1. Leave **Previous steps (JSON)** unconnected for the first later prompt.
2. Choose its **Start chunk** number and describe the scene in **Scene prompt**.
3. Connect **Prompt sequence** to the next Add a prompt node's **Previous steps (JSON)** input.
4. Connect the last Add a prompt node to **Reactor Helios: Generate a Prompt Sequence**.
   Set the opening prompt and recording length on that generation node.

| Input                 | Meaning                                                                                              |
| --------------------- | ---------------------------------------------------------------------------------------------------- |
| Previous steps (JSON) | Earlier prompts from another Add a prompt node. Default: `[]`.                                       |
| Start chunk           | When this later prompt starts, from 1 to 100,000. Each new prompt needs a larger number. Default: 1. |
| Scene prompt          | The scene and motion after the change, from 1 to 20,000 characters.                                  |

The **Prompt sequence** output contains a JSON prompt list. It can contain
up to 32 later prompts within 128 KB. The connector rejects unknown fields,
duplicate keys, empty prompts, and repeated or descending chunk numbers.

Helios generates frames in groups called chunks. A chunk contains 33 frames.
The generation node sets the opening prompt at chunk zero; add only later
prompts here. A prompt scheduled after recording ends will not appear in the file.

For example, add sunlight at chunk 1, then a clearing at chunk 3. Open the
[prompt-sequence workflow](/reactor-inc/v1/help/files/workflows/helios/helios-03-prompt-sequence.json) for
connected nodes and an eight-second recording.

If a sequence is rejected, check the chunk order and connect the previous
node's output. Do not connect a LongLive storyboard: its format is different.

[Helios command reference](https://docs.reactor.inc/model-api-reference/helios/schema)
