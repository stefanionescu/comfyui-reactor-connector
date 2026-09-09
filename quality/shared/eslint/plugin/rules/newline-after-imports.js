const blankLinePattern = /\n\s*\n/u;
const whitespaceOnlyPattern = /^\s*$/u;

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
 * @param node - Syntax-tree node to inspect.
 * @param supportRequire - Whether CommonJS require calls count as imports.
 * @returns Whether the statement belongs in an import block.
 */
const isImportLike = (node, supportRequire) => {
  if (node.type === 'ImportDeclaration') {
    return true;
  }
  return supportRequire && (isRequireDeclaration(node) || isSideEffectRequire(node));
};

/**
 * Returns the source offset after the node including any same-line trailing comments.
 * @param sourceCode - ESLint source text, comments, and token locations.
 * @param node - Syntax-tree node to inspect.
 * @returns Offset after the statement and same-line trailing comments.
 */
const getStatementEndComments = (sourceCode, node) => {
  const fullText = sourceCode.getText();
  let end = node.range[1];

  for (const comment of sourceCode.getCommentsAfter(node)) {
    const between = fullText.slice(end, comment.range[0]);
    if (!whitespaceOnlyPattern.test(between) || comment.loc.start.line !== node.loc.end.line) {
      break;
    }
    end = comment.range[1];
  }

  return end;
};

/**
 * Returns the first non-whitespace offset in a text range.
 * @param text - Source text within the selected range.
 * @param rangeStart - Absolute source offset at the start of the range.
 * @param fallbackOffset - Offset to return when the range contains only whitespace.
 * @returns First non-whitespace offset, or the supplied fallback.
 */
const getFirstContentOffset = (text, rangeStart, fallbackOffset) => {
  const contentOffset = text.search(/\S/u);
  if (contentOffset === -1) {
    return fallbackOffset;
  }
  return rangeStart + contentOffset;
};

export const newlineAfterImports = {
  meta: {
    type: 'layout',
    docs: {
      description: 'Require a blank line after the import/require section.',
    },
    fixable: 'whitespace',
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
      newlineAfterImport: 'Import statements must be followed by a blank line.',
      newlineAfterImportOrRequire: 'Import/require statements must be followed by a blank line.',
    },
  },
  create(context) {
    const sourceCode = context.sourceCode;
    const sourceText = sourceCode.getText();
    const supportRequire = context.options?.[0]?.supportRequire === true;

    return {
      Program(node) {
        const firstImportIndex = node.body.findIndex((statement) =>
          isImportLike(statement, supportRequire),
        );
        if (firstImportIndex === -1) {
          return;
        }

        let lastImportIndex = firstImportIndex;
        for (let index = firstImportIndex + 1; index < node.body.length; index += 1) {
          if (!isImportLike(node.body[index], supportRequire)) {
            break;
          }
          lastImportIndex = index;
        }

        const firstNonImportNode = node.body[lastImportIndex + 1];
        if (!firstNonImportNode) {
          return;
        }

        const lastImportNode = node.body[lastImportIndex];
        const importEnd = getStatementEndComments(sourceCode, lastImportNode);
        const boundaryText = sourceText.slice(importEnd, firstNonImportNode.range[0]);
        const firstContentOffset = getFirstContentOffset(
          boundaryText,
          importEnd,
          firstNonImportNode.range[0],
        );
        const leadingWhitespace = sourceText.slice(importEnd, firstContentOffset);

        if (blankLinePattern.test(leadingWhitespace)) {
          return;
        }

        context.report({
          node: firstNonImportNode,
          messageId: supportRequire ? 'newlineAfterImportOrRequire' : 'newlineAfterImport',
          fix: (fixer) => fixer.replaceTextRange([importEnd, firstContentOffset], '\n\n'),
        });
      },
    };
  },
};
