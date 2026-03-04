export interface Property {
  name: string;
  id: string;
  market: string;
  type: string;
  noiYtd: string;
  noiVsBudget: string;
  noiVsType: string;
  occupancy: string;
  dscr: string;
  rentExpiring: string;
  risk: string;
  monthEnd: string;
}

export interface SummaryCard {
  label: string;
  icon: string;
  value: string;
  sub: string;
  subColor: string;
  accent: string;
}

export interface AssetsData {
  page: { title: string; subtitle: string };
  properties: Property[];
  pagination: { totalItems: number; itemsPerPage: number };
  filters: { markets: string[]; types: string[] };
  summaryCards: SummaryCard[];
}
