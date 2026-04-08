import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { 
  Brain, 
  Upload, 
  Activity, 
  FileImage, 
  AlertCircle, 
  CheckCircle2,
  Loader2,
  MapPin,
  Percent,
  Calendar,
  TrendingUp,
  Shield,
  User,
  LogOut,
  Lock,
  Eye,
  EyeOff
} from 'lucide-react';

const API_URL = 'http://localhost:8000';

function getStoredToken() {
  try {
    return localStorage.getItem('medseg_token');
  } catch {
    return null;
  }
}

function setStoredToken(token) {
  try {
    if (!token) {
      localStorage.removeItem('medseg_token');
    } else {
      localStorage.setItem('medseg_token', token);
    }
  } catch {
    // ignore
  }
}

function App() {
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
  const [showResetNewPassword, setShowResetNewPassword] = useState(false);
  const [showResetConfirmPassword, setShowResetConfirmPassword] = useState(false);
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

  const handleLogout = () => {
    setStoredToken(null);
    setToken(null);
    setAuthError(null);
    setUsername('');
    setPassword('');
    setConfirmPassword('');
    setShowPassword(false);
    setShowConfirmPassword(false);
    setResetToken('');
    setResetNewPassword('');
    setResetConfirmPassword('');
    setShowResetNewPassword(false);
    setShowResetConfirmPassword(false);
    setAuthInfo(null);
    setShowProfile(false);
    setCpCurrent('');
    setCpNew('');
    setCpConfirm('');
    setCpError(null);
    setCpInfo(null);
    resetAnalysis();
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setCpLoading(true);
    setCpError(null);
    setCpInfo(null);

    if (cpNew !== cpConfirm) {
      setCpError('Passwords do not match');
      setCpLoading(false);
      return;
    }

    const rulesOk =
      cpNew.length >= 8 &&
      /[a-z]/.test(cpNew) &&
      /[A-Z]/.test(cpNew) &&
      /[0-9]/.test(cpNew) &&
      /[^A-Za-z0-9]/.test(cpNew);

    if (!rulesOk) {
      setCpError('New password does not meet the requirements');
      setCpLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append('current_password', cpCurrent);
    formData.append('new_password', cpNew);
    formData.append('confirm_password', cpConfirm);

    try {
      await axios.post(`${API_URL}/auth/change-password`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`
        }
      });
      setCpInfo('Password updated successfully');
      setCpCurrent('');
      setCpNew('');
      setCpConfirm('');
      setCpShowCurrent(false);
      setCpShowNew(false);
      setCpShowConfirm(false);
    } catch (err) {
      setCpError(err.response?.data?.detail || 'Failed to change password');
    } finally {
      setCpLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!result) return;

    try {
      let html = result.report_html;

      if (!html && result.record_id) {
        const response = await axios.get(`${API_URL}/patients/${result.record_id}/report`, {
          headers: {
            Authorization: `Bearer ${token}`
          },
          responseType: 'text'
        });
        html = response.data;
      }

      if (!html) {
        setError('Report is not available. Please re-run analysis.');
        return;
      }

      const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `NeuroScan_Report_${result.record_id || 'latest'}.html`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to download report');
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    setAuthInfo(null);

    const trimmedUser = username.trim();
    if (!trimmedUser) {
      setAuthError('Username is required');
      setAuthLoading(false);
      return;
    }

    if (authMode === 'register') {
      if (password !== confirmPassword) {
        setAuthError('Passwords do not match');
        setAuthLoading(false);
        return;
      }

      const rules = {
        length: password.length >= 8,
        lower: /[a-z]/.test(password),
        upper: /[A-Z]/.test(password),
        number: /[0-9]/.test(password),
        symbol: /[^A-Za-z0-9]/.test(password)
      };
      const allPass = Object.values(rules).every(Boolean);
      if (!allPass) {
        setAuthError('Password does not meet the requirements');
        setAuthLoading(false);
        return;
      }
    }

    const formData = new FormData();
    formData.append('username', trimmedUser);
    formData.append('password', password);
    if (authMode === 'register') {
      formData.append('confirm_password', confirmPassword);
    }

    const endpoint = authMode === 'register' ? '/auth/register' : '/auth/login';

    try {
      const response = await axios.post(`${API_URL}${endpoint}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      const accessToken = response.data?.access_token;
      if (!accessToken) {
        throw new Error('No token returned');
      }
      setStoredToken(accessToken);
      setToken(accessToken);
      setPassword('');
      setConfirmPassword('');
    } catch (err) {
      setAuthError(err.response?.data?.detail || 'Login failed');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    setAuthInfo(null);

    const trimmedUser = username.trim();
    if (!trimmedUser) {
      setAuthError('Username is required');
      setAuthLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append('username', trimmedUser);

    try {
      const response = await axios.post(`${API_URL}/auth/forgot-password`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      const tokenFromServer = response.data?.reset_token;
      if (tokenFromServer) {
        setResetToken(tokenFromServer);
        setAuthInfo('Reset token generated. Copy it and set a new password below.');
        setAuthMode('reset');
      } else {
        setAuthInfo('Request sent.');
      }
    } catch (err) {
      setAuthError(err.response?.data?.detail || 'Failed to request reset');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    setAuthInfo(null);

    if (!resetToken.trim()) {
      setAuthError('Reset token is required');
      setAuthLoading(false);
      return;
    }
    if (resetNewPassword !== resetConfirmPassword) {
      setAuthError('Passwords do not match');
      setAuthLoading(false);
      return;
    }

    const rules = {
      length: resetNewPassword.length >= 8,
      lower: /[a-z]/.test(resetNewPassword),
      upper: /[A-Z]/.test(resetNewPassword),
      number: /[0-9]/.test(resetNewPassword),
      symbol: /[^A-Za-z0-9]/.test(resetNewPassword)
    };
    const allPass = Object.values(rules).every(Boolean);
    if (!allPass) {
      setAuthError('Password does not meet the requirements');
      setAuthLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append('reset_token', resetToken.trim());
    formData.append('new_password', resetNewPassword);
    formData.append('confirm_password', resetConfirmPassword);

    try {
      await axios.post(`${API_URL}/auth/reset-password`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setAuthInfo('Password reset successful. You can now login.');
      setResetNewPassword('');
      setResetConfirmPassword('');
      setShowResetNewPassword(false);
      setShowResetConfirmPassword(false);
      setAuthMode('login');
    } catch (err) {
      setAuthError(err.response?.data?.detail || 'Failed to reset password');
    } finally {
      setAuthLoading(false);
    }
  };

  const passwordRules = {
    length: password.length >= 8,
    lower: /[a-z]/.test(password),
    upper: /[A-Z]/.test(password),
    number: /[0-9]/.test(password),
    symbol: /[^A-Za-z0-9]/.test(password)
  };

  const resetPasswordRules = {
    length: resetNewPassword.length >= 8,
    lower: /[a-z]/.test(resetNewPassword),
    upper: /[A-Z]/.test(resetNewPassword),
    number: /[0-9]/.test(resetNewPassword),
    symbol: /[^A-Za-z0-9]/.test(resetNewPassword)
  };

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff']
    },
    multiple: false
  });

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    if (patientId.trim()) formData.append('patient_id', patientId.trim());
    if (patientName.trim()) formData.append('patient_name', patientName.trim());

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`
        }
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during analysis');
    } finally {
      setLoading(false);
    }
  };

  const resetAnalysis = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    setPatientId('');
    setPatientName('');
  };

  return (
    <div className="min-h-screen app-bg text-white">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-medical-600 rounded-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">NeuroScan AI</h1>
              <p className="text-xs text-slate-400">Brain Tumor Segmentation System</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {token ? (
              <>
                <span className="hidden sm:flex items-center gap-2 text-sm text-slate-300">
                  <User className="w-4 h-4" />
                  Logged in
                </span>
                <button
                  onClick={() => setShowProfile((v) => !v)}
                  className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium transition-colors"
                >
                  <User className="w-4 h-4" />
                  Profile
                </button>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </>
            ) : (
              <span className="flex items-center gap-1.5 text-sm text-amber-300">
                <Lock className="w-4 h-4" />
                Login required
              </span>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {token && showProfile && (
          <div className="mb-6 max-w-2xl">
            <div className="bg-slate-800/80 backdrop-blur rounded-xl border border-slate-700 overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">User Profile</h3>
                  <p className="text-xs text-slate-400">Change your password</p>
                </div>
                <button
                  onClick={() => setShowProfile(false)}
                  className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium transition-colors"
                >
                  Close
                </button>
              </div>
              <div className="p-6">
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div>
                    <label className="block text-sm text-slate-300 mb-1">Current Password</label>
                    <div className="relative">
                      <input
                        value={cpCurrent}
                        onChange={(e) => setCpCurrent(e.target.value)}
                        className="w-full px-4 py-3 pr-12 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                        type={cpShowCurrent ? 'text' : 'password'}
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setCpShowCurrent((v) => !v)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                      >
                        {cpShowCurrent ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-slate-300 mb-1">New Password</label>
                    <div className="relative">
                      <input
                        value={cpNew}
                        onChange={(e) => setCpNew(e.target.value)}
                        className="w-full px-4 py-3 pr-12 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                        type={cpShowNew ? 'text' : 'password'}
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setCpShowNew((v) => !v)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                      >
                        {cpShowNew ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-slate-300 mb-1">Confirm New Password</label>
                    <div className="relative">
                      <input
                        value={cpConfirm}
                        onChange={(e) => setCpConfirm(e.target.value)}
                        className="w-full px-4 py-3 pr-12 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                        type={cpShowConfirm ? 'text' : 'password'}
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setCpShowConfirm((v) => !v)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                      >
                        {cpShowConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    {cpConfirm.length > 0 && cpConfirm !== cpNew && (
                      <p className="text-xs text-red-300 mt-1">Passwords do not match</p>
                    )}
                  </div>

                  {cpInfo && (
                    <div className="p-3 bg-emerald-900/20 border border-emerald-700/40 rounded-lg text-sm text-emerald-200">
                      {cpInfo}
                    </div>
                  )}

                  {cpError && (
                    <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                      <p className="text-sm text-red-300">{cpError}</p>
                    </div>
                  )}

                  <button
                    disabled={cpLoading}
                    className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-medical-600 hover:bg-medical-700 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    type="submit"
                  >
                    {cpLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Updating...
                      </>
                    ) : (
                      'Update Password'
                    )}
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}

        {!token && (
          <div className="max-w-md mx-auto">
            <div className="bg-slate-800/80 backdrop-blur rounded-xl border border-slate-700 overflow-hidden">
              <div className="px-6 py-5 border-b border-slate-700">
                <h2 className="text-lg font-semibold text-white">Welcome</h2>
                <p className="text-sm text-slate-400 mt-1">Login or create an account to use the system.</p>
              </div>

              <div className="p-6">
                <div className="grid grid-cols-2 gap-2 mb-5">
                  <button
                    type="button"
                    onClick={() => setAuthMode('login')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${authMode === 'login' ? 'bg-medical-600' : 'bg-slate-700 hover:bg-slate-600'}`}
                  >
                    Login
                  </button>
                  <button
                    type="button"
                    onClick={() => setAuthMode('register')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${authMode === 'register' ? 'bg-medical-600' : 'bg-slate-700 hover:bg-slate-600'}`}
                  >
                    Register
                  </button>
                </div>

                {authMode === 'forgot' && (
                  <form onSubmit={handleForgotPassword} className="space-y-4">
                    <div>
                      <label className="block text-sm text-slate-300 mb-1">Username</label>
                      <input
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                        placeholder="Your username"
                        autoComplete="username"
                        required
                      />
                    </div>

                    {authInfo && (
                      <div className="p-3 bg-emerald-900/20 border border-emerald-700/40 rounded-lg text-sm text-emerald-200">
                        {authInfo}
                      </div>
                    )}

                    {authError && (
                      <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                        <p className="text-sm text-red-300">{authError}</p>
                      </div>
                    )}

                    <button
                      disabled={authLoading}
                      className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-medical-600 hover:bg-medical-700 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      type="submit"
                    >
                      {authLoading ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Please wait...
                        </>
                      ) : (
                        <>
                          <Lock className="w-5 h-5" />
                          Get reset token
                        </>
                      )}
                    </button>

                    <button
                      type="button"
                      onClick={() => setAuthMode('login')}
                      className="w-full px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-colors"
                    >
                      Back to login
                    </button>
                  </form>
                )}

                {authMode === 'reset' && (
                  <form onSubmit={handleResetPassword} className="space-y-4">
                    <div>
                      <label className="block text-sm text-slate-300 mb-1">Reset Token</label>
                      <input
                        value={resetToken}
                        onChange={(e) => setResetToken(e.target.value)}
                        className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                        placeholder="Paste reset token"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-slate-300 mb-1">New Password</label>
                      <div className="relative">
                        <input
                          value={resetNewPassword}
                          onChange={(e) => setResetNewPassword(e.target.value)}
                          className="w-full px-4 py-3 pr-12 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                          type={showResetNewPassword ? 'text' : 'password'}
                          placeholder="Create a strong password"
                          autoComplete="new-password"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setShowResetNewPassword((v) => !v)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                          aria-label={showResetNewPassword ? 'Hide password' : 'Show password'}
                        >
                          {showResetNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm text-slate-300 mb-1">Confirm New Password</label>
                      <div className="relative">
                        <input
                          value={resetConfirmPassword}
                          onChange={(e) => setResetConfirmPassword(e.target.value)}
                          className="w-full px-4 py-3 pr-12 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                          type={showResetConfirmPassword ? 'text' : 'password'}
                          placeholder="Re-enter new password"
                          autoComplete="new-password"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setShowResetConfirmPassword((v) => !v)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                          aria-label={showResetConfirmPassword ? 'Hide password' : 'Show password'}
                        >
                          {showResetConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                      {resetConfirmPassword.length > 0 && resetConfirmPassword !== resetNewPassword && (
                        <p className="text-xs text-red-300 mt-1">Passwords do not match</p>
                      )}
                    </div>

                    <div className="bg-slate-900/60 border border-slate-700 rounded-lg p-3">
                      <p className="text-xs text-slate-300 font-medium mb-2">Password must include:</p>
                      <div className="grid grid-cols-1 gap-1 text-xs">
                        <p className={resetPasswordRules.length ? 'text-emerald-300' : 'text-slate-400'}>At least 8 characters</p>
                        <p className={resetPasswordRules.lower ? 'text-emerald-300' : 'text-slate-400'}>One lowercase letter (a-z)</p>
                        <p className={resetPasswordRules.upper ? 'text-emerald-300' : 'text-slate-400'}>One uppercase letter (A-Z)</p>
                        <p className={resetPasswordRules.number ? 'text-emerald-300' : 'text-slate-400'}>One number (0-9)</p>
                        <p className={resetPasswordRules.symbol ? 'text-emerald-300' : 'text-slate-400'}>One symbol (!@#$...)</p>
                      </div>
                    </div>

                    {authInfo && (
                      <div className="p-3 bg-emerald-900/20 border border-emerald-700/40 rounded-lg text-sm text-emerald-200">
                        {authInfo}
                      </div>
                    )}

                    {authError && (
                      <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                        <p className="text-sm text-red-300">{authError}</p>
                      </div>
                    )}

                    <button
                      disabled={authLoading}
                      className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-medical-600 hover:bg-medical-700 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      type="submit"
                    >
                      {authLoading ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Please wait...
                        </>
                      ) : (
                        <>
                          <Lock className="w-5 h-5" />
                          Reset password
                        </>
                      )}
                    </button>

                    <button
                      type="button"
                      onClick={() => setAuthMode('login')}
                      className="w-full px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-colors"
                    >
                      Back to login
                    </button>
                  </form>
                )}

                {(authMode === 'login' || authMode === 'register') && (
                  <form onSubmit={handleAuth} className="space-y-4">
                  <div>
                    <label className="block text-sm text-slate-300 mb-1">Username</label>
                    <input
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                      placeholder="e.g. radiologist1"
                      autoComplete="username"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-300 mb-1">Password</label>
                    <div className="relative">
                      <input
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-3 pr-12 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                        type={showPassword ? 'text' : 'password'}
                        placeholder={authMode === 'register' ? 'Create a strong password' : 'Enter your password'}
                        autoComplete={authMode === 'register' ? 'new-password' : 'current-password'}
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword((v) => !v)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                        aria-label={showPassword ? 'Hide password' : 'Show password'}
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  {authMode === 'register' && (
                    <>
                      <div>
                        <label className="block text-sm text-slate-300 mb-1">Confirm Password</label>
                        <div className="relative">
                          <input
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className="w-full px-4 py-3 pr-12 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                            type={showConfirmPassword ? 'text' : 'password'}
                            placeholder="Re-enter password"
                            autoComplete="new-password"
                            required
                          />
                          <button
                            type="button"
                            onClick={() => setShowConfirmPassword((v) => !v)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                            aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                          >
                            {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                        {confirmPassword.length > 0 && confirmPassword !== password && (
                          <p className="text-xs text-red-300 mt-1">Passwords do not match</p>
                        )}
                      </div>

                      <div className="bg-slate-900/60 border border-slate-700 rounded-lg p-3">
                        <p className="text-xs text-slate-300 font-medium mb-2">Password must include:</p>
                        <div className="grid grid-cols-1 gap-1 text-xs">
                          <p className={passwordRules.length ? 'text-emerald-300' : 'text-slate-400'}>At least 8 characters</p>
                          <p className={passwordRules.lower ? 'text-emerald-300' : 'text-slate-400'}>One lowercase letter (a-z)</p>
                          <p className={passwordRules.upper ? 'text-emerald-300' : 'text-slate-400'}>One uppercase letter (A-Z)</p>
                          <p className={passwordRules.number ? 'text-emerald-300' : 'text-slate-400'}>One number (0-9)</p>
                          <p className={passwordRules.symbol ? 'text-emerald-300' : 'text-slate-400'}>One symbol (!@#$...)</p>
                        </div>
                      </div>
                    </>
                  )}

                  {authError && (
                    <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                      <p className="text-sm text-red-300">{authError}</p>
                    </div>
                  )}

                  {authInfo && (
                    <div className="p-3 bg-emerald-900/20 border border-emerald-700/40 rounded-lg text-sm text-emerald-200">
                      {authInfo}
                    </div>
                  )}

                  <button
                    disabled={authLoading}
                    className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-medical-600 hover:bg-medical-700 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    type="submit"
                  >
                    {authLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Please wait...
                      </>
                    ) : (
                      <>
                        <Lock className="w-5 h-5" />
                        {authMode === 'register' ? 'Create account' : 'Login'}
                      </>
                    )}
                  </button>

                  {authMode === 'login' && (
                    <button
                      type="button"
                      onClick={() => {
                        setAuthMode('forgot');
                        setAuthError(null);
                        setAuthInfo(null);
                        setResetToken('');
                        setResetNewPassword('');
                        setResetConfirmPassword('');
                      }}
                      className="w-full text-sm text-medical-300 hover:text-medical-200 underline underline-offset-4"
                    >
                      Forgot password?
                    </button>
                  )}
                </form>
                )}
              </div>
            </div>
          </div>
        )}

        {token && (
          <>
            {/* Upload Section */}
            {!result && (
              <div className="mb-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-4">
                    <label className="block text-sm text-slate-300 mb-1">Patient ID</label>
                    <input
                      value={patientId}
                      onChange={(e) => setPatientId(e.target.value)}
                      className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                      placeholder="e.g. P-000123"
                    />
                  </div>
                  <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-4">
                    <label className="block text-sm text-slate-300 mb-1">Patient Name</label>
                    <input
                      value={patientName}
                      onChange={(e) => setPatientName(e.target.value)}
                      className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-medical-500"
                      placeholder="e.g. Jane Doe"
                    />
                  </div>
                </div>

                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300 ${
                    isDragActive
                      ? 'border-medical-400 bg-medical-900/20'
                      : 'border-slate-600 hover:border-medical-500 hover:bg-slate-800/50'
                  }`}
                >
                  <input {...getInputProps()} />
                  <div className="flex flex-col items-center gap-4">
                    <div className={`p-4 rounded-full ${isDragActive ? 'bg-medical-600' : 'bg-slate-700'}`}>
                      <Upload className="w-8 h-8 text-medical-400" />
                    </div>
                    <div>
                      <p className="text-lg font-medium text-white">
                        {isDragActive ? 'Drop the MRI scan here' : 'Drag & drop MRI scan'}
                      </p>
                      <p className="text-sm text-slate-400 mt-1">
                        or click to browse • Supports JPEG, PNG, BMP, TIFF
                      </p>
                    </div>
                  </div>
                </div>

                {/* Preview */}
                {preview && (
                  <div className="mt-6 flex flex-col items-center gap-4">
                    <div className="relative">
                      <img
                        src={preview}
                        alt="MRI Preview"
                        className="max-h-64 rounded-lg border border-slate-600"
                      />
                      <div className="absolute top-2 right-2 bg-slate-800/90 px-2 py-1 rounded text-xs text-slate-300 flex items-center gap-1">
                        <FileImage className="w-3 h-3" />
                        {file.name}
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="flex items-center gap-2 px-6 py-3 bg-medical-600 hover:bg-medical-700 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Analyzing...
                          </>
                        ) : (
                          <>
                            <Activity className="w-5 h-5" />
                            Analyze Scan
                          </>
                        )}
                      </button>
                      <button
                        onClick={resetAnalysis}
                        className="px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-colors"
                      >
                        Clear
                      </button>
                    </div>
                  </div>
                )}

                {/* Error */}
                {error && (
                  <div className="mt-6 p-4 bg-red-900/30 border border-red-700 rounded-lg flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                    <p className="text-red-300">{error}</p>
                  </div>
                )}
              </div>
            )}

            {/* Results Section */}
            {result && (
              <div className="space-y-6">
            {/* Success Banner */}
            <div className="p-4 bg-emerald-900/30 border border-emerald-700 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <p className="text-emerald-300">Analysis completed successfully</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={downloadReport}
                  className="px-4 py-2 bg-medical-600 hover:bg-medical-700 rounded-lg text-sm font-medium transition-colors"
                >
                  Download Report
                </button>
                <button
                  onClick={resetAnalysis}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium transition-colors"
                >
                  New Analysis
                </button>
              </div>
            </div>

            {/* Dual Pane View */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Original MRI */}
              <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div className="px-4 py-3 border-b border-slate-700 flex items-center gap-2">
                  <FileImage className="w-4 h-4 text-slate-400" />
                  <h3 className="font-medium text-slate-200">Original MRI Scan</h3>
                </div>
                <div className="p-4 flex items-center justify-center bg-slate-900/50">
                  <img
                    src={`data:image/png;base64,${result.original_image}`}
                    alt="Original MRI"
                    className="max-h-80 rounded-lg"
                  />
                </div>
              </div>

              {/* Segmented Result */}
              <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div className="px-4 py-3 border-b border-slate-700 flex items-center gap-2">
                  <Brain className="w-4 h-4 text-medical-400" />
                  <h3 className="font-medium text-slate-200">Segmentation Result</h3>
                </div>
                <div className="p-4 flex items-center justify-center bg-slate-900/50 relative">
                  <img
                    src={`data:image/png;base64,${result.segmented_image}`}
                    alt="Segmented MRI"
                    className="max-h-80 rounded-lg"
                  />
                  <div className="absolute top-6 right-6 bg-red-600/90 px-2 py-1 rounded text-xs font-medium">
                    Tumor Highlighted
                  </div>
                </div>
              </div>
            </div>

            {/* Prognosis Report Panel */}
            <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-700 flex items-center gap-2">
                <Activity className="w-5 h-5 text-medical-400" />
                <h3 className="text-lg font-semibold text-white">Prognosis Report</h3>
              </div>
              
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  {/* Tumor Area */}
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
                      <Percent className="w-4 h-4" />
                      Tumor Area
                    </div>
                    <p className="text-2xl font-bold text-white">{result.tumor_area}%</p>
                    <p className="text-xs text-slate-500 mt-1">of scan area</p>
                  </div>

                  {/* Confidence */}
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
                      <Shield className="w-4 h-4" />
                      Confidence
                    </div>
                    <p className="text-2xl font-bold text-emerald-400">{result.confidence}%</p>
                    <p className="text-xs text-slate-500 mt-1">model certainty</p>
                  </div>

                  {/* Location */}
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
                      <MapPin className="w-4 h-4" />
                      Location
                    </div>
                    <p className="text-lg font-semibold text-white">{result.location}</p>
                  </div>

                  {/* Volume Estimate */}
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
                      <TrendingUp className="w-4 h-4" />
                      Volume Est.
                    </div>
                    <p className="text-2xl font-bold text-white">{result.prognosis_data.tumor_volume_estimate}</p>
                  </div>
                </div>

                {/* Additional Prognosis Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Growth Risk Assessment</h4>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                      result.prognosis_data.growth_risk === 'Low' 
                        ? 'bg-emerald-900/50 text-emerald-300 border border-emerald-700'
                        : result.prognosis_data.growth_risk === 'Moderate'
                        ? 'bg-yellow-900/50 text-yellow-300 border border-yellow-700'
                        : 'bg-red-900/50 text-red-300 border border-red-700'
                    }`}>
                      {result.prognosis_data.growth_risk}
                    </span>
                  </div>

                  <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Recommended Follow-up</h4>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-medical-400" />
                      <span className="text-white font-medium">{result.prognosis_data.recommended_followup}</span>
                    </div>
                  </div>

                  <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Segmentation Quality</h4>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                      result.prognosis_data.segmentation_quality === 'High'
                        ? 'bg-emerald-900/50 text-emerald-300 border border-emerald-700'
                        : 'bg-yellow-900/50 text-yellow-300 border border-yellow-700'
                    }`}>
                      {result.prognosis_data.segmentation_quality}
                    </span>
                  </div>
                </div>

                {/* Disclaimer */}
                <div className="mt-6 p-4 bg-amber-900/20 border border-amber-700/50 rounded-lg">
                  <p className="text-sm text-amber-200/80">
                    <strong>Medical Disclaimer:</strong> This analysis is for research and educational purposes only. 
                    Results should be verified by qualified medical professionals before any clinical decisions are made.
                  </p>
                </div>
              </div>
            </div>
          </div>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-12 py-6 text-center text-sm text-slate-500">
        <p>NeuroScan AI • Brain Tumor Segmentation System • Research Use Only</p>
      </footer>
    </div>
  );
}

export default App;
