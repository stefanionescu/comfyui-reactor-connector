// web/extension.ts
import { api as api3 } from "../../scripts/api.js";
import { app as app3 } from "../../scripts/app.js";

// web/http.ts
import { api as api2 } from "../../scripts/api.js";

// web/language.ts
import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

// locales/en/main.json
var main_default = {
  reactorInc: {
    cancel: "Cancel",
    close: "Close",
    help: "Help",
    working: "Working…",
    "camera.accessFailed": "Camera access failed. Choose a camera and try again.",
    "camera.browserRequirements": "Camera access needs localhost or HTTPS and a supported browser.",
    "camera.busy": "Close other apps using the camera, then try again.",
    "camera.default": "Default camera",
    "camera.disabled": "Camera off.",
    "camera.disconnected": "The camera disconnected. The session is ending.",
    "camera.enable": "Enable camera",
    "camera.enabled": "Camera on. Microphone audio is off.",
    "camera.label": "Camera",
    "camera.notFound": "Connect a camera, then try again.",
    "camera.number": "Camera {number}",
    "camera.permissionDenied": "Allow camera access in the app or browser settings, then try again.",
    "camera.preview": "Your camera input",
    "camera.readFailed": "Camera frames could not be read.",
    "camera.select": "Use selected camera",
    "camera.unavailableSelection": "The selected camera is unavailable. Choose another camera.",
    "camera.uploadFailed": "Camera frames could not reach the session.",
    "controls.cameraRequired": "Enable a camera before starting.",
    "controls.chooseInput": "Choose your input, then start within 60 seconds.",
    "controls.connecting": "Connecting to Reactor…",
    "controls.connectionClosed": "Connection closed. Check Reactor session status before starting again.",
    "controls.connectionEnded": "The live connection ended.",
    "controls.dragInstructions": "Drag on the output to steer the subject. Release to stop. With the picture focused, arrow keys position the pointer, Space holds it, and Escape releases it.",
    "controls.emptyPrompt": "Enter a prompt before applying it.",
    "controls.pointerRateExceeded": "Pointer input arrived too quickly. The session is ending.",
    "controls.promptSent": "Prompt sent. The model applies changes to later frames.",
    "controls.recording": "Recording. Live controls are ready.",
    "controls.recordingNotStarted": "Recording did not start. Close this panel to view the workflow result.",
    "controls.recordingNotice": "Recording stops at the chosen duration. Ending early discards the unfinished video. The preview has no sound.",
    "controls.soundSent": "Sound prompt sent. The model applies changes to later audio.",
    "controls.start": "Start session",
    "controls.title": "Reactor live controls",
    "errors.acceptedClipChanged": "Fast H3 changed a clip's accepted length.",
    "errors.acceptedSequenceLimit": "The accepted clip lengths exceed the video duration limit. Choose fewer clips.",
    "errors.accessRefused": "Reactor refused access. Check your key and model access.",
    "errors.anchorInterval": "Choose an anchor interval from 0 to 1,000.",
    "errors.aspectRatio": "Choose an offered aspect ratio.",
    "errors.audioIncomplete": "The recording audio is incomplete.",
    "errors.audioLimit": "The recording audio exceeds its native limits.",
    "errors.authenticationFailed": "Reactor could not authenticate. Check your saved key and network connection.",
    "errors.automaticCheckFailed": "Automatic model check failed. Use Refresh models to retry.",
    "errors.automaticChecksType": "Use true or false for automatic model checks.",
    "errors.browserOwnerMissing": "The executing prompt has no browser owner.",
    "errors.cameraCommandLimit": "Camera input exceeded its pending command limit.",
    "errors.cameraCommandTimeout": "A live camera command was not acknowledged in time. The session is ending.",
    "errors.cameraDimensions": "Send a JPEG no larger than 640 by 480 pixels.",
    "errors.cameraDirection": "Choose a listed camera direction.",
    "errors.cameraFrameOrder": "The camera frame is out of order or the session ended.",
    "errors.cameraFrameSize": "Send a camera JPEG smaller than 300 KB.",
    "errors.cameraFrameWait": "Wait for the previous camera frame.",
    "errors.cameraInputStale": "Camera input became stale before it could be sent.",
    "errors.cameraInputStopped": "Camera input stopped. The session is ending.",
    "errors.cameraJpegRequired": "Send a camera JPEG.",
    "errors.cameraStateRequired": "Send a complete listed camera state.",
    "errors.captureDisconnected": "The Reactor connection ended before capture finished.",
    "errors.captureLimit": "Choose a capture within the host limit.",
    "errors.captureQueueFull": "The video capture queue is full. Shorten the capture.",
    "errors.captureStopped": "Video capture was stopped.",
    "errors.cleanupRestartRequired": "The remote session ended, but local cleanup failed. Restart ComfyUI.",
    "errors.cleanupUnconfirmed": "Session cleanup failed; termination is unconfirmed. The server lifetime cap applies.",
    "errors.clearKeyBody": "Do not include a body when clearing a saved key.",
    "errors.clipCaptureLimit": "The accepted clip length exceeds the host capture limit. Choose a shorter clip.",
    "errors.clipCount": "Choose 2 to 8 clips.",
    "errors.clipDurationRange": "The requested length is outside this deployment's clip limits.",
    "errors.clipDurationUnsupported": "This deployment does not support the requested clip length.",
    "errors.clipIdentifier": "Fast H3 returned an invalid clip ID.",
    "errors.clipLength": "Fast H3 returned an invalid clip length.",
    "errors.clipLengthChanged": "Fast H3 changed the accepted clip length before playback.",
    "errors.clipMediaTime": "Fast H3 returned an invalid media time.",
    "errors.clipMissing": "Fast H3 did not return a clip.",
    "errors.clipPlaybackOrder": "Fast H3 started playback before the clip was selected.",
    "errors.clipReply": "Fast H3 returned an unexpected reply.",
    "errors.clipUnfinished": "Fast H3 did not finish the queued clip.",
    "errors.clipWindowMissing": "Fast H3 did not report a precise clip window. No partial clip will be saved.",
    "errors.clipsUnexpected": "Fast H3 returned unexpected clips.",
    "errors.commandRejected": "Reactor rejected a model command. Check this node's inputs and model guide.",
    "errors.continuationLength": "Fast H3 returned an invalid continuation length.",
    "errors.continuationPrompts": "Use at most 800 characters per prompt and one later prompt per remaining clip.",
    "errors.continuedClipDuration": "Choose 5.167 to 14.375 seconds per clip.",
    "errors.encoderMetadata": "The video encoder returned invalid metadata.",
    "errors.encoderNotReady": "The video encoder did not become ready.",
    "errors.encoderPipes": "The video encoder pipes are unavailable.",
    "errors.encoderResult": "The video encoder returned no valid result.",
    "errors.encoderStopFailed": "The encoder process did not stop. Restart ComfyUI before another run.",
    "errors.endingImageUploadLimit": "Provide an ending image within the upload limit.",
    "errors.fastAspectRatio": "Choose an offered Fast H3 aspect ratio.",
    "errors.fastAudioMissing": "This Fast H3 deployment has no audio track.",
    "errors.fastDuration": "Choose 5.167 to 14.375 seconds for Fast H3.",
    "errors.fastPromptLength": "Use at most 800 prompt characters.",
    "errors.guideListIncomplete": "The guide list may be incomplete. The previous list is unchanged.",
    "errors.imageDimensions": "Use an image no larger than 8192 pixels per side.",
    "errors.imagePixels": "The image contains non-finite pixel values.",
    "errors.imageUploadLimit": "Provide image bytes within the upload limit.",
    "errors.jsonDepth": "The JSON input is nested too deeply.",
    "errors.jsonDuplicateKey": "Duplicate JSON key.",
    "errors.jsonObject": "Expected a JSON object.",
    "errors.jsonSize": "The JSON input exceeds its size limit.",
    "errors.jsonSyntax": "Enter valid JSON with unique keys.",
    "errors.jsonValues": "Use finite numbers and ordinary JSON values.",
    "errors.keyEmpty": "Enter a nonempty API key without spaces.",
    "errors.keyRequired": "Set your Reactor API key in Reactor settings or the server environment before running.",
    "errors.keyUnreadable": "Cannot read the saved Reactor key. Check its private file.",
    "errors.keyWhitespace": "The API key cannot contain whitespace.",
    "errors.laterPromptLength": "Enter a later prompt of 1 to 20,000 characters.",
    "errors.lateralDirection": "Choose a listed lateral direction.",
    "errors.liveActionValues": "Choose a supported live action and valid values.",
    "errors.liveActionWait": "Wait for the previous live action.",
    "errors.liveCameraUnsupported": "This model has no live camera adapter.",
    "errors.liveCancelled": "The live run was cancelled.",
    "errors.liveCaptureCancelled": "The live capture was cancelled.",
    "errors.liveCommandUnfinished": "A live command did not finish. The session is ending.",
    "errors.liveControlType": "Choose whether live controls are enabled.",
    "errors.liveHostRequirements": "Live controls need a local, single-user ComfyUI browser.",
    "errors.liveInputOrder": "The live input is out of order.",
    "errors.livePanelClosed": "The live panel was closed.",
    "errors.livePanelEnded": "The live panel ended or disconnected. The capture has been stopped.",
    "errors.livePanelLimit": "Too many live panels are still open.",
    "errors.livePreviewEncoding": "The live preview could not be encoded. The session is ending.",
    "errors.liveSessionUnavailable": "This live session is no longer available.",
    "errors.localCleanupFailed": "The remote session ended, but local cleanup failed.",
    "errors.localConnectionRequired": "Reactor configuration requires a local, same-origin ComfyUI connection.",
    "errors.localSourceRequired": "Connect one local SDR clip from Load Video or Create Video within the input limits.",
    "errors.longliveImagesUnsupported": "LongLive accepts shot prompts, not images.",
    "errors.ltxAudioMissing": "This LTX deployment has no audio track.",
    "errors.ltxDuration": "Use at least four seconds for LTX.",
    "errors.ltxSceneLength": "Use at most 800 scene characters.",
    "errors.modelAuthorization": "Reactor could not authorize this model. Check your key and model access before retrying.",
    "errors.modelListChanged": "The model list changed. Reload the list and retry.",
    "errors.modelListFormat": "The model model list has an invalid or unsupported format.",
    "errors.modelListGrowth": "The model list grew unexpectedly. Review the source before updating.",
    "errors.modelListHistoryEmpty": "There is no earlier model list to restore.",
    "errors.modelRefreshRunning": "A model list refresh is already running.",
    "errors.modelRefreshWait": "Wait for the model list refresh to finish.",
    "errors.modelRevisionRequired": "Send the model list revision shown in this tab.",
    "errors.modelUnavailable": "The requested Reactor model or protocol is unavailable. Check for updates.",
    "errors.modelsHttp": "Reactor's model list returned HTTP {status}. Try again later.",
    "errors.modelsUnreadable": "Cannot read Reactor's public model list. The previous list is unchanged.",
    "errors.nodeUnregistered": "The Reactor node is not registered.",
    "errors.outputClosed": "The recording output is closed.",
    "errors.outputSize": "The recording exceeds the output size limit.",
    "errors.packageIdentityInvalid": "The package identity is invalid. Reinstall the package.",
    "errors.packageIdentityUnreadable": "The package identity could not be read. Reinstall it.",
    "errors.packageVersionMissing": "The connector's version is missing. Reinstall the package.",
    "errors.phase": "{message} Stage: {phase}. Code: {code}.",
    "errors.pointerCoordinates": "Choose pointer coordinates from 0 to 1.",
    "errors.pointerOptionType": "Use boolean backlog and pointer values.",
    "errors.portraitRequired": "Provide one portrait.",
    "errors.portraitUploadLimit": "Provide one portrait within the upload limit.",
    "errors.priceListIncomplete": "The pricing list may be incomplete. The previous list is unchanged.",
    "errors.privateStateLocation": "Keep Reactor's private state outside ComfyUI, its package, and its media folders.",
    "errors.promptChunk": "Choose a later prompt's chunk from 1 to 100,000.",
    "errors.promptLength": "Enter a prompt of 1 to 20,000 characters.",
    "errors.promptSequenceOrder": "Use at most 32 later prompts with distinct, increasing chunk numbers.",
    "errors.promptSequenceSize": "Keep the prompt sequence within 128 KB.",
    "errors.providerRateLimit": "Reactor is limiting requests. Wait before starting another run.",
    "errors.providerRequestTimeout": "Reactor did not reply within its request limit.",
    "errors.queueTimeout": "Timed out waiting for another Reactor run to finish. This waiting run did not open a session.",
    "errors.recordingDisconnected": "The recording session is not connected.",
    "errors.recordingMetadata": "The recording returned invalid media metadata.",
    "errors.recordingNotReady": "The recording was not ready within the capture time limit.",
    "errors.recordingReadiness": "The recording returned invalid readiness timing.",
    "errors.recordingTiming": "The recording returned invalid timing markers.",
    "errors.recordingUnsupported": "Reactor returned an unsupported recording. No partial video was saved.",
    "errors.refreshBody": "Do not send a body when refreshing public models.",
    "errors.requestEncoding": "Send valid UTF-8 JSON.",
    "errors.requestJsonRequired": "Send a JSON request.",
    "errors.requestTimeout": "The configuration request took too long.",
    "errors.reservationReused": "Create a new reservation for each session.",
    "errors.resolutionName": "Use a short model resolution name.",
    "errors.resolutionUnavailable": "This model does not offer that resolution. Leave it blank for the default.",
    "errors.rotationSpeed": "Choose a rotation speed from 0 to 30.",
    "errors.runFailed": "Reactor could not complete this run. Check your connection and account status.",
    "errors.runTimeout": "Reactor did not finish within the configured time limit.",
    "errors.runtimeNotReady": "Reactor has not finished loading. Restart ComfyUI.",
    "errors.sanaPromptLength": "Use at most 20,000 prompt characters.",
    "errors.sanaUnsupported": "This SANA version is not supported. Update the connector.",
    "errors.sanaWebcamUnsupported": "This SANA deployment does not accept webcam input.",
    "errors.savedKeyLink": "A saved key cannot be a symbolic link.",
    "errors.savedVideoDetails": "The saved video returned invalid details.",
    "errors.savedVideoTimeout": "Reading the saved video's details took too long.",
    "errors.seedRange": "Choose a seed from 0 to 4,294,967,295.",
    "errors.sequenceCaptureLimit": "The sequence exceeded the video duration limit. Choose fewer clips or a longer limit.",
    "errors.sequencePlaybackOrder": "Fast H3 started playback before the sequence was ready.",
    "errors.sessionAlreadyConnected": "This Reactor session cannot be connected again.",
    "errors.sessionCapacity": "Choose a session capacity from 1 to 4.",
    "errors.sessionDeadline": "The session deadline expired during this operation.",
    "errors.sessionDisconnected": "The Reactor session is not connected.",
    "errors.sessionInOtherProcess": "Another ComfyUI process is using Reactor. Let its run finish before trying again.",
    "errors.sessionLimitTooShort": "The session limit must exceed the capture limit to allow setup and cleanup.",
    "errors.sessionLockLink": "The session lock cannot be a link.",
    "errors.sessionLockPermissions": "Restrict the session lock file to its owner.",
    "errors.sessionRecordDamaged": "The saved Reactor session record is damaged. Check Reactor Usage before repairing the session record in the connector's private settings folder.",
    "errors.sessionRecordPermissions": "The Reactor session record could not be updated. The saved wait still applies. Check access to the connector's private settings folder.",
    "errors.sessionRecordUnreadable": "The Reactor session record could not be read or saved. No session was started. Check access to the connector's private settings folder.",
    "errors.sessionRecordUpdateFailed": "The Reactor session record could not be updated. The saved wait still applies.",
    "errors.sessionTimeout": "Reactor exceeded the configured time limit.",
    "errors.sessionWait": "An earlier Reactor session may still be running. Wait {seconds} seconds before another run. Restarting ComfyUI does not clear this wait.",
    "errors.sessionWaitTime": "Use a positive session wait time.",
    "errors.settingReadOnly": "This setting cannot be changed here.",
    "errors.settingUnknown": "The settings contain an unknown option.",
    "errors.settingsChanged": "Settings changed. Reload them before saving.",
    "errors.settingsRange": "Choose a setting within the range shown in Reactor settings.",
    "errors.settingsRevisionRequired": "Send settings and their current revision.",
    "errors.settingsUnreadable": "Cannot load Reactor execution settings. Check the limits and private key.",
    "errors.settingsWholeNumbers": "Use whole numbers for Reactor limits and check intervals.",
    "errors.shotChunk": "Place a later shot at chunk 1 or above.",
    "errors.shotPrompt": "Enter a shot prompt of 1 to 20,000 characters.",
    "errors.shotTransition": "Choose a soft transition or a cut.",
    "errors.singleImageRequired": "Connect exactly one RGB image, not a batch.",
    "errors.singleKeyRequired": "Send one API key.",
    "errors.soundOptionType": "Use boolean sound and prompt options.",
    "errors.soundPromptLength": "Use at most 1,000 audio prompt characters.",
    "errors.sourceDimensions": "Use even video dimensions within the input limit.",
    "errors.sourceFrameCount": "Use a source video with at least 33 frames.",
    "errors.sourceFrameRate": "The prepared video has no valid frame rate.",
    "errors.sourceFramesLost": "The prepared source lost frames during encoding.",
    "errors.sourceFramesMissing": "The prepared input has no frames.",
    "errors.sourcePixels": "Source pixels must be finite numbers.",
    "errors.sourceReaderClosed": "The prepared video reader is closed.",
    "errors.sourceTimestampMissing": "The prepared video has no frame timestamp.",
    "errors.sourceVideoFormat": "Use an SDR RGB video at 1 to 120 frames per second.",
    "errors.sourceVideoRequired": "Connect a prepared source video.",
    "errors.speechLength": "Enter a script of 1 to 10,000 characters.",
    "errors.speechPace": "Use a positive whole-number speech pace.",
    "errors.speechPaceMissing": "LTX did not report its accepted speech pace.",
    "errors.speechPaceRange": "Use a speech pace from {minimum} to {maximum}.",
    "errors.startingImageRequired": "Connect one starting image.",
    "errors.stateDirectoryAbsolute": "Use an absolute state directory path.",
    "errors.stateDirectoryLink": "The state directory cannot be a symbolic link.",
    "errors.stateDirectoryPermissions": "Restrict the state directory to its owner.",
    "errors.stateFileChanged": "The private state file changed while opening.",
    "errors.stateFileLink": "A state file cannot be a symbolic link.",
    "errors.stateFilePermissions": "Restrict the state file to its owner.",
    "errors.stateFileSize": "The state file exceeds its size limit.",
    "errors.stateFileType": "The requested state file is not a regular file.",
    "errors.stateUnreadable": "Cannot read connector state. Check its location and permissions.",
    "errors.storyboardOrder": "Use a storyboard of at most 32 shots with distinct, increasing chunk numbers.",
    "errors.storyboardSize": "Keep the storyboard within 128 KB.",
    "errors.terminationUnconfirmed": "Session termination is unconfirmed. Wait for its server limit before retrying.",
    "errors.terminationWait": "An earlier Reactor session has unconfirmed termination. Wait {seconds} seconds before starting another run.",
    "errors.videoArrivalRate": "Video arrived faster than it could be saved. Shorten the capture.",
    "errors.videoEncodingFailed": "Video encoding failed. Check disk space and media support.",
    "errors.videoFrameColor": "The video track must provide RGB frames.",
    "errors.videoFrameType": "The video track returned an unsupported frame.",
    "errors.videoTimestamp": "The video track returned an invalid timestamp.",
    "errors.videoTrackMissing": "The model did not declare its expected video track.",
    "errors.viskoAudioMissing": "This Visko deployment has no audio track.",
    "errors.viskoImageChanged": "Visko started with different image settings. The run was stopped.",
    "errors.viskoResolutionChanged": "Visko started at a different resolution. The run was stopped.",
    "errors.viskoSoundChanged": "Visko started with different sound settings. The run was stopped.",
    "errors.workerArguments": "Invalid worker arguments.",
    "errors.workerLimits": "Worker limits must be positive.",
    "errors.worldPromptLength": "Use a prompt of at most 1,000 characters.",
    "errors.x2PromptLength": "Use at most 1,000 prompt characters.",
    "errors.x2Unsupported": "This X2 version is not supported. Update the connector.",
    "help.close": "Close node help",
    "help.guide": "Reactor node guide",
    "help.liveControls": "Live controls",
    "help.navigation": "Reactor guides",
    "help.newTab": " (opens in a new tab)",
    "help.project": "ComfyUI Reactor Connector",
    "help.title": "Node help",
    "help.workflows": "Workflows",
    "live.actionRejected": "The live action was not accepted. The session is ending.",
    "live.applyPrompt": "Apply prompt",
    "live.back": "Back",
    "live.cameraTitle": "Reactor live camera",
    "live.connectingPanel": "Connecting the live panel…",
    "live.connectionLost": "The live connection was lost. The connector will ask Reactor to stop after five seconds without a browser connection. Check Reactor Usage to confirm the session has ended before another run.",
    "live.discarded": "The session ended without saving a video. Close this panel to view the workflow result.",
    "live.duration": "{model} · {seconds} seconds of video",
    "live.elapsed": "Time spent on setup and recording: {seconds} seconds.",
    "live.emptyScenePrompt": "Enter a scene prompt before applying it.",
    "live.endSession": "End session",
    "live.ended": "Session ended. Close this panel to view the workflow result.",
    "live.ending": "Ending the session…",
    "live.forward": "Forward",
    "live.invalidStatus": "The live panel received an invalid status.",
    "live.lookDown": "Look down",
    "live.lookLeft": "Look left",
    "live.lookRight": "Look right",
    "live.lookUp": "Look up",
    "live.moveLeft": "Move left",
    "live.moveRight": "Move right",
    "live.movementInstructions": "Click the picture, then use W A S D to move and arrow keys to turn. Click a button for a brief movement, or hold it to keep moving. Escape stops camera movement.",
    "live.movementLabel": "Live view. W A S D moves. Arrow keys turn. Escape stops camera movement.",
    "live.output": "Live model output",
    "live.previewReady": "Live preview. Controls are active.",
    "live.promptNotice": "Prompt changes affect later frames. The starting image stays fixed.",
    "live.promptSent": "Prompt sent. Watch the video for the change.",
    "live.recordingNotice": "The preview has fewer frames per second than the saved video and has no sound. Save Video saves the finished recording. Ending early discards the unfinished video.",
    "live.scenePrompt": "Scene prompt",
    "live.unconfirmedEnd": "Reactor has not confirmed that the session ended. Wait for its time limit before another run.",
    "live.unreachable": "Live controls could not reach their session.",
    "live.waitingVideo": "Waiting for model video…",
    "models.checkDue": "An automatic model check is due. Checks do not change this list.",
    "models.checkRunning": "An automatic model check is running. Reopen this list to see its result.",
    "models.checkSchedule": "Automatic check: {date}. Checks run every {hours} hours.",
    "models.checking": "Checking public model sources…",
    "models.checksOff": "Automatic model checks are off. Change this in Reactor settings.",
    "models.close": "Close Reactor models",
    "models.connectName": "Model ID: {name}",
    "models.count": "{visible} of {total} models",
    "models.guideUnavailable": "No matching public guide was found.",
    "models.installedList": "Showing installed nodes. Refresh models to load public prices and guides.",
    "models.invalidResponse": "ComfyUI returned an invalid Reactor model list.",
    "models.lastRefresh": "Public prices and guides checked {date}.",
    "models.listChanged": "The model list has changed. Select Refresh models to update your list.",
    "models.loadFailed": "Cannot load models.",
    "models.loaded": "Local model list loaded.",
    "models.loading": "Loading model list…",
    "models.loadingLocal": "Loading the local model list…",
    "models.nodeUnavailable": "No connector node available.",
    "models.nodesAvailable": "Nodes available.",
    "models.openGuide": "Reactor model guide (opens in a new tab)",
    "models.refresh": "Refresh models",
    "models.refreshNotice": "Refresh updates public prices and model information. New models need support in the connector.",
    "models.refreshed": "Model list refreshed.",
    "models.requestFailed": "The model list request failed.",
    "models.restore": "Restore previous list",
    "models.restored": "Previous model list restored. This does not change which models Reactor offers.",
    "models.search": "Search models",
    "models.searchPlaceholder": "Model name or ID",
    "models.showAll": "Show all models",
    "models.sources": "Model sources and automatic checks",
    "models.title": "Reactor models",
    "models.unreachable": "Cannot reach the Reactor model list. Check ComfyUI and try again.",
    "nodes.seedBehavior": "Seed behavior",
    "pointer.held": "Pointer held.",
    "pointer.instructions": "Drag on the output to move the subject. Use arrow keys to position the pointer, Space to hold it, and Escape to release it.",
    "pointer.position": " {x}% across, {y}% down.",
    "pointer.released": "Pointer released.",
    "pointer.stopped": "Pointer controls stopped.",
    "pricing.calculate": "Calculate credits for session time",
    "pricing.calculation": "{seconds} session seconds × {rate} credits per second = {credits} credits.",
    "pricing.enterTime": "Enter session time",
    "pricing.estimateNotice": "Estimate = rate × session time. Session time includes setup and recording.",
    "pricing.loadFailed": "Cannot load the credit rate.",
    "pricing.loading": "Loading the local credit rate…",
    "pricing.modelUnavailable": "No rate is listed for this node. Open the ComfyUI menu, then Extensions → Reactor → Reactor models, and refresh the list.",
    "pricing.rate": "{rate} credits per session second.",
    "pricing.rateOutdated": "This rate was not found in the latest source check. Refresh Reactor models before relying on a calculation.",
    "pricing.rateUnavailable": "A current rate is not available. Refresh Reactor models to check for a rate.",
    "pricing.requestedDuration": "Requested video length: {seconds} seconds.",
    "pricing.sessionTime": "Session time to calculate (seconds)",
    "pricing.timeRange": "Enter a session time from 0.1 to {maximum} seconds.",
    "pricing.title": "Credit rate",
    "pricing.totalTimeNotice": "Use total session time, including setup and recording.",
    "pricing.unknownDuration": "The video length comes from a connected input or is not available. Enter a session time below to calculate credits.",
    "pricing.viewRate": "View credit rate",
    "settings.advancedLimits": "Advanced limits",
    "settings.automaticChecks": "Check for model updates automatically",
    "settings.checkInterval": "Check interval (hours)",
    "settings.checkNotice": "Checks read public prices and model guides. Open Reactor models to see changes and refresh your list.",
    "settings.checksSaved": "Model check settings saved. Changes take effect within one minute.",
    "settings.clearKey": "Clear saved key",
    "settings.close": "Close Reactor settings",
    "settings.credentialLabel": "Reactor API key",
    "settings.credentials": "Credentials",
    "settings.environmentKey": "The server's REACTOR_API_KEY environment variable is active.",
    "settings.incompleteResponse": "ComfyUI returned incomplete Reactor settings.",
    "settings.invalidChecks": "ComfyUI returned invalid model check settings.",
    "settings.invalidDefinition": "ComfyUI returned an invalid Reactor setting definition.",
    "settings.invalidLimit": "ComfyUI returned an invalid Reactor limit.",
    "settings.invalidResponse": "ComfyUI returned an invalid Reactor settings response.",
    "settings.keyCleared": "Saved key cleared. Any environment key remains active.",
    "settings.keyNotice": "The saved key stays on the ComfyUI server. An environment key takes precedence. Keys are not checked with Reactor here.",
    "settings.keySaved": "Key saved on this server. Reactor checks it when you start a session.",
    "settings.limit.catalog_interval_hours": "Check interval (hours)",
    "settings.limit.cleanup_timeout_seconds": "Disconnect timeout (seconds)",
    "settings.limit.connect_timeout_seconds": "Connection timeout (seconds)",
    "settings.limit.first_frame_timeout_seconds": "First-frame timeout (seconds)",
    "settings.limit.max_capture_megabytes": "Maximum video file size (MiB)",
    "settings.limit.max_capture_seconds": "Maximum video duration (seconds)",
    "settings.limit.max_queue_megabytes": "Maximum queued frame data (MiB)",
    "settings.limit.max_session_seconds": "Maximum session duration (seconds)",
    "settings.limit.max_upload_megabytes": "Maximum upload size (MiB)",
    "settings.limit.queue_timeout_seconds": "Queue wait timeout (seconds)",
    "settings.limits": "Execution limits",
    "settings.limitsSaved": "Limits saved. They apply to new executions.",
    "settings.loaded": "Local settings loaded.",
    "settings.loading": "Loading local settings…",
    "settings.missingKey": "No Reactor key is configured.",
    "settings.modelUpdates": "Model updates",
    "settings.noCheckChanges": "No model check changes to save.",
    "settings.noLimitChanges": "No limit changes to save.",
    "settings.readOnly": "Changes are disabled in this host's multi-user mode.",
    "settings.reload": "Reload settings",
    "settings.saveChecks": "Save model check settings",
    "settings.saveFailed": "ComfyUI could not save Reactor settings.",
    "settings.saveKey": "Save key",
    "settings.saveLimits": "Save limits",
    "settings.savedKey": "A saved key is configured on this server.",
    "settings.timeNotice": "Session time includes setup and generation.",
    "settings.title": "Reactor settings",
    "settings.unreachable": "Cannot reach Reactor settings. Check ComfyUI and try again.",
    "settings.unreadableResponse": "ComfyUI returned an unreadable Reactor settings response.",
    "settings.updateFailed": "Reactor settings could not be saved.",
    "sound.applyPrompt": "Apply sound prompt",
    "sound.prompt": "Sound prompt",
    "sound.promptNotice": "Describe the sound briefly. Leave blank to use the picture alone.",
    "sound.title": "Sound"
  }
};

