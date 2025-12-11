"""
Tag normalization and synonym mapping for consistent similarity matching
"""
from typing import List, Set
import re


# ================================================================
# STANDARD TAG VOCABULARY
# ================================================================

# Layer 1: Intent Tags (What functionality?)
L1_SYNONYMS = {
    "auth": ["auth", "authentication", "login", "user-auth", "identity", "sso"],
    "document-management": ["document-management", "doc-mgmt", "file-management", "content-management"],
    "file-upload": ["file-upload", "upload", "upload-files", "file-input"],
    "payment": ["payment", "billing", "checkout", "transaction", "payment-processing"],
    "search": ["search", "query", "find", "filter", "discovery"],
    "notification": ["notification", "alert", "messaging", "push-notification"],
    "analytics": ["analytics", "reporting", "dashboard", "metrics", "insights"],
    "inventory": ["inventory", "stock", "warehouse", "inventory-management"],
    "order": ["order", "order-management", "purchase", "procurement"],
    "user-management": ["user-management", "user-admin", "account-management"],
    "api": ["api", "rest-api", "graphql", "endpoint"],
    "data-export": ["data-export", "export", "download", "extract"],
    "data-import": ["data-import", "import", "upload-data", "batch-upload"],
    "chat": ["chat", "messaging", "conversation", "real-time-chat"],
    "email": ["email", "mail", "smtp", "email-service"],
    "workflow": ["workflow", "approval", "process", "automation"],
}

# Layer 2: Constraint Tags (What tech stack?)
L2_SYNONYMS = {
    "nodejs": ["nodejs", "node.js", "node", "express", "nestjs"],
    "react": ["react", "reactjs", "react.js", "react-18"],
    "typescript": ["typescript", "ts"],
    "python": ["python", "python3", "py"],
    "postgresql": ["postgresql", "postgres", "pg", "psql"],
    "mongodb": ["mongodb", "mongo", "nosql"],
    "redis": ["redis", "cache"],
    "docker": ["docker", "containerization"],
    "aws": ["aws", "amazon-web-services", "cloud"],
    "nextjs": ["nextjs", "next.js", "next"],
    "tailwind": ["tailwind", "tailwindcss"],
    "materialui": ["materialui", "material-ui", "mui"],
}

# Layer 3: Context Tags (What domain/industry?)
L3_SYNONYMS = {
    "saas": ["saas", "b2b", "enterprise"],
    "ecommerce": ["ecommerce", "e-commerce", "online-store", "retail"],
    "fintech": ["fintech", "finance", "banking", "financial-services"],
    "healthcare": ["healthcare", "medical", "health", "clinic"],
    "education": ["education", "edtech", "learning", "e-learning"],
    "logistics": ["logistics", "shipping", "delivery", "transportation"],
    "manufacturing": ["manufacturing", "factory", "production"],
}

# Layer 4: Quality Tags (What characteristics?)
L4_SYNONYMS = {
    "real-time": ["real-time", "realtime", "live", "websocket"],
    "high-traffic": ["high-traffic", "scalable", "high-performance"],
    "security-critical": ["security-critical", "secure", "encryption", "compliance"],
    "multilingual": ["multilingual", "i18n", "internationalization", "localization"],
    "mobile-first": ["mobile-first", "responsive", "mobile-responsive"],
}


# ================================================================
# NORMALIZATION FUNCTIONS
# ================================================================

def normalize_tag(tag: str, layer: str) -> str:
    """
    Normalize a tag to its canonical form using synonym mapping.
    
    Args:
        tag: Raw tag value (e.g., "Authentication")
        layer: Layer type (L1_intent, L2_constraint, L3_context, L4_quality)
    
    Returns:
        Normalized canonical tag (e.g., "auth")
    """
    # Clean: lowercase, replace spaces/underscores with hyphens
    cleaned = tag.lower().strip().replace(" ", "-").replace("_", "-")
    
    # Remove common suffixes
    cleaned = re.sub(r"-(service|module|system|management)$", "", cleaned)
    
    # Get appropriate synonym map
    synonym_map = {
        "L1_intent": L1_SYNONYMS,
        "L2_constraint": L2_SYNONYMS,
        "L3_context": L3_SYNONYMS,
        "L4_quality": L4_SYNONYMS,
    }.get(layer, {})
    
    # Find canonical tag
    for canonical, synonyms in synonym_map.items():
        if cleaned in synonyms:
            return canonical
    
    # If no match, return cleaned version
    return cleaned


