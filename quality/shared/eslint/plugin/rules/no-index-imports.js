import {
  INDEX_IMPORT_ALLOWLIST,
  INDEX_IMPORT_MESSAGE,
  INDEX_IMPORT_PATTERNS,
} from '#config/eslint.js';

const indexImportAllowlist = new Set(INDEX_IMPORT_ALLOWLIST);

function isIndexImport(source) {
  if (indexImportAllowlist.has(source)) {
    return false;
  }

  return INDEX_IMPORT_PATTERNS.some((pattern) => pattern.test(source));
}

function getStaticString(node) {
  if (!node) {
    return undefined;
  }
  if (node.type === 'Literal' && typeof node.value === 'string') {
    return node.value;
  }
  return undefined;
}

function isMockImportCall(node) {
  if (node.callee?.type !== 'MemberExpression') {
    return false;
  }

  const calleeName = node.callee.item?.name;
  const propertyName = node.callee.property?.name;
  return calleeName === 'vi' && ['doMock', 'importActual', 'mock'].includes(propertyName);
}

export const noIndexImports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow index barrel imports.',
    },
    schema: [],
  },
  create(context) {
    const checkSource = (sourceNode) => {
      const source = getStaticString(sourceNode);
      if (!source || !isIndexImport(source)) {
        return;
      }

      context.report({
        node: sourceNode,
        message: INDEX_IMPORT_MESSAGE,
      });
    };
    const visitors = {
      ImportDeclaration: (node) => checkSource(node.source),
      ExportAllDeclaration: (node) => checkSource(node.source),
      ExportNamedDeclaration(node) {
        if (node.source) {
          checkSource(node.source);
        }
      },
      ImportExpression: (node) => checkSource(node.source),
      CallExpression(node) {
        if (!isMockImportCall(node)) {
          return;
        }

        checkSource(node.arguments[0]);
      },
    };
    return visitors;
  },
};
