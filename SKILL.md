# Project Analyzer & Documentation Generator

This skill analyzes any software project codebase (web apps, mobile apps, CLI tools, libraries, data pipelines, etc.) and generates comprehensive documentation including project summary, core features/modules, system design, architecture, and project structure. The output provides valuable insights for automatic module generation and task generation.

## When to Use This Skill

- Starting work on an existing project (any type)
- Onboarding new developers to a codebase
- Planning new features or modules
- Understanding project architecture and design patterns
- Preparing for automatic code generation
- Creating project documentation
- Analyzing technical stack and dependencies
- Understanding incomplete or partial projects
- Analyzing single-component projects (frontend-only, backend-only, CLI, library, etc.)

## What This Skill Does

1. **Detects Project Type**: Automatically identifies project type (web app, mobile, CLI, library, microservice, etc.)
2. **Scans Entire Project**: Recursively reads all relevant files based on project type
3. **Analyzes Code Structure**: Identifies modules, components, services, and their relationships
4. **Extracts Core Features**: Maps out main functionalities and business logic
5. **Documents System Design**: Describes architecture patterns, data flow, and integrations
6. **Identifies Tech Stack**: Lists frameworks, libraries, and technologies used
7. **Maps Dependencies**: Shows how different parts of the system interact
8. **Generates Insights**: Provides actionable information for module and task generation
9. **Creates New Markdown File**: Outputs comprehensive documentation in a new markdown file with timestamp

## How to Use

### Basic Analysis

```
Analyze this project and generate a comprehensive summary
```

```
Read all files in the project and document the architecture
```

### Focused Analysis

```
Analyze the backend structure and document all API endpoints and services
```

```
Map out the frontend components and their data flow
```

### Full Documentation

```
Generate complete project documentation including:
- Project summary
- Core features and modules
- System architecture
- Technology stack
- Database schema
- API structure
- Component hierarchy
```

## Analysis Process

### Step 0: Detect Project Type

**Automatic Detection Based on Files Present**:

```
If has package.json + src/components → React/Vue/Angular Frontend
If has requirements.txt + app/main.py → Python Backend
If has pom.xml or build.gradle → Java/Kotlin Backend
If has Cargo.toml → Rust Project
If has go.mod → Go Project
If has setup.py or pyproject.toml → Python Library/Package
If has bin/ or cli/ → CLI Tool
If has Dockerfile only → Microservice/Container
If has .ipynb files → Data Science/Jupyter Project
If has package.json + "type": "module" → Node.js Backend/Library
If has mobile/ or android/ or ios/ → Mobile App
If has both frontend/ and backend/ → Full-stack Web App
If has lambda/ or functions/ → Serverless Functions
```

**Set Analysis Strategy Based on Type**:
- Full-stack: Analyze both frontend and backend
- Frontend-only: Focus on components, routing, state management
- Backend-only: Focus on API, services, data layer
- CLI: Focus on commands, arguments, utilities
- Library: Focus on public API, modules, exports
- Data Science: Focus on notebooks, data processing, models
- Mobile: Focus on screens, navigation, platform-specific code

### Step 1: Project Discovery

**Configuration Files** (Read based on detected type):
- `package.json`, `requirements.txt`, `composer.json`, `Cargo.toml`, `go.mod`, `pom.xml`, etc.
- Identify dependencies and tech stack
- Note build tools and scripts

**Documentation Files**:
- Review `README.md`, `API_KEYS_GUIDE.md`, `CONTRIBUTING.md`, `docs/`
- Check for existing documentation
- Understand project purpose and setup instructions

**Project Metadata**:
- License file
- Version information
- Author and contributors
- Repository structure

### Step 2: Code Structure Analysis (Adaptive)

**For Web Backend** (if detected):
```
Read API/Server files:
- API routes and endpoints
- Service layer logic
- Repository/Data access patterns
- Models and schemas
- Middleware and utilities
- Configuration files
```

