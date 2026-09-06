# Make a portrait speak with LTX

Open [ltx2-01-speaking-portrait](../../workflows/ltx2/ltx2-01-speaking-portrait.json).
Upload a clear, front-facing portrait of one person in **Upload your starting image**. Use a wide
composition with the whole head visible: fitting a tall portrait to LTX's canvas
can crop the head. The graph does not require a separately supplied voice file.

Enter the spoken words in **Spoken words**. The **Scene prompt** describes the scene and delivery;
it does not replace the speech script. For a first five-second run, keep the script
to a short sentence, such as the supplied greeting. At 140 words per minute, five
seconds allows about 11 words. An overlong script can be cut off.

Select **Run**, then inspect **Preview and save video** for portrait identity, lip motion, and
framing. Play the sound and check that all requested words are present. **Preview and save sound** saves speech separately. Check that the lip movements match the speech.

The saved recording must be at least four seconds. The connector allows up to twenty
extra generation seconds so the recording can become ready. Those seconds can use
credits and are omitted from the saved video. The deployment reports its accepted
speech pace before generation. Generation and recording must finish within the
host session limit. A finished speech video may still need time before its recording
can be downloaded. A failed recording returns no partial result.

See [LTX Speak](../nodes/ReactorIncLtxSpeak.md) for exact controls and cancellation.
