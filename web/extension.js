// web/extension.ts
import { api as api3 } from "../../scripts/api.js";
import { app as app2 } from "../../scripts/app.js";

// web/http.ts
import { api as api2 } from "../../scripts/api.js";

// web/language.ts
import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

// locales/en/main.json
var main_default = {
  reactorInc: {
    camera: {
      accessFailed: "Camera access failed. Choose a camera and try again.",
      browserRequirements: "Camera access needs localhost or HTTPS and a supported browser.",
      busy: "Close other apps using the camera, then try again.",
      default: "Default camera",
      disabled: "Camera off.",
      disconnected: "The camera disconnected. The session is ending.",
      enable: "Enable camera",
      enabled: "Camera on. Microphone audio is off.",
      label: "Camera",
      notFound: "Connect a camera, then try again.",
      number: "Camera {number}",
      permissionDenied: "Allow camera access in the app or browser settings, then try again.",
      preview: "Your camera input",
      readFailed: "Camera frames could not be read.",
      select: "Use selected camera",
      unavailableSelection: "The selected camera is unavailable. Choose another camera.",
      uploadFailed: "Camera frames could not reach the session."
    },
    cancel: "Cancel",
    close: "Close",
    controls: {
      cameraRequired: "Enable a camera before starting.",
      chooseInput: "Choose your input, then start within 60 seconds.",
      connecting: "Connecting to Reactor…",
      connectionClosed: "Connection closed. Check Reactor session status before starting again.",
      connectionEnded: "The live connection ended.",
      dragInstructions: "Drag on the output to steer the subject. Release to stop. With the picture focused, arrow keys position the pointer, Space holds it, and Escape releases it.",
      emptyPrompt: "Enter a prompt before applying it.",
      pointerRateExceeded: "Pointer input arrived too quickly. The session is ending.",
      promptSent: "Prompt sent. The model applies changes to later frames.",
      recording: "Recording. Live controls are ready.",
      recordingNotStarted: "Recording did not start. Close this panel to view the workflow result.",
      recordingNotice: "Recording stops at the chosen duration. Ending early discards the unfinished video. The preview has no sound.",
      soundSent: "Sound prompt sent. The model applies changes to later audio.",
      start: "Start session",
      title: "Reactor live controls"
    },
    errors: {
      acceptedClipChanged: "Fast H3 changed a clip's accepted length.",
      acceptedSequenceLimit: "The accepted clip lengths exceed the video duration limit. Choose fewer clips.",
      accessRefused: "Reactor refused access. Check your key and model access.",
      anchorInterval: "Choose Source refresh interval (chunks) from 0 to 1,000.",
      aspectRatio: "Choose an offered aspect ratio.",
      audioIncomplete: "The recording audio is incomplete.",
      audioLimit: "The recording audio exceeds its native limits.",
      authenticationFailed: "Reactor could not authenticate. Check your saved key and network connection.",
      automaticCheckFailed: "Automatic model check failed. Use Refresh models to retry.",
      automaticChecksType: "Use true or false for automatic model checks.",
      browserOwnerMissing: "The executing prompt has no browser owner.",
      cameraCommandLimit: "Camera input exceeded its pending command limit.",
      cameraCommandTimeout: "A live camera command was not acknowledged in time. The session is ending.",
      cameraDimensions: "Send a JPEG no larger than 640 by 480 pixels.",
      cameraDirection: "Choose a listed camera direction.",
      cameraFrameOrder: "The camera frame is out of order or the session ended.",
      cameraFrameSize: "Send a camera JPEG smaller than 300 KB.",
      cameraFrameWait: "Wait for the previous camera frame.",
      cameraInputStale: "Camera input became stale before it could be sent.",
      cameraInputStopped: "Camera input stopped. The session is ending.",
      cameraJpegRequired: "Send a camera JPEG.",
      cameraStateRequired: "Send a complete listed camera state.",
      captureDisconnected: "The Reactor connection ended before capture finished.",
      captureLimit: "Choose a video length within Maximum video duration (seconds) in Reactor settings.",
      captureQueueFull: "The video capture queue is full. Shorten the capture.",
      captureStopped: "Video capture was stopped.",
      cleanupRestartRequired: "The remote session ended, but local cleanup failed. Restart ComfyUI.",
      cleanupUnconfirmed: "Session cleanup failed; termination is unconfirmed. The server lifetime cap applies.",
      clearKeyBody: "Do not include a body when clearing a saved key.",
      clipCaptureLimit: "The accepted clip length exceeds Maximum video duration (seconds) in Reactor settings. Choose a shorter clip.",
      clipCount: "Choose 2 to 8 clips.",
      clipDurationRange: "The requested length is outside this deployment's clip limits.",
      clipDurationUnsupported: "This deployment does not support the requested clip length.",
      clipIdentifier: "Fast H3 returned an invalid clip ID.",
      clipLength: "Fast H3 returned an invalid clip length.",
      clipLengthChanged: "Fast H3 changed the accepted clip length before playback.",
      clipMediaTime: "Fast H3 returned an invalid media time.",
      clipMissing: "Fast H3 did not return a clip.",
      clipPlaybackOrder: "Fast H3 started playback before the clip was selected.",
      clipReply: "Fast H3 returned an unexpected reply.",
      clipUnfinished: "Fast H3 did not finish the queued clip.",
      clipWindowMissing: "Fast H3 did not report a precise clip window. No partial clip will be saved.",
      clipsUnexpected: "Fast H3 returned unexpected clips.",
      commandRejected: "Reactor rejected a model command. Check this node's inputs and model guide.",
      continuationLength: "Fast H3 returned an invalid continuation length.",
      continuationPrompts: "Use at most 800 characters per prompt and one later prompt per remaining clip.",
      continuedClipDuration: "Choose 5.167 to 14.375 seconds per clip.",
      encoderMetadata: "The video encoder returned invalid metadata.",
      encoderNotReady: "The video encoder did not become ready.",
      encoderPipes: "The video encoder pipes are unavailable.",
      encoderResult: "The video encoder returned no valid result.",
      encoderStopFailed: "The encoder process did not stop. Restart ComfyUI before another run.",
      endingImageUploadLimit: "Provide an ending image within the upload limit.",
      fastAspectRatio: "Choose an offered Fast H3 aspect ratio.",
      fastAudioMissing: "This Fast H3 deployment has no audio track.",
      fastDuration: "Choose 5.167 to 14.375 seconds for Fast H3.",
      fastPromptLength: "Use at most 800 prompt characters.",
      guideListIncomplete: "The guide list may be incomplete. The previous list is unchanged.",
      imageDimensions: "Use an image no larger than 8192 pixels per side.",
      imagePixels: "The image contains non-finite pixel values.",
      imageUploadLimit: "Provide image bytes within the upload limit.",
      jsonDepth: "The JSON input is nested too deeply.",
      jsonDuplicateKey: "Duplicate JSON key.",
      jsonObject: "Expected a JSON object.",
      jsonSize: "The JSON input exceeds its size limit.",
      jsonSyntax: "Enter valid JSON with unique keys.",
      jsonValues: "Use finite numbers and ordinary JSON values.",
      keyEmpty: "Enter a nonempty API key without spaces.",
      keyRequired: "Set your Reactor API key in Reactor settings or the server environment before running.",
      keyUnreadable: "Cannot read the saved Reactor key. Check its private file.",
      keyWhitespace: "The API key cannot contain whitespace.",
      laterPromptLength: "Enter a later prompt of 1 to 20,000 characters.",
      lateralDirection: "Choose an option listed under Sideways movement.",
      liveActionValues: "Choose a supported live action and valid values.",
      liveActionWait: "Wait for the previous live action.",
      liveCameraUnsupported: "This model does not support live scene controls.",
      liveCancelled: "The live run was cancelled.",
      liveCaptureCancelled: "The live capture was cancelled.",
      liveCommandUnfinished: "A live command did not finish. The session is ending.",
      liveControlType: "Choose whether live controls are enabled.",
      liveHostRequirements: "Live controls need a local, single-user ComfyUI browser.",
      liveInputOrder: "The live input is out of order.",
      livePanelClosed: "The live panel was closed.",
      livePanelEnded: "The live panel ended or disconnected. The capture has been stopped.",
      livePanelLimit: "Too many live panels are still open.",
      livePreviewEncoding: "The live preview could not be encoded. The session is ending.",
      liveSessionUnavailable: "This live session is no longer available.",
      localCleanupFailed: "The remote session ended, but local cleanup failed.",
      localConnectionRequired: "Reactor configuration requires a local, same-origin ComfyUI connection.",
      localSourceRequired: "Connect one local SDR clip from Load Video or Create Video within the input limits.",
      longliveImagesUnsupported: "LongLive accepts shot prompts, not images.",
      ltxAudioMissing: "This LTX deployment has no audio track.",
      ltxDuration: "Use at least four seconds for LTX.",
      ltxSceneLength: "Use at most 800 scene characters.",
      modelAuthorization: "Reactor could not authorize this model. Check your key and model access before retrying.",
      modelListChanged: "The model list changed. Reload the list and retry.",
      modelListFormat: "The model list has an invalid or unsupported format.",
      modelListGrowth: "The model list grew unexpectedly. Review the source before updating.",
      modelListHistoryEmpty: "There is no earlier model list to restore.",
      modelRefreshRunning: "A model list refresh is already running.",
      modelRefreshWait: "Wait for the model list refresh to finish.",
      modelRevisionRequired: "Send the model list revision shown in this tab.",
      modelUnavailable: "The requested Reactor model or protocol is unavailable. Check for updates.",
      modelsHttp: "Reactor's model list returned HTTP {status}. Try again later.",
      modelsUnreadable: "Cannot read Reactor's public model list. The previous list is unchanged.",
      nodeUnregistered: "The Reactor node is not registered.",
      outputClosed: "The recording output is closed.",
      outputSize: "The recording exceeds the output size limit.",
      packageVersionMissing: "The connector's version is missing. Reinstall the package.",
      phase: "{message} Stage: {phase}. Code: {code}.",
      pointerCoordinates: "Choose pointer coordinates from 0 to 1.",
      pointerOptionType: "Use true or false for Keep queued frames and Hold pointer.",
      portraitRequired: "Provide one portrait.",
      portraitUploadLimit: "Provide one portrait within the upload limit.",
      priceListIncomplete: "The pricing list may be incomplete. The previous list is unchanged.",
      privateStateLocation: "Keep Reactor's private state outside ComfyUI, its package, and its media folders.",
      promptChunk: "Choose a later prompt's chunk from 1 to 100,000.",
      promptLength: "Enter a prompt of 1 to 20,000 characters.",
      promptSequenceOrder: "Use at most 32 later prompts with distinct, increasing chunk numbers.",
      promptSequenceSize: "Keep the prompt sequence within 128 KB.",
      providerRateLimit: "Reactor is limiting requests. Wait before starting another run.",
      providerRequestTimeout: "Reactor did not reply within its request limit.",
      queueTimeout: "Timed out waiting for another Reactor run to finish. This waiting run did not open a session.",
      recordingDisconnected: "The recording session is not connected.",
      recordingMetadata: "The recording returned invalid media metadata.",
      recordingNotReady: "The recording was not ready within the capture time limit.",
      recordingReadiness: "The recording returned invalid readiness timing.",
      recordingTiming: "The recording returned invalid timing markers.",
      recordingUnsupported: "Reactor returned an unsupported recording. No partial video was saved.",
      refreshBody: "Do not send a body when refreshing public models.",
      requestEncoding: "Send valid UTF-8 JSON.",
      requestJsonRequired: "Send a JSON request.",
      requestTimeout: "The configuration request took too long.",
      reservationReused: "Create a new reservation for each session.",
      resolutionName: "Use a short model resolution name.",
      resolutionUnavailable: "This model does not offer that resolution. Leave it blank for the default.",
      rotationSpeed: "Choose Turn per step (degrees) from 0 to 30.",
      runFailed: "Reactor could not complete this run. Check your connection and account status.",
      runTimeout: "Reactor did not finish within the configured time limit.",
      runtimeNotReady: "Reactor has not finished loading. Restart ComfyUI.",
      sanaPromptLength: "Use at most 20,000 prompt characters.",
      sanaUnsupported: "This SANA version is not supported. Update the connector.",
      sanaWebcamUnsupported: "This SANA deployment does not accept webcam input.",
      savedKeyLink: "A saved key cannot be a symbolic link.",
      savedVideoDetails: "The saved video returned invalid details.",
      savedVideoTimeout: "Reading the saved video's details took too long.",
      seedRange: "Choose a seed from 0 to 4,294,967,295.",
      sequenceCaptureLimit: "The sequence exceeded the video duration limit. Choose fewer clips or a longer limit.",
      sequencePlaybackOrder: "Fast H3 started playback before the sequence was ready.",
      sessionAlreadyConnected: "This Reactor session cannot be connected again.",
      sessionCapacity: "Choose a session capacity from 1 to 4.",
      sessionDeadline: "The session deadline expired during this operation.",
      sessionDisconnected: "The Reactor session is not connected.",
      sessionInOtherProcess: "Another ComfyUI process is using Reactor. Let its run finish before trying again.",
      sessionLimitTooShort: "Set Maximum session duration (seconds) higher than Maximum video duration (seconds) to allow setup and cleanup.",
      sessionLockLink: "The session lock cannot be a link.",
      sessionLockPermissions: "Restrict the session lock file to its owner.",
      sessionRecordDamaged: "The saved Reactor session record is damaged. Check Reactor Usage before repairing the session record in the connector's private settings folder.",
      sessionRecordPermissions: "The Reactor session record could not be updated. The saved wait still applies. Check access to the connector's private settings folder.",
      sessionRecordUnreadable: "The Reactor session record could not be read or saved. No session was started. Check access to the connector's private settings folder.",
      sessionRecordUpdateFailed: "The Reactor session record could not be updated. The saved wait still applies.",
      sessionTimeout: "Reactor exceeded the configured time limit.",
      sessionWait: "An earlier Reactor session may still be running. Wait {seconds} seconds before another run. Restarting ComfyUI does not clear this wait.",
      sessionWaitTime: "Use a positive session wait time.",
      settingReadOnly: "This setting cannot be changed here.",
      settingUnknown: "The settings contain an unknown option.",
      settingsChanged: "Settings changed. Reload them before saving.",
      settingsRange: "Choose a setting within the range shown in Reactor settings.",
      settingsRevisionRequired: "Send settings and their current revision.",
      settingsUnreadable: "Cannot load Reactor execution settings. Check the limits and private key.",
      settingsWholeNumbers: "Use whole numbers for Reactor limits and check intervals.",
      shotChunk: "Place a later shot at chunk 1 or above.",
      shotPrompt: "Enter a shot prompt of 1 to 20,000 characters.",
      shotTransition: "Choose a soft transition or a cut.",
      singleImageRequired: "Connect exactly one RGB image, not a batch.",
      singleKeyRequired: "Send one API key.",
      soundOptionType: "Use boolean sound and prompt options.",
      soundPromptLength: "Use at most 1,000 audio prompt characters.",
      sourceDimensions: "Use even video dimensions within the input limit.",
      sourceFrameCount: "Use a source video with at least 33 frames.",
      sourceFrameRate: "The prepared video has no valid frame rate.",
      sourceFramesLost: "The prepared source lost frames during encoding.",
      sourceFramesMissing: "The prepared input has no frames.",
      sourcePixels: "Source pixels must be finite numbers.",
      sourceReaderClosed: "The prepared video reader is closed.",
      sourceTimestampMissing: "The prepared video has no frame timestamp.",
      sourceVideoFormat: "Use an SDR RGB video at 1 to 120 frames per second.",
      sourceVideoRequired: "Connect a prepared source video.",
      speechLength: "Enter a script of 1 to 10,000 characters.",
      speechPace: "Use a positive whole-number speech pace.",
      speechPaceMissing: "LTX did not report its accepted speech pace.",
      speechPaceRange: "Use a speech pace from {minimum} to {maximum}.",
      startingImageRequired: "Connect one starting image.",
      stateDirectoryAbsolute: "Use an absolute state directory path.",
      stateDirectoryLink: "The state directory cannot be a symbolic link.",
      stateDirectoryPermissions: "Restrict the state directory to its owner.",
      stateFileChanged: "The private state file changed while opening.",
      stateFileLink: "A state file cannot be a symbolic link.",
      stateFilePermissions: "Restrict the state file to its owner.",
      stateFileSize: "The state file exceeds its size limit.",
      stateFileType: "The requested state file is not a regular file.",
      stateUnreadable: "Cannot read connector state. Check its location and permissions.",
      storyboardOrder: "Use a storyboard of at most 32 shots with distinct, increasing chunk numbers.",
      storyboardSize: "Keep the storyboard within 128 KB.",
      terminationUnconfirmed: "Session termination is unconfirmed. Wait for its server limit before retrying.",
      terminationWait: "An earlier Reactor session has unconfirmed termination. Wait {seconds} seconds before starting another run.",
      videoArrivalRate: "Video arrived faster than it could be saved. Shorten the capture.",
      videoEncodingFailed: "Video encoding failed. Check disk space and media support.",
      videoFrameColor: "The video track must provide RGB frames.",
      videoFrameType: "The video track returned an unsupported frame.",
      videoTimestamp: "The video track returned an invalid timestamp.",
      videoTrackMissing: "The model did not declare its expected video track.",
      viskoAudioMissing: "This Visko deployment has no audio track.",
      viskoImageChanged: "Visko started with different image settings. The run was stopped.",
      viskoResolutionChanged: "Visko started at a different resolution. The run was stopped.",
      viskoSoundChanged: "Visko started with different sound settings. The run was stopped.",
      worldPromptLength: "Use a prompt of at most 1,000 characters.",
      x2PromptLength: "Use at most 1,000 prompt characters.",
      x2Unsupported: "This X2 version is not supported. Update the connector."
    },
    live: {
      actionRejected: "The live action was not accepted. The session is ending.",
      applyPrompt: "Apply prompt",
      back: "Back",
      connectingPanel: "Connecting the live panel…",
      connectionLost: "The live connection was lost. The connector will ask Reactor to stop after five seconds without a browser connection. Check Reactor Usage to confirm the session has ended before another run.",
      discarded: "The session ended without saving a video. Close this panel to view the workflow result.",
      duration: "{model} · {seconds} seconds of video",
      elapsed: "Time spent on setup and recording: {seconds} seconds.",
      emptyScenePrompt: "Enter a scene prompt before applying it.",
      endSession: "End session",
      ended: "Session ended. Close this panel to view the workflow result.",
      ending: "Ending the session…",
      forward: "Forward",
      invalidStatus: "The live panel received an invalid status.",
      lookDown: "Look down",
      lookLeft: "Look left",
      lookRight: "Look right",
      lookUp: "Look up",
      moveLeft: "Move left",
      moveRight: "Move right",
      movementInstructions: "Click the picture, then use W A S D to move and arrow keys to turn. Click a button for a brief movement, or hold it to keep moving. Escape stops camera movement.",
      movementLabel: "Live view. W A S D moves. Arrow keys turn. Escape stops camera movement.",
      output: "Live model output",
      previewReady: "Live preview. Controls are active.",
      promptNotice: "Prompt changes affect later frames. The starting image stays fixed.",
      promptSent: "Prompt sent. Watch the video for the change.",
      recordingNotice: "The preview has fewer frames per second than the saved video and has no sound. Save Video saves the finished recording. Ending early discards the unfinished video.",
      scenePrompt: "Scene prompt",
      unconfirmedEnd: "Reactor has not confirmed that the session ended. Wait for its time limit before another run.",
      unreachable: "Live controls could not reach their session.",
      waitingVideo: "Waiting for model video…",
      sceneTitle: "Reactor scene controls",
      editPrompt: "Edit prompt"
    },
    models: {
      checkDue: "An automatic model check is due. Checks do not change this list.",
      checkRunning: "An automatic model check is running. Reopen this list to see its result.",
      checkSchedule: "Automatic check: {date}. Checks run every {hours} hours.",
      checking: "Checking public model sources…",
      checksOff: "Automatic model checks are off. Change this in Reactor settings.",
      close: "Close Reactor models",
      connectName: "Model ID: {name}",
      count: "{visible} of {total} models",
      guideUnavailable: "No matching public guide was found.",
      installedList: "Showing installed nodes. Refresh models to load public prices and guides.",
      invalidResponse: "ComfyUI returned an invalid Reactor model list.",
      lastRefresh: "Public prices and guides checked {date}.",
      listChanged: "The model list has changed. Select Refresh models to update your list.",
      loadFailed: "Cannot load models.",
      loaded: "Local model list loaded.",
      loading: "Loading model list…",
      loadingLocal: "Loading the local model list…",
      nodeUnavailable: "No connector node available.",
      nodesAvailable: "Nodes available.",
      openGuide: "Reactor model guide (opens in a new tab)",
      refresh: "Refresh models",
      refreshNotice: "Refresh updates public prices and model information. New models need support in the connector.",
      refreshed: "Model list refreshed.",
      requestFailed: "The model list request failed.",
      restore: "Restore previous list",
      restored: "Previous model list restored. This does not change which models Reactor offers.",
      search: "Search models",
      searchPlaceholder: "Model name or ID",
      showAll: "Show all models",
      sources: "Model sources and automatic checks",
      title: "Reactor models",
      unreachable: "Cannot reach the Reactor model list. Check ComfyUI and try again."
    },
    pointer: {
      held: "Pointer held.",
      instructions: "Drag on the output to move the subject. Use arrow keys to position the pointer, Space to hold it, and Escape to release it.",
      position: " {x}% across, {y}% down.",
      released: "Pointer released.",
      stopped: "Pointer controls stopped."
    },
    pricing: {
      calculate: "Calculate credits for session time",
      calculation: "{seconds} session seconds × {rate} credits per second = {credits} credits.",
      enterTime: "Enter session time",
      estimateNotice: "Estimate = rate × session time. Session time includes setup and recording.",
      loadFailed: "Cannot load the credit rate.",
      loading: "Loading the local credit rate…",
      modelUnavailable: "No rate is listed for this node. Open the ComfyUI menu, then Extensions → Reactor → Reactor models, and refresh the list.",
      rate: "{rate} credits per session second.",
      rateOutdated: "This rate was not found in the latest source check. Refresh Reactor models before relying on a calculation.",
      rateUnavailable: "A current rate is not available. Refresh Reactor models to check for a rate.",
      requestedDuration: "Requested video length: {seconds} seconds.",
      sessionTime: "Session time to calculate (seconds)",
      timeRange: "Enter a session time from 0.1 to {maximum} seconds.",
      title: "Credit rate",
      totalTimeNotice: "Use total session time, including setup and recording.",
      unknownDuration: "The video length comes from a connected input or is not available. Enter a session time below to calculate credits.",
      viewRate: "View credit rate"
    },
    settings: {
      advancedLimits: "Advanced limits",
      automaticChecks: "Check for model updates automatically",
      checkInterval: "Check interval (hours)",
      checkNotice: "Checks read public prices and model guides. Open Reactor models to see changes and refresh your list.",
      checksSaved: "Model check settings saved. Changes take effect within one minute.",
      clearKey: "Clear saved key",
      close: "Close Reactor settings",
      credentialLabel: "Reactor API key",
      credentials: "Credentials",
      environmentKey: "The server's REACTOR_API_KEY environment variable is active.",
      incompleteResponse: "ComfyUI returned incomplete Reactor settings.",
      invalidChecks: "ComfyUI returned invalid model check settings.",
      invalidDefinition: "ComfyUI returned an invalid Reactor setting definition.",
      invalidLimit: "ComfyUI returned an invalid Reactor limit.",
      invalidResponse: "ComfyUI returned an invalid Reactor settings response.",
      keyCleared: "Saved key cleared. Any environment key remains active.",
      keyNotice: "The saved key stays on the ComfyUI server. An environment key takes precedence. Keys are not checked with Reactor here.",
      keySaved: "Key saved on this server. Reactor checks it when you start a session.",
      limit: {
        catalog_interval_hours: "Check interval (hours)",
        cleanup_timeout_seconds: "Disconnect timeout (seconds)",
        connect_timeout_seconds: "Connection timeout (seconds)",
        first_frame_timeout_seconds: "First-frame timeout (seconds)",
        max_capture_megabytes: "Maximum video file size (MiB)",
        max_capture_seconds: "Maximum video duration (seconds)",
        max_queue_megabytes: "Maximum queued frame data (MiB)",
        max_session_seconds: "Maximum session duration (seconds)",
        max_upload_megabytes: "Maximum upload size (MiB)",
        queue_timeout_seconds: "Queue wait timeout (seconds)"
      },
      limits: "Execution limits",
      limitsSaved: "Limits saved. They apply to new executions.",
      loaded: "Local settings loaded.",
      loading: "Loading local settings…",
      missingKey: "No Reactor key is configured.",
      modelUpdates: "Model updates",
      noCheckChanges: "No model check changes to save.",
      noLimitChanges: "No limit changes to save.",
      readOnly: "Changes are disabled in this host's multi-user mode.",
      reload: "Reload settings",
      saveChecks: "Save model check settings",
      saveFailed: "ComfyUI could not save Reactor settings.",
      saveKey: "Save key",
      saveLimits: "Save limits",
      savedKey: "A saved key is configured on this server.",
      timeNotice: "Session time includes setup and generation.",
      title: "Reactor settings",
      unreachable: "Cannot reach Reactor settings. Check ComfyUI and try again.",
      unreadableResponse: "ComfyUI returned an unreadable Reactor settings response.",
      updateFailed: "Reactor settings could not be saved."
    },
    sound: {
      applyPrompt: "Apply sound prompt",
      prompt: "Sound prompt",
      promptNotice: "Describe the sound briefly. Leave blank to use the picture alone.",
      title: "Sound"
    },
    working: "Working…"
  }
};