**For Web Frontend** (if detected):
```
Read UI/Client files:
- Component structure
- Page components
- State management
- API client configuration
- Routing setup
- UI/UX patterns
- Styling approach
```

**For CLI Tools** (if detected):
```
Read command-line files:
- Main entry point
- Command definitions
- Argument parsing
- Core functionality
- Utilities and helpers
- Configuration management
```

**For Libraries/Packages** (if detected):
```
Read library files:
- Public API/Exports
- Module structure
- Core functionality
- Utilities and helpers
- Types/Interfaces
- Documentation
```

**For Data Science Projects** (if detected):
```
Read data files:
- Jupyter notebooks
- Data processing scripts
- Model definitions
- Training pipelines
- Analysis notebooks
- Utility functions
```

**For Mobile Apps** (if detected):
```
Read mobile files:
- Screen/View components
- Navigation structure
- State management
- API integration
- Platform-specific code (iOS/Android)
- Native modules
```

**For Microservices** (if detected):
```
Read service files:
- Service entry point
- API endpoints
- Message handlers
- Database connections
- External integrations
- Docker/K8s configs
```

**Database Analysis** (if applicable):
```
Read migration/schema files:
- Database schema
- Table relationships
- Indexes and constraints
- Data models
- ORM configurations
```

### Step 3: Feature Extraction

For each identified module/feature:
- **Name**: Clear feature name
- **Purpose**: What problem it solves
- **Components**: Files and functions involved
- **Dependencies**: What it relies on
- **API Endpoints**: Related routes (if applicable)
- **Database Tables**: Related data (if applicable)

### Step 4: System Design Documentation (Adaptive)

**Architecture Patterns** (based on project type):
- Monolithic vs Microservices
- MVC, MVVM, Clean Architecture, Hexagonal, etc.
- Layered architecture (API → Service → Repository)
- Component-based architecture (Frontend)
- Event-driven architecture
- Pipeline architecture (Data processing)

**Data Flow** (adapt to project):
```
Full-stack Web:
User → Frontend → API → Service Layer → Repository → Database
                    ↓
              External Services

CLI Tool:
User → CLI Parser → Command Handler → Core Logic → Output

Library:
Consumer → Public API → Internal Modules → Return Value

Mobile App:
User → UI → ViewModel/Controller → Service → API/Storage → Backend

Data Pipeline:
Data Source → Ingestion → Processing → Analysis → Output/Storage
```

**Integrations** (if any):
- Third-party APIs
- External services
- Authentication systems
- Cloud services
- Databases
- Message queues

### Step 5: Generate Insights

**For Module Generation**
- List of existing modules and their boundaries
- Common patterns used in the codebase
- Naming conventions
- Code organization structure
- Reusable components and utilities

**For Task Generation**
- Feature completion status
- Missing functionality
- Improvement opportunities
- Technical debt areas
- Testing coverage gaps

## Output Format

**IMPORTANT**: Create a NEW markdown file with the analysis results. Do NOT print to console.

**File Naming Convention**:
```
project-analysis-[project-name]-[YYYY-MM-DD-HHMMSS].md

Example:
project-analysis-code-memory-2025-12-03-143022.md
```

**File Location**: Save in the project root or in a `docs/` folder if it exists.

---

The analysis markdown file should follow this adaptive structure based on project type:

```markdown
# [Project Name] - Complete Analysis

> **Analysis Date**: [Date and Time]  
> **Project Type**: [Auto-detected type: Full-stack Web App / Frontend Only / Backend API / CLI Tool / Library / Mobile App / Data Pipeline / etc.]  
> **Analyzer Version**: 1.0

## Executive Summary
[2-3 paragraphs describing what this project does, its main purpose, target users, and key capabilities]

## Project Type & Scope

**Detected Type**: [e.g., Full-stack Web Application, Python CLI Tool, React Component Library, etc.]

**Components Present**:
- [✓/✗] Frontend
- [✓/✗] Backend API
- [✓/✗] Database
- [✓/✗] CLI Interface
- [✓/✗] Mobile App
- [✓/✗] Desktop App
- [✓/✗] Library/Package
- [✓/✗] Data Processing
- [✓/✗] Microservices

**Completeness Assessment**:
- Is this a complete project? [Yes/No/Partial]
- Missing components (if any): [List]
- Development stage: [Prototype/In Development/Production/Archived]

## Technology Stack

### [Component Name] (e.g., Backend API, Frontend, CLI, etc.)
- **Language**: [e.g., Python 3.11, TypeScript, Rust, Go]
- **Framework**: [e.g., FastAPI, React, Typer, None]
- **Key Libraries**: [List main dependencies with versions]
- **Build Tools**: [e.g., Vite, Webpack, Poetry, Cargo]

### [Another Component if exists]
[Same structure]

### Infrastructure (if applicable)
- **Hosting**: [e.g., Vercel, AWS, Self-hosted, N/A]
- **Database**: [e.g., PostgreSQL via Supabase, MongoDB, SQLite, None]
- **External Services**: [List integrations or "None"]
- **CI/CD**: [GitHub Actions, GitLab CI, None]

## Project Structure

### Root Structure
```
[project-root]/
├── [folder1]/         # [Description]
├── [folder2]/         # [Description]
├── [config-file]      # [Description]
└── README.md
```

### [Main Component] Structure (e.g., Backend, Frontend, CLI, etc.)
```
[component-root]/
├── [subfolder1]/      # [Description]
├── [subfolder2]/      # [Description]
└── [files]            # [Description]
```

**Detailed Explanation**:
- **[Folder/File]**: [What it contains and its purpose]

## Core Features & Modules

> **Note**: Document actual features found, even if incomplete

### Feature/Module 1: [Feature Name]
**Purpose**: [What it does]  
**Status**: [✓ Complete / ⚠️ Partial / ✗ Not Implemented / 🚧 In Progress]  
**Location**: [File paths]

**Key Components**:
- Component 1: [Description and file location]
- Component 2: [Description and file location]

**API Endpoints** (if applicable):
- `GET /api/[endpoint]` - [Description]
- `POST /api/[endpoint]` - [Description]

**CLI Commands** (if applicable):
- `command-name [args]` - [Description]

**Public API** (if library):
- `function_name()` - [Description]

**Database Tables** (if applicable):
- `table_name`: [Description and key fields]

**Dependencies**:
- Internal: [Other modules it depends on]
- External: [External services/libraries]

**Data Flow**:
[Explain how data flows through this module]

**Implementation Notes**:
- [Any important details, patterns, or quirks]

### Feature/Module 2: [Feature Name]
[Same structure as above]

## System Architecture

### Overall Architecture Pattern
**Type**: [e.g., Layered Monolith, Microservices, Component-Based, Pipeline, etc.]

**Description**: [Explain the high-level architecture in 2-3 sentences]

**Key Characteristics**:
- [Characteristic 1]
- [Characteristic 2]

### [Layer/Component 1] (Adapt based on project type)

**For Web API**:
**Endpoints Structure**:
- `/api/v1/[resource]` - [Description]
- `/api/v1/[resource]` - [Description]

**Authentication & Authorization**:
[Describe how auth is handled or "Not implemented"]

**For CLI**:
**Commands Structure**:
- `main-command subcommand` - [Description]
- Arguments and flags: [List]

**For Library**:
**Public API Surface**:
- Exported functions: [List]
- Exported classes: [List]
- Main modules: [List]

**For Frontend**:
**Component Hierarchy**:
- Top-level: [Components]
- Pages: [List]
- Shared Components: [List]

### [Layer/Component 2]
[Continue adapting to project structure]

### Data Layer (if applicable)

**Database Type**: [SQL/NoSQL/File-based/None]

**Schema Overview**:
```sql
-- Key tables and relationships (if applicable)
-- Or data structures used
```

**Data Access Pattern**: [e.g., Repository Pattern, Direct Access, ORM, etc.]

### External Integrations (if any)

**Integration 1: [Service Name]**
- **Purpose**: [Why it's integrated]
- **Implementation**: [Where/how it's used]
- **Configuration**: [Required settings or "See .env.example"]
- **Status**: [Active/Inactive/Partial]

## Code Patterns & Conventions

### Naming Conventions
- **Files**: [e.g., snake_case.py, kebab-case.ts, PascalCase.tsx]
- **Functions**: [e.g., camelCase, snake_case]
- **Classes**: [e.g., PascalCase]
- **Constants**: [e.g., UPPER_SNAKE_CASE, SCREAMING_SNAKE_CASE]
- **Variables**: [e.g., camelCase, snake_case]

### Code Organization
- **Pattern 1**: [e.g., "Features organized by domain, not by type"]
- **Pattern 2**: [e.g., "Each module exports a single public interface"]
- **File Structure**: [e.g., "One class per file", "Grouped by functionality"]

### Error Handling
[Describe the error handling strategy or "Inconsistent/Not standardized"]

### Logging & Monitoring
[Describe logging approach or "No logging implemented"]

### Testing
- **Framework**: [e.g., pytest, Jest, None]
- **Coverage**: [High/Medium/Low/None]
- **Location**: [Where tests are located]

## Configuration & Environment

### Environment Variables (if applicable)
```
REQUIRED:
- [VAR_NAME]: [Description]
- [VAR_NAME]: [Description]

