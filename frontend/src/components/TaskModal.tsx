import { useState } from 'react';
import { X } from 'lucide-react';

interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: TaskFormData) => void;
  mode: 'create' | 'update';
  initialData?: TaskFormData;
}

export interface TaskFormData {
  name: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  timeEstimate: number;
  assignee?: string;
  difficulty: number;
  qualityScore: number;
  autonomy: number;
  status?: 'todo' | 'in-progress' | 'in-review' | 'blocked' | 'done';
}

export default function TaskModal({ isOpen, onClose, onSubmit, mode, initialData }: TaskModalProps) {
  const defaultAssignee = mode === 'create' ? (localStorage.getItem('user_name') || '') : '';
  const [formData, setFormData] = useState<TaskFormData>(
    initialData || { 
      name: '', 
      description: '', 
      priority: 'medium',
      timeEstimate: 8,
      assignee: defaultAssignee,
      difficulty: 2,
      qualityScore: 3,
      autonomy: 2
    }
  );

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert('Please enter task name');
      return;
    }
    onSubmit(formData);
    setFormData({ 
      name: '', 
      description: '', 
      priority: 'medium', 
      timeEstimate: 8, 
      assignee: '',
      difficulty: 2,
      qualityScore: 3,
      autonomy: 2
    });
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 fade-in">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-3xl m-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {mode === 'create' ? 'Create New Task' : 'Update Task'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Basic Info */}
          <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-3">Basic Information</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Task Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition"
                  placeholder="e.g., Build Login API"
                />
              </div>
              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition"
                  rows={3}
                  placeholder="Task description and acceptance criteria..."
                />
              </div>
            </div>
          </div>

          {/* Task Details */}
          <div className="bg-green-50 rounded-xl p-4 border border-green-200">
            <h3 className="font-semibold text-green-900 mb-3">Task Details</h3>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Priority</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value as 'low' | 'medium' | 'high' })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100 transition"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Difficulty (1-5)</label>
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: parseInt(e.target.value) })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100 transition"
                >
                  <option value="1">1 - Easy</option>
                  <option value="2">2 - Medium</option>
                  <option value="3">3 - Hard</option>
                  <option value="5">5 - Expert</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Time Estimate (hours)</label>
                <input
                  type="number"
                  value={formData.timeEstimate}
                  onChange={(e) => setFormData({ ...formData, timeEstimate: parseInt(e.target.value) || 0 })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100 transition"
                  min="1"
                />
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
            <h3 className="font-semibold text-purple-900 mb-3">Performance Metrics</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Quality Score (1-5)</label>
                <select
                  value={formData.qualityScore}
                  onChange={(e) => setFormData({ ...formData, qualityScore: parseInt(e.target.value) })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition"
                >
                  <option value="1">1 - Poor</option>
                  <option value="2">2 - Fair</option>
                  <option value="3">3 - Good</option>
                  <option value="4">4 - Very Good</option>
                  <option value="5">5 - Excellent</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Autonomy Level (1-4)</label>
                <select
                  value={formData.autonomy}
                  onChange={(e) => setFormData({ ...formData, autonomy: parseInt(e.target.value) })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition"
                >
                  <option value="1">A1 - Guided</option>
                  <option value="2">A2 - Supervised</option>
                  <option value="3">A3 - Independent</option>
                  <option value="4">A4 - Autonomous</option>
                </select>
              </div>
            </div>
          </div>

          {/* Assignment */}
          <div className="bg-yellow-50 rounded-xl p-4 border border-yellow-200">
            <h3 className="font-semibold text-yellow-900 mb-3">Assignment</h3>
            <div>
              <label className="block text-gray-700 font-medium mb-2 text-sm">Assignee</label>
              <input
                type="text"
                value={formData.assignee}
                onChange={(e) => setFormData({ ...formData, assignee: e.target.value })}
                className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-yellow-500 focus:ring-2 focus:ring-yellow-100 transition"
                placeholder="John Doe"
              />
            </div>
          </div>

          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition shadow-md"
            >
              {mode === 'create' ? 'Create Task' : 'Update Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
