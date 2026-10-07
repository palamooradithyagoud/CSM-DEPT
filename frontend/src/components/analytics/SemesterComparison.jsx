import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  ChevronLeft,
  ChevronRight,
  Info,
} from 'lucide-react';
import { api } from '../../services/api';

export default function SemesterComparison({ batchId, sectionId, semesters, onSelectStudent }) {
  const [sem1Id, setSem1Id] = useState('');
  const [sem2Id, setSem2Id] = useState('');
  const [tolerance, setTolerance] = useState(0.10);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL'); // 'ALL' | 'IMPROVED' | 'DECLINED' | 'STABLE'
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 15;

  // Auto-select Semester 1 and Semester 2 if available
  useEffect(() => {
    if (semesters && semesters.length >= 2) {
      const s1 = semesters.find((s) => s.semesterNumber === 1) || semesters[0];
      const s2 = semesters.find((s) => s.semesterNumber === 2) || semesters[1];
      setSem1Id(s1.id);
      setSem2Id(s2.id);
    }
  }, [semesters]);

  const loadComparison = () => {
    if (!sem1Id || !sem2Id) return;
    setLoading(true);
    api.getSemesterComparison({
      batch_id: batchId,
      sem1_id: sem1Id,
      sem2_id: sem2Id,
      section_id: sectionId || undefined,
      tolerance: tolerance,
    }).then((res) => {
      setData(res);
      setLoading(false);
    }).catch((err) => {
      console.error(err);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadComparison();
  }, [sem1Id, sem2Id, sectionId, tolerance]);

  const renderStatusBadge = (status) => {
    switch (status) {
      case 'IMPROVED':
        return (
          <span className="badge badge-success">
            <TrendingUp size={12} /> IMPROVED
          </span>
        );
      case 'DECLINED':
        return (
          <span className="badge badge-danger">
            <TrendingDown size={12} /> DECLINED
          </span>
        );
      case 'STABLE':
        return (
          <span className="badge badge-outline">
            <Minus size={12} /> STABLE
          </span>
        );
      default:
        return <span className="badge badge-outline">{status}</span>;
    }
  };

  // Filter students
  const rawStudents = data?.students || [];
  const filteredStudents = rawStudents.filter((stu) => {
    const matchesSearch =
      stu.rollNumber.toLowerCase().includes(search.toLowerCase()) ||
      stu.studentName.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || stu.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const totalPages = Math.ceil(filteredStudents.length / pageSize) || 1;
  const currentStudents = filteredStudents.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="semester-comparison-view">
      <div className="view-header-flex">
        <div>
          <h2 className="admin-page-title">Longitudinal Semester-to-Semester Comparison</h2>
          <p className="admin-page-subtitle">
            Evaluate cohort trajectory across consecutive academic semesters with deterministic classification rules.
          </p>
        </div>
      </div>

      {/* Selector Controls Bar */}
      <div className="card comparison-selectors-card">
        <div className="comparison-selectors-row">
          <div className="form-group">
            <label>Baseline Semester (T1)</label>
            <select
              value={sem1Id}
              onChange={(e) => setSem1Id(e.target.value)}
              className="form-select form-select-sm"
            >
              {semesters.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="arrow-separator">→</div>

          <div className="form-group">
            <label>Comparison Semester (T2)</label>
            <select
              value={sem2Id}
              onChange={(e) => setSem2Id(e.target.value)}
              className="form-select form-select-sm"
            >
              {semesters.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>SGPA Stability Tolerance (±)</label>
            <select
              value={tolerance}
              onChange={(e) => setTolerance(parseFloat(e.target.value))}
              className="form-select form-select-sm"
            >
              <option value={0.05}>± 0.05 SGPA (Strict)</option>
              <option value={0.10}>± 0.10 SGPA (Standard)</option>
              <option value={0.20}>± 0.20 SGPA (Broad)</option>
            </select>
          </div>
        </div>

        <div className="rule-explanation-box">
          <Info size={14} className="text-muted" />
          <span className="text-muted text-xs">
            Deterministic Rule: Delta &gt; +{tolerance} = <strong>IMPROVED</strong> | Delta &lt; -{tolerance} = <strong>DECLINED</strong> | Otherwise = <strong>STABLE</strong>.
          </span>
        </div>
      </div>

      {loading ? (
        <div className="analytics-loading-box card">
          <div className="spin-loader" />
          <span>Computing longitudinal progression deltas...</span>
        </div>
      ) : !data || !data.available ? (
        <div className="card empty-analytics-card">
          <Clock size={24} className="text-muted" />
          <p>{data?.message || 'Both selected semesters must have official result data uploaded.'}</p>
        </div>
      ) : (
        <>
          {/* Summary KPI Strip */}
          {data.summary && (
            <div className="comparison-kpi-grid">
              <div className="card kpi-card">
                <span className="kpi-label">Compared Cohort</span>
                <span className="kpi-value font-mono">{data.summary.studentsCompared}</span>
                <span className="kpi-subtext text-muted">Students present in both semesters</span>
              </div>

              <div className="card kpi-card border-green">
                <span className="kpi-label">Improved</span>
                <div className="kpi-split-val">
                  <span className="kpi-value font-mono text-primary">{data.summary.improvedCount}</span>
                  <span className="kpi-pct-badge bg-green-subtle text-primary font-mono">
                    {data.summary.improvedPercentage}%
                  </span>
                </div>
                <span className="kpi-subtext text-muted">Delta &gt; +{tolerance} SGPA</span>
              </div>

              <div className="card kpi-card">
                <span className="kpi-label">Stable</span>
                <div className="kpi-split-val">
                  <span className="kpi-value font-mono">{data.summary.stableCount}</span>
                  <span className="kpi-pct-badge font-mono">
                    {data.summary.stablePercentage}%
                  </span>
                </div>
                <span className="kpi-subtext text-muted">Within ±{tolerance} SGPA band</span>
              </div>

              <div className="card kpi-card border-red">
                <span className="kpi-label">Declined</span>
                <div className="kpi-split-val">
                  <span className="kpi-value font-mono text-danger">{data.summary.declinedCount}</span>
                  <span className="kpi-pct-badge bg-red-subtle text-danger font-mono">
                    {data.summary.declinedPercentage}%
                  </span>
                </div>
                <span className="kpi-subtext text-muted">Delta &lt; -{tolerance} SGPA</span>
              </div>

              <div className="card kpi-card">
                <span className="kpi-label">Average Cohort Delta</span>
                <span className={`kpi-value font-mono ${data.summary.averageChange >= 0 ? 'text-primary' : 'text-danger'}`}>
                  {data.summary.averageChange >= 0 ? `+${data.summary.averageChange}` : data.summary.averageChange}
                </span>
                <span className="kpi-subtext text-muted">
                  {data.summary.averageSem1SGPA} → {data.summary.averageSem2SGPA} SGPA
                </span>
              </div>
            </div>
          )}

          {/* Table Search & Filter Bar */}
          <div className="card table-card">
            <div className="table-controls-bar">
              <div className="search-input-wrap">
                <Search size={14} className="text-muted" />
                <input
                  type="text"
                  placeholder="Filter by roll number or student name..."
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    setPage(1);
                  }}
                  className="search-input"
                />
              </div>

              <div className="status-filter-pills">
                <button
                  className={`filter-pill ${statusFilter === 'ALL' ? 'active' : ''}`}
                  onClick={() => { setStatusFilter('ALL'); setPage(1); }}
                >
                  All ({rawStudents.length})
                </button>
                <button
                  className={`filter-pill text-primary ${statusFilter === 'IMPROVED' ? 'active' : ''}`}
                  onClick={() => { setStatusFilter('IMPROVED'); setPage(1); }}
                >
                  Improved ({data.summary?.improvedCount ?? 0})
                </button>
                <button
                  className={`filter-pill ${statusFilter === 'STABLE' ? 'active' : ''}`}
                  onClick={() => { setStatusFilter('STABLE'); setPage(1); }}
                >
                  Stable ({data.summary?.stableCount ?? 0})
                </button>
                <button
                  className={`filter-pill text-danger ${statusFilter === 'DECLINED' ? 'active' : ''}`}
                  onClick={() => { setStatusFilter('DECLINED'); setPage(1); }}
                >
                  Declined ({data.summary?.declinedCount ?? 0})
                </button>
              </div>
            </div>

            {/* Students Comparison Table */}
            <div className="table-responsive">
              <table className="comparison-table">
                <thead>
                  <tr>
                    <th>Roll Number</th>
                    <th>Student Name</th>
                    <th>Section</th>
                    <th>{data.sem1Name} SGPA</th>
                    <th>{data.sem2Name} SGPA</th>
                    <th>Change (Delta)</th>
                    <th>Status</th>
                    {onSelectStudent && <th>Action</th>}
                  </tr>
                </thead>
                <tbody>
                  {currentStudents.length === 0 ? (
                    <tr>
                      <td colSpan={onSelectStudent ? "8" : "7"} className="text-center empty-cell">
                        No students match the selected filter.
                      </td>
                    </tr>
                  ) : (
                    currentStudents.map((s) => (
                      <tr key={s.studentId}>
                        <td className="font-mono text-primary font-semibold">
                          {onSelectStudent ? (
                            <button
                              onClick={() => onSelectStudent(s.studentId)}
                              className="text-primary hover:underline bg-transparent border-0 p-0 font-mono font-semibold cursor-pointer text-left"
                              title="Drill down to Student Analytics"
                            >
                              {s.rollNumber}
                            </button>
                          ) : (
                            s.rollNumber
                          )}
                        </td>
                        <td className="font-semibold text-white">{s.studentName}</td>
                        <td>
                          <span className="section-pill-sm">
                            Section {s.sectionName || '—'}
                          </span>
                        </td>
                        <td className="font-mono">{s.sem1SGPA}</td>
                        <td className="font-mono">{s.sem2SGPA}</td>
                        <td className="font-mono font-semibold">
                          <span className={s.change > 0 ? 'text-primary' : (s.change < 0 ? 'text-danger' : 'text-muted')}>
                            {s.change >= 0 ? `+${s.change}` : s.change}
                          </span>
                        </td>
                        <td>{renderStatusBadge(s.status)}</td>
                        {onSelectStudent && (
                          <td>
                            <button
                              onClick={() => onSelectStudent(s.studentId)}
                              className="btn btn-secondary btn-xs"
                              title="Inspect student analytics"
                            >
                              Inspect
                            </button>
                          </td>
                        )}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="table-pagination-row">
                <span className="text-muted text-sm">
                  Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, filteredStudents.length)} of {filteredStudents.length}
                </span>
                <div className="pagination-btn-group">
                  <button
                    disabled={page === 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    className="btn btn-secondary btn-xs"
                  >
                    <ChevronLeft size={14} /> Previous
                  </button>
                  <span className="page-current">Page {page} of {totalPages}</span>
                  <button
                    disabled={page === totalPages}
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    className="btn btn-secondary btn-xs"
                  >
                    Next <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
