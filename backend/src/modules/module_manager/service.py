"""
Module manager service with tag generation and semantic similarity search
"""
from typing import List, Optional, Dict, Any
import json
from supabase import Client
import anthropic
from src.modules.module_manager.schema import ModuleCreate, ModuleUpdate
from src.modules.module_manager.model import Module, ModuleTag, ScoringWeightsConfig
from src.modules.module_manager.utils import (
    create_module_metadata_prompt,
    create_module_details_prompt
)
from src.modules.module_manager.tag_utils import create_tag_generation_prompt
from src.modules.module_manager.tag_embeddings import TagEmbeddingService
from src.modules.module_manager.similarity import (
    calculate_module_similarity_semantic,
    determine_reuse_strategy_simple,
    # Legacy functions for backward compatibility
    calculate_weighted_similarity,
    determine_reuse_strategy,
    rank_modules_by_similarity
)
from src.core.config import get_settings

settings = get_settings()


class ModuleService:
    def __init__(self, db: Client, claude: anthropic.Anthropic):
        self.db = db
        self.claude = claude
        # Initialize embedding service for semantic matching
        self.embedding_service = TagEmbeddingService(claude)
    
    async def get_modules_by_project(self, project_id: str) -> List[dict]:
        """Get all modules for a project"""
        response = self.db.table(Module.table_name)\
            .select("*")\
            .eq("project_id", project_id)\
            .execute()
        
        return [Module.to_dict(row) for row in response.data]
    
    async def get_module_by_id(self, module_id: str) -> Optional[dict]:
        """Get module by ID"""
        response = self.db.table(Module.table_name)\
            .select("*")\
            .eq("id", module_id)\
            .execute()
        
        if response.data:
            return Module.to_dict(response.data[0])
        return None
    
    async def create_module(self, module: ModuleCreate) -> dict:
        """Create new module"""
        data = {
            "project_id": module.project_id,
            "name": module.name,
            "description": module.description,
            "scope": module.scope,
            "dependencies": module.dependencies,
            "features": module.features,
            "requirements": module.requirements,
            "technical_specs": module.technical_specs,
            "generated_by_ai": False,
            # NEW: Support source_type and tags from schema
            "source_type": getattr(module, 'source_type', 'manual_upload'),
            "intent_primary": getattr(module, 'intent_primary', None),
            "tags_metadata": getattr(module, 'tags_metadata', {}),
        }
        
        response = self.db.table(Module.table_name).insert(data).execute()
        return Module.to_dict(response.data[0])
    
    async def update_module(self, module_id: str, module: ModuleUpdate) -> Optional[dict]:
        """Update module"""
        update_data = {}
        
        for field in ['name', 'description', 'scope', 'dependencies', 'features', 'requirements', 'technical_specs']:
            value = getattr(module, field, None)
            if value is not None:
                update_data[field] = value
        
        if not update_data:
            return await self.get_module_by_id(module_id)
        
        response = self.db.table(Module.table_name)\
            .update(update_data)\
            .eq("id", module_id)\
            .execute()
        
        if response.data:
            return Module.to_dict(response.data[0])
        return None
    
    async def delete_module(self, module_id: str) -> bool:
        """Delete module"""
        response = self.db.table(Module.table_name)\
            .delete()\
            .eq("id", module_id)\
            .execute()
        
        return len(response.data) > 0
    
    async def generate_modules_with_ai(
        self,
        project_id: str,
        documentation: str,
        source_type: str = "ai_generated"
    ) -> List[dict]:
        """
        Generate modules using Claude AI with 2-phase approach.
        
        Use this for:
        - Git analyzed repos (complete codebase → direct generation)
        - Any source where we have FULL documentation
        
        Args:
            project_id: Target project ID
            documentation: Complete documentation/analysis
            source_type: 'git_analyzed' or 'ai_generated'
        
        Returns:
            List of created modules
        
        Note: This does NOT search memories. For requirement docs that need
        memory search, use generate_modules_with_memory_search() instead.
        """
        
        print("=" * 80)
        print("PHASE 1: Generating module metadata...")
        print("=" * 80)
        
        # PHASE 1: Generate module metadata
        metadata_prompt = create_module_metadata_prompt(documentation)
        
        metadata_response = self.claude.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=8000,  # Sufficient for metadata of 10+ modules
            temperature=0.7,
            messages=[{"role": "user", "content": metadata_prompt}]
        )
        
        metadata_text = metadata_response.content[0].text.strip()
        print(f"Metadata response length: {len(metadata_text)} chars")
        
        # Extract JSON
        if "```json" in metadata_text:
            metadata_text = metadata_text.split("```json")[1].split("```")[0].strip()
        elif "```" in metadata_text:
            metadata_text = metadata_text.split("```")[1].split("```")[0].strip()
        
        try:
            modules_metadata = json.loads(metadata_text)
            print(f"✅ Phase 1 complete: {len(modules_metadata)} modules identified")
        except json.JSONDecodeError as e:
            print(f"❌ Phase 1 JSON Parse Error: {e}")
            print(f"Problematic JSON:\n{metadata_text[:500]}")
            raise ValueError(f"Phase 1 failed - Invalid JSON: {str(e)}")
        
        # PHASE 2: Generate details for each module
        print("=" * 80)
        print(f"PHASE 2: Generating details for {len(modules_metadata)} modules...")
        print("=" * 80)
        
        created_modules = []
        
        for idx, metadata in enumerate(modules_metadata, 1):
            module_name = metadata.get("name", "Unnamed Module")
            print(f"\n[{idx}/{len(modules_metadata)}] Generating details for: {module_name}")
            
            # Create details prompt
            details_prompt = create_module_details_prompt(
                module_name=metadata.get("name", ""),
                module_description=metadata.get("description", ""),
                module_scope=metadata.get("scope", ""),
                module_dependencies=metadata.get("dependencies", ""),
                documentation=documentation
            )
            
            # Call Claude for details with retry logic
            details_data = None
            phase_2_success = False
            max_retries = 2
            
            for retry in range(max_retries):
                try:
                    if retry > 0:
                        print(f"  🔄 Retry {retry}/{max_retries-1}...")
                    
                    details_response = self.claude.messages.create(
                        model=settings.CLAUDE_MODEL,
                        max_tokens=3072,  # Sufficient for detailed specs of 1 module
                        temperature=0.7,
                        messages=[{"role": "user", "content": details_prompt}]
                    )
                    
                    details_text = details_response.content[0].text.strip()
                    
                    # Debug: Print response snippet
                    print(f"  📝 Response length: {len(details_text)} chars")
                    print(f"  📝 First 200 chars: {details_text[:200]}")
                    
                    # Extract JSON
                    if "```json" in details_text:
                        details_text = details_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in details_text:
                        details_text = details_text.split("```")[1].split("```")[0].strip()
                    
                    # Parse JSON
                    details_data = json.loads(details_text)
                    
                    # Validate all required fields are present and non-empty
                    required_fields = ["features", "requirements", "technical_specs"]
                    missing_or_empty = [
                        field for field in required_fields 
                        if not details_data.get(field) or len(details_data.get(field, "").strip()) < 50
                    ]
                    
                    if missing_or_empty:
                        print(f"  ⚠️ Incomplete fields: {missing_or_empty}")
                        raise ValueError(f"Fields too short or missing: {missing_or_empty}")
                    
                    print(f"  ✅ Details generated successfully ({len(details_text)} chars)")
                    phase_2_success = True
                    break  # Success, exit retry loop
                    
                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON Parse Error (attempt {retry+1}/{max_retries}): {e}")
                    print(f"  📄 Problematic JSON:\n{details_text[:500] if 'details_text' in locals() else 'N/A'}")
                    if retry == max_retries - 1:
                        # Last retry failed
                        details_data = None
                        
                except Exception as e:
                    print(f"  ❌ Error (attempt {retry+1}/{max_retries}): {e}")
                    if retry == max_retries - 1:
                        details_data = None
            
            # If all retries failed, use placeholder
            if not details_data or not phase_2_success:
                print(f"  💥 Phase 2 FAILED after {max_retries} attempts")
                details_data = {
                    "features": "Details generation failed - please regenerate",
                    "requirements": "Details generation failed - please regenerate",
                    "technical_specs": "Details generation failed - please regenerate"
                }
            
            # Combine metadata + details and save to database
            full_module_data = {
                "project_id": project_id,
                "name": metadata.get("name", "Unnamed Module"),
                "description": metadata.get("description", "No description"),
                "scope": metadata.get("scope", "Scope not specified"),
                "dependencies": metadata.get("dependencies", "Dependencies not specified"),
                "features": details_data.get("features", "Features not specified"),
                "requirements": details_data.get("requirements", "Requirements not specified"),
                "technical_specs": details_data.get("technical_specs", "Technical specs not specified"),
                "generated_by_ai": True,
                "source_type": source_type,
                # No reuse_type field - FE checks reused_from_module_id instead (Issue #4)
                "generation_metadata": {
                    "model": settings.CLAUDE_MODEL,
                    "prompt_version": "3.0_two_phase",
                    "phase_1_success": True,
                    "phase_2_success": phase_2_success,
                    "generation_mode": "direct"  # Direct generation without memory search
                }
            }
            
            response = self.db.table(Module.table_name).insert(full_module_data).execute()
            created_module = Module.to_dict(response.data[0])
            created_modules.append(created_module)
            
            # 🆕 AUTO-GENERATE TAGS for searchability
            try:
                print(f"  🏷️ Auto-generating tags for module: {created_module['name']}")
                await self.generate_tags_for_module(created_module['id'])
                print(f"  ✅ Tags generated successfully")
            except Exception as tag_error:
                print(f"  ⚠️ Tag generation failed (non-critical): {tag_error}")
                # Don't fail module creation if tagging fails
        
        print("=" * 80)
        print(f"✅ ALL PHASES COMPLETE: {len(created_modules)} modules created")
        print("=" * 80)
        
        return created_modules
    
    async def regenerate_module_details(
        self,
        module_id: str,
        module: dict,
        documentation: str
    ) -> dict:
        """
        Regenerate Phase 2 details for a module that failed or has incomplete data.
        Only regenerates features, requirements, and technical_specs.
        """
        print("=" * 80)
        print(f"REGENERATING PHASE 2 for module: {module.get('name')}")
        print("=" * 80)
        
        # Create details prompt using existing metadata
        details_prompt = create_module_details_prompt(
            module_name=module.get("name", ""),
            module_description=module.get("description", ""),
            module_scope=module.get("scope", ""),
            module_dependencies=module.get("dependencies", ""),
            documentation=documentation
        )
        
        # Call Claude for details
        try:
            details_response = self.claude.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=3072,
                temperature=0.7,
                messages=[{"role": "user", "content": details_prompt}]
            )
            
            details_text = details_response.content[0].text.strip()
            print(f"Details response length: {len(details_text)} chars")
            
            # Extract JSON
            if "```json" in details_text:
                details_text = details_text.split("```json")[1].split("```")[0].strip()
            elif "```" in details_text:
                details_text = details_text.split("```")[1].split("```")[0].strip()
            
            details_data = json.loads(details_text)
            print(f"✅ Details regenerated successfully")
            
            # Update module in database
            update_data = {
                "features": details_data.get("features", "Features not specified"),
                "requirements": details_data.get("requirements", "Requirements not specified"),
                "technical_specs": details_data.get("technical_specs", "Technical specs not specified"),
                "generation_metadata": {
                    "model": settings.CLAUDE_MODEL,
                    "prompt_version": "3.0_two_phase",
                    "phase_1_success": True,
                    "phase_2_success": True,
                    "regenerated": True
                }
            }
            
            response = self.db.table(Module.table_name)\
                .update(update_data)\
                .eq("id", module_id)\
                .execute()
            
            print(f"✅ Module {module_id} updated in database")
            
            if response.data:
                return Module.to_dict(response.data[0])
            return None
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"❌ Failed to regenerate details: {e}")
            raise ValueError(f"Phase 2 regeneration failed: {str(e)}")
    
    
    async def generate_modules_with_memory_search(
        self,
        project_id: str,
        requirements_doc: str,
        config_name: str = "default",
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Generate modules for manual requirements using memory search.
        
        WORKFLOW:
        1. Extract intent from requirements → Generate target tags
        2. Search memories for similar modules (top K)
        3. For high scores (≥0.85): Direct reuse with customization
        4. For medium scores (0.6-0.85): Deep analysis + combine patterns
        5. For low scores (<0.6): Generate from scratch
        
        Use this for:
        - Manually uploaded requirement docs
        - New project ideas without existing code
        
        Args:
            project_id: Target project
            requirements_doc: User's requirement document (not full codebase)
            config_name: Scoring config to use
            top_k: Number of top matches to analyze deeply
        
        Returns:
            {
                "modules": [...created modules...],
                "reuse_summary": {
                    "direct_reuse": 2,
                    "logic_reference": 3,
                    "new_gen": 1
                },
                "top_matches": [...search results for reference...]
            }
        """
        
        print("=" * 80)
        print("MEMORY-BASED MODULE GENERATION")
        print("=" * 80)
        
        # STEP 1: Extract target tags from requirements
        print("\n📋 STEP 1: Extracting intent tags from requirements...")
        target_tags = await self._extract_tags_from_requirements(requirements_doc)
        print(f"✅ Target tags extracted:")
        print(f"   L1 Intent: {target_tags.get('L1_intent', {}).get('tag')}")
        print(f"   L2 Constraint: {target_tags.get('L2_constraint', {}).get('tag')}")
        print(f"   L3 Context: {target_tags.get('L3_context', {}).get('tag')}")
        
        # STEP 2: Search for similar modules
        print(f"\n🔍 STEP 2: Searching memories (top {top_k})...")
        search_results = await self.search_similar_modules(
            target_tags=target_tags,
            project_id=project_id,  # Exclude current project
            config_name=config_name,
            limit=top_k * 2  # Get more for analysis
        )
        
        top_matches = search_results['matches'][:top_k]
        print(f"✅ Found {len(top_matches)} top matches")
        
        # STEP 3: Analyze and generate modules based on scores
        print(f"\n🎯 STEP 3: Analyzing matches and generating modules...")
        
        created_modules = []
        reuse_summary = {
            "direct": 0,
            "partial_reuse": 0,
            "new_gen": 0
        }
        
        # Group matches by strategy (using new format)
        direct_matches = [m for m in top_matches if m['strategy'] == 'direct']
        partial_matches = [m for m in top_matches if m['strategy'] == 'partial_reuse']
        new_gen_needed = len(top_matches) == 0 or all(m['similarity']['weighted_score'] < 0.5 for m in top_matches)
        
        # STRATEGY 1: Direct Reuse (weighted_score ≥ 0.75)
        if direct_matches:
            print(f"\n✅ DIRECT REUSE: {len(direct_matches)} modules")
            for match in direct_matches:
                module = await self._direct_reuse_module(
                    project_id=project_id,
                    source_module=match['module'],
                    requirements_doc=requirements_doc,
                    match_info=match
                )
                created_modules.append(module)
                reuse_summary["direct"] += 1
        
        # STRATEGY 2: Partial Reuse (weighted_score 0.5-0.75)
        if partial_matches:
            print(f"\n🔄 PARTIAL REUSE: {len(partial_matches)} modules need adaptation")
            combined_module = await self._combine_and_adapt_modules(
                project_id=project_id,
                reference_modules=[m['module'] for m in partial_matches],
                requirements_doc=requirements_doc,
                match_details=partial_matches
            )
            created_modules.extend(combined_module)
            reuse_summary["partial_reuse"] += len(combined_module)
        
        # STRATEGY 3: New Generation (weighted_score < 0.5 or no matches)
        if new_gen_needed:
            print(f"\n🆕 NEW GENERATION: No suitable matches, generating from scratch")
            new_modules = await self.generate_modules_with_ai(
                project_id=project_id,
                documentation=requirements_doc,
                source_type="ai_generated"
            )
            created_modules.extend(new_modules)
            reuse_summary["new_gen"] += len(new_modules)
        
        # 🆕 AUTO-GENERATE TAGS for all created modules
        print("\n🏷️ Auto-generating tags for all modules...")
        for module in created_modules:
            try:
                print(f"  → Tagging: {module['name']}")
                await self.generate_tags_for_module(module['id'])
            except Exception as tag_error:
                print(f"  ⚠️ Tag generation failed for {module['name']} (non-critical): {tag_error}")
        
        print("=" * 80)
        print(f"✅ GENERATION COMPLETE: {len(created_modules)} modules created")
        print(f"   📊 Summary: {reuse_summary}")
        print("=" * 80)
        
        return {
            "modules": created_modules,
            "reuse_summary": reuse_summary,
            "top_matches": top_matches,
            "message": f"Created {len(created_modules)} modules using hybrid approach"
        }
    
    
    async def generate_modules_with_per_module_search(
        self,
        project_id: str,
        requirements_doc: str,
        config_name: str = "default",
        top_k_per_module: int = 3
    ) -> Dict[str, Any]:
        """
        🆕 ISSUE #3 SOLUTION: Generate modules with PER-MODULE semantic search.
        
        NEW WORKFLOW (More Accurate):
        1. Break requirements into module outlines (4-8 modules)
        2. For EACH module:
           - Extract tags from module description (not entire requirements)
           - Search for similar modules using module-specific tags
           - Reuse/adapt based on similarity
        3. Auto-tag all created modules
        
        WHY THIS IS BETTER:
        - Auth module searches for "auth" intent → finds Auth modules (not Inventory)
        - Inventory module searches for "inventory" intent → finds Inventory modules
        - More precise L1 matching per module responsibility
        
        Args:
            project_id: Target project
            requirements_doc: User's requirement document
            config_name: Scoring config to use
            top_k_per_module: Top matches to consider per module
        
        Returns:
            {
                "modules": [...created modules...],
                "reuse_summary": {...},
                "module_search_details": [...]
            }
        """
        
        print("=" * 80)
        print("PER-MODULE MEMORY-BASED GENERATION (ISSUE #3 SOLUTION)")
        print("=" * 80)
        
        # STEP 1: Break requirements into module outlines
        print("\n📋 STEP 1: Breaking requirements into module outlines...")
        modules_outline = await self._break_requirements_into_modules(requirements_doc)
        print(f"✅ Identified {len(modules_outline)} modules:")
        for i, m in enumerate(modules_outline, 1):
            print(f"   {i}. {m['name']}")
        
        # STEP 2: For EACH module, extract tags and search
        print("\n🔍 STEP 2: Per-module tagging and searching...")
        created_modules = []
        reuse_summary = {"direct": 0, "partial_reuse": 0, "new_gen": 0}
        module_search_details = []
        
        for idx, module_outline in enumerate(modules_outline, 1):
            print(f"\n{'='*60}")
            print(f"MODULE {idx}/{len(modules_outline)}: {module_outline['name']}")
            print(f"{'='*60}")
            
            # 2A: Extract tags for THIS specific module
            print(f"  🏷️ Extracting tags for: {module_outline['name']}")
            module_tags = await self._extract_tags_from_module_description(
                module_name=module_outline['name'],
                module_description=module_outline['description']
            )
            print(f"  ✅ Tags: L1={module_tags['L1_intent']['tag']}, L2={module_tags['L2_constraint']['tag']}, L3={module_tags['L3_context']['tag']}")
            
            # 2B: Search for similar modules using module-specific tags
            print(f"  🔍 Searching for similar modules...")
            search_results = await self.search_similar_modules(
                target_tags=module_tags,
                project_id=project_id,
                config_name=config_name,
                limit=top_k_per_module
            )
            
            top_matches = search_results['matches'][:top_k_per_module]
            
            if not top_matches:
                print(f"  📭 No matches found → Will generate new module")
                strategy = "new_gen"
            else:
                best_match = top_matches[0]
                strategy = best_match['strategy']
                sim_score = best_match['similarity']['weighted_score']
                print(f"  ✅ Best match: {best_match['module']['name']} (score: {sim_score:.1%}, strategy: {strategy})")
            
            # 2C: Generate module based on search results
            if strategy == "direct" and top_matches:
                print(f"  ♻️ Direct reuse from: {top_matches[0]['module']['name']}")
                module = await self._direct_reuse_module(
                    project_id=project_id,
                    source_module=top_matches[0]['module'],
                    requirements_doc=f"{module_outline['name']}: {module_outline['description']}\n\nFull Context:\n{requirements_doc[:1500]}",
                    match_info=top_matches[0]
                )
                reuse_summary["direct"] += 1
                
            elif strategy == "partial_reuse" and top_matches:
                print(f"  🔄 Partial reuse from {len(top_matches)} references")
                adapted_modules = await self._combine_and_adapt_modules(
                    project_id=project_id,
                    reference_modules=[m['module'] for m in top_matches],
                    requirements_doc=f"{module_outline['name']}: {module_outline['description']}\n\nFull Context:\n{requirements_doc[:1500]}",
                    match_details=top_matches
                )
                module = adapted_modules[0] if adapted_modules else None
                if module:
                    reuse_summary["partial_reuse"] += 1
                    
            else:
                print(f"  🆕 Generating new module from scratch")
                # Generate single module
                new_modules = await self.generate_modules_with_ai(
                    project_id=project_id,
                    documentation=f"{module_outline['name']}: {module_outline['description']}\n\nFull Context:\n{requirements_doc[:1500]}",
                    source_type="ai_generated"
                )
                module = new_modules[0] if new_modules else None
                if module:
                    reuse_summary["new_gen"] += 1
            
            if module:
                created_modules.append(module)
                module_search_details.append({
                    "module_name": module['name'],
                    "extracted_tags": module_tags,
                    "top_matches": top_matches,
                    "strategy_used": strategy
                })
        
        # STEP 3: Auto-tag all created modules
        print("\n🏷️ STEP 3: Auto-generating tags for all modules...")
        for module in created_modules:
            try:
                print(f"  → Tagging: {module['name']}")
                await self.generate_tags_for_module(module['id'])
            except Exception as tag_error:
                print(f"  ⚠️ Tag generation failed for {module['name']}: {tag_error}")
        
        print("\n" + "=" * 80)
        print(f"✅ GENERATION COMPLETE: {len(created_modules)} modules created")
        print(f"   📊 Reuse Summary: {reuse_summary}")
        print("=" * 80)
        
        return {
            "modules": created_modules,
            "reuse_summary": reuse_summary,
            "module_search_details": module_search_details,
            "message": f"Created {len(created_modules)} modules using per-module search"
        }
    
    
    # ================================================================
    # HELPER METHODS for Memory-Based Generation
    # ================================================================
    
    async def _break_requirements_into_modules(
        self,
        requirements_doc: str
    ) -> List[Dict[str, str]]:
        """
        ISSUE #3 SOLUTION: Break requirements into module outlines BEFORE tagging.
        This allows per-module tagging for more accurate similarity matching.
        
        Returns:
            [
                {
                    "name": "Module Name",
                    "description": "Brief description of what this module does (50-100 words)"
                }
            ]
        """
        
        prompt = f"""Analyze these requirements and break them down into logical modules.

Requirements:
{requirements_doc[:3000]}

TASK: Identify 4-8 core modules needed to fulfill these requirements.

RULES:
- Each module should have a single clear responsibility
- Module name: Descriptive and concise (3-5 words)
- Description: 50-100 words explaining WHAT it does and WHY it's needed

Return ONLY JSON array:
[
  {{
    "name": "Module Name Here",
    "description": "Clear description of functionality, purpose, and key responsibilities..."
  }}
]
"""
        
        message = self.claude.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=2048,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        modules_outline = json.loads(response_text)
        print(f"✅ Broke requirements into {len(modules_outline)} modules")
        return modules_outline
    
    
    async def _extract_tags_from_module_description(
        self,
        module_name: str,
        module_description: str
    ) -> Dict[str, Dict]:
        """
        Extract tags for a SINGLE module (not entire requirements).
        This gives more accurate L1 matching per module.
        
        Args:
            module_name: Name of the module
            module_description: Description of what this module does
        
        Returns:
            {"L1_intent": {"tag": "...", "confidence": ..., "reasoning": "..."}, ...}
        """
        
        prompt = f"""Extract classification tags for this specific module.

Module Name: {module_name}
Module Description: {module_description}

**TAGGING RULES:**
- L1_intent: ONE word for THIS module's primary function (auth, inventory, payment, analytics, etc.)
- L2_constraint: ONE word for main tech stack (nodejs, python, react, postgresql, etc.)
- L3_context: ONE word for primary domain (ecommerce, fintech, healthcare, manufacturing, etc.)
- Use standard lowercase terms with hyphens for compounds
- **REASONING IS CRITICAL**: Explain why you chose this tag, mention secondary aspects

Return ONLY JSON:
{{
  "L1_intent": {{"tag": "chosen-tag", "confidence": 0.95, "reasoning": "This module's PRIMARY responsibility is X because it handles Y. Secondary aspects: A, B."}},
  "L2_constraint": {{"tag": "chosen-tag", "confidence": 0.90, "reasoning": "Main technology is X. Also uses Y for Z purpose."}},
  "L3_context": {{"tag": "chosen-tag", "confidence": 0.85, "reasoning": "Primary domain is X. May also serve Y and Z sectors."}}
}}
"""
        
        message = self.claude.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1024,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        print(f"📝 Raw response ({len(response_text)} chars): {response_text[:300]}...")
        
        # Extract JSON from markdown blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        print(f"📝 Extracted JSON ({len(response_text)} chars): {response_text[:300]}...")
        
        # Try to parse JSON
        try:
            tags = json.loads(response_text)
            print(f"✅ Successfully parsed tags")
            return tags
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error at line {e.lineno}, column {e.colno}: {e.msg}")
            print(f"📄 Full response text:\n{response_text}")
            
            # Retry with more explicit format instruction
            print("🔄 Retrying with strict format...")
            retry_prompt = f"""Extract classification tags from this module. Return ONLY valid JSON (no extra text, no comments).

Module Name: {module_name}
Module Description: {module_description}

**CRITICAL RULES:**
1. L1_intent: THIS module's PRIMARY function (ONE word: auth, inventory, payment, analytics, procurement, etc.)
2. L2_constraint: MAIN TECHNOLOGY/LANGUAGE (ONE word: nodejs, python, go, java, react, postgresql, etc.)
   - NOT business model (don't use "saas", "b2b", "api")
   - Extract from description or infer from context
3. L3_context: PRIMARY business domain (ONE word: manufacturing, ecommerce, fintech, healthcare, etc.)

**Return format (EXACT structure, no markdown):**
{{"L1_intent":{{"tag":"function-name","confidence":0.95,"reasoning":"explanation"}},"L2_constraint":{{"tag":"tech-name","confidence":0.90,"reasoning":"explanation"}},"L3_context":{{"tag":"domain-name","confidence":0.85,"reasoning":"explanation"}}}}
"""
            
            retry_message = self.claude.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1024,
                temperature=0.2,  # Lower temperature for stricter format
                messages=[{"role": "user", "content": retry_prompt}]
            )
            
            retry_text = retry_message.content[0].text.strip()
            print(f"🔄 Retry response ({len(retry_text)} chars): {retry_text[:300]}...")
            
            # Clean up response
            if "```json" in retry_text:
                retry_text = retry_text.split("```json")[1].split("```")[0].strip()
            elif "```" in retry_text:
                retry_text = retry_text.split("```")[1].split("```")[0].strip()
            
            try:
                tags = json.loads(retry_text)
                print(f"✅ Retry successful!")
                return tags
            except json.JSONDecodeError as retry_error:
                print(f"❌ Retry also failed: {retry_error}")
                print(f"📄 Retry response:\n{retry_text}")
                
                # Fallback: Return generic tags
                print("⚠️ Using fallback generic tags")
                return {
                    "L1_intent": {
                        "tag": "business-logic",
                        "confidence": 0.5,
                        "reasoning": "Fallback tag due to parsing error. Please review requirements."
                    },
                    "L2_constraint": {
                        "tag": "python",
                        "confidence": 0.5,
                        "reasoning": "Fallback tag. Tech stack not clearly identified."
                    },
                    "L3_context": {
                        "tag": "general",
                        "confidence": 0.5,
                        "reasoning": "Fallback tag. Domain not clearly specified."
                    }
                }
    
    
    async def _extract_tags_from_requirements(
        self,
        requirements_doc: str
    ) -> Dict[str, Dict]:
        """
        Extract target tags from requirement document (single tag per layer).
        
        NOTE: This is the OLD approach (tag entire requirements).
        For better accuracy, use _break_requirements_into_modules + _extract_tags_from_module_description.
        
        Returns same format as generate_tags_for_module for consistency.
        """
        
        prompt = f"""Analyze these requirements and extract PRIMARY classification tag per layer.

Requirements:
{requirements_doc[:3000]}

**TAGGING RULES:**
- L1_intent: ONE word for primary business function (auth, inventory, payment, analytics, etc.)
- L2_constraint: ONE word for main tech stack (nodejs, python, react, postgresql, etc.)
- L3_context: ONE word for primary domain (ecommerce, fintech, healthcare, manufacturing, etc.)
- Use standard lowercase terms with hyphens for compounds
- **REASONING IS CRITICAL**: Explain your choice, mention secondary aspects

Return ONLY JSON:
{{
  "L1_intent": {{"tag": "chosen-tag", "confidence": 0.95, "reasoning": "Detailed explanation with secondary aspects..."}},
  "L2_constraint": {{"tag": "chosen-tag", "confidence": 0.90, "reasoning": "Detailed explanation with alternative tech..."}},
  "L3_context": {{"tag": "chosen-tag", "confidence": 0.85, "reasoning": "Detailed explanation with related domains..."}}
}}
"""
        
        message = self.claude.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1024,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        print(f"📝 Raw response ({len(response_text)} chars): {response_text[:300]}...")
        
        # Extract JSON from markdown blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        print(f"📝 Extracted JSON ({len(response_text)} chars): {response_text[:300]}...")
        
        # Try to parse JSON
        try:
            tags = json.loads(response_text)
            print(f"✅ Successfully parsed requirements tags")
            return tags
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error at line {e.lineno}, column {e.colno}: {e.msg}")
            print(f"📄 Full response text:\n{response_text}")
            
            # Retry with more explicit format instruction
            print("🔄 Retrying with strict format...")
            retry_prompt = f"""Extract classification tags from these requirements. Return ONLY valid JSON (no extra text, no comments).

Requirements:
{requirements_doc[:2000]}

**CRITICAL RULES:**
1. L1_intent: PRIMARY business function (ONE word: inventory, auth, payment, analytics, procurement, etc.)
2. L2_constraint: MAIN TECHNOLOGY/LANGUAGE used (ONE word: nodejs, python, go, java, react, postgresql, etc.)
   - NOT business model (don't use "saas", "b2b", "api")
   - Look for "backend", "tech stack", "built with" mentions
   - If multiple tech mentioned, choose PRIMARY backend language
3. L3_context: PRIMARY business domain (ONE word: manufacturing, ecommerce, fintech, healthcare, etc.)

**Return format (EXACT structure, no markdown):**
{{"L1_intent":{{"tag":"function-name","confidence":0.95,"reasoning":"why this is primary function"}},"L2_constraint":{{"tag":"tech-name","confidence":0.90,"reasoning":"why this is main technology"}},"L3_context":{{"tag":"domain-name","confidence":0.85,"reasoning":"why this is primary domain"}}}}
"""
            
            retry_message = self.claude.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1024,
                temperature=0.2,
                messages=[{"role": "user", "content": retry_prompt}]
            )
            
            retry_text = retry_message.content[0].text.strip()
            print(f"🔄 Retry response ({len(retry_text)} chars): {retry_text[:300]}...")
            
            # Clean up response
            if "```json" in retry_text:
                retry_text = retry_text.split("```json")[1].split("```")[0].strip()
            elif "```" in retry_text:
                retry_text = retry_text.split("```")[1].split("```")[0].strip()
            
            try:
                tags = json.loads(retry_text)
                print(f"✅ Retry successful!")
                return tags
            except json.JSONDecodeError as retry_error:
                print(f"❌ Retry also failed: {retry_error}")
                print(f"📄 Retry response:\n{retry_text}")
                
                # Fallback: Return generic tags
                print("⚠️ Using fallback generic tags for requirements")
                return {
                    "L1_intent": {
                        "tag": "business-logic",
                        "confidence": 0.5,
                        "reasoning": "Fallback tag due to parsing error. Please review requirements."
                    },
                    "L2_constraint": {
                        "tag": "python",
                        "confidence": 0.5,
                        "reasoning": "Fallback tag. Tech stack not clearly identified from requirements."
                    },
                    "L3_context": {
                        "tag": "general",
                        "confidence": 0.5,
                        "reasoning": "Fallback tag. Domain not clearly specified in requirements."
                    }
                }
    
    
    async def _direct_reuse_module(
        self,
        project_id: str,
        source_module: Dict[str, Any],
        requirements_doc: str,
        match_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Direct reuse: Copy module and customize for new requirements.
        Weighted score ≥ 0.75 means very similar, just need minor tweaks.
        """
        
        weighted_score = match_info['similarity']['weighted_score']
        print(f"   📋 Copying module: {source_module['name']} (score: {weighted_score:.1%})")
        
        # Get layer breakdown for better customization
        layer_scores = match_info['similarity']['layer_scores']
        breakdown = match_info['similarity']['breakdown']
        
        # Build detailed context about what matches and what differs
        match_analysis = f"""
SIMILARITY ANALYSIS:
- Intent Match: {layer_scores['L1_intent']:.0%} ({breakdown['L1_intent']['tag1']} vs {breakdown['L1_intent']['tag2']})
- Tech Match: {layer_scores['L2_constraint']:.0%} ({breakdown['L2_constraint']['tag1']} vs {breakdown['L2_constraint']['tag2']})
- Domain Match: {layer_scores['L3_context']:.0%} ({breakdown['L3_context']['tag1']} vs {breakdown['L3_context']['tag2']})

WHAT TO KEEP: {"Intent/logic" if layer_scores['L1_intent'] >= 0.8 else "General patterns only"}
WHAT TO ADAPT: {"Tech stack to " + breakdown['L2_constraint']['tag1'] if layer_scores['L2_constraint'] < 0.9 else "Minor config only"}
DOMAIN CONTEXT: {"Adjust for " + breakdown['L3_context']['tag1'] if layer_scores['L3_context'] < 0.9 else "Same domain"}
"""
        
        # Customize prompt to adapt module to new requirements
        customize_prompt = f"""You are adapting an existing proven module for new requirements.

SOURCE MODULE (PROVEN DESIGN):
Name: {source_module['name']}
Description: {source_module['description']}
Scope: {source_module.get('scope', 'N/A')}
Features: {source_module.get('features', 'N/A')}
Dependencies: {source_module.get('dependencies', 'N/A')}
Technical Specs: {source_module.get('technical_specs', 'N/A')}

{match_analysis}

NEW REQUIREMENTS (TARGET):
{requirements_doc[:2500]}

TASK: Adapt the source module for the new context. Be SPECIFIC and DETAILED.

RULES:
1. Name: Make it unique and descriptive (not just "Module Name")
2. Description: 2-3 sentences explaining purpose and key value
3. Scope: Define boundaries - what it DOES and DOESN'T do (150-200 words)
4. Dependencies: List specific modules/services it depends on
5. Features: 8-12 concrete features with technical details (not generic phrases)
6. Requirements: Functional + non-functional requirements (performance, security, scalability)
7. Technical Specs: Architecture, APIs, data models, tech stack, integrations (200-300 words)

CRITICAL: If tech stack differs (L2 mismatch), adapt architecture accordingly.
CRITICAL: Make name UNIQUE - check if similar names exist, add differentiator.

Return ONLY valid JSON (no markdown, no comments):
{{"name": "...", "description": "...", "scope": "...", "dependencies": "...", "features": "...", "requirements": "...", "technical_specs": "..."}}"""
        
        message = self.claude.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=4096,  # Increased for detailed responses
            temperature=0.4,  # Lower for more focused output
            messages=[{"role": "user", "content": customize_prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Extract JSON from markdown blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Try to parse JSON with improved retry
        try:
            customized_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            print(f"Response preview: {response_text[:300]}...")
            
            # Retry with more explicit format instruction
            print("🔄 Retrying with strict format...")
            retry_prompt = f"""Adapt this module. Return ONLY valid JSON (no markdown, no extra text).

SOURCE: {source_module['name']} - {source_module.get('description', '')[:200]}
TARGET: {requirements_doc[:800]}

MAKE NAME UNIQUE! Add suffix like "v2", "Pro", "Enhanced", or specific feature name.

Format (copy exactly):
{{"name":"Unique Name Here","description":"2-3 sentences","scope":"What it does and boundaries (100+ words)","dependencies":"List dependencies","features":"8-10 specific features with details","requirements":"Functional and non-functional requirements","technical_specs":"Architecture, APIs, data models, tech stack (150+ words)"}}"""
            
            retry_message = self.claude.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=4096,
                temperature=0.2,
                messages=[{"role": "user", "content": retry_prompt}]
            )
            
            response_text = retry_message.content[0].text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            try:
                customized_data = json.loads(response_text)
                print("✅ Retry successful")
            except json.JSONDecodeError as retry_error:
                print(f"❌ Retry failed: {retry_error}")
                print(f"Using fallback with detailed source data...")
                # Fallback: Use source module with adaptations
                customized_data = {
                    "name": f"{source_module['name']} (Adapted for {breakdown['L3_context']['tag1'].title()})",
                    "description": f"{source_module.get('description', '')} Adapted for {breakdown['L3_context']['tag1']} context with {breakdown['L2_constraint']['tag1']} technology stack.",
                    "scope": source_module.get('scope', 'Provides core functionality for inventory and product management with real-time tracking capabilities.'),
                    "dependencies": source_module.get('dependencies', 'Authentication service, database, API gateway'),
                    "features": source_module.get('features', 'Product management, inventory tracking, real-time updates, reporting'),
                    "requirements": f"Adapted from proven design. Must support {breakdown['L2_constraint']['tag1']} tech stack and {breakdown['L3_context']['tag1']} domain requirements.",
                    "technical_specs": source_module.get('technical_specs', f"RESTful API, {breakdown['L2_constraint']['tag1']} backend, real-time data sync, scalable architecture")
                }
                print(f"⚠️ Fallback module name: {customized_data['name']}")
        
        # Save to database
        module_data = {
            "project_id": project_id,
            **customized_data,
            "generated_by_ai": True,
            "source_type": "reused",
            "reused_from_module_id": source_module['id'],  # FE checks this field for badge (Issue #4)
            "reuse_strategy": "direct",
            # No reuse_type field - FE determines from reused_from_module_id
            "generation_metadata": {
                "model": settings.CLAUDE_MODEL,
                "generation_mode": "direct_reuse",
                "source_module_id": source_module['id'],
                "similarity": match_info['similarity'],
                "strategy": match_info['strategy'],
                "rationale": match_info['rationale']
            }
        }
        
        response = self.db.table(Module.table_name).insert(module_data).execute()
        created_module = Module.to_dict(response.data[0])
        
        # Record reuse history
        await self._record_reuse_history(
            source_module_id=source_module['id'],
            target_module_id=created_module['id'],
            target_project_id=project_id,
            match_info=match_info
        )
        
        print(f"   ✅ Created: {created_module['name']}")
        return created_module
    
    
    async def _combine_and_adapt_modules(
        self,
        project_id: str,
        reference_modules: List[Dict[str, Any]],
        requirements_doc: str,
        match_details: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Logic reference: Deep analysis of multiple modules + combine patterns.
        
        VẤN ĐỀ 2 SOLUTION:
        - Score thấp nhưng có top K matches
        - Mỗi module match 1 khía cạnh khác nhau (L1, L2, L3...)
        - Cần phân tích kỹ xem mỗi module làm gì, triển khai ra sao
        - Combine patterns từ nhiều modules → Tạo module mới phù hợp
        """
        
        print(f"   🔬 Deep analysis of {len(reference_modules)} reference modules...")
        
        # Build comprehensive context from all reference modules
        references_context = ""
        for i, (ref_module, match_detail) in enumerate(zip(reference_modules, match_details), 1):
            sim = match_detail['similarity']
            layer_scores = sim['layer_scores']
            references_context += f"""
REFERENCE MODULE {i}:
Name: {ref_module['name']}
Weighted Similarity: {sim['weighted_score']:.1%}
Layer Scores:
  - L1 Intent: {layer_scores.get('L1_intent', 0):.1%}
  - L2 Constraint: {layer_scores.get('L2_constraint', 0):.1%}
  - L3 Context: {layer_scores.get('L3_context', 0):.1%}

Description: {ref_module.get('description', 'N/A')}
Scope: {ref_module.get('scope', 'N/A')}
Key Features: {ref_module.get('features', 'N/A')[:500]}
Technical Approach: {ref_module.get('technical_specs', 'N/A')[:500]}
Dependencies: {ref_module.get('dependencies', 'N/A')}

STRATEGY: {match_detail['strategy']}
RATIONALE: {match_detail['rationale']}

---
"""
        
        # Advanced prompt for combining patterns
        combine_prompt = f"""You are an expert architect combining patterns from multiple existing modules.

NEW REQUIREMENTS:
{requirements_doc[:3000]}

REFERENCE MODULES (Partial matches - each matches different aspects):
{references_context}

TASK: Analyze what each reference module does well, then SYNTHESIZE new modules.

ANALYSIS STEPS:
1. What does each reference module excel at? (Look at high-scoring layers)
2. Which patterns/approaches are reusable? (Logic, architecture, tech choices)
3. What needs to be adapted for new requirements?
4. Should we combine patterns from multiple references into 1 module?
   Or create separate modules for different concerns?

SYNTHESIS RULES:
- If multiple references solve same problem differently → Pick best approach
- If references cover different concerns → May need multiple modules
- Adapt tech stack to requirements (if requirements specify)
- Keep proven patterns, discard mismatches

Generate 4-8 modules that COMBINE insights from references + meet new requirements.

Return JSON array:
[
  {{
    "name": "Module Name",
    "description": "...",
    "scope": "...",
    "dependencies": "...",
    "features": "...",
    "requirements": "...",
    "technical_specs": "...",
    "synthesis_notes": "How this combines patterns from references..."
  }}
]
"""
        
        message = self.claude.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=8192,  # Need more for multiple modules
            temperature=0.6,  # Slightly creative for synthesis
            messages=[{"role": "user", "content": combine_prompt}]
        )
        
        response_text = message.content[0].text.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        
        modules_data = json.loads(response_text)
        
        # Save all synthesized modules
        created_modules = []
        for module_data in modules_data:
            synthesis_notes = module_data.pop('synthesis_notes', '')
            
            full_data = {
                "project_id": project_id,
                **module_data,
                "generated_by_ai": True,
                "source_type": "reused",
                "reuse_strategy": "logic_reference",
                # No reuse_type - FE will check reused_from_module_id (Issue #4)
                # Note: partial reuse doesn't set reused_from_module_id (multiple sources)
                "generation_metadata": {
                    "model": settings.CLAUDE_MODEL,
                    "generation_mode": "combined_synthesis",
                    "reference_modules": [m['id'] for m in reference_modules],
                    "synthesis_notes": synthesis_notes
                }
            }
            
            response = self.db.table(Module.table_name).insert(full_data).execute()
            created_module = Module.to_dict(response.data[0])
            created_modules.append(created_module)
            
            # Record reuse from all references
            for ref_module in reference_modules:
                await self._record_reuse_history(
                    source_module_id=ref_module['id'],
                    target_module_id=created_module['id'],
                    target_project_id=project_id,
                    match_info={
                        'similarity': {  # Use correct format
                            'weighted_score': 0.7,
                            'layer_scores': {},
                            'breakdown': {}
                        },
                        'strategy': 'partial_reuse',  # Valid strategy value
                        'rationale': f"Combined with {len(reference_modules)} other references"
                    }
                )
            
            print(f"   ✅ Synthesized: {created_module['name']}")
        
        return created_modules
    
    
    async def _record_reuse_history(
        self,
        source_module_id: str,
        target_module_id: str,
        target_project_id: str,
        match_info: Dict[str, Any]
    ) -> None:
        """Record reuse decision in history for analytics"""
        
        from src.modules.module_manager.model import ReuseHistory
        
        sim = match_info.get('similarity', {})
        
        # Get strategy with valid fallback (not 'unknown')
        strategy = match_info.get('strategy', 'new_gen')  # Default to new_gen if missing
        # Validate strategy is one of the allowed values
        valid_strategies = {'direct', 'partial_reuse', 'new_gen'}
        if strategy not in valid_strategies:
            print(f"⚠️ Invalid strategy '{strategy}', defaulting to 'new_gen'")
            strategy = 'new_gen'
        
        history_data = {
            "source_module_id": source_module_id,
            "target_module_id": target_module_id,
            "target_project_id": target_project_id,
            "similarity_score": sim.get('weighted_score', 0.0),
            "score_breakdown": {
                "weighted_score": sim.get('weighted_score', 0.0),
                "layer_scores": sim.get('layer_scores', {}),
                "breakdown": sim.get('breakdown', {})
            },
            "reuse_strategy": strategy,
            "decision_rationale": match_info.get('rationale', ''),
            "ai_model": settings.CLAUDE_MODEL
        }
        
        try:
            self.db.table(ReuseHistory.table_name).insert(history_data).execute()
        except Exception as e:
            print(f"⚠️ Failed to record reuse history: {e}")
            # Don't fail the whole operation if history recording fails
    
    
    # ================================================================
    # NEW: Tag Generation & Similarity Search Methods
    # ================================================================
    
    async def generate_tags_for_module(
        self,
        module_id: str
    ) -> Dict[str, Any]:
        """
        Generate 4-layer tags for a module using AI.
        
        Args:
            module_id: Module to generate tags for
        
        Returns:
            {
                "module_id": str,
                "tags_generated": int,
                "tags_metadata": {...},
                "message": str
            }
        """
        
        # Get module data
        module = await self.get_module_by_id(module_id)
        if not module:
            raise ValueError(f"Module {module_id} not found")
        
        print(f"🏷️ Generating tags for module: {module['name']}")
        
        # Create prompt
        prompt = create_tag_generation_prompt(module)
        
        # Call Claude API
        message = self.claude.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=2048,
            temperature=0.3,  # Low temp for consistent tagging
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Parse JSON response
        try:
            # Handle markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            tags_data = json.loads(response_text)
            print(f"✅ Parsed tags: {json.dumps(tags_data, indent=2)[:200]}...")
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse tags JSON: {e}")
            print(f"Response: {response_text[:500]}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        
        # Save SINGLE tags to module_tags table (L1, L2, L3 only - no L4)
        tags_saved = 0
        for layer_key in ['L1_intent', 'L2_constraint', 'L3_context']:
            tag_obj = tags_data.get(layer_key)
            if not tag_obj or not isinstance(tag_obj, dict):
                continue
            
            tag_value = tag_obj.get('tag')
            confidence = tag_obj.get('confidence', 0.8)
            reasoning = tag_obj.get('reasoning', '')
            
            if not tag_value:
                continue
            
            # Insert into module_tags table (single tag per layer)
            tag_data = {
                "module_id": module_id,
                "layer": layer_key,
                "tag_value": tag_value,
                "confidence_score": confidence,
                "tag_metadata": {"reasoning": reasoning},
                "assigned_by": "ai"
            }
            
            try:
                self.db.table(ModuleTag.table_name).insert(tag_data).execute()
                tags_saved += 1
            except Exception as e:
                # Might be duplicate - skip
                print(f"⚠️ Failed to save tag {tag_value}: {e}")
        
        # Update module's tags_metadata field (denormalized for fast access)
        update_data = {
            "tags_metadata": tags_data,
            "intent_primary": tags_data.get('L1_intent', {}).get('tag') if isinstance(tags_data.get('L1_intent'), dict) else None
        }
        
        self.db.table(Module.table_name)\
            .update(update_data)\
            .eq("id", module_id)\
            .execute()
        
        print(f"✅ Saved {tags_saved} tags to database")
        
        return {
            "module_id": module_id,
            "tags_generated": tags_saved,
            "tags_metadata": tags_data,
            "message": f"Successfully generated {tags_saved} tags across 4 layers"
        }
    
    
    async def search_similar_modules(
        self,
        target_tags: Dict[str, Dict],
        project_id: Optional[str] = None,
        config_name: str = 'default',
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for modules using semantic similarity (single tag per layer).
        
        Args:
            target_tags: Target tags {"L1_intent": {"tag": "auth", ...}, ...}
            project_id: Exclude modules from this project
            config_name: Scoring config (currently uses default weights)
            limit: Max results
        
        Returns:
            {
                "matches": [
                    {
                        "module": {...},
                        "similarity": {"weighted_score": 0.87, "layer_scores": {...}},
                        "strategy": "direct",
                        "rationale": "...",
                        "details": {...}
                    }
                ],
                "total_searched": 42
            }
        """
        
        print(f"🔍 Semantic search for: L1={target_tags.get('L1_intent', {}).get('tag')}, L2={target_tags.get('L2_constraint', {}).get('tag')}, L3={target_tags.get('L3_context', {}).get('tag')}")
        
        # Query all modules with tags (exclude current project)
        query = self.db.table(Module.table_name)\
            .select("*")\
            .not_.is_("tags_metadata", "null")
        
        if project_id:
            query = query.neq("project_id", project_id)
        
        modules_response = query.execute()
        candidate_modules = [Module.to_dict(row) for row in modules_response.data]
        
        print(f"📦 Found {len(candidate_modules)} candidates with tags")
        
        # Use semantic ranking via find_similar_modules from embedding_service
        ranked_results = self.embedding_service.find_similar_modules(
            query_tags=target_tags,
            candidate_modules=candidate_modules,
            threshold=0.3,  # Include low matches for learning
            top_k=limit
        )
        
        print(f"✅ Top {len(ranked_results)} matches:")
        for i, result in enumerate(ranked_results[:3], 1):
            sim = result['similarity']
            print(f"   {i}. {result['module']['name']}: {sim['weighted_score']:.1%} (L1={sim['layer_scores']['L1_intent']:.1%}, L2={sim['layer_scores']['L2_constraint']:.1%}, L3={sim['layer_scores']['L3_context']:.1%})")
        
        # Determine strategy for each match
        matches = []
        for result in ranked_results:
            strategy, rationale, details = determine_reuse_strategy_simple(result['similarity'])
            matches.append({
                "module": result['module'],
                "similarity": result['similarity'],
                "strategy": strategy,
                "rationale": rationale,
                "details": details
            })
        
        return {
            "matches": matches,
            "total_searched": len(candidate_modules)
        }
    
    
    async def get_scoring_configs(
        self,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get available scoring weight configurations"""
        
        query = self.db.table(ScoringWeightsConfig.table_name).select("*")
        
        if active_only:
            query = query.eq("is_active", True)
        
        response = query.order("is_default", desc=True).execute()
        
        return [ScoringWeightsConfig.to_dict(row) for row in response.data]
