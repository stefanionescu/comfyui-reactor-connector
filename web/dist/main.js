// web/extension.ts
import { api as api2 } from "../../scripts/api.js";
import { app as app3 } from "../../scripts/app.js";

// web/language.ts
import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

// locales/en/main.json
var main_default = {
  reactorInc: {
    help: "Help",
    "settings.title": "Reactor settings",
    "models.title": "Reactor models",
    "settings.invalidResponse": "ComfyUI returned an invalid Reactor settings response.",
    "settings.incompleteResponse": "ComfyUI returned incomplete Reactor settings.",
    "settings.invalidDefinition": "ComfyUI returned an invalid Reactor setting definition.",
    "settings.invalidChecks": "ComfyUI returned invalid model check settings.",
    "settings.invalidLimit": "ComfyUI returned an invalid Reactor limit.",
    "settings.unreachable": "Cannot reach Reactor settings. Check ComfyUI and try again.",
    "settings.unreadableResponse": "ComfyUI returned an unreadable Reactor settings response.",
    "settings.saveFailed": "ComfyUI could not save Reactor settings.",
    "settings.loading": "Loading local settings…",
    "settings.reload": "Reload settings",
    close: "Close",
    "settings.close": "Close Reactor settings",
    "settings.loaded": "Local settings loaded.",
    "settings.accountNotice": "Reactor uses its own account and credits. Opening settings and saving a key do not start generation.",
    "settings.keyNotice": "The saved key stays on the ComfyUI server. An environment key takes precedence. Keys are not checked with Reactor here.",
    "settings.timeNotice": "Session time includes setup and generation. These limits do not buy credits or change account billing.",
    "settings.credentialLabel": "Reactor API key",
    "settings.clearKey": "Clear saved key",
    "settings.keyCleared": "Saved key cleared. Any environment key remains active.",
    "settings.saveKey": "Save key",
    "settings.credentials": "Credentials",
    "settings.keySaved": "Key saved on this server. Reactor checks it when you start a session.",
    "settings.limits": "Execution limits",
    "settings.saveLimits": "Save limits",
    "settings.advancedLimits": "Advanced limits",
    "settings.noLimitChanges": "No limit changes to save.",
    "settings.limitsSaved": "Limits saved. They apply to new executions.",
    "settings.automaticChecks": "Check for model updates automatically",
    "settings.checkInterval": "Check interval (hours)",
    "settings.modelUpdates": "Model updates",
    "settings.checkNotice": "Checks read public prices and model guides. They do not use your key or spend credits. Open Reactor models to see changes and refresh your list.",
    "settings.saveChecks": "Save model check settings",
    "settings.noCheckChanges": "No model check changes to save.",
    "settings.checksSaved": "Model check settings saved. The scheduler reads changes within one minute.",
    "settings.missingKey": "No Reactor key is configured.",
    "settings.savedKey": "A saved key is configured on this server.",
    "settings.environmentKey": "The server's REACTOR_API_KEY environment variable is active.",
    "settings.readOnly": "Changes are disabled in this host's multi-user mode.",
    working: "Working…",
    "settings.updateFailed": "Reactor settings could not be saved.",
    "nodes.seedBehavior": "Seed behavior",
    "models.nodesAvailable": "Nodes available.",
    "models.nodeUnavailable": "No connector node available.",
    "models.openGuide": "Reactor model guide (opens in a new tab)",
    "models.guideUnavailable": "No matching public guide was found.",
    "pricing.rateUnavailable": "A current rate is not available. Refresh Reactor models to check for a rate.",
    "pricing.rateOutdated": "This rate was not found in the latest source check. Refresh Reactor models before relying on a calculation.",
    "models.invalidResponse": "ComfyUI returned an invalid Reactor model list.",
    "models.installedList": "Showing installed nodes. Refresh models to load public prices and guides.",
    "models.unreachable": "Cannot reach the Reactor model list. Check ComfyUI and try again.",
    "models.requestFailed": "The model list request failed.",
    "pricing.loading": "Loading the local credit rate…",
    "pricing.title": "Credit rate",
    "pricing.unknownDuration": "The video length comes from a connected input or is not available. Enter a session time below to calculate credits.",
    "pricing.sessionTime": "Session time to calculate (seconds)",
    "pricing.enterTime": "Enter total paid session time",
    "pricing.estimateNotice": "This is rate × time, not an exact charge or a spending limit. The starting time uses the requested video length and excludes extra paid time. Your Reactor account shows actual charges.",
    "pricing.modelUnavailable": "No rate is listed for this node. Open the ComfyUI menu, then Extensions → Reactor → Reactor models, and refresh the list.",
    "pricing.loadFailed": "Cannot load the credit rate.",
    "pricing.viewRate": "View credit rate",
    "models.checksOff": "Automatic model checks are off. Change this in Reactor settings.",
    "models.checkRunning": "An automatic model check is running. Reopen this list to see its result.",
    "models.listChanged": "The model list has changed. Select Refresh models to update your list.",
    "models.checkDue": "An automatic model check is due. Checks do not change this list.",
    "models.refresh": "Refresh models",
    "models.restore": "Restore previous list",
    "models.loadingLocal": "Loading the local model list…",
    "models.close": "Close Reactor models",
    "models.search": "Search models",
    "models.searchPlaceholder": "Name or connect name",
    "models.sources": "Model sources and automatic checks",
    "models.refreshNotice": "Refresh checks Reactor's public model list and prices. It sends no API key and uses no credits. New models need a compatible connector node.",
    "models.showAll": "Show all models",
    "pricing.calculate": "Calculate credits for session time",
    "pricing.totalTimeNotice": "Use total session time, including setup, pauses, and recording. Saved video length may be shorter. This estimate is not a spending limit or a quote.",
    "models.checking": "Checking public model sources…",
    "models.loading": "Loading model list…",
    "models.refreshed": "Model list refreshed. No generation started.",
    "models.restored": "Previous model list restored. This does not change which models Reactor offers.",
    "models.loaded": "Local model list loaded.",
    "models.loadFailed": "Cannot load models.",
    "live.actionRejected": "The live action was not accepted. The session is ending.",
    "pointer.held": "Pointer held.",
    "pointer.released": "Pointer released.",
    "pointer.stopped": "Pointer controls stopped.",
    "camera.enable": "Enable camera",
    "camera.label": "Camera ",
    "camera.default": "Default camera",
    "camera.preview": "Your camera input",
    "camera.select": "Use selected camera",
    "camera.enabled": "Camera on. Microphone audio is off.",
    "camera.accessFailed": "Camera access failed. Choose a camera and try again.",
    "camera.browserRequirements": "Camera access needs localhost or HTTPS and a supported browser.",
    "camera.disconnected": "The camera disconnected. The session is ending.",
    "camera.readFailed": "Camera frames could not be read.",
    "camera.uploadFailed": "Camera frames could not reach the session.",
    "camera.disabled": "Camera off.",
    "live.unreachable": "Live controls could not reach their session.",
    "live.invalidStatus": "The live panel received an invalid status.",
    "pointer.instructions": "Drag on the output to move the subject. Use arrow keys to position the pointer, Space to hold it, and Escape to release it.",
    "live.connectingPanel": "Connecting the live panel…",
    "live.applyPrompt": "Apply prompt",
    "live.promptNotice": "Prompt changes affect later frames. The starting image stays fixed.",
    "live.endSession": "End session",
    "live.cameraTitle": "Reactor live camera",
    "live.movementLabel": "Live view. W A S D moves. Arrow keys turn. Escape stops camera movement.",
    "live.output": "Live model output",
    "live.forward": "Forward",
    "live.back": "Back",
    "live.moveLeft": "Move left",
    "live.moveRight": "Move right",
    "live.lookLeft": "Look left",
    "live.lookRight": "Look right",
    "live.lookUp": "Look up",
    "live.lookDown": "Look down",
    "live.scenePrompt": "Scene prompt ",
    "live.movementInstructions": "Click the picture, then use W A S D to move and arrow keys to turn. Click a button for a brief movement, or hold it to keep moving. Escape stops camera movement.",
    "live.recordingNotice": "The preview has fewer frames per second than the saved video and has no sound. Save Video saves the finished recording. Setup and recording use credits. Ending early discards the unfinished video.",
    "live.emptyScenePrompt": "Enter a scene prompt before applying it.",
    "live.ending": "Ending the session…",
    "live.previewReady": "Live preview. Controls are active.",
    "live.waitingVideo": "Waiting for model video…",
    "live.unconfirmedEnd": "Reactor has not confirmed that the session ended. Wait for its time limit before another run.",
    "live.discarded": "The session ended without saving a video. Close this panel to view the workflow result.",
    "live.ended": "Session ended. Close this panel to view the workflow result.",
    "live.promptSent": "Prompt sent. Watch the video for the change.",
    "live.connectionLost": "The live connection was lost. The connector will ask Reactor to stop after five seconds without a browser connection. Check Reactor Usage to confirm the session has ended before another run.",
    "controls.chooseInput": "Choose your input, then start within 60 seconds.",
    "controls.start": "Start session",
    cancel: "Cancel",
    "controls.title": "Reactor live controls",
    "controls.recordingNotice": "Starting uses Reactor credits. Recording stops at the chosen duration. Ending early discards the unfinished video. The preview has no sound.",
    "controls.dragInstructions": "Drag on the output to steer the subject. Release to stop. With the picture focused, arrow keys position the pointer, Space holds it, and Escape releases it.",
    "controls.emptyPrompt": "Enter a prompt before applying it.",
    "controls.pointerRateExceeded": "Pointer input arrived too quickly. The session is ending.",
    "controls.recording": "Recording. Live controls are ready.",
    "controls.connectionClosed": "Connection closed. Check Reactor session status before starting again.",
    "controls.recordingNotStarted": "Recording did not start. Close this panel to view the workflow result.",
    "controls.connecting": "Connecting to Reactor…",
    "controls.cameraRequired": "Enable a camera before starting.",
    "controls.promptSent": "Prompt sent. The model applies changes to later frames.",
    "controls.soundSent": "Sound prompt sent. The model applies changes to later audio.",
    "controls.connectionEnded": "The live connection ended.",
    "sound.applyPrompt": "Apply sound prompt",
    "sound.prompt": "Sound prompt ",
    "sound.title": "Sound",
    "sound.promptNotice": "Describe the sound briefly. Leave blank to use the picture alone.",
    "help.title": "Node help",
    "help.close": "Close node help",
    "help.guide": "Reactor node guide",
    "help.newTab": " (opens in a new tab)",
    "models.connectName": "Connect name: {name}",
    "pricing.rate": "{rate} credits per session second.",
    "pricing.calculation": "{seconds} session seconds × {rate} credits per second = {credits} credits.",
    "models.lastRefresh": "Public prices and guides checked {date}.",
    "pricing.requestedDuration": "This node requests {seconds} seconds of video. Setup, pauses, and recording can add paid time.",
    "pricing.timeRange": "Enter a session time from 0.1 to {maximum} seconds.",
    "models.checkSchedule": "Automatic check: {date}. Checks run every {hours} hours.",
    "models.count": "{visible} of {total} models",
    "pointer.position": " {x}% across, {y}% down.",
    "camera.number": "Camera {number}",
    "live.duration": "{model} · {seconds} seconds of video",
    "live.elapsed": "Time spent on setup and recording: {seconds} seconds.",
    "settings.limit.max_capture_seconds": "Maximum video duration (seconds)",
    "settings.limit.max_session_seconds": "Maximum session duration (seconds)",
    "settings.limit.connect_timeout_seconds": "Connection timeout (seconds)",
    "settings.limit.first_frame_timeout_seconds": "First-frame timeout (seconds)",
    "settings.limit.cleanup_timeout_seconds": "Disconnect timeout (seconds)",
    "settings.limit.queue_timeout_seconds": "Queue wait timeout (seconds)",
    "settings.limit.max_upload_megabytes": "Maximum upload size (MiB)",
    "settings.limit.max_capture_megabytes": "Maximum video file size (MiB)",
    "settings.limit.max_queue_megabytes": "Maximum queued frame data (MiB)",
    "settings.limit.catalog_interval_hours": "Check interval (hours)",
    "help.navigation": "Reactor guides",
    "help.project": "ComfyUI Reactor Connector",
    "help.workflows": "Workflows",
    "help.liveControls": "Live controls",
    "errors.keyRequired": "Set your Reactor API key in Reactor settings or the server environment before running.",
    "errors.keyEmpty": "Enter a nonempty API key without spaces.",
    "errors.keyWhitespace": "The API key cannot contain whitespace.",
    "errors.keyUnreadable": "Cannot read the saved Reactor key. Check its private file.",
    "errors.runtimeNotReady": "Reactor has not finished loading. Restart ComfyUI.",
    "errors.stateDirectoryLink": "The state directory cannot be a symbolic link.",
    "errors.stateDirectoryPermissions": "Restrict the state directory to its owner.",
    "errors.stateFileLink": "A state file cannot be a symbolic link.",
    "errors.stateFileType": "The requested state file is not a regular file.",
    "errors.stateFilePermissions": "Restrict the state file to its owner.",
    "errors.stateFileSize": "The state file exceeds its size limit.",
    "errors.stateDirectoryAbsolute": "Use an absolute state directory path.",
    "errors.stateFileChanged": "The private state file changed while opening.",
    "errors.jsonValues": "Use finite numbers and ordinary JSON values.",
    "errors.jsonSize": "The JSON input exceeds its size limit.",
    "errors.jsonDuplicateKey": "Duplicate JSON key.",
    "errors.jsonDepth": "The JSON input is nested too deeply.",
    "errors.jsonObject": "Expected a JSON object.",
    "errors.jsonSyntax": "Enter valid JSON with unique keys.",
    "errors.settingReadOnly": "This setting cannot be changed here.",
    "errors.savedKeyLink": "A saved key cannot be a symbolic link.",
    "errors.settingsUnreadable": "Cannot load Reactor execution settings. Check the limits and private key.",
    "errors.settingsChanged": "Settings changed. Reload them before saving.",
    "errors.settingUnknown": "The settings contain an unknown option.",
    "errors.automaticChecksType": "Use true or false for automatic model checks.",
    "errors.sessionLimitTooShort": "The session limit must exceed the capture limit to allow setup and cleanup.",
    "errors.settingsWholeNumbers": "Use whole numbers for Reactor limits and check intervals.",
    "errors.settingsRange": "Choose a setting within the range shown in Reactor settings.",
    "errors.settingsRevisionRequired": "Send settings and their current revision.",
    "errors.singleKeyRequired": "Send one API key.",
    "errors.clearKeyBody": "Do not include a body when clearing a saved key.",
    "errors.liveControlType": "Choose whether live controls are enabled.",
    "errors.runTimeout": "Reactor did not finish within the configured time limit.",
    "errors.browserOwnerMissing": "The executing prompt has no browser owner.",
    "errors.liveHostRequirements": "Live controls need a local, single-user ComfyUI browser.",
    "errors.liveCameraUnsupported": "This model has no live camera adapter.",
    "errors.livePanelClosed": "The live panel was closed.",
    "errors.liveCancelled": "The live run was cancelled.",
    "errors.privateStateLocation": "Keep Reactor's private state outside ComfyUI, its package, and its media folders.",
    "errors.modelListGrowth": "The model list grew unexpectedly. Review the source before updating.",
    "errors.priceListIncomplete": "The pricing list may be incomplete. The previous list is unchanged.",
    "errors.guideListIncomplete": "The guide list may be incomplete. The previous list is unchanged.",
    "errors.modelListChanged": "The model list changed. Reload the list and retry.",
    "errors.modelRefreshRunning": "A model list refresh is already running.",
    "errors.modelRefreshWait": "Wait for the model list refresh to finish.",
    "errors.modelListHistoryEmpty": "There is no earlier model list to restore.",
    "errors.modelsUnreadable": "Cannot read Reactor's public model list. The previous list is unchanged.",
    "errors.modelListFormat": "The model model list has an invalid or unsupported format.",
    "errors.automaticCheckFailed": "Automatic model check failed. Use Refresh models to retry.",
    "errors.refreshBody": "Do not send a body when refreshing public models.",
    "errors.modelRevisionRequired": "Send the model list revision shown in this tab.",
    "errors.localConnectionRequired": "Reactor configuration requires a local, same-origin ComfyUI connection.",
    "errors.requestJsonRequired": "Send a JSON request.",
    "errors.requestTimeout": "The configuration request took too long.",
    "errors.requestEncoding": "Send valid UTF-8 JSON.",
    "errors.stateUnreadable": "Cannot read connector state. Check its location and permissions.",
    "errors.sessionDisconnected": "The Reactor session is not connected.",
    "errors.sessionAlreadyConnected": "This Reactor session cannot be connected again.",
    "errors.recordingDisconnected": "The recording session is not connected.",
    "errors.recordingTiming": "The recording returned invalid timing markers.",
    "errors.recordingReadiness": "The recording returned invalid readiness timing.",
    "errors.commandRejected": "Reactor rejected a model command. Check this node's inputs and model guide.",
    "errors.captureDisconnected": "The Reactor connection ended before capture finished.",
    "errors.cleanupUnconfirmed": "Session cleanup failed; termination is unconfirmed. The server lifetime cap applies.",
    "errors.localCleanupFailed": "The remote session ended, but local cleanup failed.",
    "errors.terminationUnconfirmed": "Session termination is unconfirmed. Wait for its server limit before retrying.",
    "errors.cleanupRestartRequired": "The remote session ended, but local cleanup failed. Restart ComfyUI.",
    "errors.accessRefused": "Reactor refused access. Check your key and model access.",
    "errors.providerRateLimit": "Reactor is limiting requests. Wait before starting another run.",
    "errors.providerRequestTimeout": "Reactor did not reply within its request limit.",
    "errors.modelUnavailable": "The requested Reactor model or protocol is unavailable. Check for updates.",
    "errors.runFailed": "Reactor could not complete this run. Check your connection and account status.",
    "errors.authenticationFailed": "Reactor could not authenticate. Check your saved key and network connection.",
    "errors.sessionTimeout": "Reactor exceeded the configured time limit.",
    "errors.captureLimit": "Choose a capture within the host limit.",
    "errors.seedRange": "Choose a seed from 0 to 4,294,967,295.",
    "errors.promptLength": "Enter a prompt of 1 to 20,000 characters.",
    "errors.imageUploadLimit": "Provide image bytes within the upload limit.",
    "errors.modelAuthorization": "Reactor could not authorize this model. Check your key and model access before retrying.",
    "errors.sessionCapacity": "Choose a session capacity from 1 to 4.",
    "errors.queueTimeout": "Timed out waiting for another Reactor run to finish. This waiting run did not open a session.",
    "errors.packageVersionMissing": "The connector's version is missing. Reinstall the package.",
    "errors.packageIdentityInvalid": "The package identity is invalid. Reinstall the package.",
    "errors.nodeUnregistered": "The Reactor node is not registered.",
    "errors.packageIdentityUnreadable": "The package identity could not be read. Reinstall it.",
    "errors.livePanelEnded": "The live panel ended or disconnected. The capture has been stopped.",
    "errors.livePreviewEncoding": "The live preview could not be encoded. The session is ending.",
    "errors.liveCaptureCancelled": "The live capture was cancelled.",
    "errors.livePanelLimit": "Too many live panels are still open.",
    "errors.liveSessionUnavailable": "This live session is no longer available.",
    "errors.cameraStateRequired": "Send a complete listed camera state.",
    "errors.liveInputOrder": "The live input is out of order.",
    "errors.cameraInputStale": "Camera input became stale before it could be sent.",
    "errors.cameraCommandTimeout": "A live camera command was not acknowledged in time. The session is ending.",
    "errors.cameraCommandLimit": "Camera input exceeded its pending command limit.",
    "errors.cameraJpegRequired": "Send a camera JPEG.",
    "errors.cameraFrameWait": "Wait for the previous camera frame.",
    "errors.workerArguments": "Invalid worker arguments.",
    "errors.workerLimits": "Worker limits must be positive.",
    "errors.videoFrameType": "The video track returned an unsupported frame.",
    "errors.videoFrameColor": "The video track must provide RGB frames.",
    "errors.videoTimestamp": "The video track returned an invalid timestamp.",
    "errors.encoderMetadata": "The video encoder returned invalid metadata.",
    "errors.videoArrivalRate": "Video arrived faster than it could be saved. Shorten the capture.",
    "errors.videoEncodingFailed": "Video encoding failed. Check disk space and media support.",
    "errors.captureQueueFull": "The video capture queue is full. Shorten the capture.",
    "errors.cameraDimensions": "Send a JPEG no larger than 640 by 480 pixels.",
    "errors.cameraFrameSize": "Send a camera JPEG smaller than 300 KB.",
    "errors.cameraInputStopped": "Camera input stopped. The session is ending.",
    "errors.cameraFrameOrder": "The camera frame is out of order or the session ended.",
    "errors.singleImageRequired": "Connect exactly one RGB image, not a batch.",
    "errors.imageDimensions": "Use an image no larger than 8192 pixels per side.",
    "errors.imagePixels": "The image contains non-finite pixel values.",
    "errors.encoderResult": "The video encoder returned no valid result.",
    "errors.encoderNotReady": "The video encoder did not become ready.",
    "errors.encoderPipes": "The video encoder pipes are unavailable.",
    "errors.captureStopped": "Video capture was stopped.",
    "errors.encoderStopFailed": "The encoder process did not stop. Restart ComfyUI before another run.",
    "errors.audioLimit": "The recording audio exceeds its native limits.",
    "errors.audioIncomplete": "The recording audio is incomplete.",
    "errors.outputClosed": "The recording output is closed.",
    "errors.outputSize": "The recording exceeds the output size limit.",
    "errors.longliveImagesUnsupported": "LongLive accepts shot prompts, not images.",
    "errors.storyboardOrder": "Use a storyboard of at most 32 shots with distinct, increasing chunk numbers.",
    "errors.storyboardSize": "Keep the storyboard within 128 KB.",
    "errors.shotChunk": "Place a later shot at chunk 1 or above.",
    "errors.shotTransition": "Choose a soft transition or a cut.",
    "errors.shotPrompt": "Enter a shot prompt of 1 to 20,000 characters.",
    "errors.promptSequenceOrder": "Use at most 32 later prompts with distinct, increasing chunk numbers.",
    "errors.promptSequenceSize": "Keep the prompt sequence within 128 KB.",
    "errors.promptChunk": "Choose a later prompt's chunk from 1 to 100,000.",
    "errors.laterPromptLength": "Enter a later prompt of 1 to 20,000 characters.",
    "errors.ltxDuration": "Use at least four seconds for LTX.",
    "errors.ltxSceneLength": "Use at most 800 scene characters.",
    "errors.speechLength": "Enter a script of 1 to 10,000 characters.",
    "errors.speechPace": "Use a positive whole-number speech pace.",
    "errors.portraitUploadLimit": "Provide one portrait within the upload limit.",
    "errors.ltxAudioMissing": "This LTX deployment has no audio track.",
    "errors.portraitRequired": "Provide one portrait.",
    "errors.speechPaceMissing": "LTX did not report its accepted speech pace.",
    "errors.startingImageRequired": "Connect one starting image.",
    "errors.worldPromptLength": "Use a prompt of at most 1,000 characters.",
    "errors.cameraDirection": "Choose a listed camera direction.",
    "errors.rotationSpeed": "Choose a rotation speed from 0 to 30.",
    "errors.lateralDirection": "Choose a listed lateral direction.",
    "errors.sanaPromptLength": "Use at most 20,000 prompt characters.",
    "errors.sourceVideoRequired": "Connect a prepared source video.",
    "errors.anchorInterval": "Choose an anchor interval from 0 to 1,000.",
    "errors.sanaWebcamUnsupported": "This SANA deployment does not accept webcam input.",
    "errors.sanaUnsupported": "This SANA input contract is unsupported. Check for a connector update.",
    "errors.fastPromptLength": "Use at most 800 prompt characters.",
    "errors.fastDuration": "Choose 5.167 to 14.375 seconds for Fast H3.",
    "errors.fastAspectRatio": "Choose an offered Fast H3 aspect ratio.",
    "errors.endingImageUploadLimit": "Provide an ending image within the upload limit.",
    "errors.fastAudioMissing": "This Fast H3 deployment has no audio track.",
    "errors.clipDurationRange": "The requested length is outside this deployment's clip limits.",
    "errors.continuationLength": "Fast H3 returned an invalid continuation length.",
    "errors.clipCaptureLimit": "The accepted clip length exceeds the host capture limit. Choose a shorter clip.",
    "errors.clipPlaybackOrder": "Fast H3 started playback before the clip was selected.",
    "errors.clipWindowMissing": "Fast H3 did not report a precise clip window. No partial clip will be saved.",
    "errors.clipCount": "Choose 2 to 8 clips.",
    "errors.continuedClipDuration": "Choose 5.167 to 14.375 seconds per clip.",
    "errors.aspectRatio": "Choose an offered aspect ratio.",
    "errors.continuationPrompts": "Use at most 800 characters per prompt and one later prompt per remaining clip.",
    "errors.clipDurationUnsupported": "This deployment does not support the requested clip length.",
    "errors.sequencePlaybackOrder": "Fast H3 started playback before the sequence was ready.",
    "errors.sequenceCaptureLimit": "The sequence exceeded the video duration limit. Choose fewer clips or a longer limit.",
    "errors.acceptedSequenceLimit": "The accepted clip lengths exceed the video duration limit. Choose fewer clips.",
    "errors.clipReply": "Fast H3 returned an unexpected reply.",
    "errors.clipMediaTime": "Fast H3 returned an invalid media time.",
    "errors.clipMissing": "Fast H3 did not return a clip.",
    "errors.clipIdentifier": "Fast H3 returned an invalid clip ID.",
    "errors.clipLength": "Fast H3 returned an invalid clip length.",
    "errors.clipUnfinished": "Fast H3 did not finish the queued clip.",
    "errors.clipsUnexpected": "Fast H3 returned unexpected clips.",
    "errors.acceptedClipChanged": "Fast H3 changed a clip's accepted length.",
    "errors.clipLengthChanged": "Fast H3 changed the accepted clip length before playback.",
    "errors.viskoImageChanged": "Visko started with different image settings. The run was stopped.",
    "errors.viskoSoundChanged": "Visko started with different sound settings. The run was stopped.",
    "errors.viskoResolutionChanged": "Visko started at a different resolution. The run was stopped.",
    "errors.soundPromptLength": "Use at most 1,000 audio prompt characters.",
    "errors.resolutionName": "Use a short model resolution name.",
    "errors.soundOptionType": "Use boolean sound and prompt options.",
    "errors.viskoAudioMissing": "This Visko deployment has no audio track.",
    "errors.resolutionUnavailable": "This model does not offer that resolution. Leave it blank for the default.",
    "errors.x2Unsupported": "This X2 input contract is unsupported. Check for an update.",
    "errors.x2PromptLength": "Use at most 1,000 prompt characters.",
    "errors.pointerOptionType": "Use boolean backlog and pointer values.",
    "errors.pointerCoordinates": "Choose pointer coordinates from 0 to 1.",
    "errors.sessionRecordDamaged": "The saved Reactor session record is damaged. Check Reactor Usage before repairing the session record in the connector's private settings folder.",
    "errors.sessionWaitTime": "Use a positive session wait time.",
    "errors.reservationReused": "Create a new reservation for each session.",
    "errors.sessionLockLink": "The session lock cannot be a link.",
    "errors.sessionLockPermissions": "Restrict the session lock file to its owner.",
    "errors.sessionInOtherProcess": "Another ComfyUI process is using Reactor. Let its run finish before trying again.",
    "errors.sessionRecordUnreadable": "The Reactor session record could not be read or saved. No session was started. Check access to the connector's private settings folder.",
    "errors.sessionRecordUpdateFailed": "The Reactor session record could not be updated. The saved wait still applies.",
    "errors.sessionRecordPermissions": "The Reactor session record could not be updated. The saved wait still applies. Check access to the connector's private settings folder.",
    "errors.videoTrackMissing": "The model did not declare its expected video track.",
    "errors.sessionDeadline": "The session deadline expired during this operation.",
    "errors.liveCommandUnfinished": "A live command did not finish. The session is ending.",
    "errors.liveActionValues": "Choose a supported live action and valid values.",
    "errors.liveActionWait": "Wait for the previous live action.",
    "errors.sourceFrameRate": "The prepared video has no valid frame rate.",
    "errors.sourceFramesMissing": "The prepared input has no frames.",
    "errors.sourceReaderClosed": "The prepared video reader is closed.",
    "errors.sourceTimestampMissing": "The prepared video has no frame timestamp.",
    "errors.localSourceRequired": "Connect one local SDR clip from Load Video or Create Video within the input limits.",
    "errors.sourcePixels": "Source pixels must be finite numbers.",
    "errors.sourceVideoFormat": "Use an SDR RGB video at 1 to 120 frames per second.",
    "errors.sourceDimensions": "Use even video dimensions within the input limit.",
    "errors.sourceFrameCount": "Use a source video with at least 33 frames.",
    "errors.sourceFramesLost": "The prepared source lost frames during encoding.",
    "errors.recordingUnsupported": "Reactor returned an unsupported recording. No partial video was saved.",
    "errors.recordingNotReady": "The recording was not ready within the capture time limit.",
    "errors.recordingMetadata": "The recording returned invalid media metadata.",
    "errors.savedVideoDetails": "The saved video returned invalid details.",
    "errors.savedVideoTimeout": "Reading the saved video's details took too long.",
    "errors.modelsHttp": "Reactor's model list returned HTTP {status}. Try again later.",
    "errors.phase": "{message} Stage: {phase}. Code: {code}.",
    "errors.terminationWait": "An earlier Reactor session has unconfirmed termination. Wait {seconds} seconds before starting another run.",
    "errors.speechPaceRange": "Use a speech pace from {minimum} to {maximum}.",
    "errors.sessionWait": "An earlier Reactor session may still be running. Wait {seconds} seconds before another run. Restarting ComfyUI does not clear this wait."
  }
};

