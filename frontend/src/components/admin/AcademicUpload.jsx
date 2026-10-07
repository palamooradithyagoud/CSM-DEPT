import React, { useState, useEffect } from 'react';
import {
  UploadCloud,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ArrowRight,
  RefreshCw,
  Info,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
} from 'lucide-react';
import { api } from '../../services/api';

export default function AcademicUpload({ initialContext, onUploadSuccess }) {
  // Cascading Context State
  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState(initialContext?.batchId || '');
  const [academicYears, setAcademicYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState(initialContext?.academicYearId || '');
  const [semesters, setSemesters] = useState([]);
  const [selectedSemester, setSelectedSemester] = useState(initialContext?.semesterId || '');
  const [sections, setSections] = useState([]);
  const [selectedSection, setSelectedSection] = useState(initialContext?.sectionId || '');
  const [dataType, setDataType] = useState('ATTENDANCE');

  // File & Pipeline State
  const [file, setFile] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationReport, setValidationReport] = useState(null);
  const [showErrors, setShowErrors] = useState(false);
  const [previewPage, setPreviewPage] = useState(1);
  const previewPageSize = 10;

  // Duplicate Resolution & Confirmation
  const [duplicateStrategy, setDuplicateStrategy] = useState('SKIP');
  const [isConfirming, setIsConfirming] = useState(false);
  const [confirmSuccess, setConfirmSuccess] = useState(null);
  const [generalError, setGeneralError] = useState('');

  // 1. Load Batches on mount
  useEffect(() => {
    api.getBatches().then((bList) => {
      setBatches(bList);
      if (!selectedBatch && bList.length > 0) {
        const pref = bList.find((b) => b.name === '2025-2029') || bList[0];
        setSelectedBatch(pref.id);
      }
    }).catch((err) => setGeneralError(err.message));
  }, []);

  // 2. Load Academic Years when selectedBatch changes
  useEffect(() => {
    if (!selectedBatch) return;
    api.getAcademicYears(selectedBatch).then((years) => {
      setAcademicYears(years);
      if (years.length > 0) {
        const prefYear = years.find((y) => y.yearNumber === 2) || years[0];
        setSelectedYear(prefYear.id);
      } else {
        setSelectedYear('');
      }
    }).catch(console.error);
  }, [selectedBatch]);

  // 3. Load Semesters when selectedYear changes
  useEffect(() => {
    if (!selectedYear) {
      setSemesters([]);
      setSelectedSemester('');
      return;
    }
    api.getSemesters(selectedYear).then((sems) => {
      setSemesters(sems);
      if (sems.length > 0) {
        const prefSem = sems.find((s) => s.semesterNumber === 3) || sems[0];
        setSelectedSemester(prefSem.id);
      } else {
        setSelectedSemester('');
      }
    }).catch(console.error);
  }, [selectedYear]);

  // 4. Load Sections when selectedSemester changes
  useEffect(() => {
    if (!selectedSemester) {
      setSections([]);
      setSelectedSection('');
      return;
    }
    api.getSections(selectedSemester).then((secs) => {
      setSections(secs);
      if (secs.length > 0) {
        setSelectedSection(secs[0].id);
      } else {
        setSelectedSection('');
      }
    }).catch(console.error);
  }, [selectedSemester]);

  // File select handler
  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      const ext = selected.name.split('.').pop().toLowerCase();
      if (!['xlsx', 'xls', 'csv'].includes(ext)) {
        setGeneralError('Invalid file format. Please upload an Excel (.xlsx) or CSV (.csv) file.');
        setFile(null);
        return;
      }
      setFile(selected);
      setValidationReport(null);
      setConfirmSuccess(null);
      setGeneralError('');
    }
  };

  // Drag-and-drop
  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      const ext = dropped.name.split('.').pop().toLowerCase();
      if (!['xlsx', 'xls', 'csv'].includes(ext)) {
        setGeneralError('Invalid file format. Please upload an Excel (.xlsx) or CSV (.csv) file.');
        return;
      }
      setFile(dropped);
      setValidationReport(null);
      setConfirmSuccess(null);
      setGeneralError('');
    }
  };

  // Validate File Pipeline
  const handleValidate = async () => {
    if (!file) {
      setGeneralError('Please select a file to validate.');
      return;
    }
    if (!selectedBatch || !selectedYear || !selectedSemester || !selectedSection) {
      setGeneralError('Please complete all academic context selectors.');
      return;
    }

    setIsValidating(true);
    setGeneralError('');
    setConfirmSuccess(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('batchId', selectedBatch);
    formData.append('academicYearId', selectedYear);
    formData.append('semesterId', selectedSemester);
    formData.append('sectionId', selectedSection);
    formData.append('dataType', dataType);

    try {
      const res = await api.validateUpload(formData);
      setValidationReport(res);
      setPreviewPage(1);
    } catch (err) {
      setGeneralError(err.message || 'File validation failed.');
    } finally {
      setIsValidating(false);
    }
  };

  // Confirm Import
  const handleConfirm = async () => {
    if (!validationReport?.fileToken) return;

    setIsConfirming(true);
    setGeneralError('');

    try {
      const res = await api.confirmUpload({
        fileToken: validationReport.fileToken,
        duplicateStrategy: duplicateStrategy,
      });

      setConfirmSuccess(res.data);
      setValidationReport(null);
      setFile(null);
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      setGeneralError(err.message || 'Transaction failed. All changes have been rolled back.');
    } finally {
      setIsConfirming(false);
    }
  };

  // Pagination for preview rows
  const previewRows = validationReport?.previewRows || [];
  const totalPreviewPages = Math.ceil(previewRows.length / previewPageSize) || 1;
  const currentPreviewRows = previewRows.slice(
    (previewPage - 1) * previewPageSize,
    previewPage * previewPageSize
  );

  return (
    <div className="upload-workflow-container">
      {/* Header */}
      <div className="upload-view-header">
        <div>
          <h1 className="admin-page-title">Academic Data Ingestion Engine</h1>
          <p className="admin-page-subtitle">
            Upload and transactionally verify official departmental attendance, mid-term marks, and semester results.
          </p>
        </div>
      </div>

      {generalError && (
        <div className="alert alert-error">
          <AlertTriangle size={18} />
          <span>{generalError}</span>
        </div>
      )}

      {confirmSuccess && (
        <div className="alert alert-success">
          <CheckCircle2 size={18} />
          <div>
            <strong>Import Succeeded!</strong>
            <div>
              {confirmSuccess.imported_count} records imported, {confirmSuccess.replaced_count} replaced, {confirmSuccess.skipped_count} skipped. Transaction committed atomically.
            </div>
          </div>
        </div>
      )}

      {/* STEP 1: Academic Context Selectors */}
      <div className="card upload-context-card">
        <div className="card-section-title">
          <span className="step-number">Step 1</span>
          <h3>Academic Context Selection</h3>
        </div>
        <p className="text-muted text-sm">
          Select the exact hierarchical target for this upload. Invalid section or student cross-assignments are automatically rejected.
        </p>

        <div className="grid-5-col">
          <div className="form-group">
            <label>Batch</label>
            <select
              value={selectedBatch}
              onChange={(e) => {
                setSelectedBatch(e.target.value);
                setValidationReport(null);
              }}
              className="form-select"
            >
              {batches.map((b) => (
                <option key={b.id} value={b.id}>
                  Batch {b.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Academic Year</label>
            <select
              value={selectedYear}
              onChange={(e) => {
                setSelectedYear(e.target.value);
                setValidationReport(null);
              }}
              className="form-select"
            >
              {academicYears.map((ay) => (
                <option key={ay.id} value={ay.id}>
                  {ay.name} ({ay.calendarYear || 'AY'})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Semester</label>
            <select
              value={selectedSemester}
              onChange={(e) => {
                setSelectedSemester(e.target.value);
                setValidationReport(null);
              }}
              className="form-select"
            >
              {semesters.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Section</label>
            <select
              value={selectedSection}
              onChange={(e) => {
                setSelectedSection(e.target.value);
                setValidationReport(null);
              }}
              className="form-select"
            >
              {sections.map((sec) => (
                <option key={sec.id} value={sec.id}>
                  Section {sec.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Data Assessment Type</label>
            <select
              value={dataType}
              onChange={(e) => {
                setDataType(e.target.value);
                setValidationReport(null);
              }}
              className="form-select"
            >
              <option value="ATTENDANCE">Attendance (Subject-Wise %)</option>
              <option value="MID_1">Mid-1 Result</option>
              <option value="MID_2">Mid-2 Result</option>
              <option value="SEMESTER_RESULT">Semester Result (Grades & SGPA)</option>
            </select>
          </div>
        </div>
      </div>

      {/* STEP 2: File Upload & Validation Action */}
      <div className="card upload-file-card">
        <div className="card-section-title">
          <span className="step-number">Step 2</span>
          <h3>Upload Spreadsheet</h3>
        </div>

        <div
          className={`dropzone ${file ? 'has-file' : ''}`}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="academic-file-input"
            accept=".xlsx,.xls,.csv"
            onChange={handleFileChange}
            className="file-hidden-input"
          />
          <label htmlFor="academic-file-input" className="dropzone-label">
            <div className="dropzone-icon">
              <UploadCloud size={36} />
            </div>
            {file ? (
              <div className="dropzone-selected-info">
                <FileSpreadsheet size={20} className="text-primary" />
                <span className="file-name">{file.name}</span>
                <span className="file-size text-muted">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
              </div>
            ) : (
              <div>
                <p className="dropzone-prompt">
                  <strong>Click to browse</strong> or drag & drop department spreadsheet
                </p>
                <p className="dropzone-hint text-muted">
                  Supports college matrix format or standard column sheets (.xlsx, .csv)
                </p>
              </div>
            )}
          </label>
        </div>

        <div className="upload-action-row">
          <button
            onClick={handleValidate}
            disabled={!file || isValidating}
            className="btn btn-primary"
          >
            {isValidating ? (
              <>
                <RefreshCw size={16} className="spin" />
                <span>Validating Schema & Rows...</span>
              </>
            ) : (
              <>
                <span>Validate File</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>
      </div>

      {/* STEP 3: Validation Report & Preview */}
      {validationReport && (
        <div className="card validation-results-card">
          <div className="results-header">
            <div>
              <h3 className="results-title">File Validation Report</h3>
              <p className="text-muted text-sm">
                Target: {file?.name} • {dataType}
              </p>
            </div>
            <div className="validation-stats-row">
              <div className="stat-pill total">
                <span className="stat-label">Total Rows</span>
                <span className="stat-val">{validationReport.summary.totalRows}</span>
              </div>
              <div className="stat-pill valid">
                <span className="stat-label">Valid Rows</span>
                <span className="stat-val">{validationReport.summary.validRows}</span>
              </div>
              {validationReport.summary.invalidRows > 0 && (
                <div className="stat-pill invalid">
                  <span className="stat-label">Invalid Rows</span>
                  <span className="stat-val">{validationReport.summary.invalidRows}</span>
                </div>
              )}
              {validationReport.summary.duplicatesCount > 0 && (
                <div className="stat-pill warning">
                  <span className="stat-label">Duplicates Found</span>
                  <span className="stat-val">{validationReport.summary.duplicatesCount}</span>
                </div>
              )}
            </div>
          </div>

          {/* Error Diagnostics Section */}
          {validationReport.errors && validationReport.errors.length > 0 && (
            <div className="error-report-box">
              <div className="error-box-header">
                <div className="error-title-wrap">
                  <XCircle size={18} className="text-danger" />
                  <span>
                    {validationReport.summary.totalErrors} Validation Issues Detected
                  </span>
                </div>
                <button
                  onClick={() => setShowErrors(!showErrors)}
                  className="btn btn-secondary btn-xs"
                >
                  {showErrors ? 'Hide Issues' : 'View Error Details'}
                </button>
              </div>

              {showErrors && (
                <ul className="error-list">
                  {validationReport.errors.map((err, i) => (
                    <li key={i} className="error-item">
                      {err}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Warnings Section */}
          {validationReport.warnings && validationReport.warnings.length > 0 && (
            <div className="warning-report-box">
              <AlertTriangle size={16} className="text-warning" />
              <span>
                {validationReport.summary.duplicatesCount} existing records match these keys. Choose duplicate resolution below before confirming.
              </span>
            </div>
          )}

          {/* Extracted Subjects Section */}
          {validationReport.extractedSubjects && validationReport.extractedSubjects.length > 0 && (
            <div className="extracted-subjects-card" style={{
              background: 'rgba(34, 197, 94, 0.08)',
              border: '1px solid rgba(34, 197, 94, 0.3)',
              borderRadius: '8px',
              padding: '1rem',
              marginBottom: '1rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', flexWrap: 'wrap' }}>
                <CheckCircle2 size={18} className="text-success" />
                <span style={{ fontWeight: 600, color: '#4ade80' }}>
                  Auto-Extracted Subjects ({validationReport.extractedSubjects.length})
                </span>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  — Discovered from column headers. Will be registered into semester curriculum upon import.
                </span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {validationReport.extractedSubjects.map((sub, idx) => (
                  <div key={idx} style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid rgba(51, 65, 85, 0.8)',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '0.82rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <strong style={{ color: '#38bdf8' }}>{sub.code}</strong>
                    <span style={{ color: '#cbd5e1' }}>{sub.name}</span>
                    <span style={{ fontSize: '0.72rem', background: 'rgba(99, 102, 241, 0.2)', color: '#a5b4fc', padding: '1px 5px', borderRadius: '4px' }}>
                      {sub.credits} Cr • {sub.type}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Data Preview Table */}
          {previewRows.length > 0 && (
            <div className="preview-table-container">
              <div className="preview-table-title-row">
                <h4>Verified Data Preview ({validationReport.summary.validRows} Records Ready)</h4>
                <span className="text-muted text-xs">
                  Showing page {previewPage} of {totalPreviewPages}
                </span>
              </div>

              <div className="table-responsive">
                <table className="preview-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Roll Number</th>
                      <th>Student Name</th>
                      <th>Subject</th>
                      {dataType === 'ATTENDANCE' && <th>Attendance %</th>}
                      {dataType === 'ATTENDANCE' && <th>Classes (Attended / Total)</th>}
                      {(dataType === 'MID_1' || dataType === 'MID_2') && <th>Marks</th>}
                      {(dataType === 'MID_1' || dataType === 'MID_2') && <th>Status</th>}
                      {dataType === 'SEMESTER_RESULT' && <th>Grade</th>}
                      {dataType === 'SEMESTER_RESULT' && <th>Grade Point</th>}
                      {dataType === 'SEMESTER_RESULT' && <th>Result Status</th>}
                      <th>Duplicate Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentPreviewRows.map((r, idx) => (
                      <tr key={idx}>
                        <td>{(previewPage - 1) * previewPageSize + idx + 1}</td>
                        <td className="font-mono text-primary">{r.roll_number}</td>
                        <td>{r.student_name}</td>
                        <td>
                          <span className="badge badge-outline">{r.subject_code}</span>
                        </td>
                        {dataType === 'ATTENDANCE' && (
                          <td className="font-semibold">{r.percentage}%</td>
                        )}
                        {dataType === 'ATTENDANCE' && (
                          <td className="text-muted">
                            {r.classes_attended ?? '—'} / {r.total_classes ?? '—'}
                          </td>
                        )}
                        {(dataType === 'MID_1' || dataType === 'MID_2') && (
                          <td>{r.marks_obtained ?? '—'} / {r.max_marks ?? 30}</td>
                        )}
                        {(dataType === 'MID_1' || dataType === 'MID_2') && (
                          <td>
                            <span className={`badge ${r.status === 'AVAILABLE' ? 'badge-success' : 'badge-warning'}`}>
                              {r.status}
                            </span>
                          </td>
                        )}
                        {dataType === 'SEMESTER_RESULT' && (
                          <td><span className="badge badge-success">{r.grade ?? '—'}</span></td>
                        )}
                        {dataType === 'SEMESTER_RESULT' && (
                          <td>{r.grade_point ?? '—'}</td>
                        )}
                        {dataType === 'SEMESTER_RESULT' && (
                          <td>
                            <span className={`badge ${r.result_status === 'PASSED' ? 'badge-success' : 'badge-danger'}`}>
                              {r.result_status}
                            </span>
                          </td>
                        )}
                        <td>
                          {r.is_duplicate ? (
                            <span className="badge badge-warning">Existing (Duplicate)</span>
                          ) : (
                            <span className="badge badge-success">New Record</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {totalPreviewPages > 1 && (
                <div className="preview-pagination">
                  <button
                    disabled={previewPage === 1}
                    onClick={() => setPreviewPage((p) => Math.max(1, p - 1))}
                    className="btn btn-secondary btn-xs"
                  >
                    <ChevronLeft size={14} /> Previous
                  </button>
                  <span className="page-indicator">
                    {previewPage} / {totalPreviewPages}
                  </span>
                  <button
                    disabled={previewPage === totalPreviewPages}
                    onClick={() => setPreviewPage((p) => Math.min(totalPreviewPages, p + 1))}
                    className="btn btn-secondary btn-xs"
                  >
                    Next <ChevronRight size={14} />
                  </button>
                </div>
              )}
            </div>
          )}

          {/* STEP 4: Conflict Resolution & Confirm Action */}
          <div className="confirmation-card-footer">
            {validationReport.summary.duplicatesCount > 0 && (
              <div className="strategy-selection-box">
                <label className="strategy-label">Duplicate Conflict Strategy:</label>
                <div className="strategy-options">
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="dupStrategy"
                      value="SKIP"
                      checked={duplicateStrategy === 'SKIP'}
                      onChange={() => setDuplicateStrategy('SKIP')}
                    />
                    <span>Skip duplicates (import new records only)</span>
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="dupStrategy"
                      value="REPLACE"
                      checked={duplicateStrategy === 'REPLACE'}
                      onChange={() => setDuplicateStrategy('REPLACE')}
                    />
                    <span>Replace existing records (update database)</span>
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="dupStrategy"
                      value="CANCEL"
                      checked={duplicateStrategy === 'CANCEL'}
                      onChange={() => setDuplicateStrategy('CANCEL')}
                    />
                    <span>Cancel import if duplicates exist</span>
                  </label>
                </div>
              </div>
            )}

            <div className="confirm-buttons-row">
              <button
                onClick={() => setValidationReport(null)}
                className="btn btn-secondary"
                disabled={isConfirming}
              >
                Cancel
              </button>

              <button
                onClick={handleConfirm}
                disabled={validationReport.summary.validRows === 0 || isConfirming}
                className="btn btn-primary"
              >
                {isConfirming ? (
                  <>
                    <RefreshCw size={16} className="spin" />
                    <span>Committing Transaction...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={16} />
                    <span>Confirm & Import ({validationReport.summary.validRows} Records)</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
