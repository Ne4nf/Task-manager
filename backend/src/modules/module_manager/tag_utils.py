"""
Tag generation utilities for 3-layer module classification (Single Responsibility)
"""

# Constrained Taxonomy - AI must choose from these standard tags
TAXONOMY = {
    "L1_intent": [
        "auth", "payment", "chat", "search", "analytics", "notification", 
        "workflow", "integration", "data-sync", "reporting", "user-management",
        "content-management", "file-storage", "email", "sms", "logging",
        "monitoring", "cache", "queue", "api-gateway", "load-balancer",
        "document-management", "inventory", "order-management", "shipping",
        "billing", "subscription", "crm", "hr", "project-management",
        "task-management", "calendar", "booking", "marketplace", "recommendation",
        "ai-assistant", "ocr", "video-processing", "image-processing"
    ],
    "L2_constraint": [
        "nodejs", "python", "go", "java", "react", "vue", "angular",
        "postgresql", "mongodb", "redis", "mysql", "elasticsearch",
        "docker", "kubernetes", "aws", "gcp", "azure", "rest-api",
        "graphql", "grpc", "websocket", "oauth2", "jwt", "microservices",
        "monolith", "fastapi", "express", "django", "flask", "springboot",
        "nextjs", "typescript", "supabase", "firebase"
    ],
    "L3_context": [
        "fintech", "ecommerce", "healthcare", "education", "saas",
        "logistics", "real-estate", "social-media", "gaming", "iot",
        "enterprise", "b2b", "b2c", "internal-tools", "warehouse",
        "retail", "manufacturing", "travel", "hospitality", "legal"
    ]
}

# Prompt for AI to generate 3-layer SINGLE tags from module data
TAG_GENERATION_PROMPT = """You are an expert software architect analyzing module requirements to classify them into a 3-layer taxonomy following Single Responsibility Principle.

**CRITICAL RULES:**
1. **Each layer = EXACTLY ONE tag** (Single Responsibility)
2. **MUST choose from the provided taxonomy** (no free-form tags)
3. If a module does multiple things, it's poorly designed - choose the PRIMARY intent only
4. Provide detailed reasoning in metadata to explain your choice and mention secondary aspects

**3-Layer Classification System:**

**L1 - Intent (Functional Purpose):**
What is the PRIMARY function? Pick ONE from taxonomy.
TAXONOMY: {l1_taxonomy}

**L2 - Constraint (Primary Tech Stack):**
What is the MAIN technology? Pick ONE from taxonomy.
TAXONOMY: {l2_taxonomy}

**L3 - Context (Business Domain):**
What is the PRIMARY domain? Pick ONE from taxonomy.
TAXONOMY: {l3_taxonomy}

**Guidelines:**
- If unsure between multiple L1 tags, pick the one that represents the core responsibility
- For L2, pick the dominant/required technology (e.g., if both "nodejs" and "react", choose based on backend vs frontend focus)
- For L3, pick the most specific domain
- Use reasoning field to explain why you chose this tag and what secondary aspects exist

**Guidelines:**
- If unsure between multiple L1 tags, pick the one that represents the core responsibility
- For L2, pick the dominant/required technology (e.g., if both "nodejs" and "react", choose based on backend vs frontend focus)
- For L3, pick the most specific domain
- Use reasoning field to explain why you chose this tag and what secondary aspects exist

**Module Information:**
Name: {module_name}
Description: {module_description}
Scope: {module_scope}
Features: {module_features}
Requirements: {module_requirements}
Technical Specs: {module_technical_specs}

**Output Format:**
Return ONLY a valid JSON object (no markdown, no explanation):

{{
  "L1_intent": {{
    "tag": "chosen-tag-from-taxonomy",
    "confidence": 0.95,
    "reasoning": "Detailed explanation: Why this is the PRIMARY function. Secondary aspects: X, Y, Z"
  }},
  "L2_constraint": {{
    "tag": "chosen-tech-from-taxonomy",
    "confidence": 0.90,
    "reasoning": "Detailed explanation: Why this is the MAIN technology. Also uses: X, Y for specific purposes"
  }},
  "L3_context": {{
    "tag": "chosen-domain-from-taxonomy",
    "confidence": 0.85,
    "reasoning": "Detailed explanation: Why this is the PRIMARY domain. May also serve: X, Y"
  }}
}}

**Example 1:**
For a "User Authentication with SSO support for enterprise SaaS" module:
{{
  "L1_intent": {{
    "tag": "auth",
    "confidence": 0.98,
    "reasoning": "PRIMARY function is authentication and authorization. While it touches user-management (user profiles), the core responsibility is validating identity and managing access tokens. Secondary aspects: session management, user lookup, role-based access control."
  }},
  "L2_constraint": {{
    "tag": "nodejs",
    "confidence": 0.95,
    "reasoning": "Backend implementation uses Node.js with Express framework. While there's a React admin panel, the core auth service runs on Node.js. Full stack: JWT for tokens, Redis for sessions, PostgreSQL for user data, OAuth2 for SSO."
  }},
  "L3_context": {{
    "tag": "saas",
    "confidence": 0.95,
    "reasoning": "PRIMARY domain is SaaS (multi-tenant architecture with enterprise features). The B2B focus is a characteristic of the target customers. Serves: Enterprise clients across fintech, healthcare, and ecommerce verticals."
  }}
}}

**Example 2:**
For a "Blockchain-based supply chain tracking for pharmaceutical industry":
{{
  "L1_intent": {{
    "tag": "supply-chain-tracking",
    "confidence": 0.97,
    "reasoning": "PRIMARY function is tracking product movement through supply chain with immutable audit trail. This is more specific than generic 'tracking' or 'logistics'. Secondary: inventory snapshots, compliance reporting, temperature monitoring."
  }},
  "L2_constraint": {{
    "tag": "blockchain",
    "confidence": 0.98,
    "reasoning": "Core technology is blockchain (Hyperledger Fabric) for immutability and multi-party consensus. Backend uses Go for chaincode, Node.js for API layer. The blockchain aspect is the defining constraint."
  }},
  "L3_context": {{
    "tag": "pharmaceutical",
    "confidence": 0.96,
    "reasoning": "PRIMARY domain is pharmaceutical due to strict regulatory requirements (FDA, GDP), cold chain validation, and counterfeit prevention needs. More specific than generic 'healthcare' or 'supply-chain'."
  }}
}}

Now generate tags for the module above. Return ONLY the JSON object.
"""


def create_tag_generation_prompt(module_data: dict) -> str:
    """Create prompt for tag generation from module data"""
    prompt = TAG_GENERATION_PROMPT.replace("{module_name}", module_data.get('name', 'Unnamed'))
    prompt = prompt.replace("{module_description}", module_data.get('description', 'No description'))
    prompt = prompt.replace("{module_scope}", module_data.get('scope', 'Not specified'))
    prompt = prompt.replace("{module_features}", module_data.get('features', 'Not specified'))
    prompt = prompt.replace("{module_requirements}", module_data.get('requirements', 'Not specified'))
    prompt = prompt.replace("{module_technical_specs}", module_data.get('technical_specs', 'Not specified'))
    return prompt

