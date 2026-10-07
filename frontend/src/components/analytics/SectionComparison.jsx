import React, { useState, useEffect } from 'react';
import { Layers, BarChart2, CheckCircle2, Clock, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';

export default function SectionComparison({ semesterId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [metricTab, setMetricTab] = useState('sgpa'); // 'sgpa' | 'attendance' | 'pass'

  useEffect(() => {
    if (!semesterId) return;
    setLoading(true);
    api.getSectionAnalytics(semesterId).then((res) => {
      setData(res);
      setLoading(false);
    }).catch((err) => {
      console.error(err);
      setLoading(false);
    });
  }, [semesterId]);

  if (loading) {
    return (
      <div className="analytics-loading-box card">
        <div className="spin-loader" />
        <span>Aggregating cross-section metrics for {semesterId}...</span>
      </div>
    );
  }

  if (!data || !data.sections || data.sections.length === 0) {
    return (
      <div className="card empty-analytics-card">
        <Layers size={24} className="text-muted" />
        <p>No section records configured for this semester.</p>
      </div>
    );
  }

  const { sections, semesterName } = data;

  return (
    <div className="section-comparison-container">
      <div className="view-header-flex">
        <div>
          <h2 className="admin-page-title">Cross-Section Comparative Analytics</h2>
          <p className="admin-page-subtitle">
            Side-by-side performance evaluation across all sections of {semesterName || 'the current semester'}.
          </p>
        </div>

        {/* Visual Metric Switcher */}
        <div className="metric-switcher-btn-group">
          <button
            className={`btn btn-xs ${metricTab === 'sgpa' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setMetricTab('sgpa')}
          >
            Average SGPA
          </button>
          <button
            className={`btn btn-xs ${metricTab === 'attendance' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setMetricTab('attendance')}
          >
            Attendance %
          </button>
          <button
            className={`btn btn-xs ${metricTab === 'pass' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setMetricTab('pass')}
          >
            Pass %
          </button>
        </div>
      </div>

      {/* Visual Comparative Bars */}
      <div className="card visual-bars-card">
        <h3 className="section-title">
          {metricTab === 'sgpa' && 'Average SGPA Comparison by Section (Scale: 0 - 10)'}
          {metricTab === 'attendance' && 'Average Subject Attendance Comparison (Scale: 0 - 100%)'}
          {metricTab === 'pass' && 'Pass Percentage Comparison (Scale: 0 - 100%)'}
        </h3>

        <div className="bars-list">
          {sections.map((sec) => {
            let val = null;
            let displayVal = 'Not Available';
            let widthPct = 0;

            if (metricTab === 'sgpa') {
              val = sec.averageSGPA;
              if (val !== null) {
                displayVal = `${val} / 10.0`;
                widthPct = Math.min((val / 10) * 100, 100);
              }
            } else if (metricTab === 'attendance') {
              val = sec.averageAttendance;
              if (val !== null) {
                displayVal = `${val}%`;
                widthPct = Math.min(val, 100);
              }
            } else if (metricTab === 'pass') {
              val = sec.passPercentage;
              if (val !== null) {
                displayVal = `${val}%`;
                widthPct = Math.min(val, 100);
              }
            }

            return (
              <div key={sec.sectionId} className="bar-row">
                <div className="bar-label-col">
                  <span className="font-semibold text-white">Section {sec.sectionName}</span>
                  <span className="text-muted text-xs">({sec.totalStudents} enrolled)</span>
                </div>
                <div className="bar-track-col">
                  <div className="bar-track">
                    <div
                      className={`bar-fill ${val !== null ? 'bg-primary' : 'bg-muted'}`}
                      style={{ width: `${widthPct}%` }}
                    />
                  </div>
                </div>
                <div className="bar-val-col">
                  <span className={`font-mono text-sm ${val !== null ? 'text-primary font-semibold' : 'text-muted'}`}>
                    {displayVal}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Detailed Comparison Table */}
      <div className="card table-card">
        <div className="table-header-info">
          <span className="count-label">Section Metric Matrix</span>
        </div>

        <div className="table-responsive">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Section</th>
                <th>Enrolled Students</th>
                <th>Avg SGPA</th>
                <th>Avg Attendance</th>
                <th>Pass Percentage</th>
                <th>Results Status</th>
                <th>Attendance Status</th>
              </tr>
            </thead>
            <tbody>
              {sections.map((sec) => (
                <tr key={sec.sectionId}>
                  <td>
                    <span className="section-pill font-semibold">Section {sec.sectionName}</span>
                  </td>
                  <td>{sec.totalStudents} Students</td>
                  <td className="font-mono">
                    {sec.averageSGPA !== null ? (
                      <span className="text-primary font-semibold">{sec.averageSGPA}</span>
                    ) : (
                      <span className="text-muted">Not Available</span>
                    )}
                  </td>
                  <td className="font-mono">
                    {sec.averageAttendance !== null ? (
                      <span>{sec.averageAttendance}%</span>
                    ) : (
                      <span className="text-muted">Not Available</span>
                    )}
                  </td>
                  <td className="font-mono">
                    {sec.passPercentage !== null ? (
                      <span className={sec.passPercentage >= 85 ? 'text-primary' : 'text-yellow'}>
                        {sec.passPercentage}%
                      </span>
                    ) : (
                      <span className="text-muted">Not Available</span>
                    )}
                  </td>
                  <td>
                    {sec.resultsAvailable ? (
                      <span className="badge badge-success">
                        <CheckCircle2 size={12} /> Available
                      </span>
                    ) : (
                      <span className="badge badge-outline">
                        <Clock size={12} /> Pending
                      </span>
                    )}
                  </td>
                  <td>
                    {sec.attendanceAvailable ? (
                      <span className="badge badge-success">
                        <CheckCircle2 size={12} /> Available
                      </span>
                    ) : (
                      <span className="badge badge-outline">
                        <Clock size={12} /> Pending
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
