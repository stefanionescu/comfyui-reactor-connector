import { app } from '../../scripts/app.js';

/** The text the connector's panels show, addressed by dotted key. */
const TEXT = {
  camera: {
    accessFailed: 'Camera access failed. Choose a camera and try again.',
    browserRequirements: 'Camera access needs localhost or HTTPS and a supported browser.',
    busy: 'Close other apps using the camera, then try again.',
    default: 'Default camera',
    disconnected: 'The camera disconnected. The session is ending.',
    enable: 'Enable Camera',
    enabled: 'Camera On',
    label: 'Camera',
    notFound: 'Connect a camera, then try again.',
    number: 'Camera {number}',
    permissionDenied: 'Allow camera access in the app or browser settings, then try again.',
    preview: 'Webcam preview',
    readFailed: 'Camera frames could not be read.',
    select: 'Switch Camera',
    unavailableSelection: 'The selected camera is unavailable. Choose another camera.',
    uploadFailed: 'Camera frames could not reach the session.',
    microphone: 'Microphone Off',
  },
  cancel: 'Cancel',
  close: 'Close',
  controls: {
    cameraRequired: 'Enable a camera before starting.',
    chooseInput: 'Choose your input, then start within 60 seconds.',
    connecting: 'Connecting to Reactor...',
    connectionClosed: 'Connection closed. Check Reactor session status before starting again.',
    connectionEnded: 'The live connection ended.',
    dragInstructions:
      'Drag on the output to steer the subject. Release to stop. Focus the picture and use arrow keys to position the pointer. Hold Space to hold it; release Space or press Escape to release it.',
    emptyPrompt: 'Enter a prompt before applying it.',
    pointerRateExceeded: 'Pointer input arrived too quickly. The session is ending.',
    promptSent: 'Prompt sent.',
    recording: 'Recording. Live controls are ready.',
    recordingNotStarted: 'Recording did not start. Close this panel and run the workflow again.',
    soundSent: 'Audio prompt sent.',
    start: 'Start Session',
    title: '{model}: Live Controls (Reactor)',
  },
  live: {
    actionRejected: 'The live action was not accepted. The session is ending.',
    applyPrompt: 'Apply Prompt',
    back: 'Move Backward',
    connectingPanel: 'Connecting the live panel...',
    connectionLost:
      'The live connection was lost. The connector will ask Reactor to stop after five seconds without a browser connection. Check Reactor Usage to confirm the session has ended before another run.',
    discarded: 'Session ended without saving a video.',
    duration: '{seconds} seconds of video',
    elapsed: 'Elapsed: {seconds} s',
    emptyScenePrompt: 'Enter a scene prompt before applying it.',
    endSession: 'End Session',
    ended: 'Session ended.',
    ending: 'Ending the session...',
    forward: 'Move Forward',
    help: 'Help',
    invalidStatus: 'The live panel received an invalid status.',
    lookDown: 'Look Down',
    lookLeft: 'Look Left',
    lookRight: 'Look Right',
    lookUp: 'Look Up',
    moveLeft: 'Move Left',
    moveRight: 'Move Right',
    movementInstructions:
      'Click the picture, then use W A S D to move and arrow keys to turn. Click a button for a brief movement, or hold it to keep moving. Escape stops camera movement.',
    movementLabel: 'Live view. W A S D moves. Arrow keys turn. Escape stops camera movement.',
    output: 'Generated video preview',
    previewNotice: 'The preview has no sound. The saved video can have a higher frame rate.',
    previewReady: 'Live preview. Controls are active.',
    promptNotice: 'Prompt changes affect later frames. The starting image stays fixed.',
    promptSent: 'Prompt sent.',
    recordingNotice: 'End Session stops early and discards the unfinished video.',
    scenePrompt: 'Scene Prompt',
    unconfirmedEnd:
      'Reactor has not confirmed that the session ended. Wait for its time limit before another run.',
    unreachable: 'Live controls could not reach their session.',
    waitingVideo: 'Waiting for model video...',
    sceneTitle: '{model}: Scene Controls (Reactor)',
    editPrompt: 'Edit Prompt',
  },
  pointer: {
    held: 'Pointer held.',
    position: ' {x}% across, {y}% down.',
    released: 'Pointer released.',
    stopped: 'Pointer controls stopped.',
  },
  settings: {
    clearKey: 'Clear Saved Key',
    close: 'Close Reactor settings',
    credentialLabel: 'Reactor API key',
    credentials: 'Credentials',
    environmentKey: 'Set by REACTOR_API_KEY',
    invalidDefinition: 'ComfyUI returned an invalid Reactor setting definition.',
    invalidLimit: 'ComfyUI returned an invalid Reactor limit.',
    invalidResponse: 'ComfyUI returned an invalid Reactor settings response.',
    keyCleared: 'Saved key cleared.',
    keyNotice:
      'Add a Reactor key to use the extension. Your key stays on your ComfyUI server and is sent only to Reactor.',
    keySaved: 'Key saved.',
    limits: 'Session limits',
    limitsSaved: 'Limits saved.',
    reread: 'Settings loaded.',
    reading: 'Loading settings...',
    noLimitChanges: 'No limit changes to save.',
    readOnly: "Changes are disabled in this host's multi-user mode.",
    reload: 'Reload Settings',
    saveFailed: 'ComfyUI could not save Reactor settings.',
    saveKey: 'Save Key',
    saveLimits: 'Save Limits',
    savedKey: 'Saved key',
    title: 'Reactor Settings',
    unreachable: 'Cannot reach Reactor settings. Check ComfyUI and try again.',
    unreadableResponse: 'ComfyUI returned an unreadable Reactor settings response.',
    updateFailed: 'Reactor settings could not be saved.',
    readFailed: 'ComfyUI could not read Reactor settings.',
    removeFailed: 'ComfyUI could not clear the saved Reactor key.',
    menu: 'Reactor settings',
  },
  sound: {
    applyPrompt: 'Apply Audio Prompt',
    prompt: 'Audio Prompt',
    promptNotice: 'Describe the sound briefly. Leave blank to use the picture alone.',
  },
  working: 'Working...',
} as const;

