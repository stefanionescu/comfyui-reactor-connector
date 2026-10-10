# Visko: Generate Video (Reactor)

Generates a scene with sound from Reactor's Visko Orbis model, from text or a
starting image. You can change the scene and the sound while it records.

## Inputs

| Input                    | What it takes                                                                       |
| ------------------------ | ----------------------------------------------------------------------------------- |
| model                    | `stable` or `dynamic`: Reactor's two versions of Visko Orbis. Default: `stable`.    |
| scene prompt             | The scene, 1 to 20,000 characters.                                                  |
| video duration (seconds) | Recording length, from 0.1 to 60 seconds. Default: 5.                               |
| seed                     | Integer from 0 to 4,294,967,295. Default: 42.                                       |
| run number               | Change it to run again with the same inputs.                                        |
| audio prompt             | A short description of the sound, up to 1,000 characters. Blank uses the picture.   |
| resolution               | Blank for the model default, or an exact resolution name the model offers.          |
| generate audio           | Generate sound when on; off gives a silent track. Default: on.                      |
| use prompt unchanged     | Send your exact scene prompt when on; off lets Reactor rewrite it first.            |
| starting image           | Optional. One RGB image, at most 8,192 pixels per side and within the upload limit. |
| live controls            | Change the scene and sound while it records. Default: off.                          |

Keep **audio prompt** to about one sentence; the model reads roughly the first
128 tokens. The connector checks the image, sound, and resolution Visko reports
at start and stops the run if they differ from your choices. Resolution names
are in the [Visko Orbis schema](https://docs.reactor.inc/model-api-reference/visko-orbis-stable/schema).

## Outputs

| Output | What it carries                                     |
| ------ | --------------------------------------------------- |
| video  | The recorded video, with sound.                     |
| audio  | The same recording's sound at 48 kHz, kept in sync. |

## Use

1. Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.
2. Open **visko-01-text-to-video**, **visko-02-image-to-video**, or
   **visko-03-live-prompt** in **Browse Templates → reactor-inc**.
3. Describe the scene and its sound, then select **Run**.
4. Play the result in **Save Video**; **Save Audio** keeps the sound alone.

Preparing the recording can add time after generation, and the whole session
must finish within the maximum session duration in Reactor settings.

## Live controls

Turn **live controls** on, select **Run**, then select **Start Session** in the
live panel within 60 seconds. **Apply Prompt** changes later frames, and **Apply
Audio Prompt** changes later sound. The preview is silent; play the saved video
to hear the result. Sound on or off and resolution stay fixed. Let recording
finish to save the result; **End Session** discards it.
