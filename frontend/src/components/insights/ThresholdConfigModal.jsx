import React, { useState, useEffect } from 'react';
import { X, Sliders, CheckCircle2, RotateCcw, AlertCircle } from 'lucide-react';
import { api } from '../../services/api';

export default function ThresholdConfigModal({ onClose }) {
  const [thresholds, setThresholds] = useState({});
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.getInsightsConfig()
      .then((res) => {
        setThresholds(res.thresholds || {});
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleSave = (e) => {
    e.preventDefault();
    api.updateInsightsConfig(thresholds)
      .then((res) => {
        setThresholds(res.thresholds);
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      })
      .catch(console.error);
  };

  return (
    <div className="diagnostic-drawer-overlay" onClick={onClose}>
      <div className="diagnostic-drawer" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div className="flex items-center gap-2">
            <Sliders size={18} className="text-primary" />
            <h3 className="font-bold text-white text-base">Diagnostic Threshold Rules</h3>
          </div>
          <button onClick={onClose} className="close-btn">
            <X size={18} />
          </button>
        </div>

        <div className="drawer-body">
          <p className="text-xs text-muted">
            All problem detection rules are centralized and deterministic. Adjusting these thresholds updates detection boundaries across all departmental analytics.
          </p>

          {saved && (
            <div className="alert-banner alert-success flex items-center gap-2 text-xs">
              <CheckCircle2 size={16} />
              <span>Threshold parameters updated successfully.</span>
            </div>
          )}

          {loading ? (
            <p className="text-muted text-xs">Loading active threshold settings...</p>
          ) : (
            <form onSubmit={handleSave} className="flex flex-col gap-3">
              <div className="thresholds-grid">
                {Object.entries(thresholds).map(([key, val]) => (
                  <div key={key} className="threshold-card">
                    <div>
                      <span className="threshold-label block">{key.replace(/_/g, ' ')}</span>
                      <span className="text-xs text-muted font-mono">{typeof val === 'number' ? (key.includes('tolerance') ? 'Delta' : key.includes('threshold') && !key.includes('sgpa') ? '%' : 'Score') : ''}</span>
                    </div>
                    <input
                      type="number"
                      step={key.includes('tolerance') || key.includes('sgpa') ? '0.01' : '1'}
                      value={val}
                      onChange={(e) => setThresholds({ ...thresholds, [key]: parseFloat(e.target.value) || 0 })}
                      className="form-input text-right font-mono text-primary font-bold w-24 p-1.5 rounded bg-neutral-900 border border-neutral-700"
                    />
                  </div>
                ))}
              </div>

              <div className="flex justify-end gap-2 mt-4 pt-4 border-t border-neutral-800">
                <button type="button" onClick={onClose} className="btn btn-secondary btn-sm">
                  Close
                </button>
                <button type="submit" className="btn btn-primary btn-sm">
                  Save Changes
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
