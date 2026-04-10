import React, { useState, useEffect } from 'react';
import { Brain, Activity, Settings, History, HelpCircle, LogOut, User } from 'lucide-react';
import MRIUploader from './components/MRIUploader';
import TumorViewer from './components/TumorViewer';
import OutcomePanel from './components/OutcomePanel';
import AuthPanel from './components/AuthPanel';
import authService from './services/authService';

function App() {
  const [currentView, setCurrentView] = useState('upload');
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data);
    setCurrentView('results');
    setLoading(false);
    setError(null);
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setLoading(false);
  };

  const handleNewAnalysis = () => {
    setAnalysisData(null);
    setError(null);
    setCurrentView('upload');
  };

  const handleExportReport = (format, data) => {
    // Placeholder for export functionality
    console.log(`Exporting report in ${format} format:`, data);
    alert(`Export functionality would generate ${format} report`);
  };

  const handleShareResults = (data) => {
    // Placeholder for share functionality
    console.log('Sharing results:', data);
    alert('Share functionality would open sharing options');
  };

  const handleAuthSuccess = (authData) => {
    setIsAuthenticated(true);
    setUser(authData.user_data);
    setCurrentView('upload');
  };

  const handleLogout = async () => {
    await authService.logout();
    setIsAuthenticated(false);
    setUser(null);
    setAnalysisData(null);
    setCurrentView('upload');
  };

  // Check authentication on mount
  useEffect(() => {
    if (authService.isAuthenticated()) {
      setIsAuthenticated(true);
      setUser(authService.getUser());
    }
  }, []);

  // Show auth panel if not authenticated
  if (!isAuthenticated) {
    return <AuthPanel onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Brain Tumor Analysis System
                </h1>
                <p className="text-sm text-gray-500">
                  Clinical-grade AI-powered tumor detection
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentView('upload')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  currentView === 'upload'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                New Analysis
              </button>
              
              {analysisData && (
                <button
                  onClick={() => setCurrentView('results')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    currentView === 'results'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  View Results
                </button>
              )}

              {/* User Menu */}
              <div className="relative group">
                <button className="flex items-center space-x-2 px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                  <User className="w-4 h-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">
                    {user?.full_name || 'User'}
                  </span>
                </button>
                
                {/* Dropdown Menu */}
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="py-1">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900">{user?.email}</p>
                      <p className="text-xs text-gray-500">Member since {new Date(user?.created_at).toLocaleDateString()}</p>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 hover:text-red-700 transition-colors flex items-center space-x-2"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      {analysisData && (
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8">
              <button
                onClick={() => setCurrentView('results')}
                className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                  currentView === 'results'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Analysis Results
              </button>
              
              <button
                onClick={() => setCurrentView('outcome')}
                className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                  currentView === 'outcome'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Clinical Assessment
              </button>
            </div>
          </div>
        </nav>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Activity className="w-5 h-5 text-red-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-800">Analysis Error</h3>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Upload View */}
        {currentView === 'upload' && (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Upload MRI Scan for Analysis
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Our AI system will analyze your brain MRI scan to detect tumors and provide 
                clinical insights for medical professionals.
              </p>
            </div>
            
            <MRIUploader 
              onAnalysisComplete={handleAnalysisComplete}
              onError={handleError}
            />
            
            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="p-3 bg-blue-100 rounded-lg w-fit mb-4">
                  <Brain className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">AI-Powered Detection</h3>
                <p className="text-gray-600">
                  Advanced deep learning model trained on thousands of medical images
                </p>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="p-3 bg-green-100 rounded-lg w-fit mb-4">
                  <Activity className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Clinical Insights</h3>
                <p className="text-gray-600">
                  Detailed tumor analysis with size, location, and severity assessment
                </p>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="p-3 bg-purple-100 rounded-lg w-fit mb-4">
                  <Settings className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Treatment Guidance</h3>
                <p className="text-gray-600">
                  Evidence-based recommendations and follow-up scheduling
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Results View */}
        {currentView === 'results' && analysisData && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                Analysis Results
              </h2>
              <button
                onClick={handleNewAnalysis}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                New Analysis
              </button>
            </div>
            
            <TumorViewer analysisData={analysisData} />
          </div>
        )}

        {/* Outcome View */}
        {currentView === 'outcome' && analysisData && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                Clinical Assessment
              </h2>
              <button
                onClick={handleNewAnalysis}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                New Analysis
              </button>
            </div>
            
            <OutcomePanel 
              analysisData={analysisData}
              onExportReport={handleExportReport}
              onShareResults={handleShareResults}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">About</h3>
              <p className="text-gray-600 text-sm">
                Clinical-grade brain tumor analysis system powered by advanced AI technology 
                for medical professionals.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Features</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• AI-powered tumor detection</li>
                <li>• Size and location analysis</li>
                <li>• Clinical recommendations</li>
                <li>• Follow-up scheduling</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Disclaimer</h3>
              <p className="text-gray-600 text-sm">
                This system is for medical professional use only. Results should be verified 
                by qualified healthcare providers before making clinical decisions.
              </p>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t text-center text-sm text-gray-500">
            <p>&copy; 2024 Brain Tumor Segmentation System. For research and clinical use.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
