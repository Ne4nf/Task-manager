import { FolderKanban, Calendar, CheckCircle2 } from 'lucide-react';
import type { Project } from '../api/client';

interface ProjectCardProps {
  project: Project;
  onClick: () => void;
}

export default function ProjectCard({ project, onClick }: ProjectCardProps) {
  const completionRate = project.task_count > 0 
    ? Math.round((project.completed_tasks / project.task_count) * 100)
    : 0;

  const statusColors: Record<string, string> = {
    active: 'bg-green-100 text-green-700 border-green-200',
    completed: 'bg-blue-100 text-blue-700 border-blue-200',
    'on-hold': 'bg-yellow-100 text-yellow-700 border-yellow-200',
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-2xl p-6 cursor-pointer hover:shadow-lg transform transition-all duration-300 fade-in group border border-gray-200"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
            <FolderKanban className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-800 group-hover:text-blue-600 transition">
              {project.name}
            </h3>
            <span className={`text-xs px-2 py-1 rounded-full ${statusColors[project.status] || statusColors['active']} border`}>
              {project.status}
            </span>
          </div>
        </div>
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-2">{project.description}</p>

      <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
        <div className="flex items-center gap-1">
          <FolderKanban className="w-4 h-4" />
          <span>{project.module_count} modules</span>
        </div>
        <div className="flex items-center gap-1">
          <CheckCircle2 className="w-4 h-4" />
          <span>{project.completed_tasks}/{project.task_count} tasks</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-gray-600">
          <span>Progress</span>
          <span className="font-medium">{completionRate}%</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-500"
            style={{ width: `${completionRate}%` }}
          />
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <Calendar className="w-3 h-3" />
          <span>{new Date(project.created_at).toLocaleDateString()}</span>
        </div>
        <span className="px-2 py-1 bg-gray-100 rounded-full text-gray-700">{project.domain}</span>
      </div>
    </div>
  );
}
