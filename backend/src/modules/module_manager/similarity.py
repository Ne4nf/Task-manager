"""
Module similarity calculation using semantic tag matching

New approach (MVP):
- Single tag per layer (L1, L2, L3)
- Semantic similarity via Claude API (tag_embeddings.py)
- Weighted scoring: L1×60% + L2×25% + L3×15%
- Simple threshold-based strategy
"""
from typing import List, Dict, Any, Tuple, Optional
from src.modules.module_manager.tag_embeddings import TagEmbeddingService


def calculate_module_similarity_semantic(
    source_tags: Dict[str, Dict],
    target_tags: Dict[str, Dict],
    embedding_service: TagEmbeddingService,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Calculate similarity between two modules using semantic tag matching.
    
    Args:
        source_tags: Existing module tags {"L1_intent": {"tag": "auth", ...}, ...}
        target_tags: New requirement tags (same structure)
        embedding_service: TagEmbeddingService instance for semantic matching
        weights: Layer weights {"L1_intent": 0.6, "L2_constraint": 0.25, "L3_context": 0.15}
    
    Returns:
        {
            "overall_score": 0.75,
            "weighted_score": 0.82,
            "layer_scores": {"L1_intent": 0.95, "L2_constraint": 0.60, "L3_context": 0.80},
            "breakdown": {...}
        }
    """
    return embedding_service.calculate_module_similarity(source_tags, target_tags, weights)


def determine_reuse_strategy_simple(
    similarity_result: Dict[str, Any],
    threshold_high: float = 0.75,
    threshold_medium: float = 0.50
) -> Tuple[str, str, Dict[str, Any]]:
    """
    Determine reuse strategy based on weighted similarity score.
    
    Simplified approach:
    - weighted_score >= 0.75: Direct reuse (high confidence)
    - weighted_score >= 0.50: Partial reuse (adapt as needed)
    - weighted_score < 0.50: New generation (low match)
    
    Args:
        similarity_result: Output from calculate_module_similarity_semantic()
        threshold_high: Min score for direct reuse
        threshold_medium: Min score for partial reuse
    
    Returns:
        (strategy, rationale, details)
        - strategy: 'direct', 'partial_reuse', or 'new_gen'
        - rationale: Human-readable explanation
        - details: Layer-level breakdown with recommendations
    """
    
    weighted_score = similarity_result["weighted_score"]
    layer_scores = similarity_result["layer_scores"]
    breakdown = similarity_result["breakdown"]
    
    # Extract individual layer scores
    l1_score = layer_scores.get("L1_intent", 0.0)
    l2_score = layer_scores.get("L2_constraint", 0.0)
    l3_score = layer_scores.get("L3_context", 0.0)
    
    # Determine strategy
    if weighted_score >= threshold_high:
        strategy = "direct"
        rationale = f"High similarity (weighted: {weighted_score:.1%}). Can reuse with minor customization."
        recommendations = [
            "✅ Reuse core logic directly",
            "✅ Adapt naming and configuration",
            "✅ Review and test thoroughly"
        ]
    
    elif weighted_score >= threshold_medium:
        strategy = "partial_reuse"
        
        # Provide layer-specific guidance
        if l1_score >= 0.7:
            if l2_score < 0.5:
                rationale = f"Intent matches ({l1_score:.1%}) but tech differs ({l2_score:.1%}). Adapt tech stack."
                recommendations = [
                    f"✅ Keep business logic (Intent: {l1_score:.1%} match)",
                    f"🔧 Port to target tech stack (Tech: {l2_score:.1%} match)",
                    "⚠️ Test thoroughly after tech migration"
                ]
            elif l3_score < 0.5:
                rationale = f"Intent matches ({l1_score:.1%}) but domain differs ({l3_score:.1%}). Adapt business rules."
                recommendations = [
                    f"✅ Keep technical approach (Intent: {l1_score:.1%} match)",
                    f"🏢 Adapt domain-specific logic (Domain: {l3_score:.1%} match)",
                    "⚠️ Review compliance and business rules"
                ]
            else:
                rationale = f"Moderate match (weighted: {weighted_score:.1%}). Reuse patterns and adapt details."
                recommendations = [
                    "✅ Reuse architecture patterns",
                    "🔧 Adapt implementation details",
                    "⚠️ Test edge cases carefully"
                ]
        else:
            rationale = f"Low intent match ({l1_score:.1%}). Extract specific patterns only."
            recommendations = [
                "📖 Study implementation patterns",
                "🔧 Build new with similar tech stack" if l2_score >= 0.6 else "🔧 Build new solution",
                "⚠️ Don't force reuse - intent differs"
            ]
    
    else:
        strategy = "new_gen"
        
        # Check if any patterns can be learned
        useful_patterns = []
        if l1_score >= 0.4:
            useful_patterns.append(f"Intent patterns ({l1_score:.1%})")
        if l2_score >= 0.6:
            useful_patterns.append(f"Tech stack ({l2_score:.1%})")
        if l3_score >= 0.6:
            useful_patterns.append(f"Domain knowledge ({l3_score:.1%})")
        
        if useful_patterns:
            rationale = f"Low match (weighted: {weighted_score:.1%}). Build new but learn from: {', '.join(useful_patterns)}."
            recommendations = [
                "🆕 Generate new module",
                f"📖 Reference for inspiration: {', '.join(useful_patterns)}",
                "⚠️ Don't reuse code - too different"
            ]
        else:
            rationale = f"No meaningful match (weighted: {weighted_score:.1%}). Generate fresh."
            recommendations = [
                "🆕 Generate completely new module",
                "📖 No relevant reference found",
                "✅ Full creative freedom"
            ]
    
    # Build detailed response
    details = {
        "strategy": strategy,
        "confidence": weighted_score,
        "rationale": rationale,
        "recommendations": recommendations,
        "layer_breakdown": {
            "L1_intent": {
                "score": l1_score,
                "tag1": breakdown.get("L1_intent", {}).get("tag1"),
                "tag2": breakdown.get("L1_intent", {}).get("tag2"),
                "match_quality": "strong" if l1_score >= 0.7 else "weak"
            },
            "L2_constraint": {
                "score": l2_score,
                "tag1": breakdown.get("L2_constraint", {}).get("tag1"),
                "tag2": breakdown.get("L2_constraint", {}).get("tag2"),
                "match_quality": "strong" if l2_score >= 0.7 else "weak"
            },
            "L3_context": {
                "score": l3_score,
                "tag1": breakdown.get("L3_context", {}).get("tag1"),
                "tag2": breakdown.get("L3_context", {}).get("tag2"),
                "match_quality": "strong" if l3_score >= 0.7 else "weak"
            }
        }
    }
    
    return strategy, rationale, details


def rank_modules_by_similarity(
    target_tags: Dict[str, Dict],
    candidate_modules: List[Dict],
    embedding_service: TagEmbeddingService,
    min_score: float = 0.3,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Rank candidate modules by semantic similarity to target tags.
    
    Args:
        target_tags: New requirement tags
        candidate_modules: List of modules with tags_metadata field
        embedding_service: TagEmbeddingService instance
        min_score: Minimum weighted_score to include
        top_k: Maximum number of results
    
    Returns:
        List of ranked modules with similarity details
    """
    
    ranked = []
    
    for candidate in candidate_modules:
        candidate_tags = candidate.get("tags_metadata", {})
        
        if not candidate_tags:
            continue
        
        # Calculate similarity
        similarity = calculate_module_similarity_semantic(
            source_tags=candidate_tags,
            target_tags=target_tags,
            embedding_service=embedding_service
        )
        
        # Determine strategy
        strategy, rationale, details = determine_reuse_strategy_simple(similarity)
        
        # Include if above threshold
        if similarity["weighted_score"] >= min_score:
            ranked.append({
                "module": candidate,
                "similarity": similarity,
                "strategy": strategy,
                "rationale": rationale,
                "details": details
            })
    
    # Sort by weighted score descending
    ranked.sort(key=lambda x: x["similarity"]["weighted_score"], reverse=True)
    
    # Return top K
    return ranked[:top_k]


# Legacy functions for backward compatibility (deprecated)
def calculate_jaccard_similarity(set1: List[str], set2: List[str]) -> float:
    """
    Calculate Jaccard similarity between two sets of tags.
    
    Jaccard = |intersection| / |union|
    Returns: 0.0 (no overlap) to 1.0 (identical)
    """
    if not set1 or not set2:
        return 0.0
    
    # Convert to sets for set operations
    s1 = set(tag.lower().strip() for tag in set1)
    s2 = set(tag.lower().strip() for tag in set2)
    
    intersection = len(s1 & s2)
    union = len(s1 | s2)
    
    if union == 0:
        return 0.0
    
    return intersection / union


def calculate_weighted_similarity(
    source_tags: Dict[str, List[str]],
    target_tags: Dict[str, List[str]],
    weights: Dict[str, float]
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate weighted similarity score across all 4 layers.
    
    Args:
        source_tags: Existing module tags {L1_intent: [...], L2_constraint: [...], ...}
        target_tags: New requirement tags (same structure)
        weights: Layer weights {L1: 0.5, L2: 0.25, L3: 0.15, L4: 0.1}
    
    Returns:
        (final_score, score_breakdown)
        - final_score: Weighted average (0.0 - 1.0)
        - score_breakdown: Individual layer scores
    """
    
    # Calculate similarity for each layer
    layer_scores = {}
    
    for layer_key in ['L1_intent', 'L2_constraint', 'L3_context', 'L4_quality']:
        source_layer_tags = source_tags.get(layer_key, [])
        target_layer_tags = target_tags.get(layer_key, [])
        
        # Handle both string arrays and object arrays with {tag, confidence}
        if source_layer_tags and isinstance(source_layer_tags[0], dict):
            source_layer_tags = [item['tag'] for item in source_layer_tags]
        if target_layer_tags and isinstance(target_layer_tags[0], dict):
            target_layer_tags = [item['tag'] for item in target_layer_tags]
        
        layer_scores[layer_key] = calculate_jaccard_similarity(
            source_layer_tags,
            target_layer_tags
        )
    
    # Calculate weighted final score
    # Map layer keys to weight keys
    weight_map = {
        'L1_intent': 'L1',
        'L2_constraint': 'L2',
        'L3_context': 'L3',
        'L4_quality': 'L4'
    }
    
    final_score = sum(
        layer_scores[layer_key] * weights.get(weight_map[layer_key], 0.0)
        for layer_key in layer_scores
    )
    
    return final_score, layer_scores


def determine_reuse_strategy(
    similarity_score: float,
    threshold_direct: float = 0.85,
    threshold_logic: float = 0.60
) -> Tuple[str, str]:
    """
    Determine reuse strategy based on similarity score.
    
    Args:
        similarity_score: Overall match score (0.0 - 1.0)
        threshold_direct: Min score for direct reuse
        threshold_logic: Min score for logic reference
    
    Returns:
        (strategy, rationale)
        - strategy: 'direct', 'logic_reference', or 'new_gen'
        - rationale: Human-readable explanation
    """
    
    if similarity_score >= threshold_direct:
        return (
            'direct',
            f'High similarity ({similarity_score:.2%}). Module matches both technical stack and business logic. Recommended: Copy module structure and adapt configuration.'
        )
    
    elif similarity_score >= threshold_logic:
        return (
            'logic_reference',
            f'Moderate similarity ({similarity_score:.2%}). Business logic aligns but technical stack may differ. Recommended: Extract core patterns/flows and generate fresh implementation.'
        )
    
    else:
        return (
            'new_gen',
            f'Low similarity ({similarity_score:.2%}). No strong matches found in memory. Recommended: Generate from scratch using AI knowledge base.'
        )


def format_score_breakdown(
    layer_scores: Dict[str, float],
    weights: Dict[str, float],
    final_score: float
) -> str:
    """
    Format score breakdown as human-readable text.
    
    Returns: Multi-line explanation of how score was calculated
    """
    
    lines = [
        "📊 Score Breakdown:",
        f"  • L1 Intent:      {layer_scores.get('L1_intent', 0):.2%} × {weights.get('L1', 0):.0%} = {layer_scores.get('L1_intent', 0) * weights.get('L1', 0):.2%}",
        f"  • L2 Constraint:  {layer_scores.get('L2_constraint', 0):.2%} × {weights.get('L2', 0):.0%} = {layer_scores.get('L2_constraint', 0) * weights.get('L2', 0):.2%}",
        f"  • L3 Context:     {layer_scores.get('L3_context', 0):.2%} × {weights.get('L3', 0):.0%} = {layer_scores.get('L3_context', 0) * weights.get('L3', 0):.2%}",
        f"  • L4 Quality:     {layer_scores.get('L4_quality', 0):.2%} × {weights.get('L4', 0):.0%} = {layer_scores.get('L4_quality', 0) * weights.get('L4', 0):.2%}",
        f"  ─────────────────────────────",
        f"  Final Score: {final_score:.2%}"
    ]
    
    return "\n".join(lines)


def rank_modules_by_similarity(
    target_tags: Dict[str, List[str]],
    candidate_modules: List[Dict[str, Any]],
    weights: Dict[str, float],
    thresholds: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Rank candidate modules by similarity to target requirements.
    
    Args:
        target_tags: Target requirement tags
        candidate_modules: List of modules with tags_metadata field
        weights: Scoring weights
        thresholds: {direct: 0.85, logic: 0.60}
    
    Returns:
        List of modules with added fields:
        - similarity_score
        - score_breakdown
        - recommended_strategy
        - decision_rationale
        
        Sorted by similarity_score DESC
    """
    
    results = []
    
    for module in candidate_modules:
        source_tags = module.get('tags_metadata', {})
        
        # Calculate similarity
        final_score, layer_scores = calculate_weighted_similarity(
            source_tags,
            target_tags,
            weights
        )
        
        # Determine strategy
        strategy, rationale = determine_reuse_strategy(
            final_score,
            thresholds.get('direct', 0.85),
            thresholds.get('logic', 0.60)
        )
        
        # Add to results
        results.append({
            **module,  # Include all original module fields
            'similarity_score': final_score,
            'score_breakdown': {
                'L1_intent_score': layer_scores.get('L1_intent', 0),
                'L2_constraint_score': layer_scores.get('L2_constraint', 0),
                'L3_context_score': layer_scores.get('L3_context', 0),
                'L4_quality_score': layer_scores.get('L4_quality', 0),
                'weights_used': weights,
                'final_weighted_score': final_score
            },
            'recommended_strategy': strategy,
            'decision_rationale': rationale
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return results
