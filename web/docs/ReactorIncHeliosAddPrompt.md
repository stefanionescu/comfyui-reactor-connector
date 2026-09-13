# Helios: Add a Prompt (Reactor)

Add a later prompt to a Helios sequence. This node prepares text locally.

## Build a sequence

Connect **Add a Prompt** nodes in order. **previous prompts (JSON)** is an advanced
control for entering a list directly. Select the node, open the properties panel,
and expand **Advanced inputs** under **Parameters**. The examples do not require
editing JSON.

1. Keep `[]` in **previous prompts (JSON)** for the first later prompt.
2. Choose its **start chunk** number and describe the scene in **scene prompt**.
3. Connect **prompt sequence** to the next Add a Prompt node's **previous prompts (JSON)** input.
4. Connect the last **prompt sequence** output to **prompt sequence (JSON)** on
   **Helios: Generate Video from a Prompt Sequence (Reactor)**.
   Set the opening prompt and recording length on that generation node.

| Input                   | Meaning                                                                                              |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| previous prompts (JSON) | Earlier prompts from another Add a Prompt node. Default: `[]`.                                       |
| start chunk             | When this later prompt starts, from 1 to 100,000. Each new prompt needs a larger number. Default: 1. |
| scene prompt            | The scene and motion after the change, from 1 to 20,000 characters.                                  |

The **prompt sequence** output contains a JSON prompt list. It can contain
up to 32 later prompts within 128 KB. The connector rejects unknown fields,
duplicate keys, empty prompts, and repeated or descending chunk numbers.

Helios generates frames in groups called chunks. A chunk contains 33 frames.
The generation node sets the opening prompt at chunk zero; add only later
prompts here. A prompt scheduled after recording ends will not appear in the file.

For example, add sunlight at chunk 1, then a clearing at chunk 3. Open the
**helios-03-prompt-sequence** in native **Browse Templates → reactor-inc** for
connected nodes and an eight-second recording.

If a sequence is rejected, check the chunk order and connect the previous
node's output. Do not connect a LongLive storyboard: its format is different.

[Helios command reference](https://docs.reactor.inc/model-api-reference/helios/schema)
