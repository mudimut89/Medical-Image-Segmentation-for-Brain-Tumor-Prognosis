import React, { useState } from 'react';
import { 
  TrendingUp, 
  Calendar, 
  AlertCircle, 
  CheckCircle,
  Clock,
  User,
  Activity,
  BarChart3,
  Download,
  Share2,
  Printer
} from 'lucide-react';

const OutcomePanel = ({ analysisData, onExportReport, onShareResults }) => {
  const [activeTab, setActiveTab] = useState('summary');
  const { tumor_analysis, analysis_id } = analysisData;

  const generatePrognosisSummary = () => {
    if (!tumor_analysis.tumor_detected) {
      return {
        status: 'favorable',
        confidence: 95,
        keyPoints: [
          'No tumor detected in current scan',
          'Regular monitoring recommended',
          'Low risk of immediate complications'
        ],
        recommendations: [
          'Continue routine health monitoring',
          'Report any new symptoms immediately',
          'Consider follow-up scan in 6-12 months'
        ]
      };
    }

    // Generate prognosis based on tumor characteristics
    const severity = tumor_analysis.severity;
    const size = tumor_analysis.tumor_size_mm || 0;
    
    let status, confidence, keyPoints, recommendations;

    if (severity === 'low') {
      status = 'favorable';
      confidence = 85;
      keyPoints = [
        'Small tumor detected with low-grade characteristics',
        'Good prognosis with appropriate treatment',
        'High likelihood of successful intervention'
      ];
      recommendations = [
        'Consult with neurologist within 2-4 weeks',
        'Consider surgical evaluation',
        'Begin treatment planning',
        'Monitor for symptom changes'
      ];
    } else if (severity === 'moderate') {
      status = 'guarded';
      confidence = 75;
      keyPoints = [
        'Moderate-sized tumor with intermediate characteristics',
        'Prognosis depends on timely intervention',
        'Comprehensive treatment approach recommended'
      ];
      recommendations = [
        'Urgent neurology consultation recommended',
        'Advanced imaging may be needed',
        'Multidisciplinary treatment planning',
        'Close monitoring required'
      ];
    } else {
      status = 'serious';
      confidence = 65;
      keyPoints = [
        'Large tumor with concerning characteristics',
        'Requires immediate medical attention',
        'Complex treatment approach likely needed'
      ];
      recommendations = [
        'Immediate medical evaluation required',
        'Emergency neurology consultation',
        'Hospital admission may be necessary',
        'Aggressive treatment approach recommended'
      ];
    }

    return { status, confidence, keyPoints, recommendations };
  };

  const generateFollowUpSchedule = () => {
    if (!tumor_analysis.tumor_detected) {
      return [
        { interval: '6 months', type: 'Routine MRI', purpose: 'Baseline monitoring' },
        { interval: '12 months', type: 'Clinical Review', purpose: 'Annual assessment' }
      ];
    }

    const severity = tumor_analysis.severity;
    let schedule = [];

    if (severity === 'low') {
      schedule = [
        { interval: '3 months', type: 'Post-treatment MRI', purpose: 'Treatment response' },
        { interval: '6 months', type: 'Clinical Review', purpose: 'Symptom assessment' },
        { interval: '12 months', type: 'Annual MRI', purpose: 'Long-term monitoring' }
      ];
    } else if (severity === 'moderate') {
      schedule = [
        { interval: '6 weeks', type: 'Follow-up MRI', purpose: 'Treatment planning' },
        { interval: '3 months', type: 'Post-treatment MRI', purpose: 'Response assessment' },
        { interval: '6 months', type: 'Clinical Review', purpose: 'Progress evaluation' },
        { interval: '3 months', type: 'Surveillance MRI', purpose: 'Ongoing monitoring' }
      ];
    } else {
      schedule = [
        { interval: '2 weeks', type: 'Urgent MRI', purpose: 'Pre-treatment planning' },
        { interval: '6 weeks', type: 'Post-treatment MRI', purpose: 'Early response' },
        { interval: '3 months', type: 'Clinical Review', purpose: 'Recovery assessment' },
        { interval: '6 weeks', type: 'Surveillance MRI', purpose: 'Close monitoring' }
      ];
    }

    return schedule;
  };

  const prognosis = generatePrognosisSummary();
  const followUpSchedule = generateFollowUpSchedule();

  const getStatusColor = (status) => {
    switch (status) {
      case 'favorable': return 'text-green-600 bg-green-50 border-green-200';
      case 'guarded': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'serious': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'favorable': return <CheckCircle className="w-5 h-5" />;
      case 'guarded': return <AlertCircle className="w-5 h-5" />;
      case 'serious': return <AlertCircle className="w-5 h-5" />;
      default: return <Activity className="w-5 h-5" />;
    }
  };

  const handleExport = (format) => {
    if (onExportReport) {
      onExportReport(format, analysisData);
    }
  };

  const handleShare = () => {
    if (onShareResults) {
      onShareResults(analysisData);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Clinical Outcome Assessment
            </h2>
            <p className="text-gray-600">
              Prognosis and treatment recommendations based on AI analysis
            </p>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => handleExport('pdf')}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
            
            <button
              onClick={handleShare}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Share2 className="w-4 h-4" />
              <span>Share</span>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 border-b">
          {['summary', 'prognosis', 'followup', 'timeline'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`
                px-4 py-2 font-medium transition-colors
                ${activeTab === tab
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
                }
              `}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Summary Tab */}
      {activeTab === 'summary' && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Analysis Summary</h3>
          
          <div className={`
            border rounded-lg p-4 mb-6
            ${getStatusColor(prognosis.status)}
          `}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-white bg-opacity-50">
                  {getStatusIcon(prognosis.status)}
                </div>
                <div>
                  <h4 className="text-lg font-semibold capitalize">
                    {prognosis.status} Prognosis
                  </h4>
                  <p className="text-sm opacity-75">
                    Confidence: {prognosis.confidence}%
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-sm opacity-75">Risk Level</div>
                <div className="text-xl font-bold capitalize">
                  {prognosis.status}
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">Key Findings</h4>
              <ul className="space-y-2">
                {prognosis.keyPoints.map((point, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                    <span className="text-gray-700">{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-gray-800 mb-3">Recommendations</h4>
              <ul className="space-y-2">
                {prognosis.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-green-600 rounded-full mt-2 flex-shrink-0" />
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Prognosis Tab */}
      {activeTab === 'prognosis' && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Detailed Prognosis</h3>
          
          <div className="space-y-6">
            {/* Prognosis Overview */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold text-gray-800 mb-3">Prognosis Overview</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {prognosis.confidence}%
                  </div>
                  <div className="text-sm text-gray-500">Confidence Level</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 capitalize">
                    {prognosis.status}
                  </div>
                  <div className="text-sm text-gray-500">Prognosis Status</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {tumor_analysis.tumor_detected ? 'Yes' : 'No'}
                  </div>
                  <div className="text-sm text-gray-500">Tumor Detected</div>
                </div>
              </div>
            </div>

            {/* Risk Factors */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold text-gray-800 mb-3">Risk Assessment</h4>
              
              {tumor_analysis.tumor_detected ? (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Tumor Size</span>
                    <span className="font-medium capitalize">
                      {tumor_analysis.tumor_size_mm?.toFixed(1)}mm ({tumor_analysis.severity})
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Detection Confidence</span>
                    <span className="font-medium">
                      {(tumor_analysis.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Location Risk</span>
                    <span className="font-medium capitalize">
                      {tumor_analysis.tumor_location || 'Unknown'}
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-gray-600">
                  No tumor detected - low risk profile
                </p>
              )}
            </div>

            {/* Treatment Outlook */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold text-gray-800 mb-3">Treatment Outlook</h4>
              
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-gray-800">Expected Response</p>
                    <p className="text-gray-600">
                      {tumor_analysis.tumor_detected 
                        ? 'Good response expected with timely intervention'
                        : 'No treatment required at this time'
                      }
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <Clock className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-gray-800">Recovery Timeline</p>
                    <p className="text-gray-600">
                      {tumor_analysis.severity === 'low' ? '4-6 weeks' :
                       tumor_analysis.severity === 'moderate' ? '8-12 weeks' :
                       tumor_analysis.tumor_detected ? '12+ weeks' : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Follow-up Tab */}
      {activeTab === 'followup' && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Follow-up Schedule</h3>
          
          <div className="space-y-4">
            {followUpSchedule.map((appointment, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Calendar className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800">
                        {appointment.interval}
                      </h4>
                      <p className="text-gray-600">{appointment.type}</p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Purpose</div>
                    <div className="font-medium text-gray-800">
                      {appointment.purpose}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
              <div className="text-sm text-blue-800">
                <p className="font-semibold mb-1">Follow-up Guidelines:</p>
                <ul className="space-y-1 text-blue-700">
                  <li>• Adhere to scheduled follow-up appointments</li>
                  <li>• Report any new or worsening symptoms immediately</li>
                  <li>• Bring previous imaging to all appointments</li>
                  <li>• Maintain communication with your healthcare team</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Timeline Tab */}
      {activeTab === 'timeline' && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Treatment Timeline</h3>
          
          <div className="space-y-6">
            {/* Current Status */}
            <div className="border-l-4 border-blue-600 pl-4">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-3 h-3 bg-blue-600 rounded-full" />
                <h4 className="font-semibold text-gray-800">Current Status</h4>
              </div>
              <p className="text-gray-600">
                {tumor_analysis.tumor_detected 
                  ? 'Tumor detected - awaiting clinical evaluation'
                  : 'No tumor detected - routine monitoring'
                }
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Analysis completed on {new Date(analysisData.timestamp).toLocaleDateString()}
              </p>
            </div>

            {/* Next Steps */}
            <div className="border-l-4 border-yellow-600 pl-4">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-3 h-3 bg-yellow-600 rounded-full" />
                <h4 className="font-semibold text-gray-800">Next Steps</h4>
              </div>
              <ul className="space-y-1 text-gray-600">
                {prognosis.recommendations.slice(0, 3).map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-yellow-600 rounded-full mt-2 flex-shrink-0" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Future Monitoring */}
            <div className="border-l-4 border-green-600 pl-4">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-3 h-3 bg-green-600 rounded-full" />
                <h4 className="font-semibold text-gray-800">Long-term Monitoring</h4>
              </div>
              <p className="text-gray-600">
                Regular follow-up appointments scheduled per clinical recommendations
              </p>
              <div className="mt-2 text-sm text-gray-500">
                Next follow-up: {followUpSchedule[0]?.interval || 'To be determined'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OutcomePanel;
