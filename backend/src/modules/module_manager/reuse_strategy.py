"""
Advanced reuse strategy based on layer-level analysis
"""
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class LayerMatchQuality:
    """Quality assessment for each layer match"""
    layer: str
    score: float
    is_strong: bool  # >= 0.7
    is_acceptable: bool  # >= 0.4
    matched_tags: List[str]
    missing_tags: List[str]


@dataclass
class ReuseDecision:
    """Comprehensive reuse decision with warnings and rationale"""
    strategy: str  # "direct", "partial_reuse", "pattern_combination", "new_gen"
    confidence: float  # 0.0 - 1.0
    warnings: List[str]
    rationale: str
    layer_analysis: Dict[str, LayerMatchQuality]
    recommended_actions: List[str]


def analyze_layer_match_quality(
    score_breakdown: Dict[str, float],
    target_tags: Dict[str, List[str]],
    source_tags: Dict[str, List[str]]
) -> Dict[str, LayerMatchQuality]:
    """
    Analyze match quality for each layer individually.
    
    Returns detailed breakdown of what matched and what didn't.
    """
    analysis = {}
    
    for layer in ["L1_intent", "L2_constraint", "L3_context", "L4_quality"]:
        score = score_breakdown.get(f"{layer}_score", 0.0)
        
        target_set = set(target_tags.get(layer, []))
        source_set = set(source_tags.get(layer, []))
        
        matched = list(target_set & source_set)
        missing = list(target_set - source_set)
        
        analysis[layer] = LayerMatchQuality(
            layer=layer,
            score=score,
            is_strong=score >= 0.7,
            is_acceptable=score >= 0.4,
            matched_tags=matched,
            missing_tags=missing
        )
    
    return analysis


def determine_smart_reuse_strategy(
    overall_score: float,
    score_breakdown: Dict[str, float],
    target_tags: Dict[str, List[str]],
    source_module: Dict[str, Any],
    requirements_doc: str
) -> ReuseDecision:
    """
    Determine reuse strategy based on layer-level analysis.
    
    Key Principle: L1 (Intent) is MOST important. Even if overall score is low,
    if L1 matches well, we can adapt other layers.
    
    Strategy Decision Tree:
    1. Check L1 (Intent) - If strong → Consider reuse
    2. Check L2 (Tech) - If mismatch → Need tech adaptation
    3. Check L3 (Context) - If mismatch → Need domain customization
    4. Check L4 (Quality) - If mismatch → Need non-functional adaptation
    """
    # Analyze each layer
    source_tags = source_module.get('tags_metadata', {})
    layer_analysis = analyze_layer_match_quality(score_breakdown, target_tags, source_tags)
    
    L1 = layer_analysis["L1_intent"]
    L2 = layer_analysis["L2_constraint"]
    L3 = layer_analysis["L3_context"]
    L4 = layer_analysis["L4_quality"]
    
    warnings = []
    recommended_actions = []
    
    # ================================================================
    # DECISION LOGIC (Intent-First Approach)
    # ================================================================
    
    # Case 1: Strong L1 + Strong L2 + Acceptable L3/L4 → DIRECT REUSE
    if L1.is_strong and L2.is_strong and L3.is_acceptable:
        strategy = "direct"
        confidence = min(0.95, overall_score)
        rationale = (
            f"Strong intent match ({L1.score:.0%}) and tech alignment ({L2.score:.0%}). "
            f"Module can be copied with minor customization."
        )
        
        if not L4.is_strong:
            warnings.append(f"⚠️ Quality attributes differ (score: {L4.score:.0%}). Review non-functional requirements.")
            recommended_actions.append(f"Adapt quality aspects: {', '.join(L4.missing_tags)}")
    
    # Case 2: Strong L1 + Weak L2 → TECH ADAPTATION
    elif L1.is_strong and not L2.is_strong:
        strategy = "partial_reuse"
        confidence = 0.70
        rationale = (
            f"Intent matches well ({L1.score:.0%}) but tech stack differs ({L2.score:.0%}). "
            f"Reuse business logic and architecture, but rewrite in target tech."
        )
        warnings.append(f"🔧 Tech stack mismatch! Need to translate from {source_tags.get('L2_constraint', [])} to {target_tags.get('L2_constraint', [])}")
        recommended_actions.append(f"Port logic to: {', '.join(L2.missing_tags)}")
        recommended_actions.append("Keep: Architecture, workflows, business rules")
        recommended_actions.append("Rewrite: Implementation code, frameworks, libraries")
    
    # Case 3: Strong L1 + Weak L3 → DOMAIN ADAPTATION  
    elif L1.is_strong and not L3.is_acceptable:
        strategy = "partial_reuse"
        confidence = 0.65
        rationale = (
            f"Intent matches ({L1.score:.0%}) but domain context differs ({L3.score:.0%}). "
            f"Adapt business rules and compliance requirements for target domain."
        )
        warnings.append(f"🏢 Domain mismatch! Source: {source_tags.get('L3_context', [])} → Target: {target_tags.get('L3_context', [])}")
        recommended_actions.append("Customize: Business rules, validation logic, compliance")
        recommended_actions.append(f"Add domain-specific features for: {', '.join(L3.missing_tags)}")
    
    # Case 4: Acceptable L1 + Multiple modules → PATTERN COMBINATION
    elif L1.is_acceptable and not L1.is_strong:
        strategy = "pattern_combination"
        confidence = 0.60
        rationale = (
            f"Partial intent match ({L1.score:.0%}). "
            f"Extract specific patterns/components and combine with other references or new code."
        )
        warnings.append(f"⚡ Partial match only. Focus on reusable patterns, not full module.")
        recommended_actions.append(f"Extract patterns for: {', '.join(L1.matched_tags)}")
        recommended_actions.append(f"Build new code for: {', '.join(L1.missing_tags)}")
    
    # Case 5: Weak L1 → NEW GENERATION (with guided suggestions)
    else:
        strategy = "new_gen"
        confidence = 0.30
        rationale = (
            f"Intent mismatch ({L1.score:.0%}). "
            f"Generate new module from scratch, but consider patterns from similar modules."
        )
        warnings.append(f"❌ LOW CONFIDENCE MATCH! Intent differs significantly.")
        
        # Even for new gen, suggest what CAN be learned
        if L2.is_strong:
            recommended_actions.append(f"✅ Can reuse tech patterns: {', '.join(L2.matched_tags)}")
        if L3.is_acceptable:
            recommended_actions.append(f"✅ Can learn domain patterns: {', '.join(L3.matched_tags)}")
        
        recommended_actions.append(f"⚠️ Must build new functionality: {', '.join(L1.missing_tags)}")
    
    return ReuseDecision(
        strategy=strategy,
        confidence=confidence,
        warnings=warnings,
        rationale=rationale,
        layer_analysis=layer_analysis,
        recommended_actions=recommended_actions
    )


