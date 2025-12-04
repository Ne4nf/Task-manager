import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add user_id from localStorage
api.interceptors.request.use((config) => {
  const userId = localStorage.getItem('user_id');
  if (userId) {
    config.headers['X-User-ID'] = userId;
  }
  return config;
});

// Users
export interface CreateUserRequest {
  email: string;
  full_name: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export const createUser = async (data: CreateUserRequest): Promise<User> => {
  const response = await api.post('/users/', data);
  return response.data;
};

export const getUserByEmail = async (email: string): Promise<User | null> => {
  try {
    const response = await api.get(`/users/email/${email}`);
    return response.data;
  } catch (error) {
    return null;
  }
};

export interface CreateProjectRequest {
  name: string;
  description: string;
  domain: string;
  status?: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  domain: string;
  status: string;
  module_count: number;
  task_count: number;
  completed_tasks: number;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface Module {
  id: string;
  project_id: string;
  name: string;
  description: string;
  scope: string;
  dependencies: string;
  features: string;
  requirements: string;
  technical_specs: string;
  task_count: number;
  completed_tasks: number;
  progress: number;
  generated_by_ai: boolean;
  created_at: string;
}

export interface Task {
  id: string;
  module_id: string;
  name: string;
  description: string;
  assignee: string;
  status: 'todo' | 'in-progress' | 'in-review' | 'blocked' | 'done';
  priority: 'low' | 'medium' | 'high';
  difficulty: number;
  time_estimate: number;
  actual_time: number;
  quality_score: number;
  autonomy: number;
  due_date?: string;
  generated_by_ai: boolean;
  created_at: string;
}

export interface DocumentUploadResponse {
  id: string;
  project_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
}

// Projects
export const createProject = async (data: CreateProjectRequest): Promise<Project> => {
  const response = await api.post('/projects/', data);
  return response.data;
};

export const getProject = async (projectId: string): Promise<Project> => {
  const response = await api.get(`/projects/${projectId}`);
  return response.data;
};

export const listProjects = async (): Promise<Project[]> => {
  const response = await api.get('/projects/');
  return response.data;
};

export const updateProject = async (projectId: string, data: Partial<CreateProjectRequest>): Promise<Project> => {
  const response = await api.put(`/projects/${projectId}`, data);
  return response.data;
};

export const deleteProject = async (projectId: string): Promise<void> => {
  await api.delete(`/projects/${projectId}`);
};

// Documents
export const uploadDocument = async (projectId: string, file: File): Promise<DocumentUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post(`/documents/upload/${projectId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getProjectDocuments = async (projectId: string): Promise<DocumentUploadResponse[]> => {
  const response = await api.get(`/documents/project/${projectId}`);
  return response.data;
};

export const getDocument = async (documentId: string): Promise<any> => {
  const response = await api.get(`/documents/${documentId}`);
  return response.data;
};

export const deleteDocument = async (documentId: string): Promise<void> => {
  await api.delete(`/documents/${documentId}`);
};

// Modules
export const generateModulesWithAI = async (projectId: string, documentId?: string): Promise<{ modules: Module[], message: string }> => {
  const response = await api.post('/modules/generate', {
    project_id: projectId,
    document_id: documentId,
  });
  return response.data;
};

export const createModule = async (data: {
  project_id: string;
  name: string;
  description: string;
  scope: string;
  dependencies: string;
  features: string;
  requirements: string;
  technical_specs: string;
}): Promise<Module> => {
  const response = await api.post('/modules/', data);
  return response.data;
};

export const getModulesByProject = async (projectId: string): Promise<Module[]> => {
  const response = await api.get(`/modules/project/${projectId}`);
  return response.data;
};

export const getModule = async (moduleId: string): Promise<Module> => {
  const response = await api.get(`/modules/${moduleId}`);
  return response.data;
};

export const updateModule = async (moduleId: string, data: Partial<{
  name: string;
  description: string;
  scope: string;
  dependencies: string;
  features: string;
  requirements: string;
  technical_specs: string;
}>): Promise<Module> => {
  const response = await api.put(`/modules/${moduleId}`, data);
  return response.data;
};

export const deleteModule = async (moduleId: string): Promise<void> => {
  await api.delete(`/modules/${moduleId}`);
};

// Tasks
export const generateTasksWithAI = async (moduleId: string): Promise<{ tasks: Task[], message: string }> => {
  const response = await api.post('/tasks/generate', {
    module_id: moduleId,
  });
  return response.data;
};

export const createTask = async (data: {
  module_id: string;
  name: string;
  description: string;
  assignee?: string;
  status?: string;
  priority?: string;
  difficulty?: number;
  time_estimate?: number;
  quality_score?: number;
  autonomy?: number;
  due_date?: string;
}): Promise<Task> => {
  const response = await api.post('/tasks/', data);
  return response.data;
};

export const getTasksByModule = async (moduleId: string): Promise<Task[]> => {
  const response = await api.get(`/tasks/module/${moduleId}`);
  return response.data;
};

export const getTask = async (taskId: string): Promise<Task> => {
  const response = await api.get(`/tasks/${taskId}`);
  return response.data;
};

export const updateTask = async (taskId: string, data: Partial<{
  name: string;
  description: string;
  assignee: string;
  status: string;
  priority: string;
  difficulty: number;
  time_estimate: number;
  actual_time: number;
  quality_score: number;
  autonomy: number;
  due_date: string;
}>): Promise<Task> => {
  const response = await api.put(`/tasks/${taskId}`, data);
  return response.data;
};

export const deleteTask = async (taskId: string): Promise<void> => {
  await api.delete(`/tasks/${taskId}`);
};

export default api;
