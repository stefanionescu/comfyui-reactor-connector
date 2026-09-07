import { build } from 'esbuild';
import { basename } from 'node:path';
import { mkdir, readFile, writeFile } from 'node:fs/promises';

const result = await build({
  entryPoints: ['web/extension.ts'],
  outfile: 'web/dist/main.js',
  bundle: true,
  write: false,
  platform: 'browser',
  format: 'esm',
  target: 'es2022',
  external: ['../../scripts/app.js', '../../scripts/api.js'],
  charset: 'utf8',
  legalComments: 'inline',
});
const outputs = new Map(result.outputFiles.map((output) => [basename(output.path), output]));
for (const filename of ['main.js', 'main.css']) {
  const output = outputs.get(filename);
  if (!output) throw new Error(`The frontend build did not produce ${filename}.`);
  const destination = `web/dist/${filename}`;
  if (process.argv.includes('--check')) {
    const actual = await readFile(destination, 'utf8').catch(() => '');
    if (actual !== output.text) {
      console.error(`Rebuild ${filename} with mise run frontend:build.`);
      process.exitCode = 1;
    }
  } else {
    await mkdir('web/dist', { recursive: true });
    await writeFile(destination, output.contents);
  }
}
