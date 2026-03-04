export interface FundRow {
  name: string;
  aum: string;
  eum: string;
  cash: string;
  properties: number;
  ytdReturn: string;
  status: string;
}

export interface FundsData {
  page: { title: string; subtitle: string };
  funds: FundRow[];
}