// web/language.ts
var messages = {};
function readLanguage(document2) {
  if (typeof document2 !== "object" || document2 === null) return {};
  const source = document2.reactorInc;
  if (typeof source !== "object" || source === null) return {};
  const translated = {};
  for (const [key, value] of Object.entries(source)) {
    if (typeof value === "string") translated[key] = value;
  }
  return translated;
}
async function loadLanguage() {
  try {
    const languages = await api.getCustomNodesI18n();
    const available = {};
    for (const [language, document2] of Object.entries(languages)) {
      available[language] = readLanguage(document2);
    }
    messages = available;
  } catch {
    messages = {};
  }
}
function translate(key, values = {}, fallback) {
  const selected = app.extensionManager.setting.get("Comfy.Locale");
  const language = typeof selected === "string" ? selected : "en";
  const defaults = main_default.reactorInc;
  const message = messages[language]?.[key] ?? defaults[key] ?? fallback ?? key;
  return message.replaceAll(
    /\{(\w+)\}/g,
    (placeholder, name) => Object.hasOwn(values, name) ? String(values[name]) : placeholder
  );
}

// web/dom.ts
function element(tag, text) {
  const node = document.createElement(tag);
  if (text !== void 0) node.textContent = text;
  return node;
}
function button(text, type = "button") {
  const node = element("button", text);
  node.type = type;
  return node;
}

