# Git Analyzer - Phase 1: Simple Repository Analysis

Automatically analyze Git repositories and generate comprehensive markdown summaries using Repomix + Claude AI.

## 🎯 Phase 1 Overview

**Goal**: Given a Git URL → Generate complete markdown analysis (like `cosmo_be.md`)

**Workflow**:
```
Git URL → Repomix (bundle code) → Claude AI (analyze) → Markdown Summary
```

**Output**: Saved to `project_documents` table for project reference

---

## 📋 Features

### ✅ Phase 1 (Current)
- Analyze public/private Git repositories
- Generate comprehensive markdown analysis using SKILL.md template
- Support GitHub, GitLab, Bitbucket
- Automatic code bundling with Repomix
- Claude AI analysis with detailed prompting
- Returns markdown ready to save to `project_documents`

### 🔜 Phase 2 (Future)
- Extract modules from analysis
- Auto-generate tasks from analysis
- Store extracted modules for reuse

### 🔮 Phase 3 (Future)
- Composition-based retrieval with tags
- Cross-domain module reuse
- AI-powered similarity search

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.11+
python --version

# Node.js (for Repomix)
node --version

# Install Repomix globally
npm install -g repomix
```

### 2. Install Dependencies

```bash
cd backend
pip install anthropic
```

### 3. Environment Variables

Create `.env` file:

```env
# Claude AI
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### 4. Test the API

```bash
# Start server
uvicorn app.main:app --reload

# Test analysis
curl -X POST "http://localhost:8000/api/v1/git-analyzer/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "git_url": "https://github.com/fastapi/fastapi",
    "access_token": null
  }'
```

---

## 📚 API Documentation

### Endpoint: `POST /api/v1/git-analyzer/analyze`

Analyze a Git repository and return markdown summary.

#### Request

```json
{
  "git_url": "https://github.com/username/repo",
  "access_token": "ghp_xxxxx"  // Optional for private repos
}
```

#### Response (Success)

```json
{
  "git_url": "https://github.com/fastapi/fastapi",
  "repo_name": "fastapi",
  "owner": "fastapi",
  "analysis_markdown": "# FastAPI - (Claude review SKILL.md)\n\n**Executive Summary**\n...",
  "status": "completed",
  "error": null
}
```

#### Response (Error)

```json
{
  "git_url": "https://github.com/invalid/repo",
  "repo_name": "",
  "owner": "",
  "analysis_markdown": "",
  "status": "failed",
  "error": "Repository not found"
}
```

---

## 🏗️ Architecture

### Simple Flow (Phase 1)

```
┌─────────────┐
│  Git URL    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Repomix    │ Bundle repository code
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Claude AI  │ Analyze with SKILL.md template
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Markdown   │ Comprehensive analysis
└─────────────┘
```

### SKILL.md Analysis Template

The Claude AI prompt includes 15 comprehensive sections:

1. **Executive Summary** - Project overview, purpose, target audience
2. **Technology Stack** - Languages, frameworks, databases, tools
3. **Project Structure** - Directory layout, key files
4. **Core Modules** - Detailed module breakdown with features
5. **Architecture & Design** - Patterns, principles, scalability
6. **API Design** - Endpoints, authentication, validation
7. **Database Schema** - Tables, relationships, migrations
8. **Dependencies** - External packages and libraries
9. **Development Workflow** - Setup, testing, deployment
10. **Code Quality** - Best practices, patterns, anti-patterns
11. **Security** - Authentication, authorization, vulnerabilities
12. **Performance** - Bottlenecks, optimizations
13. **Deployment** - Infrastructure, CI/CD, monitoring
14. **Reusability Assessment** - Extractable modules, templates
15. **Recommendations** - Improvements, refactoring suggestions

### Example Output

See `cosmo_be.md` in project_documents for a complete example (665 lines).

---

## 🛠️ Development

### Project Structure

```
backend/src/modules/git_analyzer/
├── __init__.py           # Module exports
├── controller.py         # FastAPI route (1 endpoint)
├── service.py           # Analysis logic
├── schema.py            # Request/Response models
├── deps.py              # Dependency injection
└── README.md            # This file
```

### Service Methods

