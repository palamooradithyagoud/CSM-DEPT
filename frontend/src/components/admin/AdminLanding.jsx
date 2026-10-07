import React from 'react';
import { ShieldCheck, UserCheck, Layers, Database, BarChart3, AlertOctagon, LogOut, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function AdminLanding({ onBackToPublic }) {
  const { user, logout } = useAuth();

  const phaseCards = [
    {
      phase: 'Phase 1',
      title: 'Foundation & Public Department Portal',
      status: 'COMPLETED & LIVE',
      isLive: true,
      items: [
        'Modular Flask application factory & SQLAlchemy ORM',
        'Strict dark academic design system (#050506, #32DC5C)',
        'Zero student academic data leakage on public routes',
        'JWT Role-Based Access Control (HOD/Admin tokens)',
      ],
    },
    {
      phase: 'Phase 2 (Next)',
      title: 'Student & Academic Data Management',
      status: 'READY FOR SCRIPTING',
      isLive: false,
      items: [
        'Unified 2nd, 3rd, and 4th Year Student Schema',
        'Two-Stage CSV / Excel Ingestion Engine (Preview -> Validation -> Confirm)',
        'Subject-wise mark, grade & attendance percentage parser',
        'Batch duplicate and validation error diagnostics',
      ],
    },
    {
      phase: 'Phase 3',
      title: 'Academic Analytics & Comparison Engine',
      status: 'PLANNED',
      isLive: false,
      items: [
        'Semester-by-semester SGPA & CGPA delta calculations',
        'Subject performance trajectory mapping (Improved / Declined / Stable)',
        'Department, Year & Section hierarchy drill-down',
        'Subject-wise attendance vs performance matrices',
      ],
    },
    {
      phase: 'Phase 4',
      title: 'Problem Identification & Insights',
      status: 'PLANNED',
      isLive: false,
      items: [
        'Automated watchlist of students requiring urgent attention',
        'Multi-subject failure & grade decline detection',
        'Subjects with high failure or sharp drop alerts',
        'Attendance conditional risk grouping (<75% threshold)',
      ],
    },
  ];

  return (
    <div className="admin-landing-root">
      {/* Top Header */}
      <header className="admin-header">
        <div className="container admin-header-inner">
          <div className="header-brand-block">
            <button onClick={onBackToPublic} className="back-btn" title="View Public Portal">
              <ArrowLeft size={16} />
              <span>Public Portal</span>
            </button>
            <div className="admin-title-wrap">
              <span className="badge badge-success">Authenticated</span>
              <h1 className="admin-main-title">HOD Academic Intelligence Workspace</h1>
            </div>
          </div>

          <div className="admin-user-badge">
            <div className="user-icon-circle">
              <UserCheck size={18} />
            </div>
            <div className="user-text">
              <span className="user-name">{user?.fullName || "Dr. M. A. Jabbar"}</span>
              <span className="user-role-dept">{user?.role} • {user?.department || "CSE"}</span>
            </div>
            <button onClick={logout} className="btn btn-secondary btn-sm" title="Log Out">
              <LogOut size={14} />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="container admin-body">
        {/* Verification Alert Banner */}
        <div className="auth-status-card">
          <div className="status-icon-wrap">
            <ShieldCheck size={28} />
          </div>
          <div className="status-text-block">
            <h2 className="status-heading">Authentication & Role Contract Verified</h2>
            <p className="status-desc">
              You are securely authenticated as <strong>{user?.fullName}</strong> with role <strong>{user?.role}</strong>. 
              API calls made from this session transmit authorized JWT bearer tokens to private Flask backend endpoints. 
              Phase 1 foundation is fully functional.
            </p>
          </div>
        </div>

        {/* System Roadmap Grid */}
        <div className="roadmap-header">
          <h3 className="roadmap-title">Department Management System Roadmap</h3>
          <span className="roadmap-sub">Phase-by-phase development contract</span>
        </div>

        <div className="roadmap-grid">
          {phaseCards.map((p, idx) => (
            <div key={idx} className={`roadmap-card ${p.isLive ? 'card-active' : ''}`}>
              <div className="card-top-row">
                <span className="phase-pill">{p.phase}</span>
                <span className={`status-pill ${p.isLive ? 'status-live' : 'status-pending'}`}>
                  {p.status}
                </span>
              </div>

              <h4 className="phase-card-title">{p.title}</h4>

              <ul className="phase-card-list">
                {p.items.map((item, iIdx) => (
                  <li key={iIdx} className="phase-list-item">
                    <CheckCircle2 size={14} className={p.isLive ? 'item-icon-live' : 'item-icon-pending'} />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </main>

      <style>{`
        .admin-landing-root {
          min-height: 100vh;
          background-color: var(--color-background);
          color: var(--color-text-main);
          display: flex;
          flex-direction: column;
        }
        .admin-header {
          background: var(--color-card);
          border-bottom: 1px solid var(--color-border);
          padding: 16px 0;
        }
        .admin-header-inner {
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 16px;
        }
        .header-brand-block {
          display: flex;
          align-items: center;
          gap: 16px;
        }
        .back-btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          padding: 6px 12px;
          border-radius: var(--radius-sm);
          transition: all var(--transition-fast);
        }
        .back-btn:hover {
          color: var(--color-primary);
          border-color: var(--color-primary-border);
        }
        .admin-title-wrap {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .admin-main-title {
          font-size: 1.125rem;
          font-weight: 700;
        }
        .admin-user-badge {
          display: flex;
          align-items: center;
          gap: 12px;
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          padding: 6px 14px;
          border-radius: var(--radius-md);
        }
        .user-icon-circle {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: var(--color-card);
          border: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--color-primary);
        }
        .user-text {
          display: flex;
          flex-direction: column;
        }
        .user-name {
          font-size: 0.8125rem;
          font-weight: 700;
          color: var(--color-text-main);
        }
        .user-role-dept {
          font-size: 0.6875rem;
          color: var(--color-text-muted);
        }
        .admin-body {
          padding-top: var(--space-2xl);
          padding-bottom: var(--space-3xl);
          flex-grow: 1;
        }
        .auth-status-card {
          display: flex;
          align-items: flex-start;
          gap: 18px;
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-left: 4px solid var(--color-primary);
          border-radius: var(--radius-lg);
          padding: var(--space-xl);
          margin-bottom: var(--space-2xl);
        }
        .status-icon-wrap {
          color: var(--color-primary);
          flex-shrink: 0;
          margin-top: 2px;
        }
        .status-heading {
          font-size: 1.1875rem;
          font-weight: 700;
          margin-bottom: 4px;
        }
        .status-desc {
          font-size: 0.9375rem;
          color: var(--color-text-secondary);
          line-height: 1.6;
        }
        .roadmap-header {
          margin-bottom: var(--space-lg);
        }
        .roadmap-title {
          font-size: 1.25rem;
          font-weight: 700;
        }
        .roadmap-sub {
          font-size: 0.8125rem;
          color: var(--color-text-muted);
        }
        .roadmap-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: var(--space-xl);
        }
        .roadmap-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-xl);
          display: flex;
          flex-direction: column;
        }
        .card-active {
          border-color: #32dc5c55;
          box-shadow: 0 0 20px rgba(50, 220, 92, 0.05);
        }
        .card-top-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: var(--space-md);
        }
        .phase-pill {
          font-size: 0.75rem;
          font-weight: 700;
          color: var(--color-primary);
          background: var(--color-primary-subtle);
          padding: 2px 8px;
          border-radius: var(--radius-sm);
        }
        .status-pill {
          font-size: 0.6875rem;
          font-weight: 600;
          padding: 2px 8px;
          border-radius: var(--radius-sm);
        }
        .status-live {
          color: var(--color-primary);
          background: var(--color-secondary);
          border: 1px solid var(--color-primary-border);
        }
        .status-pending {
          color: var(--color-text-muted);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
        }
        .phase-card-title {
          font-size: 1.0625rem;
          font-weight: 700;
          color: var(--color-text-main);
          margin-bottom: var(--space-md);
        }
        .phase-card-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .phase-list-item {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          line-height: 1.4;
        }
        .item-icon-live {
          color: var(--color-primary);
          flex-shrink: 0;
          margin-top: 2px;
        }
        .item-icon-pending {
          color: var(--color-text-muted);
          flex-shrink: 0;
          margin-top: 2px;
        }
        @media (max-width: 800px) {
          .roadmap-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}
