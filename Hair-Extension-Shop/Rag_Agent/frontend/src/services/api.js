import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Documents API
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocuments = async () => {
  const response = await api.get('/documents/');
  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await api.delete(`/documents/${documentId}`);
  return response.data;
};

export const getCollectionStats = async () => {
  const response = await api.get('/documents/stats/collection');
  return response.data;
};

// Chat API
export const sendMessage = async (message, sessionId = null) => {
  const response = await api.post('/chat/', {
    message,
    session_id: sessionId,
  });
  return response.data;
};

export const getChatHistory = async (sessionId) => {
  const response = await api.get(`/chat/history/${sessionId}`);
  return response.data;
};

export const clearChatHistory = async (sessionId) => {
  const response = await api.delete(`/chat/history/${sessionId}`);
  return response.data;
};

// Health API
export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};


// WhatsApp API
export const getWhatsAppSessions = async () => {
  const response = await api.get('/whatsapp/sessions');
  return response.data;
};

export const deleteWhatsAppSession = async (phoneNumber) => {
  const response = await api.delete(`/whatsapp/sessions/${phoneNumber}`);
  return response.data;
};

export default api;
