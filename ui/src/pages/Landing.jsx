import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import landingData from '../data/landing.json';
import '../components/Layout.css';
import './Landing.css';

const { page, kpiRow1, kpiRow2, returns, tabs, assetRankings, actionQueue } = landingData;

function Landing() {
  const [activeTab, setActiveTab] = useState(tabs[0]);

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <Topbar title={page.title} />

        <div className="dashboard-content">
          <p className="dashboard-subtitle">{page.subtitle}</p>

          <div className="kpi-row">
            {kpiRow1.map((kpi) => (
              <div className="kpi-card" key={kpi.label} style={{ borderTopColor: kpi.accent }}>
                <span className="kpi-label">{kpi.label}</span>
                <span className="kpi-value">{kpi.value}</span>
                <span className={`kpi-change ${kpi.changeType}`}>{kpi.change}</span>
                <div className="kpi-tags">
                  {kpi.tags.map((t) => (
                    <span className="kpi-tag" key={t}>{t}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="kpi-row secondary">
            {kpiRow2.map((kpi) => (
              <div className="kpi-card secondary" key={kpi.label}>
                <span className="kpi-label">{kpi.label}</span>
                <span className={`kpi-value ${kpi.negative ? 'negative' : ''}`}>{kpi.value}</span>
                <span className="kpi-sub">{kpi.sub}</span>
                <div className="kpi-tags">
                  <span className="kpi-tag">{kpi.tag}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="returns-bar">
            <span className="returns-label">RETURNS</span>
            {returns.map((r) => (
              <div className="returns-group" key={r.period}>
                <span className="returns-period">{r.period}</span>
                <span className="returns-val primary">{r.val1}</span>
                <span className="returns-val muted">{r.val2}</span>
              </div>
            ))}
          </div>

          <div className="tab-bar">
            {tabs.map((tab) => (
              <button
                key={tab}
                className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="bottom-section">
            <div className="assets-panel">
              <h2 className="panel-title">Assets Ranked by Performance and Risk</h2>
              <table className="assets-table">
                <thead>
                  <tr>
                    <th>ASSET NAME</th>
                    <th>YTD YIELD</th>
                    <th>OCCUPANCY</th>
                    <th>WALE</th>
                    <th>RISK SCORE</th>
                  </tr>
                </thead>
                <tbody>
                  {assetRankings.map((a) => (
                    <tr key={a.name}>
                      <td className="asset-name">{a.name}</td>
                      <td className="asset-ytd">{a.ytd}</td>
                      <td>{a.occupancy}</td>
                      <td>{a.wale}</td>
                      <td>
                        <span className={`risk-badge ${a.risk.toLowerCase()}`}>{a.risk}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="action-queue-panel">
              <div className="aq-header">
                <h2 className="panel-title">ACTION QUEUE</h2>
                <span className="aq-badge">{actionQueue.length}</span>
              </div>
              <div className="aq-list">
                {actionQueue.map((a, i) => (
                  <div className="aq-item" key={i}>
                    <div className="aq-item-top">
                      <span className="aq-status" style={{ color: a.statusColor }}>{a.status}</span>
                      <span className="aq-time">{a.time}</span>
                    </div>
                    <p className="aq-title">{a.title}</p>
                    {a.hasLink && <a href="#details" className="aq-link">View Details &rsaquo;</a>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Landing;
