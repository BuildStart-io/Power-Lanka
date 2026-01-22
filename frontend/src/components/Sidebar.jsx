import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, FileText, Upload, Settings, Phone } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: MessageSquare, label: 'Chat' },
    { path: '/documents', icon: FileText, label: 'Documents' },
    { path: '/upload', icon: Upload, label: 'Upload' },
    { path: '/whatsapp', icon: Phone, label: 'WhatsApp' },
  ];

  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-purple-400">RAG Agent</h1>
        <p className="text-gray-400 text-sm">Hair Hub Assistant</p>
      </div>

      <nav className="space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="absolute bottom-4 left-4 right-4">
        <div className="bg-gray-800 rounded-lg p-3">
          <p className="text-xs text-gray-400">Powered by</p>
          <p className="text-sm font-medium">Gemini 2.5 Flash</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
