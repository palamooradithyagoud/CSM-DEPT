import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import '../../styles/reports.css';

export default function ReportsHub() {
  // Academic Context
  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState('');
  const [academicYears, setAcademicYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState('');
  const [semesters, setSemesters] = useState([]);
  const [selectedSemester, setSelectedSemester] = useState('');
  const [sections, setSections] = useState([]);
  const [selectedSection, setSelectedSection] = useState('');
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');

  // Student Search
  const [studentSearch, setStudentSearch] = useState('');
  const [studentSearchResults, setStudentSearchResults] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);

  // Report Selection & Format
  const [reportType, setReportType] = useState('department'); // department, section, student, subject, insights
  const [exportFormat, setExportFormat] = useState('pdf'); // pdf, excel, csv

  // Preview State
  const [previewData, setPreviewData] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);

  // Export State
  const [isExporting, setIsExporting] = useState(false);
  const [exportMessage, setExportMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  // 1. Initial Hierarchy Load: Batches
  useEffect(() => {
    async function loadBatches() {
      try {
        const batchList = await api.getBatches();
        setBatches(batchList || []);
        if (batchList && batchList.length > 0) {
          setSelectedBatch(batchList[0].id);
        }
      } catch (err) {
        console.error('Failed to load academic batches:', err);
      }
    }
    loadBatches();
  }, []);

  // 2. Cascade Batch -> Academic Years (Each batch has 4 years)
  useEffect(() => {
    if (!selectedBatch) {
      setAcademicYears([]);
      setSelectedYear('');
      return;
    }
    async function loadYears() {
      try {
        const years = await api.getAcademicYears(selectedBatch);
        setAcademicYears(years || []);
        if (years && years.length > 0) {
          setSelectedYear(years[0].id);
        } else {
          setSelectedYear('');
        }
      } catch (err) {
        console.error('Failed to load academic years:', err);
      }
    }
    loadYears();
  }, [selectedBatch]);

  // 3. Cascade Academic Year -> Semesters (Each year has 2 distinct semesters)
  useEffect(() => {
    if (!selectedYear) {
      setSemesters([]);
      setSelectedSemester('');
      return;
    }
    async function loadSemesters() {
      try {
        const sems = await api.getSemesters(selectedYear);
        setSemesters(sems || []);
        if (sems && sems.length > 0) {
          setSelectedSemester(sems[0].id);
        } else {
          setSelectedSemester('');
        }
      } catch (err) {
        console.error('Failed to load semesters:', err);
      }
    }
    loadSemesters();
  }, [selectedYear]);

  // 4. Cascade Semester -> Sections and Distinct Subjects (Each semester has different subjects)
  useEffect(() => {
    if (!selectedSemester) {
      setSections([]);
      setSelectedSection('');
      setSubjects([]);
      setSelectedSubject('');
      return;
    }
    async function loadSectionsAndSubjects() {
      try {
        const [secs, subs] = await Promise.all([
          api.getSections(selectedSemester),
          api.getSubjects(selectedSemester)
        ]);
        setSections(secs || []);
        setSelectedSection(secs && secs.length > 0 ? secs[0].id : '');
        setSubjects(subs || []);
        setSelectedSubject(subs && subs.length > 0 ? subs[0].id : '');
      } catch (err) {
        console.error('Failed to load sections and subjects:', err);
      }
    }
    loadSectionsAndSubjects();
  }, [selectedSemester]);

  // Student Search query
  useEffect(() => {
    if (!studentSearch || studentSearch.length < 2) {
      setStudentSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const res = await api.getStudents({ search: studentSearch, batch_id: selectedBatch, limit: 5 });
        setStudentSearchResults(res.students || []);
      } catch (err) {
        console.error('Student search failed:', err);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [studentSearch, selectedBatch]);

  // Load Preview Data
  useEffect(() => {
    async function fetchPreview() {
      setLoadingPreview(true);
      setErrorMessage(null);
      try {
        const params = {
          type: reportType,
          batch_id: selectedBatch,
          semester_id: selectedSemester,
          section_id: selectedSection,
        };
        if (reportType === 'section') params.id = selectedSection;
        if (reportType === 'subject') params.id = selectedSubject;
        if (reportType === 'student') params.id = selectedStudent?.id;

        if (reportType === 'section' && !selectedSection) {
          setPreviewData(null);
          setLoadingPreview(false);
          return;
        }
        if (reportType === 'subject' && !selectedSubject) {
          setPreviewData(null);
          setLoadingPreview(false);
          return;
        }
        if (reportType === 'student' && !selectedStudent) {
          setPreviewData(null);
          setLoadingPreview(false);
          return;
        }

        const data = await api.previewReport(params);
        setPreviewData(data);
      } catch (err) {
        console.error('Preview error:', err);
        setPreviewData(null);
      } finally {
        setLoadingPreview(false);
      }
    }
    fetchPreview();
  }, [reportType, selectedBatch, selectedSemester, selectedSection, selectedSubject, selectedStudent]);

  // Handle Export
  const handleExport = async (overrideType, overrideFormat) => {
    const type = overrideType || reportType;
    const format = overrideFormat || exportFormat;

    setIsExporting(true);
    setExportMessage(null);
    setErrorMessage(null);

    try {
      let res;
      if (type === 'department') {
        res = await api.exportDepartmentReport({
          batch_id: selectedBatch,
          semester_id: selectedSemester,
          format,
        });
      } else if (type === 'section') {
        if (!selectedSection) throw new Error('Please select a section to export.');
        res = await api.exportSectionReport(selectedSection, {
          semester_id: selectedSemester,
          format,
        });
      } else if (type === 'student') {
        if (!selectedStudent) throw new Error('Please search and select a student to export.');
        res = await api.exportStudentReport(selectedStudent.id, {
          semester_id: selectedSemester,
          format,
        });
      } else if (type === 'subject') {
        if (!selectedSubject) throw new Error('Please select a subject to export.');
        res = await api.exportSubjectReport(selectedSubject, {
          semester_id: selectedSemester,
          format,
        });
      } else if (type === 'insights') {
        res = await api.exportInsightsReport({
          batch_id: selectedBatch,
          semester_id: selectedSemester,
          section_id: selectedSection,
          format,
        });
      }

      setExportMessage(`Successfully generated & downloaded: ${res?.filename || 'Document'}`);
      setTimeout(() => setExportMessage(null), 5000);
    } catch (err) {
      console.error('Export failed:', err);
      setErrorMessage(err.message || 'Report generation failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="reports-hub">
      {/* Header Banner */}
      <div className="reports-header-card">
        <div className="reports-header-titles">
          <div className="reports-badge">PHASE 5 — PRODUCTION REPORTING ENGINE</div>
          <h2 className="reports-title">Institutional Reports & Document Exports</h2>
          <p className="reports-subtitle">
            Generate verifiable, print-ready PDF dossiers, structured Excel workbooks, and CSV exports grounded in verified departmental data.
          </p>
        </div>
        <div className="reports-header-actions">
          <button
            id="quick-export-dept-pdf"
            className="reports-btn-primary"
            onClick={() => handleExport('department', 'pdf')}
            disabled={isExporting}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
            </svg>
            Instant Department PDF
          </button>
        </div>
      </div>

      {/* Alert Notices */}
      {exportMessage && (
        <div className="reports-notice-banner success">
          <span className="notice-icon">✓</span>
          <span>{exportMessage}</span>
        </div>
      )}
      {errorMessage && (
        <div className="reports-notice-banner error">
          <span className="notice-icon">⚠</span>
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Quick Export Cards Carousel / Grid */}
      <div className="quick-exports-grid">
        <div className="quick-export-card" onClick={() => handleExport('department', 'pdf')}>
          <div className="quick-card-icon">📄</div>
          <div className="quick-card-info">
            <h4>Department Dossier</h4>
            <p>Comprehensive overview, KPIs, subject breakdown & section comparisons.</p>
          </div>
          <span className="quick-export-tag">PDF</span>
        </div>

        <div className="quick-export-card" onClick={() => handleExport('insights', 'pdf')}>
          <div className="quick-card-icon">🎯</div>
          <div className="quick-card-info">
            <h4>Academic Insights & Watchlist</h4>
            <p>Critical student attention alerts, flagged courses, and recommendations.</p>
          </div>
          <span className="quick-export-tag">PDF</span>
        </div>

        <div className="quick-export-card" onClick={() => handleExport('department', 'excel')}>
          <div className="quick-card-icon">📊</div>
          <div className="quick-card-info">
            <h4>Executive Excel Sheet</h4>
            <p>Multi-tab tabular workbook for spreadsheet analytics & reporting.</p>
          </div>
          <span className="quick-export-tag excel">XLSX</span>
        </div>

        <div className="quick-export-card" onClick={() => handleExport('insights', 'csv')}>
          <div className="quick-card-icon">📑</div>
          <div className="quick-card-info">
            <h4>Raw Watchlist CSV</h4>
            <p>Clean UTF-8 data export for administrative archives.</p>
          </div>
          <span className="quick-export-tag csv">CSV</span>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="reports-workspace-grid">
        {/* Left Column: Configuration & Selectors */}
        <div className="reports-controls-panel">
          <h3 className="panel-title">1. Report Parameters</h3>

          {/* Academic Context Cascading Dropdowns */}
          <div className="control-group">
            <label className="control-label">Batch Cohort</label>
            <select
              id="report-select-batch"
              className="reports-select"
              value={selectedBatch}
              onChange={(e) => setSelectedBatch(e.target.value)}
            >
              {batches.map((b) => (
                <option key={b.id} value={b.id}>
                  Batch {b.name}
                </option>
              ))}
            </select>
          </div>

          <div className="control-row">
            <div className="control-group">
              <label className="control-label">Academic Year (4 Years)</label>
              <select
                id="report-select-year"
                className="reports-select"
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
              >
                {academicYears.map((y) => (
                  <option key={y.id} value={y.id}>
                    {y.name} {y.calendarYear ? `(${y.calendarYear})` : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="control-group">
              <label className="control-label">Semester (2 Sems / Year)</label>
              <select
                id="report-select-semester"
                className="reports-select"
                value={selectedSemester}
                onChange={(e) => setSelectedSemester(e.target.value)}
              >
                {semesters.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} (Sem {s.semesterNumber})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <h3 className="panel-title" style={{ marginTop: '1.25rem' }}>
            2. Report Scope
          </h3>

          {/* Report Type Tabs */}
          <div className="report-type-pills">
            {[
              { id: 'department', label: 'Department' },
              { id: 'insights', label: 'Insights & Watchlist' },
              { id: 'section', label: 'Section' },
              { id: 'subject', label: 'Subject' },
              { id: 'student', label: 'Student Dossier' },
            ].map((t) => (
              <button
                key={t.id}
                id={`report-type-${t.id}`}
                className={`type-pill ${reportType === t.id ? 'active' : ''}`}
                onClick={() => setReportType(t.id)}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Dynamic Context Fields based on Report Type */}
          {reportType === 'section' && (
            <div className="control-group" style={{ marginTop: '1rem' }}>
              <label className="control-label">Select Section</label>
              <select
                id="report-select-section"
                className="reports-select"
                value={selectedSection}
                onChange={(e) => setSelectedSection(e.target.value)}
              >
                {sections.map((sec) => (
                  <option key={sec.id} value={sec.id}>
                    Section {sec.name} {sec.roomNumber ? `(${sec.roomNumber})` : ''}
                  </option>
                ))}
              </select>
            </div>
          )}

          {reportType === 'subject' && (
            <div className="control-group" style={{ marginTop: '1rem' }}>
              <label className="control-label">Select Subject</label>
              <select
                id="report-select-subject"
                className="reports-select"
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
              >
                {subjects.map((sub) => (
                  <option key={sub.id} value={sub.id}>
                    {sub.code} — {sub.name} ({sub.credits} Credits • {sub.subjectType || 'THEORY'})
                  </option>
                ))}
              </select>
            </div>
          )}

          {reportType === 'student' && (
            <div className="control-group" style={{ marginTop: '1rem' }}>
              <label className="control-label">Search Student (Roll No or Name)</label>
              <input
                id="report-student-search"
                type="text"
                className="reports-input"
                placeholder="Type 25881A... or name"
                value={studentSearch}
                onChange={(e) => setStudentSearch(e.target.value)}
              />
              {studentSearchResults.length > 0 && (
                <div className="search-dropdown-menu">
                  {studentSearchResults.map((st) => (
                    <div
                      key={st.id}
                      className="search-dropdown-item"
                      onClick={() => {
                        setSelectedStudent(st);
                        setStudentSearch(`${st.rollNumber} - ${st.name}`);
                        setStudentSearchResults([]);
                      }}
                    >
                      <span className="roll">{st.rollNumber}</span>
                      <span className="name">{st.name}</span>
                    </div>
                  ))}
                </div>
              )}
              {selectedStudent && (
                <div className="selected-student-badge">
                  Selected: <strong>{selectedStudent.name}</strong> ({selectedStudent.rollNumber})
                </div>
              )}
            </div>
          )}

          <h3 className="panel-title" style={{ marginTop: '1.25rem' }}>
            3. Export Format
          </h3>

          <div className="format-picker-grid">
            <button
              id="report-format-pdf"
              className={`format-btn ${exportFormat === 'pdf' ? 'active' : ''}`}
              onClick={() => setExportFormat('pdf')}
            >
              <span className="format-title">PDF Document</span>
              <span className="format-desc">Institutional formatted dossier</span>
            </button>

            <button
              id="report-format-excel"
              className={`format-btn ${exportFormat === 'excel' ? 'active' : ''}`}
              onClick={() => setExportFormat('excel')}
            >
              <span className="format-title">Excel (.xlsx)</span>
              <span className="format-desc">Structured tabular sheet</span>
            </button>

            <button
              id="report-format-csv"
              className={`format-btn ${exportFormat === 'csv' ? 'active' : ''}`}
              onClick={() => setExportFormat('csv')}
            >
              <span className="format-title">CSV</span>
              <span className="format-desc">Raw UTF-8 archive</span>
            </button>
          </div>

          {/* Download Action Trigger */}
          <div className="export-action-block">
            <button
              id="report-generate-btn"
              className="reports-download-btn"
              onClick={() => handleExport()}
              disabled={isExporting}
            >
              {isExporting ? (
                <>
                  <span className="spinner-inline" /> Generating {exportFormat.toUpperCase()}...
                </>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
                  </svg>
                  Generate & Download {exportFormat.toUpperCase()}
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Live Data Preview */}
        <div className="reports-preview-panel">
          <div className="preview-header">
            <div>
              <h3 className="panel-title">Document Preview</h3>
              <p className="preview-meta">
                Verifying live dataset before compilation ({reportType.toUpperCase()} — {exportFormat.toUpperCase()})
              </p>
            </div>
            <span className="preview-badge-status">
              {loadingPreview ? 'Fetching Data...' : previewData ? '✓ Verified Source Data' : 'No Selection'}
            </span>
          </div>

          <div className="preview-content-box">
            {loadingPreview ? (
              <div className="preview-loading-state">
                <div className="spinner-lg" />
                <p>Assembling institutional report metrics...</p>
              </div>
            ) : !previewData ? (
              <div className="preview-empty-state">
                <span className="empty-icon">📋</span>
                <h4>No Data Available</h4>
                <p>Please select a valid academic semester, section, subject, or student to view preview.</p>
              </div>
            ) : (
              <div className="preview-structured-view">
                {/* Department Preview */}
                {reportType === 'department' && (
                  <>
                    <div className="preview-banner-box">
                      <h4>DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING</h4>
                      <p>
                        {previewData.batchName} &bull; {previewData.semesterName}
                      </p>
                    </div>

                    <div className="preview-metrics-row">
                      <div className="metric-cell">
                        <span className="label">Total Students</span>
                        <span className="val">{previewData.kpis?.totalStudents || 0}</span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Average SGPA</span>
                        <span className="val">{previewData.kpis?.averageSGPA || 'N/A'}</span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Average Attendance</span>
                        <span className="val">
                          {previewData.kpis?.averageAttendance !== null && previewData.kpis?.averageAttendance !== undefined
                            ? `${previewData.kpis.averageAttendance}%`
                            : 'N/A'}
                        </span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Pass Rate</span>
                        <span className="val">
                          {previewData.kpis?.passPercentage !== null && previewData.kpis?.passPercentage !== undefined
                            ? `${previewData.kpis.passPercentage}%`
                            : 'N/A'}
                        </span>
                      </div>
                    </div>

                    <div className="preview-section-title">Subject Summary ({previewData.subjects?.length || 0} Courses)</div>
                    <table className="preview-mini-table">
                      <thead>
                        <tr>
                          <th>Code</th>
                          <th>Subject Name</th>
                          <th>Avg Marks</th>
                          <th>Pass %</th>
                          <th>Failures</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(previewData.subjects || []).slice(0, 5).map((s, idx) => (
                          <tr key={idx}>
                            <td><strong>{s.code}</strong></td>
                            <td>{s.name}</td>
                            <td>{s.averageMarks || 'N/A'}</td>
                            <td>{s.passPercentage !== null ? `${s.passPercentage}%` : 'N/A'}</td>
                            <td>{s.failureCount || 0}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>

                    <div className="preview-section-title">Section Comparison ({previewData.sections?.length || 0} Sections)</div>
                    <table className="preview-mini-table">
                      <thead>
                        <tr>
                          <th>Section</th>
                          <th>Students</th>
                          <th>Avg SGPA</th>
                          <th>Attendance %</th>
                          <th>Pass %</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(previewData.sections || []).map((sec, idx) => (
                          <tr key={idx}>
                            <td><strong>Section {sec.sectionName}</strong></td>
                            <td>{sec.studentCount}</td>
                            <td>{sec.averageSGPA || 'N/A'}</td>
                            <td>{sec.averageAttendance !== null ? `${sec.averageAttendance}%` : 'N/A'}</td>
                            <td>{sec.passPercentage !== null ? `${sec.passPercentage}%` : 'N/A'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </>
                )}

                {/* Section Preview */}
                {reportType === 'section' && (
                  <>
                    <div className="preview-banner-box">
                      <h4>SECTION {previewData.sectionName} PERFORMANCE ANALYSIS</h4>
                      <p>
                        {previewData.batchName} &bull; {previewData.semesterName}
                      </p>
                    </div>
                    <div className="preview-metrics-row">
                      <div className="metric-cell">
                        <span className="label">Students</span>
                        <span className="val">{previewData.studentCount || 0}</span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Avg SGPA</span>
                        <span className="val">{previewData.averageSGPA || 'N/A'}</span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Attendance</span>
                        <span className="val">
                          {previewData.averageAttendance !== null ? `${previewData.averageAttendance}%` : 'N/A'}
                        </span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Flagged</span>
                        <span className="val" style={{ color: '#FF6268' }}>{previewData.flaggedStudentsCount || 0}</span>
                      </div>
                    </div>
                  </>
                )}

                {/* Student Preview */}
                {reportType === 'student' && (
                  <>
                    <div className="preview-banner-box">
                      <h4>STUDENT DOSSIER — {previewData.name}</h4>
                      <p>
                        Roll No: {previewData.rollNumber} &bull; Section {previewData.sectionName} &bull; Batch {previewData.batchName}
                      </p>
                    </div>
                    <div className="preview-metrics-row">
                      <div className="metric-cell">
                        <span className="label">Latest SGPA</span>
                        <span className="val">{previewData.sgpa || 'N/A'}</span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Cumulative CGPA</span>
                        <span className="val">{previewData.cgpa || 'N/A'}</span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Attendance</span>
                        <span className="val">
                          {previewData.attendancePercentage !== null ? `${previewData.attendancePercentage}%` : 'N/A'}
                        </span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Trend</span>
                        <span className="val">{previewData.trend || 'STABLE'}</span>
                      </div>
                    </div>
                  </>
                )}

                {/* Subject Preview */}
                {reportType === 'subject' && (
                  <>
                    <div className="preview-banner-box">
                      <h4>{previewData.code} — {previewData.name}</h4>
                      <p>
                        Credits: {previewData.credits} &bull; Type: {previewData.subjectType} &bull; {previewData.semesterName}
                      </p>
                    </div>
                    <div className="preview-metrics-row">
                      <div className="metric-cell">
                        <span className="label">Evaluated</span>
                        <span className="val">{previewData.studentCount || 0}</span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Avg Marks</span>
                        <span className="val">{previewData.averageMarks || 'N/A'}</span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Pass Rate</span>
                        <span className="val">
                          {previewData.passPercentage !== null ? `${previewData.passPercentage}%` : 'N/A'}
                        </span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Failures</span>
                        <span className="val" style={{ color: '#FF6268' }}>{previewData.failureCount || 0}</span>
                      </div>
                    </div>
                  </>
                )}

                {/* Insights Preview */}
                {reportType === 'insights' && (
                  <>
                    <div className="preview-banner-box">
                      <h4>ACADEMIC INSIGHTS & ATTENTION WATCHLIST</h4>
                      <p>Context: {previewData.semesterName}</p>
                    </div>
                    <div className="preview-metrics-row">
                      <div className="metric-cell">
                        <span className="label">Flagged Students</span>
                        <span className="val" style={{ color: '#FF6268' }}>
                          {previewData.summary?.studentsRequiringAttention || 0}
                        </span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Critical Issues</span>
                        <span className="val" style={{ color: '#FF6268' }}>
                          {previewData.summary?.criticalIssues || 0}
                        </span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Flagged Courses</span>
                        <span className="val">{previewData.summary?.subjectsRequiringAttention || 0}</span>
                      </div>
                      <div className="metric-cell">
                        <span className="label">Flagged Sections</span>
                        <span className="val">{previewData.summary?.sectionsRequiringAttention || 0}</span>
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
