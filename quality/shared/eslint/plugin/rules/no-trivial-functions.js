import { MAX_TRIVIAL_FUNCTION_STATEMENTS } from '#config/limits.js';

const defaultMaxStatements = MAX_TRIVIAL_FUNCTION_STATEMENTS;
const message = 'Inline functions with only one or two executable statements.';
const trivialStatementTypes = new Set([
  'ExpressionStatement',
  'ReturnStatement',
  'VariableDeclaration',
]);

function executableStatements(body) {
  const statements = [];
  for (const statement of body) {
    if (statement.type !== 'EmptyStatement') {
      statements.push(statement);
    }
  }

  return statements;
}

function functionName(node) {
  if (node.id?.name) {
    return node.id.name;
  }
  if (node.parent?.type === 'VariableDeclarator' && node.parent.id.type === 'Identifier') {
    return node.parent.id.name;
  }
  if (node.key?.name) {
    return node.key.name;
  }
  if (node.key?.value) {
    return String(node.key.value);
  }

  return '<anonymous>';
}

function reportIfTrivial(context, maxStatements, node) {
  const body = node.body;
  const statements = body.type === 'BlockStatement' ? executableStatements(body.body) : [body];
  if (statements.length === 0 || statements.length > maxStatements) {
    return;
  }
  if (body.type === 'BlockStatement') {
    for (const statement of statements) {
      if (!trivialStatementTypes.has(statement.type)) return;
    }
  }
  context.report({ node, message: `${message} Function: ${functionName(node)}.` });
}

export const noTrivialFunctions = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow functions with only one or two simple executable statements.',
    },
    schema: [
      {
        type: 'object',
        additionalProperties: false,
        properties: {
          maxStatements: {
            type: 'integer',
            minimum: 1,
          },
        },
      },
    ],
  },
  create(context) {
    const maxStatements = context.options[0]?.maxStatements ?? defaultMaxStatements;
    const visit = reportIfTrivial.bind(null, context, maxStatements);
    return {
      FunctionDeclaration: visit,
      FunctionExpression: visit,
      ArrowFunctionExpression: visit,
    };
  },
};