OPTIONAL:
- [VAR_NAME]: [Description]
```

**Configuration Method**: [.env file, config.py, environment-specific files, hardcoded, etc.]

### Configuration Files
- `[config-file]`: [Purpose and key settings]
- `[config-file]`: [Purpose and key settings]

### Build Configuration
- `[build-file]`: [Purpose - e.g., "Vite config for dev server and build"]

## Data Models & Schemas (if applicable)

### [Backend/Library] Models
```[language]
[Example model/class definition]
```

### [Frontend] Types (if TypeScript)
```typescript
[Example interface/type definition]
```

## API Documentation (if applicable)

### [Resource] API
**[METHOD] /path/to/endpoint**
- **Purpose**: [Description]
- **Request**: [Parameters, body schema]
- **Response**: [Response schema]
- **Auth Required**: [Yes/No]
- **Status**: [Implemented/Mock/Not Implemented]

[Document all endpoints found]

## CLI Documentation (if applicable)

### Available Commands
**`command-name [options]`**
- **Purpose**: [Description]
- **Arguments**: [List]
- **Options/Flags**: [List]
- **Examples**: 
  ```bash
  command-name --option value
  ```

## Public API Documentation (if library)

### Exports
**`function_name(param: Type): ReturnType`**
- **Purpose**: [Description]
- **Parameters**: [Describe each parameter]
- **Returns**: [Describe return value]
- **Example**:
  ```[language]
  [Usage example]
  ```

## Insights for Automatic Generation

### Module Generation Guidelines

**Existing Module Patterns Identified**:

[Adapt based on actual project structure found]

```
Pattern 1: [Description of how modules are structured]
Example: Each feature has:
  - [Component 1 location]
  - [Component 2 location]
  - [etc.]

