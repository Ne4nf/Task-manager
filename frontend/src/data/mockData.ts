export interface Project {
  id: string;
  name: string;
  description: string;
  domain: string;
  status: 'active' | 'completed' | 'on-hold';
  moduleCount: number;
  taskCount: number;
  completedTasks: number;
  created_at: string;
  markdown?: string;
}

export interface Module {
  id: string;
  project_id: string;
  name: string;
  description: string;
  progress: number;
  taskCount: number;
  completedTasks: number;
  features?: string[];
  dependencies?: string[];
}

export interface Task {
  id: string;
  module_id: string;
  name: string;
  description: string;
  status: 'todo' | 'in-progress' | 'in-review' | 'done' | 'blocked';
  priority: 'low' | 'medium' | 'high';
  timeEstimate: number; // in hours
  actualTime?: number;
  assignee?: string;
  due_date?: string;
}

export const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Cosmo Backend',
    description: 'AI-powered email automation and CRM integration platform',
    domain: 'AI/Backend',
    status: 'active',
    moduleCount: 6,
    taskCount: 24,
    completedTasks: 18,
    created_at: '2025-01-15',
    markdown: `**Cosmo Backend - (Claude review SKILL.md)**

**Executive Summary**

Cosmo Backend is a comprehensive Go-based AI-powered email automation and CRM integration platform. The system provides intelligent email agents, marketing campaign management, contact synchronization across multiple platforms, and AI-driven content generation. It serves as the backend infrastructure for the Cosmo Agents platform, integrating with Gmail/Outlook, HubSpot, OpenAI, and various advertising platforms to automate sales and marketing workflows.

**Technology Stack**

**Backend**
- **Language**: Go 1.25.3
- **Web Framework**: Fiber v3 (high-performance HTTP framework)
- **Database**: PostgreSQL via GORM ORM
- **Queue System**: Redis with Asynq for background job processing
- **Authentication**: JWT-based with OAuth2 integration (Google, Microsoft)
- **AI Integration**: OpenAI GPT-4 for content generation and intent classification

**Core Features & Modules**

**Module 1: Agent Management System**
- AI-powered email agents that handle automated communication
- OAuth Integration: Google OAuth2 and Microsoft Graph authentication
- Token Management: Automatic token refresh and expiry handling

**Module 2: Campaign & Email Automation**
- Multi-channel email marketing campaigns with AI-generated content
- Campaign Engine: Complex workflow orchestration with intent-based routing
- AI Content Generation: OpenAI integration for personalized email templates

**Module 3: Contact Management & CRM Integration**
- Unified contact database with multi-platform synchronization
- Multi-source Import: CSV, HubSpot, Google Ads, Facebook Ads integration
- List Management: Contact segmentation and targeting

**Module 4: AI Services & Content Generation**
- AI-powered content generation and intelligent email processing
- Intent Classification: Automatic email response categorization
- AI Reply Generation: Context-aware email response generation

**Module 5: Background Job Processing**
- Asynchronous task processing for email operations and integrations
- Email Worker: Send emails, sync Gmail history, process incoming emails
- Campaign Worker: Execute campaign sequences, handle follow-ups

**Module 6: Authentication & Authorization**
- Secure API access with multi-provider OAuth integration
- JWT Authentication: Token-based API authentication
- Multi-provider OAuth: Google, Microsoft, Coze integration`
  },
  {
    id: '2',
    name: 'E-Commerce Platform',
    description: 'Full-stack e-commerce solution with payment integration',
    domain: 'Web/E-Commerce',
    status: 'active',
    moduleCount: 8,
    taskCount: 32,
    completedTasks: 12,
    created_at: '2025-01-20'
  },
  {
    id: '3',
    name: 'Mobile Banking App',
    description: 'Secure mobile banking application with biometric auth',
    domain: 'Mobile/Finance',
    status: 'active',
    moduleCount: 5,
    taskCount: 20,
    completedTasks: 15,
    created_at: '2025-01-10'
  }
];