// config/browser.ts
var browserLimits = {
  requestTimeoutMilliseconds: 1e4,
  pollIntervalMilliseconds: 100,
  actionTimeoutMilliseconds: 2e3,
  maxPendingInputs: 8,
  maxPreviewCharacters: 35e4,
  maxCalculatorSeconds: 3600
};
var browserPatterns = {
  lease: /^[a-f0-9]{32}$/,
  revision: /^[a-f0-9]{64}$/,
  preview: /^[A-Za-z0-9+/]*={0,2}$/,
  capability: /^[A-Za-z0-9_-]{43}$/
};

// web/live/commands.ts
function controls(value) {
  if (typeof value !== "object" || value === null) return;
  const v = value;
  if (typeof v.lease !== "string" || !browserPatterns.lease.test(v.lease) || typeof v.capability !== "string" || !browserPatterns.capability.test(v.capability) || typeof v.model !== "string" || typeof v.model_title !== "string" || v.model_title.length < 1 || v.model_title.length > 200 || typeof v.prompt !== "string" || typeof v.prompt_limit !== "number" || v.prompt_limit < 1 || !Number.isSafeInteger(v.prompt_limit) || v.prompt.length > v.prompt_limit || typeof v.webcam !== "boolean" || typeof v.pointer !== "boolean" || typeof v.sound !== "boolean" || typeof v.audio_prompt !== "string" || typeof v.audio_prompt_limit !== "number" || !Number.isSafeInteger(v.audio_prompt_limit) || v.audio_prompt_limit < 1 || v.audio_prompt.length > v.audio_prompt_limit || typeof v.duration_seconds !== "number" || !Number.isFinite(v.duration_seconds) || v.duration_seconds <= 0)
    return;
  return {
    lease: v.lease,
    capability: v.capability,
    model: v.model,
    modelTitle: v.model_title,
    duration_seconds: v.duration_seconds,
    axes: {},
    prompt: v.prompt,
    prompt_limit: v.prompt_limit,
    webcam: v.webcam,
    pointer: v.pointer,
    sound: v.sound,
    audio_prompt: v.audio_prompt,
    audioPromptLimit: v.audio_prompt_limit
  };
}
async function action(fetcher, owner, sequence, name, data) {
  const response = await fetcher("/reactor-inc/v1/live/action", {
    method: "POST",
    cache: "no-store",
    signal: AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds),
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" },
    body: JSON.stringify({
      lease: owner.lease,
      capability: owner.capability,
      sequence,
      action: name,
      data
    })
  });
  if (!response.ok) throw new Error(translate("live.actionRejected"));
}

