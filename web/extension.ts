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
import { translate, initializeLanguage, languageEvents } from '#web/language.ts';

app.registerExtension({
  name: 'reactor.inc.configuration',
  init: initializeLanguage,
  setup: () => {
    app.ui.settings.addEventListener('Comfy.Locale.change', refreshText);
    app.ui.settings.addEventListener(
      'Comfy.Locale.change',
      languageEvents.dispatchEvent.bind(languageEvents, new Event('change')),
    );
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = new URL('./extension.css', import.meta.url).href;
    const stylesheets = new Set();
    for (const link of document.querySelectorAll('link[rel=stylesheet]')) {
      stylesheets.add(link.getAttribute('href'));
    }
    if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);

    api.addCustomEventListener('reactor-inc.live', (event) => {
      if (event instanceof CustomEvent) {
        openSceneControls(event.detail, requestLocal);
      }
    });

    api.addCustomEventListener('reactor-inc.controls', (event) => {
      if (event instanceof CustomEvent) openControls(event.detail, requestLocal);
    });
  },

  nodeCreated: (node) => {
    if (!node.comfyClass?.startsWith('ReactorInc')) return;
    bindCreditRate(node, requestLocal);
  },
  commands: [
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
