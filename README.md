# Rockship - AI-Powered Project Management System

Modern project management system with AI-powered module and task generation using Claude 3.5 Sonnet.

## Features

- 🚀 **Project Management** - Create and manage projects with modules and tasks
- 🤖 **AI Generation** - Auto-generate modules and tasks using Claude AI
- 📄 **Document Upload** - Upload and manage project documentation (.md, .docx, .pdf)
- 📊 **Progress Tracking** - Real-time progress calculation with auto-updating metrics
- 👥 **User Management** - Simple authentication and user assignment
- 🎨 **Modern UI** - Clean white/blue interface built with React and Tailwind CSS

## Tech Stack

### Frontend
- React 19.2.0 + TypeScript
- Vite 7.2.4
- Tailwind CSS 3.4.1
- React Router DOM
- Axios for API calls
- Lucide React for icons

### Backend
- FastAPI 0.115.0
- Python 3.11
- Supabase (PostgreSQL)
- Claude 3.5 Sonnet AI
- Uvicorn server

## Project Structure

```
code-memory UI/
├── frontend/               # React frontend
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── main.tsx       # Entry point
│   ├── package.json
│   └── vercel.json        # Vercel deployment config
│
├── backend/               # FastAPI backend
│   ├── src/
│   │   ├── core/         # Core configs (settings, database, AI)
│   │   ├── modules/      # Feature modules
│   │   │   ├── projects/
│   │   │   ├── module_manager/
│   │   │   ├── task_manager/
│   │   │   └── document_upload/
│   │   └── main.py       # FastAPI app
│   ├── requirements.txt
│   ├── render.yaml       # Render deployment config
│   └── .env.example
│
└── database/
    └── migrations/       # SQL migration files
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account
- Anthropic API key (for Claude AI)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Mac/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

5. Configure `.env` with your credentials:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

6. Run database migrations (in Supabase SQL editor):
```bash
# Execute database/migrations/001_initial_schema.sql
```

7. (Optional) Seed test data:
```bash
python seed_database.py
```

8. Start backend server:
```bash
python -m uvicorn src.main:app --reload --port 8000
```

Backend will run at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will run at: `http://localhost:5173`

### Default Login
- Username: Any name (e.g., "admin")
- Password: `123`

## Deployment

### Frontend (Vercel)

1. Push code to GitHub
2. Import repository in Vercel
3. Configure:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Deploy

### Backend (Render)

1. Push code to GitHub
2. Create new Web Service in Render
3. Connect repository
4. Configure:
   - Root Directory: `backend`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `ANTHROPIC_API_KEY`
   - `CORS_ORIGINS` (add your Vercel URL)
   - `DEBUG=False`
6. Deploy

### Post-Deployment

1. Update `CORS_ORIGINS` in backend `.env`:
```env
CORS_ORIGINS=["https://your-app.vercel.app"]
```

2. Update API URL in frontend `src/api/client.ts`:
```typescript
const API_BASE_URL = 'https://your-backend.onrender.com/api/v1';
```

## API Endpoints

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/email/{email}` - Get user by email

### Projects
- `GET /api/v1/projects/` - List all projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/{id}` - Get project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Modules
- `GET /api/v1/modules/project/{project_id}` - List project modules
- `POST /api/v1/modules/` - Create module
- `POST /api/v1/modules/generate` - Generate modules with AI
- `GET /api/v1/modules/{id}` - Get module
- `PUT /api/v1/modules/{id}` - Update module
- `DELETE /api/v1/modules/{id}` - Delete module

### Tasks
- `GET /api/v1/tasks/module/{module_id}` - List module tasks
- `POST /api/v1/tasks/` - Create task
- `POST /api/v1/tasks/generate` - Generate tasks with AI
- `GET /api/v1/tasks/{id}` - Get task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

### Documents
- `POST /api/v1/documents/upload/{project_id}` - Upload document
- `GET /api/v1/documents/project/{project_id}` - List project documents
- `GET /api/v1/documents/{id}` - Get document
- `DELETE /api/v1/documents/{id}` - Delete document

## Database Schema

### Users
- `id` (UUID, PK)
- `email` (TEXT, UNIQUE)
- `full_name` (TEXT)
- `created_at` (TIMESTAMP)

### Projects
- `id` (UUID, PK)
- `user_id` (UUID, FK)
- `name` (TEXT)
- `description` (TEXT)
- `domain` (TEXT)
- `status` (ENUM: active, completed, archived)
- `progress` (NUMERIC, auto-calculated)
- `created_at`, `updated_at`

### Modules
- `id` (UUID, PK)
- `project_id` (UUID, FK)
- `name` (TEXT)
- `description` (TEXT)
- `scope`, `dependencies`, `features`, `requirements`, `technical_specs` (TEXT)
- `progress` (NUMERIC, auto-calculated)
- `created_at`, `updated_at`

### Tasks
- `id` (UUID, PK)
- `module_id` (UUID, FK)
- `name` (TEXT)
- `description` (TEXT)
- `assignee` (TEXT)
- `status` (ENUM: todo, in-progress, in-review, blocked, done)
- `priority` (ENUM: low, medium, high)
- `difficulty` (INTEGER, 1-5)
- `time_estimate`, `actual_time` (NUMERIC)
- `quality_score`, `autonomy` (INTEGER, 1-5)
- `created_at`, `updated_at`, `completed_at`

### Documents
- `id` (UUID, PK)
- `project_id` (UUID, FK)
- `user_id` (UUID, FK)
- `filename` (TEXT)
- `file_type` (TEXT)
- `file_size` (INTEGER)
- `content` (TEXT)
- `created_at`

## Environment Variables

### Backend (.env)
```env
# Application
APP_NAME=Rockship Backend
APP_VERSION=1.0.0
DEBUG=True

# Supabase
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
SUPABASE_SERVICE_KEY=your_service_key

# Claude AI
ANTHROPIC_API_KEY=your_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# API
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:5173"]

# File Upload
MAX_FILE_SIZE=10485760
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - feel free to use this project for learning or commercial purposes.

## Support

For issues or questions:
- Open an issue on GitHub
- Check API documentation at `/docs` endpoint

## Roadmap

- [ ] Real JWT authentication
- [ ] Email notifications
- [ ] Task comments and attachments
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard
- [ ] Mobile responsive improvements
- [ ] Export to PDF/Excel
- [ ] Integration with GitHub/Jira
