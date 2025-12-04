import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FolderKanban, Plus, TrendingUp, 
  Clock, CheckCircle2, AlertCircle 
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import StatCard from '../components/StatCard';
import ProjectCard from '../components/ProjectCard';
import CreateProjectModal from '../components/CreateProjectModal';
import * as api from '../api/client';

interface DashboardProps {
  onLogout: () => void;
}

export default function Dashboard({ onLogout }: DashboardProps) {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<api.Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await api.listProjects();
      setProjects(data);
    } catch (err: any) {
      console.error('Failed to load projects:', err);
      alert('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  // Calculate dashboard stats
  const stats = {
    totalProjects: projects.length,
    activeProjects: projects.filter(p => p.status === 'active').length,
    totalTasks: projects.reduce((sum, p) => sum + p.task_count, 0),
    completedTasks: projects.reduce((sum, p) => sum + p.completed_tasks, 0),
  };

  const completionRate = stats.totalTasks > 0 
    ? Math.round((stats.completedTasks / stats.totalTasks) * 100) 
    : 0;

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen">
      <Sidebar onLogout={onLogout} currentPage="dashboard" />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8 fade-in">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 mb-2">Dashboard</h1>
              <p className="text-gray-600">Overview of all your projects</p>
            </div>
            <button 
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold hover:from-blue-600 hover:to-blue-700 transition shadow-md"
            >
              <Plus className="w-5 h-5" />
              New Project
            </button>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              icon={<FolderKanban className="w-8 h-8" />}
              label="Total Projects"
              value={stats.totalProjects}
              color="purple"
            />
            <StatCard
              icon={<TrendingUp className="w-8 h-8" />}
              label="Active Projects"
              value={stats.activeProjects}
              color="blue"
            />
            <StatCard
              icon={<Clock className="w-8 h-8" />}
              label="Total Tasks"
              value={stats.totalTasks}
              color="pink"
            />
            <StatCard
              icon={<CheckCircle2 className="w-8 h-8" />}
              label="Completion Rate"
              value={`${completionRate}%`}
              color="green"
            />
          </div>

          {/* Projects Section */}
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Active Projects</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onClick={() => navigate(`/project/${project.id}`)}
              />
            ))}
          </div>

          {projects.length === 0 && (
            <div className="bg-white rounded-2xl shadow-md p-12 text-center border border-gray-200">
              <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">No Projects Yet</h3>
              <p className="text-gray-600 mb-6">Get started by creating your first project</p>
              <button 
                onClick={() => setShowCreateModal(true)}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold hover:from-blue-600 hover:to-blue-700 transition shadow-md"
              >
                Create First Project
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Create Project Modal */}
      {showCreateModal && (
        <CreateProjectModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={loadProjects}
        />
      )}
    </div>
  );
}
