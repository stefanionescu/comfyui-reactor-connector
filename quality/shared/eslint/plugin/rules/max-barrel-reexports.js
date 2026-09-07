import { isIndexFile } from '#shared/eslint/plugin/path-policy/index-file.js';
import { normalizeFilename } from '#shared/eslint/plugin/path-policy/normalization.js';

export const maxBarrelReexports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Limit the number of re-exports in barrel (index) files.',
    },
    schema: [
      {
        type: 'object',
        properties: {
          max: { type: 'integer', minimum: 1 },
        },
        additionalProperties: false,
      },
    ],
  },
  create(context) {
    const filename = context.getFilename?.() ?? '';
    const normalized = normalizeFilename(filename);

    if (!normalized || normalized === '<input>' || !isIndexFile(normalized)) {
      return {};
    }

    const max = (context.options[0] && context.options[0].max) || 5;
    const reexportNodes = [];

    return {
      ExportAllDeclaration: (node) => reexportNodes.push(node),
      ExportNamedDeclaration(node) {
        if (node.source) {
          reexportNodes.push(node);
        }
      },
      'Program:exit'() {
        if (reexportNodes.length > max) {
          for (const node of reexportNodes) {
            context.report({
              node,
              message: `Barrel file has ${reexportNodes.length} re-exports, exceeding the maximum of ${max}. Export a single map/item instead.`,
            });
          }
        }
      },
    };
  },
};
