const ALIAS_MESSAGE = 'Export the source value directly instead of adding an exported const alias.';

function unwrapExpression(node) {
  let current = node;
  while (
    current?.type === 'ChainExpression' ||
    current?.type === 'TSAsExpression' ||
    current?.type === 'TSSatisfiesExpression' ||
    current?.type === 'TSNonNullExpression'
  ) {
    current = current.expression;
  }
  return current;
}

function isIdentifierMemberExpression(node) {
  const current = unwrapExpression(node);
  if (!current) {
    return false;
  }
  if (current.type === 'Identifier') {
    return true;
  }
  if (current.type !== 'MemberExpression') {
    return false;
  }
  return isIdentifierMemberExpression(current.object);
}

export const noExportedAliasConstants = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow exported const aliases that only rename another identifier/member.',
    },
    schema: [],
  },
  create(context) {
    const ruleContext = context;
    const visitors = {
      ExportNamedDeclaration(node) {
        if (node.declaration?.type !== 'VariableDeclaration' || node.declaration.kind !== 'const') {
          return;
        }

        for (const declarator of node.declaration.declarations) {
          if (!isIdentifierMemberExpression(declarator.init)) {
            continue;
          }

          ruleContext.report({
            node: declarator,
            message: ALIAS_MESSAGE,
          });
        }
      },
    };
    return visitors;
  },
};
