export interface FundOverview {
  nav: string;
  totalEquity: string;
  totalAssets: string;
  totalLiabilities: string;
  netIncome: string;
  noi: string;
  cash: string;
  totalDebt: string;
  ltv: string;
  ytdReturn: string;
}

export interface Allocation {
  city: string;
  value: string;
  percentage: number;
  propertyCount: number;
}

export interface Investor {
  name: string;
  entityId: number;
  type: string;
}

export interface FundStructureEntity {
  entityId: number;
  entityName: string;
  investmentCount: number;
}

export interface FundsData {
  page: { title: string; subtitle: string };
  tabs: string[];
  overview: FundOverview;
  stats: { propertyCount: number; investorCount: number; fundTreeEntities: number };
  allocation: Allocation[];
  investors: Investor[];
  structure: FundStructureEntity[];
}
