/**
 * Returns true if the node is a bare `require('...')` call with no assignment.
 * @param node - Syntax-tree node to inspect.
 * @returns Whether the statement calls require without assigning its result.
 */
const isSideEffectRequire = (node) => {
  if (node.type !== 'ExpressionStatement' || node.expression?.type !== 'CallExpression') {
    return false;
  }
  const callee = node.expression.callee;
  return (
    callee?.type === 'Identifier' &&
    callee.name === 'require' &&
    node.expression.arguments?.length === 1
  );
};

/**
 * Returns true if the node is a `require('...')` call.
 * @param node - Syntax-tree node to inspect.
 * @returns Whether the node is a one-argument call to require.
 */
function isRequireCall(node) {
  if (node?.type !== 'CallExpression') {
    return false;
  }

  const callee = node.callee;
  return callee?.type === 'Identifier' && callee.name === 'require' && node.arguments.length === 1;
}

/**
 * Returns true if the node reads a property from a `require()` call.
 * @param node - Syntax-tree node to inspect.
 * @returns Whether the node reads a property from a require call.
 */
function isRequireMemberExpression(node) {
  if (node?.type !== 'MemberExpression') {
    return false;
  }

  return isRequireCall(node.object);
}

/**
 * Returns true if the node is a variable declaration initialized by a `require()` call.
 * @param node - Syntax-tree node to inspect.
 * @returns Whether one declared variable is initialized from require.
 */
const isRequireDeclaration = (node) => {
  if (node.type !== 'VariableDeclaration' || node.declarations.length !== 1) {
    return false;
  }

  const declaration = node.declarations[0];
  if (!declaration?.init) {
    return false;
  }

  return isRequireCall(declaration.init) || isRequireMemberExpression(declaration.init);
};

/**
 * Returns true if the statement belongs to a directive prologue such as `'use strict';`.
 * @param statement - Top-level syntax-tree statement to inspect.
 * @returns Whether the statement is a directive such as use strict.
 */
const isDirectiveStatement = (statement) => {
  if (statement.type !== 'ExpressionStatement') {
    return false;
  }
  return typeof statement.directive === 'string';
};

/**
 * Returns true if the node is an import declaration or (optionally) a require statement.
 * @param statement - Top-level syntax-tree statement to inspect.
 * @param supportRequire - Whether CommonJS require calls count as imports.
 * @returns Whether the statement belongs in an import block.
 */
const isImportLike = (statement, supportRequire) => {
  if (statement.type === 'ImportDeclaration') {
    return true;
  }
  return supportRequire && (isRequireDeclaration(statement) || isSideEffectRequire(statement));
};

export const noImportsAfterStatements = {
  meta: {
    type: 'layout',
    docs: {
      description:
        'Disallow static import declarations or supported require statements after top-level statements.',
    },
    schema: [
      {
        type: 'object',
        properties: {
          supportRequire: { type: 'boolean' },
        },
        additionalProperties: false,
      },
    ],
    messages: {
      importAfterStatement: 'Static import declarations must appear before top-level statements.',
      importOrRequireAfterStatement:
        'Static import/require declarations must appear before top-level statements.',
    },
  },
  create(context) {
    const supportRequire = context.options?.[0]?.supportRequire === true;
    const visitors = {
      Program(node) {
        let hasTopLevelStatement = false;

        for (const statement of node.body) {
          if (!hasTopLevelStatement && isDirectiveStatement(statement)) {
            continue;
          }

          if (isImportLike(statement, supportRequire)) {
            reportLateImport(context, statement, hasTopLevelStatement, supportRequire);
            continue;
          }

          hasTopLevelStatement = true;
        }
      },
    };
    return visitors;
  },
};

function reportLateImport(context, statement, hasTopLevelStatement, supportRequire) {
  if (!hasTopLevelStatement) return;
  context.report({
    node: statement,
    messageId: supportRequire ? 'importOrRequireAfterStatement' : 'importAfterStatement',
  });
}