// web/language.ts
var languageEvents = new EventTarget();
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
async function initializeLanguage() {
  try {
    const languages = await api.getCustomNodesI18n();
    const available = {};
    for (const [language, document2] of Object.entries(languages)) {
      available[language.toLowerCase()] = readLanguage(document2);
    }
    messages = available;
  } catch {
    messages = {};
  }
  app.ui.settings.addEventListener(
    "Comfy.Locale.change",
    () => languageEvents.dispatchEvent(new Event("change"))
  );
}
function translate(key, values = {}, fallback) {
  const languages = localeCandidates(selectedLocale());
  const defaults = main_default.reactorInc;
  const message2 = languages.map((language) => messages[language]?.[key]).find((value) => value !== void 0) ?? defaults[key] ?? fallback ?? key;
  return message2.replaceAll(
    /\{(\w+)\}/g,
    (placeholder, name) => Object.hasOwn(values, name) ? displayValue(values[name]) : placeholder
  );
}
function selectedLocale() {
  const value = app.extensionManager.setting.get("Comfy.Locale");
  try {
    return Intl.getCanonicalLocales(typeof value === "string" ? value.replaceAll("_", "-") : "en")[0] ?? "en";
  } catch {
    return "en";
  }
}
function localeCandidates(locale) {
  const exact = locale.replaceAll("_", "-").toLowerCase();
  const base = exact.split("-")[0] ?? "en";
  const chinese = ["zh-tw", "zh-hk", "zh-mo", "zh-hant"].some(
    (tag) => exact === tag || exact.startsWith(tag + "-")
  );
  return [.../* @__PURE__ */ new Set([exact, chinese ? "zh-tw" : base, "en"])];
}
function formatNumber(value, options) {
  return new Intl.NumberFormat(selectedLocale(), options).format(value);
}
function formatDate(value) {
  return new Date(value).toLocaleString(selectedLocale());
}
function displayValue(value) {
  if (typeof value === "function") return value();
  return typeof value === "number" ? formatNumber(value) : String(value);
}