// web/language.ts
var languageEvents = new EventTarget();
var messages = /* @__PURE__ */ new Map();
function readMessage(source, key) {
  let value = source;
  for (const part of key.split(".")) {
    if (typeof value !== "object" || value === null || !Object.hasOwn(value, part))
      return void 0;
    value = value[part];
  }
  return typeof value === "string" ? value : void 0;
}
async function initializeLanguage() {
  try {
    const languages = await api.getCustomNodesI18n();
    const available = /* @__PURE__ */ new Map();
    for (const [language, document2] of Object.entries(languages)) {
      available.set(language.toLowerCase(), document2);
    }
    messages = available;
  } catch {
    messages = /* @__PURE__ */ new Map();
  }
}
function translate(key, values = {}, fallback) {
  let message2;
  for (const language of localeCandidates(selectedLocale())) {
    message2 = readMessage(messages.get(language), `reactorInc.${key}`);
    if (message2 !== void 0) break;
  }
  const text = message2 ?? readMessage(main_default.reactorInc, key) ?? fallback ?? key;
  return text.replaceAll(/\{(\w+)\}/g, substituteValue.bind(null, values));
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
  let chinese = false;
  for (const tag of ["zh-tw", "zh-hk", "zh-mo", "zh-hant"]) {
    if (exact === tag || exact.startsWith(tag + "-")) {
      chinese = true;
      break;
    }
  }
  return [.../* @__PURE__ */ new Set([exact, chinese ? "zh-tw" : base, "en"])];
}
function formatNumber(value, options) {
  const locale = selectedLocale();
  const formatter = new Intl.NumberFormat(locale, options);
  return formatter.format(value);
}
function formatDate(value) {
  const date = new Date(value);
  const locale = selectedLocale();
  return date.toLocaleString(locale);
}
function substituteValue(values, placeholder, name) {
  if (!Object.hasOwn(values, name)) return placeholder;
  return displayValue(values[name]);
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
  const content = { key, values };
  if (fallback !== void 0) content.fallback = fallback;
  return content;
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
    const current4 = bindingText(target, binding.attribute);
    if (current4 !== binding.rendered) {
      bindings.delete(binding);
      continue;
    }
    updateBinding(target, binding);
  }
}
function bindingText(target, attribute) {
  if (target instanceof Text) return target.data;
  return target instanceof Element && attribute ? target.getAttribute(attribute) : null;
}
function updateBinding(target, binding) {
  binding.rendered = translate(
    binding.message.key,
    binding.message.values,
    binding.message.fallback
  );
  if (target instanceof Text) target.data = binding.rendered;
  else if (target instanceof Element && binding.attribute)
    target.setAttribute(binding.attribute, binding.rendered);
}

