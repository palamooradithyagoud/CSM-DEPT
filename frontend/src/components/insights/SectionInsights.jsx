import React from 'react';
import { Layers, Compass } from 'lucide-react';

export default function SectionInsights({ sections, loading }) {
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
        <span className="text-muted text-sm">Evaluating section cohort diagnostics...</span>
      </div>
    );
  }

  if (!sections || sections.length === 0) {
    return (
      <div className="card text-center py-12">
        <Layers size={32} className="text-muted inline mb-2 opacity-30" />
        <h4 className="text-white font-medium text-base">All Section Cohorts Balanced</h4>
        <p className="text-xs text-muted mt-1">
          No individual section shows anomalous failure or attendance concentration.
        </p>
      </div>
    );
  }

  return (
    <div className="grid-2-col">
      {sections.map((sec) => (
        <div key={sec.entity_id} className={`card diagnostic-signal-card ${sec.severity.toLowerCase()}`}>
          <div className="signal-card-header mb-2">
            <div>
              <span className="font-mono text-primary text-xs font-bold block">SECTION COHORT</span>
              <h3 className="text-white font-bold text-lg">Section {sec.section_name}</h3>
            </div>
            <span className={`badge ${getSeverityBadgeClass(sec.severity)} text-xs`}>
              {sec.severity} ATTENTION
            </span>
          </div>

          {/* Quick Metrics Strip */}
          <div className="grid-3-col my-2 bg-neutral-900 p-2 rounded border border-neutral-800">
            <div>
              <span className="text-muted text-xs block">Enrolled Roster</span>
              <span className="font-mono font-bold text-sm text-white">
                {sec.total_students} students
              </span>
            </div>
            <div>
              <span className="text-muted text-xs block">Avg Attendance</span>
              <span className={`font-mono font-bold text-sm ${sec.average_attendance < 75 ? 'text-danger' : 'text-primary'}`}>
                {sec.average_attendance !== null ? `${sec.average_attendance}%` : 'N/A'}
              </span>
            </div>
            <div>
              <span className="text-muted text-xs block">Pass Percentage</span>
              <span className={`font-mono font-bold text-sm ${sec.pass_percentage < 75 ? 'text-danger' : 'text-primary'}`}>
                {sec.pass_percentage !== null ? `${sec.pass_percentage}%` : 'N/A'}
              </span>
            </div>
          </div>

          {/* Diagnostic Reasons */}
          <div className="my-2">
            <span className="text-xs font-semibold text-muted block mb-1">Attention Reason:</span>
            <p className="text-xs text-white leading-relaxed">{sec.reason}</p>
          </div>

          {/* Recommendations */}
          {sec.recommendations && sec.recommendations.length > 0 && (
            <div className="mt-3 pt-3 border-t border-neutral-800">
              <div className="flex items-center gap-1.5 text-primary text-xs font-bold mb-2">
                <Compass size={14} />
                <span>Section Remedial Suggestions:</span>
              </div>
              <ul className="text-xs text-muted space-y-1.5 pl-4 list-disc">
                {sec.recommendations.map((rec, i) => (
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
