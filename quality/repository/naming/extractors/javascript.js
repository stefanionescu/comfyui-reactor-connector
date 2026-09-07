import path from 'node:path';
import { JSX_EXTENSIONS } from '#config/files.js';
import { getKeys } from '@typescript-eslint/visitor-keys';
import { parse } from '@typescript-eslint/typescript-estree';

import {
  CONSTANT_PROPERTY_REGEX,
  GENERATED_PROPERTY_KEYS,
  SNAKE_PROPERTY_REGEX,
  SOCKET_STATE_KEYS,
} from '#config/naming.js';

const JSX_EXTENSION_SET = new Set(JSX_EXTENSIONS);
const GENERATED_PROPERTY_KEY_SET = new Set(GENERATED_PROPERTY_KEYS);
const SOCKET_STATE_KEY_SET = new Set(SOCKET_STATE_KEYS);

function lineFor(node) {
  if (!node?.loc?.start) {
    return 1;
  }
  return node.loc.start.line ?? 1;
}

function addEntry(entries, file, language, category, kind, name, node) {
  if (!name || name === '_') {
    return;
  }

  entries.push({
    file,
    line: lineFor(node),
    language,
    category,
    kind,
    name,
  });
}

function keyName(node) {
  if (node?.type === 'Identifier' || node?.type === 'PrivateIdentifier') {
    return node.name;
  }
  if (node?.type === 'Literal' && typeof node.value === 'string') {
    return node.value;
  }
  return null;
}

function isExternalContractProperty(name) {
  if (GENERATED_PROPERTY_KEY_SET.has(name) || SOCKET_STATE_KEY_SET.has(name)) {
    return true;
  }
  if (CONSTANT_PROPERTY_REGEX.test(name)) {
    return true;
  }
  return SNAKE_PROPERTY_REGEX.test(name);
}

function skipPatternField(field) {
  if (field?.type !== 'Property') {
    return false;
  }

  const key = keyName(field.key);
  return (
    isExternalContractProperty(key) &&
    field.value?.type === 'Identifier' &&
    field.value.name === key
  );
}

function addKeyEntry(entries, file, language, category, kind, node) {
  if (node?.computed) {
    return;
  }

  addEntry(entries, file, language, category, kind, keyName(node.key), node.key ?? node);
}

function patternChildren(node) {
  switch (node.type) {
    case 'RestElement':
      return [node.argument];
    case 'TSParameterProperty':
      return [node.parameter];
    case 'AssignmentPattern':
      return [node.left];
    case 'ArrayPattern':
      return node.elements;
    case 'ObjectPattern':
      return node.properties
        .filter((field) => !skipPatternField(field))
        .map((field) => (field.type === 'RestElement' ? field.argument : field.value));
    default:
      return [];
  }
}

function collectPatternNames(entries, file, language, category, kind, node) {
  if (!node) return;
  if (node.type === 'Identifier') {
    addEntry(entries, file, language, category, kind, node.name, node);
    return;
  }
  for (const child of patternChildren(node)) {
    collectPatternNames(entries, file, language, category, kind, child);
  }
}

function collectParams(entries, file, language, node) {
  for (const param of node.params ?? []) {
    collectPatternNames(entries, file, language, 'parameters', `${language} parameter`, param);
  }
}

function isTreeNode(value) {
  if (!value || typeof value !== 'object') {
    return false;
  }
  return typeof value.type === 'string';
}

function walkTree(node, visit, parent = null) {
  if (!isTreeNode(node)) {
    return;
  }

  visit(node, parent);

  for (const key of getKeys(node)) {
    const child = node[key];
    if (Array.isArray(child)) {
      for (const item of child) {
        walkTree(item, visit, node);
      }
      continue;
    }
    walkTree(child, visit, node);
  }
}

function parseSource(relativePath, sourceText) {
  const extension = path.extname(relativePath).toLowerCase();
  const options = {
    comment: false,
    jsx: JSX_EXTENSION_SET.has(extension),
    loc: true,
    range: false,
    sourceType: 'module',
    filePath: relativePath,
    tokens: false,
  };

  return parse(sourceText, options);
}

function collectNode(entries, file, language, node) {
  switch (node.type) {
    case 'ClassDeclaration':
    case 'TSInterfaceDeclaration':
    case 'TSTypeAliasDeclaration':
    case 'TSEnumDeclaration':
      addEntry(
        entries,
        file,
        language,
        'classes',
        `${language} class`,
        node.id?.name,
        node.id ?? node,
      );
      break;
    case 'TSDeclareFunction':
    case 'FunctionDeclaration':
      addEntry(
        entries,
        file,
        language,
        'functions',
        `${language} function`,
        node.id?.name,
        node.id ?? node,
      );
      collectParams(entries, file, language, node);
      break;
    case 'FunctionExpression':
      addEntry(
        entries,
        file,
        language,
        'functions',
        `${language} function`,
        node.id?.name,
        node.id ?? node,
      );
      collectParams(entries, file, language, node);
      break;
    case 'TSFunctionType':
    case 'TSCallSignatureDeclaration':
    case 'TSConstructSignatureDeclaration':
    case 'ArrowFunctionExpression':
      collectParams(entries, file, language, node);
      break;
    case 'VariableDeclarator':
      collectPatternNames(entries, file, language, 'variables', `${language} variable`, node.id);
      break;
    case 'TSMethodSignature':
    case 'MethodDefinition':
      if (node.kind !== 'constructor') {
        addKeyEntry(entries, file, language, 'functions', `${language} function`, node);
      }
      collectParams(entries, file, language, node.value ?? node);
      break;
    case 'TSAbstractPropertyDefinition':
    case 'TSPropertySignature':
    case 'PropertyDefinition':
      addKeyEntry(entries, file, language, 'properties', `${language} property`, node);
      break;
    case 'TSTypeParameter':
      addEntry(
        entries,
        file,
        language,
        'classes',
        'type parameter',
        node.name?.name ?? node.name,
        node,
      );
      break;
    case 'TSParameterProperty':
      collectPatternNames(
        entries,
        file,
        language,
        'properties',
        'parameter property',
        node.parameter,
      );
      break;
    case 'TSEnumMember':
      addEntry(entries, file, language, 'properties', 'enum member', keyName(node.id), node);
      break;
    default:
      break;
  }
}

/**
 * Parse JavaScript or TypeScript and collect its declared names.
 * @param relativePath - File path relative to the repository root.
 * @param sourceText - Complete source text for the file.
 * @param language - Language profile used to classify identifiers.
 * @returns Declared-name records with their locations and categories.
 */
function collectJavaScriptNames(relativePath, sourceText, language) {
  const entries = [];
  let astRoot;

  try {
    astRoot = parseSource(relativePath, sourceText);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`failed to parse ${relativePath}: ${message}`, { cause: error });
  }

  walkTree(astRoot, (node) => collectNode(entries, relativePath, language, node));
  return entries;
}

export { collectJavaScriptNames };
