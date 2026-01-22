import { useState, useCallback } from 'react';
import { Upload, FileSpreadsheet, File, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { uploadDocument } from '../services/api';

const UploadPage = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const result = await uploadDocument(file);
      setUploadResult(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = (filename) => {
    if (filename?.endsWith('.xlsx') || filename?.endsWith('.xls') || filename?.endsWith('.csv')) {
      return <FileSpreadsheet className="text-green-500" size={24} />;
    }
    return <File className="text-blue-500" size={24} />;
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Upload Documents</h1>

      <div
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
          dragActive
            ? 'border-purple-500 bg-purple-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {uploading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="animate-spin text-purple-500 mb-4" size={48} />
            <p className="text-gray-600">Processing document...</p>
            <p className="text-sm text-gray-400">Extracting products and generating embeddings</p>
          </div>
        ) : (
          <>
            <Upload className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-lg text-gray-700 mb-2">
              Drag and drop your file here
            </p>
            <p className="text-gray-500 mb-4">or</p>
            <label className="cursor-pointer">
              <span className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors">
                Browse Files
              </span>
              <input
                type="file"
                className="hidden"
                accept=".xlsx,.xls,.csv,.pdf,.txt"
                onChange={handleChange}
              />
            </label>
            <p className="text-sm text-gray-400 mt-4">
              Supported: Excel (.xlsx, .xls), CSV, PDF, TXT (Max 5MB)
            </p>
          </>
        )}
      </div>

      {error && (
        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <XCircle className="text-red-500" size={24} />
          <div>
            <p className="font-medium text-red-800">Upload Failed</p>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      )}

      {uploadResult && (
        <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-3 mb-3">
            <CheckCircle className="text-green-500" size={24} />
            <p className="font-medium text-green-800">Upload Successful!</p>
          </div>
          <div className="bg-white rounded-lg p-4 flex items-center gap-4">
            {getFileIcon(uploadResult.filename)}
            <div className="flex-1">
              <p className="font-medium text-gray-800">{uploadResult.filename}</p>
              <p className="text-sm text-gray-500">
                {uploadResult.product_count} products extracted
              </p>
            </div>
            <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm">
              {uploadResult.status}
            </span>
          </div>
        </div>
      )}

      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <h3 className="font-medium text-gray-800 mb-3">Expected Excel Format</h3>
        <div className="overflow-x-auto">
          <table className="text-sm text-left w-full">
            <thead className="bg-gray-200">
              <tr>
                <th className="px-3 py-2">category</th>
                <th className="px-3 py-2">sub_category</th>
                <th className="px-3 py-2">product_name</th>
                <th className="px-3 py-2">price_lkr</th>
              </tr>
            </thead>
            <tbody className="bg-white">
              <tr>
                <td className="px-3 py-2 border">Extension Tools</td>
                <td className="px-3 py-2 border">Beads</td>
                <td className="px-3 py-2 border">3mm Nano Beads</td>
                <td className="px-3 py-2 border">178</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
