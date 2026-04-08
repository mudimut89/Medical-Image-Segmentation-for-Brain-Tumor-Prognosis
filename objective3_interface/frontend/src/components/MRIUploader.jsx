import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileImage, AlertCircle, CheckCircle } from 'lucide-react';
import axios from 'axios';

const MRIUploader = ({ onAnalysisComplete, onError }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setUploadedFile(file);
      handleUpload(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff', '.nii']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  });

  const handleUpload = async (file) => {
    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);
    
    // Add clinical metadata
    formData.append('patient_id', `PAT-${Date.now()}`);
    formData.append('scan_type', 'MRI_T1');
    formData.append('clinical_notes', '');

    try {
      const response = await axios.post('http://localhost:8000/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        },
      });

      onAnalysisComplete(response.data);
    } catch (error) {
      console.error('Upload error:', error);
      onError(error.response?.data?.detail || 'Analysis failed');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setUploadProgress(0);
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            MRI Scan Upload
          </h2>
          <p className="text-gray-600">
            Upload brain MRI scan for tumor analysis and clinical assessment
          </p>
        </div>

        {!uploadedFile ? (
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
              ${isDragActive || dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
              }
              ${uploading ? 'pointer-events-none opacity-50' : ''}
            `}
          >
            <input {...getInputProps()} />
            
            <div className="flex flex-col items-center space-y-4">
              <div className={`
                p-4 rounded-full
                ${isDragActive || dragActive ? 'bg-blue-100' : 'bg-gray-100'}
              `}>
                <Upload className={`
                  w-8 h-8
                  ${isDragActive || dragActive ? 'text-blue-600' : 'text-gray-600'}
                `} />
              </div>
              
              <div>
                <p className="text-lg font-medium text-gray-700">
                  {isDragActive
                    ? 'Drop the MRI scan here'
                    : 'Drag & drop MRI scan here, or click to select'
                  }
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Supports: JPEG, PNG, BMP, TIFF, NIfTI (Max 50MB)
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileImage className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-800">{uploadedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              
              {!uploading && (
                <button
                  onClick={removeFile}
                  className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>

            {uploading && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Analyzing...</span>
                  <span className="text-gray-800 font-medium">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        )}

        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Clinical Information:</p>
              <ul className="space-y-1 text-blue-700">
                <li>• Ensure patient consent for AI analysis</li>
                <li>• High-quality scans provide better results</li>
                <li>• Results should be reviewed by qualified medical professionals</li>
                <li>• This tool is for assistance, not replacement of clinical judgment</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MRIUploader;
