# LingBot: Explore an Image (Reactor)

Moves through a scene from your image with Reactor's LingBot model and saves
a video. Choose camera directions before the run, or steer live with keys and
buttons.

## Inputs

| Input                    | What it takes                                                                                      |
| ------------------------ | -------------------------------------------------------------------------------------------------- |
| starting image           | One picture to start from. Batches are not supported.                                              |
| scene prompt             | The scene and motion, 1 to 1,000 characters.                                                       |
| video duration (seconds) | Recording length, up to 60 seconds. Default: 5.                                                    |
| seed                     | Integer from 0 to 4,294,967,295. Default: 42.                                                      |
| run number               | Change it to run again with the same inputs.                                                       |
| movement                 | `forward`, `back`, `strafe_left`, `strafe_right`, or `idle` (stop).                                |
| turn left or right       | `left` or `right` keeps turning; `idle` stops.                                                     |
| look up or down          | `up` or `down` keeps tilting; `idle` stops.                                                        |
| turn per step (degrees)  | How fast the camera turns, from 0 to 30. Default: 5.                                               |
| live controls            | Steer live instead. Default: off. The camera starts still and the panel replaces the inputs above. |

Choose one movement direction at a time; in the live panel, forward or back wins over sideways. Camera changes show up as the model generates new frames, and a
direction stays on until you change it.

## Outputs

| Output | What it carries                    |
| ------ | ---------------------------------- |
| video  | The recorded video, without sound. |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **lingbot-01-explore-image** or **lingbot-02-live-camera** in **Browse
   Templates → reactor-inc**, and upload a picture in **Load Starting Image**.
3. Describe the scene, choose the length and directions, and select **Run**.
4. Play the result in **Save Video**, which also saves the file.

For a first run, use a picture of a path or room with clear depth, set
**movement** to `forward` and the other directions to `idle`, and record two
seconds. A saved video cannot reopen the scene.

## Live controls

Turn **live controls** on and select **Run**. When the live picture appears,
click it and use **W, A, S, D** to move and the **arrow keys** to look around, or
click a direction button briefly or hold it. **Escape**, leaving the window, or
hiding the tab releases held movement. **Apply Prompt** changes later frames, up
to 1,000 characters; the starting image and the saved workflow stay as they
were. Let recording finish to save the video; **End Session** discards it. The
preview shows up to ten frames per second at up to 640 × 360 pixels.

[Reactor LingBot schema](https://docs.reactor.inc/model-api-reference/lingbot/schema)
