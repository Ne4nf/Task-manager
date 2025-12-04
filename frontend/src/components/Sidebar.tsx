import { Home, FolderKanban, Settings, LogOut, Sparkles } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

interface SidebarProps {
  onLogout: () => void;
  currentPage: string;
}

export default function Sidebar({ onLogout, currentPage }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { id: 'dashboard', icon: <Home className="w-5 h-5" />, label: 'Dashboard', path: '/dashboard' },
    { id: 'projects', icon: <FolderKanban className="w-5 h-5" />, label: 'Projects', path: '/dashboard' },
    { id: 'ai', icon: <Sparkles className="w-5 h-5" />, label: 'AI Workspace', path: '#' },
    { id: 'settings', icon: <Settings className="w-5 h-5" />, label: 'Settings', path: '#' },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col shadow-sm">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600"></div>
          Rockship
        </h2>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => item.path !== '#' && navigate(item.path)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl mb-2 transition ${
              currentPage === item.id || location.pathname === item.path
                ? 'bg-blue-50 text-blue-600 font-medium'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-gray-600 hover:bg-red-50 hover:text-red-600 transition"
        >
          <LogOut className="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}
