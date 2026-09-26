"""The English titles, node names, and notes written into the example workflows."""

TITLES = {
    "fast-h3-01-text-to-video": "Fast H3: Generate a Clip with Audio",
    "fast-h3-02-image-to-video": "Fast H3: Animate an Image",
    "fast-h3-03-first-and-last-frames": "Fast H3: Connect Two Images with Motion",
    "fast-h3-04-ending-frame": "Fast H3: Finish on a Chosen Image",
    "fast-h3-05-continue-scene": "Fast H3: Continue a Scene",
    "fast-h3-06-continue-image": "Fast H3: Continue from an Image",
    "helios-01-text-to-video": "Helios: Generate Video",
    "helios-02-image-to-video": "Helios: Animate an Image",
    "helios-03-prompt-sequence": "Helios: Follow a Prompt Sequence",
    "helios-04-image-sequence": "Helios: Animate an Image with a Prompt Sequence",
    "helios-05-live-prompt": "Helios: Change the Prompt While Recording",
    "helios-06-live-image": "Helios: Animate an Image with Live Prompts",
    "lingbot-01-explore-image": "LingBot: Explore an Image",
    "lingbot-02-live-camera": "LingBot: Explore an Image with Live Controls",
    "lingbot-world-2-01-explore-image": "LingBot World 2: Explore an Image",
    "lingbot-world-2-02-live-camera": "LingBot World 2: Explore an Image with Live Controls",
    "longlive-v2-01-text-to-video": "LongLive: Generate Video",
    "longlive-v2-02-storyboard": "LongLive: Generate Video with Shot Transitions",
    "longlive-v2-03-live-prompt": "LongLive: Change the Prompt While Recording",
    "ltx2-01-speaking-portrait": "LTX: Make a Portrait Speak",
    "sana-streaming-01-edit-video": "SANA: Edit Video",
    "sana-streaming-02-live-prompt": "SANA: Change the Prompt While Recording",
    "sana-streaming-03-webcam": "SANA: Edit Webcam Video",
    "visko-dynamic-01-text-to-video": "Visko Dynamic: Generate Video with Audio",
    "visko-dynamic-02-image-to-video": "Visko Dynamic: Animate an Image with Audio",
    "visko-dynamic-03-live-prompt": "Visko Dynamic: Change the Prompt While Recording",
    "visko-stable-01-text-to-video": "Visko Stable: Generate Video with Audio",
    "visko-stable-02-image-to-video": "Visko Stable: Animate an Image with Audio",
    "visko-stable-03-live-prompt": "Visko Stable: Change the Prompt While Recording",
    "x2-01-edit-video": "X2: Edit Video",
    "x2-02-reference-edit": "X2: Edit with a Reference Image",
    "x2-03-webcam": "X2: Edit Webcam Video with Pointer Controls",
    "x2-04-live-prompt": "X2: Drag and Edit a Video",
}

LIMITS = {
    "continuation": (
        "The {clips} clips continue from each previous final frame. Put one prompt per line in **later clip "
        "prompts**, starting with clip 2. Leave it empty to repeat the opening prompt."
    ),
    "fast": (
        "Fast H3 rounds each clip to a supported length. Saving starts one extra continuation that uses credits and "
        "is excluded from the output."
    ),
    "helios": (
        "Each Helios chunk contains 33 frames. Connect prompts in order and use increasing **start chunk** values. "
        "The opening prompt starts at chunk 0. Later prompts do not extend the recording."
    ),
    "longlive": (
        "Each LongLive chunk is about 1.2 seconds at 24 fps. The soft transition starts near 1.2 seconds; the hard "
        "cut near 2.4 seconds. Increase **video duration (seconds)** if you schedule later shots."
    ),
    "ltx": (
        "Use a clear portrait with the whole head visible. Finishing the recording may generate up to 20 extra "
        "seconds that use credits and are not saved."
    ),
    "sourceVideo": "Use standard dynamic range (SDR) video. The edited output has no sound.",
    "totalDuration": (
        "This example requests {seconds:g} seconds in total. The model may round each clip up; the combined "
        "length must be 60 seconds or less."
    ),
}

LIVE = {
    "camera": (
        "Select **Enable Camera**, allow access, then **Start Session**. Reactor receives camera video without "
        "microphone audio."
    ),
    "drag": (
        "Drag on the output to steer the subject. Escape releases the pointer. **Info** also explains keyboard "
        "controls."
    ),
    "editPrompt": "Change **edit prompt**, then select **Apply Prompt** to change later frames.",
    "examplePrompt": "Try: {prompt}",
    "finish": "Let recording finish to save the video. **End Session** stops early and discards it.",
    "move": (
        "This controls a virtual camera, not your webcam. In the live panel, click the picture. W A S D moves; arrow "
        "keys turn. Escape stops movement. **Apply Prompt** changes later frames."
    ),
    "prompt": "Edit **scene prompt**, then select **Apply Prompt** to change later frames.",
    "sound": "**Apply Audio Prompt** changes later sound. The live preview is silent.",
    "start": "In the live panel, select **Start Session** within 60 seconds.",
}

NODES = {
    "clearing": "2. Enter a Clearing",
    "endingImage": "Load Final Image",
    "hardCut": "2. Hard Cut",
    "portraitImage": "Load Portrait Image",
    "referenceImage": "Load Reference Image",
    "saveAudio": "Save Audio",
    "saveVideo": "Save Video",
    "softTransition": "1. Soft Transition",
    "sourceVideo": "Load Source Video",
    "startingImage": "Load Starting Image",
    "sunlight": "1. Let Sunlight Through",
}

NOTES = {
    "start": "Start Here",
    "usage": "Using This Workflow",
}

SETUP = {
    "editPrompt": "Describe the change you want in **edit prompt**.",
    "endingImage": "Upload the ending image in **{title}**.",
    "image": "Upload an image in **{title}**.",
    "key": "Set your key in **ComfyUI menu → Extensions → Reactor → Reactor settings**.",
    "live": "Select **Run** to open the live panel.",
    "portrait": "Upload a portrait in **{title}**.",
    "prompt": "Edit **scene prompt** to describe the scene or change you want.",
    "record": "Select **Run** to create and save the video.",
    "reference": "Upload the subject to insert in **{title}**.",
    "sequence": "Edit the opening prompt, **{first}**, and **{second}**.",
    "shots": "Edit the opening prompt, **{first}**, and **{second}**.",
    "speech": "Edit **spoken words**. Keep the speech short enough for five seconds.",
    "video": "Upload a video in **{title}** (at least 33 frames).",
    "viskoImage": (
        "Edit **scene prompt** to name what is in your image and describe its motion. The example prompt describes a "
        "forest path."
    ),
}
