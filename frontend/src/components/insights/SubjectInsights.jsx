import React from 'react';
import { BookOpen, AlertTriangle, Compass, CheckCircle2 } from 'lucide-react';

export default function SubjectInsights({ subjects, loading }) {
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

  if (loading) {
    return (
      <div className="card text-center py-12">
        <span className="text-muted text-sm">Evaluating curriculum course diagnostics...</span>
      </div>
    );
  }

  if (!subjects || subjects.length === 0) {
    return (
      <div className="card text-center py-12">
        <BookOpen size={32} className="text-muted inline mb-2 opacity-30" />
        <h4 className="text-white font-medium text-base">All Subjects Performing Within Normal Standard</h4>
        <p className="text-xs text-muted mt-1">
          No courses currently trigger the departmental pass rate or failure threshold alerts.
        </p>
      </div>
    );
  }

  return (
    <div className="grid-2-col">
      {subjects.map((sub) => (
        <div key={sub.entity_id} className={`card diagnostic-signal-card ${sub.severity.toLowerCase()}`}>
          <div className="signal-card-header mb-2">
            <div>
              <span className="font-mono text-primary text-xs font-bold block">{sub.subject_code}</span>
              <h3 className="text-white font-bold text-base">{sub.subject_name}</h3>
            </div>
            <span className={`badge ${getSeverityBadgeClass(sub.severity)} text-xs`}>
              {sub.severity} ATTENTION
            </span>
          </div>

          {/* Quick Metrics Strip */}
          <div className="grid-3-col my-2 bg-neutral-900 p-2 rounded border border-neutral-800">
            <div>
              <span className="text-muted text-xs block">Pass Rate</span>
              <span className={`font-mono font-bold text-sm ${sub.pass_percentage < 70 ? 'text-danger' : 'text-primary'}`}>
                {sub.pass_percentage !== null ? `${sub.pass_percentage}%` : 'N/A'}
              </span>
            </div>
            <div>
              <span className="text-muted text-xs block">Avg Marks</span>
              <span className="font-mono font-bold text-sm text-white">
                {sub.average_marks !== null ? `${sub.average_marks}/100` : 'N/A'}
              </span>
            </div>
            <div>
              <span className="text-muted text-xs block">Failed Count</span>
              <span className="font-mono font-bold text-sm text-danger">
                {sub.fail_count} students
              </span>
            </div>
          </div>

          {/* Diagnostic Reasons */}
          <div className="my-2">
            <span className="text-xs font-semibold text-muted block mb-1">Attention Reason:</span>
            <p className="text-xs text-white leading-relaxed">{sub.reason}</p>
          </div>

          {/* Recommendations */}
          {sub.recommendations && sub.recommendations.length > 0 && (
            <div className="mt-3 pt-3 border-t border-neutral-800">
              <div className="flex items-center gap-1.5 text-primary text-xs font-bold mb-2">
                <Compass size={14} />
                <span>Departmental Recommendations:</span>
              </div>
              <ul className="text-xs text-muted space-y-1.5 pl-4 list-disc">
                {sub.recommendations.map((rec, i) => (
                  <li key={i}>
                    <strong className="text-white font-medium">{rec.title}:</strong> {rec.description}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