// web/live/input.ts
function cameraAxes(keys, hasIndependentAxes) {
  function direction(negative, positive, first, second) {
    if (keys.has(negative) === keys.has(positive)) return "idle";
    return keys.has(negative) ? first : second;
  }
  const forward = direction("w", "s", "forward", "back");
  const lateral = direction("a", "d", "strafe_left", "strafe_right");
  return {
    ...hasIndependentAxes ? { move_longitudinal: forward, move_lateral: lateral } : { movement: forward !== "idle" ? forward : lateral },
    look_horizontal: direction("ArrowLeft", "ArrowRight", "left", "right"),
    look_vertical: direction("ArrowUp", "ArrowDown", "up", "down")
  };
}
var cameraKeys = ["w", "s", "a", "d", "ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];
var CameraInput = class {
  /**
   * Bind camera input for the lifetime of the panel.
   * @param surface - The keyboard camera surface.
   * @param controls - The camera direction buttons.
   * @param signal - The panel's listener lifetime.
   * @param update - Receive the combined keys and explicit release requests.
   */
  constructor(surface, controls2, signal, update) {
    this.update = update;
    surface.addEventListener(
      "keydown",
      (event) => {
        const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
        if (cameraKeys.includes(key)) {
          event.preventDefault();
          event.stopPropagation();
          this.keyboard.add(key);
          this.publish();
        } else if (key === "Escape") {
          event.preventDefault();
          event.stopPropagation();
          this.release();
          surface.blur();
        }
      },
      { signal }
    );
    surface.addEventListener(
      "keyup",
      (event) => {
        const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
        if (cameraKeys.includes(key)) {
          event.preventDefault();
          event.stopPropagation();
          this.keyboard.delete(key);
          this.publish();
        }
      },
      { signal }
    );
    surface.addEventListener("blur", () => this.release(), { signal });
    this.bindButtons(controls2, signal);
    window.addEventListener("blur", () => this.release(), { signal });
    document.addEventListener(
      "visibilitychange",
      () => {
        if (document.hidden) this.release();
      },
      { signal }
    );
    signal.addEventListener("abort", () => this.release(), { once: true });
  }
  update;
  keyboard = /* @__PURE__ */ new Set();
  pointers = /* @__PURE__ */ new Map();
  pointerStarted = /* @__PURE__ */ new Map();
  nudges = /* @__PURE__ */ new Map();
  lastHold;
  /**
   * Send combined input after a key, pointer, or timer changes.
   * @param release - Whether the user explicitly released all input.
   */
  // eslint-disable-next-line local/no-trivial-functions -- Each event must publish the same combined keyboard, pointer, and timer state.
  publish(release = false) {
    const keys = /* @__PURE__ */ new Set([...this.keyboard, ...this.pointers.values(), ...this.nudges.keys()]);
    this.update(keys, release);
  }
  /**
   * Keep a short press visible for the next server update.
   * @param key - The direction key to hold briefly.
   * @param milliseconds - Remaining duration of the short press.
   */
  nudge(key, milliseconds) {
    const previous = this.nudges.get(key);
    if (previous !== void 0) clearTimeout(previous);
    this.nudges.set(
      key,
      // eslint-disable-next-line local/no-trivial-functions -- The timer removes its key before publishing the remaining held inputs.
      setTimeout(() => {
        this.nudges.delete(key);
        this.publish();
      }, milliseconds)
    );
  }
  /** Clear every held input and timer, then send an explicit release. */
  release() {
    this.keyboard.clear();
    this.pointers.clear();
    this.pointerStarted.clear();
    this.lastHold = void 0;
    for (const timer of this.nudges.values()) clearTimeout(timer);
    this.nudges.clear();
    this.publish(true);
  }
  /**
   * Bind mouse, touch, keyboard, and assistive button activation.
   * @param controls - The container for direction buttons.
   * @param signal - The panel's listener lifetime.
   */
  bindButtons(controls2, signal) {
    controls2.addEventListener(
      "pointerdown",
      (event) => {
        const target = event.target;
        if (!(target instanceof HTMLButtonElement) || !target.dataset.key || event.button !== 0)
          return;
        event.preventDefault();
        target.setPointerCapture(event.pointerId);
        this.lastHold = void 0;
        this.pointers.set(event.pointerId, target.dataset.key);
        this.pointerStarted.set(event.pointerId, performance.now());
        this.publish();
      },
      { signal }
    );
    for (const kind of ["pointerup", "pointercancel", "lostpointercapture"])
      controls2.addEventListener(kind, (event) => this.releasePointer(event), { signal });
    for (const kind of ["keydown", "keyup"])
      controls2.addEventListener(kind, (event) => this.buttonKey(event), { signal });
    controls2.addEventListener("focusout", () => this.release(), { signal });
    controls2.addEventListener(
      "click",
      (event) => {
        const target = event.target;
        if (!(target instanceof HTMLButtonElement) || !target.dataset.key) return;
        if (event.detail !== 0 && this.lastHold?.key === target.dataset.key) return;
        this.nudge(target.dataset.key, 250);
        this.publish();
      },
      { signal }
    );
  }
  /**
   * Finish a held button and preserve very short presses.
   * @param event - The pointer release or cancellation.
   */
  releasePointer(event) {
    const key = this.pointers.get(event.pointerId);
    const started = this.pointerStarted.get(event.pointerId);
    if (event.type === "pointerup" && key && started !== void 0) {
      this.lastHold = { key, milliseconds: performance.now() - started };
      if (this.lastHold.milliseconds < 250) this.nudge(key, 250 - this.lastHold.milliseconds);
    }
    this.pointers.delete(event.pointerId);
    this.pointerStarted.delete(event.pointerId);
    this.publish();
  }
  /**
   * Treat Space and Enter as a held direction on a focused button.
   * @param event - A key press or release on the button container.
   */
  buttonKey(event) {
    const target = event.target;
    if (!(target instanceof HTMLButtonElement) || !target.dataset.key || ![" ", "Enter"].includes(event.key))
      return;
    event.preventDefault();
    event.stopPropagation();
    if (event.type === "keydown") this.keyboard.add(target.dataset.key);
    else this.keyboard.delete(target.dataset.key);
    this.publish();
  }
};

// web/live/state.ts
var CameraStates = class {
  current;
  pending = [];
  hasIndependentAxes;
  /**
   * Initialize idle camera movement for the selected model.
   * @param hasIndependentAxes - Whether independent movement axes are supported.
   */
  // eslint-disable-next-line local/no-trivial-functions -- Construction records the model and initializes its supported idle axes.
  constructor(hasIndependentAxes) {
    this.hasIndependentAxes = hasIndependentAxes;
    this.current = cameraAxes(/* @__PURE__ */ new Set(), hasIndependentAxes);
  }
  /**
   * Queue changed camera input while preserving explicit releases.
   * @param keys - The keys currently held or briefly pressed.
   * @param release - Whether to clear queued movement before this update.
   */
  update(keys, release = false) {
    const axes = cameraAxes(keys, this.hasIndependentAxes);
    if (release) this.pending = [];
    if (release || JSON.stringify(axes) !== JSON.stringify(this.current)) {
      if (this.pending.length >= browserLimits.maxPendingInputs) {
        this.pending = [{ axes: cameraAxes(/* @__PURE__ */ new Set(), this.hasIndependentAxes), release: true }];
        if (Object.values(axes).some((value) => value !== "idle"))
          this.pending.push({ axes, release: false });
      } else this.pending.push({ axes, release });
    }
    this.current = axes;
  }
  /**
   * Consume a queued camera update or keep the current held movement.
   * @returns The axes and release flag for the next exchange.
   */
  // eslint-disable-next-line local/no-trivial-functions -- Reading the next state consumes a queued update, so callers must use this owner.
  take() {
    return this.pending.shift() ?? { axes: this.current, release: false };
  }
};

// web/live/api.ts
function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function parseInvitation(value) {
  if (!isRecord(value) || !isRecord(value.axes)) return;
  if (typeof value.lease !== "string" || !browserPatterns.lease.test(value.lease) || typeof value.capability !== "string" || !browserPatterns.capability.test(value.capability) || typeof value.model !== "string" || typeof value.model_title !== "string" || value.model_title.length < 1 || value.model_title.length > 200 || typeof value.prompt !== "string" || typeof value.prompt_limit !== "number" || !Number.isSafeInteger(value.prompt_limit) || value.prompt_limit < 1 || value.prompt.length > value.prompt_limit || typeof value.duration_seconds !== "number" || !Number.isFinite(value.duration_seconds) || value.duration_seconds <= 0)
    return;
  const axes = {};
  const expected = Object.keys(
    cameraAxes(/* @__PURE__ */ new Set(), Object.hasOwn(value.axes, "move_longitudinal"))
  );
  if (Object.keys(value.axes).length !== expected.length) return;
  for (const key of expected) {
    const choices = value.axes[key];
    if (!Array.isArray(choices) || !choices.includes("idle") || !choices.every((choice) => typeof choice === "string"))
      return;
    axes[key] = choices;
  }
  return {
    lease: value.lease,
    capability: value.capability,
    model: value.model,
    modelTitle: value.model_title,
    duration_seconds: value.duration_seconds,
    axes,
    prompt: value.prompt,
    prompt_limit: value.prompt_limit
  };
}
async function exchange(fetcher, owner, sequence, axes, end, previewSequence, signal, release = false) {
  const response = await fetcher("/reactor-inc/v1/live/exchange", {
    method: "POST",
    cache: "no-store",
    signal,
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" },
    body: JSON.stringify({
      lease: owner.lease,
      capability: owner.capability,
      sequence,
      axes,
      end,
      release,
      preview_sequence: previewSequence
    })
  });
  if (!response.ok) throw new Error(translate("live.unreachable"));
  const value = await response.json();
  if (!isRecord(value) || typeof value.closed !== "boolean" || typeof value.termination_confirmed !== "boolean" || typeof value.failed !== "boolean" || typeof value.controls_ready !== "boolean" || typeof value.finishing !== "boolean" || typeof value.elapsed_seconds !== "number" || !Number.isFinite(value.elapsed_seconds) || typeof value.preview_sequence !== "number" || !Number.isSafeInteger(value.preview_sequence) || typeof value.preview !== "string" || value.preview.length > browserLimits.maxPreviewCharacters || !browserPatterns.preview.test(value.preview)) {
    throw new Error(translate("live.invalidStatus"));
  }
  return {
    closed: value.closed,
    termination_confirmed: value.termination_confirmed,
    failed: value.failed,
    controls_ready: value.controls_ready,
    finishing: value.finishing,
    elapsed_seconds: value.elapsed_seconds,
    preview_sequence: value.preview_sequence,
    preview: value.preview
  };
}

// web/live/dialog.ts
var panels = /* @__PURE__ */ new Set();
var CameraPanel = class {
  /**
   * Build camera controls for the invited model.
   * @param owner - The validated camera session invitation.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(owner, fetcher) {
    this.owner = owner;
    this.fetcher = fetcher;
    this.dialog.className = "reactor-settings reactor-live";
    this.dialog.setAttribute("aria-label", translate("live.cameraTitle"));
    this.status.setAttribute("role", "status");
    this.promptStatus.setAttribute("role", "status");
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.prompt_limit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.apply.disabled = true;
    this.surface.className = "reactor-preview";
    this.surface.tabIndex = 0;
    this.surface.setAttribute("aria-label", translate("live.movementLabel"));
    this.image.alt = translate("live.output");
    this.image.hidden = true;
    this.surface.append(this.image);
    this.controls.className = "reactor-actions";
    const labels = [
      translate("live.forward"),
      translate("live.back"),
      translate("live.moveLeft"),
      translate("live.moveRight"),
      translate("live.lookLeft"),
      translate("live.lookRight"),
      translate("live.lookUp"),
      translate("live.lookDown")
    ];
    for (const [index, key] of cameraKeys.entries()) {
      const control = button(labels[index] ?? key);
      control.dataset.key = key;
      control.disabled = true;
      this.controls.append(control);
    }
    this.states = new CameraStates(owner.model.endsWith("world-2"));
    const input = new CameraInput(
      this.surface,
      this.controls,
      this.controller.signal,
      (keys, urgent) => this.states.update(keys, urgent)
    );
    this.release = input.release.bind(input);
    this.bindActions();
    this.appendContent();
  }
  owner;
  fetcher;
  previousFocus = document.activeElement;
  controller = new AbortController();
  dialog = element("dialog");
  status = element("p", translate("live.connectingPanel"));
  elapsed = element("p");
  prompt = element("textarea");
  apply = button(translate("live.applyPrompt"));
  promptStatus = element("p", translate("live.promptNotice"));
  surface = element("div");
  image = element("img");
  controls = element("div");
  end = button(translate("live.endSession"));
  states;
  release;
  pendingPrompt;
  actionSequence = 0;
  ending = false;
  finished = false;
  disposed = false;
  sequence = 0;
  previewSequence = 0;
  /** Build the session header, movement controls, and prompt input. */
  appendContent() {
    const header = element("header");
    header.append(element("h2", translate("live.cameraTitle")), this.end);
    const promptLabel = element("label", translate("live.scenePrompt"));
    promptLabel.append(this.prompt);
    this.dialog.append(
      header,
      element(
        "p",
        translate("live.duration", {
          model: this.owner.modelTitle,
          seconds: this.owner.duration_seconds
        })
      ),
      element("p", translate("live.movementInstructions")),
      this.surface,
      this.controls,
      promptLabel,
      this.apply,
      this.promptStatus,
      this.status,
      this.elapsed,
      element("p", translate("live.recordingNotice"))
    );
  }
  /** Bind prompt updates, explicit ending, and focus cleanup. */
  bindActions() {
    this.apply.addEventListener("click", () => {
      if (!this.prompt.value.trim()) {
        this.promptStatus.textContent = translate("live.emptyScenePrompt");
        return;
      }
      this.pendingPrompt = this.prompt.value;
      this.apply.disabled = true;
    });
    this.end.addEventListener("click", () => {
      if (this.finished) this.dialog.close();
      else this.stop();
    });
    this.dialog.addEventListener("cancel", (event) => {
      event.preventDefault();
      this.release();
      this.surface.blur();
    });
    this.dialog.addEventListener(
      "close",
      () => {
        this.stop();
        this.disposed = true;
        this.controller.abort();
        this.image.removeAttribute("src");
        panels.delete(this.owner.lease);
        this.dialog.remove();
        if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
          this.previousFocus.focus();
      },
      { once: true }
    );
  }
  /** Stop camera movement and request the end of the session. */
  stop() {
    this.ending = true;
    this.release();
    this.end.disabled = true;
    this.apply.disabled = this.prompt.disabled = true;
    this.status.textContent = translate("live.ending");
  }
  /**
   * Update camera controls and the preview while the panel is visible.
   * @param result - The validated session status.
   */
  display(result) {
    if (this.disposed) return;
    for (const control of this.controls.querySelectorAll("button"))
      control.disabled = !result.controls_ready || this.ending;
    this.prompt.disabled = !result.controls_ready || this.ending;
    this.apply.disabled = this.prompt.disabled || this.pendingPrompt !== void 0;
    this.elapsed.textContent = translate("live.elapsed", {
      seconds: result.elapsed_seconds.toFixed(1)
    });
    if (result.preview) {
      this.image.src = `data:image/jpeg;base64,${result.preview}`;
      this.image.hidden = false;
    }
    this.displayProgress(result);
  }
  /**
   * Describe whether the model is preparing, recording, or finishing.
   * @param result - The validated session status.
   */
  displayProgress(result) {
    if (result.finishing && !result.closed) {
      this.release();
      this.surface.blur();
      this.end.disabled = true;
      this.status.textContent = translate("live.ending");
    } else if (!this.ending) {
      this.status.textContent = result.controls_ready && result.preview_sequence > 0 ? translate("live.previewReady") : translate("live.waitingVideo");
    }
  }
  /**
   * Show the final session result without implying unconfirmed termination.
   * @param result - The terminal session status.
   */
  finish(result) {
    this.finished = true;
    if (!result.termination_confirmed) this.status.textContent = translate("live.unconfirmedEnd");
    else
      this.status.textContent = result.failed ? translate("live.discarded") : translate("live.ended");
  }
  /**
   * Send a queued prompt only while the session accepts controls.
   * @param result - The current session readiness.
   * @returns When the prompt request, if any, finishes.
   */
  async sendPrompt(result) {
    if (!result.controls_ready || result.finishing || this.ending || this.pendingPrompt === void 0)
      return;
    await action(this.fetcher, this.owner, this.actionSequence++, "prompt", {
      prompt: this.pendingPrompt
    });
    this.pendingPrompt = void 0;
    this.promptStatus.textContent = translate("live.promptSent");
  }
  /**
   * Exchange input and status until the server ends the session.
   * @returns When polling and listener cleanup finish.
   */
  async poll() {
    try {
      while (!this.finished) {
        const input = this.states.take();
        const result = await exchange(
          this.fetcher,
          this.owner,
          this.sequence++,
          input.axes,
          this.ending,
          this.previewSequence,
          AbortSignal.timeout(2e3),
          input.release
        );
        this.previewSequence = result.preview_sequence;
        this.display(result);
        if (result.closed) this.finish(result);
        else {
          await this.sendPrompt(result);
          await new Promise(
            (resolve) => setTimeout(resolve, browserLimits.pollIntervalMilliseconds)
          );
        }
      }
    } catch {
      this.finished = true;
      this.status.textContent = translate("live.connectionLost");
    } finally {
      this.release();
      this.controller.abort();
      this.end.disabled = false;
      this.end.textContent = translate("close");
      this.prompt.disabled = this.apply.disabled = true;
      for (const control of this.controls.querySelectorAll("button")) control.disabled = true;
      if (this.disposed) panels.delete(this.owner.lease);
    }
  }
  /** Show the panel, focus camera input, and begin exchanging session status. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.surface.focus();
    void this.poll();
  }
};
function openLive(value, fetcher) {
  const owner = parseInvitation(value);
  if (!owner || panels.has(owner.lease)) return;
  panels.add(owner.lease);
  const panel = new CameraPanel(owner, fetcher);
  panel.show();
}

// web/live/webcam.ts
var Webcam = class {
  /**
   * Build camera selection and a muted input preview.
   * @param owner - The validated session invitation.
   * @param fetcher - ComfyUI's local API client.
   * @param fail - Request session ending if the camera disconnects.
   */
  constructor(owner, fetcher, fail) {
    this.owner = owner;
    this.fetcher = fetcher;
    this.fail = fail;
    this.view.className = "reactor-webcam";
    const label = element("label", translate("camera.label"));
    label.append(this.select);
    this.select.append(new Option(translate("camera.default"), ""));
    this.video.muted = true;
    this.video.autoplay = true;
    this.video.playsInline = true;
    this.video.hidden = true;
    this.video.setAttribute("aria-label", translate("camera.preview"));
    const controls2 = element("div");
    controls2.append(label, this.enable);
    this.view.append(controls2, this.video, this.status);
    this.enable.addEventListener("click", () => void this.start());
  }
  owner;
  fetcher;
  fail;
  view = element("section");
  video = element("video");
  enable = button(translate("camera.enable"));
  select = element("select");
  status = element("p");
  stream;
  closed = false;
  sequence = 0;
  canvas = element("canvas");
  upload;
  controller = new AbortController();
  async start() {
    this.enable.disabled = true;
    try {
      if (!await this.openCamera()) return;
      await this.listCameras();
      if (this.closed) return;
      this.enable.textContent = translate("camera.select");
      this.status.textContent = translate("camera.enabled");
    } catch (error) {
      this.stopCamera();
      if (this.closed) return;
      this.status.textContent = error instanceof Error ? error.message : translate("camera.accessFailed");
    } finally {
      if (!this.closed) this.enable.disabled = false;
    }
  }
  /**
   * Open the selected camera and release any previous stream.
   * @returns Whether the camera is ready and the panel is still open.
   */
  async openCamera() {
    if (!navigator.mediaDevices?.getUserMedia)
      throw new Error(translate("camera.browserRequirements"));
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        frameRate: { ideal: 12, max: 24 },
        ...this.select.value ? { deviceId: { exact: this.select.value } } : {}
      }
    });
    if (this.closed) {
      for (const track of stream.getTracks()) track.stop();
      return false;
    }
    for (const track of this.stream?.getTracks() ?? []) {
      track.stop();
    }
    this.stream = stream;
    this.video.srcObject = stream;
    await this.video.play();
    if (this.closed) return false;
    this.video.hidden = false;
    return true;
  }
  /**
   * List cameras after permission reveals their names.
   * @returns When the available camera choices have been updated.
   */
  async listCameras() {
    const devices = await navigator.mediaDevices.enumerateDevices();
    if (this.closed) return;
    const selected = this.stream?.getVideoTracks()[0]?.getSettings().deviceId;
    this.select.replaceChildren(
      ...devices.filter((device) => device.kind === "videoinput").map(
        (device, index) => new Option(
          device.label || translate("camera.number", { number: index + 1 }),
          device.deviceId,
          false,
          device.deviceId === selected
        )
      )
    );
  }
  /**
   * Upload a camera frame without overlapping uploads.
   * @returns Whether a camera frame was available to send.
   */
  async frame() {
    if (this.closed || !this.stream || this.video.readyState < 2) return false;
    if (this.stream.getVideoTracks().some((track) => track.readyState !== "live")) {
      this.fail(translate("camera.disconnected"));
      return false;
    }
    if (this.upload) {
      await this.upload;
      return true;
    }
    const ratio = Math.min(640 / this.video.videoWidth, 480 / this.video.videoHeight, 1);
    this.canvas.width = Math.max(1, Math.round(this.video.videoWidth * ratio));
    this.canvas.height = Math.max(1, Math.round(this.video.videoHeight * ratio));
    const context = this.canvas.getContext("2d");
    if (!context) throw new Error(translate("camera.readFailed"));
    context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
    this.upload = this.send();
    try {
      await this.upload;
      return true;
    } finally {
      this.upload = void 0;
    }
  }
  async send() {
    const blob = await new Promise(
      (resolve) => this.canvas.toBlob(resolve, "image/jpeg", 0.8)
    );
    if (this.closed || !blob) return;
    const response = await this.fetcher("/reactor-inc/v1/live/camera", {
      method: "POST",
      cache: "no-store",
      body: blob,
      signal: AbortSignal.any([this.controller.signal, AbortSignal.timeout(2e3)]),
      headers: {
        "Content-Type": "image/jpeg",
        "X-Reactor-Comfy": "1",
        "X-Reactor-Lease": this.owner.lease,
        "X-Reactor-Capability": this.owner.capability,
        "X-Reactor-Sequence": String(this.sequence++)
      }
    });
    if (!response.ok) throw new Error(translate("camera.uploadFailed"));
  }
  /**
   * Stop the camera, cancel uploads, and clear the capture canvas.
   */
  close() {
    this.closed = true;
    this.controller.abort();
    this.stopCamera();
    this.select.disabled = this.enable.disabled = true;
    this.status.textContent = translate("camera.disabled");
    this.canvas.width = this.canvas.height = 0;
  }
  stopCamera() {
    this.video.hidden = true;
    for (const track of this.stream?.getTracks() ?? []) {
      track.stop();
    }
    this.stream = void 0;
    this.video.srcObject = null;
  }
};

