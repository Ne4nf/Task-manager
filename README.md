# Rockship - AI-Powered Project Management

Modern project management system with AI-powered module and task generation using Claude 3.5 Sonnet, featuring intelligent memory-based reuse capabilities and Git repository analysis.

---

## ✨ Features

### 🧠 GenAI with Memory System
- **Semantic Search** - Find similar modules using 3-layer tag classification (L1: Intent, L2: Tech, L3: Domain)
- **Smart Reuse** - Automatically reuse proven modules with 3 strategies:
  - **Direct Reuse** (≥75% similarity) - Copy + customize
  - **Partial Reuse** (50-75%) - Adapt patterns from multiple sources
  - **New Generation** (<50%) - Generate from scratch
- **Self-Learning** - Auto-tag generated modules to build memory bank

### 🚀 Core Features
- **Project Management** - Create and manage projects with modules and tasks
- **AI Generation** - Auto-generate modules and tasks using Claude AI
- **Document Upload** - Upload and manage project documentation (.md, .docx, .pdf)
- **Git Analysis** - Analyze GitHub/GitLab/Bitbucket repos and generate comprehensive documentation
- **Progress Tracking** - Real-time progress calculation with auto-updating metrics
- **User Management** - Authentication with session management
- **Modern UI** - Clean interface with Tailwind CSS

---

## 🛠️ Tech Stack

### Frontend
- React 19.2.0 + TypeScript
- Vite 7.2.4
- Tailwind CSS 3.4.1
- React Router DOM
- Axios

### Backend
- FastAPI 0.115.0
- Python 3.11.9
- Supabase (PostgreSQL)
- Claude 3.5 Sonnet
- Uvicorn

---

## 📋 Prerequisites

- **Python 3.11.9** (Required - NOT 3.12+)
- **Node.js 18+**
- **Supabase Account** - https://supabase.com
- **Anthropic API Key** - https://console.anthropic.com

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Ne4nf/Task-manager.git
cd Task-manager
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# Edit .env with your credentials:
# - SUPABASE_URL
# - SUPABASE_KEY
# - SUPABASE_SERVICE_KEY
# - ANTHROPIC_API_KEY
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# (Optional) Configure environment
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
```

### 4. Database Setup

1. Create a Supabase project at https://app.supabase.com
2. Go to SQL Editor
3. Run migrations in order:
   - `database/migrations/001_initial_schema.sql`
   - `database/migrations/002_module_memory_system.sql`
   - `database/migrations/003_single_tag_per_layer.sql`

### 5. Run Application

**Terminal 1 - Backend:**
```bash
cd backend
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # macOS/Linux

# Set PYTHONPATH (Windows)
$env:PYTHONPATH = "path\to\backend"

# Set PYTHONPATH (macOS/Linux)
# export PYTHONPATH="/path/to/backend"

python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

---

## 🌐 Deployment

### Backend (Render)

1. Push code to GitHub
2. Create Web Service on Render
3. Connect repository: `Ne4nf/Task-manager`
4. Render auto-detects `backend/render.yaml`
5. Add environment variables:
   ```
   SUPABASE_URL=<your_url>
   SUPABASE_KEY=<your_key>
   SUPABASE_SERVICE_KEY=<your_service_key>
   ANTHROPIC_API_KEY=<your_api_key>
   CORS_ORIGINS=["https://your-frontend-url.vercel.app"]
   DEBUG=False
   ```

### Frontend (Vercel)

1. Import repository to Vercel
2. Set Root Directory: `frontend`
3. Framework: Vite
4. Add environment variable:
   ```
   VITE_API_URL=https://your-backend.onrender.com/api/v1
   ```
5. Deploy

---

## 📁 Project Structure

```
Task-manager/
├── backend/
│   ├── src/
│   │   ├── core/          # Config, database, AI clients
│   │   ├── modules/       # Feature modules
│   │   │   ├── auth/
│   │   │   ├── projects/
│   │   │   ├── module_manager/
│   │   │   ├── task_manager/
│   │   │   ├── document_upload/
│   │   │   └── git_analyzer/
│   │   └── main.py        # FastAPI app
│   ├── .env.example
│   ├── .python-version    # Python 3.11.9
│   ├── requirements.txt
│   └── render.yaml        # Deployment config
│
├── frontend/
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── main.tsx
│   ├── .env.example
│   ├── package.json
│   └── vercel.json        # Deployment config
│
└── database/
    └── migrations/        # SQL migration files
```

---

## 🔑 Environment Variables

### Backend (.env)
```env
# Application
APP_NAME=Rockship Backend
DEBUG=True

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key

# Claude AI
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-latest

# CORS (development)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 🧪 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/email/{email}` - Get user by email

### Projects
- `GET /api/v1/projects/` - List projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/{id}` - Get project details

### Modules
- `GET /api/v1/projects/{id}/modules` - List modules
- `POST /api/v1/modules/generate` - Generate modules with AI
- `POST /api/v1/modules/generate-with-memory` - Generate with memory reuse

### Git Analyzer
- `POST /api/v1/git-analyzer/analyze` - Analyze Git repository

Full API documentation: http://127.0.0.1:8000/docs

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Must be 3.11.9

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check .env file exists and has correct values
```

### ModuleNotFoundError: No module named 'src'
```bash
# Set PYTHONPATH (Windows)
$env:PYTHONPATH = "C:\path\to\Task-manager\backend"

# Set PYTHONPATH (macOS/Linux)
export PYTHONPATH="/path/to/Task-manager/backend"
```

### Frontend can't connect to backend
- Check backend is running on port 8000
- Check CORS_ORIGINS in backend/.env includes frontend URL
- Check VITE_API_URL in frontend/.env

### Git Analyzer fails
- Ensure Node.js and npx are installed
- Test: `npx repomix --version`
- Repomix auto-downloads via npx (no manual install needed)

---

## 📚 Key Technologies

- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database with real-time features
- **Claude AI** - Advanced language model for code analysis
- **Repomix** - Git repository bundling for AI analysis
- **React** - UI library with TypeScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🆘 Support

For issues and questions:
- Check API docs: http://127.0.0.1:8000/docs
- Review backend logs for errors
- Ensure all environment variables are set correctly

---

**Built with ❤️ using AI-powered development**
