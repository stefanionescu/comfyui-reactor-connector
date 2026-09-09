var path = require('node:path');

module.exports = {
  resolve: {
    alias: {
      // ComfyUI supplies these modules; the graph follows their declared host boundary.
      '../../scripts/app.js$': path.resolve(process.cwd(), 'web/host.d.ts'),
      '../../scripts/api.js$': path.resolve(process.cwd(), 'web/host.d.ts'),
      '#config': path.resolve(process.cwd(), 'config'),
      '#web': path.resolve(process.cwd(), 'web'),
    },
    extensions: ['.ts', '.js', '.mjs', '.json'],
  },
};