// web/live/sound.ts
var SoundControls = class {
  view = element("fieldset");
  prompt = element("textarea");
  apply = button(translate("sound.applyPrompt"));
  pending;
  /**
   * Build the sound prompt controls in their disabled state.
   * @param initialPrompt - The workflow's starting sound prompt.
   * @param promptLimit - The model's maximum sound prompt length.
   */
  constructor(initialPrompt, promptLimit) {
    this.prompt.value = initialPrompt;
    this.prompt.maxLength = promptLimit;
    this.prompt.rows = 2;
    const label = element("label", translate("sound.prompt"));
    label.append(this.prompt);
    this.view.append(
      element("legend", translate("sound.title")),
      label,
      this.apply,
      element("p", translate("sound.promptNotice"))
    );
    this.apply.addEventListener("click", () => {
      this.pending = this.prompt.value;
      this.apply.disabled = true;
    });
    this.setReady(false);
  }
  /**
   * Enable sound input only when the session accepts changes.
   * @param ready - Whether the model accepts live controls.
   */
  // eslint-disable-next-line local/no-trivial-functions -- Both controls follow session readiness while a queued prompt keeps Apply disabled.
  setReady(ready) {
    this.prompt.disabled = !ready;
    this.apply.disabled = !ready || this.pending !== void 0;
  }
  /**
   * Consume the next sound prompt queued by the user.
   * @returns The queued prompt, or undefined when none is waiting.
   */
  takePrompt() {
    const value = this.pending;
    this.pending = void 0;
    return value;
  }
};

