import { useState, useEffect } from 'react';
import { Phone, Trash2, RefreshCw, MessageSquare } from 'lucide-react';
import { getWhatsAppSessions, deleteWhatsAppSession } from '../services/api';

const WhatsAppPage = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await getWhatsAppSessions();
      setSessions(data.sessions || []);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (phoneNumber) => {
    if (!confirm(`Delete history for ${phoneNumber}? This cannot be undone.`)) {
      return;
    }

    setDeleting(phoneNumber);
    try {
      await deleteWhatsAppSession(phoneNumber);
      await loadData();
    } catch (err) {
      console.error('Failed to delete session:', err);
      alert('Failed to delete session');
    } finally {
      setDeleting(null);
    }
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
        <h1 className="text-2xl font-bold text-gray-800">WhatsApp Sessions</h1>
        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
        >
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <Phone className="text-green-500" size={24} />
            <div>
              <p className="text-sm text-gray-500">Active Sessions</p>
              <p className="text-xl font-bold">{sessions.length}</p>
            </div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <RefreshCw className="animate-spin mx-auto text-gray-400 mb-4" size={32} />
          <p className="text-gray-500">Loading sessions...</p>
        </div>
      ) : sessions.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg">
          <MessageSquare className="mx-auto text-gray-300 mb-4" size={48} />
          <p className="text-gray-500">No WhatsApp sessions yet</p>
          <p className="text-sm text-gray-400">Start a conversation via WhatsApp to see it here</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Phone Number</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Session ID</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Started</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Last Message</th>
                <th className="text-right px-6 py-3 text-sm font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {sessions.map((session) => (
                <tr key={session.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="bg-green-100 p-2 rounded-full">
                        <Phone className="text-green-600" size={16} />
                      </div>
                      <span className="font-medium text-gray-800">{session.phone_number}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 font-mono">
                    {session.session_id.substring(0, 8)}...
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-sm">
                    {formatDate(session.created_at)}
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-sm">
                    {formatDate(session.last_message_at)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(session.phone_number)}
                      disabled={deleting === session.phone_number}
                      className="text-red-500 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                      title="Clear History"
                    >
                      {deleting === session.phone_number ? (
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

export default WhatsAppPage;
