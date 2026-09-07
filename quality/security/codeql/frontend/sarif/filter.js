#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { readJsonFile, requireArray, requireDictionary, requireString } from '#shared/json.js';

const sarifPath = process.argv[2];
const falsePositivePath = process.argv[3];

if (!sarifPath || !falsePositivePath) {
  console.error('Usage: bun filter.js <sarif-path> <false-positive-path>');
  process.exit(1);
}

const sarif = requireDictionary(readJsonFile(sarifPath, 'SARIF'), 'SARIF');
const falsePositiveConfig = requireDictionary(
  readJsonFile(falsePositivePath, 'CodeQL false-positive config'),
  'CodeQL false-positive config',
);
const ignoredEntries = requireArray(falsePositiveConfig.ignored, 'ignored');

const ignored = new Set(
  ignoredEntries.map((entry) => {
    const ignoredEntry = requireDictionary(entry, 'ignored entry');
    const ruleId = requireString(ignoredEntry.ruleId, 'ruleId');
    const uri = requireString(ignoredEntry.uri, 'uri');
    return `${ruleId}::${uri}`;
  }),
);

let filteredCount = 0;

const runs = requireArray(sarif.runs, 'runs');
if (runs.length === 0) throw new Error('CodeQL returned no analysis runs.');
let remainingCount = 0;

for (const run of runs) {
  const currentRun = requireDictionary(run, 'run');
  const invocations = requireArray(currentRun.invocations ?? [], 'invocations');
  for (const invocation of invocations) {
    if (requireDictionary(invocation, 'invocation').executionSuccessful === false) {
      throw new Error('CodeQL did not complete its analysis.');
    }
  }
  const originalResults = requireArray(currentRun.results, 'results');
  currentRun.results = originalResults.filter((result) => {
    const currentResult = requireDictionary(result, 'result');
    const locations = requireArray(currentResult.locations ?? [], 'locations');
    const firstLocation = requireDictionary(locations[0] ?? {}, 'location');
    const physicalLocation = requireDictionary(
      firstLocation.physicalLocation ?? {},
      'physicalLocation',
    );
    const artifactLocation = requireDictionary(
      physicalLocation.artifactLocation ?? {},
      'artifactLocation',
    );
    const uri = artifactLocation.uri ? requireString(artifactLocation.uri, 'uri') : '';
    const ruleId = requireString(currentResult.ruleId, 'ruleId');
    const key = uri ? `${ruleId}::${uri}` : '';
    const isIgnored = ignored.has(key);

    if (isIgnored) {
      filteredCount += 1;
    }

    return !isIgnored;
  });
  remainingCount += currentRun.results.length;
}

fs.writeFileSync(sarifPath, `${JSON.stringify(sarif)}\n`);

const relativeFalsePositivePath =
  path.relative(process.cwd(), falsePositivePath) || falsePositivePath;
console.log(
  `codeql filtered ${filteredCount} false positive(s) using ${relativeFalsePositivePath}`,
);

if (remainingCount > 0) {
  console.error(
    `CodeQL found ${remainingCount} unreviewed findings. Review the private SARIF report.`,
  );
  process.exitCode = 1;
}