// web/live/pointer.ts
var PointerPreview = class {
  view = element("div");
  status = element("p");
  #marker = element("span");
  #state = element("span");
  #position = element("span");
  #image;
  #pointer;
  /**
   * Show pointer position alongside the output image.
   * @param image - The model output used for dragging.
   * @param signal - The panel's listener and observer lifetime.
   */
  constructor(image, signal) {
    this.#image = image;
    this.view.className = "reactor-pointer-preview";
    this.#marker.className = "reactor-pointer-marker";
    this.#marker.hidden = true;
    this.#marker.setAttribute("aria-hidden", "true");
    this.#state.setAttribute("role", "status");
    this.status.hidden = true;
    this.status.append(this.#state, this.#position);
    this.view.append(image, this.#marker);
    const resize = new ResizeObserver(() => this.#place());
    resize.observe(image);
    image.addEventListener("blur", () => this.#marker.hidden = true, { signal });
    image.addEventListener("focus", () => this.#place(), { signal });
    signal.addEventListener("abort", () => resize.disconnect(), { once: true });
  }
  /**
   * Move the marker to the user's latest pointer position.
   * @param pointer - The normalized image coordinates and hold state.
   */
  move(pointer) {
    this.#pointer = pointer;
    this.status.hidden = false;
    this.#position.textContent = translate("pointer.position", {
      x: Math.round(pointer.x * 100),
      y: Math.round(pointer.y * 100)
    });
    this.#place();
  }
  /**
   * Announce a hold or release after the server accepts it.
   * @param pointer - The pointer update accepted by the server.
   */
  confirm(pointer) {
    const message = pointer.active ? translate("pointer.held") : translate("pointer.released");
    if (this.#state.textContent !== message) this.#state.textContent = message;
  }
  /**
   * Hide the marker and announce that pointer input has stopped.
   */
  stop() {
    this.#pointer = void 0;
    this.#marker.hidden = true;
    if (!this.status.hidden) this.#state.textContent = translate("pointer.stopped");
  }
  #place() {
    const pointer = this.#pointer;
    if (!pointer || this.#image.hidden || document.activeElement !== this.#image) return;
    this.#marker.hidden = false;
    this.#marker.style.left = `${this.#image.offsetLeft + pointer.x * this.#image.clientWidth}px`;
    this.#marker.style.top = `${this.#image.offsetTop + pointer.y * this.#image.clientHeight}px`;
  }
};

// web/live/drag.ts
var DragInput = class {
  /**
   * Bind input until the panel's abort signal fires.
   * @param image - The output image that receives input.
   * @param signal - The panel's listener lifetime.
   * @param send - Receive pointer updates in normalized image coordinates.
   */
  constructor(image, signal, send) {
    this.image = image;
    this.send = send;
    image.tabIndex = 0;
    image.draggable = false;
    image.style.touchAction = "none";
    image.setAttribute("aria-label", translate("pointer.instructions"));
    image.addEventListener(
      "pointerdown",
      (event) => {
        if (event.button !== 0 || this.captured !== void 0) return;
        this.captured = event.pointerId;
        image.setPointerCapture(this.captured);
        image.focus();
        this.position(event);
      },
      { signal }
    );
    image.addEventListener(
      "pointermove",
      (event) => {
        if (this.captured === event.pointerId) this.position(event);
      },
      { signal }
    );
    for (const name of ["pointerup", "pointercancel", "lostpointercapture", "blur"])
      image.addEventListener(name, () => this.release(), { signal });
    image.addEventListener("keydown", (event) => this.keydown(event), { signal });
    image.addEventListener(
      "keyup",
      (event) => {
        if (event.key === " ") {
          event.preventDefault();
          event.stopPropagation();
          this.release();
        }
      },
      { signal }
    );
    window.addEventListener("blur", () => this.release(), { signal });
    document.addEventListener(
      "visibilitychange",
      () => {
        if (document.hidden) this.release();
      },
      { signal }
    );
    signal.addEventListener("abort", () => this.release(), { once: true });
  }
  image;
  send;
  pointer = { x: 0.5, y: 0.5, active: false };
  captured;
  /** Stop holding the pointer and release any browser pointer capture. */
  release() {
    const wasActive = this.pointer.active;
    this.pointer = { ...this.pointer, active: false };
    const previousCapture = this.captured;
    this.captured = void 0;
    if (wasActive) this.send(this.pointer);
    if (previousCapture !== void 0 && this.image.hasPointerCapture(previousCapture))
      this.image.releasePointerCapture(previousCapture);
  }
  /**
   * Normalize a drag event to the displayed image bounds.
   * @param event - The captured pointer event.
   */
  position(event) {
    const rect = this.image.getBoundingClientRect();
    this.pointer = {
      x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)),
      active: true
    };
    this.send(this.pointer);
  }
  /**
   * Move, hold, or release the pointer with the keyboard.
   * @param event - A key pressed while the preview has focus.
   */
  keydown(event) {
    const offsets = {
      ArrowLeft: [-0.03, 0],
      ArrowRight: [0.03, 0],
      ArrowUp: [0, -0.03],
      ArrowDown: [0, 0.03],
      " ": [0, 0],
      Escape: [0, 0]
    };
    const offset = Object.hasOwn(offsets, event.key) ? offsets[event.key] : void 0;
    if (!offset) return;
    event.preventDefault();
    event.stopPropagation();
    if (event.key === "Escape") {
      this.release();
      this.image.blur();
      return;
    }
    this.pointer = {
      x: Math.max(0, Math.min(1, this.pointer.x + offset[0])),
      y: Math.max(0, Math.min(1, this.pointer.y + offset[1])),
      active: event.key === " " || this.pointer.active
    };
    this.send(this.pointer);
  }
};

// web/live/controls.ts
var panels2 = /* @__PURE__ */ new Set();
var ControlPanel = class {
  /**
   * Build only the controls supported by this session.
   * @param owner - The validated session invitation.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(owner, fetcher) {
    this.owner = owner;
    this.fetcher = fetcher;
    this.dialog.className = "reactor-settings reactor-controls";
    this.dialog.setAttribute("aria-label", translate("controls.title"));
    this.image.alt = translate("live.output");
    this.image.hidden = true;
    this.pointerPreview = owner.pointer ? new PointerPreview(this.image, this.abort.signal) : void 0;
    this.status.setAttribute("role", "status");
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.prompt_limit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.update.disabled = true;
    this.sound = owner.sound ? new SoundControls(owner.audio_prompt, owner.audioPromptLimit) : void 0;
    this.camera = owner.webcam ? new Webcam(owner, fetcher, (message) => this.stop(message)) : void 0;
    if (owner.pointer)
      new DragInput(this.image, this.abort.signal, (next) => this.queuePointer(next));
    this.bindActions();
    this.appendContent();
  }
  owner;
  fetcher;
  prior = document.activeElement;
  abort = new AbortController();
  dialog = element("dialog");
  image = element("img");
  status = element("p", translate("controls.chooseInput"));
  prompt = element("textarea");
  start = button(translate("controls.start"));
  update = button(translate("live.applyPrompt"));
  end = button(translate("cancel"));
  pointerPreview;
  camera;
  sound;
  pointers = [];
  ending = false;
  finished = false;
  ready = false;
  sequence = 0;
  actionSequence = 0;
  previewSequence = 0;
  pendingPrompt;
  startRequested = false;
  startAttempted = false;
  /** Build the preview, supported inputs, and session actions. */
  appendContent() {
    this.dialog.append(
      element("h2", translate("controls.title")),
      element(
        "p",
        translate("live.duration", {
          model: this.owner.modelTitle,
          seconds: this.owner.duration_seconds
        })
      ),
      element("p", translate("controls.recordingNotice"))
    );
    if (this.camera) this.dialog.append(this.camera.view);
    this.dialog.append(this.pointerPreview?.view ?? this.image);
    if (this.owner.pointer)
      this.dialog.append(element("p", translate("controls.dragInstructions")));
    if (this.pointerPreview) this.dialog.append(this.pointerPreview.status);
    const label = element("label", translate("live.scenePrompt"));
    label.append(this.prompt);
    this.dialog.append(label, this.update);
    if (this.sound) this.dialog.append(this.sound.view);
    const footer = element("footer");
    const actions = element("div");
    actions.className = "reactor-actions";
    actions.append(this.start, this.end);
    footer.append(this.status, actions);
    this.dialog.append(footer);
  }
  /** Bind start, prompt, stop, and dialog cleanup actions. */
  bindActions() {
    this.start.addEventListener("click", () => {
      this.startRequested = true;
      this.start.disabled = true;
    });
    this.update.addEventListener("click", () => {
      if (!this.prompt.value.trim() && this.owner.model !== "reactor/sana-streaming") {
        this.status.textContent = translate("controls.emptyPrompt");
        return;
      }
      this.pendingPrompt = this.prompt.value;
      this.update.disabled = true;
    });
    this.end.addEventListener("click", () => {
      if (this.finished) this.dialog.close();
      else this.stop();
    });
    this.dialog.addEventListener("cancel", (event) => {
      event.preventDefault();
      if (this.finished) this.dialog.close();
      else this.stop();
    });
    this.dialog.addEventListener(
      "close",
      () => {
        this.stop();
        this.abort.abort();
        this.image.removeAttribute("src");
        this.dialog.remove();
        panels2.delete(this.owner.lease);
        if (this.prior instanceof HTMLElement && this.prior.isConnected) this.prior.focus();
      },
      { once: true }
    );
  }
  /**
   * Keep pointer releases while combining consecutive held moves.
   * @param next - The next normalized pointer update.
   */
  queuePointer(next) {
    if (!this.ready || this.ending) return;
    this.pointerPreview?.move(next);
    const previous = this.pointers.at(-1);
    if (previous?.active && next.active) this.pointers.pop();
    if (this.pointers.length >= browserLimits.maxPendingInputs) {
      this.stop(translate("controls.pointerRateExceeded"));
      return;
    }
    this.pointers.push(next);
  }
  /**
   * Stop sending input while waiting for the server to end the session.
   * @param message - The reason shown in the panel.
   */
  stop(message = translate("live.ending")) {
    this.ending = true;
    this.ready = false;
    this.start.disabled = this.update.disabled = true;
    this.sound?.setReady(false);
    this.pointerPreview?.stop();
    this.status.textContent = message;
    this.camera?.close();
  }
  /**
   * Apply current readiness and the latest preview.
   * @param reply - The validated session status.
   */
  display(reply) {
    const wasReady = this.ready;
    this.ready = reply.controls_ready && !reply.finishing && !this.ending;
    this.prompt.disabled = !this.ready;
    this.sound?.setReady(this.ready);
    if (this.ready && !wasReady) this.status.textContent = translate("controls.recording");
    this.update.disabled = !this.ready || this.pendingPrompt !== void 0;
    if (reply.preview) {
      this.image.src = `data:image/jpeg;base64,${reply.preview}`;
      this.image.hidden = false;
    }
    this.previewSequence = reply.preview_sequence;
  }
  /**
   * Release devices and explain how the session ended.
   * @param reply - The terminal session status.
   */
  finish(reply) {
    this.finished = true;
    this.camera?.close();
    this.start.disabled = this.update.disabled = true;
    this.sound?.setReady(false);
    this.pointerPreview?.stop();
    if (!reply.termination_confirmed)
      this.status.textContent = translate("controls.connectionClosed");
    else if (!this.startAttempted)
      this.status.textContent = translate("controls.recordingNotStarted");
    else
      this.status.textContent = reply.failed ? translate("live.discarded") : translate("live.ended");
    this.end.textContent = translate("close");
  }
  /**
   * Upload camera input and apply a requested start once a frame is ready.
   * @returns When this cycle's camera upload and start request finish.
   */
  async prepare() {
    const hasFrame = this.camera ? await this.camera.frame() : true;
    if (!this.startRequested) return;
    if (hasFrame) {
      this.startAttempted = true;
      await action(this.fetcher, this.owner, this.actionSequence++, "start", {});
      this.end.textContent = translate("live.endSession");
      this.status.textContent = translate("controls.connecting");
    } else {
      this.status.textContent = translate("controls.cameraRequired");
      this.start.disabled = false;
    }
    this.startRequested = false;
  }
  /**
   * Send queued prompt, pointer, and sound changes in order.
   * @returns When this cycle's pending controls have been sent.
   */
  async sendControls() {
    if (!this.ready) return;
    if (this.pendingPrompt !== void 0) {
      await action(this.fetcher, this.owner, this.actionSequence++, "prompt", {
        prompt: this.pendingPrompt
      });
      this.pendingPrompt = void 0;
      this.status.textContent = translate("controls.promptSent");
    }
    const next = this.pointers.shift();
    if (next) {
      await action(this.fetcher, this.owner, this.actionSequence++, "pointer", next);
      this.pointerPreview?.confirm(next);
    }
    const audioPrompt = this.sound?.takePrompt();
    if (audioPrompt !== void 0) {
      await action(this.fetcher, this.owner, this.actionSequence++, "audio_prompt", {
        prompt: audioPrompt
      });
      this.status.textContent = translate("controls.soundSent");
    }
  }
  /**
   * Read and display the session's current state.
   * @returns The validated session status.
   */
  async refresh() {
    const reply = await exchange(
      this.fetcher,
      this.owner,
      this.sequence++,
      {},
      this.ending,
      this.previewSequence,
      AbortSignal.timeout(2e3)
    );
    this.display(reply);
    return reply;
  }
  /**
   * Send input and check whether a rejection coincided with session completion.
   * @param reply - The status received before sending input.
   * @returns The current status after input is sent or recording ends.
   */
  async sendInput(reply) {
    try {
      await this.prepare();
      await this.sendControls();
      return reply;
    } catch (error) {
      const current5 = await this.refresh();
      if (!current5.closed && !current5.finishing) throw error;
      return current5;
    }
  }
  /**
   * Exchange status, apply pending input, and handle session completion.
   * @returns Whether the session needs another status update.
   */
  async cycle() {
    let reply = await this.refresh();
    if (!this.ending && !reply.closed && !reply.finishing) reply = await this.sendInput(reply);
    if (reply.closed) this.finish(reply);
    else if (reply.finishing) {
      this.camera?.close();
      this.status.textContent = translate("live.ending");
    }
    return !this.finished;
  }
  /**
   * Exchange status and input until the session ends or the panel closes.
   * @returns When polling ends and the panel shows its final state.
   */
  async poll() {
    try {
      while (!this.finished && !this.abort.signal.aborted) {
        if (!await this.cycle()) break;
        await new Promise((resolve) => setTimeout(resolve, browserLimits.pollIntervalMilliseconds));
      }
    } catch (error) {
      this.stop(error instanceof Error ? error.message : translate("controls.connectionEnded"));
      this.finished = true;
      this.end.textContent = translate("close");
    }
  }
  /** Show the session panel and begin the local status exchange. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.start.focus();
    void this.poll();
  }
};
function openControls(value, fetcher) {
  const owner = controls(value);
  if (!owner || panels2.has(owner.lease)) return;
  panels2.add(owner.lease);
  const panel = new ControlPanel(owner, fetcher);
  panel.show();
}

// web/discovery/pricing.ts
function formatCreditSummary(model2, seconds) {
  const rate = model2.credits_per_second;
  if (rate === null) return [translate("pricing.rateUnavailable")];
  const details = [translate("pricing.rate", { rate: rate.toLocaleString() })];
  if (!model2.observed) {
    details.push(translate("pricing.rateOutdated"));
  } else if (seconds !== void 0) {
    const credits = (rate * seconds).toLocaleString(void 0, {
      maximumFractionDigits: 2
    });
    details.push(
      translate("pricing.calculation", {
        seconds: seconds.toLocaleString(),
        rate: rate.toLocaleString(),
        credits
      })
    );
  }
  return details;
}

// web/discovery/row.ts
function modelRow(model2, seconds) {
  const row = element("li");
  row.append(element("h3", model2.title), element("code", model2.name));
  const support = model2.support === "available" ? translate("models.nodesAvailable") : translate("models.nodeUnavailable");
  row.append(element("p", support));
  if (model2.connect_name)
    row.append(element("p", translate("models.connectName", { name: model2.connect_name })));
  for (const detail of formatCreditSummary(model2, seconds)) row.append(element("p", detail));
  if (model2.documentation_url) {
    const link = element("a", translate("models.openGuide"));
    link.href = model2.documentation_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    row.append(link);
  } else row.append(element("p", translate("models.guideUnavailable")));
  return row;
}

// web/discovery/api.ts
var INVALID_MODEL_LIST = translate("models.invalidResponse");
function record(value) {
  if (!value || typeof value !== "object" || Array.isArray(value))
    throw new Error(INVALID_MODEL_LIST);
  return value;
}
function shortText(value, max = 200) {
  return typeof value === "string" && value.length > 0 && value.length <= max;
}
function model(value) {
  const row = record(value);
  if (!shortText(row.key) || !shortText(row.name) || !shortText(row.title) || !(row.connect_name === null || shortText(row.connect_name)) || !(row.documentation_url === null || typeof row.documentation_url === "string" && /^https:\/\/docs\.reactor\.inc\/model-api-reference\/[a-z0-9._-]+\/overview$/.test(
    row.documentation_url
  )) || !(row.credits_per_second === null || typeof row.credits_per_second === "number" && Number.isFinite(row.credits_per_second) && row.credits_per_second >= 0) || typeof row.observed !== "boolean" || !["available", "adapter_required"].includes(String(row.support)) || !Array.isArray(row.node_ids) || row.node_ids.length > 100 || !row.node_ids.every((id) => typeof id === "string" && /^ReactorInc[A-Za-z0-9]+$/.test(id)))
    throw new Error(INVALID_MODEL_LIST);
  return row;
}
function parseCatalog(value) {
  const document2 = record(value);
  if (typeof document2.revision !== "string" || !browserPatterns.revision.test(document2.revision) || !(document2.retrieved_at === null || shortText(document2.retrieved_at, 40) && Number.isFinite(Date.parse(document2.retrieved_at))) || typeof document2.can_rollback !== "boolean" || typeof document2.mutation_allowed !== "boolean" || !Array.isArray(document2.models) || document2.models.length < 1 || document2.models.length > 1024)
    throw new Error(INVALID_MODEL_LIST);
  const models = document2.models.map(model);
  if (document2.automatic_check !== void 0) {
    const check = record(document2.automatic_check);
    if (typeof check.enabled !== "boolean" || typeof check.running !== "boolean" || typeof check.interval_hours !== "number" || !Number.isSafeInteger(check.interval_hours) || check.interval_hours < 1 || !(check.checked_at === null || shortText(check.checked_at, 40) && Number.isFinite(Date.parse(check.checked_at))) || !(check.update_available === null || typeof check.update_available === "boolean") || !(check.error === null || shortText(check.error, 1024)))
      throw new Error(INVALID_MODEL_LIST);
  }
  if (new Set(models.map((row) => row.key)).size !== models.length)
    throw new Error(INVALID_MODEL_LIST);
  return { ...document2, models };
}
function metadataStatus(retrievedAt) {
  return retrievedAt === null ? translate("models.installedList") : translate("models.lastRefresh", { date: new Date(retrievedAt).toLocaleString() });
}
async function requestModels(fetcher, signal, action2, revision) {
  const options = {
    method: action2 === "read" ? "GET" : "POST",
    cache: "no-store",
    credentials: "same-origin",
    signal: AbortSignal.any([signal, AbortSignal.timeout(3e4)]),
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" }
  };
  if (action2 === "rollback") options.body = JSON.stringify({ revision });
  const suffix = action2 === "read" ? "" : `/${action2}`;
  let response;
  try {
    response = await fetcher(`/reactor-inc/v1/catalog${suffix}`, options);
  } catch {
    throw new Error(translate("models.unreachable"));
  }
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error(INVALID_MODEL_LIST);
  }
  if (!response.ok) {
    const error = record(body).error;
    throw new Error(shortText(error, 1024) ? error : translate("models.requestFailed"));
  }
  return parseCatalog(body);
}

// web/discovery/dialog.ts
var current;
function automaticStatus(check) {
  if (!check) return "";
  if (!check.enabled) return translate("models.checksOff");
  if (check.running) return translate("models.checkRunning");
  if (check.error) return check.error;
  if (check.update_available === true) return translate("models.listChanged");
  if (check.checked_at)
    return translate("models.checkSchedule", {
      date: new Date(check.checked_at).toLocaleString(),
      hours: check.interval_hours
    });
  return translate("models.checkDue");
}
var ModelDialog = class {
  /**
   * Build the model browser and its optional node filter.
   * @param fetcher - ComfyUI's local API client.
   * @param nodeId - Show models supported by this node, if supplied.
   */
  constructor(fetcher, nodeId2) {
    this.fetcher = fetcher;
    this.nodeId = nodeId2;
    this.dialog.className = "reactor-settings reactor-catalog";
    this.dialog.setAttribute("aria-labelledby", "reactor-catalog-title");
    const heading = element("h2", translate("models.title"));
    heading.id = "reactor-catalog-title";
    const close = button(translate("close"));
    close.setAttribute("aria-label", translate("models.close"));
    close.addEventListener("click", () => this.dialog.close());
    const header = element("header");
    header.append(heading, close);
    const searchLabel = element("label", translate("models.search"));
    this.search.type = "search";
    this.search.placeholder = translate("models.searchPlaceholder");
    searchLabel.append(this.search);
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.list.setAttribute("aria-label", translate("models.title"));
    const sources = element("details");
    sources.append(element("summary", translate("models.sources")), this.checked, this.automatic);
    this.dialog.append(
      header,
      element("p", translate("models.refreshNotice")),
      this.actions(),
      this.status,
      searchLabel,
      this.calculation(),
      sources,
      this.count,
      this.list
    );
    this.search.addEventListener("input", () => this.render());
    this.duration.addEventListener("input", () => this.render());
    this.dialog.addEventListener("close", () => this.dispose(), { once: true });
  }
  fetcher;
  nodeId;
  dialog = element("dialog");
  previousFocus = document.activeElement;
  controller = new AbortController();
  search = element("input");
  duration = element("input");
  refresh = button(translate("models.refresh"));
  rollback = button(translate("models.restore"));
  status = element("p", translate("models.loadingLocal"));
  checked = element("p");
  automatic = element("p");
  count = element("p");
  list = element("ul");
  catalog;
  /**
   * Build list updates and the node filter reset.
   * @returns The model browser actions.
   */
  actions() {
    const showAll = button(translate("models.showAll"));
    showAll.hidden = !this.nodeId;
    showAll.addEventListener("click", () => {
      this.nodeId = void 0;
      showAll.hidden = true;
      this.render();
    });
    this.refresh.disabled = this.rollback.disabled = true;
    this.refresh.addEventListener("click", () => void this.updateModels("refresh"));
    this.rollback.addEventListener("click", () => void this.updateModels("rollback"));
    const actions = element("div");
    actions.className = "reactor-actions";
    actions.append(this.refresh, this.rollback, showAll);
    return actions;
  }
  /**
   * Build the optional session time calculation.
   * @returns The collapsed calculation controls.
   */
  calculation() {
    const label = element("label", translate("pricing.sessionTime"));
    this.duration.type = "number";
    this.duration.min = "0.1";
    this.duration.max = String(browserLimits.maxCalculatorSeconds);
    this.duration.step = "any";
    this.duration.placeholder = translate("pricing.enterTime");
    label.append(this.duration);
    const calculation = element("details");
    calculation.append(
      element("summary", translate("pricing.calculate")),
      label,
      element("p", translate("pricing.totalTimeNotice"))
    );
    return calculation;
  }
  /** Update matching models and calculations from the current controls. */
  render() {
    const query = this.search.value.trim().toLowerCase();
    const nodeId2 = this.nodeId;
    const visible = this.catalog?.models.filter(
      (model2) => (!nodeId2 || model2.node_ids.includes(nodeId2)) && `${model2.name} ${model2.title} ${model2.connect_name ?? ""}`.toLowerCase().includes(query)
    ) ?? [];
    const seconds = this.duration.validity.valid && this.duration.value !== "" ? this.duration.valueAsNumber : void 0;
    this.list.replaceChildren(...visible.map((model2) => modelRow(model2, seconds)));
    this.count.textContent = translate("models.count", {
      visible: visible.length,
      total: this.catalog?.models.length ?? 0
    });
  }
  /**
   * Read or update the locally stored model list.
   * @param action - Read, refresh from public sources, or restore the previous list.
   * @returns When the model list or error is displayed.
   */
  async updateModels(action2) {
    this.refresh.disabled = this.rollback.disabled = true;
    this.status.textContent = action2 === "refresh" ? translate("models.checking") : translate("models.loading");
    try {
      const next = await requestModels(
        this.fetcher,
        this.controller.signal,
        action2,
        this.catalog?.revision
      );
      if (this.controller.signal.aborted) return;
      this.catalog = next;
      this.checked.textContent = metadataStatus(next.retrieved_at);
      this.automatic.textContent = automaticStatus(next.automatic_check);
      this.status.textContent = {
        refresh: translate("models.refreshed"),
        rollback: translate("models.restored"),
        read: translate("models.loaded")
      }[action2];
      this.render();
    } catch (error) {
      if (!this.controller.signal.aborted)
        this.status.textContent = error instanceof Error ? error.message : translate("models.loadFailed");
    } finally {
      this.restoreActions();
    }
  }
  /** Re-enable allowed list changes after the current request finishes. */
  restoreActions() {
    if (this.controller.signal.aborted) return;
    this.refresh.disabled = !this.catalog?.mutation_allowed;
    this.rollback.disabled = !this.catalog?.mutation_allowed || !this.catalog.can_rollback;
  }
  /** Show the dialog and read the local model list. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    void this.updateModels("read");
  }
  /** Stop pending requests and return focus to the caller. */
  dispose() {
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = void 0;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
};
function openModels(fetcher, nodeId2) {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new ModelDialog(fetcher, nodeId2);
  current.show();
}

// web/settings/api.ts
function record2(value) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(translate("settings.invalidResponse"));
  }
  return value;
}
function parseDefinitions(value) {
  const definitions = record2(value);
  if (!Object.hasOwn(definitions, "catalog_interval_hours"))
    throw new Error(translate("settings.incompleteResponse"));
  const result = {};
  for (const [name, raw] of Object.entries(definitions)) {
    const field = record2(raw);
    if (!/^[a-z][a-z_]+$/.test(name) || typeof field.label !== "string" || field.label.length < 1 || field.label.length > 200 || typeof field.minimum !== "number" || !Number.isSafeInteger(field.minimum) || typeof field.maximum !== "number" || !Number.isSafeInteger(field.maximum) || field.minimum > field.maximum)
      throw new Error(translate("settings.invalidDefinition"));
    result[name] = { label: field.label, minimum: field.minimum, maximum: field.maximum };
  }
  return result;
}
function parseConfiguration(value) {
  const document2 = record2(value);
  const settings = record2(document2.settings);
  const credential = record2(document2.credential);
  if (typeof document2.revision !== "string" || !browserPatterns.revision.test(document2.revision) || typeof document2.mutation_allowed !== "boolean" || typeof credential.source !== "string" || !["missing", "saved", "environment"].includes(credential.source)) {
    throw new Error(translate("settings.invalidResponse"));
  }
  const definitions = parseDefinitions(document2.integer_settings);
  if (typeof settings.catalog_auto_check !== "boolean" || typeof document2.credential_limit !== "number" || !Number.isSafeInteger(document2.credential_limit) || document2.credential_limit < 1)
    throw new Error(translate("settings.invalidChecks"));
  for (const [name, definition] of Object.entries(definitions)) {
    const value2 = settings[name];
    if (typeof value2 !== "number" || !Number.isSafeInteger(value2) || value2 < definition.minimum || value2 > definition.maximum)
      throw new Error(translate("settings.invalidLimit"));
  }
  return {
    revision: document2.revision,
    credentialSource: credential.source,
    mutationAllowed: document2.mutation_allowed,
    settings,
    definitions,
    credentialLimit: document2.credential_limit
  };
}
async function requestConfiguration(fetcher, signal, route = "/status", method = "GET", body) {
  const options = {
    method,
    cache: "no-store",
    credentials: "same-origin",
    signal: AbortSignal.any([
      signal,
      AbortSignal.timeout(browserLimits.requestTimeoutMilliseconds)
    ]),
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" }
  };
  if (body !== void 0) options.body = JSON.stringify(body);
  let response;
  try {
    response = await fetcher(`/reactor-inc/v1${route}`, options);
  } catch {
    throw new Error(translate("settings.unreachable"));
  }
  let document2;
  try {
    document2 = await response.json();
  } catch {
    throw new Error(translate("settings.unreadableResponse"));
  }
  if (!response.ok) {
    const error = record2(document2).error;
    throw new Error(
      typeof error === "string" && error.length <= 1024 ? error : translate("settings.saveFailed")
    );
  }
  return parseConfiguration(document2);
}

// web/settings/dialog.ts
var current2;
var SettingsDialog = class {
  /**
   * Build settings forms without contacting Reactor.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(fetcher) {
    this.fetcher = fetcher;
    this.dialog.className = "reactor-settings";
    this.dialog.setAttribute("aria-labelledby", "reactor-settings-title");
    const heading = element("h2", translate("settings.title"));
    heading.id = "reactor-settings-title";
    const close = button(translate("close"));
    close.setAttribute("aria-label", translate("settings.close"));
    close.addEventListener("click", () => this.dialog.close());
    const header = element("header");
    header.append(heading, close);
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.reload.addEventListener(
      "click",
      () => void this.updateSettings(translate("settings.loaded"))
    );
    this.dialog.append(
      header,
      element("p", translate("settings.accountNotice")),
      this.source,
      this.credentials(),
      element("p", translate("settings.keyNotice")),
      this.limits(),
      element("p", translate("settings.timeNotice")),
      this.modelUpdates(),
      this.status,
      this.reload
    );
    this.dialog.addEventListener("close", () => this.dispose(), { once: true });
  }
  fetcher;
  dialog = element("dialog");
  previousFocus = document.activeElement;
  controller = new AbortController();
  status = element("p", translate("settings.loading"));
  source = element("p");
  reload = button(translate("settings.reload"));
  key = element("input");
  keyFields = element("fieldset");
  limitFields = element("fieldset");
  catalogFields = element("fieldset");
  automatic = element("input");
  interval = element("input");
  inputs = /* @__PURE__ */ new Map();
  configuration;
  /**
   * Build the private key form.
   * @returns The form for saving or clearing the server's key.
   */
  credentials() {
    const form = element("form");
    this.keyFields.disabled = true;
    const label = element("label", translate("settings.credentialLabel"));
    this.key.type = "password";
    this.key.autocomplete = "off";
    this.key.spellcheck = false;
    this.key.required = true;
    label.append(this.key);
    const clear = button(translate("settings.clearKey"));
    clear.addEventListener("click", () => {
      this.key.value = "";
      void this.updateSettings(translate("settings.keyCleared"), "/credential", "DELETE");
    });
    const actions = element("div");
    actions.className = "reactor-actions";
    actions.append(button(translate("settings.saveKey"), "submit"), clear);
    this.keyFields.append(element("legend", translate("settings.credentials")), label, actions);
    form.append(this.keyFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const value = this.key.value;
      this.key.value = "";
      void this.updateSettings(translate("settings.keySaved"), "/credential", "PUT", {
        api_key: value
      });
    });
    return form;
  }
  /**
   * Build duration, timeout, and media size inputs.
   * @returns The form for execution limits.
   */
  limits() {
    const form = element("form");
    this.limitFields.disabled = true;
    this.limitFields.append(element("legend", translate("settings.limits")));
    this.limitFields.append(button(translate("settings.saveLimits"), "submit"));
    form.append(this.limitFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveLimits(this.configuration);
    });
    return form;
  }
  /**
   * Build fields from the backend's setting definitions.
   * @param configuration - The validated limits and labels.
   */
  populateLimits(configuration) {
    this.limitFields.replaceChildren(element("legend", translate("settings.limits")));
    const advanced = element("details");
    advanced.append(element("summary", translate("settings.advancedLimits")));
    for (const [index, [name, definition]] of Object.entries(configuration.definitions).filter(([name2]) => name2 !== "catalog_interval_hours").entries()) {
      const label = element(
        "label",
        translate(`settings.limit.${name}`, {}, definition.label)
      );
      const input = element("input");
      input.type = "number";
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.step = "1";
      input.required = true;
      this.inputs.set(name, input);
      label.append(input);
      (index < 2 ? this.limitFields : advanced).append(label);
    }
    this.limitFields.append(advanced, button(translate("settings.saveLimits"), "submit"));
  }
  /**
   * Save only limits changed since the last successful read.
   * @param configuration - The settings and revision currently shown.
   */
  saveLimits(configuration) {
    const changes = {};
    for (const [name, input] of this.inputs) {
      if (input.valueAsNumber !== configuration.settings[name]) changes[name] = input.valueAsNumber;
    }
    if (Object.keys(changes).length === 0) {
      this.status.textContent = translate("settings.noLimitChanges");
      return;
    }
    void this.updateSettings(translate("settings.limitsSaved"), "/settings", "PATCH", {
      revision: configuration.revision,
      settings: changes
    });
  }
  /**
   * Build the controls for checking public model sources.
   * @returns The automatic model check form.
   */
  modelUpdates() {
    const form = element("form");
    this.catalogFields.disabled = true;
    const automaticLabel = element("label", translate("settings.automaticChecks"));
    this.automatic.type = "checkbox";
    automaticLabel.prepend(this.automatic);
    const intervalLabel = element("label", translate("settings.checkInterval"));
    this.interval.type = "number";
    this.interval.step = "1";
    this.interval.required = true;
    intervalLabel.append(this.interval);
    this.catalogFields.append(
      element("legend", translate("settings.modelUpdates")),
      automaticLabel,
      intervalLabel,
      element("p", translate("settings.checkNotice")),
      button(translate("settings.saveChecks"), "submit")
    );
    form.append(this.catalogFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveModelUpdates(this.configuration);
    });
    return form;
  }
  /**
   * Save automatic checks without changing the displayed model list.
   * @param configuration - The settings and revision currently shown.
   */
  saveModelUpdates(configuration) {
    const settings = {
      catalog_auto_check: this.automatic.checked,
      catalog_interval_hours: this.interval.valueAsNumber
    };
    if (settings.catalog_auto_check === configuration.settings.catalog_auto_check && settings.catalog_interval_hours === configuration.settings.catalog_interval_hours) {
      this.status.textContent = translate("settings.noCheckChanges");
      return;
    }
    void this.updateSettings(translate("settings.checksSaved"), "/settings", "PATCH", {
      revision: configuration.revision,
      settings
    });
  }
  /**
   * Show validated settings and apply the server's editing policy.
   * @param configuration - The last successful server response.
   */
  display(configuration) {
    this.configuration = configuration;
    if (this.inputs.size === 0) this.populateLimits(configuration);
    this.key.maxLength = configuration.credentialLimit;
    const interval = configuration.definitions.catalog_interval_hours;
    this.interval.min = String(interval.minimum);
    this.interval.max = String(interval.maximum);
    this.source.textContent = {
      missing: translate("settings.missingKey"),
      saved: translate("settings.savedKey"),
      environment: translate("settings.environmentKey")
    }[configuration.credentialSource];
    this.automatic.checked = configuration.settings.catalog_auto_check;
    this.interval.value = String(configuration.settings.catalog_interval_hours);
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const input = this.inputs.get(name);
      if (!input) continue;
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.value = String(configuration.settings[name]);
    }
    if (!configuration.mutationAllowed) this.status.textContent = translate("settings.readOnly");
  }
  /**
   * Keep settings requests serial and show the server's response.
   * @param message - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @returns When the response or error is displayed.
   */
  async updateSettings(message, route, method, body) {
    this.keyFields.disabled = this.limitFields.disabled = this.catalogFields.disabled = true;
    this.reload.disabled = true;
    this.status.textContent = translate("working");
    try {
      const value = await requestConfiguration(
        this.fetcher,
        this.controller.signal,
        route,
        method,
        body
      );
      if (this.controller.signal.aborted) return;
      this.status.textContent = message;
      this.display(value);
    } catch (error) {
      if (!this.controller.signal.aborted)
        this.status.textContent = error instanceof Error ? error.message : translate("settings.updateFailed");
    } finally {
      if (!this.controller.signal.aborted) {
        this.keyFields.disabled = this.limitFields.disabled = this.catalogFields.disabled = !this.configuration?.mutationAllowed;
        this.reload.disabled = false;
      }
    }
  }
  /** Show the dialog and read local settings. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    void this.updateSettings(translate("settings.loaded"));
  }
  /** Clear the key input, stop requests, and return focus to the caller. */
  dispose() {
    this.key.value = "";
    this.controller.abort();
    this.dialog.remove();
    if (current2 === this) current2 = void 0;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
};
function openSettings(fetcher) {
  if (current2?.dialog.open) {
    current2.dialog.focus();
    return;
  }
  current2 = new SettingsDialog(fetcher);
  current2.show();
}

