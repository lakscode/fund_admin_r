import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import settingsData from '../data/settings.json';
import '../components/Layout.css';
import './Settings.css';

const { page, chartOfAccounts } = settingsData;

function Settings() {
  const [currentPage, setCurrentPage] = useState(1);

  const { accounts, totalItems, itemsPerPage, title, description } = chartOfAccounts;
  const mappedCount = accounts.filter((a) => a.status === 'mapped').length;
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <Topbar title={page.title} showLive={false} />

        <div className="settings-content">
          <p className="settings-subtitle">{page.subtitle}</p>

          <div className="coa-card">
            <div className="coa-header">
              <div className="coa-header-text">
                <h2 className="coa-title">{title}</h2>
                <p className="coa-desc">{description}</p>
              </div>
              <span className="coa-badge">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
                {mappedCount}/{totalItems} MAPPED
              </span>
            </div>

            <table className="coa-table">
              <thead>
                <tr>
                  <th>SOURCE GL ACCOUNT</th>
                  <th>STANDARDIZED CATEGORY</th>
                  <th>STATUS</th>
                  <th>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {accounts.map((account) => (
                  <tr key={account.code}>
                    <td className="coa-gl-account">{account.code} - {account.name}</td>
                    <td className={account.status === 'pending' ? 'coa-unassigned' : ''}>{account.category}</td>
                    <td>
                      {account.status === 'mapped' ? (
                        <span className="coa-status mapped">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M22 11.08V12a10 10 0 11-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
                          </svg>
                          Mapped
                        </span>
                      ) : (
                        <span className="coa-status pending">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" />
                          </svg>
                          Pending
                        </span>
                      )}
                    </td>
                    <td>
                      {account.status === 'mapped' ? (
                        <button className="coa-edit-btn" aria-label="Edit mapping">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" /><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                          </svg>
                        </button>
                      ) : (
                        <button className="coa-map-btn">Map Now</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="coa-footer">
              <span className="coa-showing">Showing {startItem}-{endItem} of {totalItems} items</span>
              <div className="coa-pagination">
                <button className="coa-page-btn" disabled={currentPage === 1} onClick={() => setCurrentPage((p) => p - 1)}>Previous</button>
                <button className="coa-page-btn" disabled={endItem >= totalItems} onClick={() => setCurrentPage((p) => p + 1)}>Next</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;
