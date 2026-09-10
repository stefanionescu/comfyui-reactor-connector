import './styles/interface.css';
import { api } from '../../scripts/api.js';
import { app } from '../../scripts/app.js';
import { requestLocal } from '#web/http.ts';
import { refreshText } from '#web/localization.ts';
import { openControls } from '#web/live/controls.ts';
import { openModels } from '#web/discovery/dialog.ts';
import { openSceneControls } from '#web/live/scene.ts';
import { openSettings } from '#web/settings/dialog.ts';
import { bindCreditRate } from '#web/discovery/rate.ts';
import { HELP_COMMAND, helpCommands, openNodeHelp } from '#web/help/command.ts';
import { configureNodeWidgets, refreshWidgetLabels } from '#web/nodes/labels.ts';
import { translate, initializeLanguage, languageEvents } from '#web/language.ts';

app.registerExtension({
  name: 'reactor.inc.configuration',
  init: initializeLanguage,
  setup: () => {
    app.ui.settings.addEventListener('Comfy.Locale.change', () => {
      refreshText();
      refreshWidgetLabels();
      languageEvents.dispatchEvent(new Event('change'));
    });
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = new URL('./main.css', import.meta.url).href;
    const stylesheets = new Set();
    for (const link of document.querySelectorAll('link[rel=stylesheet]')) {
      stylesheets.add(link.getAttribute('href'));
    }
    if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);

    api.addEventListener('reactor-inc.live', (event) => {
      if (event instanceof CustomEvent) {
        openSceneControls(event.detail, requestLocal);
      }
    });

    api.addEventListener('reactor-inc.controls', (event) => {
      if (event instanceof CustomEvent) openControls(event.detail, requestLocal);
    });
  },

  nodeCreated: (node) => {
    if (!node.comfyClass?.startsWith('ReactorInc')) return;
    configureNodeWidgets(node);
    const changed = node.onConnectionsChange;
    node.onConnectionsChange = function (...args: unknown[]) {
      if (changed) changed.apply(this, args);
      configureNodeWidgets(node);
    };
    bindCreditRate(node, requestLocal);
  },
  loadedGraphNode: configureNodeWidgets,
  getSelectionToolboxCommands: helpCommands,
  commands: [
    {
      id: HELP_COMMAND,
      label: translate('help.label'),
      icon: 'pi pi-question-circle',
      function: openNodeHelp,
    },
    {
      id: 'ReactorInc.OpenSettings',
      label: translate('settings.title'),
      function: openSettings.bind(null, requestLocal),
    },
    {
      id: 'ReactorInc.OpenCatalog',
      label: translate('models.title'),
      function: openModels.bind(null, requestLocal, undefined),
    },
  ],
  menuCommands: [
    {
      path: ['Extensions', 'Reactor'],
      commands: ['ReactorInc.OpenSettings', 'ReactorInc.OpenCatalog'],
    },
  ],
});
