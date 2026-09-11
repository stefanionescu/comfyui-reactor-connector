import * as v from 'valibot';
import { translate } from '#web/language.ts';
import { browserLimits, browserPatterns } from '#config/web/browser.ts';

const shortTextSchema = v.pipe(
  v.string(),
  v.minLength(1),
  v.maxLength(browserLimits.maxTextCharacters),
);

function isRetrievalTime(value: string): boolean {
  const timestamp = Date.parse(value);
  const parsedDate = new Date(timestamp);
  return Number.isFinite(timestamp) && !Number.isNaN(parsedDate.getTime());
}

const retrievalTimeSchema = v.nullable(
  v.pipe(
    v.string(),
    v.minLength(1),
    v.maxLength(browserLimits.maxRetrievalTimeCharacters),
    v.check(isRetrievalTime),
  ),
);

const modelSchema = v.pipe(
  v.object({
    key: shortTextSchema,
    name: shortTextSchema,
    title: shortTextSchema,
    connect_name: v.nullable(shortTextSchema),
    documentation_url: v.nullable(v.pipe(v.string(), v.regex(browserPatterns.documentation))),
    credits_per_second: v.nullable(v.pipe(v.number(), v.finite(), v.minValue(0))),
    observed: v.boolean(),
    support: v.picklist(['available', 'adapter_required']),
    node_ids: v.pipe(
      v.array(v.pipe(v.string(), v.regex(browserPatterns.nodeId))),
      v.maxLength(browserLimits.maxModelNodeIds),
    ),
  }),
  v.transform((model) => {
    const identity = { entryKey: model.key, modelSlug: model.name, title: model.title };
    const connection = {
      connectionName: model.connect_name,
      documentationUrl: model.documentation_url,
      creditsPerSecond: model.credits_per_second,
    };
    return {
      ...identity,
      ...connection,
      observed: model.observed,
      support: model.support,
      nodeIds: model.node_ids,
    };
  }),
);

const automaticCheckSchema = v.pipe(
  v.object({
    enabled: v.boolean(),
    running: v.boolean(),
    interval_hours: v.pipe(v.number(), v.safeInteger(), v.minValue(1)),
    checked_at: retrievalTimeSchema,
    update_available: v.nullable(v.boolean()),
    error: v.nullable(
      v.pipe(v.string(), v.minLength(1), v.maxLength(browserLimits.maxErrorCharacters)),
    ),
  }),
  v.transform((check) => {
    const schedule = { intervalHours: check.interval_hours, checkedAt: check.checked_at };
    const result = { updateAvailable: check.update_available, error: check.error };
    return { enabled: check.enabled, running: check.running, ...schedule, ...result };
  }),
);

const modelListSchema = v.pipe(
  v.object({
    revision: v.pipe(v.string(), v.regex(browserPatterns.revision)),
    retrieved_at: retrievalTimeSchema,
    models: v.pipe(v.array(modelSchema), v.minLength(1), v.maxLength(browserLimits.maxModels)),
    can_rollback: v.boolean(),
    mutation_allowed: v.boolean(),
    automatic_check: v.optional(automaticCheckSchema),
  }),
  v.check((document) => {
    const keys = new Set<string>();
    for (const model of document.models) {
      if (keys.has(model.entryKey)) return false;
      keys.add(model.entryKey);
    }
    return true;
  }),
  v.transform((document) => {
    const identity = { revision: document.revision, retrievedAt: document.retrieved_at };
    const permissions = {
      canRollback: document.can_rollback,
      mutationAllowed: document.mutation_allowed,
    };
    return {
      ...identity,
      ...permissions,
      models: document.models,
      ...(document.automatic_check === undefined
        ? {}
        : { automaticCheck: document.automatic_check }),
    };
  }),
);

export type Model = v.InferOutput<typeof modelSchema>;
export type ModelList = v.InferOutput<typeof modelListSchema>;

/**
 * Validate and transform a model list returned by the local server.
 * @param value - The untrusted JSON response.
 * @returns The browser model list.
 */
export function parseModelList(value: unknown): ModelList {
  const result = v.safeParse(modelListSchema, value);
  if (!result.success) throw new Error(translate('models.invalidResponse'));
  return result.output;
}