def generate_reuse_prompt_with_guidance(
    decision: ReuseDecision,
    source_module: Dict[str, Any],
    requirements_doc: str,
    match_details: Dict[str, Any]
) -> str:
    """
    Generate AI prompt with detailed guidance based on reuse decision.
    
    This gives Claude specific instructions on what to keep, what to adapt,
    and what to build new.
    """
    L1 = decision.layer_analysis["L1_intent"]
    L2 = decision.layer_analysis["L2_constraint"]
    L3 = decision.layer_analysis["L3_context"]
    L4 = decision.layer_analysis["L4_quality"]
    
    if decision.strategy == "direct":
        prompt = f"""You are adapting an existing module for new requirements.

**SOURCE MODULE**: {source_module['name']}
{source_module.get('description', '')}

**MATCH ANALYSIS**:
- Intent Match: {L1.score:.0%} ✅ (Strong)
- Tech Match: {L2.score:.0%} ✅ (Strong)
- Overall Confidence: {decision.confidence:.0%}

**STRATEGY**: DIRECT REUSE with Minor Customization

**WHAT TO KEEP**:
- Core architecture and structure
- Business logic and workflows
- Tech stack: {', '.join(L2.matched_tags)}
- Features: {', '.join(L1.matched_tags)}

**WHAT TO CUSTOMIZE**:
{chr(10).join(f"- {action}" for action in decision.recommended_actions)}

**NEW REQUIREMENTS**:
{requirements_doc[:2000]}

Generate the adapted module with same structure but customized details.
Return JSON: {{"name": "...", "description": "...", "features": "...", ...}}
"""

    elif decision.strategy == "partial_reuse":
        prompt = f"""You are adapting a module with significant changes.

**SOURCE MODULE**: {source_module['name']}
Features: {source_module.get('features', '')[:500]}
Tech: {', '.join(source_module.get('tags_metadata', {}).get('L2_constraint', []))}

**MATCH ANALYSIS**:
- Intent Match: {L1.score:.0%} {'✅' if L1.is_strong else '⚠️'}
- Tech Match: {L2.score:.0%} {'✅' if L2.is_strong else '❌ MISMATCH'}
- Domain Match: {L3.score:.0%} {'✅' if L3.is_acceptable else '❌ MISMATCH'}

**STRATEGY**: PARTIAL REUSE - Adapt Architecture

**⚠️ WARNINGS**:
{chr(10).join(f"- {warning}" for warning in decision.warnings)}

**KEEP (Architecture & Logic)**:
- Functional workflows: {', '.join(L1.matched_tags)}
- Business processes and state machines
- Data models and relationships

**ADAPT (Implementation)**:
{chr(10).join(f"- {action}" for action in decision.recommended_actions)}

**NEW REQUIREMENTS**:
{requirements_doc[:2000]}

Generate NEW module that:
1. Reuses proven architecture/workflows from source
2. Implements in target tech stack: {', '.join(L2.missing_tags)}
3. Adapts for target domain: {', '.join(L3.missing_tags)}

Return JSON: {{"name": "...", "description": "...", "features": "...", ...}}
"""

    elif decision.strategy == "pattern_combination":
        prompt = f"""You are synthesizing a module from multiple partial matches.

**REFERENCE MODULE**: {source_module['name']}

**MATCH ANALYSIS**:
- Intent Match: {L1.score:.0%} (Partial - some features match)
- Matched Intent: {', '.join(L1.matched_tags)}
- Missing Intent: {', '.join(L1.missing_tags)}

**STRATEGY**: PATTERN COMBINATION

**EXTRACT FROM REFERENCE**:
- Patterns for: {', '.join(L1.matched_tags)}
- Architecture concepts
- Best practices

**BUILD NEW**:
{chr(10).join(f"- {action}" for action in decision.recommended_actions)}

**NEW REQUIREMENTS**:
{requirements_doc[:2000]}

Generate module that combines:
1. Proven patterns from reference (where applicable)
2. New implementation for missing functionality
3. Cohesive solution meeting all requirements

Return JSON: {{"name": "...", "description": "...", "features": "...", ...}}
"""

    else:  # new_gen
        prompt = f"""Generate a NEW module from scratch (low match with existing).

**REFERENCE** (for inspiration only): {source_module['name']}

**MATCH ANALYSIS**:
- Intent Match: {L1.score:.0%} ❌ (Low - different functionality)
- Can learn from: {', '.join(L2.matched_tags + L3.matched_tags)}

**STRATEGY**: NEW GENERATION

**⚠️ CRITICAL**:
{chr(10).join(f"- {warning}" for warning in decision.warnings)}

**SUGGESTED GUIDANCE**:
{chr(10).join(f"- {action}" for action in decision.recommended_actions)}

**REQUIREMENTS** (PRIMARY SOURCE):
{requirements_doc[:2000]}

Generate module primarily from requirements. Only reference existing module for:
- General tech patterns if applicable
- Code style and structure conventions

Return JSON: {{"name": "...", "description": "...", "features": "...", ...}}
"""

    return prompt


# ================================================================
# FRONTEND WARNING GENERATION
# ================================================================

def generate_ui_warnings(decision: ReuseDecision) -> Dict[str, Any]:
    """
    Generate warnings and badges for UI display.
    
    Returns structure for frontend to show user what to review.
    """
    severity_map = {
        "direct": "success",
        "partial_reuse": "warning", 
        "pattern_combination": "warning",
        "new_gen": "info"
    }
    
    return {
        "strategy": decision.strategy,
        "confidence": decision.confidence,
        "severity": severity_map[decision.strategy],
        "badge_text": {
            "direct": "✅ High Confidence Reuse",
            "partial_reuse": "⚠️ Adaptation Required",
            "pattern_combination": "🧩 Pattern Combination",
            "new_gen": "🆕 New Generation (Low Match)"
        }[decision.strategy],
        "warnings": decision.warnings,
        "recommended_actions": decision.recommended_actions,
        "layer_breakdown": {
            layer: {
                "score": analysis.score,
                "status": "✅ Strong" if analysis.is_strong else ("⚠️ Partial" if analysis.is_acceptable else "❌ Weak"),
                "matched": analysis.matched_tags,
                "missing": analysis.missing_tags
            }
            for layer, analysis in decision.layer_analysis.items()
        }
    }
