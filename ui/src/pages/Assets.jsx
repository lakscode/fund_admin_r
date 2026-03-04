import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import assetsData from '../data/assets.json';
import '../components/Layout.css';
import './Assets.css';

const { page, properties, pagination, filters, summaryCards } = assetsData;
const TOTAL_PAGES = Math.ceil(pagination.totalItems / pagination.itemsPerPage);

function SummaryIcon({ type, color }) {
  const props = { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: color, strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round' };
  switch (type) {
    case 'trend':
      return <svg {...props}><polyline points="23 6 13.5 15.5 8.5 10.5 1 18" /><polyline points="17 6 23 6 23 12" /></svg>;
    case 'clock':
      return <svg {...props}><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>;
    case 'calendar':
      return <svg {...props}><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>;
    default:
      return null;
  }
}

function Assets() {
  const [search, setSearch] = useState('');
  const [marketFilter, setMarketFilter] = useState(filters.markets[0]);
  const [typeFilter, setTypeFilter] = useState(filters.types[0]);
  const [currentPage, setCurrentPage] = useState(1);

  const filtered = properties.filter((a) => {
    const matchSearch = !search || a.name.toLowerCase().includes(search.toLowerCase()) || a.id.toLowerCase().includes(search.toLowerCase()) || a.market.toLowerCase().includes(search.toLowerCase());
    const matchMarket = marketFilter === filters.markets[0] || a.market === marketFilter;
    const matchType = typeFilter === filters.types[0] || a.type === typeFilter;
    return matchSearch && matchMarket && matchType;
  });

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <Topbar title={page.title} />

        <div className="assets-content">
          <p className="assets-subtitle">{page.subtitle}</p>

          <div className="assets-filter-bar">
            <div className="assets-search-wrap">
              <svg className="assets-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                type="text"
                className="assets-search"
                placeholder="Search property name, city, or ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <select className="assets-select" value={marketFilter} onChange={(e) => setMarketFilter(e.target.value)}>
              {filters.markets.map((m) => <option key={m}>{m}</option>)}
            </select>
            <select className="assets-select" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              {filters.types.map((t) => <option key={t}>{t}</option>)}
            </select>
            <button className="assets-filters-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="4" y1="21" x2="4" y2="14" /><line x1="4" y1="10" x2="4" y2="3" /><line x1="12" y1="21" x2="12" y2="12" /><line x1="12" y1="8" x2="12" y2="3" /><line x1="20" y1="21" x2="20" y2="16" /><line x1="20" y1="12" x2="20" y2="3" />
              </svg>
              Filters
            </button>
            <button className="assets-add-btn">+ Add Asset</button>
          </div>

          <div className="assets-table-card">
            <table className="ap-table">
              <thead>
                <tr>
                  <th>PROPERTY NAME</th>
                  <th>MARKET</th>
                  <th>TYPE</th>
                  <th>NOI YTD</th>
                  <th>NOI VS BUDGET</th>
                  <th>OCCUPANCY</th>
                  <th>DSCR</th>
                  <th>RENT EXPIRING (6mo)</th>
                  <th>RISK</th>
                  <th>MONTH-END</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((asset) => (
                  <tr key={asset.id}>
                    <td>
                      <div className="ap-property-cell">
                        <span className="ap-property-name">{asset.name}</span>
                        <span className="ap-property-id">{asset.id}</span>
                      </div>
                    </td>
                    <td>{asset.market}</td>
                    <td>{asset.type}</td>
                    <td className="ap-noi">{asset.noiYtd}</td>
                    <td className={`ap-budget ${asset.noiVsType}`}>{asset.noiVsBudget}</td>
                    <td>{asset.occupancy}</td>
                    <td>{asset.dscr}</td>
                    <td>{asset.rentExpiring}</td>
                    <td>
                      <span className={`ap-risk-badge ${asset.risk.toLowerCase()}`}>{asset.risk}</span>
                    </td>
                    <td>
                      <span className={`ap-me-status ${asset.monthEnd.replace(/\s/g, '-').toLowerCase()}`}>{asset.monthEnd}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="ap-footer">
              <span className="ap-showing">Showing {filtered.length} of {pagination.totalItems} assets</span>
              <div className="ap-pagination">
                <button className="ap-page-btn" disabled={currentPage === 1} onClick={() => setCurrentPage((p) => p - 1)}>Previous</button>
                {Array.from({ length: TOTAL_PAGES }, (_, i) => i + 1).slice(0, 3).map((pg) => (
                  <button key={pg} className={`ap-page-num ${currentPage === pg ? 'active' : ''}`} onClick={() => setCurrentPage(pg)}>{pg}</button>
                ))}
                <button className="ap-page-btn" disabled={currentPage >= TOTAL_PAGES} onClick={() => setCurrentPage((p) => p + 1)}>Next</button>
              </div>
            </div>
          </div>

          <div className="ap-summary-row">
            {summaryCards.map((card) => (
              <div className="ap-summary-card" key={card.label} style={{ borderTopColor: card.accent }}>
                <div className="ap-summary-header">
                  <span className="ap-summary-label">{card.label}</span>
                  <SummaryIcon type={card.icon} color={card.accent} />
                </div>
                <span className="ap-summary-value">{card.value}</span>
                <span className="ap-summary-sub" style={{ color: card.subColor }}>{card.sub}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Assets;
