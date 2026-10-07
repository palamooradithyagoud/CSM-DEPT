import React from 'react';
import {
  X,
  AlertTriangle,
  CheckCircle2,
  BrainCircuit,
  Compass,
  Clock,
  BookOpen,
  TrendingDown,
  Sparkles,
} from 'lucide-react';

export default function StudentDiagnosticDrawer({ studentInsight, onClose }) {
  if (!studentInsight) return null;

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

  return (
    <div className="diagnostic-drawer-overlay" onClick={onClose}>
      <div className="diagnostic-drawer" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="drawer-header">
          <div>
            <div className="flex items-center gap-2">
              <span className={`badge ${getSeverityBadgeClass(studentInsight.severity)}`}>
                {studentInsight.severity} PRIORITY
              </span>
              <span className="text-muted text-xs font-mono">• {studentInsight.signals_count || studentInsight.signals?.length} SIGNAL(S)</span>
            </div>
            <h3 className="font-bold text-white text-lg mt-1">{studentInsight.name}</h3>
            <span className="font-mono text-primary text-sm">
              {studentInsight.roll_number} {studentInsight.section_name && `• Section ${studentInsight.section_name}`}
            </span>
          </div>
          <button onClick={onClose} className="close-btn" title="Close Drawer">
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="drawer-body">
          {/* AI-Assisted Pedagogical Summary */}
          {studentInsight.ai_explanation && (
            <div className="ai-synthesis-box">
              <div className="ai-synthesis-header">
                <Sparkles size={14} />
                <span>AI-Assisted Diagnostic Summary</span>
              </div>
              <p className="ai-synthesis-text">{studentInsight.ai_explanation}</p>
              <span className="ai-disclaimer">
                * Grounded explanation derived strictly from verified database metrics.
              </span>
            </div>
          )}

          {/* Signals Breakdown */}
          <div className="flex flex-col gap-3">
            <h4 className="text-xs uppercase text-muted font-mono tracking-wider font-bold">
              Identified Diagnostic Signals
            </h4>

            {studentInsight.signals && studentInsight.signals.map((sig, idx) => (
              <div key={idx} className={`diagnostic-signal-card ${sig.severity.toLowerCase()}`}>
                <div className="signal-card-header">
                  <span className="signal-card-title">{sig.title}</span>
                  <span className={`badge ${getSeverityBadgeClass(sig.severity)} text-xs`}>
                    {sig.severity}
                  </span>
                </div>

                <p className="signal-card-reason">{sig.reason}</p>

                {/* Evidence Box */}
                {sig.evidence && Object.keys(sig.evidence).length > 0 && (
                  <div className="signal-card-evidence">
                    <span className="text-muted text-xs block mb-1 font-sans">Traceable Evidence:</span>
                    {Object.entries(sig.evidence).map(([k, v]) => {
                      if (typeof v === 'object' && v !== null) return null;
                      return (
                        <div key={k} className="flex justify-between py-0.5">
                          <span className="text-muted">{k.replace(/_/g, ' ')}:</span>
                          <span className="text-white font-bold">{String(v)}</span>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Affected Courses */}
                {sig.affected_subjects && sig.affected_subjects.length > 0 && (
                  <div className="mt-2">
                    <span className="text-xs text-muted block mb-1">Affected Course(s):</span>
                    <div className="flex flex-wrap gap-1">
                      {sig.affected_subjects.map((sub, i) => (
                        <span key={i} className="signal-tag">
                          {sub.subject_code || sub.subject_name}
                          {sub.attendance !== undefined && ` (${sub.attendance}%)`}
                          {sub.marks !== undefined && ` (${sub.marks}m)`}
                          {sub.grade && ` [${sub.grade}]`}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Actionable Recommendations */}
          <div className="recommendations-box">
            <div className="recommendations-title">
              <Compass size={16} />
              <span>Grounded Departmental Recommendations</span>
            </div>

            {studentInsight.recommendations && studentInsight.recommendations.length > 0 ? (
              <div className="flex flex-col">
                {studentInsight.recommendations.map((rec, idx) => (
                  <div key={idx} className="rec-item">
                    <div className="rec-icon">
                      <CheckCircle2 size={16} className="text-primary mt-1" />
                    </div>
                    <div className="rec-content flex-1">
                      <div className="flex justify-between items-center mb-1">
                        <h5>{rec.title}</h5>
                        <span className={`badge ${getSeverityBadgeClass(rec.priority)} text-xs`}>
                          {rec.priority}
                        </span>
                      </div>
                      <p>{rec.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted">No specific interventions required at this time.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
