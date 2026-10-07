import React, { useState } from 'react';
import {
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Eye,
  Sliders,
  Sparkles,
  User,
  ArrowRight,
} from 'lucide-react';
import StudentDiagnosticDrawer from './StudentDiagnosticDrawer';

export default function StudentWatchlist({
  students,
  total,
  page,
  limit,
  onPageChange,
  severityFilter,
  onSeverityChange,
  loading,
}) {
  const [selectedStudent, setSelectedStudent] = useState(null);

  const getSeverityBadgeClass = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return 'badge-critical';
      case 'HIGH':
        return 'badge-high';
      case 'MEDIUM':
        return 'badge-medium';
      case 'LOW':
        return 'badge-low';
      default:
        return 'badge-info';
    }
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="watchlist-section">
      {/* Severity Filter Pills */}
      <div className="watchlist-controls-row">
        <div className="severity-filter-group">
          <button
            className={`sev-pill ${severityFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => onSeverityChange('ALL')}
          >
            All Priority ({total})
          </button>
          <button
            className={`sev-pill ${severityFilter === 'CRITICAL' ? 'active critical' : ''}`}
            onClick={() => onSeverityChange('CRITICAL')}
          >
            Critical
          </button>
          <button
            className={`sev-pill ${severityFilter === 'HIGH' ? 'active high' : ''}`}
            onClick={() => onSeverityChange('HIGH')}
          >
            High Priority
          </button>
          <button
            className={`sev-pill ${severityFilter === 'MEDIUM' ? 'active' : ''}`}
            onClick={() => onSeverityChange('MEDIUM')}
          >
            Medium
          </button>
          <button
            className={`sev-pill ${severityFilter === 'LOW' ? 'active' : ''}`}
            onClick={() => onSeverityChange('LOW')}
          >
            Low
          </button>
        </div>

        <span className="text-muted text-xs font-mono">
          Showing {students.length} of {total} flagged students
        </span>
      </div>

      {/* Watchlist Table */}
      <div className="card table-card">
        {loading ? (
          <div className="text-center py-12">
            <span className="text-muted text-sm">Evaluating deterministic diagnostic signals...</span>
          </div>
        ) : students.length === 0 ? (
          <div className="text-center py-12">
            <User size={32} className="text-muted inline mb-2 opacity-30" />
            <h4 className="text-white font-medium text-base">No Students Flagged in This Selection</h4>
            <p className="text-xs text-muted mt-1">
              All students in the selected cohort are progressing within normal departmental thresholds.
            </p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="watchlist-table">
              <thead>
                <tr>
                  <th>Severity</th>
                  <th>Roll Number</th>
                  <th>Student Name</th>
                  <th>Section</th>
                  <th>Primary Attention Reason</th>
                  <th>Active Signals</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {students.map((st) => (
                  <tr key={st.entity_id}>
                    <td>
                      <span className={`badge ${getSeverityBadgeClass(st.severity)} text-xs`}>
                        {st.severity}
                      </span>
                    </td>
                    <td className="font-mono text-primary font-bold">{st.roll_number}</td>
                    <td className="font-semibold text-white">{st.name}</td>
                    <td>
                      <span className="section-pill-sm">
                        Section {st.section_name || '—'}
                      </span>
                    </td>
                    <td className="text-muted max-w-xs text-xs">
                      {st.primary_reasons && st.primary_reasons.length > 0
                        ? st.primary_reasons[0]
                        : 'Academic distress detected.'}
                    </td>
                    <td>
                      <div className="signal-tags-wrap">
                        {st.signals && st.signals.map((sig, i) => (
                          <span key={i} className="signal-tag">
                            {sig.category.replace(/_/g, ' ')}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <button
                        onClick={() => setSelectedStudent(st)}
                        className="btn btn-secondary btn-xs flex items-center gap-1"
                        title="View diagnostic details & recommendations"
                      >
                        <Eye size={13} />
                        <span>Inspect Diagnostic</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="table-pagination-row">
            <span className="text-muted text-xs">
              Page {page} of {totalPages}
            </span>
            <div className="pagination-btn-group">
              <button
                disabled={page === 1}
                onClick={() => onPageChange(page - 1)}
                className="btn btn-secondary btn-xs"
              >
                <ChevronLeft size={14} /> Previous
              </button>
              <button
                disabled={page === totalPages}
                onClick={() => onPageChange(page + 1)}
                className="btn btn-secondary btn-xs"
              >
                Next <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Drawer */}
      {selectedStudent && (
        <StudentDiagnosticDrawer
          studentInsight={selectedStudent}
          onClose={() => setSelectedStudent(null)}
        />
      )}
    </div>
  );
}
