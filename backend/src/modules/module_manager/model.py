"""
Module model and related entities for Hybrid Weighted Scoring system
"""


class Module:
    table_name = "modules"
    
    @staticmethod
    def to_dict(row) -> dict:
        """Convert database row to dictionary"""
        return {
            "id": row.get("id"),
            "project_id": row.get("project_id"),
            "name": row.get("name"),
            "description": row.get("description"),
            "scope": row.get("scope"),
            "dependencies": row.get("dependencies"),
            "features": row.get("features"),
            "requirements": row.get("requirements"),
            "technical_specs": row.get("technical_specs"),
            "progress": row.get("progress", 0),
            "task_count": row.get("task_count", 0),
            "completed_tasks": row.get("completed_tasks", 0),
            "generated_by_ai": row.get("generated_by_ai", False),
            "generation_metadata": row.get("generation_metadata", {}),
            # New: 4-layer metadata and reuse tracking
            "source_type": row.get("source_type"),
            "intent_primary": row.get("intent_primary"),
            "tags_metadata": row.get("tags_metadata", {}),
            "reused_from_module_id": row.get("reused_from_module_id"),
            "reuse_strategy": row.get("reuse_strategy"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }


class ModuleTag:
    """Model for module_tags table - normalized multi-tagging"""
    table_name = "module_tags"
    
    @staticmethod
    def to_dict(row) -> dict:
        """Convert database row to dictionary"""
        return {
            "id": row.get("id"),
            "module_id": row.get("module_id"),
            "layer": row.get("layer"),
            "tag_value": row.get("tag_value"),
            "confidence_score": float(row.get("confidence_score", 0.8)),
            "tag_metadata": row.get("tag_metadata", {}),
            "assigned_by": row.get("assigned_by"),
            "assigned_at": row.get("assigned_at"),
            "created_at": row.get("created_at"),
        }


class ReuseHistory:
    """Model for reuse_history table - tracking module reuse decisions"""
    table_name = "reuse_history"
    
    @staticmethod
    def to_dict(row) -> dict:
        """Convert database row to dictionary"""
        return {
            "id": row.get("id"),
            "source_module_id": row.get("source_module_id"),
            "target_module_id": row.get("target_module_id"),
            "target_project_id": row.get("target_project_id"),
            "similarity_score": float(row.get("similarity_score", 0.0)),
            "score_breakdown": row.get("score_breakdown", {}),
            "reuse_strategy": row.get("reuse_strategy"),
            "decision_rationale": row.get("decision_rationale"),
            "user_accepted": row.get("user_accepted"),
            "user_feedback": row.get("user_feedback"),
            "ai_model": row.get("ai_model"),
            "created_at": row.get("created_at"),
        }


class ScoringWeightsConfig:
    """Model for scoring_weights_config table - configurable matching weights"""
    table_name = "scoring_weights_config"
    
    @staticmethod
    def to_dict(row) -> dict:
        """Convert database row to dictionary"""
        return {
            "id": row.get("id"),
            "config_name": row.get("config_name"),
            "description": row.get("description"),
            "project_domain": row.get("project_domain"),
            "target_tech_stack": row.get("target_tech_stack"),
            "weight_L1_intent": float(row.get("weight_L1_intent", 0.5)),
            "weight_L2_constraint": float(row.get("weight_L2_constraint", 0.25)),
            "weight_L3_context": float(row.get("weight_L3_context", 0.15)),
            "weight_L4_quality": float(row.get("weight_L4_quality", 0.1)),
            "threshold_direct_reuse": float(row.get("threshold_direct_reuse", 0.85)),
            "threshold_logic_reference": float(row.get("threshold_logic_reference", 0.6)),
            "is_active": row.get("is_active", True),
            "is_default": row.get("is_default", False),
            "usage_count": row.get("usage_count", 0),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }
