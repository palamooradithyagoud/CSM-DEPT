import React, { useState, useEffect } from 'react';
import {
  Search,
  User,
  TrendingUp,
  TrendingDown,
  Minus,
  Award,
  BookOpen,
  Clock,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  ExternalLink,
  Download,
} from 'lucide-react';
import { api } from '../../services/api';

export default function StudentAnalytics({ studentId: initialStudentId, onClose }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedStudentId, setSelectedStudentId] = useState(initialStudentId || null);
  const [studentData, setStudentData] = useState(null);
  const [studentInsights, setStudentInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (initialStudentId) {
      setSelectedStudentId(initialStudentId);
    }
  }, [initialStudentId]);

  useEffect(() => {
    if (!selectedStudentId) return;
    setLoading(true);
    setError(null);
    Promise.all([
      api.getStudentAnalytics(selectedStudentId),
      api.getStudentInsights(selectedStudentId).catch(() => null),
    ])
      .then(([analyticsData, insightsData]) => {
        setStudentData(analyticsData);
        setStudentInsights(insightsData);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError('Failed to load student analytics data.');
        setLoading(false);
      });
  }, [selectedStudentId]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    api.getStudents({ search: searchQuery.trim(), limit: 8 })
      .then((res) => {
        setSearchResults(res.data || []);
        setIsSearching(false);
      })
      .catch((err) => {
        console.error(err);
        setIsSearching(false);
      });
  };

  const trendIcon = (trend) => {
    if (trend === 'IMPROVED') return <TrendingUp size={16} className="text-success" />;
    if (trend === 'DECLINED') return <TrendingDown size={16} className="text-danger" />;
    return <Minus size={16} className="text-muted" />;
  };

  const trendBadgeClass = (trend) => {
    if (trend === 'IMPROVED') return 'badge-success';
    if (trend === 'DECLINED') return 'badge-danger';
    return 'badge-neutral';
  };

  return (
    <div className="student-analytics-container">
      {/* Search Header if not pinned to a specific student */}
      {!initialStudentId && (
        <div className="card student-search-card">
          <div className="section-title-wrap mb-3">
            <User size={18} className="text-primary" />
            <h3>Individual Student Performance Profile</h3>
          </div>
          <p className="text-sm text-muted mb-4">
            Search by student roll number or name to inspect cross-semester trajectory, subject mastery, and attendance association.
          </p>

          <form onSubmit={handleSearch} className="student-search-form">
            <div className="search-input-wrap flex-1">
              <Search size={16} className="text-muted" />
              <input
                type="text"
                placeholder="Enter Roll Number (e.g. 25881A6601) or Name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
            </div>
            <button type="submit" className="btn btn-primary btn-sm" disabled={isSearching}>
              {isSearching ? <RefreshCw size={14} className="spin" /> : 'Search Student'}
            </button>
          </form>

          {searchResults.length > 0 && (
            <div className="search-results-dropdown mt-3">
              <span className="text-xs text-muted font-mono block mb-2">Matching Students ({searchResults.length}):</span>
              <div className="student-result-pills">
                {searchResults.map((s) => (
                  <button
                    key={s.id}
                    className={`student-pill-btn ${selectedStudentId === s.id ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedStudentId(s.id);
                      setSearchResults([]);
                    }}
                  >
                    <span className="font-mono text-primary font-semibold">{s.rollNumber}</span>
                    <span className="text-muted text-xs"> — {s.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {loading && (
        <div className="card text-center py-10">
          <RefreshCw size={28} className="spin text-primary inline mb-3" />
          <p className="text-muted">Loading deterministic student analytics...</p>
        </div>
      )}

      {error && (
        <div className="card alert-banner alert-warning">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {!loading && !studentData && !initialStudentId && (
        <div className="card text-center py-12">
          <User size={36} className="text-muted inline mb-3 opacity-40" />
          <h4 className="text-muted font-normal">No Student Selected</h4>
          <p className="text-xs text-muted mt-1">Search for a roll number above to render the comprehensive academic profile.</p>
        </div>
      )}

      {!loading && studentData && (
        <div className="student-analytics-profile">
          {/* Top KPI Header */}
          <div className="card student-kpi-summary-card">
            <div className="student-hero-row">
              <div className="student-title-block">
                <div className="flex items-center gap-2">
                  <User size={24} className="text-primary" />
                  <h2 className="student-hero-name">{studentData.student?.name}</h2>
                </div>
                <div className="student-hero-meta">
                  <span className="font-mono text-primary font-semibold text-base">{studentData.student?.roll_number}</span>
                  <span className="meta-divider">•</span>
                  <span className="badge badge-outline">Undergraduate Department Cohort</span>
                  <button
                    className="btn btn-secondary btn-sm"
                    style={{ marginLeft: '1rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem', padding: '0.25rem 0.6rem' }}
                    onClick={async () => {
                      try {
                        await api.exportStudentReport(selectedStudentId, { format: 'pdf' });
                      } catch (e) {
                        alert('Export failed: ' + e.message);
                      }
                    }}
                  >
                    <Download size={13} />
                    <span>Export Dossier (PDF)</span>
                  </button>
                </div>
              </div>

              <div className="student-kpi-grid">
                <div className="student-kpi-box">
                  <span className="kpi-lbl">Current CGPA</span>
                  <span className="kpi-val font-mono text-primary">
                    {studentData.student?.current_cgpa !== null ? studentData.student.current_cgpa : 'N/A'}
                  </span>
                  <span className="text-xs text-muted">Cumulative Grade</span>
                </div>

                <div className="student-kpi-box">
                  <span className="kpi-lbl">Latest SGPA</span>
                  <span className="kpi-val font-mono">
                    {studentData.student?.latest_sgpa !== null ? studentData.student.latest_sgpa : 'N/A'}
                  </span>
                  <span className="text-xs text-muted">Most recent semester</span>
                </div>

                <div className="student-kpi-box">
                  <span className="kpi-lbl">Avg Attendance</span>
                  <span className="kpi-val font-mono">
                    {studentData.student?.average_attendance !== null
                      ? `${studentData.student.average_attendance}%`
                      : 'N/A'}
                  </span>
                  <span className="text-xs text-muted">Official attendance</span>
                </div>

                <div className="student-kpi-box">
                  <span className="kpi-lbl">Performance Trend</span>
                  <div className="flex items-center gap-1 mt-1">
                    {trendIcon(studentData.student?.performance_trend)}
                    <span className={`badge ${trendBadgeClass(studentData.student?.performance_trend)}`}>
                      {studentData.student?.performance_trend || 'N/A'}
                    </span>
                  </div>
                  <span className="text-xs text-muted">Longitudinal delta</span>
                </div>
              </div>
            </div>
          </div>

          {/* Academic Attention & Diagnostic Insights (Phase 4) */}
          {studentInsights && studentInsights.requires_attention && (
            <div className={`card mb-6 diagnostic-signal-card ${studentInsights.severity.toLowerCase()}`}>
              <div className="signal-card-header mb-2">
                <div className="flex items-center gap-2">
                  <AlertCircle size={18} className={studentInsights.severity === 'CRITICAL' ? 'text-danger' : 'text-warning'} />
                  <h3 className="text-white font-bold text-base">Academic Attention Diagnostic</h3>
                </div>
                <span className={`badge badge-${studentInsights.severity.toLowerCase()} text-xs font-bold`}>
                  {studentInsights.severity} PRIORITY
                </span>
              </div>

              {/* Reasons */}
              <div className="my-2">
                <span className="text-xs font-semibold text-muted block mb-1">Identified Attention Reasons:</span>
                <ul className="text-xs text-white space-y-1 pl-4 list-disc">
                  {studentInsights.primary_reasons?.map((reason, idx) => (
                    <li key={idx}>{reason}</li>
                  ))}
                </ul>
              </div>

              {/* Recommendations */}
              {studentInsights.recommendations && studentInsights.recommendations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-neutral-800">
                  <span className="text-xs font-semibold text-primary block mb-1 font-mono uppercase tracking-wide">
                    Departmental Recommendations:
                  </span>
                  <div className="space-y-1.5">
                    {studentInsights.recommendations.map((rec, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-xs">
                        <CheckCircle2 size={13} className="text-primary mt-0.5 shrink-0" />
                        <div>
                          <strong className="text-white">{rec.title}:</strong>{' '}
                          <span className="text-muted">{rec.description}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* AI-Assisted Synthesis */}
              {studentInsights.ai_explanation && (
                <div className="mt-3 p-2.5 rounded bg-neutral-900 border border-neutral-800 text-xs">
                  <span className="text-primary font-semibold block mb-0.5 font-mono">
                    Diagnostic Summary:
                  </span>
                  <p className="text-muted leading-relaxed">{studentInsights.ai_explanation}</p>
                </div>
              )}
            </div>
          )}

          {/* 1. CGPA & SGPA Progression Trajectory */}
          <div className="card mb-6">
            <div className="section-title-wrap mb-4">
              <Award size={18} className="text-primary" />
              <h3>Academic Progression Trajectory</h3>
            </div>
            <p className="text-xs text-muted mb-4">
              Deterministic progression curve showing official SGPA and cumulative CGPA across completed semesters. Semesters without published official summaries are excluded.
            </p>

            {studentData.trajectory && studentData.trajectory.length > 0 ? (
              <div className="trajectory-view">
                {/* Visual progression timeline */}
                <div className="trajectory-timeline">
                  {studentData.trajectory.map((point, idx) => (
                    <div key={idx} className="timeline-node">
                      <div className="node-marker">
                        <span className="node-sem-label">{point.semester_name}</span>
                        <div className="node-dot"></div>
                      </div>
                      <div className="node-card">
                        <div className="node-stat-row">
                          <span className="text-muted text-xs">SGPA:</span>
                          <span className="font-mono text-primary font-bold text-base">
                            {point.sgpa !== null ? point.sgpa : 'N/A'}
                          </span>
                        </div>
                        {point.cgpa !== null && (
                          <div className="node-stat-row">
                            <span className="text-muted text-xs">CGPA:</span>
                            <span className="font-mono text-muted text-sm">{point.cgpa}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Trajectory Table */}
                <div className="table-responsive mt-4">
                  <table className="mini-table">
                    <thead>
                      <tr>
                        <th>Academic Progression</th>
                        <th>Semester Name</th>
                        <th>Official SGPA</th>
                        <th>Cumulative CGPA</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {studentData.trajectory.map((p, i) => (
                        <tr key={i}>
                          <td className="font-mono text-muted text-xs">Step {i + 1}</td>
                          <td className="font-semibold">{p.semester_name}</td>
                          <td className="font-mono text-primary font-bold">{p.sgpa ?? '—'}</td>
                          <td className="font-mono">{p.cgpa ?? '—'}</td>
                          <td>
                            <span className="badge badge-success">Official Verified</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="alert-banner alert-neutral">
                <AlertCircle size={16} />
                <span>Official semester summary records are not yet available to plot academic trajectory.</span>
              </div>
            )}
          </div>

          {/* 2-Column: Semester Performance & Subject Performance */}
          <div className="grid-2-col mb-6">
            {/* Semester Performance */}
            <div className="card">
              <div className="section-title-wrap mb-3">
                <Award size={18} className="text-primary" />
                <h3>Semester Summaries</h3>
              </div>
              {studentData.semester_performance && studentData.semester_performance.length > 0 ? (
                <div className="table-responsive">
                  <table className="mini-table">
                    <thead>
                      <tr>
                        <th>Semester</th>
                        <th>SGPA</th>
                        <th>CGPA</th>
                      </tr>
                    </thead>
                    <tbody>
                      {studentData.semester_performance.map((sp, idx) => (
                        <tr key={idx}>
                          <td className="font-semibold">{sp.semester_name}</td>
                          <td className="font-mono text-primary font-bold">{sp.sgpa ?? 'N/A'}</td>
                          <td className="font-mono">{sp.cgpa ?? 'N/A'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-xs text-muted">No semester summary records found.</p>
              )}
            </div>

            {/* Attendance Performance */}
            <div className="card">
              <div className="section-title-wrap mb-3">
                <Clock size={18} className="text-primary" />
                <h3>Subject-Wise Attendance</h3>
              </div>
              {studentData.attendance_performance && studentData.attendance_performance.length > 0 ? (
                <div className="table-responsive">
                  <table className="mini-table">
                    <thead>
                      <tr>
                        <th>Subject</th>
                        <th>Attended / Total</th>
                        <th>Attendance %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {studentData.attendance_performance.map((att, idx) => (
                        <tr key={idx}>
                          <td>
                            <span className="font-mono text-primary text-xs block">{att.subject_code}</span>
                            <span className="text-xs">{att.subject_name}</span>
                          </td>
                          <td className="font-mono text-xs">
                            {att.attended} / {att.total}
                          </td>
                          <td>
                            <span
                              className={`percentage-badge ${
                                att.percentage >= 75 ? 'badge-success' : 'badge-danger'
                              }`}
                            >
                              {att.percentage}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-xs text-muted">No official attendance records found.</p>
              )}
            </div>
          </div>

          {/* 3. Subject Performance & Exam Mastery */}
          <div className="card mb-6">
            <div className="section-title-wrap mb-3">
              <BookOpen size={18} className="text-primary" />
              <h3>Subject End-Semester Results</h3>
            </div>
            {studentData.subject_performance && studentData.subject_performance.length > 0 ? (
              <div className="table-responsive">
                <table className="mini-table">
                  <thead>
                    <tr>
                      <th>Subject Code</th>
                      <th>Subject Name</th>
                      <th>Total Marks</th>
                      <th>Grade</th>
                      <th>Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {studentData.subject_performance.map((sb, idx) => (
                      <tr key={idx}>
                        <td className="font-mono text-primary font-semibold">{sb.subject_code}</td>
                        <td>{sb.subject_name}</td>
                        <td className="font-mono font-bold">{sb.marks !== null ? sb.marks : '—'}</td>
                        <td>
                          <span className="badge badge-outline font-mono font-bold">{sb.grade}</span>
                        </td>
                        <td>
                          <span
                            className={`badge ${
                              sb.status === 'PASSED' ? 'badge-success' : 'badge-danger'
                            }`}
                          >
                            {sb.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-xs text-muted">No subject semester results found for this student.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
