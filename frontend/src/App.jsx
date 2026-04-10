import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import {
  Brain, Upload, Activity, FileImage, AlertCircle, CheckCircle2,
  Loader2, MapPin, Percent, Calendar, TrendingUp, Shield, User,
  LogOut, Lock, Eye, EyeOff, LayoutDashboard, Users, FileText,
  BarChart2, ChevronRight, Cpu
} from 'lucide-react';

const API_URL = 'https://medical-image-segmentation-for-brain-hq5b.onrender.com';

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg-base: #07090f;
    --bg-surface: #0c1018;
    --bg-elevated: #111827;
    --bg-hover: #161d2b;
    --border: rgba(99,179,237,0.09);
    --border-strong: rgba(99,179,237,0.18);
    --accent: #2563eb;
    --accent-light: #3b82f6;
    --accent-glow: rgba(37,99,235,0.15);
    --text-primary: #e2e8f0;
    --text-secondary: #64748b;
    --text-muted: #334155;
    --green: #22c55e;
    --yellow: #f59e0b;
    --red: #ef4444;
    --font: 'DM Sans', sans-serif;
    --mono: 'DM Mono', monospace;
  }

  body { font-family: var(--font); background: var(--bg-base); color: var(--text-primary); min-height: 100vh; }

  .app { display: flex; flex-direction: column; min-height: 100vh; }

  /* ── Topbar ── */
  .topbar {
    position: sticky; top: 0; z-index: 50;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 24px; height: 52px;
    background: rgba(7,9,15,0.92);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
  }
  .logo { display: flex; align-items: center; gap: 10px; text-decoration: none; }
  .logo-mark {
    width: 30px; height: 30px; border-radius: 7px;
    background: var(--accent);
    display: flex; align-items: center; justify-content: center;
  }
  .logo-name { font-size: 14px; font-weight: 500; color: var(--text-primary); letter-spacing: 0.02em; }
  .logo-tag { font-size: 10px; color: var(--text-muted); font-family: var(--mono); margin-top: 1px; }

  .topbar-center {
    display: flex; align-items: center; gap: 4px;
  }
  .topbar-nav {
    font-size: 12px; padding: 5px 12px; border-radius: 6px;
    color: var(--text-secondary); cursor: pointer; transition: all 0.15s;
    background: transparent; border: none;
  }
  .topbar-nav:hover { color: var(--text-primary); background: var(--bg-hover); }
  .topbar-nav.active { color: var(--accent-light); background: var(--accent-glow); }

  .topbar-right { display: flex; align-items: center; gap: 8px; }
  .status-pill {
    display: flex; align-items: center; gap: 6px;
    font-size: 11px; font-family: var(--mono); color: var(--text-muted);
    padding: 4px 10px; border-radius: 999px;
    border: 1px solid var(--border);
  }
  .status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); }
  .user-btn {
    display: flex; align-items: center; gap: 7px;
    font-size: 12px; color: var(--text-secondary); padding: 5px 12px;
    border-radius: 6px; cursor: pointer; border: 1px solid var(--border);
    background: var(--bg-surface); transition: all 0.15s;
  }
  .user-btn:hover { border-color: var(--border-strong); color: var(--text-primary); }
  .logout-btn {
    display: flex; align-items: center; gap: 6px;
    font-size: 12px; color: var(--text-secondary); padding: 5px 10px;
    border-radius: 6px; cursor: pointer; border: 1px solid var(--border);
    background: transparent; transition: all 0.15s;
  }
  .logout-btn:hover { color: var(--red); border-color: rgba(239,68,68,0.3); }

  /* ── Layout ── */
  .layout { display: flex; flex: 1; }

  /* ── Sidebar ── */
  .sidebar {
    width: 200px; flex-shrink: 0;
    background: var(--bg-surface);
    border-right: 1px solid var(--border);
    padding: 20px 12px;
    display: flex; flex-direction: column; gap: 6px;
  }
  .sidebar-label {
    font-size: 9px; font-family: var(--mono); color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.1em;
    padding: 0 8px; margin: 10px 0 4px;
  }
  .sidebar-label:first-child { margin-top: 0; }
  .nav-item {
    display: flex; align-items: center; gap: 9px;
    padding: 7px 8px; border-radius: 6px; cursor: pointer;
    font-size: 12px; color: var(--text-secondary);
    transition: all 0.12s; border: 1px solid transparent;
  }
  .nav-item:hover { background: var(--bg-hover); color: var(--text-primary); }
  .nav-item.active {
    background: var(--accent-glow); color: var(--accent-light);
    border-color: rgba(37,99,235,0.2);
  }

  /* ── Content ── */
  .content { flex: 1; padding: 28px; overflow-y: auto; min-width: 0; }

  .page-header { margin-bottom: 24px; }
  .page-title { font-size: 17px; font-weight: 500; color: var(--text-primary); }
  .page-sub { font-size: 12px; color: var(--text-muted); font-family: var(--mono); margin-top: 4px; }

  /* ── Stats row ── */
  .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
  .stat-card {
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 16px;
  }
  .stat-label { font-size: 10px; font-family: var(--mono); color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px; }
  .stat-value { font-size: 24px; font-weight: 300; color: var(--text-primary); letter-spacing: -0.02em; }
  .stat-sub { font-size: 11px; color: var(--text-muted); margin-top: 4px; }
  .stat-sub.green { color: var(--green); }
  .stat-sub.yellow { color: var(--yellow); }

  /* ── Two-col ── */
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }

  /* ── Panel ── */
  .panel { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
  .panel-header {
    padding: 12px 16px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
  }
  .panel-title { font-size: 12px; font-weight: 500; color: var(--text-secondary); display: flex; align-items: center; gap: 7px; }
  .panel-badge {
    font-size: 10px; font-family: var(--mono); padding: 2px 8px; border-radius: 999px;
    background: var(--accent-glow); color: var(--accent-light);
    border: 1px solid rgba(37,99,235,0.25);
  }
  .panel-body { padding: 16px; }

  /* ── Upload zone ── */
  .upload-zone {
    border: 1px dashed var(--border-strong); border-radius: 8px;
    padding: 28px 16px; text-align: center; cursor: pointer; transition: all 0.2s;
  }
  .upload-zone:hover, .upload-zone.active {
    border-color: var(--accent-light);
    background: var(--accent-glow);
  }
  .upload-title { font-size: 13px; color: var(--text-secondary); margin-bottom: 3px; }
  .upload-sub { font-size: 11px; font-family: var(--mono); color: var(--text-muted); }

  /* ── Forms ── */
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 12px; }
  .form-group { display: flex; flex-direction: column; gap: 5px; }
  .form-label { font-size: 11px; font-family: var(--mono); color: var(--text-muted); }
  .form-input {
    background: var(--bg-base); border: 1px solid var(--border);
    border-radius: 6px; padding: 7px 10px; font-size: 12px;
    color: var(--text-primary); font-family: var(--font); outline: none; transition: border 0.15s;
  }
  .form-input:focus { border-color: var(--accent-light); }
  .form-input::placeholder { color: var(--text-muted); }

  /* ── Buttons ── */
  .btn-primary {
    width: 100%; padding: 9px; border-radius: 7px; border: none;
    background: var(--accent); color: #fff; font-size: 13px; font-weight: 500;
    cursor: pointer; margin-top: 10px; font-family: var(--font);
    transition: background 0.15s; display: flex; align-items: center; justify-content: center; gap: 7px;
  }
  .btn-primary:hover { background: var(--accent-light); }
  .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-ghost {
    padding: 8px 14px; border-radius: 7px;
    border: 1px solid var(--border); background: transparent;
    color: var(--text-secondary); font-size: 12px; font-family: var(--font);
    cursor: pointer; transition: all 0.15s; display: flex; align-items: center; gap: 6px;
  }
  .btn-ghost:hover { border-color: var(--border-strong); color: var(--text-primary); }

  /* ── MRI placeholders ── */
  .mri-frame {
    aspect-ratio: 1; background: var(--bg-base); border-radius: 7px;
    border: 1px solid var(--border); display: flex; align-items: center;
    justify-content: center; position: relative; overflow: hidden;
  }
  .mri-frame img { width: 100%; height: 100%; object-fit: contain; border-radius: 7px; }
  .mri-label {
    position: absolute; bottom: 8px; left: 10px;
    font-size: 9px; font-family: var(--mono); color: var(--text-muted); letter-spacing: 0.08em;
  }
  .mri-tag {
    position: absolute; top: 8px; right: 8px;
    font-size: 9px; font-family: var(--mono); padding: 2px 6px;
    border-radius: 4px; background: rgba(239,68,68,0.15); color: #f87171;
    border: 1px solid rgba(239,68,68,0.25);
  }

  /* ── Result rows ── */
  .result-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 0; border-bottom: 1px solid var(--border);
    font-size: 12px;
  }
  .result-row:last-child { border-bottom: none; }
  .result-key { color: var(--text-muted); font-family: var(--mono); }
  .result-val { color: var(--text-primary); font-weight: 500; }

  /* ── Badges ── */
  .badge { font-size: 10px; font-family: var(--mono); padding: 3px 9px; border-radius: 999px; }
  .badge-green { background: rgba(34,197,94,0.1); color: #4ade80; border: 1px solid rgba(34,197,94,0.2); }
  .badge-yellow { background: rgba(245,158,11,0.1); color: #fcd34d; border: 1px solid rgba(245,158,11,0.25); }
  .badge-red { background: rgba(239,68,68,0.1); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }

  /* ── Table ── */
  .data-table { width: 100%; border-collapse: collapse; }
  .data-table th {
    font-size: 10px; font-family: var(--mono); color: var(--text-muted);
    text-align: left; padding: 0 0 10px; text-transform: uppercase; letter-spacing: 0.07em;
  }
  .data-table td { font-size: 12px; color: var(--text-secondary); padding: 9px 0; border-top: 1px solid var(--border); }
  .data-table td:first-child { color: var(--text-primary); }

  /* ── Auth page ── */
  .auth-page {
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    background: var(--bg-base);
    background-image: radial-gradient(ellipse at 20% 50%, rgba(37,99,235,0.06) 0%, transparent 60%),
                      radial-gradient(ellipse at 80% 20%, rgba(37,99,235,0.04) 0%, transparent 50%);
  }
  .auth-card {
    width: 360px; background: var(--bg-surface);
    border: 1px solid var(--border); border-radius: 14px; overflow: hidden;
  }
  .auth-header { padding: 28px 28px 20px; border-bottom: 1px solid var(--border); }
  .auth-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
  .auth-title { font-size: 16px; font-weight: 500; color: var(--text-primary); }
  .auth-sub { font-size: 12px; color: var(--text-muted); margin-top: 3px; }
  .auth-tabs { display: flex; gap: 4px; }
  .auth-tab {
    flex: 1; padding: 7px; border-radius: 6px; border: none;
    font-size: 12px; font-family: var(--font); cursor: pointer; transition: all 0.15s;
    background: transparent; color: var(--text-muted);
  }
  .auth-tab.active { background: var(--accent-glow); color: var(--accent-light); }
  .auth-body { padding: 24px 28px; }
  .auth-form { display: flex; flex-direction: column; gap: 14px; }
  .auth-input-wrap { position: relative; }
  .auth-input {
    width: 100%; background: var(--bg-base); border: 1px solid var(--border);
    border-radius: 7px; padding: 9px 12px; font-size: 13px;
    color: var(--text-primary); font-family: var(--font); outline: none; transition: border 0.15s;
  }
  .auth-input:focus { border-color: var(--accent-light); }
  .auth-input::placeholder { color: var(--text-muted); }
  .auth-input.with-icon { padding-right: 38px; }
  .eye-btn {
    position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
    background: none; border: none; cursor: pointer; color: var(--text-muted);
    display: flex; align-items: center;
  }
  .eye-btn:hover { color: var(--text-secondary); }
  .auth-error {
    display: flex; align-items: center; gap: 8px; padding: 10px 12px;
    background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);
    border-radius: 7px; font-size: 12px; color: #f87171;
  }
  .auth-info {
    padding: 10px 12px; background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.2); border-radius: 7px;
    font-size: 12px; color: #4ade80;
  }
  .pw-rules { display: flex; flex-direction: column; gap: 4px; }
  .pw-rule { font-size: 11px; font-family: var(--mono); color: var(--text-muted); transition: color 0.15s; }
  .pw-rule.pass { color: var(--green); }
  .forgot-link {
    text-align: center; font-size: 11px; color: var(--text-muted);
    cursor: pointer; margin-top: 4px; background: none; border: none;
    font-family: var(--font); transition: color 0.15s;
  }
  .forgot-link:hover { color: var(--accent-light); }

  /* ── Profile panel ── */
  .profile-overlay {
    position: fixed; inset: 0; z-index: 100;
    background: rgba(7,9,15,0.7); backdrop-filter: blur(4px);
    display: flex; align-items: center; justify-content: center;
  }
  .profile-card {
    width: 400px; background: var(--bg-surface);
    border: 1px solid var(--border); border-radius: 14px; overflow: hidden;
  }
  .profile-header {
    padding: 16px 20px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
  }

  /* ── Results banner ── */
  .success-banner {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; background: rgba(34,197,94,0.07);
    border: 1px solid rgba(34,197,94,0.2); border-radius: 9px;
    margin-bottom: 16px;
  }
  .success-left { display: flex; align-items: center; gap: 9px; font-size: 13px; color: #4ade80; }
  .success-actions { display: flex; gap: 8px; }

  /* ── Error box ── */
  .error-box {
    display: flex; align-items: center; gap: 10px; padding: 12px 14px;
    background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);
    border-radius: 8px; font-size: 13px; color: #f87171; margin-top: 12px;
  }

  /* ── Full result grid ── */
  .result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
  .metrics-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 14px; }
  .metric-card {
    background: var(--bg-elevated); border: 1px solid var(--border);
    border-radius: 8px; padding: 12px 14px;
  }
  .metric-label { font-size: 10px; font-family: var(--mono); color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px; display: flex; align-items: center; gap: 5px; }
  .metric-value { font-size: 22px; font-weight: 300; color: var(--text-primary); letter-spacing: -0.02em; }
  .metric-sub { font-size: 10px; color: var(--text-muted); margin-top: 3px; font-family: var(--mono); }

  .prognosis-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-bottom: 14px; }
  .prog-card {
    background: var(--bg-elevated); border: 1px solid var(--border);
    border-radius: 8px; padding: 12px 14px;
  }
  .prog-label { font-size: 10px; font-family: var(--mono); color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px; }

  .disclaimer {
    padding: 12px 14px; background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.15); border-radius: 8px;
    font-size: 11px; color: rgba(245,158,11,0.7);
  }

  .scan-empty {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 8px; height: 100%;
  }
  .scan-empty-text { font-size: 10px; font-family: var(--mono); color: var(--text-muted); }