// web/discovery/rate.ts
function requestedSeconds(node) {
  function value(name) {
    if (node.inputs?.some((input) => input.name === name && input.link != null)) return void 0;
    const raw = node.widgets?.find((widget) => widget.name === name)?.value;
    return typeof raw === "number" && Number.isFinite(raw) && raw > 0 ? raw : void 0;
  }
  if (node.comfyClass === "ReactorIncFastContinue") {
    const seconds = value("clip_seconds");
    const count = value("clip_count");
    return seconds !== void 0 && count !== void 0 ? seconds * count : void 0;
  }
  return value("duration_seconds");
}
var current3;
var CreditDialog = class {
  /**
   * Build the calculator for a node.
   * @param node - The node whose public rate is requested.
   */
  constructor(node) {
    this.node = node;
    this.dialog.className = "reactor-settings";
    this.dialog.setAttribute("aria-labelledby", "reactor-rate-title");
    const title = element("h2", translate("pricing.title"));
    title.id = "reactor-rate-title";
    const close = button(translate("close"));
    close.addEventListener("click", () => this.dialog.close());
    const header = element("header");
    header.append(title, close);
    const seconds = requestedSeconds(node);
    const request = element(
      "p",
      seconds === void 0 ? translate("pricing.unknownDuration") : translate("pricing.requestedDuration", { seconds: seconds.toLocaleString() })
    );
    const label = element("label", translate("pricing.sessionTime"));
    this.duration.type = "number";
    this.duration.min = "0.1";
    this.duration.max = String(browserLimits.maxCalculatorSeconds);
    this.duration.step = "any";
    this.duration.placeholder = translate("pricing.enterTime");
    if (seconds !== void 0) this.duration.value = String(seconds);
    label.append(this.duration);
    this.validation.setAttribute("role", "status");
    this.status.setAttribute("role", "status");
    this.rates.setAttribute("aria-live", "polite");
    this.dialog.append(
      header,
      request,
      label,
      this.validation,
      element("p", translate("pricing.estimateNotice")),
      this.status,
      this.rates
    );
    this.duration.addEventListener("input", () => this.render());
    this.dialog.addEventListener("close", () => this.dispose(), { once: true });
    this.render();
  }
  node;
  dialog = element("dialog");
  previousFocus = document.activeElement;
  controller = new AbortController();
  duration = element("input");
  validation = element("p");
  status = element("p", translate("pricing.loading"));
  rates = element("div");
  models = [];
  /**
   * Read public rates from the local model list.
   * @param fetcher - ComfyUI's local API client.
   * @returns When rates or an error are displayed.
   */
  async readRates(fetcher) {
    try {
      const catalog = await requestModels(fetcher, this.controller.signal, "read");
      if (this.controller.signal.aborted) return;
      this.models = catalog.models.filter(
        (model2) => model2.node_ids.includes(this.node.comfyClass ?? "")
      );
      this.status.textContent = metadataStatus(catalog.retrieved_at);
      if (!this.models.length) this.status.textContent = translate("pricing.modelUnavailable");
      this.render();
    } catch (error) {
      if (!this.controller.signal.aborted)
        this.status.textContent = error instanceof Error ? error.message : translate("pricing.loadFailed");
    }
  }
  /** Validate session time and update every rate calculation. */
  render() {
    const valid = this.duration.value !== "" && this.duration.validity.valid;
    this.validation.textContent = valid ? "" : translate("pricing.timeRange", {
      maximum: browserLimits.maxCalculatorSeconds.toLocaleString()
    });
    this.rates.replaceChildren();
    for (const model2 of this.models) {
      this.rates.append(element("h3", model2.title));
      const seconds = valid ? this.duration.valueAsNumber : void 0;
      for (const detail of formatCreditSummary(model2, seconds))
        this.rates.append(element("p", detail));
    }
  }
  /**
   * Show the calculator and read local rates.
   * @param fetcher - ComfyUI's local API client.
   */
  show(fetcher) {
    document.body.append(this.dialog);
    this.dialog.showModal();
    void this.readRates(fetcher);
  }
  /** Stop the request and return focus to the caller. */
  dispose() {
    this.controller.abort();
    this.dialog.remove();
    if (current3 === this) current3 = void 0;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
};
function openCreditRate(node, fetcher) {
  if (current3?.dialog.open) {
    current3.dialog.focus();
    return;
  }
  current3 = new CreditDialog(node);
  current3.show(fetcher);
}
function bindCreditRate(node, fetcher) {
  const id = node.comfyClass;
  if (!id?.startsWith("ReactorInc") || id === "ReactorIncHeliosAddPrompt" || id === "ReactorIncLongLiveAddShot")
    return;
  node.addWidget("button", translate("pricing.viewRate"), "", () => openCreditRate(node, fetcher), {
    serialize: false
  });
}

// web/nodes/labels.ts
function configureNodeWidgets(node) {
  if (!node.comfyClass?.startsWith("ReactorInc")) return;
  const control = node.widgets?.find((widget) => widget.name === "control_after_generate");
  if (control) control.label = translate("nodes.seedBehavior");
  for (const widget of node.widgets ?? []) {
    if (typeof widget.options?.advanced !== "boolean") continue;
    const connected = node.inputs?.some(
      (input) => input.name === widget.name && input.link != null
    );
    widget.advanced = widget.options.advanced && !connected;
  }
}
function bindNodeWidgets(node) {
  if (!node.comfyClass?.startsWith("ReactorInc")) return;
  configureNodeWidgets(node);
  const changed = node.onConnectionsChange;
  node.onConnectionsChange = function(...args) {
    changed?.apply(this, args);
    configureNodeWidgets(node);
  };
}

// web/help/command.ts
import { app as app2 } from "../../scripts/app.js";

// web/help/dialog.ts
var current4;
function openHelpDialog(nodeId2) {
  current4?.close();
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  current4 = dialog;
  dialog.className = "reactor-settings reactor-node-help";
  dialog.setAttribute("aria-labelledby", "reactor-node-help-title");
  const heading = element("h2", translate("help.title"));
  heading.id = "reactor-node-help-title";
  const close = button(translate("close"));
  close.setAttribute("aria-label", translate("help.close"));
  close.addEventListener("click", () => dialog.close());
  const header = element("header");
  header.append(heading, close);
  const frame = element("iframe");
  frame.title = translate("help.guide");
  frame.sandbox.add(
    "allow-same-origin",
    "allow-popups",
    "allow-popups-to-escape-sandbox",
    "allow-downloads"
  );
  frame.src = `/extensions/reactor-inc/guides/nodes/${nodeId2}.html`;
  frame.addEventListener("load", () => prepareGuide(frame, dialog, controller.signal));
  dialog.append(header, frame);
  dialog.addEventListener(
    "close",
    () => {
      controller.abort();
      dialog.remove();
      if (current4 === dialog) current4 = void 0;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    },
    { once: true }
  );
  document.body.append(dialog);
  dialog.showModal();
  close.focus();
}
function prepareGuide(frame, dialog, signal) {
  const guide = frame.contentDocument;
  if (!guide) return;
  const colors = getComputedStyle(dialog);
  guide.body.style.background = colors.backgroundColor;
  guide.body.style.color = colors.color;
  for (const link of guide.querySelectorAll("a")) {
    link.style.color = "inherit";
    if (new URL(link.href).origin !== location.origin) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.append(translate("help.newTab"));
    }
  }
  for (const block of guide.querySelectorAll("pre")) {
    block.style.background = colors.getPropertyValue("--comfy-input-bg") || colors.backgroundColor;
  }
  guide.addEventListener(
    "keydown",
    (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        dialog.close();
      }
    },
    { signal }
  );
}

