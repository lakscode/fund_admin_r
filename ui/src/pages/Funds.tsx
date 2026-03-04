import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import fundsFallback from '../data/funds.json';
import { getFunds } from '../services/api';
import { FundsData } from '../types/funds';
import '../components/Layout.css';
import './Funds.css';

function Funds() {
  const [data, setData] = useState<FundsData>(fundsFallback);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(fundsFallback.tabs[0]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const closeSidebar = () => setSidebarOpen(false);

  useEffect(() => {
    getFunds()
      .then((apiData) => {
        setData(apiData);
        setActiveTab(apiData.tabs?.[0] || fundsFallback.tabs[0]);
      })
      .catch(() => {
        setData(fundsFallback);
      })
      .finally(() => setLoading(false));
  }, []);

  const { page, tabs, overview, stats, allocation, investors, structure } = data;

  if (loading) {
    return (
      <div className="dashboard-layout">
        <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
        <div className="dashboard-main">
          <Topbar title="Fund Overview" onMenuToggle={toggleSidebar} />
          <div className="funds-content">
            <div className="loading-overlay">
              <svg className="loading-spinner" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="2" x2="12" y2="6" /><line x1="12" y1="18" x2="12" y2="22" />
                <line x1="4.93" y1="4.93" x2="7.76" y2="7.76" /><line x1="16.24" y1="16.24" x2="19.07" y2="19.07" />
                <line x1="2" y1="12" x2="6" y2="12" /><line x1="18" y1="12" x2="22" y2="12" />
                <line x1="4.93" y1="19.07" x2="7.76" y2="16.24" /><line x1="16.24" y1="7.76" x2="19.07" y2="4.93" />
              </svg>
              <p className="loading-text">Loading fund data...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      <div className="dashboard-main">
        <Topbar title={page.title} onMenuToggle={toggleSidebar} />

        <div className="funds-content">
          <p className="funds-subtitle">{page.subtitle}</p>

          <div className="funds-tab-bar">
            {tabs.map((tab) => (
              <button
                key={tab}
                className={`funds-tab-btn ${activeTab === tab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="funds-stats-row">
            <div className="funds-stat-card">
              <span className="funds-stat-value">{stats.propertyCount}</span>
              <span className="funds-stat-label">Properties</span>
            </div>
            <div className="funds-stat-card">
              <span className="funds-stat-value">{stats.investorCount}</span>
              <span className="funds-stat-label">Investors</span>
            </div>
            <div className="funds-stat-card">
              <span className="funds-stat-value">{stats.fundTreeEntities}</span>
              <span className="funds-stat-label">Fund Tree Entities</span>
            </div>
          </div>

          <div className="funds-overview-grid">
            <div className="funds-overview-card highlight">
              <span className="fo-label">NAV</span>
              <span className="fo-value">{overview.nav}</span>
            </div>
            <div className="funds-overview-card highlight">
              <span className="fo-label">Total Equity</span>
              <span className="fo-value">{overview.totalEquity}</span>
            </div>
            <div className="funds-overview-card">
              <span className="fo-label">Total Assets</span>
              <span className="fo-value">{overview.totalAssets}</span>
            </div>
            <div className="funds-overview-card warn">
              <span className="fo-label">Total Liabilities</span>
              <span className="fo-value">{overview.totalLiabilities}</span>
            </div>
            <div className="funds-overview-card accent">
              <span className="fo-label">Net Income</span>
              <span className="fo-value">{overview.netIncome}</span>
            </div>
            <div className="funds-overview-card">
              <span className="fo-label">NOI</span>
              <span className="fo-value">{overview.noi}</span>
            </div>
            <div className="funds-overview-card highlight">
              <span className="fo-label">Cash</span>
              <span className="fo-value">{overview.cash}</span>
            </div>
            <div className="funds-overview-card warn">
              <span className="fo-label">Total Debt</span>
              <span className="fo-value">{overview.totalDebt}</span>
            </div>
            <div className="funds-overview-card">
              <span className="fo-label">LTV</span>
              <span className="fo-value">{overview.ltv}</span>
            </div>
            <div className="funds-overview-card accent">
              <span className="fo-label">YTD Return</span>
              <span className="fo-value">{overview.ytdReturn}</span>
            </div>
          </div>

          <div className="funds-bottom-grid">
            <div className="funds-panel">
              <h2 className="funds-panel-title">Property Allocation</h2>
              {allocation.map((a) => (
                <div className="alloc-item" key={a.city}>
                  <div className="alloc-header">
                    <span className="alloc-city">{a.city}</span>
                    <span className="alloc-value">{a.value}</span>
                  </div>
                  <div className="alloc-bar-bg">
                    <div className="alloc-bar-fill" style={{ width: `${a.percentage}%` }} />
                  </div>
                  <span className="alloc-meta">{a.propertyCount} properties · {a.percentage}%</span>
                </div>
              ))}
            </div>

            <div className="funds-panel">
              <h2 className="funds-panel-title">Investors</h2>
              <ul className="investor-list">
                {investors.map((inv) => (
                  <li className="investor-item" key={inv.entityId}>
                    <span className="investor-name">{inv.name}</span>
                    <span className="investor-type">{inv.type}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="funds-panel">
              <h2 className="funds-panel-title">Fund Structure</h2>
              {structure.map((s) => (
                <div className="structure-item" key={s.entityId}>
                  <span className="structure-name">{s.entityName}</span>
                  <span className="structure-count">{s.investmentCount}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Funds;