def normalize_tags_dict(tags_dict: dict) -> dict:
    """
    Normalize all tags in a tags dictionary.
    
    Args:
        tags_dict: {L1_intent: [...], L2_constraint: [...], ...}
    
    Returns:
        Normalized tags dictionary with canonical tags
    """
    normalized = {}
    
    for layer, tags in tags_dict.items():
        if isinstance(tags, list):
            # Normalize each tag and remove duplicates
            normalized_tags = list(set(
                normalize_tag(tag, layer) for tag in tags
            ))
            normalized[layer] = sorted(normalized_tags)  # Sort for consistency
    
    return normalized


def expand_tag_to_synonyms(tag: str, layer: str) -> Set[str]:
    """
    Expand a canonical tag to all its synonyms for fuzzy matching.
    
    Args:
        tag: Canonical tag (e.g., "auth")
        layer: Layer type
    
    Returns:
        Set of all synonyms including canonical
    """
    synonym_map = {
        "L1_intent": L1_SYNONYMS,
        "L2_constraint": L2_SYNONYMS,
        "L3_context": L3_SYNONYMS,
        "L4_quality": L4_SYNONYMS,
    }.get(layer, {})
    
    # Find synonyms for this tag
    for canonical, synonyms in synonym_map.items():
        if tag == canonical or tag in synonyms:
            return set(synonyms)
    
    # Not found in map, return original
    return {tag}


# ================================================================
# ENHANCED SIMILARITY WITH NORMALIZATION
# ================================================================

def calculate_normalized_similarity(tags_a: List[str], tags_b: List[str], layer: str) -> float:
    """
    Calculate Jaccard similarity with tag normalization.
    
    This handles synonyms so "Auth" and "Authentication" are considered the same.
    
    Args:
        tags_a: Tags from module A
        tags_b: Tags from module B
        layer: Layer type for normalization
    
    Returns:
        Jaccard similarity score (0.0 - 1.0)
    """
    # Normalize both tag lists
    normalized_a = set(normalize_tag(tag, layer) for tag in tags_a)
    normalized_b = set(normalize_tag(tag, layer) for tag in tags_b)
    
    # Calculate Jaccard
    intersection = len(normalized_a & normalized_b)
    union = len(normalized_a | normalized_b)
    
    if union == 0:
        return 0.0
    
    return intersection / union


# ================================================================
# PROMPT ENHANCEMENT FOR CONSISTENT TAGGING
# ================================================================

TAG_VOCABULARY_PROMPT = """
**IMPORTANT**: Use these standard tags when possible for consistency:

**L1 Intent** (choose from):
- auth, document-management, file-upload, payment, search, notification
- analytics, inventory, order, user-management, api, data-export
- data-import, chat, email, workflow

**L2 Constraint** (choose from):
- nodejs, react, typescript, python, postgresql, mongodb, redis
- docker, aws, nextjs, tailwind, materialui

**L3 Context** (choose from):
- saas, ecommerce, fintech, healthcare, education, logistics, manufacturing

**L4 Quality** (choose from):
- real-time, high-traffic, security-critical, multilingual, mobile-first

If functionality doesn't match standard tags, create descriptive hyphenated tags (e.g., "video-streaming", "ai-chatbot").
"""


# ================================================================
# EXAMPLE USAGE
# ================================================================

if __name__ == "__main__":
    # Test normalization
    test_tags = {
        "L1_intent": ["Authentication", "Document Management", "File Upload Service"],
        "L2_constraint": ["Node.js", "React 18", "PostgreSQL"],
        "L3_context": ["B2B SaaS", "Enterprise Software"],
        "L4_quality": ["Real-Time Updates", "High Performance"],
    }
    
    normalized = normalize_tags_dict(test_tags)
    print("Normalized tags:", normalized)
    # Output: {
    #   "L1_intent": ["auth", "document-management", "file-upload"],
    #   "L2_constraint": ["nodejs", "postgresql", "react"],
    #   ...
    # }
    
    # Test similarity
    tags_a = ["Auth", "Login", "User Management"]
    tags_b = ["Authentication", "User-Auth", "Account Management"]
    
    similarity = calculate_normalized_similarity(tags_a, tags_b, "L1_intent")
    print(f"Similarity: {similarity}")  # Should be high despite different wording
