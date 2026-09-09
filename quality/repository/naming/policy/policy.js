import fs from 'node:fs';
import path from 'node:path';
import { NAMING_POLICY_PATH } from '#config/paths.js';
import { GENERATED_SOURCE_FILES } from '#config/files.js';
import { buildTermEntries } from '#shared/naming/identifier-parts.js';
import { SCOPE_PREFIXES, VALID_SCOPES, VALID_SCOPE_USAGE } from '#config/repository.js';

const repoRoot = process.cwd();
const policyPath = path.join(repoRoot, NAMING_POLICY_PATH);
const usage = `Usage: node quality/repository/naming/check.js [--scope ${VALID_SCOPE_USAGE}]`;
const generatedFiles = new Set(GENERATED_SOURCE_FILES);

function toPosix(value) {
  if (typeof value !== 'string') {
    throw new TypeError(`path must be a string, received ${typeof value}`);
  }

  return value.replaceAll('\\', '/');
}

/**
 * Split the requested scopes and reject unknown names.
 * @param scope - Comma-separated repository scopes to check.
 * @returns Validated scope names as an array.
 */
function scopeParts(scope) {
  const parts = String(scope)
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean);
  if (parts.length === 0 || parts.some((part) => !VALID_SCOPES.includes(part))) {
    throw new Error(`invalid scope "${scope}". expected ${VALID_SCOPE_USAGE}`);
  }

  return parts;
}

/**
 * Check whether a file belongs to any requested scope.
 * @param relativePath - File path relative to the repository root.
 * @param scope - Comma-separated repository scopes to check.
 * @returns Whether at least one selected scope contains the file.
 */
function pathHasScope(relativePath, scope) {
  const parts = scopeParts(scope);
  if (parts.includes('all')) {
    return true;
  }

  return parts.some((part) =>
    SCOPE_PREFIXES[part].some((prefix) => toPosix(relativePath).startsWith(prefix)),
  );
}

