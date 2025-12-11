import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ChevronRight, Sparkles, Plus, Edit, Trash2,
  CheckCircle2, Clock, AlertCircle, Play, Circle
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import TaskModal, { type TaskFormData } from '../components/TaskModal';
import LoadingOverlay from '../components/LoadingOverlay';
import SelectionModal from '../components/SelectionModal';
import * as api from '../api/client';

interface ModuleDetailProps {
  onLogout: () => void;
}

const statusConfig = {
  'todo': { color: 'bg-gray-500/20 text-gray-700 border-gray-400/30', icon: Circle },
  'in-progress': { color: 'bg-blue-500/20 text-blue-700 border-blue-400/30', icon: Play },
  'in-review': { color: 'bg-yellow-500/20 text-yellow-700 border-yellow-400/30', icon: Clock },
  'done': { color: 'bg-green-500/20 text-green-700 border-green-400/30', icon: CheckCircle2 },
  'blocked': { color: 'bg-red-500/20 text-red-700 border-red-400/30', icon: AlertCircle },
};

export default function ModuleDetail({ onLogout }: ModuleDetailProps) {
  const { projectId, moduleId } = useParams();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<api.Project | null>(null);
  const [module, setModule] = useState<api.Module | null>(null);
  const [tasks, setTasks] = useState<api.Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [taskModalMode, setTaskModalMode] = useState<'create' | 'update'>('create');
  const [showSelectionModal, setShowSelectionModal] = useState(false);
  const [selectedTaskForUpdate, setSelectedTaskForUpdate] = useState<api.Task | null>(null);
  const [isRegeneratingDetails, setIsRegeneratingDetails] = useState(false);

  useEffect(() => {
    loadModuleData();
  }, [projectId, moduleId]);

  const loadModuleData = async () => {
    if (!projectId || !moduleId) return;
    
    setLoading(true);
    try {
      const [projectData, moduleData, tasksData] = await Promise.all([
        api.getProject(projectId),
        api.getModule(moduleId),
        api.getTasksByModule(moduleId),
      ]);
      setProject(projectData);
      setModule(moduleData);
      setTasks(tasksData);
    } catch (err: any) {
      console.error('Failed to load module:', err);
      alert('Failed to load module data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenAITasks = async () => {
    if (!moduleId) return;
    
    setIsGenerating(true);
    try {
      const result = await api.generateTasksWithAI(moduleId);
      alert(`Success! Generated ${result.tasks.length} tasks with AI`);
      await loadModuleData(); // Reload to show new tasks
    } catch (err: any) {
      console.error('Gen AI error:', err);
      alert(err.response?.data?.detail || 'Failed to generate tasks');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRegenerateDetails = async () => {
    if (!moduleId) return;
    
    setIsRegeneratingDetails(true);
    try {
      await api.regenerateModuleDetails(moduleId);
      alert('✅ Module details regenerated successfully!');
      await loadModuleData(); // Reload to show updated details
    } catch (err: any) {
      console.error('Regenerate error:', err);
      alert(err.response?.data?.detail || 'Failed to regenerate module details');
    } finally {
      setIsRegeneratingDetails(false);
    }
  };

  const handleCreateTask = () => {
    setTaskModalMode('create');
    setSelectedTaskForUpdate(null);
    setShowTaskModal(true);
  };

  const handleUpdateTask = () => {
    setShowSelectionModal(true);
  };

  const handleTaskSelect = (taskId: string) => {
    const selectedTask = tasks.find(t => t.id === taskId);
    if (selectedTask) {
      setSelectedTaskForUpdate(selectedTask);
      setTaskModalMode('update');
      setShowTaskModal(true);
    }
  };

  const handleTaskSubmit = async (data: TaskFormData) => {
    if (!moduleId) return;

    try {
      if (taskModalMode === 'create') {
        await api.createTask({
          module_id: moduleId,
          name: data.name,
          description: data.description,
          assignee: data.assignee,
          status: data.status || 'todo',
          priority: data.priority || 'medium',
          difficulty: data.difficulty || 2,
          time_estimate: data.timeEstimate || 0,
          quality_score: data.qualityScore || 3,
          autonomy: data.autonomy || 2,
        });
        alert(`Task created: ${data.name}`);
      } else if (selectedTaskForUpdate) {
        await api.updateTask(selectedTaskForUpdate.id, {
          name: data.name,
          description: data.description,
          assignee: data.assignee,
          status: data.status,
          priority: data.priority,
          difficulty: data.difficulty,
          time_estimate: data.timeEstimate,
          quality_score: data.qualityScore,
          autonomy: data.autonomy,
        });
        alert(`Task updated: ${data.name}`);
      }
      
      setShowTaskModal(false);
      await loadModuleData(); // Reload tasks
    } catch (err: any) {
      console.error('Task operation error:', err);
      alert(err.response?.data?.detail || 'Failed to save task');
    }
  };

  const handleDeleteTask = async (taskId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await api.deleteTask(taskId);
      alert('Task deleted successfully');
      await loadModuleData();
    } catch (err: any) {
      console.error('Delete task error:', err);
      alert(err.response?.data?.detail || 'Failed to delete task');
    }
  };

  const handleUpdateTaskStatus = async (taskId: string, newStatus: api.Task['status'], e: React.MouseEvent) => {
    e.stopPropagation();

    try {
      await api.updateTask(taskId, { status: newStatus });
      await loadModuleData(); // Reload to update progress
    } catch (err: any) {
      console.error('Update task status error:', err);
      alert(err.response?.data?.detail || 'Failed to update task status');
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!project || !module) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-gray-800 text-xl">Module not found</div>
      </div>
    );
  }

  const tasksByStatus = {
    todo: tasks.filter(t => t.status === 'todo').length,
    inProgress: tasks.filter(t => t.status === 'in-progress').length,
    inReview: tasks.filter(t => t.status === 'in-review').length,
    done: tasks.filter(t => t.status === 'done').length,
    blocked: tasks.filter(t => t.status === 'blocked').length,
  };

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
              className="hover:text-gray-800 transition"
            >
              Dashboard
            </button>
            <ChevronRight className="w-4 h-4" />
            <button
              onClick={() => navigate(`/project/${projectId}`)}
              className="hover:text-gray-800 transition"
            >
              {project.name}
            </button>
            <ChevronRight className="w-4 h-4" />
            <span className="text-gray-800 font-medium">{module.name}</span>
          </div>

          {/* Module Header */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 fade-in border border-gray-200">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h1 className="text-4xl font-bold text-gray-800 mb-2">{module.name}</h1>
                <div className="flex items-center gap-2">
                  {module.generated_by_ai && (
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-purple-100 text-purple-700 text-xs font-medium">
                      <Sparkles className="w-3 h-3" />
                      AI Generated
                    </span>
                  )}
                  {module.reused_from_module_id && (
                    <>
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-medium">
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Reused ({module.reuse_strategy === 'direct' ? 'Direct' : module.reuse_strategy === 'partial_reuse' ? 'Partial' : 'Logic Ref'})
                      </span>
                      <button
                        onClick={() => navigate(`/project/${projectId}/module/${module.reused_from_module_id}`)}
                        className="inline-flex items-center gap-1 px-2 py-1 text-xs text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                        title="View source module"
                      >
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                        View Source
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
            
            <p className="text-gray-600 text-lg mb-6 leading-relaxed">{module.description}</p>

            {/* Progress */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Progress</span>
                <span className="font-semibold">{module.progress}%</span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                  style={{ width: `${module.progress}%` }}
                />
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-5 gap-4">
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                <div className="text-sm text-gray-600 mb-1">Total Tasks</div>
                <div className="text-2xl font-bold text-gray-800">{tasks.length}</div>
              </div>
              <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                <div className="text-sm text-blue-600 mb-1">In Progress</div>
                <div className="text-2xl font-bold text-blue-700">{tasksByStatus.inProgress}</div>
              </div>
              <div className="bg-yellow-50 rounded-xl p-4 border border-yellow-200">
                <div className="text-sm text-yellow-600 mb-1">In Review</div>
                <div className="text-2xl font-bold text-yellow-700">{tasksByStatus.inReview}</div>
              </div>
              <div className="bg-green-50 rounded-xl p-4 border border-green-200">
                <div className="text-sm text-green-600 mb-1">Done</div>
                <div className="text-2xl font-bold text-green-700">{tasksByStatus.done}</div>
              </div>
              <div className="bg-red-50 rounded-xl p-4 border border-red-200">
                <div className="text-sm text-red-600 mb-1">Blocked</div>
                <div className="text-2xl font-bold text-red-700">{tasksByStatus.blocked}</div>
              </div>
            </div>
          </div>

          {/* Module Details - Expandable Sections */}
          {(module.scope || module.dependencies || module.features || module.requirements || module.technical_specs) && (
            <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 border border-gray-200">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Module Specifications</h3>
              
              <div className="space-y-4">
                {module.scope && (
                  <details className="group">
                    <summary className="cursor-pointer list-none flex items-center justify-between p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition">
                      <span className="font-semibold text-gray-800">📋 Scope</span>
                      <span className="text-gray-500 text-sm group-open:hidden">Click to expand</span>
                    </summary>
                    <div className="mt-2 p-4 bg-gray-50 rounded-lg">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">{module.scope}</pre>
                    </div>
                  </details>
                )}

                {module.features && (
                  <details className="group">
                    <summary className="cursor-pointer list-none flex items-center justify-between p-4 bg-green-50 rounded-lg hover:bg-green-100 transition">
                      <span className="font-semibold text-gray-800">✨ Features</span>
                      <span className="text-gray-500 text-sm group-open:hidden">Click to expand</span>
                    </summary>
                    <div className="mt-2 p-4 bg-gray-50 rounded-lg">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">{module.features}</pre>
                    </div>
                  </details>
                )}

                {module.dependencies && (
                  <details className="group">
                    <summary className="cursor-pointer list-none flex items-center justify-between p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition">
                      <span className="font-semibold text-gray-800">🔗 Dependencies</span>
                      <span className="text-gray-500 text-sm group-open:hidden">Click to expand</span>
                    </summary>
                    <div className="mt-2 p-4 bg-gray-50 rounded-lg">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">{module.dependencies}</pre>
                    </div>
                  </details>
                )}

                {module.requirements && (
                  <details className="group">
                    <summary className="cursor-pointer list-none flex items-center justify-between p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition">
                      <span className="font-semibold text-gray-800">📌 Requirements</span>
                      <span className="text-gray-500 text-sm group-open:hidden">Click to expand</span>
                    </summary>
                    <div className="mt-2 p-4 bg-gray-50 rounded-lg">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">{module.requirements}</pre>
                    </div>
                  </details>
                )}

                {module.technical_specs && (
                  <details className="group">
                    <summary className="cursor-pointer list-none flex items-center justify-between p-4 bg-red-50 rounded-lg hover:bg-red-100 transition">
                      <span className="font-semibold text-gray-800">⚙️ Technical Specifications</span>
                      <span className="text-gray-500 text-sm group-open:hidden">Click to expand</span>
                    </summary>
                    <div className="mt-2 p-4 bg-gray-50 rounded-lg">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">{module.technical_specs}</pre>
                    </div>
                  </details>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 border border-gray-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Task Management</h3>
            
            {/* Warning if Phase 2 failed */}
            {module.generation_metadata?.phase_2_success === false && (
              <div className="mb-4 p-4 bg-yellow-50 border border-yellow-300 rounded-xl flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-yellow-800 font-medium">
                    ⚠️ Module details are incomplete. Features, requirements, and technical specs failed to generate.
                  </p>
                  <button
                    onClick={handleRegenerateDetails}
                    disabled={isRegeneratingDetails}
                    className="mt-2 px-3 py-1.5 rounded-lg bg-yellow-600 text-white text-sm font-medium hover:bg-yellow-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isRegeneratingDetails ? 'Regenerating...' : '🔄 Regenerate Details'}
                  </button>
                </div>
              </div>
            )}
            
            <div className="flex gap-3">
              <button 
                onClick={handleGenAITasks}
                disabled={isGenerating}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-purple-600 text-white font-semibold hover:from-purple-600 hover:to-purple-700 transition shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Sparkles className="w-4 h-4" />
                {isGenerating ? 'Generating...' : 'Gen AI Tasks'}
              </button>
              <button 
                onClick={handleCreateTask}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 text-gray-700 hover:bg-gray-200 transition border border-gray-300"
              >
                <Plus className="w-4 h-4" />
                Create Task
              </button>
              <button 
                onClick={handleUpdateTask}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 text-gray-700 hover:bg-gray-200 transition border border-gray-300"
              >
                <Edit className="w-4 h-4" />
                Update Task
              </button>
            </div>
          </div>

          {/* Tasks List */}
          <div className="space-y-3">
            {tasks.length === 0 && (
              <div className="bg-white rounded-xl shadow-md p-12 text-center border border-gray-200">
                <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <h3 className="text-xl font-semibold text-gray-800 mb-2">No Tasks Yet</h3>
                <p className="text-gray-600 mb-4">Create tasks to start working on this module</p>
              </div>
            )}
            
            {tasks.map((task) => {
              return (
                <details
                  key={task.id}
                  className="bg-white rounded-xl shadow-md hover:shadow-lg transform transition border border-gray-200 group"
                >
                  <summary className="cursor-pointer list-none p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 pr-4">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="text-gray-800 font-semibold">{task.name}</h4>
                          {task.generated_by_ai && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 text-xs font-medium">
                              <Sparkles className="w-3 h-3" />
                              AI
                            </span>
                          )}
                        </div>
                        <p className="text-gray-600 text-sm line-clamp-2">{task.description}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {/* Status Dropdown */}
                        <select
                          value={task.status}
                          onChange={(e) => handleUpdateTaskStatus(task.id, e.target.value as api.Task['status'], e as any)}
                          onClick={(e) => e.stopPropagation()}
                          className={`px-3 py-1 rounded-full text-xs border cursor-pointer ${statusConfig[task.status].color}`}
                        >
                          <option value="todo">Todo</option>
                          <option value="in-progress">In Progress</option>
                          <option value="in-review">In Review</option>
                          <option value="blocked">Blocked</option>
                          <option value="done">Done</option>
                        </select>
                        
                        {/* Delete Button */}
                        <button
                          onClick={(e) => handleDeleteTask(task.id, e)}
                          className="p-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 opacity-0 group-hover:opacity-100 transition"
                          title="Delete task"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    
                    {/* Quick Info */}
                    <div className="flex items-center gap-4 text-xs text-gray-500 mt-3">
                      {task.assignee && (
                        <span className="flex items-center gap-1">
                          <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-xs">
                            {task.assignee[0]}
                          </div>
                          {task.assignee}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {task.time_estimate}h est
                      </span>
                      <span className={`px-2 py-0.5 rounded-full ${
                        task.priority === 'high' ? 'bg-red-100 text-red-700' :
                        task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {task.priority}
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-gray-100 text-gray-700">
                        Difficulty: {task.difficulty}/5
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">
                        Quality: {task.quality_score}/5
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                        Autonomy: {task.autonomy}/4
                      </span>
                    </div>
                  </summary>
                  
                  {/* Expanded Details */}
                  <div className="px-4 pb-4 pt-2 border-t border-gray-100 mt-3 space-y-3">
                    {/* Full Description */}
                    <div>
                      <h5 className="text-sm font-semibold text-gray-700 mb-1">📝 Description</h5>
                      <p className="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed">{task.description}</p>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-4 gap-3">
                      <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                        <div className="text-xs text-blue-600 mb-1">Time Estimate</div>
                        <div className="text-lg font-bold text-blue-700">{task.time_estimate}h</div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                        <div className="text-xs text-green-600 mb-1">Actual Time</div>
                        <div className="text-lg font-bold text-green-700">{task.actual_time || 0}h</div>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
                        <div className="text-xs text-purple-600 mb-1">Quality Target</div>
                        <div className="text-lg font-bold text-purple-700">{task.quality_score}/5</div>
                      </div>
                      <div className="bg-orange-50 rounded-lg p-3 border border-orange-200">
                        <div className="text-xs text-orange-600 mb-1">Autonomy Level</div>
                        <div className="text-lg font-bold text-orange-700">
                          {task.autonomy === 1 ? 'A1-Guided' : 
                           task.autonomy === 2 ? 'A2-Supervised' :
                           task.autonomy === 3 ? 'A3-Independent' : 'A4-Autonomous'}
                        </div>
                      </div>
                    </div>

                    {/* Additional Info */}
                    <div className="flex items-center gap-6 text-xs text-gray-500">
                      {task.due_date && (
                        <span className="flex items-center gap-1">
                          📅 Due: {new Date(task.due_date).toLocaleDateString()}
                        </span>
                      )}
                      {task.started_at && (
                        <span className="flex items-center gap-1">
                          ▶️ Started: {new Date(task.started_at).toLocaleDateString()}
                        </span>
                      )}
                      {task.completed_at && (
                        <span className="flex items-center gap-1 text-green-600">
                          ✅ Completed: {new Date(task.completed_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </details>
              );
            })}
          </div>

          {tasks.length === 0 && (
            <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-200">
              <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">No Tasks Yet</h3>
              <p className="text-gray-600 mb-6">Create tasks to start working on this module</p>
              <button className="px-6 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold shadow-md">
                Create First Task
              </button>
            </div>
          )}
        </div>

        {/* Tasks Sidebar */}
        <div className="w-80 bg-white border-l border-gray-200 overflow-auto p-4 shadow-lg">
          <div className="mb-4">
            <h3 className="text-gray-800 font-bold text-lg mb-2">Tasks</h3>
            <p className="text-gray-600 text-sm mb-4">Quick navigation</p>
          </div>

          <div className="space-y-2">
            {tasks.map((task) => {
              const StatusIcon = statusConfig[task.status].icon;
              return (
                <button
                  key={task.id}
                  onClick={() => alert(`Task: ${task.name}`)}
                  className="w-full text-left p-3 rounded-xl bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 transition group"
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-gray-800 text-sm font-medium group-hover:text-blue-600 transition flex-1 pr-2">
                      {task.name}
                    </span>
                    <StatusIcon className="w-4 h-4 text-gray-500 flex-shrink-0" />
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    <span>{task.time_estimate}h</span>
                    <span className={`ml-auto px-2 py-0.5 rounded-full ${statusConfig[task.status].color}`}>
                      {task.status}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          <button className="w-full mt-4 p-3 rounded-xl border-2 border-dashed border-gray-300 text-gray-600 hover:border-blue-400 hover:text-blue-600 transition flex items-center justify-center gap-2">
            <Plus className="w-4 h-4" />
            <span className="text-sm font-medium">Add Task</span>
          </button>
        </div>
      </div>

      {/* Modals */}
      <TaskModal
        isOpen={showTaskModal}
        onClose={() => setShowTaskModal(false)}
        onSubmit={handleTaskSubmit}
        mode={taskModalMode}
      />

      <SelectionModal
        isOpen={showSelectionModal}
        onClose={() => setShowSelectionModal(false)}
        onSelect={handleTaskSelect}
        items={tasks.map(t => ({ id: t.id, name: t.name, description: t.description }))}
        title="Select Task to Update"
        type="task"
      />

      <LoadingOverlay
        isLoading={isGenerating}
        message="Generating tasks with AI..."
      />
    </div>
  );
}