// web/routes.ts
var browserRoutes = {
  settings: {
    status: "/reactor-inc/v1/status",
    values: "/reactor-inc/v1/settings",
    credential: "/reactor-inc/v1/credential"
  },
  models: {
    read: "/reactor-inc/v1/catalog",
    refresh: "/reactor-inc/v1/catalog/refresh",
    rollback: "/reactor-inc/v1/catalog/rollback"
  },
  live: {
    exchange: "/reactor-inc/v1/live/exchange",
    action: "/reactor-inc/v1/live/action",
    camera: "/reactor-inc/v1/live/camera"
  }
};

// node_modules/valibot/dist/index.mjs
var store$4;
var DEFAULT_CONFIG = {
  lang: void 0,
  message: void 0,
  abortEarly: void 0,
  abortPipeEarly: void 0
};
// @__NO_SIDE_EFFECTS__
function getGlobalConfig(config$1) {
  if (!config$1 && !store$4) return DEFAULT_CONFIG;
  return {
    lang: config$1?.lang ?? store$4?.lang,
    message: config$1?.message,
    abortEarly: config$1?.abortEarly ?? store$4?.abortEarly,
    abortPipeEarly: config$1?.abortPipeEarly ?? store$4?.abortPipeEarly
  };
}
var store$3;
// @__NO_SIDE_EFFECTS__
function getGlobalMessage(lang) {
  return store$3?.get(lang);
}
var store$2;
// @__NO_SIDE_EFFECTS__
function getSchemaMessage(lang) {
  return store$2?.get(lang);
}
var store$1;
// @__NO_SIDE_EFFECTS__
function getSpecificMessage(reference, lang) {
  return store$1?.get(reference)?.get(lang);
}
// @__NO_SIDE_EFFECTS__
function _stringify(input) {
  const type = typeof input;
  if (type === "string") return `"${input}"`;
  if (type === "number" || type === "bigint" || type === "boolean") return `${input}`;
  if (type === "object" || type === "function") return (input && Object.getPrototypeOf(input)?.constructor?.name) ?? "null";
  return type;
}
function _addIssue(context, label, dataset, config$1, other) {
  const input = other && "input" in other ? other.input : dataset.value;
  const expected = other?.expected ?? context.expects ?? null;
  const received = other?.received ?? /* @__PURE__ */ _stringify(input);
  const issue = {
    kind: context.kind,
    type: context.type,
    input,
    expected,
    received,
    message: `Invalid ${label}: ${expected ? `Expected ${expected} but r` : "R"}eceived ${received}`,
    requirement: context.requirement,
    path: other?.path,
    issues: other?.issues,
    lang: config$1.lang,
    abortEarly: config$1.abortEarly,
    abortPipeEarly: config$1.abortPipeEarly
  };
  const isSchema = context.kind === "schema";
  const message$1 = other?.message ?? context.message ?? /* @__PURE__ */ getSpecificMessage(context.reference, issue.lang) ?? (isSchema ? /* @__PURE__ */ getSchemaMessage(issue.lang) : null) ?? config$1.message ?? /* @__PURE__ */ getGlobalMessage(issue.lang);
  if (message$1 !== void 0) issue.message = typeof message$1 === "function" ? message$1(issue) : message$1;
  if (isSchema) dataset.typed = false;
  if (dataset.issues) dataset.issues.push(issue);
  else dataset.issues = [issue];
}
// @__NO_SIDE_EFFECTS__
function _isValidObjectKey(object$1, key) {
  return Object.prototype.hasOwnProperty.call(object$1, key) && key !== "__proto__" && key !== "prototype" && key !== "constructor";
}
// @__NO_SIDE_EFFECTS__
function _joinExpects(values$1, separator) {
  const list = [...new Set(values$1)];
  if (list.length > 1) return `(${list.join(` ${separator} `)})`;
  return list[0] ?? "never";
}
function _standardSchema(schema) {
  schema["~standard"] = {
    version: 1,
    vendor: "valibot",
    validate: (value$1) => schema["~run"]({ value: value$1 }, /* @__PURE__ */ getGlobalConfig())
  };
  return schema;
}
// @__NO_SIDE_EFFECTS__
function check(requirement, message$1) {
  return {
    kind: "validation",
    type: "check",
    reference: check,
    async: false,
    expects: null,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement(dataset.value)) _addIssue(this, "input", dataset, config$1);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function finite(message$1) {
  return {
    kind: "validation",
    type: "finite",
    reference: finite,
    async: false,
    expects: null,
    requirement: Number.isFinite,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement(dataset.value)) _addIssue(this, "finite", dataset, config$1);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function gtValue(requirement, message$1) {
  return {
    kind: "validation",
    type: "gt_value",
    reference: gtValue,
    async: false,
    expects: `>${requirement instanceof Date ? requirement.toJSON() : /* @__PURE__ */ _stringify(requirement)}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !(dataset.value > this.requirement)) _addIssue(this, "value", dataset, config$1, { received: dataset.value instanceof Date ? dataset.value.toJSON() : /* @__PURE__ */ _stringify(dataset.value) });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function includes(requirement, message$1) {
  const expects = /* @__PURE__ */ _stringify(requirement);
  return {
    kind: "validation",
    type: "includes",
    reference: includes,
    async: false,
    expects,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !dataset.value.includes(this.requirement)) _addIssue(this, "content", dataset, config$1, { received: `!${expects}` });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function maxLength(requirement, message$1) {
  return {
    kind: "validation",
    type: "max_length",
    reference: maxLength,
    async: false,
    expects: `<=${requirement}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && dataset.value.length > this.requirement) _addIssue(this, "length", dataset, config$1, { received: `${dataset.value.length}` });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function maxValue(requirement, message$1) {
  return {
    kind: "validation",
    type: "max_value",
    reference: maxValue,
    async: false,
    expects: `<=${requirement instanceof Date ? requirement.toJSON() : /* @__PURE__ */ _stringify(requirement)}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !(dataset.value <= this.requirement)) _addIssue(this, "value", dataset, config$1, { received: dataset.value instanceof Date ? dataset.value.toJSON() : /* @__PURE__ */ _stringify(dataset.value) });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function minLength(requirement, message$1) {
  return {
    kind: "validation",
    type: "min_length",
    reference: minLength,
    async: false,
    expects: `>=${requirement}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && dataset.value.length < this.requirement) _addIssue(this, "length", dataset, config$1, { received: `${dataset.value.length}` });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function minValue(requirement, message$1) {
  return {
    kind: "validation",
    type: "min_value",
    reference: minValue,
    async: false,
    expects: `>=${requirement instanceof Date ? requirement.toJSON() : /* @__PURE__ */ _stringify(requirement)}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !(dataset.value >= this.requirement)) _addIssue(this, "value", dataset, config$1, { received: dataset.value instanceof Date ? dataset.value.toJSON() : /* @__PURE__ */ _stringify(dataset.value) });
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function regex(requirement, message$1) {
  return {
    kind: "validation",
    type: "regex",
    reference: regex,
    async: false,
    expects: `${requirement}`,
    requirement,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement.test(dataset.value)) _addIssue(this, "format", dataset, config$1);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function safeInteger(message$1) {
  return {
    kind: "validation",
    type: "safe_integer",
    reference: safeInteger,
    async: false,
    expects: null,
    requirement: Number.isSafeInteger,
    message: message$1,
    "~run"(dataset, config$1) {
      if (dataset.typed && !this.requirement(dataset.value)) _addIssue(this, "safe integer", dataset, config$1);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function transform(operation) {
  return {
    kind: "transformation",
    type: "transform",
    reference: transform,
    async: false,
    operation,
    "~run"(dataset) {
      dataset.value = this.operation(dataset.value);
      return dataset;
    }
  };
}
// @__NO_SIDE_EFFECTS__
function getFallback(schema, dataset, config$1) {
  return typeof schema.fallback === "function" ? schema.fallback(dataset, config$1) : schema.fallback;
}
// @__NO_SIDE_EFFECTS__
function getDefault(schema, dataset, config$1) {
  return typeof schema.default === "function" ? schema.default(dataset, config$1) : schema.default;
}
// @__NO_SIDE_EFFECTS__
function array(item, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "array",
    reference: array,
    expects: "Array",
    async: false,
    item,
    message: message$1,
    "~run"(dataset, config$1) {
      const input = dataset.value;
      if (Array.isArray(input)) {
        dataset.typed = true;
        dataset.value = [];
        for (let key = 0; key < input.length; key++) {
          const value$1 = input[key];
          const itemDataset = this.item["~run"]({ value: value$1 }, config$1);
          if (itemDataset.issues) {
            const pathItem = {
              type: "array",
              origin: "value",
              input,
              key,
              value: value$1
            };
            for (const issue of itemDataset.issues) {
              if (issue.path) issue.path.unshift(pathItem);
              else issue.path = [pathItem];
              dataset.issues?.push(issue);
            }
            if (!dataset.issues) dataset.issues = itemDataset.issues;
            if (config$1.abortEarly) {
              dataset.typed = false;
              break;
            }
          }
          if (!itemDataset.typed) dataset.typed = false;
          dataset.value.push(itemDataset.value);
        }
      } else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function boolean(message$1) {
  return _standardSchema({
    kind: "schema",
    type: "boolean",
    reference: boolean,
    expects: "boolean",
    async: false,
    message: message$1,
    "~run"(dataset, config$1) {
      if (typeof dataset.value === "boolean") dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function nullable(wrapped, default_) {
  return _standardSchema({
    kind: "schema",
    type: "nullable",
    reference: nullable,
    expects: `(${wrapped.expects} | null)`,
    async: false,
    wrapped,
    default: default_,
    "~run"(dataset, config$1) {
      if (dataset.value === null) {
        if (this.default !== void 0) dataset.value = /* @__PURE__ */ getDefault(this, dataset, config$1);
        if (dataset.value === null) {
          dataset.typed = true;
          return dataset;
        }
      }
      return this.wrapped["~run"](dataset, config$1);
    }
  });
}
// @__NO_SIDE_EFFECTS__
function number(message$1) {
  return _standardSchema({
    kind: "schema",
    type: "number",
    reference: number,
    expects: "number",
    async: false,
    message: message$1,
    "~run"(dataset, config$1) {
      if (typeof dataset.value === "number" && !isNaN(dataset.value)) dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function object(entries$1, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "object",
    reference: object,
    expects: "Object",
    async: false,
    entries: entries$1,
    message: message$1,
    "~run"(dataset, config$1) {
      const input = dataset.value;
      if (input && typeof input === "object") {
        dataset.typed = true;
        dataset.value = {};
        for (const key in this.entries) {
          const valueSchema = this.entries[key];
          if (key in input || (valueSchema.type === "exact_optional" || valueSchema.type === "optional" || valueSchema.type === "nullish") && valueSchema.default !== void 0) {
            const value$1 = key in input ? input[key] : /* @__PURE__ */ getDefault(valueSchema);
            const valueDataset = valueSchema["~run"]({ value: value$1 }, config$1);
            if (valueDataset.issues) {
              const pathItem = {
                type: "object",
                origin: "value",
                input,
                key,
                value: value$1
              };
              for (const issue of valueDataset.issues) {
                if (issue.path) issue.path.unshift(pathItem);
                else issue.path = [pathItem];
                dataset.issues?.push(issue);
              }
              if (!dataset.issues) dataset.issues = valueDataset.issues;
              if (config$1.abortEarly) {
                dataset.typed = false;
                break;
              }
            }
            if (!valueDataset.typed) dataset.typed = false;
            dataset.value[key] = valueDataset.value;
          } else if (valueSchema.fallback !== void 0) dataset.value[key] = /* @__PURE__ */ getFallback(valueSchema);
          else if (valueSchema.type !== "exact_optional" && valueSchema.type !== "optional" && valueSchema.type !== "nullish") {
            _addIssue(this, "key", dataset, config$1, {
              input: void 0,
              expected: `"${key}"`,
              path: [{
                type: "object",
                origin: "key",
                input,
                key,
                value: input[key]
              }]
            });
            if (config$1.abortEarly) break;
          }
        }
      } else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function optional(wrapped, default_) {
  return _standardSchema({
    kind: "schema",
    type: "optional",
    reference: optional,
    expects: `(${wrapped.expects} | undefined)`,
    async: false,
    wrapped,
    default: default_,
    "~run"(dataset, config$1) {
      if (dataset.value === void 0) {
        if (this.default !== void 0) dataset.value = /* @__PURE__ */ getDefault(this, dataset, config$1);
        if (dataset.value === void 0) {
          dataset.typed = true;
          return dataset;
        }
      }
      return this.wrapped["~run"](dataset, config$1);
    }
  });
}
// @__NO_SIDE_EFFECTS__
function picklist(options, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "picklist",
    reference: picklist,
    expects: /* @__PURE__ */ _joinExpects(options.map(_stringify), "|"),
    async: false,
    options,
    message: message$1,
    "~run"(dataset, config$1) {
      if (this.options.includes(dataset.value)) dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function record(key, value$1, message$1) {
  return _standardSchema({
    kind: "schema",
    type: "record",
    reference: record,
    expects: "Object",
    async: false,
    key,
    value: value$1,
    message: message$1,
    "~run"(dataset, config$1) {
      const input = dataset.value;
      if (input && typeof input === "object") {
        dataset.typed = true;
        dataset.value = {};
        for (const entryKey in input) if (/* @__PURE__ */ _isValidObjectKey(input, entryKey)) {
          const entryValue = input[entryKey];
          const keyDataset = this.key["~run"]({ value: entryKey }, config$1);
          if (keyDataset.issues) {
            const pathItem = {
              type: "object",
              origin: "key",
              input,
              key: entryKey,
              value: entryValue
            };
            for (const issue of keyDataset.issues) {
              issue.path = [pathItem];
              dataset.issues?.push(issue);
            }
            if (!dataset.issues) dataset.issues = keyDataset.issues;
            if (config$1.abortEarly) {
              dataset.typed = false;
              break;
            }
          }
          const valueDataset = this.value["~run"]({ value: entryValue }, config$1);
          if (valueDataset.issues) {
            const pathItem = {
              type: "object",
              origin: "value",
              input,
              key: entryKey,
              value: entryValue
            };
            for (const issue of valueDataset.issues) {
              if (issue.path) issue.path.unshift(pathItem);
              else issue.path = [pathItem];
              dataset.issues?.push(issue);
            }
            if (!dataset.issues) dataset.issues = valueDataset.issues;
            if (config$1.abortEarly) {
              dataset.typed = false;
              break;
            }
          }
          if (!keyDataset.typed || !valueDataset.typed) dataset.typed = false;
          if (keyDataset.typed) dataset.value[keyDataset.value] = valueDataset.value;
        }
      } else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function string(message$1) {
  return _standardSchema({
    kind: "schema",
    type: "string",
    reference: string,
    expects: "string",
    async: false,
    message: message$1,
    "~run"(dataset, config$1) {
      if (typeof dataset.value === "string") dataset.typed = true;
      else _addIssue(this, "type", dataset, config$1);
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function unknown() {
  return _standardSchema({
    kind: "schema",
    type: "unknown",
    reference: unknown,
    expects: "unknown",
    async: false,
    "~run"(dataset) {
      dataset.typed = true;
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function pipe(...pipe$1) {
  return _standardSchema({
    ...pipe$1[0],
    pipe: pipe$1,
    "~run"(dataset, config$1) {
      for (const item of pipe$1) if (item.kind !== "metadata") {
        if (dataset.issues && (item.kind === "schema" || item.kind === "transformation")) {
          dataset.typed = false;
          break;
        }
        if (!dataset.issues || !config$1.abortEarly && !config$1.abortPipeEarly) dataset = item["~run"](dataset, config$1);
      }
      return dataset;
    }
  });
}
// @__NO_SIDE_EFFECTS__
function safeParse(schema, input, config$1) {
  const dataset = schema["~run"]({ value: input }, /* @__PURE__ */ getGlobalConfig(config$1));
  return {
    typed: dataset.typed,
    success: !dataset.issues,
    output: dataset.value,
    issues: dataset.issues
  };
}

// web/browser.ts
var browserLimits = {
  requestTimeoutMilliseconds: 1e4,
  discoveryTimeoutMilliseconds: 3e4,
  pollIntervalMilliseconds: 100,
  actionTimeoutMilliseconds: 2e3,
  inputNudgeMilliseconds: 250,
  maxPendingInputs: 8,
  maxPreviewCharacters: 35e4,
  maxCalculatorSeconds: 3600,
  maxTextCharacters: 200,
  maxErrorCharacters: 1024,
  maxRetrievalTimeCharacters: 40,
  maxModelNodeIds: 100,
  maxModels: 1024
};
var browserInput = {
  pointerCenter: 0.5,
  pointerMinimum: 0,
  pointerMaximum: 1,
  pointerStep: 0.03,
  cameraWidth: 640,
  cameraHeight: 480,
  cameraIdealFrameRate: 12,
  cameraMaxFrameRate: 24,
  cameraJpegQuality: 0.8
};
var browserPatterns = {
  lease: /^[a-f0-9]{32}$/,
  revision: /^[a-f0-9]{64}$/,
  preview: /^[A-Za-z0-9+/]*={0,2}$/,
  capability: /^[A-Za-z0-9_-]{43}$/,
  documentation: /^https:\/\/docs\.reactor\.inc\/model-api-reference\/[a-z0-9._-]+\/overview$/,
  nodeId: /^ReactorInc[A-Za-z0-9]+$/,
  settingName: /^[a-z][a-z_]+$/
};

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
  constructor(surface, controls, signal, update) {
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
    surface.addEventListener("blur", this.release.bind(this), { signal });
    this.bindButtons(controls, signal);
    window.addEventListener("blur", this.release.bind(this), { signal });
    document.addEventListener(
      "visibilitychange",
      () => {
        if (document.hidden) this.release();
      },
      { signal }
    );
    signal.addEventListener("abort", this.release.bind(this), { once: true });
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
  publish(release = false) {
    const keys = new Set(this.keyboard);
    for (const key of this.pointers.values()) keys.add(key);
    for (const key of this.nudges.keys()) keys.add(key);
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
      setTimeout(() => {
        this.nudges.delete(key);
        const keys = /* @__PURE__ */ new Set([...this.keyboard, ...this.pointers.values(), ...this.nudges.keys()]);
        this.update(keys, false);
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
  bindButtons(controls, signal) {
    controls.addEventListener(
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
      controls.addEventListener(kind, this.releasePointer.bind(this), { signal });
    for (const kind of ["keydown", "keyup"])
      controls.addEventListener(kind, this.buttonKey.bind(this), { signal });
    controls.addEventListener("focusout", this.release.bind(this), { signal });
    controls.addEventListener(
      "click",
      (event) => {
        const target = event.target;
        if (!(target instanceof HTMLButtonElement) || !target.dataset.key) return;
        if (event.detail !== 0 && this.lastHold?.key === target.dataset.key) return;
        this.nudge(target.dataset.key, browserLimits.inputNudgeMilliseconds);
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
      if (this.lastHold.milliseconds < browserLimits.inputNudgeMilliseconds)
        this.nudge(key, browserLimits.inputNudgeMilliseconds - this.lastHold.milliseconds);
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

// web/live/schema.ts
var invitationEntries = {
  lease: pipe(string(), regex(browserPatterns.lease)),
  capability: pipe(string(), regex(browserPatterns.capability)),
  model_title: pipe(string(), minLength(1), maxLength(browserLimits.maxTextCharacters)),
  duration_seconds: pipe(number(), finite(), gtValue(0)),
  prompt_kind: picklist(["scene", "edit"]),
  allow_empty_prompt: boolean()
};
var invitationSchema = object(invitationEntries);
function buildInvitation(document2, axes) {
  const identity = { lease: document2.lease, capability: document2.capability };
  const presentation = { modelTitle: document2.model_title, promptKind: document2.prompt_kind };
  return {
    ...identity,
    ...presentation,
    durationSeconds: document2.duration_seconds,
    allowEmptyPrompt: document2.allow_empty_prompt,
    axes
  };
}
var promptEntries = {
  prompt: string(),
  prompt_limit: pipe(number(), safeInteger(), minValue(1))
};
var axisChoicesSchema = pipe(array(string()), includes("idle"));
var axesSchema = record(string(), axisChoicesSchema);
var sceneInvitationSchema = pipe(
  object({
    ...invitationSchema.entries,
    ...promptEntries,
    axes: axesSchema
  }),
  check((document2) => {
    const promptLength = document2.prompt.length;
    const charactersRemaining = document2.prompt_limit - promptLength;
    return Number.isSafeInteger(charactersRemaining) && charactersRemaining >= 0;
  }),
  check((document2) => {
    const hasIndependentAxes = Object.hasOwn(document2.axes, "move_longitudinal");
    const expected = Object.keys(cameraAxes(/* @__PURE__ */ new Set(), hasIndependentAxes));
    if (Object.keys(document2.axes).length !== expected.length) return false;
    for (const name of expected) {
      if (!Object.hasOwn(document2.axes, name)) return false;
    }
    return true;
  }),
  transform((document2) => {
    const invitation = buildInvitation(document2, document2.axes);
    const prompt = { prompt: document2.prompt, promptCharacterLimit: document2.prompt_limit };
    return { ...invitation, ...prompt };
  })
);
var controlsInvitationSchema = pipe(
  object({
    ...invitationSchema.entries,
    ...promptEntries,
    webcam: boolean(),
    pointer: boolean(),
    sound: boolean(),
    audio_prompt: string(),
    audio_prompt_limit: pipe(number(), safeInteger(), minValue(1))
  }),
  check((document2) => {
    if (document2.prompt.length > document2.prompt_limit) return false;
    return document2.audio_prompt.length <= document2.audio_prompt_limit;
  }),
  transform((document2) => {
    const invitation = buildInvitation(document2, {});
    const prompt = { prompt: document2.prompt, promptCharacterLimit: document2.prompt_limit };
    const audioPrompt = {
      audioPrompt: document2.audio_prompt,
      audioPromptCharacterLimit: document2.audio_prompt_limit
    };
    return {
      ...invitation,
      ...prompt,
      ...audioPrompt,
      webcam: document2.webcam,
      pointer: document2.pointer,
      sound: document2.sound
    };
  })
);
var liveStatusSchema = pipe(
  object({
    closed: boolean(),
    termination_confirmed: boolean(),
    failed: boolean(),
    controls_ready: boolean(),
    finishing: boolean(),
    elapsed_seconds: pipe(number(), finite()),
    preview_sequence: pipe(number(), safeInteger()),
    preview: pipe(
      string(),
      maxLength(browserLimits.maxPreviewCharacters),
      regex(browserPatterns.preview)
    )
  }),
  transform((status) => {
    const termination = {
      closed: status.closed,
      terminationConfirmed: status.termination_confirmed,
      failed: status.failed
    };
    const progress = { controlsReady: status.controls_ready, finishing: status.finishing };
    return {
      ...termination,
      ...progress,
      elapsedSeconds: status.elapsed_seconds,
      previewSequence: status.preview_sequence,
      preview: status.preview
    };
  })
);
function parseSceneInvitation(value) {
  const result = safeParse(sceneInvitationSchema, value);
  if (!result.success) return;
  return result.output;
}
function parseControlsInvitation(value) {
  const result = safeParse(controlsInvitationSchema, value);
  if (!result.success) return;
  return result.output;
}
function parseLiveStatus(value) {
  const result = safeParse(liveStatusSchema, value);
  if (!result.success) return;
  return result.output;
}

// web/live/api.ts
async function exchange(fetcher, owner, sequence, axes, end, previewSequence, signal, release = false) {
  const response = await fetcher(browserRoutes.live.exchange, {
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
  const status = parseLiveStatus(await response.json());
  if (!status) throw new Error(translate("live.invalidStatus"));
  return status;
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
    const controls = element("div");
    controls.append(label, this.enable);
    this.view.append(controls, this.video, this.status);
    this.enable.addEventListener("click", () => {
      this.enable.disabled = true;
      const selected = this.select.value;
      void this.start(selected);
    });
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
  async start(selected) {
    try {
      if (!await this.openCamera(selected)) return;
      await this.listCameras();
      if (this.closed) return;
      setText(this.enable, message("camera.select"));
      setText(this.status, message("camera.enabled"));
    } catch (error) {
      this.stopCamera();
      if (this.closed) return;
      const errors = /* @__PURE__ */ new Map([
        ["NotAllowedError", "camera.permissionDenied"],
        ["SecurityError", "camera.browserRequirements"],
        ["NotFoundError", "camera.notFound"],
        ["NotReadableError", "camera.busy"],
        ["OverconstrainedError", "camera.unavailableSelection"]
      ]);
      setText(
        this.status,
        message(
          error instanceof Error ? errors.get(error.name) ?? "camera.accessFailed" : "camera.accessFailed"
        )
      );
    } finally {
      if (!this.closed) this.enable.disabled = false;
    }
  }
  /**
   * Open the selected camera and release any previous stream.
   * @param selected - The selected device ID, or an empty string for the default camera.
   * @returns Whether the camera is ready and the panel is still open.
   */
  async openCamera(selected) {
    if (!navigator.mediaDevices?.getUserMedia) throw new DOMException("", "SecurityError");
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        width: { ideal: browserInput.cameraWidth },
        height: { ideal: browserInput.cameraHeight },
        frameRate: {
          ideal: browserInput.cameraIdealFrameRate,
          max: browserInput.cameraMaxFrameRate
        },
        ...selected ? { deviceId: { exact: selected } } : {}
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
    const options = document.createDocumentFragment();
    for (const device of devices) {
      if (device.kind !== "videoinput") continue;
      const option = element(
        "option",
        device.label || message("camera.number", { number: options.childElementCount + 1 })
      );
      option.value = device.deviceId;
      option.selected = device.deviceId === selected;
      options.appendChild(option);
    }
    this.select.replaceChildren();
    this.select.appendChild(options);
  }
  /**
   * Upload a camera frame without overlapping uploads.
   * @returns Whether a camera frame was available to send.
   */
  async frame() {
    if (this.closed || !this.stream || this.video.readyState < 2) return false;
    for (const track of this.stream.getVideoTracks()) {
      if (track.readyState === "live") continue;
      this.fail(translate("camera.disconnected"));
      return false;
    }
    if (this.upload) {
      await this.upload;
      return true;
    }
    const ratio = Math.min(
      browserInput.cameraWidth / this.video.videoWidth,
      browserInput.cameraHeight / this.video.videoHeight,
      1
    );
    this.canvas.width = Math.max(1, Math.round(this.video.videoWidth * ratio));
    this.canvas.height = Math.max(1, Math.round(this.video.videoHeight * ratio));
    this.upload = this.send();
    try {
      await this.upload;
      return true;
    } finally {
      this.upload = void 0;
    }
  }
  async send() {
    const blob = await new Promise((fulfill) => {
      const context = this.canvas.getContext("2d");
      if (!context) throw new Error(translate("camera.readFailed"));
      context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
      this.canvas.toBlob(fulfill, "image/jpeg", browserInput.cameraJpegQuality);
    });
    if (this.closed || !blob) return;
    const response = await this.fetcher(browserRoutes.live.camera, {
      method: "POST",
      cache: "no-store",
      body: blob,
      signal: AbortSignal.any([
        this.controller.signal,
        AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds)
      ]),
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

// web/live/polling.ts
async function pause(milliseconds, signal) {
  if (signal?.aborted) return;
  await new Promise((fulfill) => {
    const finish = () => {
      clearTimeout(timer);
      signal?.removeEventListener("abort", finish);
      fulfill();
    };
    const timer = setTimeout(finish, milliseconds);
    signal?.addEventListener("abort", finish);
  });
}

// web/live/sound.ts
var SoundControls = class {
  view = element("fieldset");
  prompt = element("textarea");
  apply = button(message("sound.applyPrompt"), "submit");
  pending;
  /**
   * Build the sound prompt controls in their disabled state.
   * @param initialPrompt - The workflow's starting sound prompt.
   * @param promptCharacterLimit - The model's maximum sound prompt length.
   */
  constructor(initialPrompt, promptCharacterLimit) {
    this.prompt.value = initialPrompt;
    this.prompt.maxLength = promptCharacterLimit;
    this.prompt.rows = 2;
    const label = element("label", message("sound.prompt"));
    label.append(this.prompt);
    const form = element("form");
    form.append(label, this.apply, element("p", message("sound.promptNotice")));
    this.view.append(element("legend", message("sound.title")), form);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      this.pending = this.prompt.value;
      this.apply.disabled = true;
    });
    this.setReady(false);
  }
  /**
   * Enable sound input only when the session accepts changes.
   * @param ready - Whether the model accepts live controls.
   */
  setReady(ready) {
    this.prompt.disabled = !ready;
    if (!ready) {
      this.apply.disabled = true;
      return;
    }
    this.apply.disabled = this.pending !== void 0;
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

// web/live/commands.ts
async function sendAction(fetcher, owner, sequence, name, fields) {
  const response = await fetcher(browserRoutes.live.action, {
    method: "POST",
    cache: "no-store",
    signal: AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds),
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" },
    body: JSON.stringify({
      lease: owner.lease,
      capability: owner.capability,
      sequence,
      action: name,
      fields
    })
  });
  if (!response.ok) throw new Error(translate("live.actionRejected"));
}

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
    const resize = new ResizeObserver(this.#place.bind(this));
    resize.observe(image);
    image.addEventListener("blur", this.#place.bind(this), { signal });
    image.addEventListener("focus", this.#place.bind(this), { signal });
    signal.addEventListener("abort", resize.disconnect.bind(resize), { once: true });
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
    this.#marker.hidden = !pointer || this.#image.hidden || document.activeElement !== this.#image;
    if (this.#marker.hidden || !pointer) return;
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
      image.addEventListener(name, this.release.bind(this), { signal });
    image.addEventListener("keydown", this.keydown.bind(this), { signal });
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
    window.addEventListener("blur", this.release.bind(this), { signal });
    document.addEventListener(
      "visibilitychange",
      () => {
        if (document.hidden) this.release();
      },
      { signal }
    );
    signal.addEventListener("abort", this.release.bind(this), { once: true });
  }
  image;
  send;
  pointer = {
    x: browserInput.pointerCenter,
    y: browserInput.pointerCenter,
    active: false
  };
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
      x: Math.max(
        browserInput.pointerMinimum,
        Math.min(browserInput.pointerMaximum, (event.clientX - rect.left) / rect.width)
      ),
      y: Math.max(
        browserInput.pointerMinimum,
        Math.min(browserInput.pointerMaximum, (event.clientY - rect.top) / rect.height)
      ),
      active: true
    };
    this.send(this.pointer);
  }
  /**
   * Move, hold, or release the pointer with the keyboard.
   * @param event - A key pressed while the preview has focus.
   */
  keydown(event) {
    const offsets = /* @__PURE__ */ new Map([
      ["ArrowLeft", [-browserInput.pointerStep, 0]],
      ["ArrowRight", [browserInput.pointerStep, 0]],
      ["ArrowUp", [0, -browserInput.pointerStep]],
      ["ArrowDown", [0, browserInput.pointerStep]],
      [" ", [0, 0]],
      ["Escape", [0, 0]]
    ]);
    const offset = offsets.get(event.key);
    if (!offset) return;
    event.preventDefault();
    event.stopPropagation();
    if (event.key === "Escape") {
      this.release();
      this.image.blur();
      return;
    }
    this.pointer = {
      x: Math.max(
        browserInput.pointerMinimum,
        Math.min(browserInput.pointerMaximum, this.pointer.x + offset[0])
      ),
      y: Math.max(
        browserInput.pointerMinimum,
        Math.min(browserInput.pointerMaximum, this.pointer.y + offset[1])
      ),
      active: event.key === " " || this.pointer.active
    };
    this.send(this.pointer);
  }
};

// web/live/controls.ts
var panels = /* @__PURE__ */ new Set();
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
    this.prompt.maxLength = owner.promptCharacterLimit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.update.disabled = true;
    this.sound = owner.sound ? new SoundControls(owner.audioPrompt, owner.audioPromptCharacterLimit) : void 0;
    this.camera = owner.webcam ? new Webcam(owner, fetcher, this.stop.bind(this)) : void 0;
    if (owner.pointer) new DragInput(this.image, this.abort.signal, this.queuePointer.bind(this));
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
    const label = element(
      "label",
      message(this.owner.promptKind === "edit" ? "live.editPrompt" : "live.scenePrompt")
    );
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
    this.dialog.addEventListener("click", (event) => {
      if (event.target === this.start) {
        this.startRequested = true;
        this.start.disabled = true;
      } else if (event.target === this.end) {
        if (this.finished) this.dialog.close();
        else this.stop();
      }
    });
    this.update.addEventListener("click", () => {
      if (!this.prompt.value.trim() && !this.owner.allowEmptyPrompt) {
        setText(this.status, message("controls.emptyPrompt"));
        return;
      }
      this.pendingPrompt = this.prompt.value;
      this.update.disabled = true;
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
        panels.delete(this.owner.lease);
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
    this.ready = reply.controlsReady && !reply.finishing && !this.ending;
    this.prompt.disabled = !this.ready;
    this.sound?.setReady(this.ready);
    if (this.ready && !wasReady) setText(this.status, message("controls.recording"));
    this.update.disabled = !this.ready || this.pendingPrompt !== void 0;
    if (reply.preview) {
      this.image.src = `data:image/jpeg;base64,${reply.preview}`;
      this.image.hidden = false;
    }
    this.previewSequence = reply.previewSequence;
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
    if (!reply.terminationConfirmed) setText(this.status, message("controls.connectionClosed"));
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
      await sendAction(this.fetcher, this.owner, this.actionSequence++, "start", {});
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
      await sendAction(this.fetcher, this.owner, this.actionSequence++, "prompt", {
        prompt: this.pendingPrompt
      });
      this.pendingPrompt = void 0;
      setText(this.status, message("controls.promptSent"));
    }
    const next = this.pointers.shift();
    if (next) {
      await sendAction(this.fetcher, this.owner, this.actionSequence++, "pointer", next);
      this.pointerPreview?.confirm(next);
    }
    const audioPrompt = this.sound?.takePrompt();
    if (audioPrompt !== void 0) {
      await sendAction(this.fetcher, this.owner, this.actionSequence++, "audio_prompt", {
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
      AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds)
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
      const current4 = await this.refresh();
      if (!current4.closed && !current4.finishing) throw error;
      return current4;
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
        await pause(browserLimits.pollIntervalMilliseconds, this.abort.signal);
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
  const owner = parseControlsInvitation(value);
  if (!owner || panels.has(owner.lease)) return;
  panels.add(owner.lease);
  const panel = new ControlPanel(owner, fetcher);
  panel.show();
}

// web/discovery/pricing.ts
var fastContinueNodeId = "ReactorIncFastContinue";
var nodePricingRules = {
  excludedNodeIds: ["ReactorIncHeliosAddPrompt", "ReactorIncLongLiveAddShot"],
  multipliedDurationInputs: {
    [fastContinueNodeId]: ["clip_seconds", "clip_count"]
  }
};
function formatCreditSummary(model, seconds) {
  const rate = model.creditsPerSecond;
  if (rate === null) return [message("pricing.rateUnavailable")];
  const summary = [message("pricing.rate", { rate })];
  if (!model.observed) {
    summary.push(message("pricing.rateOutdated"));
  } else if (seconds !== void 0) {
    const credits = () => formatNumber(rate * seconds, {
      maximumFractionDigits: 2
    });
    summary.push(
      message("pricing.calculation", {
        seconds,
        rate,
        credits
      })
    );
  }
  return summary;
}

// web/discovery/row.ts
function buildModelRow(model, seconds) {
  const row = element("li");
  row.append(element("h3", model.title), element("code", model.modelSlug));
  const support = model.support === "available" ? message("models.nodesAvailable") : message("models.nodeUnavailable");
  row.append(element("p", support));
  if (model.connectionName)
    row.append(element("p", message("models.connectName", { name: model.connectionName })));
  for (const detail of formatCreditSummary(model, seconds)) row.append(element("p", detail));
  if (model.documentationUrl) {
    const link = element("a", message("models.openGuide"));
    link.href = model.documentationUrl;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    row.append(link);
  } else row.append(element("p", message("models.guideUnavailable")));
  return row;
}

// web/schema.ts
var publicErrorSchema = object({
  error: optional(
    pipe(string(), minLength(1), maxLength(browserLimits.maxErrorCharacters))
  )
});
function parsePublicError(value) {
  const result = safeParse(publicErrorSchema, value);
  if (!result.success) return void 0;
  return result.output.error;
}

// web/discovery/schema.ts
var shortTextSchema = pipe(
  string(),
  minLength(1),
  maxLength(browserLimits.maxTextCharacters)
);
function isRetrievalTime(value) {
  const timestamp = Date.parse(value);
  const parsedDate = new Date(timestamp);
  return Number.isFinite(timestamp) && !Number.isNaN(parsedDate.getTime());
}
var retrievalTimeSchema = nullable(
  pipe(
    string(),
    minLength(1),
    maxLength(browserLimits.maxRetrievalTimeCharacters),
    check(isRetrievalTime)
  )
);
var modelSchema = pipe(
  object({
    key: shortTextSchema,
    name: shortTextSchema,
    title: shortTextSchema,
    connect_name: nullable(shortTextSchema),
    documentation_url: nullable(pipe(string(), regex(browserPatterns.documentation))),
    credits_per_second: nullable(pipe(number(), finite(), minValue(0))),
    observed: boolean(),
    support: picklist(["available", "adapter_required"]),
    node_ids: pipe(
      array(pipe(string(), regex(browserPatterns.nodeId))),
      maxLength(browserLimits.maxModelNodeIds)
    )
  }),
  transform((model) => {
    const identity = { entryKey: model.key, modelSlug: model.name, title: model.title };
    const connection = {
      connectionName: model.connect_name,
      documentationUrl: model.documentation_url,
      creditsPerSecond: model.credits_per_second
    };
    return {
      ...identity,
      ...connection,
      observed: model.observed,
      support: model.support,
      nodeIds: model.node_ids
    };
  })
);
var automaticCheckSchema = pipe(
  object({
    enabled: boolean(),
    running: boolean(),
    interval_hours: pipe(number(), safeInteger(), minValue(1)),
    checked_at: retrievalTimeSchema,
    update_available: nullable(boolean()),
    error: nullable(
      pipe(string(), minLength(1), maxLength(browserLimits.maxErrorCharacters))
    )
  }),
  transform((check2) => {
    const schedule = { intervalHours: check2.interval_hours, checkedAt: check2.checked_at };
    const result = { updateAvailable: check2.update_available, error: check2.error };
    return { enabled: check2.enabled, running: check2.running, ...schedule, ...result };
  })
);
var modelListSchema = pipe(
  object({
    revision: pipe(string(), regex(browserPatterns.revision)),
    retrieved_at: retrievalTimeSchema,
    models: pipe(array(modelSchema), minLength(1), maxLength(browserLimits.maxModels)),
    can_rollback: boolean(),
    mutation_allowed: boolean(),
    automatic_check: optional(automaticCheckSchema)
  }),
  check((document2) => {
    const keys = /* @__PURE__ */ new Set();
    for (const model of document2.models) {
      if (keys.has(model.entryKey)) return false;
      keys.add(model.entryKey);
    }
    return true;
  }),
  transform((document2) => {
    const identity = { revision: document2.revision, retrievedAt: document2.retrieved_at };
    const permissions = {
      canRollback: document2.can_rollback,
      mutationAllowed: document2.mutation_allowed
    };
    return {
      ...identity,
      ...permissions,
      models: document2.models,
      ...document2.automatic_check === void 0 ? {} : { automaticCheck: document2.automatic_check }
    };
  })
);
function parseModelList(value) {
  const result = safeParse(modelListSchema, value);
  if (!result.success) throw new Error(translate("models.invalidResponse"));
  return result.output;
}

// web/discovery/api.ts
function modelRoute(action) {
  if (action === "read") return browserRoutes.models.read;
  if (action === "refresh") return browserRoutes.models.refresh;
  return browserRoutes.models.rollback;
}
function metadataStatus(retrievedAt) {
  if (retrievedAt === null) return message("models.installedList");
  return message("models.lastRefresh", { date: formatDate.bind(null, retrievedAt) });
}
async function requestModels(fetcher, signal, action, revision) {
  const options = {
    method: action === "read" ? "GET" : "POST",
    cache: "no-store",
    credentials: "same-origin",
    signal: AbortSignal.any([
      signal,
      AbortSignal.timeout(browserLimits.discoveryTimeoutMilliseconds)
    ]),
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" }
  };
  if (action === "rollback") options.body = JSON.stringify({ revision });
  let response;
  try {
    response = await fetcher(modelRoute(action), options);
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
    throw new Error(parsePublicError(body) ?? translate("models.requestFailed"));
  }
  return parseModelList(body);
}

// web/discovery/dialog.ts
var current;
function automaticStatus(check2) {
  if (!check2) return "";
  if (!check2.enabled) return message("models.checksOff");
  if (check2.running) return message("models.checkRunning");
  if (check2.error) return check2.error;
  if (check2.updateAvailable === true) return message("models.listChanged");
  if (check2.checkedAt)
    return message("models.checkSchedule", {
      date: formatDate.bind(null, check2.checkedAt),
      hours: check2.intervalHours
    });
  return message("models.checkDue");
}
var ModelDialog = class {
  /**
   * Build the model browser and its optional node filter.
   * @param fetcher - ComfyUI's local API client.
   * @param nodeId - Show models supported by this node, if supplied.
   */
  constructor(fetcher, nodeId) {
    this.fetcher = fetcher;
    this.nodeId = nodeId;
    this.dialog.className = "reactor-dialog reactor-models";
    this.dialog.setAttribute("aria-labelledby", "reactor-models-title");
    const heading = element("h2", message("models.title"));
    heading.id = "reactor-models-title";
    const close = button(message("close"));
    setTextAttribute(close, "aria-label", message("models.close"));
    close.addEventListener("click", this.dialog.close.bind(this.dialog, void 0));
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
    this.search.addEventListener("input", this.updateView.bind(this));
    this.duration.addEventListener("input", this.updateView.bind(this));
    this.dialog.addEventListener("close", this.dispose.bind(this), { once: true });
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
  modelList;
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
      this.updateView();
    });
    this.refresh.disabled = this.rollback.disabled = true;
    this.refresh.addEventListener("click", this.updateModels.bind(this, "refresh"));
    this.rollback.addEventListener("click", this.updateModels.bind(this, "rollback"));
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
  updateView() {
    const query = this.search.value.trim().toLowerCase();
    const nodeId = this.nodeId;
    const seconds = this.duration.validity.valid && this.duration.value !== "" ? this.duration.valueAsNumber : void 0;
    const rows = document.createDocumentFragment();
    for (const model of this.modelList?.models ?? []) {
      if (nodeId && !model.nodeIds.includes(nodeId)) continue;
      const label = `${model.modelSlug} ${model.title} ${model.connectionName ?? ""}`;
      if (label.toLowerCase().includes(query)) rows.appendChild(buildModelRow(model, seconds));
    }
    const visible = rows.childElementCount;
    this.list.replaceChildren();
    this.list.appendChild(rows);
    setText(
      this.count,
      message("models.count", {
        visible,
        total: this.modelList?.models.length ?? 0
      })
    );
  }
  /**
   * Read or update the locally stored model list.
   * @param action - Read, refresh from public sources, or restore the previous list.
   */
  updateModels(action) {
    this.refresh.disabled = this.rollback.disabled = true;
    setText(
      this.status,
      action === "refresh" ? message("models.checking") : message("models.loading")
    );
    void this.requestModels(action);
  }
  /**
   * Apply a model-list response while the dialog is open.
   * @param action - The requested list operation.
   * @returns When the request and action cleanup finish.
   */
  async requestModels(action) {
    try {
      const next = await requestModels(
        this.fetcher,
        this.controller.signal,
        action,
        this.modelList?.revision
      );
      if (this.controller.signal.aborted) return;
      this.displayModels(next, action);
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(this.status, error instanceof Error ? error.message : message("models.loadFailed"));
    } finally {
      this.restoreActions();
    }
  }
  /**
   * Display a model list and the outcome of its requested operation.
   * @param next - The validated local model list.
   * @param action - The completed list operation.
   */
  displayModels(next, action) {
    this.modelList = next;
    setText(this.checked, metadataStatus(next.retrievedAt));
    setText(this.automatic, automaticStatus(next.automaticCheck));
    let status = message("models.loaded");
    if (action === "refresh") status = message("models.refreshed");
    if (action === "rollback") status = message("models.restored");
    setText(this.status, status);
    this.updateView();
  }
  /** Re-enable allowed list changes after the current request finishes. */
  restoreActions() {
    if (this.controller.signal.aborted) return;
    this.refresh.disabled = !this.modelList?.mutationAllowed;
    this.rollback.disabled = !this.modelList?.mutationAllowed || !this.modelList.canRollback;
  }
  /** Show the dialog and read the local model list. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.updateModels("read");
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
function openModels(fetcher, nodeId) {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new ModelDialog(fetcher, nodeId);
  current.show();
}

// web/live/state.ts
var CameraStates = class {
  current;
  pending;
  hasIndependentAxes;
  /**
   * Initialize idle camera movement for the selected model.
   * @param hasIndependentAxes - Whether independent movement axes are supported.
   */
  constructor(hasIndependentAxes) {
    this.hasIndependentAxes = hasIndependentAxes;
    this.current = cameraAxes(/* @__PURE__ */ new Set(), hasIndependentAxes);
    this.pending = [];
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
        if (!Object.values(axes).every(Object.is.bind(null, "idle")))
          this.pending.push({ axes, release: false });
      } else this.pending.push({ axes, release });
    }
    this.current = axes;
  }
  /**
   * Consume a queued camera update or keep the current held movement.
   * @returns The axes and release flag for the next exchange.
   */
  take() {
    const queued = this.pending.shift();
    if (queued) return queued;
    return { axes: this.current, release: false };
  }
};

// web/live/scene.ts
var panels2 = /* @__PURE__ */ new Set();
var ScenePanel = class {
  /**
   * Build camera controls for the invited model.
   * @param owner - The validated camera session invitation.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(owner, fetcher) {
    this.owner = owner;
    this.fetcher = fetcher;
    this.dialog.className = "reactor-dialog reactor-live";
    setTextAttribute(this.dialog, "aria-label", message("live.sceneTitle"));
    this.status.setAttribute("role", "status");
    this.promptStatus.setAttribute("role", "status");
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.promptCharacterLimit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.apply.disabled = true;
    this.surface.className = "reactor-preview";
    this.surface.tabIndex = 0;
    setTextAttribute(this.surface, "aria-label", message("live.movementLabel"));
    setTextAttribute(this.image, "alt", message("live.output"));
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
      const control = button(labels.at(index) ?? key);
      control.dataset.key = key;
      control.disabled = true;
      this.controls.append(control);
    }
    this.states = new CameraStates(Object.hasOwn(owner.axes, "move_longitudinal"));
    const input = new CameraInput(
      this.surface,
      this.controls,
      this.controller.signal,
      this.states.update.bind(this.states)
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
    header.append(element("h2", message("live.sceneTitle")), this.end);
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
        panels2.delete(this.owner.lease);
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
      control.disabled = !result.controlsReady || this.ending;
    this.prompt.disabled = !result.controlsReady || this.ending;
    this.apply.disabled = this.prompt.disabled || this.pendingPrompt !== void 0;
    setText(
      this.elapsed,
      message("live.elapsed", {
        seconds: Math.round(result.elapsedSeconds * 10) / 10
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
        result.controlsReady && result.previewSequence > 0 ? message("live.previewReady") : message("live.waitingVideo")
      );
    }
  }
  /**
   * Show the final session result without implying unconfirmed termination.
   * @param result - The terminal session status.
   */
  finish(result) {
    this.finished = true;
    if (!result.terminationConfirmed) setText(this.status, message("live.unconfirmedEnd"));
    else setText(this.status, result.failed ? message("live.discarded") : message("live.ended"));
  }
  /**
   * Send a queued prompt only while the session accepts controls.
   * @param result - The current session readiness.
   * @returns When the prompt request, if any, finishes.
   */
  async sendPrompt(result) {
    if (!result.controlsReady || result.finishing || this.ending || this.pendingPrompt === void 0)
      return;
    await sendAction(this.fetcher, this.owner, this.actionSequence++, "prompt", {
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
          AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds),
          input.release
        );
        this.previewSequence = result.previewSequence;
        this.display(result);
        if (result.closed) this.finish(result);
        else {
          await this.sendPrompt(result);
          await pause(browserLimits.pollIntervalMilliseconds);
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
      if (this.disposed) panels2.delete(this.owner.lease);
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
function openSceneControls(value, fetcher) {
  const owner = parseSceneInvitation(value);
  if (!owner || panels2.has(owner.lease)) return;
  panels2.add(owner.lease);
  const panel = new ScenePanel(owner, fetcher);
  panel.show();
}

// web/settings/schema.ts
var unknownRecordSchema = record(string(), unknown());
var settingNameSchema = pipe(string(), regex(browserPatterns.settingName));
var settingDefinitionSchema = object({
  label: pipe(string(), minLength(1), maxLength(browserLimits.maxTextCharacters)),
  minimum: pipe(number(), safeInteger()),
  maximum: pipe(number(), safeInteger())
});
var configurationDocumentSchema = object({
  revision: pipe(string(), regex(browserPatterns.revision)),
  mutation_allowed: boolean(),
  credential: object({
    source: picklist(["missing", "saved", "environment"])
  }),
  integer_settings: unknown(),
  settings: unknownRecordSchema,
  credential_limit: unknown()
});
var checkSettingsSchema = object({ catalog_auto_check: boolean() });
var credentialLimitSchema = pipe(number(), safeInteger(), minValue(1));
function parseDefinitions(value) {
  const document2 = safeParse(unknownRecordSchema, value);
  if (!document2.success) throw new Error(translate("settings.invalidResponse"));
  if (!Object.hasOwn(document2.output, "catalog_interval_hours")) {
    throw new Error(translate("settings.incompleteResponse"));
  }
  const definitions = /* @__PURE__ */ new Map();
  for (const [name, raw] of Object.entries(document2.output)) {
    const validName = safeParse(settingNameSchema, name);
    const definition = safeParse(settingDefinitionSchema, raw);
    if (!validName.success || !definition.success || definition.output.minimum > definition.output.maximum) {
      throw new Error(translate("settings.invalidDefinition"));
    }
    definitions.set(name, definition.output);
  }
  return Object.fromEntries(definitions);
}
function parseConfiguration(value) {
  const result = safeParse(configurationDocumentSchema, value);
  if (!result.success) throw new Error(translate("settings.invalidResponse"));
  const document2 = result.output;
  const definitions = parseDefinitions(document2.integer_settings);
  const checkSettings = safeParse(checkSettingsSchema, document2.settings);
  const credentialLimit = safeParse(credentialLimitSchema, document2.credential_limit);
  if (!checkSettings.success || !credentialLimit.success) {
    throw new Error(translate("settings.invalidChecks"));
  }
  const settings = new Map(Object.entries(document2.settings));
  for (const [name, definition] of Object.entries(definitions)) {
    const setting = safeParse(
      pipe(
        number(),
        safeInteger(),
        minValue(definition.minimum),
        maxValue(definition.maximum)
      ),
      settings.get(name)
    );
    if (!setting.success) throw new Error(translate("settings.invalidLimit"));
  }
  return {
    revision: document2.revision,
    credentialSource: document2.credential.source,
    credentialLimit: credentialLimit.output,
    mutationAllowed: document2.mutation_allowed,
    definitions,
    settings: document2.settings
  };
}

// web/settings/api.ts
async function requestConfiguration(fetcher, signal, route = browserRoutes.settings.status, method = "GET", body) {
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
    response = await fetcher(route, options);
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
    throw new Error(parsePublicError(document2) ?? translate("settings.saveFailed"));
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
    close.addEventListener("click", this.dialog.close.bind(this.dialog, void 0));
    const header = element("header");
    header.append(heading, close);
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.reload.addEventListener(
      "click",
      this.updateSettings.bind(this, message("settings.loaded"), void 0, void 0, void 0)
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
    this.dialog.addEventListener("close", this.dispose.bind(this), { once: true });
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
  modelCheckFields = element("fieldset");
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
    clear.addEventListener(
      "click",
      this.updateSettings.bind(
        this,
        message("settings.keyCleared"),
        browserRoutes.settings.credential,
        "DELETE",
        void 0
      )
    );
    const actions = element("div");
    actions.className = "reactor-actions";
    actions.append(button(message("settings.saveKey"), "submit"), clear);
    this.keyFields.append(element("legend", message("settings.credentials")), label, actions);
    form.append(this.keyFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const value = this.key.value;
      this.updateSettings(message("settings.keySaved"), browserRoutes.settings.credential, "PUT", {
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
    const additionalLimits = element("details");
    additionalLimits.append(element("summary", message("settings.advancedLimits")));
    let index = 0;
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      if (name === "catalog_interval_hours") continue;
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
      (index < 2 ? this.limitFields : additionalLimits).append(label);
      index += 1;
    }
    this.limitFields.append(additionalLimits, button(message("settings.saveLimits"), "submit"));
  }
  /**
   * Save only limits changed since the last successful read.
   * @param configuration - The settings and revision currently shown.
   */
  saveLimits(configuration) {
    const changes = /* @__PURE__ */ new Map();
    const settings = new Map(Object.entries(configuration.settings));
    for (const [name, input] of this.inputs) {
      if (input.valueAsNumber !== settings.get(name)) changes.set(name, input.valueAsNumber);
    }
    if (changes.size === 0) {
      setText(this.status, message("settings.noLimitChanges"));
      return;
    }
    this.updateSettings(message("settings.limitsSaved"), browserRoutes.settings.values, "PATCH", {
      revision: configuration.revision,
      settings: Object.fromEntries(changes)
    });
  }
  /**
   * Build the controls for checking public model sources.
   * @returns The automatic model check form.
   */
  modelUpdates() {
    const form = element("form");
    this.modelCheckFields.disabled = true;
    const automaticLabel = element("label", message("settings.automaticChecks"));
    this.automatic.type = "checkbox";
    automaticLabel.prepend(this.automatic);
    const intervalLabel = element("label", message("settings.checkInterval"));
    this.interval.type = "number";
    this.interval.step = "1";
    this.interval.required = true;
    intervalLabel.append(this.interval);
    this.modelCheckFields.append(
      element("legend", message("settings.modelUpdates")),
      automaticLabel,
      intervalLabel,
      element("p", message("settings.checkNotice")),
      button(message("settings.saveChecks"), "submit")
    );
    form.append(this.modelCheckFields);
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
    this.updateSettings(message("settings.checksSaved"), browserRoutes.settings.values, "PATCH", {
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
    const settings = new Map(Object.entries(configuration.settings));
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const input = this.inputs.get(name);
      if (!input) continue;
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.value = String(settings.get(name));
    }
    if (!configuration.mutationAllowed) setText(this.status, message("settings.readOnly"));
  }
  /**
   * Keep settings requests serial and show the server's response.
   * @param success - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   */
  updateSettings(success, route, method, body) {
    if (route === browserRoutes.settings.credential) this.key.value = "";
    this.keyFields.disabled = this.limitFields.disabled = this.modelCheckFields.disabled = true;
    this.reload.disabled = true;
    setText(this.status, message("working"));
    void this.requestSettings(success, route, method, body);
  }
  /**
   * Apply the server response and restore editing after a settings request.
   * @param success - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @returns When the response or error is displayed.
   */
  async requestSettings(success, route, method, body) {
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
        this.keyFields.disabled = this.limitFields.disabled = this.modelCheckFields.disabled = !this.configuration?.mutationAllowed;
        this.reload.disabled = false;
      }
    }
  }
  /** Show the dialog and read local settings. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.updateSettings(message("settings.loaded"));
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

// web/nodes/inputs.ts
function connectedInputs(node) {
  const names = /* @__PURE__ */ new Set();
  for (const input of node.inputs) {
    if (input.link != null) names.add(input.name);
  }
  return names;
}
function inputValues(node) {
  const connected = connectedInputs(node);
  const values = /* @__PURE__ */ new Map();
  for (const widget of node.widgets ?? []) {
    if (!values.has(widget.name) && !connected.has(widget.name))
      values.set(widget.name, widget.value);
  }
  return values;
}

// web/discovery/rate.ts
function requestedSeconds(node) {
  const widgets = inputValues(node);
  function value(name) {
    const raw = widgets.get(name);
    if (typeof raw !== "number" || !Number.isFinite(raw) || raw <= 0) return void 0;
    return raw;
  }
  const factors = node.comfyClass ? nodePricingRules.multipliedDurationInputs[node.comfyClass] : void 0;
  if (factors) {
    const first = value(factors[0]);
    const second = value(factors[1]);
    return first !== void 0 && second !== void 0 ? first * second : void 0;
  }
  return value("duration_seconds");
}
var boundNodes = /* @__PURE__ */ new WeakSet();
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
    close.addEventListener("click", this.dialog.close.bind(this.dialog, void 0));
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
    this.duration.addEventListener("input", this.updateView.bind(this));
    this.dialog.addEventListener("close", this.dispose.bind(this), { once: true });
    this.updateView();
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
      const modelList = await requestModels(fetcher, this.controller.signal, "read");
      if (this.controller.signal.aborted) return;
      this.displayRates(modelList);
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(
          this.status,
          error instanceof Error ? error.message : message("pricing.loadFailed")
        );
    }
  }
  /**
   * Display rates for the selected node and update its calculation.
   * @param modelList - The validated local model list.
   */
  displayRates(modelList) {
    this.models = [];
    for (const model of modelList.models) {
      if (model.nodeIds.includes(this.node.comfyClass ?? "")) this.models.push(model);
    }
    setText(this.status, metadataStatus(modelList.retrievedAt));
    if (!this.models.length) setText(this.status, message("pricing.modelUnavailable"));
    this.updateView();
  }
  /** Validate session time and update every rate calculation. */
  updateView() {
    const valid = this.duration.value !== "" && this.duration.validity.valid;
    setText(
      this.validation,
      valid ? "" : message("pricing.timeRange", {
        maximum: browserLimits.maxCalculatorSeconds
      })
    );
    this.rates.replaceChildren();
    for (const model of this.models) {
      this.rates.append(element("h3", model.title));
      const seconds = valid ? this.duration.valueAsNumber : void 0;
      for (const detail of formatCreditSummary(model, seconds))
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
  if (!id?.startsWith("ReactorInc") || nodePricingRules.excludedNodeIds.includes(id)) return;
  if (boundNodes.has(node)) return;
  boundNodes.add(node);
  const widget = node.addWidget(
    "button",
    translate("pricing.viewRate"),
    "",
    openCreditRate.bind(null, node, fetcher),
    {
      serialize: false
    }
  );
  widget.serialize = false;
  const refreshLabel = () => {
    const label = translate("pricing.viewRate");
    if (widget.label !== label) {
      widget.label = label;
      node.graph?.setDirtyCanvas(true);
    }
  };
  refreshLabel();
  languageEvents.addEventListener("change", refreshLabel);
  const removed = node.onRemoved?.bind(node);
  node.onRemoved = function(...args) {
    languageEvents.removeEventListener("change", refreshLabel);
    boundNodes.delete(node);
    if (current3?.node === node) current3.dialog.close();
    removed?.apply(this, args);
  };
}

// web/extension.ts
app2.registerExtension({
  name: "reactor.inc.configuration",
  init: initializeLanguage,
  setup: () => {
    app2.ui.settings.addEventListener("Comfy.Locale.change", refreshText);
    app2.ui.settings.addEventListener(
      "Comfy.Locale.change",
      languageEvents.dispatchEvent.bind(languageEvents, new Event("change"))
    );
    const stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = new URL("./extension.css", import.meta.url).href;
    const stylesheets = /* @__PURE__ */ new Set();
    for (const link of document.querySelectorAll("link[rel=stylesheet]")) {
      stylesheets.add(link.getAttribute("href"));
    }
    if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
    api3.addCustomEventListener("reactor-inc.live", (event) => {
      if (event instanceof CustomEvent) {
        openSceneControls(event.detail, requestLocal);
      }
    });
    api3.addCustomEventListener("reactor-inc.controls", (event) => {
      if (event instanceof CustomEvent) openControls(event.detail, requestLocal);
    });
  },
  nodeCreated: (node) => {
    if (!node.comfyClass?.startsWith("ReactorInc")) return;
    bindCreditRate(node, requestLocal);
  },
  commands: [
    {
      id: "ReactorInc.OpenSettings",
      label: translate("settings.title"),
      function: openSettings.bind(null, requestLocal)
    },
    {
      id: "ReactorInc.OpenCatalog",
      label: translate("models.title"),
      function: openModels.bind(null, requestLocal, void 0)
    }
  ],
  menuCommands: [
    {
      path: ["Extensions", "Reactor"],
      commands: ["ReactorInc.OpenSettings", "ReactorInc.OpenCatalog"]
    }
  ]
});
