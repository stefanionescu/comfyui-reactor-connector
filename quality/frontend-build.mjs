import { readFile, writeFile } from "node:fs/promises";
import { build } from "esbuild";

const result = await build({
  entryPoints: ["frontend/extension.ts"],
  bundle: true,
  write: false,
  platform: "browser",
  format: "esm",
  target: "es2022",
  external: ["../../scripts/app.js", "../../scripts/api.js"],
  charset: "utf8",
  legalComments: "inline",
});
const output = result.outputFiles[0];
if (!output) throw new Error("The frontend build produced no output.");
const expected = `// Generated from frontend source. Run mise run frontend:build.\n${output.text}`;
if (process.argv.includes("--check")) {
  const actual = await readFile("web/main.js", "utf8").catch(() => "");
  if (actual !== expected) {
    console.error("Rebuild frontend assets with mise run frontend:build.");
    process.exitCode = 1;
  }
} else {
  await writeFile("web/main.js", expected);
}
