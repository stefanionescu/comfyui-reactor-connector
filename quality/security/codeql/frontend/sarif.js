#!/usr/bin/env node

import { CODEQL_REVIEWED_FINDINGS } from '#config/security/codeql/frontend/paths.js';
import { readJsonFile, requireArray, requireDictionary, requireString } from '#shared/json.js';

const sarifPath = process.argv[2];
if (!sarifPath || process.argv.length !== 3) {
  console.error('Usage: bun sarif.js <sarif-path>');
  process.exit(2);
}

const reviewed = requireArray(
  readJsonFile(CODEQL_REVIEWED_FINDINGS, 'Reviewed CodeQL findings'),
  'reviewed findings',
).map((entry) => {
  const finding = requireDictionary(entry, 'reviewed finding');
  requireString(finding.rule, 'rule');
  requireString(finding.path, 'path');
  requireString(finding.lineHash, 'lineHash');
  requireString(finding.columnHash, 'columnHash');
  requireString(finding.reason, 'reason');
  return finding;
});
const matched = new Set();
const sarif = requireDictionary(readJsonFile(sarifPath, 'SARIF'), 'SARIF');
const runs = requireArray(sarif.runs, 'runs');
if (runs.length === 0) throw new Error('CodeQL returned no analysis runs.');
let findingCount = 0;

for (const run of runs) {
  const currentRun = requireDictionary(run, 'run');
  const invocations = requireArray(currentRun.invocations ?? [], 'invocations');
  for (const invocation of invocations) {
    if (requireDictionary(invocation, 'invocation').executionSuccessful === false) {
      throw new Error('CodeQL did not complete its analysis.');
    }
  }
  for (const result of requireArray(currentRun.results, 'results')) {
    const finding = requireDictionary(result, 'result');
    const rule = requireString(finding.ruleId, 'ruleId');
    const fingerprints = requireDictionary(finding.partialFingerprints ?? {}, 'fingerprints');
    const locations = requireArray(finding.locations ?? [], 'locations');
    const location = requireDictionary(locations[0] ?? {}, 'location');
    const physical = requireDictionary(location.physicalLocation ?? {}, 'physicalLocation');
    const artifact = requireDictionary(physical.artifactLocation ?? {}, 'artifactLocation');
    const accepted = reviewed.find(
      (entry) =>
        entry.rule === rule &&
        entry.path === artifact.uri &&
        entry.lineHash === fingerprints.primaryLocationLineHash &&
        entry.columnHash === fingerprints.primaryLocationStartColumnFingerprint,
    );
    if (accepted && !matched.has(accepted)) matched.add(accepted);
    else findingCount += 1;
  }
}

if (matched.size !== reviewed.length) {
  console.error('Reviewed CodeQL findings no longer match the report. Review the changed results.');
  process.exitCode = 1;
}
console.log(`CodeQL matched ${matched.size} exactly reviewed dependency findings.`);
if (findingCount > 0) {
  console.error(`CodeQL found ${findingCount} findings. Review the private SARIF report.`);
  process.exitCode = 1;
} else {
  console.log('CodeQL reported no unreviewed findings.');
}
