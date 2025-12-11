"""
Module generation prompts for Claude AI - 2-Phase Approach
"""

# Phase 1: Generate module metadata (name, description, scope, dependencies)
MODULE_METADATA_PROMPT = """You are an expert software architect analyzing a project to identify its core modules.

Given this project documentation:

<project_documentation>
{documentation}
</project_documentation>

Analyze the "Core Features & Modules" section and identify the IMPLEMENTED core modules only.
DO NOT include modules from "Missing Features" or "Insights for Future Development" sections.

For each CORE module that is already implemented, provide:

1. **name**: Clear, descriptive module name (e.g., "User Authentication & Authorization")

2. **description**: 3-4 sentences explaining:
   - What this module does (functionality)
   - Why it's important (business value)
   - How it fits in the system (role)
   - Who uses it (users/other modules)

3. **scope**: Write in markdown format:
   ```
   ✅ **What IS included:**
   - Feature 1 - Brief explanation why
   - Feature 2 - Brief explanation why
   - Feature 3 - Brief explanation why
   
   ❌ **What is NOT included:**
   - Out of scope item 1
   - Out of scope item 2
   
   🔗 **Key Interactions:**
   - With Module A: How they interact
   - With Module B: How they interact
   ```

4. **dependencies**: Write in markdown format:
   ```
   **Internal Modules:** 
   - Module Name 1 - Why needed
   - Module Name 2 - Why needed
   
   **External APIs/Services:** 
   - Gmail API - For email sync
   - Stripe API - For payments
   
   **Infrastructure:** 
   - PostgreSQL - Stores user data
   - Redis - Caches session tokens
   
   **Key Libraries:** 
   - fiber/v3 - Web framework
   - golang-jwt - Token validation
   ```

Return ONLY a valid JSON array with these 4 fields per module.
IMPORTANT: scope and dependencies MUST be markdown-formatted strings, NOT JSON objects.

Example output:
[{{
  "name": "User Authentication",
  "description": "Manages user login, registration, and session handling. Critical for securing all API endpoints. Acts as the gatekeeper for the entire application. Used by all modules that need to verify user identity.",
  "scope": "✅ **What IS included:**\n- JWT token generation - Secure stateless auth\n- Password hashing - Protects credentials\n- Session management - Tracks logged-in users\n\n❌ **What is NOT included:**\n- User profile data\n- Authorization rules\n\n🔗 **Key Interactions:**\n- With API Gateway: Validates all requests\n- With User Management: Fetches user credentials",
  "dependencies": "**Internal Modules:**\n- User Management - Retrieves user data\n\n**External APIs/Services:**\n- None\n\n**Infrastructure:**\n- PostgreSQL - Stores sessions\n- Redis - Token blacklist\n\n**Key Libraries:**\n- golang-jwt/jwt - Token generation\n- bcrypt - Password hashing"
}}]

Keep description ~100 words, scope ~150 words, dependencies ~100 words."""  

# Phase 2: Generate detailed specifications for each module
MODULE_DETAILS_PROMPT = """You are a technical architect providing detailed implementation specs for a module.

<module_name>{module_name}</module_name>
<module_description>{module_description}</module_description>
<module_scope>{module_scope}</module_scope>
<module_dependencies>{module_dependencies}</module_dependencies>

<project_context>{documentation}</project_context>

Generate detailed specifications with these 3 fields in markdown format:

1. **features** (250-350 words):
🎯 **Core Features** (5-7 items):
• Feature name - What it does and why it matters

🔧 **Technical Features** (3-5 items):
• Technical capability - How it works internally

2. **requirements** (250-350 words):
📋 **Functional Requirements** (5-7 items)
⚡ **Performance Requirements** (3-4 items)
🔒 **Security Requirements** (3-5 items)
🧪 **Testing Requirements** (2-3 items)

3. **technical_specs** (300-400 words):
🏗️ **Architecture:** Pattern and components (3-4 lines)

💻 **Tech Stack:**
• Backend: Framework + version, language
• Database: Type + main tables
• Key Libraries: Top 3-5 with purpose

🔌 **Key APIs:** (2-3 endpoints)
• Method + Path - Purpose
  Request: Schema
  Response: Schema with status codes

💾 **Database Schema:** (2-4 tables)
• Table: key columns, indexes

🔐 **Security:** Auth + encryption (2-3 lines)

Return ONLY valid JSON with these 3 fields as markdown strings:
{{"features": "...", "requirements": "...", "technical_specs": "..." }}

CRITICAL: Keep each field concise (250-400 words). Use markdown with emojis. Be specific but brief.
"""  


def create_module_metadata_prompt(documentation: str) -> str:
    """Create prompt for Phase 1: Module metadata generation"""
    return MODULE_METADATA_PROMPT.replace("{documentation}", documentation)


def create_module_details_prompt(
    module_name: str,
    module_description: str, 
    module_scope: str,
    module_dependencies: str,
    documentation: str
) -> str:
    """Create prompt for Phase 2: Module details generation"""
    # Convert to string if needed (handle dict/list from Phase 1 JSON)
    module_name = str(module_name) if module_name else ""
    module_description = str(module_description) if module_description else ""
    module_scope = str(module_scope) if module_scope else ""
    module_dependencies = str(module_dependencies) if module_dependencies else ""
    
    prompt = MODULE_DETAILS_PROMPT.replace("{module_name}", module_name)
    prompt = prompt.replace("{module_description}", module_description)
    prompt = prompt.replace("{module_scope}", module_scope)
    prompt = prompt.replace("{module_dependencies}", module_dependencies)
    prompt = prompt.replace("{documentation}", documentation)
    return prompt
