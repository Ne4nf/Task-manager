"""
Task generation prompts for Claude AI
"""

TASK_GENERATION_PROMPT = """You are an expert agile project manager and senior software engineer tasked with breaking down a software module into specific, actionable, beginner-friendly tasks.

Your goal: Create tasks that a **junior developer** or **new team member** can pick up and understand immediately. Each task should be a clear "mini-project" with enough context to work independently.

Given the following module information:

<module_name>{module_name}</module_name>

<module_description>{module_description}</module_description>

<module_scope>{scope}</module_scope>

<module_features>
{features}
</module_features>

<module_requirements>
{requirements}
</module_requirements>

<module_technical_specs>
{technical_specs}
</module_technical_specs>

Analyze this module and generate a comprehensive list of tasks. For each task, provide:

1. **name**: Clear, actionable task name with context
   - Format: "[Category] Action + What + Context"
   - Examples: 
     * "✅ [Backend] Create user registration API with email validation"
     * "🎨 [Frontend] Design login form component with Tailwind"
     * "📝 [Docs] Write API documentation for authentication endpoints"
     * "🧪 [Test] Add unit tests for password hashing service"

2. **description**: Comprehensive task description in **markdown format** with clear sections.
   
   **CRITICAL**: Description MUST be a single-line JSON string with escaped newlines (\n).
   **KEEP IT CONCISE**: 80-120 words max per task to avoid token limit.
   
   **Structure (use \n for line breaks):**
   ```
   "## 🎯 Objective\n[1-2 sentences: what and why]\n\n## ✅ Acceptance Criteria\n- [ ] Deliverable 1\n- [ ] Deliverable 2\n- [ ] Deliverable 3\n\n## 🔧 Key Steps\n- File: path/to/file - what to do\n- Key tech detail or API to use"
   ```
   
   **JSON FORMATTING RULES (MANDATORY):**
   - Entire description is ONE string with NO literal line breaks
   - Use \n (backslash-n) for every line break
   - Use \t for tabs if needed
   - Escape double quotes as \"
   - Do NOT use triple backticks ``` anywhere
   - Use single backticks for inline code: `functionName()`
   - Write code examples on single lines without backtick blocks
   
   **Good example (concise, ~50 words):**
   ```
   "description": "## 🎯 Objective\nCreate agents table for Agent Management module.\n\n## ✅ Acceptance Criteria\n- [ ] UUID primary key\n- [ ] Required name field\n- [ ] Timestamps\n\n## 🔧 Key Steps\n- File: database/migrations/002_agents.sql\n- SQL: CREATE TABLE agents (id UUID, name VARCHAR(255) NOT NULL, created_at TIMESTAMP)"
   ```
   
   **Bad example (literal newlines break JSON):**
   ```
   "description": "Objective
   Create table
   
   File: agents.sql"
   ```

3. **priority**: One of: "low", "medium", "high"
   - **high**: Blocking other tasks, core functionality, security-critical
   - **medium**: Important but not blocking, enhances UX
   - **low**: Nice-to-have, optimizations, polish

4. **difficulty**: Integer 1-5 (calibrated for AI-assisted development)
   - **1 = Trivial**: Copy-paste, AI can generate 90%, <30min (e.g., "Add loading spinner")
   - **2 = Easy**: Simple logic, clear pattern, AI generates most code, 30min-1.5h (e.g., "Create CRUD endpoint")
   - **3 = Medium**: Understanding required, AI helps with boilerplate, 2-4 hours (e.g., "Implement auth middleware")
   - **4 = Hard**: Complex logic, multiple integrations, AI reduces debugging time, 4-6 hours (e.g., "Real-time sync system")
   - **5 = Expert**: Architectural design, novel algorithms, AI helps research, 6-8 hours (e.g., "Design distributed cache")
   
   💡 **AI Era Calibration**: Tasks that were difficulty 4 in 2020 are now difficulty 3 with GitHub Copilot/Claude assistance.

5. **time_estimate**: Realistic hours for **mid-level developer WITH AI assistance** (decimal, e.g., 2.5)
   - Assumes: GitHub Copilot, ChatGPT/Claude for debugging, AI code review
   - Traditional estimate × 0.6-0.7 (AI reduces time by 30-40%)
   - Include: coding, testing, debugging, documentation
   - Junior devs may need 1.3-1.5x this time

6. **quality_score**: Expected quality level 1-5 (AI doesn't change quality requirements)
   - **5**: Production-ready, fully tested, documented, all edge cases
   - **4**: High quality, tested, minor edge cases may be missing  
   - **3**: Good quality, basic tests, happy path works
   - **2**: Prototype quality, minimal testing
   - **1**: Proof of concept only

7. **autonomy**: Independence level 1-4 (adjusted for AI assistance era)
   - **1 = A1 Guided**: Pair programming, real-time mentoring (intern, first week)
   - **2 = A2 Supervised**: Daily check-ins, AI + senior help, 1-2 reviews/day (junior with <1 year)
   - **3 = A3 Independent**: AI as primary assistant, weekly check-ins, self-unblock (junior 1-2 years or mid-level)
   - **4 = A4 Autonomous**: Fully self-directed with AI, makes architectural decisions (mid-senior+)
   
   💡 **AI Era Shift**: Junior developers with AI assistance can often work at A3 autonomy (previously A2).

8. **assignee**: Leave empty "" (will be assigned later by PM)

Requirements:
- Generate **8-12 tasks** per module (focused, actionable work)
- **Logical ordering**: Setup → Core → Features → Tests → Docs → Polish
- Prefer **fewer, well-scoped tasks** over many tiny tasks
- Each task should be **completable in 0.5-6 hours** (AI-assisted time)
- Include diverse task types:
  * 🏗️ Setup/Infrastructure (15-20% of tasks)
  * 💻 Implementation (50-60% of tasks: APIs, services, UI)
  * 🧪 Testing (15-20% of tasks)
  * 📝 Documentation (5-10% of tasks)
  * 🔒 Security & Performance (occasional, critical tasks only)
- Be **specific with file paths, function names, endpoints**
- Use **markdown format** for descriptions (with emojis for visual scanning)
- Include **code snippets** when helpful
- Link to **docs/resources** for complex concepts

Output Format:
Return ONLY a valid JSON array of task objects. Each object must have these exact keys:
- name (string)
- description (string) - MUST be valid JSON string with escaped newlines
- priority (string: "low" | "medium" | "high")
- difficulty (integer: 1-5)
- time_estimate (number)
- quality_score (integer: 1-5)
- autonomy (integer: 1-4)
- assignee (string: always "")

⚠️ CRITICAL JSON FORMATTING REQUIREMENTS:
1. **NEVER** use literal line breaks in JSON strings - use \n instead
2. **NEVER** use triple backticks (```) anywhere in descriptions
3. **ALWAYS** escape newlines as \n (backslash-n)
4. **ALWAYS** escape double quotes as \" inside descriptions
5. Use single backticks for inline code only: `functionName()`
6. Write entire description as ONE string with \n for line breaks
7. Validate JSON syntax before returning

WRONG (will break JSON):
```json
{{
  "description": "Line 1
  Line 2"
}}
```

CORRECT (valid JSON):
```json
{{
  "description": "Line 1\nLine 2"
}}
```

Example (CORRECT JSON formatting with concise descriptions):
```json
[
  {{
    "name": "🏗️ [Setup] Create agents database table",
    "description": "## 🎯 Objective\nCreate agents table for storing AI agent configurations.\n\n## ✅ Acceptance Criteria\n- [ ] UUID primary key with gen_random_uuid()\n- [ ] Required name field (VARCHAR 255)\n- [ ] Foreign key to organizations with CASCADE\n- [ ] Indexes on org_id and name\n\n## 🔧 Key Steps\n- File: database/migrations/002_agents.sql\n- Schema: id, name, org_id, created_at, updated_at\n- Indexes for fast lookups",
    "priority": "high",
    "difficulty": 2,
    "time_estimate": 1.0,
    "quality_score": 5,
    "autonomy": 3,
    "assignee": ""
  }},
  {{
    "name": "💻 [Backend] POST /api/agents creation endpoint",
    "description": "## 🎯 Objective\nBuild API endpoint for creating new AI agents.\n\n## ✅ Acceptance Criteria\n- [ ] POST /api/agents accepts name, personality, instructions\n- [ ] Validates name (3-100 chars), returns 400 if invalid\n- [ ] Returns 201 with created agent object\n- [ ] Returns 409 for duplicate names\n- [ ] Requires JWT authentication\n\n## 🔧 Key Steps\n- Files: routes/agents.ts, controllers/agentController.ts\n- Validation: express-validator for input checks\n- Database: Parameterized INSERT with pg library\n- Error handling: Catch unique constraint violations",
    "priority": "high",
    "difficulty": 2,
    "time_estimate": 2.0,
    "quality_score": 4,
    "autonomy": 3,
    "assignee": ""
  }}
]
```

CRITICAL REQUIREMENTS:
- Generate EXACTLY 8-12 tasks (balanced workload, not overwhelming)
- Each description should be 50-80 words (concise but actionable)
- EVERY task MUST have ALL 8 fields: name, description, priority, difficulty, time_estimate, quality_score, autonomy, assignee
- DO NOT leave any field as null or empty (assignee should be "")
- Use ONLY escaped newlines (\n) in descriptions - NO literal line breaks

Now generate tasks for this module. Be specific with file paths and APIs, but keep descriptions brief:"""


def create_task_generation_prompt(module_data: dict) -> str:
    """Create the prompt for task generation"""
    # Use replace instead of format to avoid issues with curly braces in JSON examples
    # Handle None values by converting to 'Not specified'
    prompt = TASK_GENERATION_PROMPT.replace("{module_name}", module_data.get('name') or 'Unnamed Module')
    prompt = prompt.replace("{module_description}", module_data.get('description') or 'No description provided')
    prompt = prompt.replace("{scope}", module_data.get('scope') or 'Not specified')
    prompt = prompt.replace("{features}", module_data.get('features') or 'Not specified')
    prompt = prompt.replace("{requirements}", module_data.get('requirements') or 'Not specified')
    prompt = prompt.replace("{technical_specs}", module_data.get('technical_specs') or 'Not specified')
    return prompt
