"""
Git Analyzer Service - Simplified for Phase 1
Handles: Git URL → Repomix → Claude AI → Markdown Summary
"""
import os
import subprocess
import tempfile
import shutil
import hashlib
from typing import Optional, Dict
from pathlib import Path
from urllib.parse import urlparse
import anthropic
from supabase import Client

from src.core.config import get_settings


class GitAnalyzerService:
    """Simple service for analyzing Git repositories"""
    
    ALLOWED_HOSTS = ["github.com", "gitlab.com", "bitbucket.org"]
    
    def __init__(self, db: Client = None):
        self.settings = get_settings()
        self.anthropic_client = anthropic.Anthropic(
            api_key=self.settings.ANTHROPIC_API_KEY
        )
        self.temp_dir = None
        self.db = db
    
    def _validate_git_url(self, git_url: str) -> bool:
        """Validate Git URL against allowed hosts"""
        try:
            parsed = urlparse(git_url)
            hostname = parsed.netloc.lower()
            
            # Remove 'www.' prefix
            if hostname.startswith('www.'):
                hostname = hostname[4:]
            
            if hostname not in self.ALLOWED_HOSTS:
                raise ValueError(
                    f"Repository host '{hostname}' is not allowed. "
                    f"Allowed hosts: {', '.join(self.ALLOWED_HOSTS)}"
                )
            return True
        except Exception as e:
            raise ValueError(f"Invalid Git URL: {str(e)}")
    
    def _extract_repo_info(self, git_url: str) -> tuple[str, str]:
        """Extract owner and repo name from Git URL"""
        parsed = urlparse(git_url)
        path = parsed.path.strip('/')
        
        # Remove .git suffix
        if path.endswith('.git'):
            path = path[:-4]
        
        parts = path.split('/')
        if len(parts) >= 2:
            owner = parts[0]
            repo_name = parts[1]
            return owner, repo_name
        else:
            raise ValueError(f"Cannot extract repo info from URL: {git_url}")
    
    def _run_repomix(
        self,
        git_url: str,
        access_token: Optional[str] = None
    ) -> str:
        """
        Run repomix on Git repository
        Returns packed content as string
        """
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp(prefix="repomix_")
        _, repo_name = self._extract_repo_info(git_url)
        
        # Output file in current directory (repomix creates it here by default)
        output_filename = f"{repo_name}.txt"
        output_file = os.path.join(self.temp_dir, output_filename)
        
        # Build Git URL with token if private
        repo_url = git_url
        if access_token:
            # Add .git suffix if not present for token authentication
            if not git_url.endswith('.git'):
                git_url = git_url + '.git'
            parsed = urlparse(git_url)
            repo_url = f"{parsed.scheme}://{access_token}@{parsed.netloc}{parsed.path}"
        
        # Build repomix command
        # Note: --remote flag clones repo, so output goes to cwd
        # Use full path for npx on Windows
        npx_cmd = "npx"
        if os.name == 'nt':  # Windows
            npx_cmd = r"C:\Program Files\nodejs\npx.cmd"
        
        cmd = [
            npx_cmd,
            "repomix",
            "--remote", repo_url,
            "--output", output_filename,  # Just filename, not full path
            "--style", "plain"  # Use plain instead of xml for better compatibility
        ]
        
        try:
            # Run repomix from temp directory
            print(f"[DEBUG] Running repomix in: {self.temp_dir}")
            print(f"[DEBUG] Command: {' '.join(cmd[:4])}...")  # Don't log token
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
                cwd=self.temp_dir,
                encoding='utf-8',
                errors='ignore'  # Ignore encoding errors
            )
            
            print(f"[DEBUG] Repomix stdout: {result.stdout[:500] if result.stdout else 'None'}")
            print(f"[DEBUG] Repomix stderr: {result.stderr[:500] if result.stderr else 'None'}")
            print(f"[DEBUG] Return code: {result.returncode}")
            
            # List files in temp directory to debug
            files_in_dir = os.listdir(self.temp_dir)
            print(f"[DEBUG] Files in temp dir: {files_in_dir}")
            
            # Don't fail on non-zero return code immediately - check if file exists first
            # because repomix sometimes returns non-zero even when successful
            
            # Check output file exists
            if not os.path.exists(output_file):
                # Try to find any repomix output file
                possible_files = [f for f in files_in_dir if repo_name in f.lower() or 'repomix' in f.lower() or f.endswith(('.txt', '.xml', '.md'))]
                print(f"[DEBUG] Possible output files: {possible_files}")
                
                if possible_files:
                    output_file = os.path.join(self.temp_dir, possible_files[0])
                    print(f"[DEBUG] Using alternative output file: {output_file}")
                else:
                    error_msg = result.stderr or result.stdout or "Unknown error"
                    raise RuntimeError(f"Repomix did not create output file. Return code: {result.returncode}. Error: {error_msg}. Files: {files_in_dir}")
            
            # Read content
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content or len(content) < 100:
                raise RuntimeError("Repomix output is empty or too small")
            
            print(f"[DEBUG] Successfully read {len(content)} chars from repomix output")
            return content
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Repomix execution timed out after 5 minutes")
        except Exception as e:
            raise RuntimeError(f"Failed to run repomix: {str(e)}")
    
    def _cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass
    
    def _get_analysis_prompt(self, repo_name: str, packed_content: str) -> str:
        """
        Generate Claude analysis prompt with SKILL.md template
        """
        # Truncate if too large
        max_length = 180000  # ~45k tokens
        if len(packed_content) > max_length:
            packed_content = packed_content[:max_length] + "\n\n[Content truncated...]"
        
        prompt = f"""You are an expert software architect analyzing the repository: **{repo_name}**

Your task is to produce a **comprehensive, well-structured Markdown analysis** that helps engineers quickly understand the project.

Output must be in **Markdown format** following this structure:

---

# Project Name Analysis Documentation

**Executive Summary**

[1-2 paragraphs describing what this project does, its main purpose, and value proposition]

---

## Technology Stack

**Backend**
- **Language**: [e.g., Python 3.11, Go 1.25, TypeScript]
- **Framework**: [e.g., FastAPI, Express, Django]
- **Database**: [e.g., PostgreSQL, MongoDB]
- **Authentication**: [e.g., JWT, OAuth2]
- **AI Integration**: [e.g., OpenAI GPT-4, Claude]

**Frontend** (if applicable)
- **Framework**: [e.g., React, Vue, Next.js]
- **State Management**: [e.g., Redux, Zustand]
- **UI Library**: [e.g., Tailwind CSS, Material-UI]

**Infrastructure & Tools**
- **Deployment**: [e.g., Docker, Kubernetes]
- **CI/CD**: [e.g., GitHub Actions]
- **Monitoring**: [e.g., Sentry, Prometheus]

---

## Project Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.tsx
│   └── package.json
└── README.md
```

[Describe the folder structure and organization]

---

## Core Features & Modules

### Module 1: [Module Name]
**Purpose**: [What this module does]

**Key Components**:
- [Component 1]: [Description]
- [Component 2]: [Description]

**API Endpoints** (if applicable):
- `GET /api/endpoint` - [Description]
- `POST /api/endpoint` - [Description]

**Database Tables**:
- `table_name`: [Description]

**Dependencies**:
- Internal: [Other modules it depends on]
- External: [External services/APIs]

### Module 2: [Module Name]
[Same structure as Module 1...]

[Continue for all major modules - aim for 3-6 modules]

---

## System Architecture

**Architecture Pattern**: [MVC, Microservices, Monolith, etc.]

**Data Flow**:
```
User → Frontend → API Gateway → Backend Services → Database
                                    ↓
                              External APIs (OpenAI, etc.)
```

**Key Design Patterns**:
- [Pattern 1]: [Where and why it's used]
- [Pattern 2]: [Where and why it's used]

---

## API Documentation

### [Feature] API

**Endpoint**: `POST /api/v1/feature`
- **Purpose**: [What it does]
- **Request**: [Request body structure]
- **Response**: [Response structure]
- **Auth Required**: Yes/No

[Document 5-10 key endpoints]

---

## Database Schema

```sql
-- Key tables and relationships
users (1:many) → projects
projects (1:many) → modules
modules (1:many) → tasks
```

**Main Tables**:
- `users`: [Description]
- `projects`: [Description]
- `modules`: [Description]

---

## Notable Features

1. **[Feature 1]**: [Description and why it's notable]
2. **[Feature 2]**: [Description and why it's notable]
3. **[Feature 3]**: [Description and why it's notable]

---

## Code Patterns & Conventions

**Naming Conventions**:
- Files: [e.g., snake_case, kebab-case]
- Functions: [e.g., camelCase, snake_case]
- Classes: [e.g., PascalCase]

**Code Organization**:
- [Pattern 1]: [Description]
- [Pattern 2]: [Description]

**Error Handling**:
- [Approach used in the project]

---

## External Integrations

### Integration 1: [Service Name]
- **Purpose**: [What it's used for]
- **Implementation**: [How it's integrated]
- **Configuration**: [Required setup]

[List all major external integrations]

---

## Configuration & Environment

**Required Environment Variables**:
```env
DATABASE_URL=postgresql://...
API_KEY=xxx
JWT_SECRET=xxx
```

**Optional Environment Variables**:
```env
REDIS_URL=redis://...
SENTRY_DSN=...
```

---

## Development Workflow

**Setup Instructions**:
1. Clone repository
2. Install dependencies
3. Configure environment
4. Run migrations
5. Start development server

**Common Commands**:
```bash
npm install
npm run dev
npm run build
npm test
```

---

## Insights for Future Development

**Strengths**:
- [What the project does well]

**Potential Improvements**:
- [Areas that could be enhanced]

**Missing Features**:
- [Features that could be added]

**Technical Debt**:
- [Technical debt items identified]

---

## 🤖 Insights for AI-Powered Module & Task Generation

> **CRITICAL SECTION**: This section is used by AI to automatically generate new modules and break down tasks. Be extremely specific and detailed.

### Module Generation Guidelines

**IMPORTANT**: Analyze the ACTUAL codebase structure. Don't assume patterns - discover them from the code.

**Step 1: Identify Project Type**
First, detect what type of project this is:
- Web Backend (REST API, GraphQL, gRPC)
- Web Frontend (React, Vue, Angular, etc.)
- Full-stack (Both frontend + backend)
- CLI Tool
- Library/Package
- Mobile App
- Microservice
- Data Pipeline
- Monorepo (multiple projects)

**Step 2: Discover Module Patterns**

Analyze how modules are ACTUALLY organized in this project. Look for:

**Pattern 1: [Discovered Pattern Name]**
```
[Actual structure found in codebase]

Example from this project:
feature_name/
├── [file1.ext]          # [What it does]
├── [file2.ext]          # [What it does]
├── [file3.ext]          # [What it does]
└── [subfolder]/         # [What it contains]
    ├── [file.ext]
    └── [file.ext]

Key characteristics:
- File naming convention: [Actual convention used]
- Organization principle: [By feature / By type / By layer]
- Dependencies pattern: [How files import each other]
- Size range: [Typical file sizes in lines]
```

**Pattern 2: [Another Pattern if different modules use different patterns]**
```
[Second pattern structure]
```

**Common Elements Across All Modules**:
- Required files: [List files that every module has]
- Optional files: [List files that some modules have]
- Shared utilities: [Location of shared code]
- Configuration: [How modules are configured]

**Boilerplate Template for New Module**:
```[language]
# Extract ACTUAL code template from existing modules
# Include real imports, class/function signatures, patterns

[Paste actual boilerplate code from 2-3 similar modules]

Key patterns to follow:
1. [Pattern 1 from actual code]
2. [Pattern 2 from actual code]
3. [Pattern 3 from actual code]
```

**Module Dependencies & Communication**:

Analyze how modules interact:
- **Inter-module communication**: [Direct imports / Event bus / API calls / Message queue]
- **Dependency injection**: [Pattern used: Constructor injection / Setter injection / Global instance / None]
- **Shared resources**: [Database / Cache / Config / File system]
- **Error propagation**: [How errors bubble up between modules]

Example from this project:
```[language]
[Show actual code example of how Module A uses Module B]
```

**Naming Conventions** (Extract from ACTUAL code):

Analyze 5-10 existing files and identify the consistent patterns:

- **File/Module names**: [Examples: `user_service.py`, `UserService.ts`, `user-service.js`]
- **Class names**: [Examples: `UserService`, `UserRepository`, `UserController`]
- **Function/Method names**: [Examples: `get_user_by_id()`, `getUserById()`, `GetUserByID()`]
- **Variable names**: [Examples: `user_data`, `userData`, `UserData`]
- **Constants**: [Examples: `MAX_RETRY_COUNT`, `maxRetryCount`, `MaxRetryCount`]
- **Private members**: [Examples: `_internal_method()`, `#privateField`, `__private`]

**Project-Specific Conventions**:
- [Convention 1 unique to this project]
- [Convention 2 unique to this project]

**Registration/Integration Pattern**:

How new modules are integrated into the system:
```[language]
[Show actual code for how modules are registered]

Example locations:
- Main entry point: [file path]
- Router registration: [file path and code]
- Dependency container: [file path and code]
- Configuration: [file path and code]
```

**Testing Pattern** (if tests exist):

Analyze test structure:
```
[Actual test directory structure]

Test file naming: [Pattern from actual tests]
Test class/function naming: [Pattern from actual tests]
Fixtures/Mocks location: [Where they are]
Setup/Teardown pattern: [How it's done]

Example test structure:
[Paste actual test code showing the pattern]
```

If no tests: [Recommend testing pattern based on project type]

### Task Generation Guidelines

**IMPORTANT**: Tasks must be concrete, actionable, and specific to THIS project's patterns.

**Task Complexity Classification**:

Analyze existing commits/changes to understand complexity levels in THIS project:

**Simple Tasks** (1-3 hours) - Examples from this codebase:
- [List 3-5 actual simple changes made in this project]
- Pattern: [What makes a task simple in this project]

**Medium Tasks** (4-8 hours) - Examples from this codebase:
- [List 3-5 actual medium changes made in this project]
- Pattern: [What makes a task medium in this project]

**Complex Tasks** (1-3 days) - Examples from this codebase:
- [List 3-5 actual complex changes made in this project]
- Pattern: [What makes a task complex in this project]

**Task Breakdown Template**:

Use this structure for generating tasks:

```markdown
## Task: [Action Verb] [Specific Entity/Feature]

**Context**: [Why this task is needed - business value]

**Type**: [Choose based on project type]
- API Development: Create/Update/Delete endpoint
- UI Development: Create/Update component
- Data Processing: Create pipeline/transformer
- Integration: Connect to external service
- Refactoring: Improve existing code
- Bug Fix: Fix specific issue
- Testing: Add test coverage
- Documentation: Update docs

**Complexity**: [Simple / Medium / Complex] ([X] hours estimated)

**Module/Area**: [Which part of codebase - be specific]

### Implementation Details

**Files to Create**:
```
path/to/new_file.ext (XXX lines estimated)
├── Purpose: [Specific purpose]
├── Responsibilities: [What this file will do]
├── Dependencies: [What it needs to import]
└── Exports: [What other files will import from this]
```

**Files to Modify**:
```
1. path/to/existing_file.ext
   Location: [Function/Class name, approximate line number if possible]
   Change: [Specific change to make]
   Reason: [Why this change is needed]

2. path/to/another_file.ext
   [Same structure]
```

**Dependencies**:
- **Internal**: [List modules/files within project]
- **External**: [List new packages needed - with versions if possible]
- **Configuration**: [New env vars, config files needed]
- **Database**: [Migrations, schema changes needed]
- **Infrastructure**: [API keys, services, permissions needed]

**Data Model Changes** (if applicable):
```[language]
[Show specific schema/model changes needed]

For SQL:
-- Migration: descriptive_name.sql
CREATE TABLE ... / ALTER TABLE ...

For NoSQL:
[Document structure changes]

For Code:
[Class/Interface definition]
```

**API Changes** (if applicable):
```
New Endpoints:
- [METHOD] /path/to/endpoint
  Request: [Schema]
  Response: [Schema]
  Auth: [Required/Optional]

Modified Endpoints:
- [METHOD] /path/to/endpoint
  Changes: [What's different]
```

**Acceptance Criteria**:
Use project-specific criteria:
- [ ] [Criterion 1 specific to this project's quality standards]
- [ ] [Criterion 2 specific to this project's quality standards]
- [ ] [Criterion 3 specific to this project's quality standards]
- [ ] [Testing requirements based on project's test coverage goals]
- [ ] [Documentation requirements based on project's docs standards]
- [ ] [Code review requirements based on project's review process]

**Testing Requirements**:

Based on project's testing approach:
```
Test files to create/update:
- tests/path/to/test_file.ext

Test cases needed:
1. Happy path: [Describe expected behavior]
2. Edge case: [Specific edge case for this feature]
3. Error handling: [Specific errors to test]
4. Integration: [How this integrates with other modules]

Mock/Stub requirements:
- [What needs to be mocked and why]
```

**Implementation Order** (Specific to this project's workflow):
1. [Step 1 - following project's development process]
2. [Step 2 - following project's development process]
3. [Step 3 - following project's development process]
...

**Rollback Plan** (if complex):
- [How to undo this change if it breaks]
- [What to monitor after deployment]
```

**Task Chaining** (if task is part of larger feature):
```
Related tasks:
- Prerequisite: [Task that must be done first]
- Follow-up: [Tasks that should come after]
- Parallel: [Tasks that can be done simultaneously]
```

### Reusable Components Identified

**IMPORTANT**: Only list components that ACTUALLY exist and can be extracted.

**Highly Reusable Components** (90%+ reusability):

For each component, provide:
- **Component Name**: [Actual name from code]
- **Location**: [Exact file path]
- **Current Usage**: [Where it's used - list 3-5 places]
- **Why It's Reusable**: [Specific reason - generic, well-abstracted, no hard dependencies]
- **How to Extract**: [Concrete steps to make it a standalone module/package]
- **Dependencies**: [What it needs to function]
- **Example Usage**:
```[language]
[Show actual code example from current usage]
```

Example:
```
Component: Authentication Middleware
Location: src/middleware/auth.py
Usage: Used in 15 API endpoints across 5 modules
Reusability: 95% - Generic JWT validation, no project-specific logic
Extract: Can be published as standalone package with 2-3 hours work
Dependencies: jwt library only
```

**Moderately Reusable Components** (70-90%):
[Same structure as above]

**Project-Specific Components** (< 70%):
[List components that are too specific to extract, and explain why]

### Code Generation Best Practices

**From Analyzing This Codebase**:

**DO** (Patterns that work well in this project):
1. [Pattern 1 with example from code]
2. [Pattern 2 with example from code]
3. [Pattern 3 with example from code]

**DON'T** (Anti-patterns found - AI should avoid):
1. [Anti-pattern 1 with example and what to do instead]
2. [Anti-pattern 2 with example and what to do instead]
3. [Anti-pattern 3 with example and what to do instead]

**Code Quality Standards** (Derived from actual code):
- **Function length**: [Median: XX lines, Max observed: YY lines]
- **File length**: [Median: XX lines, Max observed: YY lines]
- **Complexity**: [Patterns observed for keeping complexity low]
- **Type annotations**: [Required / Optional / Not used]
- **Documentation**: [Format used - Docstrings / JSDoc / Comments / None]
- **Error handling**: [Pattern used in 80%+ of code]
- **Logging**: [Where and how logging is used]

**Consistency Checklist for Generated Code**:
- [ ] Follows the [discovered naming convention]
- [ ] Uses same import style as rest of codebase
- [ ] Error handling matches project pattern
- [ ] Logging follows project format
- [ ] File organization matches module pattern
- [ ] Documentation style matches existing docs
- [ ] Testing approach matches existing tests

### Gaps & Opportunities for New Modules

**Missing Features** (ranked by priority):
1. **[Feature Name]** - Priority: High
   - Why needed: [Business value]
   - Complexity: Medium
   - Dependencies: [List]
   - Estimated effort: 3 days
   - Module pattern to use: [Pattern X from above]

2. **[Feature Name]** - Priority: Medium
   [Same structure]

**Incomplete Implementations**:
- `module_name.py`: Missing error handling in lines 45-67
- `another_module.py`: TODO comments indicate incomplete feature
- Database: Missing indexes on frequently queried columns

**Technical Debt to Address**:
1. **[Debt Item]**: 
   - Impact: High/Medium/Low
   - Effort to fix: [Hours/Days]
   - Risk if not fixed: [Description]
   - Suggested approach: [How to fix]

### Integration Patterns

**How to Add New External Service**:
```python
# Pattern found in existing integrations:
1. Create service/integration/service_name.py
2. Add API client initialization
3. Create wrapper methods for API calls
4. Add error handling and retries
5. Register in dependency injection
6. Add configuration to .env
```

**How to Add New Database Table**:
```python
# Pattern from existing migrations:
1. Create migration file: migrations/XXX_add_table.sql
2. Define model in models/table_name.py
3. Create Pydantic schema in schemas/table_name.py
4. Add repository methods if needed
5. Update alembic revision (if using Alembic)
```

---

REPOSITORY CONTENT:
{packed_content}

---

**IMPORTANT**: Provide a thorough analysis. Extract ALL modules, features, API endpoints, and database tables. Be specific with file paths and code patterns. This analysis will be used to understand the entire project structure.
"""
        return prompt
    
    def _analyze_with_claude(self, repo_name: str, packed_content: str) -> str:
        """
        Analyze repository with Claude AI
        Returns markdown analysis
        """
        prompt = self._get_analysis_prompt(repo_name, packed_content)
        
        # Call Claude API
        response = self.anthropic_client.messages.create(
            model=self.settings.CLAUDE_MODEL,
            max_tokens=8000,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content[0].text
    
    async def analyze_repository(
        self,
        git_url: str,
        project_id: str,
        access_token: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Main method: Analyze Git repository and save to project_documents
        
        Args:
            git_url: Git repository URL
            project_id: Project ID to save analysis to
            access_token: GitHub access token for private repos
        
        Returns:
            {
                "git_url": "https://github.com/user/repo",
                "repo_name": "repo",
                "owner": "user",
                "analysis_markdown": "# Full Analysis...",
                "status": "completed",
                "document_id": "uuid-of-saved-document"
            }
        """
        try:
            # 1. Validate URL
            self._validate_git_url(git_url)
            
            # 2. Extract repo info
            owner, repo_name = self._extract_repo_info(git_url)
            
            # 3. Run Repomix
            packed_content = self._run_repomix(git_url, access_token)
            
            # 4. Analyze with Claude
            analysis_markdown = self._analyze_with_claude(repo_name, packed_content)
            
            # 5. Save to database
            document_id = None
            if self.db:
                try:
                    filename = f"{repo_name}_analysis.md"
                    data = {
                        "project_id": project_id,
                        "filename": filename,
                        "file_type": "markdown",
                        "content": analysis_markdown,
                        "file_size": len(analysis_markdown.encode('utf-8')),
                        "metadata": {
                            "from_git_analyzer": True,  # Mark as git analysis
                            "git_url": git_url,
                            "repo_name": repo_name,
                            "owner": owner
                        }
                    }
                    response = self.db.table("project_documents").insert(data).execute()
                    if response.data:
                        document_id = response.data[0].get("id")
                        print(f"[DEBUG] Saved to project_documents: {document_id}")
                except Exception as e:
                    print(f"[WARNING] Failed to save to database: {e}")
            
            # 6. Return result
            return {
                "git_url": git_url,
                "repo_name": repo_name,
                "owner": owner,
                "analysis_markdown": analysis_markdown,
                "status": "completed",
                "document_id": document_id
            }
            
        except Exception as e:
            return {
                "git_url": git_url,
                "repo_name": "",
                "owner": "",
                "analysis_markdown": "",
                "status": "failed",
                "error": str(e)
            }
        finally:
            self._cleanup()
