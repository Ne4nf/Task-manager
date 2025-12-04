"""
Task generation prompts for Claude AI
"""

TASK_GENERATION_PROMPT = """You are an expert project manager and software engineer tasked with breaking down a software module into specific, actionable tasks.

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

Analyze this module and generate a comprehensive list of tasks that need to be completed to implement it. For each task, provide:

1. **name**: Clear, actionable task name starting with a verb (e.g., "Create user login API endpoint", "Design database schema")
2. **description**: Detailed description including acceptance criteria and implementation notes (2-4 sentences)
3. **priority**: One of: "low", "medium", "high" (based on dependencies and importance)
4. **difficulty**: Integer 1-5 where:
   - 1 = Easy (junior dev, < 2 hours)
   - 2 = Medium (mid-level dev, 2-4 hours)
   - 3 = Hard (senior dev, 4-8 hours)
   - 5 = Expert (architect level, > 8 hours or complex)
5. **time_estimate**: Estimated hours to complete (decimal, e.g., 2.5)
6. **quality_score**: Expected quality level 1-5 (default to 3 for good quality)
7. **autonomy**: Independence level 1-4:
   - 1 = A1 Guided (needs constant supervision)
   - 2 = A2 Supervised (needs periodic check-ins)
   - 3 = A3 Independent (can work alone)
   - 4 = A4 Autonomous (fully self-directed)
8. **assignee**: Leave empty (will be assigned later)

Requirements:
- Generate 8-15 tasks per module (depending on complexity)
- Tasks should be granular and completable within 1-8 hours each
- Order tasks logically (dependencies first)
- Include setup, implementation, testing, and documentation tasks
- Be specific and actionable

Output Format:
Return ONLY a valid JSON array of task objects. Each object must have these exact keys:
- name (string)
- description (string)
- priority (string: "low" | "medium" | "high")
- difficulty (integer: 1-5)
- time_estimate (number)
- quality_score (integer: 1-5)
- autonomy (integer: 1-4)
- assignee (string: empty)

Example:
```json
[
  {{
    "name": "Design database schema for users table",
    "description": "Create PostgreSQL schema with fields: id (UUID), email, password_hash, full_name, avatar_url, created_at, updated_at. Include unique constraint on email and indexes on email. Document schema with comments.",
    "priority": "high",
    "difficulty": 2,
    "time_estimate": 2.0,
    "quality_score": 4,
    "autonomy": 3,
    "assignee": ""
  }},
  {{
    "name": "Implement user registration API endpoint",
    "description": "Create POST /auth/signup endpoint that validates email format, checks for duplicates, hashes password with bcrypt, stores user in database, and returns JWT token. Include input validation and error handling for all edge cases.",
    "priority": "high",
    "difficulty": 3,
    "time_estimate": 4.0,
    "quality_score": 4,
    "autonomy": 3,
    "assignee": ""
  }}
]
```

Now generate tasks for this module:"""


def create_task_generation_prompt(module_data: dict) -> str:
    """Create the prompt for task generation"""
    return TASK_GENERATION_PROMPT.format(
        module_name=module_data.get('name', ''),
        module_description=module_data.get('description', ''),
        scope=module_data.get('scope', 'Not specified'),
        features=module_data.get('features', 'Not specified'),
        requirements=module_data.get('requirements', 'Not specified'),
        technical_specs=module_data.get('technical_specs', 'Not specified')
    )