export const mockModules: Record<string, Module[]> = {
  '1': [
    {
      id: 'm1',
      project_id: '1',
      name: 'Agent Management System',
      description: 'AI-powered email agents that handle automated communication',
      progress: 75,
      taskCount: 8,
      completedTasks: 6,
      features: ['Agent CRUD', 'OAuth Integration', 'Token Management'],
      dependencies: ['User Management', 'Organization System']
    },
    {
      id: 'm2',
      project_id: '1',
      name: 'Campaign & Email Automation',
      description: 'Multi-channel email marketing campaigns with AI-generated content',
      progress: 60,
      taskCount: 10,
      completedTasks: 6,
      features: ['Campaign Engine', 'AI Content Generation', 'Intent Classification'],
      dependencies: ['Agent System', 'AI Services']
    },
    {
      id: 'm3',
      project_id: '1',
      name: 'Contact Management & CRM',
      description: 'Unified contact database with multi-platform synchronization',
      progress: 85,
      taskCount: 6,
      completedTasks: 5,
      features: ['Contact CRUD', 'Multi-source Import', 'List Management'],
      dependencies: ['Organization System']
    }
  ],
  '2': [
    {
      id: 'm4',
      project_id: '2',
      name: 'User Authentication',
      description: 'Login, signup, password reset, and session management',
      progress: 90,
      taskCount: 6,
      completedTasks: 5,
      features: ['JWT Auth', 'OAuth2', 'Password Reset'],
      dependencies: []
    },
    {
      id: 'm5',
      project_id: '2',
      name: 'Product Catalog',
      description: 'Product listing, search, filtering, and inventory management',
      progress: 70,
      taskCount: 8,
      completedTasks: 6,
      features: ['Product CRUD', 'Search & Filter', 'Inventory Tracking'],
      dependencies: ['User Authentication']
    },
    {
      id: 'm6',
      project_id: '2',
      name: 'Payment Integration',
      description: 'Stripe integration with checkout and payment processing',
      progress: 50,
      taskCount: 10,
      completedTasks: 5,
      features: ['Stripe API', 'Checkout Flow', 'Payment Webhooks'],
      dependencies: ['Product Catalog', 'Shopping Cart']
    }
  ]
};

export const mockTasks: Record<string, Task[]> = {
  'm1': [
    {
      id: 't1',
      module_id: 'm1',
      name: 'Build Agent CRUD API',
      description: 'Implement RESTful endpoints for agent management',
      status: 'done',
      priority: 'high',
      timeEstimate: 8,
      actualTime: 7,
      assignee: 'John Doe'
    },
    {
      id: 't2',
      module_id: 'm1',
      name: 'OAuth2 Integration',
      description: 'Integrate Google and Microsoft OAuth for agent credentials',
      status: 'in-progress',
      priority: 'high',
      timeEstimate: 12,
      actualTime: 10,
      assignee: 'Jane Smith'
    },
    {
      id: 't3',
      module_id: 'm1',
      name: 'Token Refresh Service',
      description: 'Automatic token refresh for expired OAuth tokens',
      status: 'todo',
      priority: 'medium',
      timeEstimate: 6,
      assignee: 'John Doe'
    }
  ],
  'm2': [
    {
      id: 't4',
      module_id: 'm2',
      name: 'Campaign Workflow Engine',
      description: 'Build campaign orchestration with intent-based routing',
      status: 'in-review',
      priority: 'high',
      timeEstimate: 16,
      actualTime: 18,
      assignee: 'Mike Johnson'
    },
    {
      id: 't5',
      module_id: 'm2',
      name: 'AI Email Template Generator',
      description: 'OpenAI integration for personalized email templates',
      status: 'in-progress',
      priority: 'high',
      timeEstimate: 10,
      assignee: 'Sarah Lee'
    }
  ],
  'm4': [
    {
      id: 't6',
      module_id: 'm4',
      name: 'JWT Authentication',
      description: 'Implement JWT-based authentication system',
      status: 'done',
      priority: 'high',
      timeEstimate: 8,
      actualTime: 8,
      assignee: 'Alex Chen'
    },
    {
      id: 't7',
      module_id: 'm4',
      name: 'Password Reset Flow',
      description: 'Email-based password reset with secure tokens',
      status: 'done',
      priority: 'medium',
      timeEstimate: 6,
      actualTime: 5,
      assignee: 'Emily Wong'
    },
    {
      id: 't8',
      module_id: 'm4',
      name: 'OAuth2 Provider Setup',
      description: 'Google and Facebook OAuth integration',
      status: 'in-progress',
      priority: 'medium',
      timeEstimate: 10,
      assignee: 'Alex Chen'
    }
  ]
};
