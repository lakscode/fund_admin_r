export interface LeasingKpiCard {
  label: string;
  icon: string;
  value: string;
  unit: string;
  sub: string;
  dotColor: string;
}

export interface ChartDataPoint {
  quarter: string;
  renewed: number;
  potential: number;
}

export interface LeasingAction {
  icon: string;
  color: string;
  bgColor: string;
  title: string;
  impact: string;
  reason: string;
  next: string;
}

export interface LeasingData {
  page: { title: string; subtitle: string };
  tabs: string[];
  kpiCards: LeasingKpiCard[];
  chartData: ChartDataPoint[];
  actionQueue: LeasingAction[];
}
