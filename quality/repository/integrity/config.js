#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { JAVASCRIPT_EXTENSIONS } from '#config/files.js';
import { DISALLOWED_RUNTIME_FOLDERS } from '#config/folders.js';
import { QUALITY_CONFIG_FORBIDDEN_PATTERNS, SHELL_CONFIG_GUARDS } from '#config/config.js';

const REPO_ROOT = process.cwd();
const QUALITY_ROOT = path.join(REPO_ROOT, 'quality');
const CONFIG_ROOT = path.join(QUALITY_ROOT, 'config');
const JAVASCRIPT_EXTENSION_SET = new Set(JAVASCRIPT_EXTENSIONS);
const SHELL_CONFIG_EXTENSIONS = new Set(['.sh']);
const DISALLOWED_RUNTIME_FOLDER_NAMES = new Set(DISALLOWED_RUNTIME_FOLDERS);
const CONFIG_POLICY_FILE = path.join(CONFIG_ROOT, 'config.js');
const errors = [];

function listFiles(rootPath, results = []) {
  if (!fs.existsSync(rootPath)) {
    return results;
  }

  for (const entry of fs.readdirSync(rootPath, { withFileTypes: true })) {
    // reason: Directory entries come from readdir under the fixed policy directory; symbolic links are not followed.
    // bearer:disable javascript_lang_path_traversal
    const entryPath = path.join(rootPath, entry.name);
    if (entry.isDirectory()) {
      listFiles(entryPath, results);
      continue;
    }
    if (entry.isFile()) {
      results.push(entryPath);
    }
  }

  return results;
}

function checkConfigFile(filePath) {
  if (filePath === CONFIG_POLICY_FILE) return;
  const extension = path.extname(filePath);
  const patterns = JAVASCRIPT_EXTENSION_SET.has(extension)
    ? QUALITY_CONFIG_FORBIDDEN_PATTERNS
    : SHELL_CONFIG_EXTENSIONS.has(extension)
      ? SHELL_CONFIG_GUARDS
      : [];
  const source = fs.readFileSync(filePath, 'utf8');
  for (const { pattern, message } of patterns) {
    if (pattern.test(source)) {
      errors.push(`${path.relative(REPO_ROOT, filePath).replaceAll(path.sep, '/')}: ${message}`);
    }
  }
}

function checkRuntimeBucketFolders(directory = QUALITY_ROOT) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (!entry.isDirectory()) {
      continue;
    }

    // reason: Directory entries come from readdir under the fixed quality directory; symbolic links are not followed.
    // bearer:disable javascript_lang_path_traversal
    const entryPath = path.join(directory, entry.name);
    if (DISALLOWED_RUNTIME_FOLDER_NAMES.has(entry.name)) {
      errors.push(
        `${path.relative(REPO_ROOT, entryPath).replaceAll(path.sep, '/')}/: split quality code by owner or behavior, not by runtime folder`,
      );
    }
    checkRuntimeBucketFolders(entryPath);
  }
}

for (const filePath of listFiles(CONFIG_ROOT)) checkConfigFile(filePath);
checkRuntimeBucketFolders();

if (errors.length > 0) {
  console.error('quality config policy failed:');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('quality config policy passed.');
