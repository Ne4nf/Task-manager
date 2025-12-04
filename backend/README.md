# Rockship Backend

Backend API cho hệ thống quản lý dự án Rockship với tính năng Gen AI tự động sinh modules và tasks.

## 🏗️ Kiến trúc

```
backend/
├── src/
│   ├── core/               # Core functionality
│   │   ├── config.py       # App configuration
│   │   ├── database.py     # Supabase client
│   │   └── claude.py       # Claude AI client
│   ├── modules/            # Feature modules
│   │   ├── projects/       # Project management
│   │   │   ├── controller.py
│   │   │   ├── schema.py
│   │   │   ├── service.py
│   │   │   ├── model.py
│   │   │   └── deps.py
│   │   ├── module_manager/ # Module CRUD + Gen AI
│   │   ├── task_manager/   # Task CRUD + Gen AI
│   │   └── document_upload/# File upload (.md, .docx)
│   └── main.py             # FastAPI app entry point
├── requirements.txt
└── .env
```

## 🚀 Setup

### 1. Cài đặt dependencies

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Cấu hình môi trường

Copy `.env.example` thành `.env` và điền thông tin:

```bash
cp .env.example .env
```

Cập nhật các giá trị:
- `SUPABASE_URL`: URL project từ Supabase dashboard
- `SUPABASE_KEY`: Anon key từ Supabase
- `SUPABASE_SERVICE_KEY`: Service role key từ Supabase (Settings > API)
- `ANTHROPIC_API_KEY`: API key từ console.anthropic.com

### 3. Setup Database

Chạy migration SQL trong Supabase SQL Editor:

```sql
-- Copy nội dung từ database/migrations/001_initial_schema.sql
```

### 4. Chạy server

```bash
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: http://localhost:8000
API docs: http://localhost:8000/docs

## 📡 API Endpoints

### Projects
- `GET /api/v1/projects` - Lấy danh sách projects
- `GET /api/v1/projects/{id}` - Lấy chi tiết project
- `POST /api/v1/projects` - Tạo project mới
- `PUT /api/v1/projects/{id}` - Cập nhật project
- `DELETE /api/v1/projects/{id}` - Xóa project

### Document Upload
- `POST /api/v1/documents/upload/{project_id}` - Upload file .md/.docx
- `GET /api/v1/documents/project/{project_id}` - Lấy danh sách documents
- `GET /api/v1/documents/{id}` - Lấy nội dung document
- `DELETE /api/v1/documents/{id}` - Xóa document

### Modules (with Gen AI)
- `GET /api/v1/modules/project/{project_id}` - Lấy modules của project
- `GET /api/v1/modules/{id}` - Lấy chi tiết module
- `POST /api/v1/modules` - Tạo module thủ công
- `POST /api/v1/modules/generate` - **Gen AI Modules** 🤖
- `PUT /api/v1/modules/{id}` - Cập nhật module
- `DELETE /api/v1/modules/{id}` - Xóa module

### Tasks (with Gen AI)
- `GET /api/v1/tasks/module/{module_id}` - Lấy tasks của module
- `GET /api/v1/tasks/{id}` - Lấy chi tiết task
- `POST /api/v1/tasks` - Tạo task thủ công
- `POST /api/v1/tasks/generate` - **Gen AI Tasks** 🤖
- `PUT /api/v1/tasks/{id}` - Cập nhật task
- `DELETE /api/v1/tasks/{id}` - Xóa task

## 🤖 Gen AI Workflow

### 1. Upload Documentation
```bash
POST /api/v1/documents/upload/{project_id}
Content-Type: multipart/form-data
file: project_spec.md
```

### 2. Generate Modules
```bash
POST /api/v1/modules/generate
{
  "project_id": "uuid",
  "document_id": "uuid"  // optional, sẽ dùng document mới nhất
}
```

Claude AI sẽ phân tích document và sinh ra 5-12 modules với đầy đủ thông tin:
- name, description
- scope, dependencies
- features, requirements
- technical_specs

### 3. Generate Tasks
```bash
POST /api/v1/tasks/generate
{
  "module_id": "uuid"
}
```

Claude AI sẽ phân tích module và sinh ra 8-15 tasks chi tiết:
- name, description
- priority (low/medium/high)
- difficulty (1-5), time_estimate
- quality_score (1-5), autonomy (1-4)

## 🗃️ Database Schema

### Projects
- Lưu thông tin dự án
- Auto-calculate: module_count, task_count, completed_tasks, progress

### Project Documents
- Lưu file .md/.docx đã upload
- content được parse thành text để feed vào AI

### Modules
- 7 trường chi tiết: scope, dependencies, features, requirements, technical_specs
- Auto-calculate: task_count, completed_tasks, progress

### Tasks
- 8 trường performance tracking
- status: todo, in-progress, in-review, blocked, done
- priority: low, medium, high

## 🔧 Development

### Test API
Dùng Swagger UI tại http://localhost:8000/docs

### Database triggers
- Auto-update module progress khi tasks thay đổi
- Auto-update project stats khi modules/tasks thay đổi

### Lỗi thường gặp

**Import errors (supabase, anthropic):**
```bash
pip install -r requirements.txt
```

**Database connection failed:**
- Check SUPABASE_URL và SUPABASE_SERVICE_KEY trong .env
- Verify RLS policies trong Supabase

**Claude API errors:**
- Check ANTHROPIC_API_KEY
- Verify API quota tại console.anthropic.com

## 📝 Notes

- Backend dùng modular architecture với separation of concerns rõ ràng
- Mỗi module có: controller (endpoints), schema (validation), service (business logic), model (DB mapping), deps (DI)
- Gen AI prompts được optimize cho Claude 3.5 Sonnet
- File upload hiện tại chỉ support .md (docx/pdf pending)
