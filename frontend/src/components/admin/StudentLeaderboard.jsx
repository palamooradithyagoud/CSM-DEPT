import React, { useState, useEffect } from 'react';
import {
  Trophy,
  Medal,
  Award,
  TrendingUp,
  TrendingDown,
  Minus,
  Search,
  Filter,
  Download,
  RefreshCw,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  User,
  GraduationCap,
} from 'lucide-react';
import { api } from '../../services/api';

export default function StudentLeaderboard({ batches, onSelectStudent }) {
  const [selectedBatch, setSelectedBatch] = useState('');
  const [sectionFilter, setSectionFilter] = useState('');
  const [viewMode, setViewMode] = useState('cumulative'); // 'cumulative' | 'sem1' | 'sem2' | 'attendance'
  const [searchQuery, setSearchQuery] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sections, setSections] = useState([]);

  // Initialize batch
  useEffect(() => {
    if (batches && batches.length > 0 && !selectedBatch) {
      const primary = batches.find((b) => b.name === '2025-2029') || batches[0];
      setSelectedBatch(primary.id);
    }
  }, [batches]);

  // Load sections for selected batch's active semesters
  useEffect(() => {
    if (!selectedBatch) return;
    api.getAcademicYears(selectedBatch).then(async (years) => {
      if (years.length > 0) {
        const sems = await api.getSemesters(years[0].id);
        if (sems.length > 0) {
          const secs = await api.getSections(sems[0].id);
          setSections(secs);
        }
      }
    }).catch(console.error);
  }, [selectedBatch]);

  // Fetch Leaderboard data
  const fetchLeaderboard = () => {
    if (!selectedBatch) return;
    setLoading(true);
    api.getLeaderboard({
      batch_id: selectedBatch,
      section_id: sectionFilter || undefined,
      view_mode: viewMode,
      search: searchQuery || undefined,
      limit: 150,
    }).then((res) => {
      setData(res);
      setLoading(false);
    }).catch((err) => {
      console.error('Failed to fetch leaderboard:', err);
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchLeaderboard();
  }, [selectedBatch, sectionFilter, viewMode, searchQuery]);

  // CSV Export
  const handleExportCSV = () => {
    if (!data || !data.rankings || data.rankings.length === 0) return;
    const headers = ['Rank', 'Roll Number', 'Student Name', 'Section', 'Sem 1 SGPA', 'Sem 2 SGPA', 'Cumulative CGPA', 'SGPA Change', 'Overall Attendance %', 'Standing'];
    const rows = data.rankings.map((r) => [
      r.rank,
      r.rollNumber,
      `"${r.name}"`,
      r.section,
      r.sem1.sgpa ?? 'N/A',
      r.sem2.sgpa ?? 'N/A',
      r.cumulative.cgpa ?? 'N/A',
      r.cumulative.sgpaChange !== null ? (r.cumulative.sgpaChange > 0 ? `+${r.cumulative.sgpaChange}` : r.cumulative.sgpaChange) : 'N/A',
      r.cumulative.overallAttendancePct ?? 'N/A',
      r.cumulative.standing,
    ]);

    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Department_Leaderboard_${viewMode}_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const podium = data?.podium || [];
  const summary = data?.summary || {};
  const rankings = data?.rankings || [];

  return (
    <div className="student-leaderboard-container">
      {/* View Header */}
      <div className="view-header-flex" style={{ marginBottom: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-success" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Trophy size={13} />
              <span>Academic Merit Engine</span>
            </span>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Mapped: Sem 1 & Sem 2 Results</span>
          </div>
          <h1 className="admin-page-title" style={{ fontSize: '1.75rem', fontWeight: 700 }}>
            Student Academic Leaderboard & Merit Standings
          </h1>
          <p className="admin-page-subtitle">
            Verified academic ranking extracted dynamically from college examination results and attendance registers.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={handleExportCSV}
            disabled={!rankings.length}
            className="btn btn-secondary btn-sm"
            title="Download CSV Dossier"
          >
            <Download size={15} />
            <span>Export Leaderboard</span>
          </button>
          <button
            onClick={fetchLeaderboard}
            disabled={loading}
            className="btn btn-secondary btn-sm"
            title="Refresh Standings"
          >
            <RefreshCw size={15} className={loading ? 'spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Control Bar: Batch, View Mode, Section, Search */}
      <div className="card" style={{ padding: '1rem', marginBottom: '1.5rem', background: 'rgba(15, 23, 42, 0.75)' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* View Mode Tabs */}
          <div style={{ display: 'flex', gap: '6px', background: 'rgba(30, 41, 59, 0.7)', padding: '4px', borderRadius: '8px' }}>
            <button
              onClick={() => setViewMode('cumulative')}
              className={`btn btn-xs ${viewMode === 'cumulative' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontWeight: 600 }}
            >
              🏆 Cumulative (Sem 1 + Sem 2)
            </button>
            <button
              onClick={() => setViewMode('sem1')}
              className={`btn btn-xs ${viewMode === 'sem1' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontWeight: 600 }}
            >
              1️⃣ Semester 1 Standings
            </button>
            <button
              onClick={() => setViewMode('sem2')}
              className={`btn btn-xs ${viewMode === 'sem2' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontWeight: 600 }}
            >
              2️⃣ Semester 2 Standings
            </button>
            <button
              onClick={() => setViewMode('attendance')}
              className={`btn btn-xs ${viewMode === 'attendance' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontWeight: 600 }}
            >
              📅 Attendance Standings
            </button>
          </div>

          {/* Filters: Batch & Section */}
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            {/* Batch */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <label style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Batch:</label>
              <select
                value={selectedBatch}
                onChange={(e) => setSelectedBatch(e.target.value)}
                className="form-select form-select-sm"
                style={{ width: '130px' }}
              >
                {batches?.map((b) => (
                  <option key={b.id} value={b.id}>
                    Batch {b.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Section Scope */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <label style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Section:</label>
              <select
                value={sectionFilter}
                onChange={(e) => setSectionFilter(e.target.value)}
                className="form-select form-select-sm"
                style={{ width: '190px' }}
              >
                <option value="">Overall Year (All: A, B, C)</option>
                {sections.map((sec) => (
                  <option key={sec.id} value={sec.id}>
                    Section {sec.name} Rankers
                  </option>
                ))}
              </select>
            </div>

            {/* Search */}
            <div style={{ position: 'relative' }}>
              <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
              <input
                type="text"
                placeholder="Search Roll No or Name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="form-input form-input-sm"
                style={{ paddingLeft: '30px', width: '210px' }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Cohort Stats Banner */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="card" style={{ padding: '1rem', textAlign: 'center', borderLeft: '4px solid #f59e0b' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Top Score (CGPA)</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fbbf24', marginTop: '4px' }}>
            {summary.highestCgpa ? Number(summary.highestCgpa).toFixed(2) : '—'}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>Highest in Cohort</div>
        </div>

        <div className="card" style={{ padding: '1rem', textAlign: 'center', borderLeft: '4px solid #38bdf8' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Batch Average</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#38bdf8', marginTop: '4px' }}>
            {summary.averageCgpa ? Number(summary.averageCgpa).toFixed(2) : '—'}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>Mean CGPA Benchmark</div>
        </div>

        <div className="card" style={{ padding: '1rem', textAlign: 'center', borderLeft: '4px solid #a855f7' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Distinctions (≥ 8.0)</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#c084fc', marginTop: '4px' }}>
            {summary.distinctionCount ?? 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>Honor Roll Rankers</div>
        </div>

        <div className="card" style={{ padding: '1rem', textAlign: 'center', borderLeft: '4px solid #10b981' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>First Class (≥ 6.5)</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#34d399', marginTop: '4px' }}>
            {summary.firstClassCount ?? 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>Proficient Learners</div>
        </div>

        <div className="card" style={{ padding: '1rem', textAlign: 'center', borderLeft: '4px solid #6366f1' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Total Ranked</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#818cf8', marginTop: '4px' }}>
            {summary.rankedCount ?? 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
            Mapped: {summary.bothSemestersCount} across Sem 1 & 2
          </div>
        </div>
      </div>

      {/* Top 3 Podium Cards */}
      {podium.length > 0 && !searchQuery && (
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Award size={18} className="text-warning" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
              Merit Podium — Top 3 Cohort Champions
            </h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
            {podium.map((student, idx) => {
              const medalGlow = idx === 0
                ? 'rgba(234, 179, 8, 0.25)'
                : idx === 1
                ? 'rgba(148, 163, 184, 0.25)'
                : 'rgba(217, 119, 6, 0.25)';
              const borderColor = idx === 0 ? '#eab308' : idx === 1 ? '#94a3b8' : '#d97706';

              return (
                <div
                  key={student.studentId}
                  className="card"
                  style={{
                    position: 'relative',
                    overflow: 'hidden',
                    border: `1.5px solid ${borderColor}`,
                    boxShadow: `0 8px 24px ${medalGlow}`,
                    background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%)',
                    padding: '1.25rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{
                        width: '42px',
                        height: '42px',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '1.5rem',
                        background: 'rgba(15, 23, 42, 0.6)',
                        border: `1px solid ${borderColor}`,
                      }}>
                        {student.medal}
                      </div>
                      <div>
                        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: borderColor, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                          {student.rankBadge}
                        </span>
                        <h4 style={{ margin: '2px 0 0 0', fontSize: '1rem', fontWeight: 700, color: '#fff' }}>
                          {student.name}
                        </h4>
                        <div style={{ fontSize: '0.8rem', color: '#94a3b8', fontFamily: 'monospace' }}>
                          {student.rollNumber} • Section {student.section}
                        </div>
                      </div>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '1.4rem', fontWeight: 800, color: borderColor }}>
                        {student.cumulative.cgpa ? Number(student.cumulative.cgpa).toFixed(2) : '—'}
                      </div>
                      <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>CGPA</span>
                    </div>
                  </div>

                  {/* Sem 1 vs Sem 2 breakdown */}
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr 1fr',
                    gap: '8px',
                    background: 'rgba(15, 23, 42, 0.5)',
                    padding: '8px',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    textAlign: 'center',
                    marginTop: '10px',
                  }}>
                    <div>
                      <div style={{ color: '#94a3b8' }}>Sem 1 SGPA</div>
                      <div style={{ fontWeight: 700, color: '#38bdf8', fontSize: '0.9rem' }}>
                        {student.sem1.sgpa ? Number(student.sem1.sgpa).toFixed(2) : '—'}
                      </div>
                    </div>
                    <div>
                      <div style={{ color: '#94a3b8' }}>Sem 2 SGPA</div>
                      <div style={{ fontWeight: 700, color: '#a78bfa', fontSize: '0.9rem' }}>
                        {student.sem2.sgpa ? Number(student.sem2.sgpa).toFixed(2) : '—'}
                      </div>
                    </div>
                    <div>
                      <div style={{ color: '#94a3b8' }}>Attendance</div>
                      <div style={{ fontWeight: 700, color: '#34d399', fontSize: '0.9rem' }}>
                        {student.cumulative.overallAttendancePct ? `${student.cumulative.overallAttendancePct}%` : '—'}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Leaderboard Table */}
      <div className="card table-card">
        <div className="table-header-info" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="count-label" style={{ fontWeight: 600 }}>
              Official Merit Standings ({rankings.length} Students)
            </span>
            <span className="text-muted text-xs">
              • Showing {data?.cohort?.viewMode?.toUpperCase()} view
            </span>
          </div>
          {searchQuery && (
            <span className="text-xs text-muted">
              Filtered by: "{searchQuery}"
            </span>
          )}
        </div>

        <div className="table-responsive">
          <table className="subjects-table">
            <thead>
              <tr>
                <th style={{ width: '70px', textAlign: 'center' }}>Rank</th>
                <th>Student Roll & Name</th>
                <th style={{ width: '80px', textAlign: 'center' }}>Section</th>
                <th style={{ textAlign: 'center' }}>Sem 1 SGPA</th>
                <th style={{ textAlign: 'center' }}>Sem 2 SGPA</th>
                <th style={{ textAlign: 'center' }}>Cumulative CGPA</th>
                <th style={{ textAlign: 'center' }}>Progression (Δ)</th>
                <th style={{ textAlign: 'center' }}>Attendance %</th>
                <th style={{ textAlign: 'center' }}>Standing</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="9" className="text-center py-8">
                    <RefreshCw size={24} className="spin text-primary inline" />
                    <div style={{ marginTop: '8px', color: '#94a3b8' }}>Computing merit rankings and mappings...</div>
                  </td>
                </tr>
              ) : rankings.length === 0 ? (
                <tr>
                  <td colSpan="9" className="text-center empty-cell" style={{ padding: '2.5rem 1rem' }}>
                    <AlertTriangle size={24} className="text-warning inline" style={{ marginBottom: '8px' }} />
                    <div style={{ color: '#94a3b8', fontWeight: 600 }}>No student records found matching this criteria.</div>
                    <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '4px' }}>
                      Upload semester result files in Academic Upload to automatically populate this leaderboard.
                    </div>
                  </td>
                </tr>
              ) : (
                rankings.map((st) => {
                  const isTop3 = st.rank <= 3;
                  const medalEmoji = st.rank === 1 ? '🥇' : st.rank === 2 ? '🥈' : st.rank === 3 ? '🥉' : null;

                  return (
                    <tr
                      key={st.studentId}
                      style={{
                        background: isTop3 ? 'rgba(234, 179, 8, 0.03)' : 'transparent',
                        cursor: onSelectStudent ? 'pointer' : 'default',
                      }}
                      onClick={() => onSelectStudent && onSelectStudent(st.studentId)}
                    >
                      {/* Rank */}
                      <td style={{ textAlign: 'center' }}>
                        {medalEmoji ? (
                          <span style={{ fontSize: '1.25rem' }} title={`Rank ${st.rank}`}>
                            {medalEmoji}
                          </span>
                        ) : (
                          <span
                            className="font-mono"
                            style={{
                              display: 'inline-block',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              fontSize: '0.85rem',
                              fontWeight: 700,
                              background: st.rank <= 10 ? 'rgba(99, 102, 241, 0.15)' : 'rgba(30, 41, 59, 0.5)',
                              color: st.rank <= 10 ? '#a5b4fc' : '#94a3b8',
                            }}
                          >
                            #{st.rank}
                          </span>
                        )}
                      </td>

                      {/* Student Info */}
                      <td>
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                          <span className="font-semibold text-white" style={{ fontSize: '0.9rem' }}>
                            {st.name}
                          </span>
                          <span className="font-mono text-xs text-muted">
                            {st.rollNumber}
                          </span>
                        </div>
                      </td>

                      {/* Section */}
                      <td style={{ textAlign: 'center' }}>
                        <span
                          className="badge"
                          style={{
                            background: 'rgba(56, 189, 248, 0.1)',
                            color: '#38bdf8',
                            border: '1px solid rgba(56, 189, 248, 0.3)',
                            fontWeight: 700,
                          }}
                        >
                          Sec {st.section}
                        </span>
                      </td>

                      {/* Sem 1 */}
                      <td style={{ textAlign: 'center' }}>
                        {st.sem1.sgpa !== null ? (
                          <div>
                            <span className="font-mono" style={{ fontWeight: 700, color: '#38bdf8' }}>
                              {Number(st.sem1.sgpa).toFixed(2)}
                            </span>
                            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                              {st.sem1.passedSubjects}/{st.sem1.totalSubjects} Passed
                            </div>
                          </div>
                        ) : (
                          <span className="text-muted text-xs">—</span>
                        )}
                      </td>

                      {/* Sem 2 */}
                      <td style={{ textAlign: 'center' }}>
                        {st.sem2.sgpa !== null ? (
                          <div>
                            <span className="font-mono" style={{ fontWeight: 700, color: '#a78bfa' }}>
                              {Number(st.sem2.sgpa).toFixed(2)}
                            </span>
                            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                              {st.sem2.passedSubjects}/{st.sem2.totalSubjects} Passed
                            </div>
                          </div>
                        ) : (
                          <span className="text-muted text-xs">—</span>
                        )}
                      </td>

                      {/* Cumulative CGPA */}
                      <td style={{ textAlign: 'center' }}>
                        {st.cumulative.cgpa !== null ? (
                          <span
                            className="font-mono"
                            style={{
                              display: 'inline-block',
                              padding: '3px 10px',
                              borderRadius: '6px',
                              fontWeight: 800,
                              fontSize: '0.95rem',
                              background: st.cumulative.cgpa >= 8.5
                                ? 'rgba(234, 179, 8, 0.15)'
                                : st.cumulative.cgpa >= 7.0
                                ? 'rgba(56, 189, 248, 0.15)'
                                : 'rgba(148, 163, 184, 0.15)',
                              color: st.cumulative.cgpa >= 8.5
                                ? '#fbbf24'
                                : st.cumulative.cgpa >= 7.0
                                ? '#38bdf8'
                                : '#cbd5e1',
                              border: st.cumulative.cgpa >= 8.5
                                ? '1px solid rgba(234, 179, 8, 0.4)'
                                : '1px solid rgba(56, 189, 248, 0.3)',
                            }}
                          >
                            {Number(st.cumulative.cgpa).toFixed(2)}
                          </span>
                        ) : (
                          <span className="text-muted text-xs">—</span>
                        )}
                      </td>

                      {/* Progression Δ */}
                      <td style={{ textAlign: 'center' }}>
                        {st.cumulative.sgpaChange !== null ? (
                          st.cumulative.sgpaChange > 0 ? (
                            <span style={{ color: '#4ade80', fontSize: '0.8rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '2px' }}>
                              <TrendingUp size={13} />
                              +{Number(st.cumulative.sgpaChange).toFixed(2)}
                            </span>
                          ) : st.cumulative.sgpaChange < 0 ? (
                            <span style={{ color: '#f87171', fontSize: '0.8rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '2px' }}>
                              <TrendingDown size={13} />
                              {Number(st.cumulative.sgpaChange).toFixed(2)}
                            </span>
                          ) : (
                            <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>0.00</span>
                          )
                        ) : (
                          <span className="text-muted text-xs">—</span>
                        )}
                      </td>

                      {/* Attendance % */}
                      <td style={{ textAlign: 'center' }}>
                        {st.cumulative.overallAttendancePct !== null ? (
                          <span
                            className="font-mono"
                            style={{
                              fontSize: '0.85rem',
                              fontWeight: 600,
                              color: st.cumulative.overallAttendancePct >= 75
                                ? '#34d399'
                                : st.cumulative.overallAttendancePct >= 65
                                ? '#fbbf24'
                                : '#f87171',
                            }}
                          >
                            {st.cumulative.overallAttendancePct}%
                          </span>
                        ) : (
                          <span className="text-muted text-xs">—</span>
                        )}
                      </td>

                      {/* Standing */}
                      <td style={{ textAlign: 'center' }}>
                        <span
                          className={`badge ${
                            st.cumulative.standingColor === 'gold'
                              ? 'badge-warning'
                              : st.cumulative.standingColor === 'purple'
                              ? 'badge-info'
                              : st.cumulative.standingColor === 'blue'
                              ? 'badge-primary'
                              : st.cumulative.standingColor === 'danger'
                              ? 'badge-danger'
                              : 'badge-outline'
                          }`}
                          style={{ fontSize: '0.75rem', fontWeight: 600 }}
                        >
                          {st.cumulative.standing}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
