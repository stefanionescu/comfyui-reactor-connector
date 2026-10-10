# Helios: Add a Prompt (Reactor)

Adds a later prompt to a Helios prompt sequence. It runs locally and opens no
Reactor session.

## Inputs

| Input                   | What it takes                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------ |
| previous prompts (JSON) | Earlier prompts from another **Add a Prompt** node. Default: `[]`.                   |
| start chunk             | When this prompt starts, from 1 to 100,000. Each later prompt needs a larger number. |
| scene prompt            | The scene after the change, 1 to 20,000 characters.                                  |

**previous prompts (JSON)** is an advanced input: select the node, open the
properties panel, and expand **Advanced inputs** to type a list. A Helios chunk
is 33 frames, and the opening prompt on the generation node is chunk 0. A
sequence holds up to 32 later prompts and 128 KB. The node rejects unknown
fields, duplicate keys, empty prompts, and chunk numbers that repeat or go down.

## Outputs

| Output          | What it carries                                                               |
| --------------- | ----------------------------------------------------------------------------- |
| prompt sequence | The prompt list, for the next **Add a Prompt** or **Helios: Generate Video**. |

## Use

1. Keep `[]` in **previous prompts (JSON)** for the first later prompt, then set
   **start chunk** and **scene prompt**.
2. Connect **prompt sequence** to the next **Add a Prompt** node's **previous
   prompts (JSON)**.
3. Connect the last **prompt sequence** to **prompt sequence (JSON)** on
   **Helios: Generate Video (Reactor)**, where you set the opening prompt and
   length.

**helios-03-prompt-sequence** adds sunlight at chunk 1 and a clearing at chunk 3
in an eight-second recording. A prompt that starts after the recording ends does
not appear. A LongLive storyboard does not fit here; its format is different.

[Helios command reference](https://docs.reactor.inc/model-api-reference/helios/schema)
