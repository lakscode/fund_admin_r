import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import leasingData from '../data/leasing.json';
import '../components/Layout.css';
import './Leasing.css';

const { page, tabs, kpiCards, chartData, actionQueue } = leasingData;

function KpiIcon({ type }) {
  const props = { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', stroke: '#8b8ba3', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round' };
  switch (type) {
    case 'clock':
      return <svg {...props}><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>;
    case 'dollar':
      return <svg {...props}><line x1="12" y1="1" x2="12" y2="23" /><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" /></svg>;
    case 'timer':
      return <svg {...props}><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 8 14" /></svg>;
    case 'calendar':
      return <svg {...props}><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>;
    default:
      return null;
  }
}

function ActionIcon({ type, color }) {
  const props = { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: color, strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round' };
  switch (type) {
    case 'warning':
      return <svg {...props}><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>;
    case 'document':
      return <svg {...props}><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>;
    case 'chart':
      return <svg {...props}><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>;
    default:
      return null;
  }
}

function Leasing() {
  const [activeTab, setActiveTab] = useState(tabs[0]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const closeSidebar = () => setSidebarOpen(false);

  const maxBarHeight = Math.max(...chartData.map((d) => d.renewed + d.potential));

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      <div className="dashboard-main">
        <Topbar title={page.title} onMenuToggle={toggleSidebar} />

        <div className="leasing-content">
          <p className="leasing-subtitle">{page.subtitle}</p>

          <div className="leasing-tab-bar">
            {tabs.map((tab) => (
              <button
                key={tab}
                className={`leasing-tab-btn ${activeTab === tab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="leasing-grid">
            <div className="leasing-left">
              <div className="leasing-kpi-row">
                {kpiCards.map((kpi) => (
                  <div className="leasing-kpi-card" key={kpi.label}>
                    <div className="lkpi-header">
                      <span className="lkpi-label">{kpi.label}</span>
                      <KpiIcon type={kpi.icon} />
                    </div>
                    <div className="lkpi-value-row">
                      <span className="lkpi-value">{kpi.value}</span>
                      {kpi.unit && <span className="lkpi-unit">{kpi.unit}</span>}
                    </div>
                    <div className="lkpi-sub">
                      <span className="lkpi-dot" style={{ backgroundColor: kpi.dotColor }} />
                      <span>{kpi.sub}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="leasing-chart-card">
                <div className="chart-header">
                  <h2 className="chart-title">Lease Expiry Exposure by Quarter</h2>
                  <div className="chart-legend">
                    <span className="legend-item">
                      <span className="legend-swatch renewed" />
                      Renewed
                    </span>
                    <span className="legend-item">
                      <span className="legend-swatch potential" />
                      Potential
                    </span>
                  </div>
                </div>
                <div className="chart-area">
                  <div className="chart-bars">
                    {chartData.map((d) => {
                      const renewedPct = (d.renewed / maxBarHeight) * 100;
                      const potentialPct = (d.potential / maxBarHeight) * 100;
                      return (
                        <div className="chart-col" key={d.quarter}>
                          <div className="bar-stack">
                            <div className="bar renewed" style={{ height: `${renewedPct}%` }} />
                            <div className="bar potential" style={{ height: `${potentialPct}%` }} />
                          </div>
                          <span className="chart-label">{d.quarter}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            <div className="leasing-right">
              <div className="leasing-aq">
                <div className="leasing-aq-header">
                  <span className="leasing-aq-title">ACTION QUEUE</span>
                  <span className="leasing-aq-badge">{actionQueue.length} TASKS</span>
                </div>
                <div className="leasing-aq-list">
                  {actionQueue.map((item, i) => (
                    <div
                      className="leasing-aq-card"
                      key={i}
                      style={{ borderLeftColor: item.color, backgroundColor: item.bgColor }}
                    >
                      <div className="laq-card-icon">
                        <ActionIcon type={item.icon} color={item.color} />
                      </div>
                      <div className="laq-card-body">
                        <p className="laq-card-title">{item.title}</p>
                        <div className="laq-meta">
                          <span className="laq-meta-label">IMPACT</span>
                          <span className="laq-meta-value">{item.impact}</span>
                        </div>
                        <div className="laq-meta">
                          <span className="laq-meta-label">REASON</span>
                          <span className="laq-meta-value">{item.reason}</span>
                        </div>
                        <div className="laq-meta next">
                          <span className="laq-meta-label">NEXT:</span>
                          <span className="laq-meta-value bold">{item.next}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <button className="leasing-aq-view-btn">
                  VIEW FULL QUEUE &rarr;
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Leasing;