Pattern 2: [Another pattern if found]
```

**Recommended Structure for New Modules**:
```
New Module: [ModuleName]
1. [Step 1 based on existing pattern]
2. [Step 2 based on existing pattern]
3. [etc.]
```

**Naming Conventions to Follow**:
- [Convention 1]
- [Convention 2]

**Boilerplate Code Template**:
```[language]
[Provide a template based on existing code patterns]
```

### Task Generation Guidelines

**Common Task Types Identified**:
1. **[Task Type]**: [Description and examples from codebase]
2. **[Task Type]**: [Description and examples from codebase]

**Task Complexity Levels**:
- **Simple**: [Examples: "Add new field to model", "Create new utility function"]
- **Medium**: [Examples: "Add new API endpoint", "Create new page component"]
- **Complex**: [Examples: "Add new feature module", "Integrate new service"]

**Task Template Based on Project**:
```
Task: [Action] [Entity/Feature]
Type: [Task type from above]
Complexity: [Simple/Medium/Complex]
Module: [Related module if applicable]
Files to Create/Modify:
- [File 1]: [What to add/change]
- [File 2]: [What to add/change]
Dependencies:
- [Dependency 1]
- [Dependency 2]
Acceptance Criteria:
- [Criteria 1]
- [Criteria 2]
Testing Requirements:
- [Test requirement 1]
```

### Identified Gaps & Opportunities

**Missing Features** (based on typical projects of this type):
- [Feature 1]: [Why it would be valuable]
- [Feature 2]: [Why it would be valuable]

**Incomplete Implementations**:
- [Feature/Module]: [What's missing or incomplete]

**Improvement Areas**:
- [Area 1]: [Suggestion with specific recommendation]
- [Area 2]: [Suggestion with specific recommendation]

**Technical Debt**:
- [Issue 1]: [Description and potential impact]
- [Issue 2]: [Description and potential impact]

**Testing Gaps**:
- [Gap 1]: [What tests are missing]
- [Gap 2]: [What tests are missing]

**Documentation Gaps**:
- [Gap 1]: [What documentation is missing]

## Dependencies Map

### [Component] Dependencies
```
[Entry point file]
├── [Dependency 1]
│   ├── [Sub-dependency 1]
│   └── [Sub-dependency 2]
├── [Dependency 2]
└── [Dependency 3]
```

**External Dependencies**:
- [Package 1] (v[version]): [Purpose in project]
- [Package 2] (v[version]): [Purpose in project]

**Internal Dependencies**:
- [Module A] depends on [Module B] for [reason]
- [Module C] depends on [Module D] for [reason]

## Development Workflow

### Setup Instructions
> Based on README.md and configuration files

1. [Step 1]
2. [Step 2]
3. [Step 3]

**Prerequisites**:
- [Requirement 1]
- [Requirement 2]

### Build Process
**Command**: `[build command]`
**Output**: [What gets generated]
**Time**: [Approximate time if known]

### Development Process
**Dev Server**: `[dev command]` (if applicable)
**Watch Mode**: `[watch command]` (if applicable)
**Hot Reload**: [Yes/No/Partial]

### Testing Strategy
**Run Tests**: `[test command]`
**Test Location**: [Where tests are]
**Coverage**: [How to check coverage if applicable]

### Deployment
**Method**: [How the application is deployed or "Not configured"]
**Target**: [Where it's deployed to or "Not specified"]
**CI/CD**: [Automated/Manual/Not configured]

## Recommendations

### For Module Generation
> Based on actual patterns found in this project

1. [Recommendation 1 based on existing code]
2. [Recommendation 2 based on existing code]
3. [Recommendation 3 based on existing code]

### For Task Generation
> Based on project structure and gaps identified

1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

### For Code Quality
1. [Suggestion 1]
2. [Suggestion 2]

### For Project Improvement
1. [Improvement 1]: [Specific actionable suggestion]
2. [Improvement 2]: [Specific actionable suggestion]

## Appendix

### File Inventory
- **Total Files Analyzed**: [Count]
- **[Component] Files**: [Count]
- **Configuration Files**: [Count]
- **Documentation Files**: [Count]
- **Test Files**: [Count]

### Key Files Reference
- **Entry Point**: `[file path]`
- **Main Configuration**: `[file path]`
- **[Other important file]**: `[file path]`

### Technology Versions
- **[Language]**: [Version]
- **[Framework]**: [Version]
- **[Key Library]**: [Version]

### External Resources
- **Repository**: [URL if found]
- **Documentation**: [URL if found]
- **Issue Tracker**: [URL if found]

---

**Analysis Generated**: [Full timestamp]  
**Analyzer Version**: 1.0  
**Project Version**: [If available from package.json, etc.]  
**Files Analyzed**: [Number]  
**Analysis Duration**: [Approximate time taken]
```

