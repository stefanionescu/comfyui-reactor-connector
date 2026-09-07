import { MAX_TRIVIAL_FUNCTION_STATEMENTS } from '#config/limits.js';

const DEFAULT_MAX_STATEMENTS = MAX_TRIVIAL_FUNCTION_STATEMENTS;
const MESSAGE = 'Inline functions whose block body only wraps trivial delegation.';
const TRIVIAL_STATEMENT_TYPES = new Set([
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

function maxStatements(context) {
  const [options = {}] = context.options;
  const configured = Number(options.maxStatements ?? DEFAULT_MAX_STATEMENTS);
  if (!Number.isInteger(configured) || configured < 1) {
    return DEFAULT_MAX_STATEMENTS;
  }

  return configured;
}

function reportIfTrivial(context, node) {
  const body = node.body;
  if (!body || body.type !== 'BlockStatement') {
    return;
  }

  const statements = executableStatements(body.body);
  if (statements.length === 0 || statements.length > maxStatements(context)) {
    return;
  }
  if (statements.some((statement) => !TRIVIAL_STATEMENT_TYPES.has(statement.type))) {
    return;
  }

  context.report({
    node,
    message: `${MESSAGE} Function: ${functionName(node)}.`,
  });
}

function reportIfExpressionArrow(context, node) {
  if (node.body?.type === 'BlockStatement') {
    return;
  }

  const name = functionName(node);
  if (name === '<anonymous>') {
    return;
  }

  context.report({
    node,
    message: `${MESSAGE} Function: ${name}.`,
  });
}

export const noTrivialFunctions = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow block-bodied functions with too few trivial executable statements.',
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
  create: (context) => ({
    FunctionDeclaration: (node) => reportIfTrivial(context, node),
    FunctionExpression: (node) => reportIfTrivial(context, node),
    ArrowFunctionExpression: (node) => {
      reportIfTrivial(context, node);
      if (node.body?.type === 'BlockStatement') {
        return;
      }
      reportIfExpressionArrow(context, node);
    },
  }),
};