/** Labels of the server's execution limits, keyed by setting name. */
export const LIMIT_LABELS = new Map<string, string>([
  ['max_session_seconds', 'maximum session duration (seconds)'],
  ['max_upload_megabytes', 'maximum upload size (MiB)'],
]);

type MessagePaths<Messages> = {
  [Key in keyof Messages & string]: Messages[Key] extends string
    ? Key
    : `${Key}.${MessagePaths<Messages[Key]>}`;
}[keyof Messages & string];

export type MessageKey = MessagePaths<typeof TEXT>;
type MessageValues = Record<string, string | number>;

/**
 * Read one message and insert its named values as plain text.
 * @param key - A dotted path into the connector text.
 * @param values - Named values inserted for `{name}` placeholders.
 * @returns The rendered message.
 */
export function message(key: MessageKey, values: MessageValues = {}): string {
  let value: unknown = TEXT;
  for (const part of key.split('.')) {
    // eslint-disable-next-line security/detect-object-injection -- The key is a literal path checked by its type.
    value = (value as Record<string, unknown>)[part];
  }
  return String(value).replaceAll(/\{(\w+)\}/g, (placeholder, name: string) => {
    if (!Object.hasOwn(values, name)) return placeholder;
    // eslint-disable-next-line security/detect-object-injection -- Interpolation reads an own property of the caller's display values and inserts it as plain text.
    const inserted = values[name];
    return typeof inserted === 'number'
      ? new Intl.NumberFormat(selectedLocale()).format(inserted)
      : String(inserted);
  });
}

/**
 * Replace an element's text.
 * @param target - The element whose text the connector owns.
 * @param content - The new text.
 */
export function setText(target: HTMLElement, content: string): void {
  // reason: The content becomes a Text node, never parsed HTML.
  // bearer:disable javascript_lang_dangerous_insert_html
  target.replaceChildren(document.createTextNode(content));
}

/**
 * Read the active locale for number and date display.
 * @returns A valid language tag, or English when the setting is invalid.
 */
export function selectedLocale(): string {
  const value = app.extensionManager.setting.get('Comfy.Locale');
  try {
    return (
      Intl.getCanonicalLocales(typeof value === 'string' ? value.replaceAll('_', '-') : 'en')[0] ??
      'en'
    );
  } catch {
    return 'en';
  }
}
