export interface AssetRanking {
  name: string;
  risk: string;
  ytd?: string;
  occupancy?: string;
  wale?: string;
  marketValue?: string;
  city?: string;
  province?: string;
}

export interface LandingData {
  page: { title: string; subtitle: string };
  kpiRow1: { label: string; value: string; change: string; changeType: string; tags: string[]; accent: string }[];
  kpiRow2: { label: string; value: string; sub: string; tag: string; negative: boolean }[];
  returns: { period: string; val1: string; val2: string }[];
  tabs: string[];
  assetRankings: AssetRanking[];
  actionQueue: { status: string; statusColor: string; time: string; title: string; hasLink: boolean }[];
}