// web/http.ts
function requestLocal(route, options) {
  const headers = new Headers(options.headers);
  headers.set("Accept-Language", selectedLocale());
  return api2.fetchApi(route, { ...options, headers });
}

// web/localization.ts
var bindings = /* @__PURE__ */ new Set();
var textBindings = /* @__PURE__ */ new WeakMap();
function message(key, values = {}, fallback) {
  return { key, values, ...fallback === void 0 ? {} : { fallback } };
}
function textNode(content) {
  const node = document.createTextNode(
    typeof content === "string" ? content : translate(content.key, content.values, content.fallback)
  );
  if (typeof content !== "string") {
    const binding = { target: new WeakRef(node), message: content, rendered: node.data };
    bindings.add(binding);
    textBindings.set(node, binding);
  }
  return node;
}
function setText(target, content) {
  for (const child of target.childNodes) {
    if (!(child instanceof Text)) continue;
    const previous = textBindings.get(child);
    if (previous) bindings.delete(previous);
  }
  target.replaceChildren();
  target.appendChild(textNode(content));
}
function setTextAttribute(target, attribute, content) {
  const rendered = translate(content.key, content.values, content.fallback);
  target.setAttribute(attribute, rendered);
  for (const binding of bindings) {
    if (binding.target.deref() === target && binding.attribute === attribute)
      bindings.delete(binding);
  }
  bindings.add({ target: new WeakRef(target), attribute, message: content, rendered });
}
function refreshText() {
  for (const binding of bindings) {
    const target = binding.target.deref();
    if (!target?.isConnected) {
      bindings.delete(binding);
      continue;
    }
    const current5 = bindingText(target, binding.attribute);
    if (current5 !== binding.rendered) {
      bindings.delete(binding);
      continue;
    }
    renderBinding(target, binding);
  }
}
function bindingText(target, attribute) {
  if (target instanceof Text) return target.data;
  return target instanceof Element && attribute ? target.getAttribute(attribute) : null;
}
function renderBinding(target, binding) {
  binding.rendered = translate(
    binding.message.key,
    binding.message.values,
    binding.message.fallback
  );
  if (target instanceof Text) target.data = binding.rendered;
  else if (target instanceof Element && binding.attribute)
    target.setAttribute(binding.attribute, binding.rendered);
}

