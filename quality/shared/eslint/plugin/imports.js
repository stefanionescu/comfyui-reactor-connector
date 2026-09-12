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
 * Returns true if the node is an import declaration or (optionally) a require statement.
 * @param supportRequire - Whether CommonJS require calls count as imports.
 * @param node - Syntax-tree node to inspect.
 * @returns Whether the statement belongs in an import block.
 */
export const isImportLike = (supportRequire, node) => {
  if (node.type === 'ImportDeclaration') {
    return true;
  }
  if (supportRequire) {
    return isRequireDeclaration(node) || isSideEffectRequire(node);
  }
  return false;
};

/**
 * Include comments attached to the same line as a statement.
 * @param sourceCode - ESLint source text and comment locations.
 * @param node - The statement whose trailing comments belong to its edit range.
 * @returns The offset after the statement and its same-line comments.
 */
export function statementEnd(sourceCode, node) {
  const text = sourceCode.getText();
  let end = node.range[1];
  for (const comment of sourceCode.getCommentsAfter(node)) {
    if (
      !/^\s*$/u.test(text.slice(end, comment.range[0])) ||
      comment.loc.start.line !== node.loc.end.line
    )
      break;
    end = comment.range[1];
  }
  return end;
}

/**
 * Preserve the quote style of an import when rewriting its path.
 * @param sourceNode - The import's string literal.
 * @returns Its quote character, or a single quote when raw text is unavailable.
 */
export function getQuote(sourceNode) {
  const raw = typeof sourceNode.raw === 'string' ? sourceNode.raw : '';
  return raw.startsWith('"') ? '"' : "'";
}
