"""
Tag embedding system for semantic similarity matching using Claude API

This module uses Claude's text embeddings (via prompt-based similarity) or a lightweight
embedding approach to enable semantic matching of tags even when text differs.

For MVP, we use a simple context-aware similarity:
1. Normalize tags to lowercase
2. Use Claude to assess semantic similarity between tags
3. Cache results for performance

For production, consider:
- sentence-transformers models (all-MiniLM-L6-v2)
- OpenAI embeddings API
- Dedicated vector database (pgvector, Pinecone, Weaviate)
"""

from typing import Dict, List, Tuple, Optional
import json
import anthropic
from src.core.config import get_settings

settings = get_settings()


class TagEmbeddingService:
    """
    Service for generating and comparing tag embeddings.
    
    MVP approach: Uses Claude API to assess semantic similarity between tags.
    This is simpler than maintaining an embedding model but requires API calls.
    
    For better performance, cache similarity scores in memory or Redis.
    """
    
    def __init__(self, claude: anthropic.Anthropic):
        self.claude = claude
        self.similarity_cache: Dict[Tuple[str, str, str], float] = {}  # (tag1, tag2, layer) -> score
    
    def calculate_semantic_similarity(
        self,
        tag1: str,
        tag2: str,
        layer: str,
        tag1_reasoning: Optional[str] = None,
        tag2_reasoning: Optional[str] = None
    ) -> float:
        """
        Calculate semantic similarity between two tags using Claude API.
        
        ISSUE #2 SOLUTION: Now accepts reasoning from tag_metadata for better context.
        When reasoning is provided, Claude can understand WHY each tag was chosen,
        leading to more accurate similarity scoring.
        
        Args:
            tag1: First tag (e.g., "auth")
            tag2: Second tag (e.g., "authentication")
            layer: Layer context (L1_intent, L2_constraint, L3_context)
            tag1_reasoning: Optional reasoning explaining why tag1 was chosen
            tag2_reasoning: Optional reasoning explaining why tag2 was chosen
        
        Returns:
            Similarity score 0.0-1.0
        """
        
        # Normalize tags
        tag1_norm = tag1.lower().strip()
        tag2_norm = tag2.lower().strip()
        
        # Exact match
        if tag1_norm == tag2_norm:
            return 1.0
        
        # Check cache
        cache_key = (tag1_norm, tag2_norm, layer)
        reverse_key = (tag2_norm, tag1_norm, layer)
        
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        if reverse_key in self.similarity_cache:
            return self.similarity_cache[reverse_key]
        
        # Use Claude to assess similarity with reasoning context
        similarity_score = self._assess_similarity_with_claude(
            tag1_norm, tag2_norm, layer, tag1_reasoning, tag2_reasoning
        )
        
        # Cache result (note: caching doesn't include reasoning, which is acceptable for MVP)
        self.similarity_cache[cache_key] = similarity_score
        
        return similarity_score
    
    def _assess_similarity_with_claude(
        self,
        tag1: str,
        tag2: str,
        layer: str,
        tag1_reasoning: Optional[str] = None,
        tag2_reasoning: Optional[str] = None
    ) -> float:
        """
        Use Claude API to assess semantic similarity between tags.
        
        This is the MVP approach - for production, use pre-computed embeddings.
        """
        
        layer_context = {
            "L1_intent": "functional purpose (what the module does)",
            "L2_constraint": "technical stack (technologies used)",
            "L3_context": "business domain (industry/use case)"
        }
        
        context = layer_context.get(layer, "general classification")
        
        # Build prompt with reasoning context (ISSUE #2 solution)
        tag1_context = f"\nTag 1 Reasoning: {tag1_reasoning}" if tag1_reasoning else ""
        tag2_context = f"\nTag 2 Reasoning: {tag2_reasoning}" if tag2_reasoning else ""
        
        prompt = f"""You are a semantic similarity expert for software module tags.

Assess the semantic similarity between these two tags in the context of {context}:

Tag 1: "{tag1}"{tag1_context}
Tag 2: "{tag2}"{tag2_context}

Consider:
- Are these synonyms or closely related concepts?
- Would a module with tag1 be relevant when searching for tag2?
- Do they serve the same or similar purposes?
- **IMPORTANT**: Use the reasoning to understand the INTENT behind each tag, not just the tag name

Return ONLY a JSON object with the similarity score:

{{
  "similarity": 0.95,
  "reasoning": "Brief explanation of the similarity"
}}

Scoring guide:
- 1.0: Exact match or perfect synonyms (e.g., "auth" and "authentication")
- 0.9-0.95: Very close semantics (e.g., "user-management" and "auth")
- 0.7-0.85: Related concepts (e.g., "payment" and "billing")
- 0.4-0.65: Somewhat related (e.g., "auth" and "api-gateway")
- 0.0-0.35: Different concepts (e.g., "auth" and "payment")

Return ONLY the JSON object."""

        try:
            message = self.claude.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=256,
                temperature=0.0,  # Deterministic for consistency
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            # Parse JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            similarity = result.get("similarity", 0.0)
            
            # Clamp to 0-1 range
            similarity = max(0.0, min(1.0, similarity))
            
            return similarity
            
        except Exception as e:
            print(f"⚠️ Failed to assess similarity between '{tag1}' and '{tag2}': {e}")
            # Fallback: simple string matching
            return self._fallback_similarity(tag1, tag2)
    
    def _fallback_similarity(self, tag1: str, tag2: str) -> float:
        """
        Fallback similarity using simple string matching.
        Used when Claude API fails.
        """
        # Exact match
        if tag1 == tag2:
            return 1.0
        
        # Contains
        if tag1 in tag2 or tag2 in tag1:
            return 0.8
        
        # Common words
        words1 = set(tag1.replace("-", " ").replace("_", " ").split())
        words2 = set(tag2.replace("-", " ").replace("_", " ").split())
        
        if words1 and words2:
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            jaccard = intersection / union if union > 0 else 0.0
            return jaccard * 0.7  # Scale down since it's just word overlap
        
        return 0.0
    
    def calculate_module_similarity(
        self,
        module1_tags: Dict[str, Dict],
        module2_tags: Dict[str, Dict],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, any]:
        """
        Calculate overall similarity between two modules based on their tags.
        
        Args:
            module1_tags: {"L1_intent": {"tag": "auth", ...}, "L2_constraint": {...}, ...}
            module2_tags: Same structure
            weights: {"L1": 0.6, "L2": 0.25, "L3": 0.15} (defaults if None)
        
        Returns:
            {
                "overall_score": 0.75,
                "layer_scores": {
                    "L1_intent": 0.95,
                    "L2_constraint": 0.60,
                    "L3_context": 0.80
                },
                "weighted_score": 0.82,
                "breakdown": {...}
            }
        """
        
        # Default weights (prioritize intent > tech > domain)
        if weights is None:
            weights = {"L1_intent": 0.60, "L2_constraint": 0.25, "L3_context": 0.15}
        
        layer_scores = {}
        breakdown = {}
        
        for layer in ["L1_intent", "L2_constraint", "L3_context"]:
            tag1_obj = module1_tags.get(layer, {})
            tag2_obj = module2_tags.get(layer, {})
            
            tag1 = tag1_obj.get("tag") if isinstance(tag1_obj, dict) else None
            tag2 = tag2_obj.get("tag") if isinstance(tag2_obj, dict) else None
            
            if not tag1 or not tag2:
                layer_scores[layer] = 0.0
                breakdown[layer] = {
                    "tag1": tag1,
                    "tag2": tag2,
                    "score": 0.0,
                    "reasoning": "One or both tags missing"
                }
                continue
            
            # Calculate semantic similarity
            similarity = self.calculate_semantic_similarity(tag1, tag2, layer)
            
            layer_scores[layer] = similarity
            breakdown[layer] = {
                "tag1": tag1,
                "tag2": tag2,
                "score": similarity,
                "reasoning": f"Semantic similarity between '{tag1}' and '{tag2}'"
            }
        
        # Calculate weighted score
        weighted_score = sum(
            layer_scores.get(layer, 0.0) * weight
            for layer, weight in weights.items()
        )
        
        # Overall average (unweighted)
        overall_score = sum(layer_scores.values()) / len(layer_scores) if layer_scores else 0.0
        
        return {
            "overall_score": overall_score,
            "weighted_score": weighted_score,
            "layer_scores": layer_scores,
            "breakdown": breakdown,
            "weights_used": weights
        }
    
    def find_similar_modules(
        self,
        query_tags: Dict[str, Dict],
        candidate_modules: List[Dict],
        threshold: float = 0.5,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Find similar modules based on tag similarity.
        
        Args:
            query_tags: Tags of the module we're trying to match
            candidate_modules: List of modules with tags_metadata field
            threshold: Minimum weighted_score to include
            top_k: Maximum number of results to return
        
        Returns:
            List of modules with similarity scores, sorted by weighted_score descending
        """
        
        results = []
        
        for candidate in candidate_modules:
            candidate_tags = candidate.get("tags_metadata", {})
            
            if not candidate_tags:
                continue
            
            similarity = self.calculate_module_similarity(query_tags, candidate_tags)
            
            if similarity["weighted_score"] >= threshold:
                results.append({
                    "module": candidate,
                    "similarity": similarity
                })
        
        # Sort by weighted score descending
        results.sort(key=lambda x: x["similarity"]["weighted_score"], reverse=True)
        
        # Return top K
        return results[:top_k]


# Example usage
"""
from src.core.claude import get_claude_client

claude = get_claude_client()
embedding_service = TagEmbeddingService(claude)

# Calculate similarity between two tags
similarity = embedding_service.calculate_semantic_similarity(
    tag1="auth",
    tag2="authentication",
    layer="L1_intent"
)
print(f"Similarity: {similarity}")  # Expected: ~0.95-1.0

# Calculate module similarity
module1_tags = {
    "L1_intent": {"tag": "auth"},
    "L2_constraint": {"tag": "nodejs"},
    "L3_context": {"tag": "saas"}
}

module2_tags = {
    "L1_intent": {"tag": "authentication"},
    "L2_constraint": {"tag": "python"},
    "L3_context": {"tag": "saas"}
}

result = embedding_service.calculate_module_similarity(module1_tags, module2_tags)
print(f"Overall: {result['overall_score']:.2f}")
print(f"Weighted: {result['weighted_score']:.2f}")
print(f"Layer scores: {result['layer_scores']}")
"""
