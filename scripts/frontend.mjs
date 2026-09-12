import { build } from 'esbuild';
import { basename } from 'node:path';
import { mkdir, readFile, writeFile } from 'node:fs/promises';

const result = await build({
  entryPoints: ['web/scripts/extension.ts'],
  outfile: 'web/extension.js',
  bundle: true,
  write: false,
  platform: 'browser',
  format: 'esm',
  target: 'es2022',
  external: ['../../scripts/app.js', '../../scripts/api.js'],
  charset: 'utf8',
  legalComments: 'inline',
});
const outputs = new Map();
for (const output of result.outputFiles) {
  outputs.set(basename(output.path), output);
}
for (const filename of ['extension.js', 'extension.css']) {
  const output = outputs.get(filename);
  if (!output) throw new Error(`The frontend build did not produce ${filename}.`);
  const destination = `web/${filename}`;
  if (process.argv.includes('--check')) {
    let actual;
    try {
      // eslint-disable-next-line security/detect-non-literal-fs-filename -- The destination is web/extension.js or web/extension.css from the literal filename list above.
      actual = await readFile(destination, 'utf8');
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      console.error(`Build ${filename} with mise run comfy:frontend:build.`);
      process.exitCode = 1;
      continue;
    }
    if (actual !== output.text) {
      console.error(`Rebuild ${filename} with mise run comfy:frontend:build.`);
      process.exitCode = 1;
    }
  } else {
    await mkdir('web', { recursive: true });
    // eslint-disable-next-line security/detect-non-literal-fs-filename -- Write only extension.js or extension.css under the fixed web directory.
    await writeFile(destination, output.contents);
  }
}
