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
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const closeSidebar = () => setSidebarOpen(false);

  useEffect(() => {
    getFunds()
      .then((apiData) => setData(apiData))
      .catch(() => setData(fundsFallback))
      .finally(() => setLoading(false));
  }, []);

  const { page, funds } = data;

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      <div className="dashboard-main">
        <Topbar title={page.title} onMenuToggle={toggleSidebar} />

        <div className="funds-content">
          <p className="funds-subtitle">{page.subtitle}</p>

          {loading ? (
            <div className="loading-overlay">
              <svg className="loading-spinner" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="2" x2="12" y2="6" /><line x1="12" y1="18" x2="12" y2="22" />
                <line x1="4.93" y1="4.93" x2="7.76" y2="7.76" /><line x1="16.24" y1="16.24" x2="19.07" y2="19.07" />
                <line x1="2" y1="12" x2="6" y2="12" /><line x1="18" y1="12" x2="22" y2="12" />
                <line x1="4.93" y1="19.07" x2="7.76" y2="16.24" /><line x1="16.24" y1="7.76" x2="19.07" y2="4.93" />
              </svg>
              <p className="loading-text">Loading fund data...</p>
            </div>
          ) : (
            <div className="funds-table-wrapper">
              <table className="funds-table">
                <thead>
                  <tr>
                    <th>Fund Name</th>
                    <th>AUM</th>
                    <th>EUM</th>
                    <th>Cash</th>
                    <th>Properties</th>
                    <th>YTD Return</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {funds.map((fund) => (
                    <tr key={fund.name}>
                      <td className="fund-name-cell">{fund.name}</td>
                      <td>{fund.aum}</td>
                      <td>{fund.eum}</td>
                      <td>{fund.cash}</td>
                      <td>{fund.properties}</td>
                      <td className="fund-return-cell">{fund.ytdReturn}</td>
                      <td>
                        <span className={`fund-status-badge ${fund.status.toLowerCase()}`}>
                          {fund.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Funds;
