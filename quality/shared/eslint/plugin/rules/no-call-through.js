const MESSAGE =
  'Inline trivial call-through functions unless they own policy, validation, telemetry, caching, or error handling.';
const UNWRAP_NODE_TYPES = new Set([
  'AwaitExpression',
  'ChainExpression',
  'TSAsExpression',
  'TSSatisfiesExpression',
  'TSNonNullExpression',
  'TSInstantiationExpression',
]);

function unwrapExpression(node) {
  let current = node;
  while (current && UNWRAP_NODE_TYPES.has(current.type)) {
    current = current.expression;
  }
  return current;
}

function getStatementExpression(statement) {
  if (statement.type === 'ReturnStatement') {
    return statement.argument;
  }
  if (statement.type === 'ExpressionStatement') {
    return statement.expression;
  }
  return null;
}

function getOnlyCall(body) {
  if (!body || body.type !== 'BlockStatement' || body.body.length !== 1) {
    return null;
  }

  const expression = unwrapExpression(getStatementExpression(body.body[0]));
  return expression?.type === 'CallExpression' ? expression : null;
}

function getParameterName(parameter) {
  const current = unwrapExpression(parameter);
  if (current?.type === 'Identifier') {
    return current.name;
  }
  if (current?.type === 'AssignmentPattern' && current.left.type === 'Identifier') {
    return current.left.name;
  }
  return null;
}

function getArgumentName(argument) {
  const current = unwrapExpression(argument);
  if (current?.type !== 'Identifier') {
    return null;
  }
  return current.name;
}

function isDirectCallThrough(node, call) {
  const parameterNames = node.params.map(getParameterName);
  if (parameterNames.includes(null)) {
    return false;
  }

  const callee = unwrapExpression(call.callee);
  return (
    callee?.type === 'Identifier' &&
    call.arguments.length === parameterNames.length &&
    call.arguments.every((argument, index) => getArgumentName(argument) === parameterNames[index])
  );
}

function normalizedFilename(context) {
  const filename = String(
    context.physicalFilename || context.filename || context.getFilename?.() || '',
  );
  const normalized = filename.replaceAll('\\', '/');
  return normalized;
}

function isAllowed(context, functionName, allow) {
  if (!functionName || allow.length === 0) {
    return false;
  }

  const filename = normalizedFilename(context);
  const key = `${filename}:${functionName}`;
  return allow.some((entry) => key === entry || key.endsWith(`/${entry}`));
}

function reportCallThrough(context, node, allow) {
  const functionName = node.id?.name ?? null;
  if (!functionName || isAllowed(context, functionName, allow)) {
    return;
  }

  const call = getOnlyCall(node.body);
  if (call && isDirectCallThrough(node, call)) {
    context.report({ node, message: MESSAGE });
  }
}

export const noCallThrough = {
  meta: {
    type: 'problem',
    docs: {
      description:
        'Disallow trivial functions whose only behavior is forwarding their parameters to another call.',
    },
    schema: [
      {
        type: 'object',
        properties: {
          allow: {
            type: 'array',
            items: { type: 'string' },
          },
        },
        additionalProperties: false,
      },
    ],
  },
  create(context) {
    const options = context.options?.[0] ?? {};
    const allow = Array.isArray(options.allow) ? options.allow : [];

    return {
      FunctionDeclaration: (node) => reportCallThrough(context, node, allow),
    };
  },
};
