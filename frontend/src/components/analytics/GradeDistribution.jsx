import React, { useState, useEffect } from 'react';
import { Award, Clock, BarChart3 } from 'lucide-react';
import { api } from '../../services/api';

export default function GradeDistribution({ semesterId, sectionId, subjectId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!semesterId) return;
    setLoading(true);
    api.getGradeDistribution({
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
        <span>Aggregating grade distribution...</span>
      </div>
    );
  }

  if (!data || !data.available || !data.distribution || data.distribution.length === 0) {
    return (
      <div className="card empty-analytics-card">
        <Clock size={24} className="text-muted" />
        <p>{data?.message || 'No examination grade records available for this selection.'}</p>
      </div>
    );
  }

  const { distribution, totalGradesRecorded } = data;
  const maxCount = Math.max(...distribution.map((d) => d.count), 1);

  return (
    <div className="grade-distribution-view">
      <div className="view-header-flex">
        <div>
          <h2 className="admin-page-title">Cohort Examination Grade Distribution</h2>
          <p className="admin-page-subtitle">
            Observed grade spectrum across {totalGradesRecorded} verified subject examinations. Zero synthetic buckets.
          </p>
        </div>
      </div>

      <div className="card distribution-card">
        <div className="distribution-bars-container">
          {distribution.map((item) => {
            const heightPct = Math.round((item.count / maxCount) * 100);
            const isFail = item.grade === 'F';
            const isTop = ['O', 'A+'].includes(item.grade);

            return (
              <div key={item.grade} className="hist-col">
                <div className="hist-val-top font-mono text-xs">
                  {item.count}
                </div>
                <div className="hist-track">
                  <div
                    className={`hist-bar ${isFail ? 'bar-fail' : (isTop ? 'bar-top' : 'bar-normal')}`}
                    style={{ height: `${heightPct}%` }}
                    title={`${item.grade}: ${item.count} (${item.percentage}%)`}
                  />
                </div>
                <span className="hist-label font-mono font-bold">
                  {item.grade}
                </span>
                <span className="hist-pct font-mono text-muted text-xs">
                  {item.percentage}%
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Grade Table Breakdown */}
      <div className="card table-card">
        <div className="table-header-info">
          <span className="count-label">Detailed Grade Frequency</span>
        </div>
        <div className="table-responsive">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Letter Grade</th>
                <th>Frequency (Count)</th>
                <th>Cohort Proportion</th>
                <th>Status Classification</th>
              </tr>
            </thead>
            <tbody>
              {distribution.map((d) => (
                <tr key={d.grade}>
                  <td>
                    <span className={`badge ${d.grade === 'F' ? 'badge-danger' : 'badge-success'}`}>
                      Grade {d.grade}
                    </span>
                  </td>
                  <td className="font-mono font-semibold text-white">{d.count}</td>
                  <td className="font-mono">{d.percentage}%</td>
                  <td>
                    <span className="text-muted text-sm">
                      {d.grade === 'F' ? 'Academic Backlog (Fail)' : (['O', 'A+'].includes(d.grade) ? 'Exemplary / Distinction' : 'Qualified Passing')}
                    </span>
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
