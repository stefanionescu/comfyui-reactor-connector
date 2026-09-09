import fs from 'node:fs';
import path from 'node:path';
import { visibleFiles } from '#shared/files.js';
import { validateName } from '#shared/naming/validate-name.js';
import { collectJavaScriptNames } from '#repository/naming/extractors/javascript.js';

import {
  collectDirectoryNames,
  collectFileNames,
  languageForPath,
} from '#repository/naming/extractors/files.js';
import {
  repoRoot,
  isPathExcluded,
  nameRulesForEntry,
  pathHasScope,
  termEntriesForPath,
} from '#repository/naming/policy/policy.js';

function addViolation(violations, seen, violation) {
  const key = [violation.file, violation.line, violation.name, violation.kind, violation.rule].join(
    ':',
  );
  if (seen.has(key)) {
    return;
  }

  seen.add(key);
  violations.push(violation);
}

function compareViolations(left, right) {
  if (left.file !== right.file) {
    return left.file.localeCompare(right.file);
  }
  if (left.line !== right.line) {
    return left.line - right.line;
  }
  return left.message.localeCompare(right.message);
}

function readTrackedFile(relativePath) {
  // reason: The caller supplies only Git-listed regular files after symbolic-link checks.
  // bearer:disable javascript_lang_path_traversal
  const absolutePath = path.join(repoRoot, relativePath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`tracked file is missing: ${relativePath}`);
  }

  return fs.readFileSync(absolutePath, 'utf8');
}

function sourceNamingEntries(relativePath, sourceText, language) {
  if (language === 'javascript') {
    return collectJavaScriptNames(relativePath, sourceText, language);
  }

  return [];
}

function namingEntriesForFile(relativePath, policy) {
  if (isPathExcluded(relativePath, policy)) {
    return [];
  }

  const sourceText = readTrackedFile(relativePath);
  const language = languageForPath(relativePath, sourceText);
  if (language !== 'javascript') return [];
  const fileNames = [
    ...collectDirectoryNames(relativePath),
    ...collectFileNames(relativePath, sourceText),
  ];
  if (!language) {
    return fileNames;
  }

  return [...fileNames, ...sourceNamingEntries(relativePath, sourceText, language)];
}

function stripStructuralPrefixes(name, regexes) {
  let strippedName = name;
  for (const regex of regexes) {
    strippedName = strippedName.replace(regex, '');
  }
  return strippedName;
}

function checkedEntryForRules(entry, nameRules) {
  const caseRule = nameRules.findLast((rule) => rule.caseNames.length > 0);
  const structuralPrefixRegexes = nameRules.flatMap((rule) => rule.structuralPrefixRegexes);
  if (!caseRule && structuralPrefixRegexes.length === 0) {
    return entry;
  }

  return {
    ...entry,
    caseName: stripStructuralPrefixes(entry.caseName ?? entry.name, structuralPrefixRegexes),
    digitsName: stripStructuralPrefixes(entry.digitsName ?? entry.name, structuralPrefixRegexes),
    limitName: stripStructuralPrefixes(entry.limitName ?? entry.name, structuralPrefixRegexes),
    partsName: stripStructuralPrefixes(entry.partsName ?? entry.name, structuralPrefixRegexes),
    ...(caseRule ? { caseNames: caseRule.caseNames } : {}),
  };
}

function addNamingEntryViolations(policy, relativePath, entry, violations, seen) {
  const nameRules = nameRulesForEntry(policy, relativePath, entry);
  if (nameRules.some((rule) => rule.exclude)) return;
  const checkedEntry = checkedEntryForRules(entry, nameRules);
  const profile = policy.languages?.[entry.language];
  const termEntries = termEntriesForPath(policy, relativePath);
  for (const violation of validateName(checkedEntry, profile, termEntries, policy.global)) {
    addViolation(violations, seen, violation);
  }
}

/**
 * Check names in public source files within the selected repository scope.
 * @param scope - Repository scope selected by the command.
 * @param policy - Parsed naming rules and boundary exceptions.
 * @returns Naming violations sorted by path and source location.
 */
function analyzeNaming(scope, policy) {
  const violations = [];
  const seen = new Set();
  const trackedFiles = visibleFiles(repoRoot);

  for (const relativePath of trackedFiles) {
    if (!pathHasScope(relativePath, scope)) {
      continue;
    }

    const displayPath = relativePath;
    for (const entry of namingEntriesForFile(displayPath, policy)) {
      addNamingEntryViolations(policy, displayPath, entry, violations, seen);
    }
  }

  return violations.sort(compareViolations);
}

export { analyzeNaming };
