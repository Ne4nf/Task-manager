import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ChevronLeft, Sparkles, Plus, Edit, Trash2,
  FolderKanban, CheckCircle2, Clock, TrendingUp,
  ChevronRight, FileText
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import ModuleModal from '../components/ModuleModal';
import type { ModuleFormData } from '../components/ModuleModal';
import LoadingOverlay from '../components/LoadingOverlay';
import SelectionModal from '../components/SelectionModal';
import DocumentUpload from '../components/DocumentUpload';
import GitAnalyzer from '../components/GitAnalyzer';
import * as api from '../api/client';

interface ProjectOverviewProps {
  onLogout: () => void;
}

export default function ProjectOverview({ onLogout }: ProjectOverviewProps) {
  const { projectId } = useParams();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<api.Project | null>(null);
  const [modules, setModules] = useState<api.Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'docs'>('overview');
  const [isGenerating, setIsGenerating] = useState(false);
  const [showModuleModal, setShowModuleModal] = useState(false);
  const [moduleModalMode, setModuleModalMode] = useState<'create' | 'update'>('create');
  const [showSelectionModal, setShowSelectionModal] = useState(false);
  const [selectedModuleForUpdate, setSelectedModuleForUpdate] = useState<api.Module | null>(null);

  // Load project and modules
  useEffect(() => {
    loadProjectData();
  }, [projectId]);

  const loadProjectData = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      const [projectData, modulesData] = await Promise.all([
        api.getProject(projectId),
        api.getModulesByProject(projectId),
      ]);
      setProject(projectData);
      setModules(modulesData);
    } catch (err: any) {
      console.error('Failed to load project:', err);
      alert('Failed to load project data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenAIModules = async () => {
    if (!projectId) return;
    
    setIsGenerating(true);
    try {
      const result = await api.generateModulesDirect(projectId);
      alert(`Success! Generated ${result.modules.length} modules with direct AI analysis`);
      await loadProjectData(); // Reload to show new modules
    } catch (err: any) {
      console.error('Gen AI error:', err);
      alert(err.response?.data?.detail || 'Failed to generate modules');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenAIWithMemories = async () => {
    if (!projectId) return;
    
    setIsGenerating(true);
    try {
      const result = await api.generateModulesWithMemories(projectId);
      
      // Show result with reuse info
      let message = `Success! Generated ${result.modules.length} modules`;
      if (result.reuse_summary) {
        message += `\n\nReuse Summary:\n`;
        message += `- Direct Reuse: ${result.reuse_summary.direct_reuse || 0}\n`;
        message += `- Pattern Combination: ${result.reuse_summary.logic_reference || 0}\n`;
        message += `- New Generation: ${result.reuse_summary.new_gen || 0}`;
      }
      
      alert(message);
      await loadProjectData(); // Reload to show new modules
    } catch (err: any) {
      console.error('Gen AI with memories error:', err);
      alert(err.response?.data?.detail || 'Failed to generate modules with memories');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCreateModule = () => {
    setModuleModalMode('create');
    setSelectedModuleForUpdate(null);
    setShowModuleModal(true);
  };

  const handleUpdateModule = () => {
    setShowSelectionModal(true);
  };

  const handleModuleSelect = (moduleId: string) => {
    const selectedModule = modules.find(m => m.id === moduleId);
    if (selectedModule) {
      setSelectedModuleForUpdate(selectedModule);
      setModuleModalMode('update');
      setShowModuleModal(true);
    }
  };

  const handleModuleSubmit = async (data: ModuleFormData) => {
    if (!projectId) return;

    try {
      if (moduleModalMode === 'create') {
        await api.createModule({
          project_id: projectId,
          name: data.name,
          description: data.description,
          scope: data.scope,
          dependencies: data.dependencies,
          features: data.features,
          requirements: data.requirements,
          technical_specs: data.technicalSpecs,
        });
        alert(`Module created: ${data.name}`);
      } else if (selectedModuleForUpdate) {
        await api.updateModule(selectedModuleForUpdate.id, {
          name: data.name,
          description: data.description,
          scope: data.scope,
          dependencies: data.dependencies,
          features: data.features,
          requirements: data.requirements,
          technical_specs: data.technicalSpecs,
        });
        alert(`Module updated: ${data.name}`);
      }
      
      setShowModuleModal(false);
      await loadProjectData(); // Reload modules
    } catch (err: any) {
      console.error('Module operation error:', err);
      alert(err.response?.data?.detail || 'Failed to save module');
    }
  };

  const handleDeleteProject = async () => {
    if (!projectId) return;
    
    if (!confirm('Are you sure you want to delete this project? All modules and tasks will be deleted.')) {
      return;
    }

    try {
      await api.deleteProject(projectId);
      alert('Project deleted successfully');
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Delete project error:', err);
      alert(err.response?.data?.detail || 'Failed to delete project');
    }
  };

  const handleDeleteModule = async (moduleId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!confirm('Are you sure you want to delete this module? All tasks will be deleted.')) {
      return;
    }

    try {
      await api.deleteModule(moduleId);
      alert('Module deleted successfully');
      await loadProjectData();
    } catch (err: any) {
      console.error('Delete module error:', err);
      alert(err.response?.data?.detail || 'Failed to delete module');
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-gray-900 text-xl">Project not found</div>
      </div>
    );
  }

  const completionRate = project.task_count > 0
    ? Math.round((project.completed_tasks / project.task_count) * 100)
    : 0;

  return (
    <div className="flex h-screen">
      <Sidebar onLogout={onLogout} currentPage="projects" />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Main Content */}
        <div className="flex-1 overflow-auto p-8">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-gray-600 mb-6 fade-in">
            <button
              onClick={() => navigate('/dashboard')}
              className="hover:text-gray-900 transition flex items-center gap-1"
            >
              <ChevronLeft className="w-4 h-4" />
              Dashboard
            </button>
            <ChevronRight className="w-4 h-4" />
            <span className="text-gray-900 font-medium">{project.name}</span>
          </div>

          {/* Project Header */}
          <div className="bg-white rounded-2xl p-6 mb-6 fade-in shadow-md border border-gray-200">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h1 className="text-4xl font-bold text-gray-800 mb-2">{project.name}</h1>
                <p className="text-gray-600 text-lg">{project.description}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="px-4 py-2 bg-green-100 text-green-700 rounded-xl border border-green-200">
                  {project.status}
                </span>
                <button
                  onClick={handleDeleteProject}
                  className="px-4 py-2 rounded-xl bg-red-50 text-red-600 hover:bg-red-100 border border-red-200 transition flex items-center gap-2"
                  title="Delete Project"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mt-6">
              <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
                <div className="flex items-center gap-2 text-purple-600 mb-2">
                  <FolderKanban className="w-5 h-5" />
                  <span className="text-sm">Modules</span>
                </div>
                <div className="text-2xl font-bold text-purple-700">{project.module_count}</div>
              </div>
              <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                <div className="flex items-center gap-2 text-blue-600 mb-2">
                  <Clock className="w-5 h-5" />
                  <span className="text-sm">Total Tasks</span>
                </div>
                <div className="text-2xl font-bold text-blue-700">{project.task_count}</div>
              </div>
              <div className="bg-green-50 rounded-xl p-4 border border-green-200">
                <div className="flex items-center gap-2 text-green-600 mb-2">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="text-sm">Completed</span>
                </div>
                <div className="text-2xl font-bold text-green-700">{project.completed_tasks}</div>
              </div>
              <div className="bg-pink-50 rounded-xl p-4 border border-pink-200">
                <div className="flex items-center gap-2 text-pink-600 mb-2">
                  <TrendingUp className="w-5 h-5" />
                  <span className="text-sm">Progress</span>
                </div>
                <div className="text-2xl font-bold text-pink-700">{completionRate}%</div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setSelectedTab('overview')}
              className={`px-6 py-3 rounded-xl font-semibold transition ${
                selectedTab === 'overview'
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <FileText className="w-4 h-4 inline mr-2" />
              Overview
            </button>
            <button
              onClick={() => setSelectedTab('docs')}
              className={`px-6 py-3 rounded-xl font-semibold transition ${
                selectedTab === 'docs'
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              Documentation
            </button>
          </div>

          {/* Content */}
          {selectedTab === 'overview' && (
            <div className="space-y-6">
              {/* Actions */}
              <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-200">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Module Management</h3>
                <div className="flex gap-3 flex-wrap">
                  <button 
                    onClick={handleGenAIModules}
                    disabled={isGenerating}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-purple-600 text-white font-semibold hover:from-purple-600 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                  >
                    <Sparkles className="w-4 h-4" />
                    {isGenerating ? 'Generating...' : '🔧 Gen AI Modules'}
                  </button>
                  <button 
                    onClick={handleGenAIWithMemories}
                    disabled={isGenerating}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold hover:from-blue-600 hover:to-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                  >
                    <Sparkles className="w-4 h-4" />
                    {isGenerating ? 'Searching Memories...' : '📝 Gen AI with Memories'}
                  </button>
                  <button 
                    onClick={handleCreateModule}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 text-gray-700 hover:bg-gray-200 transition border border-gray-300"
                  >
                    <Plus className="w-4 h-4" />
                    Create Module
                  </button>
                  <button 
                    onClick={handleUpdateModule}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 text-gray-700 hover:bg-gray-200 transition border border-gray-300"
                  >
                    <Edit className="w-4 h-4" />
                    Update Module
                  </button>
                </div>
              </div>

              {/* Modules List */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {modules.map((module) => (
                  <div
                    key={module.id}
                    className="bg-white rounded-xl p-5 hover:shadow-lg transform transition group border border-gray-200 relative"
                  >
                    <div 
                      onClick={() => navigate(`/project/${projectId}/module/${module.id}`)}
                      className="cursor-pointer"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <h4 className="text-lg font-bold text-gray-800 group-hover:text-blue-600 transition pr-8">
                          {module.name}
                        </h4>
                        <span className="text-sm text-gray-600">{module.progress}%</span>
                      </div>
                      <p className="text-gray-600 text-sm mb-4">{module.description}</p>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-3">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                          style={{ width: `${module.progress}%` }}
                        />
                      </div>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>{module.task_count} tasks</span>
                        <span>{module.completed_tasks} completed</span>
                      </div>
                    </div>
                    
                    {/* Delete button */}
                    <button
                      onClick={(e) => handleDeleteModule(module.id, e)}
                      className="absolute top-3 right-3 p-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 opacity-0 group-hover:opacity-100 transition"
                      title="Delete module"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedTab === 'docs' && (
            <div className="space-y-6">
              {/* Git Analyzer */}
              <div className="bg-white rounded-2xl p-8 shadow-md border border-gray-200">
                <h3 className="text-xl font-bold text-gray-800 mb-6">AI Repository Analysis</h3>
                <GitAnalyzer 
                  projectId={projectId!} 
                  onAnalyzeComplete={loadProjectData}
                />
              </div>

              {/* Document Upload */}
              <div className="bg-white rounded-2xl p-8 shadow-md border border-gray-200">
                <h3 className="text-xl font-bold text-gray-800 mb-6">Manual Document Upload</h3>
                <DocumentUpload 
                  projectId={projectId!} 
                  onUploadComplete={loadProjectData}
                />
              </div>
            </div>
          )}
        </div>

        {/* Modules Sidebar */}
        <div className="w-80 bg-white border-l border-gray-200 overflow-auto p-4">
          <div className="mb-4">
            <h3 className="text-gray-800 font-bold text-lg mb-2">Modules</h3>
            <p className="text-gray-600 text-sm mb-4">Click to navigate</p>
          </div>

          <div className="space-y-2">
            {modules.map((module) => (
              <button
                key={module.id}
                onClick={() => navigate(`/project/${projectId}/module/${module.id}`)}
                className="w-full text-left p-3 rounded-xl bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 transition group"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-800 font-medium text-sm group-hover:text-blue-600 transition">
                    {module.name}
                  </span>
                  <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600" />
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>{module.completed_tasks}/{module.task_count}</span>
                  <div className="flex-1 h-1 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-purple-500"
                      style={{ width: `${module.progress}%` }}
                    />
                  </div>
                </div>
              </button>
            ))}
          </div>

          <button className="w-full mt-4 p-3 rounded-xl border-2 border-dashed border-white/20 text-gray-300 hover:border-purple-400/50 hover:text-white transition flex items-center justify-center gap-2">
            <Plus className="w-4 h-4" />
            <span className="text-sm">Add Module</span>
          </button>
        </div>
      </div>

      {/* Modals */}
      <ModuleModal
        isOpen={showModuleModal}
        onClose={() => setShowModuleModal(false)}
        onSubmit={handleModuleSubmit}
        mode={moduleModalMode}
      />

      <SelectionModal
        isOpen={showSelectionModal}
        onClose={() => setShowSelectionModal(false)}
        onSelect={handleModuleSelect}
        items={modules.map(m => ({ id: m.id, name: m.name, description: m.description, progress: m.progress }))}
        title="Select Module to Update"
        type="module"
      />

      <LoadingOverlay
        isLoading={isGenerating}
        message="Generating modules with AI..."
      />
    </div>
  );
}
