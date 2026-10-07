import React, { useState, useEffect } from 'react';
import { History, CheckCircle2, XCircle, AlertCircle, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '../../services/api';

export default function UploadHistoryView() {
  const [historyList, setHistoryList] = useState([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const limit = 15;

  const loadHistory = () => {
    setLoading(true);
    api.getUploadHistory(page, limit).then((res) => {
      setHistoryList(res.data || []);
      setTotalRecords(res.total || 0);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => {
    loadHistory();
  }, [page]);

  const totalPages = Math.ceil(totalRecords / limit) || 1;

  const formatDate = (isoStr) => {
    if (!isoStr) return '—';
    try {
      const d = new Date(isoStr);
      return d.toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoStr;
    }
  };

  const renderStatus = (status) => {
    switch (status) {
      case 'IMPORTED':
        return (
          <span className="badge badge-success">
            <CheckCircle2 size={12} />
            <span>IMPORTED</span>
          </span>
        );
      case 'FAILED':
        return (
          <span className="badge badge-danger">
            <XCircle size={12} />
            <span>FAILED</span>
          </span>
        );
      case 'VALIDATED':
        return (
          <span className="badge badge-info">
            <AlertCircle size={12} />
            <span>VALIDATED</span>
          </span>
        );
      default:
        return <span className="badge badge-outline">{status}</span>;
    }
  };

  return (
    <div className="upload-history-container">
      {/* Header */}
      <div className="view-header-flex">
        <div>
          <h1 className="admin-page-title">Dataset Upload & Ingestion Audit Log</h1>
          <p className="admin-page-subtitle">
            Immutable audit record of all official departmental academic data imports, file validations, and transaction commitments.
          </p>
        </div>
        <button onClick={loadHistory} className="btn btn-secondary btn-sm" disabled={loading}>
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="card table-card">
        <div className="table-header-info">
          <span className="count-label">
            Logged Ingestion Events ({totalRecords})
          </span>
        </div>

        <div className="table-responsive">
          <table className="history-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>File Name</th>
                <th>Target Context</th>
                <th>Data Type</th>
                <th>Rows Summary</th>
                <th>Duplicates</th>
                <th>Imported By</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-6">
                    <RefreshCw size={20} className="spin text-primary inline" />
                    <span className="ml-2">Loading upload audit records...</span>
                  </td>
                </tr>
              ) : historyList.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center empty-cell">
                    No upload history recorded yet. Uploaded spreadsheets will appear here once confirmed.
                  </td>
                </tr>
              ) : (
                historyList.map((item) => (
                  <tr key={item.id}>
                    <td className="text-muted text-sm whitespace-nowrap">
                      {formatDate(item.uploadedAt)}
                    </td>
                    <td className="font-mono text-white">{item.filename}</td>
                    <td>
                      <span className="context-pill">
                        {item.batchName || 'Batch'} • {item.semesterName || 'Sem'} • Sec {item.sectionName || 'A'}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-outline">{item.dataType}</span>
                    </td>
                    <td>
                      <div className="row-counts">
                        <span className="text-success">{item.validRows} valid</span>
                        {item.invalidRows > 0 && (
                          <span className="text-danger ml-2">({item.invalidRows} inv)</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="text-muted">{item.duplicatesCount}</span>
                    </td>
                    <td className="text-muted text-sm">{item.uploadedBy}</td>
                    <td>{renderStatus(item.status)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="table-pagination-row">
            <span className="text-muted text-sm">
              Showing {(page - 1) * limit + 1} to {Math.min(page * limit, totalRecords)} of {totalRecords}
            </span>
            <div className="pagination-btn-group">
              <button
                disabled={page === 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="btn btn-secondary btn-xs"
              >
                <ChevronLeft size={14} /> Previous
              </button>
              <span className="page-current">Page {page} of {totalPages}</span>
              <button
                disabled={page === totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="btn btn-secondary btn-xs"
              >
                Next <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
