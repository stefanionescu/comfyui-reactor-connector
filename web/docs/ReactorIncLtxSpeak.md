# LTX: Make a Portrait Speak (Reactor)

Animates one portrait speaking a script with Reactor's LTX model. The video has
the speech; a separate audio output carries it alone.

## Inputs

| Input                    | What it takes                                                                      |
| ------------------------ | ---------------------------------------------------------------------------------- |
| portrait image           | One clear RGB portrait with the whole head visible.                                |
| scene prompt             | Optional scene description, up to 800 characters.                                  |
| spoken words             | The script, 1 to 10,000 characters.                                                |
| video duration (seconds) | Saved length, from 4 to 60 seconds. Default: 5.                                    |
| words per minute         | Speech pace. Default: 140. Reactor's supported range is checked before generation. |
| seed                     | Integer from 0 to 4,294,967,295. Default: 42.                                      |
| run number               | Change it to run again with the same inputs.                                       |

Use a front-facing portrait of one person, at most 8,192 pixels per side and
within the upload limit in Reactor settings. LTX fits the picture to a wide
canvas, so a tall portrait can lose the top of the head. Fit the script to the
length: at 140 words per minute, five seconds holds about 11 words, and a longer
script can be cut off.

## Outputs

| Output | What it carries                                 |
| ------ | ----------------------------------------------- |
| video  | The speaking portrait, with sound.              |
| audio  | The speech as 48 kHz samples, in the same time. |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **ltx2-01-speaking-portrait** in **Browse Templates → reactor-inc**.
3. Upload a portrait in **Load Image** and edit **spoken words**.
4. Select **Run**, then play the result in **Save Video**.

LTX can generate up to 20 extra seconds while Reactor prepares the recording.
They use credits and are not saved, and the whole run must fit the session limit.

[Reactor LTX schema](https://docs.reactor.inc/model-api-reference/ltx/schema)
