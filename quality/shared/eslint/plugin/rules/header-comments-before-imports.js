const DIRECTIVE_COMMENT_PATTERN =
  /^(?:eslint(?:\s|$|-)|global\s|globals\s|exported\s|jshint\s|jslint\s|istanbul\s|c8\s|@?ts-(?:ignore|expect-error|nocheck|check)\b)/u;
const BLANK_LINE_PATTERN = /\n\s*\n/u;
const WHITESPACE_ONLY_PATTERN = /^\s*$/u;

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
  if (supportRequire) {
    return isRequireDeclaration(node) || isSideEffectRequire(node);
  }
  return false;
};

/**
 * Returns true if the comment's range falls entirely within the node's range.
 * @param comment - Parsed comment and its source range.
 * @param node - Syntax-tree node to inspect.
 * @returns Whether the entire comment lies within the node.
 */
const isCommentInsideNode = (comment, node) => {
  const startsInside = comment.range[0] >= node.range[0];
  const endsInside = comment.range[1] <= node.range[1];
  return startsInside && endsInside;
};

/**
 * Returns true if the comment sits on the same line after the node with only whitespace between them.
 * @param sourceText - Complete source text for the file.
 * @param comment - Parsed comment and its source range.
 * @param node - Syntax-tree node to inspect.
 * @returns Whether the comment follows the node on the same line.
 */
const isTrailingCommentNode = (sourceText, comment, node) => {
  if (comment.loc.start.line !== node.loc.end.line) {
    return false;
  }
  if (comment.range[0] < node.range[1]) {
    return false;
  }

  return WHITESPACE_ONLY_PATTERN.test(sourceText.slice(node.range[1], comment.range[0]));
};

/**
 * Returns true if the comment appears directly before the node with only whitespace (and optionally one blank line) between them.
 * @param sourceText - Complete source text for the file.
 * @param comment - Parsed comment and its source range.
 * @param node - Syntax-tree node to inspect.
 * @param root0 - Comment attachment options.
 * @param root0.allowSingleBlankLine - Whether one blank line may separate a comment from the node.
 * @returns Whether the comment is attached before the node.
 */
const isLeadingCommentNode = (sourceText, comment, node, { allowSingleBlankLine = false } = {}) => {
  if (comment.range[1] > node.range[0]) {
    return false;
  }

  const between = sourceText.slice(comment.range[1], node.range[0]);
  if (!WHITESPACE_ONLY_PATTERN.test(between)) {
    return false;
  }

  const lineDistance = node.loc.start.line - comment.loc.end.line;
  if (allowSingleBlankLine) {
    if (lineDistance > 2) {
      return false;
    }
  } else if (lineDistance > 1) {
    return false;
  }

  if (!allowSingleBlankLine && BLANK_LINE_PATTERN.test(between)) {
    return false;
  }

  const lineStart = sourceText.lastIndexOf('\n', comment.range[0] - 1) + 1;
  return WHITESPACE_ONLY_PATTERN.test(sourceText.slice(lineStart, comment.range[0]));
};

/**
 * Returns true if the comment is inside, trailing, or leading-attached to the given node.
 * @param sourceText - Complete source text for the file.
 * @param comment - Parsed comment and its source range.
 * @param node - Syntax-tree node to inspect.
 * @param options - Comment attachment options.
 * @returns Whether the comment belongs to the node.
 */
const isAttachedToNode = (sourceText, comment, node, options) => {
  if (isCommentInsideNode(comment, node)) {
    return true;
  }
  if (isTrailingCommentNode(sourceText, comment, node)) {
    return true;
  }
  return isLeadingCommentNode(sourceText, comment, node, options);
};

export const headerCommentsBeforeImports = {
  meta: {
    type: 'layout',
    docs: {
      description: 'Require file-level comments/docs to appear before the import/require section.',
    },
    fixable: 'code',
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
      headerFirst: 'Top-level comments/docs must be placed before import/require statements.',
    },
  },
  create(context) {
    const sourceCode = context.sourceCode;
    const sourceText = sourceCode.getText();
    const options = context.options?.[0] ?? {};
    const supportRequire = options.supportRequire === true;

    return {
      Program(node) {
        const firstImportIndex = node.body.findIndex((statement) =>
          isImportLike(statement, supportRequire),
        );
        if (firstImportIndex === -1) {
          return;
        }

        let firstNonImportRun = -1;
        for (let index = firstImportIndex + 1; index < node.body.length; index += 1) {
          if (!isImportLike(node.body[index], supportRequire)) {
            firstNonImportRun = index;
            break;
          }
        }
        if (firstNonImportRun === -1) {
          return;
        }

        const firstImportNode = node.body[firstImportIndex];
        const importRun = node.body.slice(firstImportIndex, firstNonImportRun);
        const firstNonImportNode = node.body[firstNonImportRun];
        const violatingComment = sourceCode.getAllComments().find((comment) => {
          if (comment.range[0] < firstImportNode.range[0]) {
            return false;
          }
          if (comment.range[1] > firstNonImportNode.range[0]) {
            return false;
          }
          const normalizedComment = comment.value.replace(/^\s*\*?/u, '').trim();
          if (DIRECTIVE_COMMENT_PATTERN.test(normalizedComment)) {
            return false;
          }

          if (importRun.some((importNode) => isAttachedToNode(sourceText, comment, importNode))) {
            return false;
          }

          if (
            isAttachedToNode(sourceText, comment, firstNonImportNode, {
              allowSingleBlankLine: true,
            })
          ) {
            return false;
          }

          return true;
        });

        if (!violatingComment) {
          return;
        }

        context.report({
          node: violatingComment,
          fix: (fixer) => {
            const lineStart = sourceText.lastIndexOf('\n', violatingComment.range[0] - 1) + 1;
            let segmentEnd = violatingComment.range[1];
            while (segmentEnd < sourceText.length && /[\t\n\r ]/u.test(sourceText[segmentEnd])) {
              segmentEnd += 1;
            }
            const commentText = sourceText.slice(lineStart, violatingComment.range[1]).trimEnd();

            return [
              fixer.insertTextBeforeRange(
                [firstImportNode.range[0], firstImportNode.range[0]],
                `${commentText}\n\n`,
              ),
              fixer.removeRange([lineStart, segmentEnd]),
            ];
          },
          messageId: 'headerFirst',
        });
      },
    };
  },
};