`;

function getStoredToken() {
  try { return localStorage.getItem('medseg_token'); } catch { return null; }
}
function setStoredToken(token) {
  try {
    if (!token) localStorage.removeItem('medseg_token');
    else localStorage.setItem('medseg_token', token);
  } catch {}
}

function RiskBadge({ risk }) {
  if (!risk) return null;
  const cls = risk === 'Low' ? 'badge-green' : risk === 'Moderate' ? 'badge-yellow' : 'badge-red';
  return <span className={`badge ${cls}`}>{risk}</span>;
}

export default function App() {
  const [token, setToken] = useState(getStoredToken());
  const [authMode, setAuthMode] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [resetToken, setResetToken] = useState('');
  const [resetNewPassword, setResetNewPassword] = useState('');
  const [resetConfirmPassword, setResetConfirmPassword] = useState('');
  const [showResetNew, setShowResetNew] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [authError, setAuthError] = useState(null);
  const [authLoading, setAuthLoading] = useState(false);
  const [authInfo, setAuthInfo] = useState(null);

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [patientId, setPatientId] = useState('');
  const [patientName, setPatientName] = useState('');

  const [showProfile, setShowProfile] = useState(false);
  const [cpCurrent, setCpCurrent] = useState('');
  const [cpNew, setCpNew] = useState('');
  const [cpConfirm, setCpConfirm] = useState('');
  const [cpShowCurrent, setCpShowCurrent] = useState(false);
  const [cpShowNew, setCpShowNew] = useState(false);
  const [cpShowConfirm, setCpShowConfirm] = useState(false);
  const [cpError, setCpError] = useState(null);
  const [cpInfo, setCpInfo] = useState(null);
  const [cpLoading, setCpLoading] = useState(false);

  const [activeNav, setActiveNav] = useState('dashboard');

  const handleLogout = () => {
    setStoredToken(null); setToken(null);
    setAuthError(null); setUsername(''); setPassword(''); setConfirmPassword('');
    setShowPassword(false); setShowConfirmPassword(false);
    setResetToken(''); setResetNewPassword(''); setResetConfirmPassword('');
    setAuthInfo(null); setShowProfile(false);
    setCpCurrent(''); setCpNew(''); setCpConfirm('');
    setCpError(null); setCpInfo(null);
    resetAnalysis();
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setCpLoading(true); setCpError(null); setCpInfo(null);
    if (cpNew !== cpConfirm) { setCpError('Passwords do not match'); setCpLoading(false); return; }
    const ok = cpNew.length >= 8 && /[a-z]/.test(cpNew) && /[A-Z]/.test(cpNew) && /[0-9]/.test(cpNew) && /[^A-Za-z0-9]/.test(cpNew);
    if (!ok) { setCpError('Password does not meet requirements'); setCpLoading(false); return; }
    const fd = new FormData();
    fd.append('current_password', cpCurrent);
    fd.append('new_password', cpNew);
    fd.append('confirm_password', cpConfirm);
    try {
      await axios.post(`${API_URL}/auth/change-password`, fd, {
        headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${token}` }
      });
      setCpInfo('Password updated successfully');
      setCpCurrent(''); setCpNew(''); setCpConfirm('');
    } catch (err) {
      setCpError(err.response?.data?.detail || 'Failed to change password');
    } finally { setCpLoading(false); }
  };

  const downloadReport = async () => {
    if (!result) return;
    try {
      let html = result.report_html;
      if (!html && result.record_id) {
        const response = await axios.get(`${API_URL}/patients/${result.record_id}/report`, {
          headers: { Authorization: `Bearer ${token}` }, responseType: 'text'
        });
        html = response.data;
      }
      if (!html) { setError('Report not available. Please re-run analysis.'); return; }
      const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `NeuroScan_Report_${result.record_id || 'latest'}.html`;
      document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
    } catch (err) { setError(err.response?.data?.detail || 'Failed to download report'); }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    setAuthLoading(true); setAuthError(null); setAuthInfo(null);
    const trimmedUser = username.trim();
    if (!trimmedUser) { setAuthError('Username is required'); setAuthLoading(false); return; }
    if (authMode === 'register') {
      if (password !== confirmPassword) { setAuthError('Passwords do not match'); setAuthLoading(false); return; }
      const rules = { length: password.length >= 8, lower: /[a-z]/.test(password), upper: /[A-Z]/.test(password), number: /[0-9]/.test(password), symbol: /[^A-Za-z0-9]/.test(password) };
      if (!Object.values(rules).every(Boolean)) { setAuthError('Password does not meet requirements'); setAuthLoading(false); return; }
    }
    const fd = new FormData();
    fd.append('username', trimmedUser); fd.append('password', password);
    if (authMode === 'register') fd.append('confirm_password', confirmPassword);
    try {
      const response = await axios.post(`${API_URL}${authMode === 'register' ? '/auth/register' : '/auth/login'}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      const accessToken = response.data?.access_token;
      if (!accessToken) throw new Error('No token returned');
      setStoredToken(accessToken); setToken(accessToken);
      setPassword(''); setConfirmPassword('');
    } catch (err) { setAuthError(err.response?.data?.detail || 'Login failed'); }
    finally { setAuthLoading(false); }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setAuthLoading(true); setAuthError(null); setAuthInfo(null);
    const trimmedUser = username.trim();
    if (!trimmedUser) { setAuthError('Username is required'); setAuthLoading(false); return; }
    const fd = new FormData(); fd.append('username', trimmedUser);
    try {
      const response = await axios.post(`${API_URL}/auth/forgot-password`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      const tok = response.data?.reset_token;
      if (tok) { setResetToken(tok); setAuthInfo('Reset token generated — paste it below.'); setAuthMode('reset'); }
      else setAuthInfo('Request sent.');
    } catch (err) { setAuthError(err.response?.data?.detail || 'Failed to request reset'); }
    finally { setAuthLoading(false); }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setAuthLoading(true); setAuthError(null); setAuthInfo(null);
    if (!resetToken.trim()) { setAuthError('Reset token is required'); setAuthLoading(false); return; }
    if (resetNewPassword !== resetConfirmPassword) { setAuthError('Passwords do not match'); setAuthLoading(false); return; }
    const rules = { length: resetNewPassword.length >= 8, lower: /[a-z]/.test(resetNewPassword), upper: /[A-Z]/.test(resetNewPassword), number: /[0-9]/.test(resetNewPassword), symbol: /[^A-Za-z0-9]/.test(resetNewPassword) };
    if (!Object.values(rules).every(Boolean)) { setAuthError('Password does not meet requirements'); setAuthLoading(false); return; }
    const fd = new FormData();
    fd.append('reset_token', resetToken.trim()); fd.append('new_password', resetNewPassword); fd.append('confirm_password', resetConfirmPassword);
    try {
      await axios.post(`${API_URL}/auth/reset-password`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      setAuthInfo('Password reset. You can now log in.');
      setResetNewPassword(''); setResetConfirmPassword(''); setAuthMode('login');
    } catch (err) { setAuthError(err.response?.data?.detail || 'Failed to reset password'); }
    finally { setAuthLoading(false); }
  };

  const pwRules = { length: password.length >= 8, lower: /[a-z]/.test(password), upper: /[A-Z]/.test(password), number: /[0-9]/.test(password), symbol: /[^A-Za-z0-9]/.test(password) };
  const resetPwRules = { length: resetNewPassword.length >= 8, lower: /[a-z]/.test(resetNewPassword), upper: /[A-Z]/.test(resetNewPassword), number: /[0-9]/.test(resetNewPassword), symbol: /[^A-Za-z0-9]/.test(resetNewPassword) };

  const onDrop = useCallback((acceptedFiles) => {
    const f = acceptedFiles[0];
    if (f) { setFile(f); setPreview(URL.createObjectURL(f)); setResult(null); setError(null); }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff'] }, multiple: false
  });

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true); setError(null);
    const fd = new FormData();
    fd.append('file', file);
    if (patientId.trim()) fd.append('patient_id', patientId.trim());
    if (patientName.trim()) fd.append('patient_name', patientName.trim());
    try {
      const response = await axios.post(`${API_URL}/upload`, fd, {
        headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${token}` }
      });
      setResult(response.data);
    } catch (err) { setError(err.response?.data?.detail || 'An error occurred during analysis'); }
    finally { setLoading(false); }
  };

  const resetAnalysis = () => { setFile(null); setPreview(null); setResult(null); setError(null); setPatientId(''); setPatientName(''); };

  if (!token) {
    return (
      <>
        <style>{CSS}</style>
        <div className="auth-page">
          <div className="auth-card">
            <div className="auth-header">
              <div className="auth-logo">
                <div className="logo-mark">
                  <Brain size={16} color="#fff" />
                </div>
                <div>
                  <div className="logo-name">NeuroScan AI</div>
                  <div className="logo-tag">brain tumor segmentation</div>
                </div>
              </div>
              {(authMode === 'login' || authMode === 'register') && (
                <div className="auth-tabs">
                  <button className={`auth-tab ${authMode === 'login' ? 'active' : ''}`} onClick={() => { setAuthMode('login'); setAuthError(null); setAuthInfo(null); }}>Login</button>
                  <button className={`auth-tab ${authMode === 'register' ? 'active' : ''}`} onClick={() => { setAuthMode('register'); setAuthError(null); setAuthInfo(null); }}>Register</button>
                </div>
              )}
              {(authMode === 'forgot' || authMode === 'reset') && (
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  {authMode === 'forgot' ? 'Reset password' : 'Set new password'}
                </div>
              )}
            </div>

            <div className="auth-body">
              {(authMode === 'login' || authMode === 'register') && (
                <form className="auth-form" onSubmit={handleAuth}>
                  <div className="form-group">
                    <label className="form-label">Username</label>
                    <input className="auth-input" value={username} onChange={e => setUsername(e.target.value)} placeholder="e.g. radiologist1" autoComplete="username" required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Password</label>
                    <div className="auth-input-wrap">
                      <input className="auth-input with-icon" type={showPassword ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder={authMode === 'register' ? 'Strong password' : 'Your password'} autoComplete={authMode === 'register' ? 'new-password' : 'current-password'} required />
                      <button type="button" className="eye-btn" onClick={() => setShowPassword(v => !v)}>{showPassword ? <EyeOff size={14} /> : <Eye size={14} />}</button>
                    </div>
                  </div>
                  {authMode === 'register' && (
                    <>
                      <div className="form-group">
                        <label className="form-label">Confirm password</label>
                        <div className="auth-input-wrap">
                          <input className="auth-input with-icon" type={showConfirmPassword ? 'text' : 'password'} value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} placeholder="Re-enter password" autoComplete="new-password" required />
                          <button type="button" className="eye-btn" onClick={() => setShowConfirmPassword(v => !v)}>{showConfirmPassword ? <EyeOff size={14} /> : <Eye size={14} />}</button>
                        </div>
                        {confirmPassword.length > 0 && confirmPassword !== password && <div style={{ fontSize: 11, color: 'var(--red)', marginTop: 4 }}>Passwords do not match</div>}
                      </div>
                      <div className="pw-rules">
                        <div className={`pw-rule ${pwRules.length ? 'pass' : ''}`}>✓ at least 8 characters</div>
                        <div className={`pw-rule ${pwRules.lower ? 'pass' : ''}`}>✓ one lowercase (a–z)</div>
                        <div className={`pw-rule ${pwRules.upper ? 'pass' : ''}`}>✓ one uppercase (A–Z)</div>
                        <div className={`pw-rule ${pwRules.number ? 'pass' : ''}`}>✓ one number (0–9)</div>
                        <div className={`pw-rule ${pwRules.symbol ? 'pass' : ''}`}>✓ one symbol (!@#$…)</div>
                      </div>
                    </>
                  )}
                  {authError && <div className="auth-error"><AlertCircle size={13} />{authError}</div>}
                  {authInfo && <div className="auth-info">{authInfo}</div>}
                  <button className="btn-primary" disabled={authLoading}>
                    {authLoading ? <><Loader2 size={14} className="spin" />Please wait…</> : <><Lock size={14} />{authMode === 'register' ? 'Create account' : 'Log in'}</>}
                  </button>
                  {authMode === 'login' && (
                    <button type="button" className="forgot-link" onClick={() => { setAuthMode('forgot'); setAuthError(null); setAuthInfo(null); }}>Forgot password?</button>
                  )}
                </form>
              )}

              {authMode === 'forgot' && (
                <form className="auth-form" onSubmit={handleForgotPassword}>
                  <div className="form-group">
                    <label className="form-label">Username</label>
                    <input className="auth-input" value={username} onChange={e => setUsername(e.target.value)} placeholder="Your username" required />
                  </div>
                  {authError && <div className="auth-error"><AlertCircle size={13} />{authError}</div>}
                  {authInfo && <div className="auth-info">{authInfo}</div>}
                  <button className="btn-primary" disabled={authLoading}>
                    {authLoading ? <><Loader2 size={14} />Please wait…</> : 'Get reset token'}
                  </button>
                  <button type="button" className="forgot-link" onClick={() => setAuthMode('login')}>Back to login</button>
                </form>
              )}

              {authMode === 'reset' && (
                <form className="auth-form" onSubmit={handleResetPassword}>
                  <div className="form-group">
                    <label className="form-label">Reset token</label>
                    <input className="auth-input" value={resetToken} onChange={e => setResetToken(e.target.value)} placeholder="Paste token here" required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">New password</label>
                    <div className="auth-input-wrap">
                      <input className="auth-input with-icon" type={showResetNew ? 'text' : 'password'} value={resetNewPassword} onChange={e => setResetNewPassword(e.target.value)} placeholder="Strong password" required />
                      <button type="button" className="eye-btn" onClick={() => setShowResetNew(v => !v)}>{showResetNew ? <EyeOff size={14} /> : <Eye size={14} />}</button>
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Confirm new password</label>
                    <div className="auth-input-wrap">
                      <input className="auth-input with-icon" type={showResetConfirm ? 'text' : 'password'} value={resetConfirmPassword} onChange={e => setResetConfirmPassword(e.target.value)} placeholder="Re-enter password" required />
                      <button type="button" className="eye-btn" onClick={() => setShowResetConfirm(v => !v)}>{showResetConfirm ? <EyeOff size={14} /> : <Eye size={14} />}</button>
                    </div>
                  </div>
                  <div className="pw-rules">
                    <div className={`pw-rule ${resetPwRules.length ? 'pass' : ''}`}>✓ at least 8 characters</div>
                    <div className={`pw-rule ${resetPwRules.lower ? 'pass' : ''}`}>✓ one lowercase</div>
                    <div className={`pw-rule ${resetPwRules.upper ? 'pass' : ''}`}>✓ one uppercase</div>
                    <div className={`pw-rule ${resetPwRules.number ? 'pass' : ''}`}>✓ one number</div>
                    <div className={`pw-rule ${resetPwRules.symbol ? 'pass' : ''}`}>✓ one symbol</div>
                  </div>
                  {authError && <div className="auth-error"><AlertCircle size={13} />{authError}</div>}
                  {authInfo && <div className="auth-info">{authInfo}</div>}
                  <button className="btn-primary" disabled={authLoading}>
                    {authLoading ? <><Loader2 size={14} />Please wait…</> : 'Reset password'}
                  </button>
                  <button type="button" className="forgot-link" onClick={() => setAuthMode('login')}>Back to login</button>
                </form>
              )}
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <style>{CSS}</style>
      <style>{`.spin { animation: spin 1s linear infinite; } @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>

      {showProfile && (
        <div className="profile-overlay" onClick={() => setShowProfile(false)}>
          <div className="profile-card" onClick={e => e.stopPropagation()}>
            <div className="profile-header">
              <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>Change password</span>
              <button className="btn-ghost" style={{ padding: '4px 10px' }} onClick={() => setShowProfile(false)}>Close</button>
            </div>
            <div style={{ padding: 20 }}>
              <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {['Current password', 'New password', 'Confirm new password'].map((label, i) => {
                  const vals = [cpCurrent, cpNew, cpConfirm];
                  const sets = [setCpCurrent, setCpNew, setCpConfirm];
                  const shows = [cpShowCurrent, cpShowNew, cpShowConfirm];
                  const setShows = [setCpShowCurrent, setCpShowNew, setCpShowConfirm];
                  return (
                    <div key={i} className="form-group">
                      <label className="form-label">{label}</label>
                      <div className="auth-input-wrap">
                        <input className="auth-input with-icon" type={shows[i] ? 'text' : 'password'} value={vals[i]} onChange={e => sets[i](e.target.value)} required />
                        <button type="button" className="eye-btn" onClick={() => setShows[i](v => !v)}>{shows[i] ? <EyeOff size={13} /> : <Eye size={13} />}</button>
                      </div>
                    </div>
                  );
                })}
                {cpInfo && <div className="auth-info">{cpInfo}</div>}
                {cpError && <div className="auth-error"><AlertCircle size={13} />{cpError}</div>}
                <button className="btn-primary" disabled={cpLoading}>
                  {cpLoading ? <><Loader2 size={14} className="spin" />Updating…</> : 'Update password'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      <div className="app">
        <div className="topbar">
          <div className="logo">
            <div className="logo-mark"><Brain size={16} color="#fff" /></div>
            <div>
              <div className="logo-name">NeuroScan AI</div>
              <div className="logo-tag">brain tumor segmentation</div>
            </div>
          </div>
          <div className="topbar-right">
            <div className="status-pill"><div className="status-dot" />system online</div>
            <button className="user-btn" onClick={() => setShowProfile(true)}><User size={13} />Profile</button>
            <button className="logout-btn" onClick={handleLogout}><LogOut size={13} />Logout</button>
          </div>
        </div>

        <div className="layout">
          <div className="sidebar">
            <div className="sidebar-label">Workspace</div>
            <div className={`nav-item ${activeNav === 'dashboard' ? 'active' : ''}`} onClick={() => { setActiveNav('dashboard'); resetAnalysis(); }}>
              <LayoutDashboard size={14} />Dashboard
            </div>
            <div className={`nav-item ${activeNav === 'upload' ? 'active' : ''}`} onClick={() => { setActiveNav('upload'); setResult(null); }}>
              <Upload size={14} />Upload scan
            </div>
            <div className="sidebar-label">Records</div>
            <div className={`nav-item ${activeNav === 'patients' ? 'active' : ''}`} onClick={() => setActiveNav('patients')}>
              <Users size={14} />Patients
            </div>
            <div className={`nav-item ${activeNav === 'reports' ? 'active' : ''}`} onClick={() => setActiveNav('reports')}>
              <FileText size={14} />Reports
            </div>
          </div>

          <div className="content">

            {/* ── DASHBOARD ── */}
            {activeNav === 'dashboard' && !result && (
              <>
                <div className="page-header">
                  <div className="page-title">Dashboard</div>
                  <div className="page-sub">welcome back — NeuroScan AI v1.0</div>
                </div>
                <div className="stats-row">
                  <div className="stat-card">
                    <div className="stat-label">Model</div>
                    <div className="stat-value" style={{ fontSize: 16, marginTop: 4 }}>U-Net</div>
                    <div className="stat-sub">128×128 input</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Architecture</div>
                    <div className="stat-value" style={{ fontSize: 16, marginTop: 4 }}>Dice loss</div>
                    <div className="stat-sub">0.80 val score</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Status</div>
                    <div className="stat-value" style={{ fontSize: 16, marginTop: 4, color: 'var(--green)' }}>Online</div>
                    <div className="stat-sub green">Backend healthy</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Output</div>
                    <div className="stat-value" style={{ fontSize: 16, marginTop: 4 }}>Report</div>
                    <div className="stat-sub">HTML + overlay</div>
                  </div>
                </div>
                <div className="two-col">
                  <div className="panel">
                    <div className="panel-header">
                      <div className="panel-title"><Upload size={13} color="#60a5fa" />Quick upload</div>
                      <span className="panel-badge">U-Net model</span>
                    </div>
                    <div className="panel-body">
                      <div {...getRootProps()} className={`upload-zone ${isDragActive ? 'active' : ''}`}>
                        <input {...getInputProps()} />
                        <FileImage size={28} color="#334155" style={{ margin: '0 auto 10px' }} />
                        <div className="upload-title">{isDragActive ? 'Drop it here' : 'Drop MRI scan or click to browse'}</div>
                        <div className="upload-sub">JPEG · PNG · TIFF · BMP</div>
                      </div>
                      <div className="form-row">
                        <div className="form-group">
                          <label className="form-label">patient_id</label>
                          <input className="form-input" placeholder="P-000123" value={patientId} onChange={e => setPatientId(e.target.value)} />
                        </div>
                        <div className="form-group">
                          <label className="form-label">patient_name</label>
                          <input className="form-input" placeholder="Jane Doe" value={patientName} onChange={e => setPatientName(e.target.value)} />
                        </div>
                      </div>
                      {preview && (
                        <div style={{ marginTop: 12 }}>
                          <div className="mri-frame" style={{ aspectRatio: 'auto', maxHeight: 140 }}>
                            <img src={preview} alt="preview" style={{ maxHeight: 140, objectFit: 'contain' }} />
                            <div className="mri-label">{file?.name}</div>
                          </div>
                        </div>
                      )}
                      <button className="btn-primary" disabled={!file || loading} onClick={handleAnalyze}>
                        {loading ? <><Loader2 size={14} className="spin" />Analyzing…</> : <><Cpu size={14} />Analyze scan</>}
                      </button>
                      {error && <div className="error-box"><AlertCircle size={14} />{error}</div>}
                    </div>
                  </div>

                  <div className="panel">
                    <div className="panel-header">
                      <div className="panel-title"><Activity size={13} color="#60a5fa" />How it works</div>
                    </div>
                    <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                      {[
                        { n: '01', title: 'Upload MRI', desc: 'Drop a brain MRI scan in JPEG, PNG, TIFF or BMP format.' },
                        { n: '02', title: 'Preprocessing', desc: 'CLAHE contrast enhancement, resize to 128×128, normalize.' },
                        { n: '03', title: 'U-Net inference', desc: 'Trained model generates a binary segmentation mask.' },
                        { n: '04', title: 'Report', desc: 'Download a full HTML prognosis report with overlays.' },
                      ].map(s => (
                        <div key={s.n} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                          <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--accent-light)', minWidth: 20, marginTop: 2 }}>{s.n}</div>
                          <div>
                            <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 2 }}>{s.title}</div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{s.desc}</div>
                          </div>
                        </div>
                      ))}
                      <div className="disclaimer" style={{ marginTop: 4 }}>
                        Research use only. Results must be verified by qualified medical professionals.
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* ── UPLOAD PAGE ── */}
            {activeNav === 'upload' && !result && (
              <>
                <div className="page-header">
                  <div className="page-title">Upload scan</div>
                  <div className="page-sub">run segmentation on a new MRI image</div>
                </div>
                <div className="panel" style={{ maxWidth: 600 }}>
                  <div className="panel-header">
                    <div className="panel-title"><Upload size={13} color="#60a5fa" />MRI upload</div>
                    <span className="panel-badge">U-Net</span>
                  </div>
                  <div className="panel-body">
                    <div {...getRootProps()} className={`upload-zone ${isDragActive ? 'active' : ''}`} style={{ padding: 48 }}>
                      <input {...getInputProps()} />
                      <FileImage size={36} color="#334155" style={{ margin: '0 auto 12px' }} />
                      <div className="upload-title" style={{ fontSize: 14 }}>{isDragActive ? 'Drop it here' : 'Drop MRI scan here'}</div>
                      <div className="upload-sub">or click to browse · JPEG · PNG · TIFF · BMP</div>
                    </div>
                    <div className="form-row" style={{ marginTop: 16 }}>
                      <div className="form-group">
                        <label className="form-label">patient_id</label>
                        <input className="form-input" placeholder="e.g. P-000123" value={patientId} onChange={e => setPatientId(e.target.value)} />
                      </div>
                      <div className="form-group">
                        <label className="form-label">patient_name</label>
                        <input className="form-input" placeholder="e.g. Jane Doe" value={patientName} onChange={e => setPatientName(e.target.value)} />
                      </div>
                    </div>
                    {preview && (
                      <div style={{ marginTop: 14 }}>
                        <div style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--text-muted)', marginBottom: 8 }}>preview</div>
                        <div className="mri-frame" style={{ aspectRatio: 'auto', maxHeight: 200 }}>
                          <img src={preview} alt="preview" style={{ maxHeight: 200, objectFit: 'contain' }} />
                          <div className="mri-label">{file?.name}</div>
                        </div>
                      </div>
                    )}
                    <button className="btn-primary" disabled={!file || loading} onClick={handleAnalyze}>
                      {loading ? <><Loader2 size={14} className="spin" />Analyzing…</> : <><Cpu size={14} />Analyze scan</>}
                    </button>
                    {error && <div className="error-box"><AlertCircle size={14} />{error}</div>}
                  </div>
                </div>
              </>
            )}

            {/* ── RESULTS ── */}
            {result && (
              <>
                <div className="page-header">
                  <div className="page-title">Segmentation result</div>
                  <div className="page-sub">record #{result.record_id} — analysis complete</div>
                </div>

                <div className="success-banner">
                  <div className="success-left"><CheckCircle2 size={15} />Analysis completed successfully</div>
                  <div className="success-actions">
                    <button className="btn-ghost" onClick={downloadReport}><FileText size={13} />Download report</button>
                    <button className="btn-ghost" onClick={resetAnalysis}><Upload size={13} />New scan</button>
                  </div>
                </div>

                <div className="metrics-grid">
                  <div className="metric-card">
                    <div className="metric-label"><Percent size={11} />Tumor area</div>
                    <div className="metric-value">{result.tumor_area}%</div>
                    <div className="metric-sub">of scan area</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-label"><Shield size={11} />Confidence</div>
                    <div className="metric-value" style={{ color: 'var(--green)' }}>{result.confidence}%</div>
                    <div className="metric-sub">model certainty</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-label"><MapPin size={11} />Location</div>
                    <div className="metric-value" style={{ fontSize: 13, marginTop: 4 }}>{result.location}</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-label"><TrendingUp size={11} />Volume est.</div>
                    <div className="metric-value" style={{ fontSize: 18 }}>{result.prognosis_data.tumor_volume_estimate}</div>
                  </div>
                </div>

                <div className="result-grid">
                  <div className="panel">
                    <div className="panel-header"><div className="panel-title"><FileImage size={13} />Original MRI</div></div>
                    <div className="panel-body">
                      <div className="mri-frame">
                        <img src={`data:image/png;base64,${result.original_image}`} alt="Original MRI" />
                        <div className="mri-label">ORIGINAL</div>
                      </div>
                    </div>
                  </div>
                  <div className="panel">
                    <div className="panel-header"><div className="panel-title"><Brain size={13} color="#60a5fa" />Segmentation overlay</div></div>
                    <div className="panel-body">
                      <div className="mri-frame">
                        <img src={`data:image/png;base64,${result.segmented_image}`} alt="Segmented" />
                        <div className="mri-label">SEGMENTED</div>
                        <div className="mri-tag">TUMOR</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="prognosis-grid">
                  <div className="prog-card">
                    <div className="prog-label">Growth risk</div>
                    <RiskBadge risk={result.prognosis_data.growth_risk} />
                  </div>
                  <div className="prog-card">
                    <div className="prog-label">Recommended follow-up</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginTop: 2 }}>
                      <Calendar size={13} color="var(--accent-light)" />
                      <span style={{ fontSize: 13, color: 'var(--text-primary)' }}>{result.prognosis_data.recommended_followup}</span>
                    </div>
                  </div>
                  <div className="prog-card">
                    <div className="prog-label">Segmentation quality</div>
                    <span className={`badge ${result.prognosis_data.segmentation_quality === 'High' ? 'badge-green' : 'badge-yellow'}`}>
                      {result.prognosis_data.segmentation_quality}
                    </span>
                  </div>
                </div>

                <div className="disclaimer">
                  Medical disclaimer: This analysis is for research and educational purposes only. Results must be verified by qualified medical professionals before any clinical decisions are made.
                </div>
              </>
            )}

            {/* ── PATIENTS placeholder ── */}
            {activeNav === 'patients' && (
              <>
                <div className="page-header">
                  <div className="page-title">Patients</div>
                  <div className="page-sub">patient records from your analyses</div>
                </div>
                <div className="panel">
                  <div className="panel-header"><div className="panel-title"><Users size={13} />Records</div></div>
                  <div className="panel-body" style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)', fontSize: 13 }}>
                    Upload and analyze scans to populate patient records.
                    <div style={{ marginTop: 12 }}>
                      <button className="btn-ghost" onClick={() => setActiveNav('upload')}><Upload size={13} />Upload scan <ChevronRight size={12} /></button>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* ── REPORTS placeholder ── */}
            {activeNav === 'reports' && (
              <>
                <div className="page-header">
                  <div className="page-title">Reports</div>
                  <div className="page-sub">downloadable HTML prognosis reports</div>
                </div>
                <div className="panel">
                  <div className="panel-header"><div className="panel-title"><FileText size={13} />Reports</div></div>
                  <div className="panel-body" style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)', fontSize: 13 }}>
                    Reports are generated automatically after each analysis.
                    <div style={{ marginTop: 12 }}>
                      <button className="btn-ghost" onClick={() => setActiveNav('upload')}><Upload size={13} />Upload scan <ChevronRight size={12} /></button>
                    </div>
                  </div>
                </div>
              </>
            )}

          </div>
        </div>
      </div>
    </>
  );
}