// web/dom.ts
function element(tag, text) {
  const node = document.createElement(tag);
  if (text !== void 0) node.appendChild(textNode(text));
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
    durationSeconds: v.duration_seconds,
    axes: {},
    prompt: v.prompt,
    promptLimit: v.prompt_limit,
    webcam: v.webcam,
    pointer: v.pointer,
    sound: v.sound,
    audioPrompt: v.audio_prompt,
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
    durationSeconds: value.duration_seconds,
    axes,
    prompt: value.prompt,
    promptLimit: value.prompt_limit
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
    this.dialog.className = "reactor-dialog reactor-live";
    setTextAttribute(this.dialog, "aria-label", message("live.cameraTitle"));
    this.status.setAttribute("role", "status");
    this.promptStatus.setAttribute("role", "status");
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.promptLimit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.apply.disabled = true;
    this.surface.className = "reactor-preview";
    this.surface.tabIndex = 0;
    setTextAttribute(this.surface, "aria-label", message("live.movementLabel"));
    setTextAttribute(this.image, "alt", message("live.output"));
    this.image.hidden = true;
    this.surface.append(this.image);
    this.controls.className = "reactor-actions";
    const labels2 = [
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
      const control = button(labels2[index] ?? key);
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
  status = element("p", message("live.connectingPanel"));
  elapsed = element("p");
  prompt = element("textarea");
  apply = button(message("live.applyPrompt"));
  promptStatus = element("p", message("live.promptNotice"));
  surface = element("div");
  image = element("img");
  controls = element("div");
  end = button(message("live.endSession"));
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
    header.append(element("h2", message("live.cameraTitle")), this.end);
    const promptLabel = element("label", message("live.scenePrompt"));
    promptLabel.append(this.prompt);
    this.dialog.append(
      header,
      element(
        "p",
        message("live.duration", {
          model: this.owner.modelTitle,
          seconds: this.owner.durationSeconds
        })
      ),
      element("p", message("live.movementInstructions")),
      this.surface,
      this.controls,
      promptLabel,
      this.apply,
      this.promptStatus,
      this.status,
      this.elapsed,
      element("p", message("live.recordingNotice"))
    );
  }
  /** Bind prompt updates, explicit ending, and focus cleanup. */
  bindActions() {
    this.apply.addEventListener("click", () => {
      if (!this.prompt.value.trim()) {
        setText(this.promptStatus, message("live.emptyScenePrompt"));
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
    setText(this.status, message("live.ending"));
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
    setText(
      this.elapsed,
      message("live.elapsed", {
        seconds: Math.round(result.elapsed_seconds * 10) / 10
      })
    );
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
      setText(this.status, message("live.ending"));
    } else if (!this.ending) {
      setText(
        this.status,
        result.controls_ready && result.preview_sequence > 0 ? message("live.previewReady") : message("live.waitingVideo")
      );
    }
  }
  /**
   * Show the final session result without implying unconfirmed termination.
   * @param result - The terminal session status.
   */
  finish(result) {
    this.finished = true;
    if (!result.termination_confirmed) setText(this.status, message("live.unconfirmedEnd"));
    else setText(this.status, result.failed ? message("live.discarded") : message("live.ended"));
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
    setText(this.promptStatus, message("live.promptSent"));
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
      setText(this.status, message("live.connectionLost"));
    } finally {
      this.release();
      this.controller.abort();
      this.end.disabled = false;
      setText(this.end, message("close"));
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
    const label = element("label", message("camera.label"));
    label.append(this.select);
    const defaultCamera = element("option", message("camera.default"));
    defaultCamera.value = "";
    this.select.append(defaultCamera);
    this.video.muted = true;
    this.video.autoplay = true;
    this.video.playsInline = true;
    this.video.hidden = true;
    setTextAttribute(this.video, "aria-label", message("camera.preview"));
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
  enable = button(message("camera.enable"));
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
      setText(this.enable, message("camera.select"));
      setText(this.status, message("camera.enabled"));
    } catch (error) {
      this.stopCamera();
      if (this.closed) return;
      const errors = {
        NotAllowedError: "camera.permissionDenied",
        SecurityError: "camera.browserRequirements",
        NotFoundError: "camera.notFound",
        NotReadableError: "camera.busy",
        OverconstrainedError: "camera.unavailableSelection"
      };
      setText(
        this.status,
        message(
          error instanceof Error ? errors[error.name] ?? "camera.accessFailed" : "camera.accessFailed"
        )
      );
    } finally {
      if (!this.closed) this.enable.disabled = false;
    }
  }
  /**
   * Open the selected camera and release any previous stream.
   * @returns Whether the camera is ready and the panel is still open.
   */
  async openCamera() {
    if (!navigator.mediaDevices?.getUserMedia) throw new DOMException("", "SecurityError");
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
      ...devices.filter((device) => device.kind === "videoinput").map((device, index) => {
        const option = element(
          "option",
          device.label || message("camera.number", { number: index + 1 })
        );
        option.value = device.deviceId;
        option.selected = device.deviceId === selected;
        return option;
      })
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
    setText(this.status, message("camera.disabled"));
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
  apply = button(message("sound.applyPrompt"));
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
    const label = element("label", message("sound.prompt"));
    label.append(this.prompt);
    this.view.append(
      element("legend", message("sound.title")),
      label,
      this.apply,
      element("p", message("sound.promptNotice"))
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
    setText(
      this.#position,
      message("pointer.position", {
        x: Math.round(pointer.x * 100),
        y: Math.round(pointer.y * 100)
      })
    );
    this.#place();
  }
  /**
   * Announce a hold or release after the server accepts it.
   * @param pointer - The pointer update accepted by the server.
   */
  confirm(pointer) {
    const key = pointer.active ? "pointer.held" : "pointer.released";
    if (this.#state.textContent !== translate(key)) setText(this.#state, message(key));
  }
  /**
   * Hide the marker and announce that pointer input has stopped.
   */
  stop() {
    this.#pointer = void 0;
    this.#marker.hidden = true;
    if (!this.status.hidden) setText(this.#state, message("pointer.stopped"));
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
    image.classList.add("reactor-drag-input");
    setTextAttribute(image, "aria-label", message("pointer.instructions"));
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
    this.dialog.className = "reactor-dialog reactor-controls";
    setTextAttribute(this.dialog, "aria-label", message("controls.title"));
    setTextAttribute(this.image, "alt", message("live.output"));
    this.image.hidden = true;
    this.pointerPreview = owner.pointer ? new PointerPreview(this.image, this.abort.signal) : void 0;
    this.status.setAttribute("role", "status");
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.promptLimit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.update.disabled = true;
    this.sound = owner.sound ? new SoundControls(owner.audioPrompt, owner.audioPromptLimit) : void 0;
    this.camera = owner.webcam ? new Webcam(owner, fetcher, (message2) => this.stop(message2)) : void 0;
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
  status = element("p", message("controls.chooseInput"));
  prompt = element("textarea");
  start = button(message("controls.start"));
  update = button(message("live.applyPrompt"));
  end = button(message("cancel"));
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
      element("h2", message("controls.title")),
      element(
        "p",
        message("live.duration", {
          model: this.owner.modelTitle,
          seconds: this.owner.durationSeconds
        })
      ),
      element("p", message("controls.recordingNotice"))
    );
    if (this.camera) this.dialog.append(this.camera.view);
    this.dialog.append(this.pointerPreview?.view ?? this.image);
    if (this.owner.pointer) this.dialog.append(element("p", message("controls.dragInstructions")));
    if (this.pointerPreview) this.dialog.append(this.pointerPreview.status);
    const label = element("label", message("live.scenePrompt"));
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
        setText(this.status, message("controls.emptyPrompt"));
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
  stop(message2 = translate("live.ending")) {
    this.ending = true;
    this.ready = false;
    this.start.disabled = this.update.disabled = true;
    this.sound?.setReady(false);
    this.pointerPreview?.stop();
    this.status.textContent = message2;
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
    if (this.ready && !wasReady) setText(this.status, message("controls.recording"));
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
    if (!reply.termination_confirmed) setText(this.status, message("controls.connectionClosed"));
    else if (!this.startAttempted) setText(this.status, message("controls.recordingNotStarted"));
    else setText(this.status, reply.failed ? message("live.discarded") : message("live.ended"));
    setText(this.end, message("close"));
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
      setText(this.end, message("live.endSession"));
      setText(this.status, message("controls.connecting"));
    } else {
      setText(this.status, message("controls.cameraRequired"));
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
      setText(this.status, message("controls.promptSent"));
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
      setText(this.status, message("controls.soundSent"));
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
      setText(this.status, message("live.ending"));
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
      setText(this.end, message("close"));
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
  if (rate === null) return [message("pricing.rateUnavailable")];
  const details = [message("pricing.rate", { rate })];
  if (!model2.observed) {
    details.push(message("pricing.rateOutdated"));
  } else if (seconds !== void 0) {
    const credits = () => formatNumber(rate * seconds, {
      maximumFractionDigits: 2
    });
    details.push(
      message("pricing.calculation", {
        seconds,
        rate,
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
  const support = model2.support === "available" ? message("models.nodesAvailable") : message("models.nodeUnavailable");
  row.append(element("p", support));
  if (model2.connect_name)
    row.append(element("p", message("models.connectName", { name: model2.connect_name })));
  for (const detail of formatCreditSummary(model2, seconds)) row.append(element("p", detail));
  if (model2.documentation_url) {
    const link = element("a", message("models.openGuide"));
    link.href = model2.documentation_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    row.append(link);
  } else row.append(element("p", message("models.guideUnavailable")));
  return row;
}

// web/discovery/api.ts
function record(value) {
  if (!value || typeof value !== "object" || Array.isArray(value))
    throw new Error(translate("models.invalidResponse"));
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
    throw new Error(translate("models.invalidResponse"));
  return row;
}
function parseCatalog(value) {
  const document2 = record(value);
  if (typeof document2.revision !== "string" || !browserPatterns.revision.test(document2.revision) || !(document2.retrieved_at === null || shortText(document2.retrieved_at, 40) && Number.isFinite(Date.parse(document2.retrieved_at))) || typeof document2.can_rollback !== "boolean" || typeof document2.mutation_allowed !== "boolean" || !Array.isArray(document2.models) || document2.models.length < 1 || document2.models.length > 1024)
    throw new Error(translate("models.invalidResponse"));
  const models = document2.models.map(model);
  if (document2.automatic_check !== void 0) {
    const check = record(document2.automatic_check);
    if (typeof check.enabled !== "boolean" || typeof check.running !== "boolean" || typeof check.interval_hours !== "number" || !Number.isSafeInteger(check.interval_hours) || check.interval_hours < 1 || !(check.checked_at === null || shortText(check.checked_at, 40) && Number.isFinite(Date.parse(check.checked_at))) || !(check.update_available === null || typeof check.update_available === "boolean") || !(check.error === null || shortText(check.error, 1024)))
      throw new Error(translate("models.invalidResponse"));
  }
  if (new Set(models.map((row) => row.key)).size !== models.length)
    throw new Error(translate("models.invalidResponse"));
  return { ...document2, models };
}
function metadataStatus(retrievedAt) {
  return retrievedAt === null ? message("models.installedList") : message("models.lastRefresh", { date: () => formatDate(retrievedAt) });
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
    throw new Error(translate("models.invalidResponse"));
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
  if (!check.enabled) return message("models.checksOff");
  if (check.running) return message("models.checkRunning");
  if (check.error) return check.error;
  if (check.update_available === true) return message("models.listChanged");
  if (check.checked_at)
    return message("models.checkSchedule", {
      date: () => formatDate(check.checked_at ?? ""),
      hours: check.interval_hours
    });
  return message("models.checkDue");
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
    this.dialog.className = "reactor-dialog reactor-catalog";
    this.dialog.setAttribute("aria-labelledby", "reactor-catalog-title");
    const heading = element("h2", message("models.title"));
    heading.id = "reactor-catalog-title";
    const close = button(message("close"));
    setTextAttribute(close, "aria-label", message("models.close"));
    close.addEventListener("click", () => this.dialog.close());
    const header = element("header");
    header.append(heading, close);
    const searchLabel = element("label", message("models.search"));
    this.search.type = "search";
    setTextAttribute(this.search, "placeholder", message("models.searchPlaceholder"));
    searchLabel.append(this.search);
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    setTextAttribute(this.list, "aria-label", message("models.title"));
    const sources = element("details");
    sources.append(element("summary", message("models.sources")), this.checked, this.automatic);
    this.dialog.append(
      header,
      element("p", message("models.refreshNotice")),
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
  refresh = button(message("models.refresh"));
  rollback = button(message("models.restore"));
  status = element("p", message("models.loadingLocal"));
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
    const showAll = button(message("models.showAll"));
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
    const label = element("label", message("pricing.sessionTime"));
    this.duration.type = "number";
    this.duration.min = "0.1";
    this.duration.max = String(browserLimits.maxCalculatorSeconds);
    this.duration.step = "any";
    setTextAttribute(this.duration, "placeholder", message("pricing.enterTime"));
    label.append(this.duration);
    const calculation = element("details");
    calculation.append(
      element("summary", message("pricing.calculate")),
      label,
      element("p", message("pricing.totalTimeNotice"))
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
    setText(
      this.count,
      message("models.count", {
        visible: visible.length,
        total: this.catalog?.models.length ?? 0
      })
    );
  }
  /**
   * Read or update the locally stored model list.
   * @param action - Read, refresh from public sources, or restore the previous list.
   * @returns When the model list or error is displayed.
   */
  async updateModels(action2) {
    this.refresh.disabled = this.rollback.disabled = true;
    setText(
      this.status,
      action2 === "refresh" ? message("models.checking") : message("models.loading")
    );
    try {
      const next = await requestModels(
        this.fetcher,
        this.controller.signal,
        action2,
        this.catalog?.revision
      );
      if (this.controller.signal.aborted) return;
      this.catalog = next;
      setText(this.checked, metadataStatus(next.retrieved_at));
      setText(this.automatic, automaticStatus(next.automatic_check));
      setText(
        this.status,
        {
          refresh: message("models.refreshed"),
          rollback: message("models.restored"),
          read: message("models.loaded")
        }[action2]
      );
      this.render();
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(this.status, error instanceof Error ? error.message : message("models.loadFailed"));
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
    this.dialog.className = "reactor-dialog";
    this.dialog.setAttribute("aria-labelledby", "reactor-settings-title");
    const heading = element("h2", message("settings.title"));
    heading.id = "reactor-settings-title";
    const close = button(message("close"));
    setTextAttribute(close, "aria-label", message("settings.close"));
    close.addEventListener("click", () => this.dialog.close());
    const header = element("header");
    header.append(heading, close);
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.reload.addEventListener(
      "click",
      () => void this.updateSettings(message("settings.loaded"))
    );
    this.dialog.append(
      header,
      this.source,
      this.credentials(),
      element("p", message("settings.keyNotice")),
      this.limits(),
      element("p", message("settings.timeNotice")),
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
  status = element("p", message("settings.loading"));
  source = element("p");
  reload = button(message("settings.reload"));
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
    const label = element("label", message("settings.credentialLabel"));
    this.key.type = "password";
    this.key.autocomplete = "off";
    this.key.spellcheck = false;
    this.key.required = true;
    label.append(this.key);
    const clear = button(message("settings.clearKey"));
    clear.addEventListener("click", () => {
      this.key.value = "";
      void this.updateSettings(message("settings.keyCleared"), "/credential", "DELETE");
    });
    const actions = element("div");
    actions.className = "reactor-actions";
    actions.append(button(message("settings.saveKey"), "submit"), clear);
    this.keyFields.append(element("legend", message("settings.credentials")), label, actions);
    form.append(this.keyFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const value = this.key.value;
      this.key.value = "";
      void this.updateSettings(message("settings.keySaved"), "/credential", "PUT", {
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
    this.limitFields.append(element("legend", message("settings.limits")));
    this.limitFields.append(button(message("settings.saveLimits"), "submit"));
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
    this.limitFields.replaceChildren(element("legend", message("settings.limits")));
    const advanced = element("details");
    advanced.append(element("summary", message("settings.advancedLimits")));
    for (const [index, [name, definition]] of Object.entries(configuration.definitions).filter(([name2]) => name2 !== "catalog_interval_hours").entries()) {
      const label = element(
        "label",
        message(`settings.limit.${name}`, {}, definition.label)
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
    this.limitFields.append(advanced, button(message("settings.saveLimits"), "submit"));
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
      setText(this.status, message("settings.noLimitChanges"));
      return;
    }
    void this.updateSettings(message("settings.limitsSaved"), "/settings", "PATCH", {
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
    const automaticLabel = element("label", message("settings.automaticChecks"));
    this.automatic.type = "checkbox";
    automaticLabel.prepend(this.automatic);
    const intervalLabel = element("label", message("settings.checkInterval"));
    this.interval.type = "number";
    this.interval.step = "1";
    this.interval.required = true;
    intervalLabel.append(this.interval);
    this.catalogFields.append(
      element("legend", message("settings.modelUpdates")),
      automaticLabel,
      intervalLabel,
      element("p", message("settings.checkNotice")),
      button(message("settings.saveChecks"), "submit")
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
      setText(this.status, message("settings.noCheckChanges"));
      return;
    }
    void this.updateSettings(message("settings.checksSaved"), "/settings", "PATCH", {
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
    setText(
      this.source,
      {
        missing: message("settings.missingKey"),
        saved: message("settings.savedKey"),
        environment: message("settings.environmentKey")
      }[configuration.credentialSource]
    );
    this.automatic.checked = configuration.settings.catalog_auto_check;
    this.interval.value = String(configuration.settings.catalog_interval_hours);
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const input = this.inputs.get(name);
      if (!input) continue;
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.value = String(configuration.settings[name]);
    }
    if (!configuration.mutationAllowed) setText(this.status, message("settings.readOnly"));
  }
  /**
   * Keep settings requests serial and show the server's response.
   * @param success - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @returns When the response or error is displayed.
   */
  async updateSettings(success, route, method, body) {
    this.keyFields.disabled = this.limitFields.disabled = this.catalogFields.disabled = true;
    this.reload.disabled = true;
    setText(this.status, message("working"));
    try {
      const value = await requestConfiguration(
        this.fetcher,
        this.controller.signal,
        route,
        method,
        body
      );
      if (this.controller.signal.aborted) return;
      setText(this.status, success);
      this.display(value);
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(
          this.status,
          error instanceof Error ? error.message : message("settings.updateFailed")
        );
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
    void this.updateSettings(message("settings.loaded"));
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

// web/nodes/labels.ts
function configureNodeWidgets(node) {
  if (!node.comfyClass?.startsWith("ReactorInc")) return;
  const control = node.widgets?.find((widget) => widget.name === "control_after_generate");
  if (control) bindWidgetLabel(node, control, "nodes.seedBehavior");
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
var labels = /* @__PURE__ */ new Map();
function bindWidgetLabel(node, widget, key) {
  widget.label = translate(key);
  for (const [reference] of labels) {
    if (!reference.deref()) labels.delete(reference);
    else if (reference.deref() === widget) return;
  }
  labels.set(new WeakRef(widget), { node: new WeakRef(node), key });
}
function refreshWidgetLabels() {
  for (const [reference, binding] of labels) {
    const widget = reference.deref();
    const node = binding.node.deref();
    if (!widget || !node?.graph) {
      labels.delete(reference);
      continue;
    }
    widget.label = translate(binding.key);
    node.graph.setDirtyCanvas(true);
  }
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
    this.dialog.className = "reactor-dialog";
    this.dialog.setAttribute("aria-labelledby", "reactor-rate-title");
    const title = element("h2", message("pricing.title"));
    title.id = "reactor-rate-title";
    const close = button(message("close"));
    close.addEventListener("click", () => this.dialog.close());
    const header = element("header");
    header.append(title, close);
    const seconds = requestedSeconds(node);
    const request = element(
      "p",
      seconds === void 0 ? message("pricing.unknownDuration") : message("pricing.requestedDuration", { seconds })
    );
    const label = element("label", message("pricing.sessionTime"));
    this.duration.type = "number";
    this.duration.min = "0.1";
    this.duration.max = String(browserLimits.maxCalculatorSeconds);
    this.duration.step = "any";
    setTextAttribute(this.duration, "placeholder", message("pricing.enterTime"));
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
      element("p", message("pricing.estimateNotice")),
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
  status = element("p", message("pricing.loading"));
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
      setText(this.status, metadataStatus(catalog.retrieved_at));
      if (!this.models.length) setText(this.status, message("pricing.modelUnavailable"));
      this.render();
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(
          this.status,
          error instanceof Error ? error.message : message("pricing.loadFailed")
        );
    }
  }
  /** Validate session time and update every rate calculation. */
  render() {
    const valid = this.duration.value !== "" && this.duration.validity.valid;
    setText(
      this.validation,
      valid ? "" : message("pricing.timeRange", {
        maximum: browserLimits.maxCalculatorSeconds
      })
    );
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
  const widget = node.addWidget(
    "button",
    translate("pricing.viewRate"),
    "",
    () => openCreditRate(node, fetcher),
    {
      serialize: false
    }
  );
  bindWidgetLabel(node, widget, "pricing.viewRate");
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
  dialog.className = "reactor-dialog reactor-node-help";
  dialog.setAttribute("aria-labelledby", "reactor-node-help-title");
  const heading = element("h2", message("help.title"));
  heading.id = "reactor-node-help-title";
  const close = button(message("close"));
  setTextAttribute(close, "aria-label", message("help.close"));
  close.addEventListener("click", () => dialog.close());
  const header = element("header");
  header.append(heading, close);
  const frame = element("iframe");
  setTextAttribute(frame, "title", message("help.guide"));
  frame.sandbox.add(
    "allow-same-origin",
    "allow-popups",
    "allow-popups-to-escape-sandbox",
    "allow-downloads"
  );
  void selectGuide(frame, nodeId2, controller.signal);
  frame.addEventListener("load", () => prepareGuide(frame, dialog, controller.signal));
  dialog.append(header, frame);
  languageEvents.addEventListener(
    "change",
    () => void selectGuide(frame, nodeId2, controller.signal),
    { signal: controller.signal }
  );
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
  guide.documentElement.style.setProperty("--guide-background", colors.backgroundColor);
  guide.documentElement.style.setProperty("--guide-color", colors.color);
  guide.documentElement.style.setProperty("--guide-link", colors.color);
  guide.documentElement.style.setProperty(
    "--guide-code-background",
    colors.getPropertyValue("--comfy-input-bg") || colors.backgroundColor
  );
  for (const link of guide.querySelectorAll("a")) {
    if (new URL(link.href).origin !== location.origin) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.append(textNode(message("help.newTab")));
    }
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
async function selectGuide(frame, nodeId2, signal) {
  const requested = selectedLocale();
  let language = "en";
  try {
    const response = await fetch(new URL("./guides/languages.json", import.meta.url), { signal });
    const inventory = response.ok ? await response.json() : void 0;
    language = guideLanguage(inventory, nodeId2, requested);
  } catch {
  }
  if (signal.aborted || requested !== selectedLocale()) return;
  const path = language === "en" ? `${nodeId2}.html` : `${nodeId2}/${encodeURIComponent(language)}.html`;
  const url = new URL(`./guides/nodes/${path}`, import.meta.url).href;
  if (frame.src !== url) frame.src = url;
}
function guideLanguage(inventory, nodeId2, requested) {
  if (typeof inventory !== "object" || inventory === null || Array.isArray(inventory)) return "en";
  const installed = inventory[nodeId2];
  if (!Array.isArray(installed)) return "en";
  const names = installed.filter((value) => typeof value === "string");
  for (const candidate of localeCandidates(requested)) {
    const match = names.find((value) => value.toLowerCase() === candidate);
    if (match) return match;
  }
  return "en";
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
app3.registerExtension({
  name: "reactor.inc.configuration",
  init: initializeLanguage,
  setup: () => {
    languageEvents.addEventListener("change", refreshText);
    languageEvents.addEventListener("change", refreshWidgetLabels);
    const stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = new URL("./main.css", import.meta.url).href;
    if (![...document.querySelectorAll("link[rel=stylesheet]")].some(
      (link) => link.getAttribute("href") === stylesheet.href
    ))
      document.head.append(stylesheet);
    api3.addEventListener("reactor-inc.live", (event) => {
      if (event instanceof CustomEvent) {
        openLive(event.detail, requestLocal);
      }
    });
    api3.addEventListener("reactor-inc.controls", (event) => {
      if (event instanceof CustomEvent) openControls(event.detail, requestLocal);
    });
  },
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
