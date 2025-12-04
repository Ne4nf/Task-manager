import type { ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="flex h-screen bg-gradient-to-br from-indigo-600 to-purple-700">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-gray-400 flex flex-col">
        <div className="p-6 pb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-500 to-pink-500 text-transparent bg-clip-text">
            Rockship
          </h1>
        </div>

        <nav className="flex-1">
          <div
            onClick={() => navigate('/')}
            className={`px-6 py-3.5 cursor-pointer transition-colors ${
              isActive('/') ? 'bg-white/10 text-white' : 'hover:bg-white/5 hover:text-white'
            }`}
          >
            <i className="fas fa-th-large mr-3"></i>
            Dashboard
          </div>

          <div className="px-6 py-3.5 cursor-pointer hover:bg-white/5 hover:text-white transition-colors">
            <i className="fas fa-folder mr-3"></i>
            Projects
          </div>

          <div className="px-6 py-3.5 cursor-pointer hover:bg-white/5 hover:text-white transition-colors">
            <i className="fas fa-brain mr-3"></i>
            AI Workspace
          </div>

          <div className="px-6 py-3.5 cursor-pointer hover:bg-white/5 hover:text-white transition-colors">
            <i className="fas fa-cog mr-3"></i>
            Settings
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        {children}
      </div>
    </div>
  );
}
