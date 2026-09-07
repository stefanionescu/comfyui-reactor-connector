import { INTERNAL_PREFIXES } from '#config/paths.js';

const STYLE_MESSAGES = {
  js: 'Internal imports must use explicit JavaScript file extensions.',
  ts: 'Internal imports must use explicit .ts extensions.',
  extensionless: 'Internal imports must be extensionless (no .js/.ts suffix).',
};
const JAVASCRIPT_EXTENSIONS = ['.js', '.mjs', '.cjs'];
const TYPESCRIPT_EXTENSIONS = ['.ts', '.mts', '.cts'];
const SKIPPED_EXTENSIONS = ['.json'];

/**
 * Returns the file extension from an import source, if the source includes one.
 * @param source - Module path written in the import.
 * @returns The final filename suffix, or an empty string when absent.
 */
function getSourceExtension(source) {
  const fileName = source.split('/').pop() ?? '';
  const index = fileName.lastIndexOf('.');
  return index > 0 ? fileName.slice(index) : '';
}

/**
 * Returns true if the import source starts with any of the known internal prefixes.
 * @param source - Module path written in the import.
 * @param internalPrefixes - Prefixes that identify imports owned by the repository.
 * @returns Whether the module path has a configured internal prefix.
 */
function isInternalImport(source, internalPrefixes) {
  for (const prefix of internalPrefixes) {
    if (source.startsWith(prefix)) {
      return true;
    }
  }
  return false;
}

/**
 * Returns true if the import source's file extension matches the required style (js, ts, or extensionless).
 * @param source - Module path written in the import.
 * @param style - Required import extension style.
 * @returns Whether the module path follows the selected extension rule.
 */
function isCompliant(source, style) {
  const extension = getSourceExtension(source);
  const hasKnownScriptExtension =
    JAVASCRIPT_EXTENSIONS.includes(extension) || TYPESCRIPT_EXTENSIONS.includes(extension);

  if (SKIPPED_EXTENSIONS.includes(extension) || (extension && !hasKnownScriptExtension)) {
    return true;
  }

  if (style === 'js') {
    return JAVASCRIPT_EXTENSIONS.includes(extension);
  }

  if (style === 'ts') {
    return TYPESCRIPT_EXTENSIONS.includes(extension);
  }

  return !hasKnownScriptExtension;
}

/**
 * Returns the preferred source value for fixable extension-style violations.
 * @param source - Module path written in the import.
 * @param style - Required import extension style.
 * @returns Module path with the required extension added, replaced, or removed.
 */
function getPreferredSource(source, style) {
  const extension = getSourceExtension(source);

  if (style === 'extensionless') {
    return extension ? source.slice(0, -extension.length) : source;
  }

  if (extension) {
    return source.slice(0, -extension.length) + `.${style}`;
  }

  return `${source}.${style}`;
}

/**
 * Returns the quote character used by the import source node.
 * @param sourceNode - String-literal node containing the module path.
 * @returns The original quote character, defaulting to a single quote.
 */
function getQuote(sourceNode) {
  const raw = typeof sourceNode.raw === 'string' ? sourceNode.raw : '';
  if (raw.startsWith('"')) {
    return '"';
  }
  return "'";
}

export const importPathStyle = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce internal import suffix style by runtime boundary.',
    },
    fixable: 'code',
    schema: [
      {
        type: 'object',
        properties: {
          style: {
            enum: ['js', 'ts', 'extensionless'],
          },
          internalPrefixes: {
            type: 'array',
            items: { type: 'string' },
          },
          externalSources: {
            type: 'array',
            items: { type: 'string' },
            uniqueItems: true,
          },
        },
        required: ['style'],
        additionalProperties: false,
      },
    ],
  },
  create(context) {
    const options = context.options?.[0] ?? {};
    const style = options.style;
    const internalPrefixes =
      Array.isArray(options.internalPrefixes) && options.internalPrefixes.length > 0
        ? options.internalPrefixes
        : INTERNAL_PREFIXES;

    if (!STYLE_MESSAGES[style]) {
      return {};
    }

    const checkSource = (sourceNode) => {
      const source = sourceNode?.value;
      if (typeof source !== 'string') {
        return;
      }

      if (
        options.externalSources?.includes(source) ||
        !isInternalImport(source, internalPrefixes)
      ) {
        return;
      }

      if (isCompliant(source, style)) {
        return;
      }

      context.report({
        node: sourceNode,
        message: STYLE_MESSAGES[style],
        fix(fixer) {
          const preferredSource = getPreferredSource(source, style);
          const quote = getQuote(sourceNode);
          return fixer.replaceText(sourceNode, `${quote}${preferredSource}${quote}`);
        },
      });
    };

    const checkRequireCall = (node) => {
      if (node.callee?.type !== 'Identifier' || node.callee.name !== 'require') {
        return;
      }
      checkSource(node.arguments?.[0]);
    };

    return {
      CallExpression: checkRequireCall,
      ImportDeclaration: (node) => checkSource(node.source),
      ImportExpression: (node) => checkSource(node.source),
      ExportAllDeclaration(node) {
        if (node.source) {
          checkSource(node.source);
        }
      },
      ExportNamedDeclaration(node) {
        if (node.source) {
          checkSource(node.source);
        }
      },
    };
  },
};
