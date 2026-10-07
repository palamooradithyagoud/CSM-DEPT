import React, { useState, useEffect } from 'react';
import { BookOpen, CheckCircle2, AlertTriangle, Clock, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';

export default function SubjectAnalytics({ semesterId, sectionId, subjectId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!semesterId) return;
    setLoading(true);
    api.getSubjectAnalytics({
      semester_id: semesterId,
      section_id: sectionId || undefined,
      subject_id: subjectId || undefined,
    }).then((res) => {
      setData(res);
      setLoading(false);
    }).catch((err) => {
      console.error(err);
      setLoading(false);
    });
  }, [semesterId, sectionId, subjectId]);

  if (loading) {
    return (
      <div className="analytics-loading-box card">
        <div className="spin-loader" />
        <span>Aggregating subject-level examination records...</span>
      </div>
    );
  }

  if (!data || !data.subjects || data.subjects.length === 0) {
    return (
      <div className="card empty-analytics-card">
        <BookOpen size={24} className="text-muted" />
        <p>No subjects configured or no records uploaded for this semester.</p>
      </div>
    );
  }

  const { subjects } = data;

  return (
    <div className="subject-analytics-container">
      <div className="view-header-flex">
        <div>
          <h2 className="admin-page-title">Curriculum Subject Performance Analysis</h2>
          <p className="admin-page-subtitle">
            Course-by-course assessment metrics: Average marks, score ranges, pass rates, and attendance coverage.
          </p>
        </div>
      </div>

      <div className="subject-cards-grid">
        {subjects.map((sub) => (
          <div key={sub.subjectId} className="card subject-analytics-card">
            <div className="subject-card-header">
              <div>
                <div className="subject-badge-group">
                  <span className="font-mono text-primary font-semibold">{sub.code}</span>
                  <span className="badge badge-outline">{sub.subjectType}</span>
                  <span className="badge badge-outline">{sub.credits} Credits</span>
                </div>
                <h3 className="subject-title">{sub.name}</h3>
              </div>
            </div>

            {sub.hasResultData ? (
              <div className="subject-metrics-strip">
                <div className="metric-cell">
                  <span className="metric-lbl">Average Marks</span>
                  <span className="metric-val font-mono">{sub.averageMarks ?? '—'}</span>
                </div>
                <div className="metric-cell">
                  <span className="metric-lbl">Highest / Lowest</span>
                  <span className="metric-val font-mono text-sm">
                    {sub.highestMarks ?? '—'} / {sub.lowestMarks ?? '—'}
                  </span>
                </div>
                <div className="metric-cell">
                  <span className="metric-lbl">Pass Rate</span>
                  <span className={`metric-val font-mono ${sub.passPercentage >= 85 ? 'text-primary' : 'text-yellow'}`}>
                    {sub.passPercentage !== null ? `${sub.passPercentage}%` : '—'}
                  </span>
                  <span className="metric-sub text-muted">
                    {sub.passCount} pass • {sub.failCount} fail
                  </span>
                </div>
                <div className="metric-cell">
                  <span className="metric-lbl">Subject Attendance</span>
                  <span className="metric-val font-mono">
                    {sub.averageAttendance !== null ? `${sub.averageAttendance}%` : 'Not Available'}
                  </span>
                </div>
              </div>
            ) : (
              <div className="subject-empty-note">
                <Clock size={14} className="text-muted" />
                <span>Semester result records not yet uploaded for this subject.</span>
              </div>
            )}

            {/* Grade breakdown if available */}
            {sub.gradeDistribution && Object.keys(sub.gradeDistribution).length > 0 && (
              <div className="subject-grade-chips">
                <span className="chips-label">Grade Spread:</span>
                <div className="chips-list">
                  {Object.entries(sub.gradeDistribution).map(([grade, count]) => (
                    <span key={grade} className={`grade-chip ${grade === 'F' ? 'chip-fail' : ''}`}>
                      <strong>{grade}:</strong> {count}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
