# LongLive: Add a Shot (Reactor)

Adds a later shot to a LongLive storyboard. It runs locally and opens no Reactor
session.

## Inputs

| Input                 | What it takes                                                                    |
| --------------------- | -------------------------------------------------------------------------------- |
| previous shots (JSON) | Earlier shots from another **Add a Shot** node. Default: `[]`.                   |
| start chunk           | When this shot starts, from 1 to 100,000. Each later shot needs a larger number. |
| transition            | `soft` changes the prompt within the scene; `cut` starts a new scene.            |
| scene prompt          | The shot, 1 to 20,000 characters.                                                |

**previous shots (JSON)** is an advanced input: select the node, open the
properties panel, and expand **Advanced inputs** to type a list. A LongLive chunk
is 29 frames, about 1.2 seconds, counted from the start of generation. The
opening shot is set on the generation node; do not add it here. A list holds up
to 32 later shots and 128 KB, and the node rejects unknown fields, duplicate
keys, empty prompts, and chunk numbers that repeat or go down.

## Outputs

| Output | What it carries                                                             |
| ------ | --------------------------------------------------------------------------- |
| shots  | The shot list, for the next **Add a Shot** or **LongLive: Generate Video**. |

## Use

1. Keep `[]` in **previous shots (JSON)** for the first later shot, then set
   **start chunk**, **transition**, and **scene prompt**.
2. Connect **shots** to the next **Add a Shot** node's **previous shots (JSON)**.
3. Connect the last **shots** to **shots (JSON)** on **LongLive: Generate Video
   (Reactor)**, where you set the opening prompt and length.

**longlive-v2-02-storyboard** adds a soft pullback at chunk 1 and a cut to a lake
at chunk 2 in a five-second recording. Record long enough to reach every shot: a
shot at chunk 20 does not appear in a two-second video.

[LongLive schema](https://docs.reactor.inc/model-api-reference/longlive-v2/schema)
