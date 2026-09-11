type DurationInputs = readonly [string, string];
type NodePricingRules = Readonly<{
  excludedNodeIds: readonly string[];
  multipliedDurationInputs: Readonly<Record<string, DurationInputs>>;
}>;

const fastContinueNodeId = 'ReactorIncFastContinue';

/** Node-specific behavior used by the local credit-rate interface. */
export const nodePricingRules: NodePricingRules = {
  excludedNodeIds: ['ReactorIncHeliosAddPrompt', 'ReactorIncLongLiveAddShot'],
  multipliedDurationInputs: {
    [fastContinueNodeId]: ['clip_seconds', 'clip_count'],
  },
};
