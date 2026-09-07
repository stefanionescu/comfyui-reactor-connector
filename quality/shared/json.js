import fs from 'node:fs';

/**
 * Throws a validation error.
 *
 * @param {string} message Failure reason.
 */
function fail(message) {
  throw new Error(message);
}

/**
 * Reads a JSON file.
 *
 * @param {string} filePath File path.
 * @param {string} description Source description.
 * @returns {unknown} Parsed JSON.
 */
export function readJsonFile(filePath, description) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    fail(`${description} could not be read: ${message}`);
  }
}

/**
 * Requires an array value.
 *
 * @param {unknown} value Value to validate.
 * @param {string} name Value name.
 * @returns {unknown[]} The array value.
 */
export function requireArray(value, name) {
  if (!Array.isArray(value)) {
    fail(`${name} must be an array`);
  }
  return value;
}

/**
 * Requires a plain item value.
 *
 * @param {unknown} value Value to validate.
 * @param {string} name Value name.
 * @returns {Record<string, unknown>} The item value.
 */
export function requireDictionary(value, name) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    fail(`${name} must be an item`);
  }
  return value;
}

/**
 * Requires a non-empty string value.
 *
 * @param {unknown} value Value to validate.
 * @param {string} name Value name.
 * @returns {string} The string value.
 */
export function requireString(value, name) {
  if (typeof value !== 'string' || value.length === 0) {
    fail(`${name} must be a non-empty string`);
  }
  return value;
}