function assertPlainRecord(value, key) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${key} must be an object`);
  }

  return value;
}

function assertArray(value, key) {
  if (!Array.isArray(value)) {
    throw new Error(`${key} must be an array`);
  }

  return value;
}

function normalizeTerms(terms, key) {
  const normalized = Array.from(
    new Set(
      assertArray(terms, key)
        .map((term) => String(term).trim())
        .filter(Boolean),
    ),
  );
  if (normalized.length === 0) {
    throw new Error(`${key} must not be empty`);
  }

  return normalized;
}

function normalizeOptionalTerms(value, key) {
  if (value === undefined) return [];
  const normalized = Array.from(
    new Set(
      assertArray(value, key)
        .map((term) => String(term).trim())
        .filter(Boolean),
    ),
  );
  return normalized;
}

function normalizeNameList(names, caseInsensitive, key) {
  const normalizedNames = normalizeOptionalTerms(names, key).map((name) =>
    caseInsensitive ? name.toLowerCase() : name,
  );
  const nameSet = new Set(normalizedNames);
  return nameSet;
}

function normalizeRegexList(value, key) {
  const patterns = normalizeOptionalTerms(value, key);
  // eslint-disable-next-line security/detect-non-literal-regexp -- Patterns come from the reviewed repository policy.
  const regexes = patterns.map((pattern) => new RegExp(pattern, 'u'));
  return regexes;
}

function buildNameRules(nameRules) {
  const rules = assertArray(nameRules, 'nameRules');
  const normalizedRules = rules.map((entry, index) => {
    const rule = assertPlainRecord(entry, `nameRules[${index}]`);
    const pathRegexes = normalizeRegexList(rule.pathRegexes, `nameRules[${index}].pathRegexes`);
    if (pathRegexes.length === 0)
      throw new Error(`nameRules[${index}].pathRegexes must not be empty`);
    return {
      pathRegexes,
      entryPathRegexes: normalizeRegexList(
        rule.entryPathRegexes,
        `nameRules[${index}].entryPathRegexes`,
      ),
      languages: normalizeOptionalTerms(rule.languages, `nameRules[${index}].languages`),
      categories: normalizeOptionalTerms(rule.categories, `nameRules[${index}].categories`),
      kinds: normalizeOptionalTerms(rule.kinds, `nameRules[${index}].kinds`),
      names: normalizeOptionalTerms(rule.names, `nameRules[${index}].names`),
      nameRegexes: normalizeRegexList(rule.nameRegexes, `nameRules[${index}].nameRegexes`),
      caseNames: normalizeOptionalTerms(rule.caseNames, `nameRules[${index}].caseNames`),
      structuralPrefixRegexes: normalizeRegexList(
        rule.structuralPrefixRegexes,
        `nameRules[${index}].structuralPrefixRegexes`,
      ),
      exclude: Boolean(rule.exclude),
    };
  });

  return normalizedRules;
}

function buildLocalTerms(localTerms) {
  const terms = assertArray(localTerms, 'local.bannedTerms');
  const normalizedTerms = terms.map((value, index) => {
    const entry = assertPlainRecord(value, `local.bannedTerms[${index}]`);
    const scopes = normalizeTerms(entry.scopes, `local.bannedTerms[${index}].scopes`);
    if (scopes.length === 0) {
      throw new Error(`local.bannedTerms[${index}].scopes must not be empty`);
    }

    for (const scope of scopes) {
      if (!VALID_SCOPES.includes(scope)) {
        throw new Error(`local.bannedTerms[${index}] has invalid scope "${scope}"`);
      }
    }

    const terms = normalizeTerms(entry.terms, `local.bannedTerms[${index}].terms`);

    return {
      scopes,
      termEntries: buildTermEntries(terms),
    };
  });

  return normalizedTerms;
}

/**
 * Load and validate the repository naming policy.
 * @returns Validated rules, normalized terms, and path exclusions.
 */
function readPolicy() {
  const parsed = assertPlainRecord(
    JSON.parse(fs.readFileSync(policyPath, 'utf8')),
    'naming policy',
  );
  const global = assertPlainRecord(parsed.global, 'global');
  const local = assertPlainRecord(parsed.local, 'local');
  const caseInsensitive = Boolean(parsed.matching?.caseInsensitive);
  const globalTerms = normalizeTerms(global.bannedTerms, 'global.bannedTerms');

  return {
    ...parsed,
    global: {
      ...global,
      reservedTerms: assertArray(global.reservedTerms, 'global.reservedTerms').map(
        (value, index) => {
          const entry = assertPlainRecord(value, `global.reservedTerms[${index}]`);
          const term = String(entry.term).trim().toLowerCase();
          const allowedKinds = normalizeTerms(
            entry.allowedKinds,
            `global.reservedTerms[${index}].allowedKinds`,
          );
          return {
            term,
            allowedKinds,
          };
        },
      ),
      bannedTermExemptions: normalizeNameList(
        global.bannedTermExemptions,
        caseInsensitive,
        'global.bannedTermExemptions',
      ),
      caseInsensitive,
      termEntries: buildTermEntries(globalTerms),
    },
    scopedTermEntries: buildLocalTerms(local.bannedTerms),
    nameRules: buildNameRules(parsed.nameRules),
    excludedPathParts: normalizeTerms(parsed.excludedPaths, 'excludedPaths'),
    excludedBasenames: new Set(normalizeTerms(parsed.excludedBasenames, 'excludedBasenames')),
  };
}

function nameRuleApplies(rule, relativePath, entry) {
  if (!rule.pathRegexes.some((regex) => regex.test(relativePath))) {
    return false;
  }
  if (
    rule.entryPathRegexes.length > 0 &&
    !rule.entryPathRegexes.some((regex) => regex.test(entry.path ?? ''))
  ) {
    return false;
  }
  const fields = [
    [rule.languages, entry.language],
    [rule.categories, entry.category],
    [rule.kinds, entry.kind],
    [rule.names, entry.name],
  ];
  if (fields.some(([values, value]) => values.length > 0 && !values.includes(value))) return false;

  return rule.nameRegexes.length === 0 || rule.nameRegexes.some((regex) => regex.test(entry.name));
}

/**
 * Select naming rules that apply to one identifier.
 * @param policy - Validated repository naming policy.
 * @param relativePath - File path relative to the repository root.
 * @param entry - Identifier record with its name, kind, language, and source location.
 * @returns Policy rules matching the identifier and its source path.
 */
function nameRulesForEntry(policy, relativePath, entry) {
  const matchingRules = [];
  for (const rule of policy.nameRules) {
    if (nameRuleApplies(rule, relativePath, entry)) {
      matchingRules.push(rule);
    }
  }
  return matchingRules;
}

/**
 * Combine global and scoped banned terms for a source file.
 * @param policy - Validated repository naming policy.
 * @param relativePath - File path relative to the repository root.
 * @returns Global and applicable scoped term records.
 */
function termEntriesForPath(policy, relativePath) {
  const entries = [...policy.global.termEntries];
  for (const scopedEntry of policy.scopedTermEntries) {
    if (scopedEntry.scopes.some((scope) => pathHasScope(relativePath, scope))) {
      entries.push(...scopedEntry.termEntries);
    }
  }
  return entries;
}

/**
 * Check generated-file and path exclusions before naming analysis.
 * @param relativePath - File path relative to the repository root.
 * @param policy - Validated repository naming policy.
 * @returns Whether the file is excluded from naming checks.
 */
function isPathExcluded(relativePath, policy) {
  const normalized = `/${toPosix(relativePath)}`;
  const basename = path.basename(relativePath);

  if (generatedFiles.has(toPosix(relativePath))) {
    return true;
  }

  return (
    policy.excludedBasenames.has(basename) ||
    policy.excludedPathParts.some((part) => normalized.includes(part))
  );
}

export {
  repoRoot,
  usage,
  isPathExcluded,
  nameRulesForEntry,
  pathHasScope,
  readPolicy,
  scopeParts,
  termEntriesForPath,
};
