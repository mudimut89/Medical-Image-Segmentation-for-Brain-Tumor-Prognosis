import React, { useState } from 'react';
import { 
  Brain, 
  Ruler, 
  MapPin, 
  AlertTriangle, 
  CheckCircle,
  Activity,
  Clock,
  Calendar,
  FileText
} from 'lucide-react';

const TumorViewer = ({ analysisData }) => {
  const [activeView, setActiveView] = useState('overview');
  const [showOverlay, setShowOverlay] = useState(true);

  const { tumor_analysis, image_metadata, processing_time, analysis_id } = analysisData;

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'moderate': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high': return <AlertTriangle className="w-5 h-5" />;
      case 'moderate': return <Activity className="w-5 h-5" />;
      case 'low': return <CheckCircle className="w-5 h-5" />;
      default: return <Brain className="w-5 h-5" />;
    }
  };

  const formatTime = (seconds) => {
    return `${seconds.toFixed(2)}s`;
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Tumor Analysis Results
            </h2>
            <p className="text-gray-600">
              Analysis ID: {analysis_id} | Completed: {formatTimestamp(analysisData.timestamp)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Processing Time</p>
            <p className="text-lg font-semibold text-blue-600">
              {formatTime(processing_time)}
            </p>
          </div>
        </div>

        {/* Tumor Detection Status */}
        <div className={`
          border rounded-lg p-4
          ${tumor_analysis.tumor_detected 
            ? 'border-green-200 bg-green-50' 
            : 'border-gray-200 bg-gray-50'
          }
        `}>
          <div className="flex items-center space-x-3">
            <div className={`
              p-3 rounded-full
              ${tumor_analysis.tumor_detected 
                ? 'bg-green-100 text-green-600' 
                : 'bg-gray-100 text-gray-600'
              }
            `}>
              {tumor_analysis.tumor_detected ? (
                <Brain className="w-6 h-6" />
              ) : (
                <CheckCircle className="w-6 h-6" />
              )}
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-800">
                {tumor_analysis.tumor_detected ? 'Tumor Detected' : 'No Tumor Detected'}
              </h3>
              <p className="text-gray-600">
                Confidence: {(tumor_analysis.confidence * 100).toFixed(1)}%
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">
                {(tumor_analysis.confidence * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-500">Confidence</div>
            </div>
          </div>
        </div>
      </div>

      {/* Image Comparison */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Image Analysis</h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Original Image */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Original MRI</h4>
            <div className="border rounded-lg overflow-hidden bg-gray-100">
              {analysisData.images?.original && (
                <img 
                  src={analysisData.images.original} 
                  alt="Original MRI" 
                  className="w-full h-auto"
                />
              )}
            </div>
          </div>

          {/* Segmentation Mask */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Segmentation Mask</h4>
            <div className="border rounded-lg overflow-hidden bg-gray-100">
              {analysisData.images?.segmentation_mask && (
                <img 
                  src={analysisData.images.segmentation_mask} 
                  alt="Tumor Segmentation" 
                  className="w-full h-auto"
                />
              )}
            </div>
          </div>

          {/* Overlay */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Overlay (Difference)</h4>
            <div className="border rounded-lg overflow-hidden bg-gray-100">
              {analysisData.images?.overlay && (
                <img 
                  src={analysisData.images.overlay} 
                  alt="Tumor Overlay" 
                  className="w-full h-auto"
                />
              )}
            </div>
          </div>
        </div>

        {image_metadata.tumor_percentage && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-blue-800 font-medium">Tumor Coverage</span>
              <span className="text-blue-600 font-bold">
                {image_metadata.tumor_percentage?.toFixed(1)}% of image area
              </span>
            </div>
          </div>
        )}
      </div>

      {tumor_analysis.tumor_detected && (
        <>
          {/* Tumor Metrics */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Tumor Metrics</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-2">
                  <Ruler className="w-5 h-5 text-blue-600" />
                  <span className="font-medium text-gray-700">Size</span>
                </div>
                <div className="text-2xl font-bold text-gray-800">
                  {tumor_analysis.tumor_size_mm?.toFixed(1) || 'N/A'} mm
                </div>
                <div className="text-sm text-gray-500">Diameter</div>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-2">
                  <Activity className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-gray-700">Volume</span>
                </div>
                <div className="text-2xl font-bold text-gray-800">
                  {tumor_analysis.tumor_volume_mm3?.toFixed(0) || 'N/A'} mm³
                </div>
                <div className="text-sm text-gray-500">Estimated</div>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-2">
                  <MapPin className="w-5 h-5 text-purple-600" />
                  <span className="font-medium text-gray-700">Location</span>
                </div>
                <div className="text-lg font-bold text-gray-800 capitalize">
                  {tumor_analysis.tumor_location || 'Unknown'}
                </div>
                <div className="text-sm text-gray-500">Predicted</div>
              </div>
            </div>
          </div>

          {/* Severity Assessment */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Severity Assessment</h3>
            
            <div className={`
              border rounded-lg p-4
              ${getSeverityColor(tumor_analysis.severity)}
            `}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-white bg-opacity-50">
                    {getSeverityIcon(tumor_analysis.severity)}
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold capitalize">
                      {tumor_analysis.severity || 'Unknown'} Severity
                    </h4>
                    <p className="text-sm opacity-75">
                      Based on size, location, and characteristics
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-sm opacity-75">Risk Level</div>
                  <div className="text-xl font-bold capitalize">
                    {tumor_analysis.severity || 'Unknown'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Clinical Recommendations */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Clinical Recommendations</h3>
            
            <div className="space-y-3">
              {tumor_analysis.recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="p-1 bg-blue-100 rounded-full mt-0.5">
                    <div className="w-2 h-2 bg-blue-600 rounded-full" />
                  </div>
                  <p className="text-gray-700 flex-1">{recommendation}</p>
                </div>
              ))}
            </div>

            {tumor_analysis.follow_up_time && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Calendar className="w-5 h-5 text-yellow-600" />
                  <div>
                    <h4 className="font-semibold text-gray-800">Follow-up Schedule</h4>
                    <p className="text-gray-600">
                      Recommended follow-up: {tumor_analysis.follow_up_time}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Clinical Notes */}
          {tumor_analysis.clinical_notes && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Clinical Notes</h3>
              
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-gray-700">{tumor_analysis.clinical_notes}</p>
              </div>
            </div>
          )}
        </>
      )}

      {/* Image Metadata */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Scan Information</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center space-x-3">
            <FileText className="w-5 h-5 text-gray-600" />
            <div>
              <p className="text-sm text-gray-500">Filename</p>
              <p className="font-medium text-gray-800">
                {image_metadata.filename || 'Unknown'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Activity className="w-5 h-5 text-gray-600" />
            <div>
              <p className="text-sm text-gray-500">File Size</p>
              <p className="font-medium text-gray-800">
                {((image_metadata.size || 0) / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Brain className="w-5 h-5 text-gray-600" />
            <div>
              <p className="text-sm text-gray-500">Processing Shape</p>
              <p className="font-medium text-gray-800">
                {image_metadata.original_shape ? 
                  `${image_metadata.original_shape[1]}×${image_metadata.original_shape[0]}` : 
                  'Unknown'
                }
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Clock className="w-5 h-5 text-gray-600" />
            <div>
              <p className="text-sm text-gray-500">Analysis Time</p>
              <p className="font-medium text-gray-800">
                {formatTime(processing_time)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
          <div className="text-sm text-amber-800">
            <p className="font-semibold mb-1">Medical Disclaimer:</p>
            <p>
              This AI analysis is intended to assist medical professionals and should not replace 
              clinical judgment. All results should be verified by qualified healthcare providers 
              before making any medical decisions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TumorViewer;
