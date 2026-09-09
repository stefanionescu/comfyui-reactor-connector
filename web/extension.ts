import './styles.css';
import { api } from '../../scripts/api.js';
import { app } from '../../scripts/app.js';
import { openLive } from '#web/live/dialog.ts';
import { openControls } from '#web/live/controls.ts';
import { openModels } from '#web/discovery/dialog.ts';
import { openSettings } from '#web/settings/dialog.ts';
import { bindCreditRate } from '#web/discovery/rate.ts';
import { translate, loadLanguage } from '#web/language.ts';
import { bindNodeWidgets, configureNodeWidgets } from '#web/nodes/labels.ts';
import { HELP_COMMAND, helpCommands, openNodeHelp } from '#web/help/command.ts';

/**
 * Send the selected ComfyUI language with local connector requests.
 * @param route - The local connector endpoint.
 * @param options - The request's existing method, headers, and body.
 * @returns The local ComfyUI response.
 */
function requestLocal(route: string, options: RequestInit): Promise<Response> {
  const selected = app.extensionManager.setting.get('Comfy.Locale');
  const headers = new Headers(options.headers);
  headers.set('Accept-Language', typeof selected === 'string' ? selected : 'en');
  return api.fetchApi(route, { ...options, headers });
}

const stylesheet = document.createElement('link');
stylesheet.rel = 'stylesheet';
stylesheet.href = new URL('./main.css', import.meta.url).href;
document.head.append(stylesheet);

api.addEventListener('reactor-inc.live', (event) => {
  if (event instanceof CustomEvent) {
    openLive(event.detail, requestLocal);
  }
});

api.addEventListener('reactor-inc.controls', (event) => {
  if (event instanceof CustomEvent) openControls(event.detail, requestLocal);
});

app.registerExtension({
  name: 'reactor.inc.configuration',
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
      label: translate('help'),
      icon: 'pi pi-question-circle',
      function: openNodeHelp,
    },
    {
      id: 'ReactorInc.OpenSettings',
      label: translate('settings.title'),
      function: () => openSettings(requestLocal),
    },
    {
      id: 'ReactorInc.OpenCatalog',
      label: translate('models.title'),
      function: () => openModels(requestLocal),
    },
  ],
  menuCommands: [
    {
      path: ['Extensions', 'Reactor'],
      commands: ['ReactorInc.OpenSettings', 'ReactorInc.OpenCatalog'],
    },
  ],
});
