"""
Module generation prompts for Claude AI
"""

MODULE_GENERATION_PROMPT = """You are an expert software architect tasked with breaking down a project into logical, well-defined modules.

Given the following project documentation:

<project_documentation>
{documentation}
</project_documentation>

Analyze this documentation and generate a comprehensive list of modules that should be implemented. For each module, provide:

1. **name**: A clear, concise module name (e.g., "User Authentication", "Payment Processing")
2. **description**: Brief description of what this module does (2-3 sentences)
3. **scope**: Detailed scope of responsibilities and boundaries
4. **dependencies**: List any dependencies on other modules or external systems
5. **features**: Key features this module will provide (bullet points)
6. **requirements**: Functional and non-functional requirements
7. **technical_specs**: Technical specifications, tech stack recommendations, APIs, etc.

Requirements:
- Generate between 5-12 modules depending on project complexity
- Each module should be focused and have clear boundaries
- Modules should be logically organized (e.g., Frontend, Backend, Database, Infrastructure, etc.)
- Consider both functional modules (e.g., User Management) and cross-cutting concerns (e.g., Logging, Authentication)
- Make modules practical and implementable

Output Format:
Return ONLY a valid JSON array of module objects. Each object must have these exact keys:
- name (string)
- description (string)
- scope (string)
- dependencies (string)
- features (string)
- requirements (string)
- technical_specs (string)

Example:
```json
[
  {{
    "name": "User Authentication",
    "description": "Handles user registration, login, password management, and session management using JWT tokens.",
    "scope": "Manages all user authentication flows including signup, login, logout, password reset, email verification, and token refresh. Does not include user profile management or authorization (handled by separate module).",
    "dependencies": "Database Module (user storage), Email Service (verification emails), Redis (session storage)",
    "features": "• JWT-based authentication\\n• Email/password login\\n• OAuth2 social login (Google, GitHub)\\n• Password reset flow\\n• Email verification\\n• Remember me functionality\\n• Session management",
    "requirements": "• Must support 10,000+ concurrent users\\n• Token expiry: 1 hour (access), 30 days (refresh)\\n• Password requirements: min 8 chars, uppercase, lowercase, number, special char\\n• Rate limiting: 5 failed attempts = 15 min lockout",
    "technical_specs": "• Tech Stack: Node.js, Express, JWT, bcrypt, Redis\\n• Database: PostgreSQL users table\\n• APIs: POST /auth/signup, POST /auth/login, POST /auth/refresh, POST /auth/reset-password\\n• Security: HTTPS only, secure httpOnly cookies, CORS configured"
  }}
]
```

Now generate modules for this project:"""


def create_module_generation_prompt(documentation: str) -> str:
    """Create the prompt for module generation"""
    return MODULE_GENERATION_PROMPT.format(documentation=documentation)
