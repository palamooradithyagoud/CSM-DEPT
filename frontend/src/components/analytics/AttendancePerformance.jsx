import React, { useState, useEffect } from 'react';
import { Activity, Info, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import { api } from '../../services/api';

export default function AttendancePerformance({ semesterId, sectionId, subjectId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!semesterId) return;
    setLoading(true);
    api.getAttendancePerformance({
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
        <span>Evaluating attendance-performance association...</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card empty-analytics-card">
        <Activity size={24} className="text-muted" />
        <p>Select a semester to evaluate attendance vs examination marks.</p>
      </div>
    );
  }

  const isSuccess = data.status === 'SUCCESS';
  const isInsufficient = data.status === 'INSUFFICIENT_DATA';
  const isUndefined = data.status === 'UNDEFINED_VARIATION';

  return (
    <div className="attendance-performance-view">
      <div className="view-header-flex">
        <div>
          <h2 className="admin-page-title">Attendance vs Examination Performance Association</h2>
          <p className="admin-page-subtitle">
            Statistical observation mapping student subject attendance percentages with verified semester examination scores.
          </p>
        </div>
      </div>

      {/* Association Stats Summary */}
      <div className="card correlation-summary-card">
        <div className="correlation-header-row">
          <div className="metric-group">
            <span className="metric-lbl">Analysis Scope</span>
            <span className="metric-title font-semibold text-white">
              {subjectId ? 'Selected Course' : 'All Curricular Subjects'}
            </span>
          </div>

          <div className="metric-group">
            <span className="metric-lbl">Sample Size (Paired Observations)</span>
            <span className="metric-val font-mono">{data.sampleSize ?? 0}</span>
          </div>

          {isSuccess && (
            <>
              <div className="metric-group">
                <span className="metric-lbl">Pearson Correlation (r)</span>
                <span className={`metric-val font-mono ${data.correlation >= 0.4 ? 'text-primary' : (data.correlation <= -0.4 ? 'text-danger' : 'text-white')}`}>
                  {data.correlation !== null ? `${data.correlation > 0 ? '+' : ''}${data.correlation}` : '—'}
                </span>
              </div>

              <div className="metric-group">
                <span className="metric-lbl">Average Marks</span>
                <span className="metric-val font-mono">{data.averageMarks}</span>
              </div>

              <div className="metric-group">
                <span className="metric-lbl">Average Attendance</span>
                <span className="metric-val font-mono">{data.averageAttendance}%</span>
              </div>
            </>
          )}
        </div>

        {/* Interpretation Banner */}
        <div className={`correlation-interpretation-strip ${isSuccess ? 'strip-success' : 'strip-warning'}`}>
          <div className="strip-title-row">
            {isSuccess ? <CheckCircle2 size={16} className="text-primary" /> : <AlertTriangle size={16} className="text-warning" />}
            <strong>{data.interpretation}</strong>
          </div>
          {data.trendline && (
            <div className="trendline-info font-mono text-xs">
              Regression Trend: {data.trendline.formula}
            </div>
          )}
          <div className="disclaimer-note text-muted text-xs">
            <Info size={12} className="inline mr-1" />
            {data.note || 'Statistical correlation measures observed linear association and does not imply direct causation.'}
          </div>
        </div>
      </div>

      {/* Observations Table */}
      {data.dataPoints && data.dataPoints.length > 0 && (
        <div className="card table-card">
          <div className="table-header-info">
            <span className="count-label">
              Observed Student-Subject Data Points ({data.dataPoints.length})
            </span>
          </div>

          <div className="table-responsive">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Roll Number</th>
                  <th>Student Name</th>
                  <th>Subject</th>
                  <th>Attendance %</th>
                  <th>Examination Marks</th>
                  <th>Grade</th>
                </tr>
              </thead>
              <tbody>
                {data.dataPoints.slice(0, 50).map((dp, i) => (
                  <tr key={i}>
                    <td className="font-mono text-primary">{dp.rollNumber}</td>
                    <td className="font-semibold text-white">{dp.studentName}</td>
                    <td>
                      <span className="badge badge-outline">{dp.subjectCode}</span>
                    </td>
                    <td className="font-mono font-semibold">
                      <span className={dp.attendance >= 75 ? 'text-primary' : 'text-danger'}>
                        {dp.attendance}%
                      </span>
                    </td>
                    <td className="font-mono font-semibold text-white">
                      {dp.marks}
                    </td>
                    <td>
                      <span className="badge badge-success">{dp.grade || '—'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data.dataPoints.length > 50 && (
            <div className="p-3 text-center text-muted text-xs">
              Displaying first 50 observations.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
