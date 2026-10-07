import React, { useState } from 'react';
import { Shield, Lock, Mail, AlertTriangle, X, Check, Loader2, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function LoginModal({ isOpen, onClose, onSuccess }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMessage('Please enter both email and password.');
      return;
    }

    setLoading(true);
    setErrorMessage('');

    try {
      await login(email, password);
      onClose();
      if (onSuccess) onSuccess();
    } catch (err) {
      setErrorMessage(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (userEmail, userPass) => {
    setEmail(userEmail);
    setPassword(userPass);
    setErrorMessage('');
  };

  return (
    <div className="login-modal-backdrop" onClick={onClose}>
      <div className="login-modal-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="login-modal-header">
          <div className="header-left">
            <div className="login-shield-wrap">
              <Shield size={20} />
            </div>
            <div>
              <h3 className="login-title">HOD Academic Portal</h3>
              <span className="login-subtitle">Restricted Access • Department Intelligence System</span>
            </div>
          </div>
          <button onClick={onClose} className="login-close-btn" aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        {/* Notice */}
        <div className="login-security-notice">
          <span>Official Institutional Portal. Unauthorized access is monitored and logged.</span>
        </div>

        {/* Error alert */}
        {errorMessage && (
          <div className="login-error-alert" role="alert">
            <AlertTriangle size={16} className="error-icon" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">
              Institutional Email
            </label>
            <div className="input-icon-wrap">
              <Mail size={16} className="input-icon" />
              <input
                id="login-email"
                type="email"
                className="modal-input"
                placeholder="hod.cse@college.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="login-password">
              Password
            </label>
            <div className="input-icon-wrap">
              <Lock size={16} className="input-icon" />
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                className="modal-input"
                style={{ paddingRight: '40px' }}
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="password-toggle-btn"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary login-submit-btn"
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 size={16} className="spinner" />
                <span>Authenticating...</span>
              </>
            ) : (
              <>
                <Lock size={16} />
                <span>Sign In to Dashboard</span>
              </>
            )}
          </button>
        </form>

        {/* Quick Fill Demo Credentials */}
        <div className="demo-fill-block">
          <span className="demo-label">Quick Testing Credentials:</span>
          <div className="demo-buttons-row">
            <button
              type="button"
              className="demo-pill"
              onClick={() => fillCredentials('hod@department.edu', 'Admin@123')}
            >
              <Check size={12} />
              <span>HOD (Dr. M. A. Jabbar)</span>
            </button>
            <button
              type="button"
              className="demo-pill"
              onClick={() => fillCredentials('admin@department.edu', 'Admin@123')}
            >
              <Check size={12} />
              <span>Administrator</span>
            </button>
          </div>
        </div>
      </div>

      <style>{`
        .login-modal-backdrop {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.82);
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 250;
          padding: var(--space-md);
        }
        .login-modal-panel {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          max-width: 440px;
          width: 100%;
          padding: var(--space-xl);
          box-shadow: var(--shadow-elevated);
          position: relative;
        }
        .login-modal-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          margin-bottom: var(--space-md);
        }
        .header-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .login-shield-wrap {
          width: 40px;
          height: 40px;
          border-radius: var(--radius-md);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--color-primary);
          flex-shrink: 0;
        }
        .login-title {
          font-size: 1.125rem;
          font-weight: 700;
          color: var(--color-text-main);
        }
        .login-subtitle {
          display: block;
          font-size: 0.75rem;
          color: var(--color-text-muted);
        }
        .login-close-btn {
          color: var(--color-text-muted);
          padding: 4px;
        }
        .login-close-btn:hover {
          color: var(--color-text-main);
        }
        .login-security-notice {
          padding: 8px 12px;
          background: var(--color-secondary);
          border: 1px solid var(--color-border-subtle);
          border-radius: var(--radius-sm);
          font-size: 0.75rem;
          color: var(--color-text-muted);
          margin-bottom: var(--space-md);
        }
        .login-error-alert {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 14px;
          background: var(--color-destructive-subtle);
          border: 1px solid var(--color-destructive-border);
          border-radius: var(--radius-sm);
          font-size: 0.8125rem;
          color: var(--color-destructive);
          margin-bottom: var(--space-md);
        }
        .error-icon {
          flex-shrink: 0;
        }
        .login-form {
          display: flex;
          flex-direction: column;
          gap: var(--space-md);
        }
        .form-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .form-label {
          font-size: 0.8125rem;
          font-weight: 600;
          color: var(--color-text-secondary);
        }
        .input-icon-wrap {
          position: relative;
          display: flex;
          align-items: center;
        }
        .input-icon {
          position: absolute;
          left: 12px;
          color: var(--color-text-muted);
        }
        .modal-input {
          width: 100%;
          padding-left: 38px;
        }
        .password-toggle-btn {
          position: absolute;
          right: 12px;
          color: var(--color-text-muted);
          background: transparent;
          border: none;
          padding: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: color var(--transition-fast);
        }
        .password-toggle-btn:hover {
          color: var(--color-text-main);
        }
        .login-submit-btn {
          width: 100%;
          margin-top: 6px;
          padding: 12px;
        }
        .spinner {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .demo-fill-block {
          margin-top: var(--space-lg);
          padding-top: var(--space-md);
          border-top: 1px solid var(--color-border);
        }
        .demo-label {
          display: block;
          font-size: 0.6875rem;
          color: var(--color-text-muted);
          text-transform: uppercase;
          letter-spacing: 0.04em;
          margin-bottom: 8px;
        }
        .demo-buttons-row {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        .demo-pill {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          font-size: 0.75rem;
          color: var(--color-text-secondary);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          padding: 4px 10px;
          border-radius: var(--radius-sm);
          transition: all var(--transition-fast);
        }
        .demo-pill:hover {
          color: var(--color-primary);
          border-color: var(--color-primary-border);
        }
      `}</style>
    </div>
  );
}
