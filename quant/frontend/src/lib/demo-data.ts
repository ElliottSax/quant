import type { Politician } from './types';

/** Placeholder data shown while the live API loads (or when it is unavailable). */
export const DEMO_POLITICIANS: Politician[] = [
  { id: 'demo-1', name: 'Jane Representative', party: 'Independent', chamber: 'House', state: 'CA', tradeCount: 42 },
  { id: 'demo-2', name: 'John Senator', party: 'Independent', chamber: 'Senate', state: 'NY', tradeCount: 37 },
  { id: 'demo-3', name: 'Alex Congressmember', party: 'Independent', chamber: 'House', state: 'TX', tradeCount: 28 },
];

export default DEMO_POLITICIANS;