---

## Template Adaptation Rules

**Adapt the output based on what's actually found**:

1. **Skip sections** that don't apply (e.g., no API documentation for a CLI tool)
2. **Add sections** for project-specific needs (e.g., "Data Processing Pipelines" for data science projects)
3. **Rename sections** to match project terminology (e.g., "Screens" instead of "Pages" for mobile apps)
4. **Focus depth** on the main components (more detail for what exists, less for what doesn't)
5. **Be honest** about gaps and incomplete areas - mark with ⚠️ or 🚧
6. **Provide context** - explain why something might be missing or incomplete

**Quality over Template Adherence**:
- It's better to have accurate, focused documentation than to force-fit a template
- If a section would be empty or full of "N/A", skip it
- Add sections that would be valuable for this specific project type

```markdown
# [Project Name] - Complete Analysis
```

## Best Practices

### Completeness
✓ Read ALL relevant code files (don't skip based on assumptions)
✓ Analyze ONLY components that actually exist
✓ Be honest about missing or incomplete parts
✓ Document all integrations found (not assumed)
✓ Map actual data flow (not theoretical)
✓ Include configuration details as they exist
✗ Don't assume a project has both frontend and backend
✗ Don't skip complex files
✗ Don't fill in sections with "N/A" - just omit them
✗ Don't guess at implementations you didn't see
✗ Don't force-fit the template to incomplete projects

### Accuracy
✓ Use actual code as the ONLY source of truth
✓ Verify relationships between components by reading imports
✓ Test understanding by tracing actual code paths
✓ Cross-reference multiple files to confirm patterns
✓ Note when something appears incomplete or unclear
✗ Don't make assumptions about missing code
✗ Don't guess at implementations
✗ Don't assume standard patterns if code shows otherwise
✗ Don't document features that don't exist yet

### Usefulness
✓ Focus on actionable insights for developers
✓ Highlight actual patterns found in the code
✓ Identify truly reusable components
✓ Note real improvement opportunities with specific suggestions
✓ Provide concrete examples from the actual codebase
✓ Mark incomplete/partial implementations clearly
✓ Suggest realistic next steps based on current state
✗ Don't just list files without explaining their purpose
✗ Don't provide surface-level descriptions
✗ Don't suggest features that don't fit the project scope
✗ Don't assume standard project structure if reality differs

### Adaptability
✓ Adapt documentation structure to match project type
✓ Use terminology that matches the project domain
✓ Focus on what exists, not what "should" exist
✓ Add project-specific sections as needed
✓ Skip template sections that don't apply
✓ Be flexible with depth - more for main features, less for utilities
✗ Don't rigidly follow the template
✗ Don't use web-app terminology for CLI tools
✗ Don't document theoretical features
✗ Don't create empty sections

## Advanced Features

### Dependency Graph Generation
```
Generate a visual dependency graph showing how all modules connect
```

### API Contract Documentation
```
Extract all API endpoints and generate OpenAPI/Swagger documentation
```

### Database ER Diagram
```
Analyze database schema and create entity relationship diagram
```

### Code Quality Analysis
```
Identify code smells, duplications, and improvement opportunities
```

### Security Analysis
```
Review authentication, authorization, and security practices
```

## Common Workflows

### New Developer Onboarding (Any Project Type)
1. Request project analysis with this skill
2. Read generated analysis markdown file
3. Understand project type and scope
4. Review core modules/features
5. Study code patterns and conventions
6. Check setup instructions
7. Start contributing

### Feature Planning (Any Project Type)
1. Analyze existing features and patterns
2. Identify similar implementations
3. Plan new module structure following existing conventions
4. Generate specific tasks
5. Implement following documented patterns

### Refactoring Preparation
1. Document current architecture
2. Identify problem areas and technical debt
3. Plan improvements with specific recommendations
4. Generate refactoring tasks
5. Execute systematically

### Code Review / Audit
1. Run complete analysis
2. Review architecture and patterns
3. Identify inconsistencies
4. Note security or quality concerns
5. Generate improvement tasks

### Legacy Project Understanding
1. Run analysis to get full picture
2. Map dependencies and data flow
3. Identify core vs. peripheral code
4. Document current state honestly
5. Plan modernization if needed

## Tips for Success

1. **Be Thorough But Smart**: Read every relevant file, but prioritize based on project type
2. **Follow the Code**: Let actual implementation guide documentation, not assumptions
3. **Think Holistically**: Consider all components together, not in isolation
4. **Document Patterns**: Note recurring designs and conventions you actually see
5. **Provide Real Examples**: Include code snippets from the actual project
6. **Be Specific**: Use exact file paths and line numbers when referencing
7. **Think Forward**: Document in a way that helps future development
8. **Update Regularly**: Re-run analysis as project evolves
9. **Be Honest**: Clearly mark incomplete, partial, or missing features
10. **Adapt the Template**: Don't force sections that don't apply
11. **Focus on Value**: Prioritize insights that help with module/task generation
12. **Cross-Reference**: Verify patterns by checking multiple examples

## Critical Instructions

### 1. File Creation
**ALWAYS create a new markdown file** for the analysis output:
- Filename format: `project-analysis-[name]-[timestamp].md`
- Location: Project root or `docs/` folder
- DO NOT just return text in the chat
- DO NOT overwrite existing files

### 2. Project Type Detection
**ALWAYS start by detecting project type**:
- Check what files/folders actually exist
- Don't assume it's a full-stack web app
- Adapt the entire analysis based on what you find

### 3. Template Flexibility
**ALWAYS adapt the output template**:
- Skip sections that don't apply
- Add sections for project-specific needs
- Use appropriate terminology for the project type
- Don't create empty sections with "N/A"

### 4. Accuracy Over Completeness
**ALWAYS prioritize accuracy**:
- Only document what you actually find in the code
- Mark incomplete features clearly (⚠️ Partial, 🚧 In Progress)
- Don't guess or assume implementations
- Be honest about gaps and missing pieces

### 5. Actionable Insights
**ALWAYS provide actionable insights**:
- Focus on information useful for generating modules/tasks
- Identify clear patterns from actual code
- Provide specific examples and templates
- Give concrete recommendations based on what exists

## Output Deliverables

**Primary Output**:
- **Analysis Markdown File**: `project-analysis-[name]-[timestamp].md` created in project root or docs/
  - Complete, structured documentation
  - Adapted to actual project type
  - Focused on actionable insights

**File Should Contain**:
- Project type and scope assessment
- Technology stack (what's actually used)
- Project structure (as it actually exists)
- Core features/modules (documented accurately)
- System architecture (based on actual code)
- Code patterns and conventions (from real examples)
- **Module generation guidelines** (based on existing patterns)
- **Task generation templates** (adapted to project)
- Identified gaps and opportunities (realistic suggestions)
- Dependencies map (actual relationships)

**Key Sections for Automation**:
- **"Insights for Automatic Generation"** - Critical for module/task gen
- **"Code Patterns & Conventions"** - For maintaining consistency
- **"Existing Module Patterns"** - Templates for new modules
- **"Task Generation Guidelines"** - How to break down work
- **"Identified Gaps & Opportunities"** - What to build next

## Related Use Cases

- Generating new feature modules automatically (using discovered patterns)
- Creating development tasks from requirements (using task templates)
- Code review and quality assessment
- Technical documentation maintenance
- Architecture decision records
- Developer onboarding materials
- Estimating development effort for new features
- Understanding inherited/legacy codebases
- Planning refactoring efforts
- Auditing project completeness
- Technology stack assessment
- Dependency analysis
- Pattern extraction for code generation
