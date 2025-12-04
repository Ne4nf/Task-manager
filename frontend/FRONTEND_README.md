# 🚀 Rockship - Modern Project Management System

## ✨ Tổng Quan

Hệ thống quản lý dự án hiện đại với React + TypeScript + Tailwind CSS, thiết kế giao diện đẹp mắt với gradient backgrounds và glass morphism effects.

## 🎨 Tính Năng Chính

### 1. **Login Page** (`/login`)
- Giao diện đăng nhập đẹp mắt với animated background blobs
- Username & Password (default password: `123`)
- Glass morphism card design
- Animated transitions

### 2. **Dashboard** (`/dashboard`)
- Tổng quan thống kê:
  - Total Projects
  - Active Projects
  - Total Tasks
  - Completion Rate
- Grid hiển thị tất cả projects
- Click vào project card để xem chi tiết

### 3. **Project Overview** (`/project/:projectId`)
- **2 Tabs chính:**
  - **Overview Tab**: Hiển thị modules của project
  - **Documentation Tab**: Hiển thị markdown documentation (từ `cosmo_be.md`)

- **Module Management (3 nút chính):**
  - 🤖 **Gen AI Modules**: Tự động generate modules từ project docs bằng AI
  - ➕ **Create Module**: Tạo module thủ công
  - ✏️ **Update Module**: Chỉnh sửa module hiện có

- **Modules Sidebar (bên phải):**
  - Danh sách tất cả modules dạng thanh ngang nhỏ
  - Click để navigate đến module detail
  - Progress bar cho mỗi module
  - Nút + để thêm module mới

### 4. **Module Detail** (`/project/:projectId/module/:moduleId`)
- **Module Header**: Tên, mô tả, progress bar
- **Task Stats**: Hiển thị số lượng tasks theo status
  - Total, In Progress, In Review, Done, Blocked

- **Task Management (3 nút chính):**
  - 🤖 **Gen AI Tasks**: Tự động generate tasks cho module bằng AI
  - ➕ **Create Task**: Tạo task thủ công
  - ✏️ **Update Task**: Chỉnh sửa task hiện có

- **Tasks List**: Danh sách tasks với:
  - Task name & description
  - Status badge (todo, in-progress, in-review, done, blocked)
  - Assignee avatar
  - Time estimate & actual time
  - Priority level

- **Tasks Sidebar (bên phải):**
  - Danh sách tất cả tasks dạng thanh ngang nhỏ
  - Quick navigation
  - Status indicator
  - Time estimate
  - Nút + để thêm task mới

## 📁 Cấu Trúc Code

```
frontend/src/
├── App.tsx                     # Main app với routing và authentication
├── App.css                     # Global styles (gradients, animations)
├── data/
│   └── mockData.ts            # Mock data cho projects, modules, tasks
├── components/
│   ├── Sidebar.tsx            # Sidebar navigation
│   ├── StatCard.tsx           # Card hiển thị thống kê
│   └── ProjectCard.tsx        # Card hiển thị project
└── pages/
    ├── LoginPage.tsx          # Trang đăng nhập
    ├── Dashboard.tsx          # Dashboard chính
    ├── ProjectOverview.tsx    # Chi tiết project
    └── ModuleDetail.tsx       # Chi tiết module (cũ - cần update)
```

## 🎯 Mock Data Structure

### Projects
```typescript
{
  id: '1',
  name: 'Cosmo Backend',
  description: 'AI-powered email automation...',
  domain: 'AI/Backend',
  status: 'active',
  moduleCount: 6,
  taskCount: 24,
  completedTasks: 18,
  markdown: '# Cosmo Backend...' // Full documentation
}
```

### Modules
```typescript
{
  id: 'm1',
  name: 'Agent Management System',
  description: 'AI-powered email agents...',
  progress: 75,
  taskCount: 8,
  completedTasks: 6,
  features: ['...'],
  dependencies: ['...']
}
```

### Tasks
```typescript
{
  id: 't1',
  name: 'Build Agent CRUD API',
  description: '...',
  status: 'done', // todo, in-progress, in-review, done, blocked
  priority: 'high', // low, medium, high
  timeEstimate: 8, // hours
  actualTime: 7,
  assignee: 'John Doe'
}
```

## 🎨 Design System

### Colors
- **Primary Gradient**: Purple (#667eea) → Pink (#764ba2)
- **Glass Effect**: rgba(255, 255, 255, 0.1) với backdrop-filter blur
- **Status Colors**:
  - Green: Success/Done
  - Blue: In Progress
  - Yellow: In Review
  - Red: Blocked
  - Gray: Todo

### Components
- **Glass Cards**: `glass` class với backdrop blur
- **Gradient Buttons**: Purple to Pink gradient
- **Hover Effects**: Scale transform + color transitions
- **Fade In Animation**: Smooth entrance animations

## 🚀 Chạy Ứng Dụng

```bash
cd frontend
npm install
npm run dev
```

Mở http://localhost:5173

## 🔐 Authentication

- Default username: bất kỳ
- Default password: **123**
- Sau khi login, credentials lưu trong `localStorage`
- Logout sẽ xóa credentials

## 📝 Các Tính Năng Đã Implement

✅ Login page với animated background
✅ Dashboard với stats cards
✅ Project cards grid
✅ Project overview với tabs
✅ Modules sidebar navigation
✅ Module detail với tasks list
✅ Tasks sidebar navigation
✅ Status badges cho tasks
✅ Progress bars
✅ Glass morphism design
✅ Responsive layout
✅ Smooth animations

## 🔄 Các Tính Năng Cần Implement

🔲 Gen AI Modules (Backend API integration)
🔲 Gen AI Tasks (Backend API integration)
🔲 Create Module modal
🔲 Update Module modal
🔲 Create Task modal
🔲 Update Task modal
🔲 Task detail modal
🔲 Markdown editor cho docs
🔲 Real-time updates
🔲 Task filtering & sorting
🔲 Module filtering & search

## 🎯 Next Steps

1. **Update ModuleDetail.tsx** với design mới (như ProjectOverview)
2. **Tạo Modals** cho:
   - Create/Update Module
   - Create/Update Task
   - Task Detail với breakdown
3. **Backend Integration**:
   - Connect Gen AI Modules button với backend API
   - Connect Gen AI Tasks button với backend API
   - CRUD operations cho modules và tasks
4. **Enhancements**:
   - Search & filter functionality
   - Drag & drop cho tasks
   - Task time tracking
   - Notifications
   - Export project documentation

## 💡 UI/UX Highlights

- **Gradient Background**: Đẹp mắt, không quá chói
- **Glass Morphism**: Hiện đại, trong suốt
- **Sidebar Navigation**: Dễ sử dụng với modules/tasks
- **Quick Actions**: 3 nút chính cho mỗi level (Modules/Tasks)
- **Progress Visualization**: Progress bars ở mọi nơi
- **Status Indicators**: Màu sắc rõ ràng cho từng status
- **Hover Effects**: Interactive, smooth transitions
- **Responsive**: Hoạt động tốt trên mọi màn hình

## 🎨 Customization

Để thay đổi màu sắc gradient:
- Sửa `body` background trong `App.css`
- Update gradient classes trong components

Để thay đổi glass effect:
- Adjust `.glass` class opacity và blur values

Để thêm animations mới:
- Thêm @keyframes trong `App.css`
- Sử dụng với className

---

**Note**: Hiện tại đang dùng mock data trong `mockData.ts`. Khi tích hợp backend, cần thay thế bằng API calls trong `api/client.ts`.