```python
class GitAnalyzerService:
    def _validate_git_url(url)        # Validate URL format
    def _extract_repo_info(url)       # Parse owner/repo
    def _run_repomix(url, token)      # Bundle code
    def _get_analysis_prompt()        # Generate prompt
    def _analyze_with_claude()        # Call Claude API
    def analyze_repository()          # Main entry point
    def _cleanup()                    # Clean temp files
```

---

## 🔧 Configuration

### Allowed Git Hosts

```python
ALLOWED_GIT_HOSTS = [
    "github.com",
    "gitlab.com", 
    "bitbucket.org"
]
```

### Repomix Command

```bash
npx repomix \
  --remote {git_url} \
  --output repomix-output.txt \
  --style xml \
  --remove-comments \
  --remove-empty-lines
```

### Claude AI Settings

```python
model = "claude-3-5-sonnet-20241022"
max_tokens = 16000
temperature = 0.3  # More focused, less creative
```

---

## 💾 Frontend Integration

### Save Analysis to Database

```typescript
// Call API
const result = await fetch('/api/v1/git-analyzer/analyze', {
  method: 'POST',
  body: JSON.stringify({
    git_url: 'https://github.com/user/repo',
    access_token: null
  })
});

const analysis = await result.json();

// Save to project_documents
if (analysis.status === 'completed') {
  await uploadDocument({
    project_id: currentProject.id,
    filename: `${analysis.repo_name}_analysis.md`,
    content: analysis.analysis_markdown,
    file_type: 'markdown'
  });
}
```

---

## 🔒 Security

### Private Repositories

Generate GitHub Personal Access Token:
1. Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Required scope: `repo` (Full control of private repositories)

```json
{
  "git_url": "https://github.com/private/repo",
  "access_token": "ghp_xxxxxxxxxxxxx"
}
```

---

## 🐛 Troubleshooting

### Error: "Repomix command not found"

```bash
npm install -g repomix
npx repomix --version
```

### Error: "Anthropic API key not found"

```bash
# Add to .env
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### Error: "Repository not found" (Private Repo)

Provide access token in request.

### Error: "Claude API rate limit"

Wait 60 seconds and retry. Consider:
- Exponential backoff
- Caching results
- Upgrading API plan

---

## 📊 Example Usage

### Analyze FastAPI Repository

**Input**:
```json
{
  "git_url": "https://github.com/fastapi/fastapi"
}
```

**Output** (abbreviated):
```markdown
# FastAPI - (Claude review SKILL.md)

**Executive Summary**

FastAPI is a modern, high-performance web framework for building APIs 
with Python 3.7+ based on standard Python type hints...

**Technology Stack**
- Python 3.7+
- Starlette (ASGI framework)
- Pydantic (data validation)
- Uvicorn (ASGI server)

**Core Modules**

1. **Routing System** (`fastapi/routing.py`)
   - Features: Path operations, dependencies, parameter validation
   - Dependencies: Starlette routing
   
2. **Dependency Injection** (`fastapi/dependencies`)
   - Features: Automatic dependency resolution, caching
   - Design Pattern: Dependency Injection
   
...

**Reusability Assessment**

Highly reusable modules:
- Dependency injection system (90% reusability)
- Parameter validation (85% reusability)
- OpenAPI schema generation (80% reusability)

**Recommendations**

1. Consider extracting dependency injection as standalone library
2. Improve error handling in routing module
3. Add more comprehensive examples in documentation
```

---

## 🚧 Roadmap

### ✅ Phase 1: Simple Analysis (Current)
- Git URL → Markdown summary
- SKILL.md template
- Save to project_documents

### 🔜 Phase 2: Module Extraction (Q2 2024)
- Parse analysis markdown
- Extract reusable modules
- Generate task lists
- Store in new tables

### 🔮 Phase 3: Composition System (Q3 2024)
- Tag-based search: `["type:auth", "security:oauth2"]`
- Cross-domain module reuse
- Vector similarity search
- AI template generation

---

## 📝 Notes

- Phase 1 is intentionally simple: Just analyze and return markdown
- No database tables for tracking (uses existing `project_documents`)
- No background jobs (direct API response)
- Frontend handles saving to database

For Phase 2/3 features, please coordinate with the development team.

---

## 🤝 Support

For issues:
1. Check troubleshooting section
2. Review `cosmo_be.md` example
3. Contact development team
