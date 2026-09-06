# Reactor LongLive: Add a shot

Add a later shot to a LongLive storyboard. This node prepares the shot list locally;
it does not need a key, start a model session, or use credits.

## Build a sequence

Connect **Add a shot** nodes in order. **Previous steps (JSON)** is an advanced
control for entering a list directly. To show it, right-click the node and
choose **Show Advanced**. The examples do not require editing JSON.

1. Leave **Previous steps (JSON)** unconnected for the first later shot.
2. Choose when the shot starts in **Start chunk**, then set its transition and prompt.
3. Connect the **Storyboard** output to another Reactor LongLive: Add a shot node's **Previous steps (JSON)**
   input to add another shot, or to Reactor LongLive: Create a storyboard to generate the video.
4. Set the opening prompt and video length on the generation node.

| Input | Meaning |
| --- | --- |
| Previous steps (JSON) | The earlier shot list. Default: `[]`. Connect another Reactor LongLive: Add a shot node to extend its list. |
| Start chunk | Chunk number from the start of generation, from 1 to 100,000. Each later shot needs a larger number. Default: 1. |
| Transition | `soft` changes the prompt within the scene. `cut` starts a new scene. Default: soft. |
| Scene prompt | The later shot's description, from 1 to 20,000 characters. |

The output is a `STRING` containing a validated JSON shot list. It can be saved
inside a normal workflow. Lists contain at most 32 later shots and 128 KB.
Unknown fields, duplicate keys, repeated indices, descending order, and empty
prompts are rejected. The opening shot is configured on the generation node;
do not add it here at chunk zero.

LongLive generates frames in groups called chunks. Each chunk contains 29 frames,
about 1.2 seconds at 24 frames per second. Record long enough to include the later
shots. A shot at chunk 20 will not appear in a two-second video.

Example: add a soft pullback at chunk 1, then a cut to a lake at chunk 2. Connect
the list to Reactor LongLive: Create a storyboard and record five seconds. Watch
the resulting transitions; this node alone does not produce video.

If the list is invalid, check ordering and connect the previous node's output
instead of copying and editing its JSON.

[LongLive schema](https://docs.reactor.inc/model-api-reference/longlive-v2/schema)