// web/help/command.ts
var HELP_COMMAND = "ReactorInc.OpenNodeHelp";
function nodeId(item) {
  if (typeof item !== "object" || item === null || !("comfyClass" in item)) return;
  const id = item.comfyClass;
  return typeof id === "string" && /^ReactorInc[A-Za-z0-9]+$/.test(id) ? id : void 0;
}
function helpCommands(item) {
  if (!nodeId(item)) return [];
  return [HELP_COMMAND];
}
function openNodeHelp() {
  const id = Array.from(app2.canvas.selectedItems ?? []).map(nodeId).find(Boolean);
  if (!id) return;
  openHelpDialog(id);
}

// web/extension.ts
function requestLocal(route, options) {
  const selected = app3.extensionManager.setting.get("Comfy.Locale");
  const headers = new Headers(options.headers);
  headers.set("Accept-Language", typeof selected === "string" ? selected : "en");
  return api2.fetchApi(route, { ...options, headers });
}
var stylesheet = document.createElement("link");
stylesheet.rel = "stylesheet";
stylesheet.href = new URL("./main.css", import.meta.url).href;
document.head.append(stylesheet);
api2.addEventListener("reactor-inc.live", (event) => {
  if (event instanceof CustomEvent) {
    openLive(event.detail, requestLocal);
  }
});
api2.addEventListener("reactor-inc.controls", (event) => {
  if (event instanceof CustomEvent) openControls(event.detail, requestLocal);
});
app3.registerExtension({
  name: "reactor.inc.configuration",
  setup: loadLanguage,
  // eslint-disable-next-line local/no-trivial-functions -- ComfyUI calls this hook once to attach labels and the credit rate button.
  nodeCreated: (node) => {
    bindNodeWidgets(node);
    bindCreditRate(node, requestLocal);
  },
  loadedGraphNode: configureNodeWidgets,
  getSelectionToolboxCommands: helpCommands,
  commands: [
    {
      id: HELP_COMMAND,
      label: translate("help"),
      icon: "pi pi-question-circle",
      function: openNodeHelp
    },
    {
      id: "ReactorInc.OpenSettings",
      label: translate("settings.title"),
      function: () => openSettings(requestLocal)
    },
    {
      id: "ReactorInc.OpenCatalog",
      label: translate("models.title"),
      function: () => openModels(requestLocal)
    }
  ],
  menuCommands: [
    {
      path: ["Extensions", "Reactor"],
      commands: ["ReactorInc.OpenSettings", "ReactorInc.OpenCatalog"]
    }
  ]
});
