import { useState } from 'react';
import { X } from 'lucide-react';

interface ModuleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ModuleFormData) => void;
  mode: 'create' | 'update';
  initialData?: ModuleFormData;
}

export interface ModuleFormData {
  name: string;
  description: string;
  scope: string;
  dependencies: string;
  features: string;
  requirements: string;
  technicalSpecs: string;
}

export default function ModuleModal({ isOpen, onClose, onSubmit, mode, initialData }: ModuleModalProps) {
  const [formData, setFormData] = useState<ModuleFormData>(
    initialData || { 
      name: '', 
      description: '',
      scope: '',
      dependencies: '',
      features: '',
      requirements: '',
      technicalSpecs: ''
    }
  );

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert('Please enter module name');
      return;
    }
    onSubmit(formData);
    setFormData({ 
      name: '', 
      description: '',
      scope: '',
      dependencies: '',
      features: '',
      requirements: '',
      technicalSpecs: ''
    });
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 fade-in">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-4xl m-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {mode === 'create' ? 'Create New Module' : 'Update Module'}
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
            <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm">1</span>
              Basic Information
            </h3>
            <div className="space-y-3">
              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Module Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition"
                  placeholder="e.g., User Authentication"
                />
              </div>
              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition"
                  rows={3}
                  placeholder="Brief description of the module..."
                />
              </div>
            </div>
          </div>

          {/* Scope & Dependencies */}
          <div className="bg-green-50 rounded-xl p-4 border border-green-200">
            <h3 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-green-500 text-white flex items-center justify-center text-sm">2</span>
              Scope & Dependencies
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Scope</label>
                <textarea
                  value={formData.scope}
                  onChange={(e) => setFormData({ ...formData, scope: e.target.value })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100 transition"
                  rows={3}
                  placeholder="What's included in this module..."
                />
              </div>
              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Dependencies</label>
                <textarea
                  value={formData.dependencies}
                  onChange={(e) => setFormData({ ...formData, dependencies: e.target.value })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100 transition"
                  rows={3}
                  placeholder="External libraries, APIs..."
                />
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
            <h3 className="font-semibold text-purple-900 mb-3 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-purple-500 text-white flex items-center justify-center text-sm">3</span>
              Key Features
            </h3>
            <div>
              <label className="block text-gray-700 font-medium mb-2 text-sm">Sub-features</label>
              <textarea
                value={formData.features}
                onChange={(e) => setFormData({ ...formData, features: e.target.value })}
                className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition"
                rows={3}
                placeholder="List of key features (one per line)..."
              />
            </div>
          </div>

          {/* Requirements */}
          <div className="bg-yellow-50 rounded-xl p-4 border border-yellow-200">
            <h3 className="font-semibold text-yellow-900 mb-3 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-yellow-500 text-white flex items-center justify-center text-sm">4</span>
              Requirements & Technical Specs
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Requirements</label>
                <textarea
                  value={formData.requirements}
                  onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-yellow-500 focus:ring-2 focus:ring-yellow-100 transition"
                  rows={4}
                  placeholder="Functional & non-functional requirements..."
                />
              </div>
              <div>
                <label className="block text-gray-700 font-medium mb-2 text-sm">Technical Specifications</label>
                <textarea
                  value={formData.technicalSpecs}
                  onChange={(e) => setFormData({ ...formData, technicalSpecs: e.target.value })}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-yellow-500 focus:ring-2 focus:ring-yellow-100 transition"
                  rows={4}
                  placeholder="APIs, data models, architecture..."
                />
              </div>
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
              {mode === 'create' ? 'Create Module' : 'Update Module'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
