import { useState, useEffect } from 'react';
import { FileSpreadsheet, File, Trash2, RefreshCw, Database } from 'lucide-react';
import { getDocuments, deleteDocument, getCollectionStats } from '../services/api';

const DocumentsPage = () => {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [docs, collectionStats] = await Promise.all([
        getDocuments(),
        getCollectionStats(),
      ]);
      setDocuments(docs);
      setStats(collectionStats);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (docId, filename) => {
    if (!confirm(`Delete "${filename}"? This will remove all its products from the database.`)) {
      return;
    }

    setDeleting(docId);
    try {
      await deleteDocument(docId);
      await loadData();
    } catch (err) {
      console.error('Failed to delete:', err);
      alert('Failed to delete document');
    } finally {
      setDeleting(null);
    }
  };

  const getFileIcon = (fileType) => {
    if (['.xlsx', '.xls', '.csv'].includes(fileType)) {
      return <FileSpreadsheet className="text-green-500" size={24} />;
    }
    return <File className="text-blue-500" size={24} />;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Documents</h1>
        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
        >
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <Database className="text-purple-500" size={24} />
              <div>
                <p className="text-sm text-gray-500">Total Vectors</p>
                <p className="text-xl font-bold">{stats.points_count || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <FileSpreadsheet className="text-green-500" size={24} />
              <div>
                <p className="text-sm text-gray-500">Documents</p>
                <p className="text-xl font-bold">{documents.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${stats.status === 'green' ? 'bg-green-500' : 'bg-yellow-500'}`} />
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <p className="text-xl font-bold capitalize">{stats.status || 'Unknown'}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <RefreshCw className="animate-spin mx-auto text-gray-400 mb-4" size={32} />
          <p className="text-gray-500">Loading documents...</p>
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg">
          <FileSpreadsheet className="mx-auto text-gray-300 mb-4" size={48} />
          <p className="text-gray-500">No documents uploaded yet</p>
          <p className="text-sm text-gray-400">Upload an Excel or PDF file to get started</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">File</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Products</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Uploaded</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Status</th>
                <th className="text-right px-6 py-3 text-sm font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      {getFileIcon(doc.file_type)}
                      <div>
                        <p className="font-medium text-gray-800">{doc.filename}</p>
                        <p className="text-sm text-gray-400">{doc.file_type}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm">
                      {doc.product_count} products
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-sm">
                    {formatDate(doc.uploaded_at)}
                  </td>
                  <td className="px-6 py-4">
                    <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm">
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(doc.id, doc.filename)}
                      disabled={deleting === doc.id}
                      className="text-red-500 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                    >
                      {deleting === doc.id ? (
                        <RefreshCw className="animate-spin" size={18} />
                      ) : (
                        <Trash2 size={18} />
                      )}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default DocumentsPage;
