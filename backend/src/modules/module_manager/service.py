"""
Module manager service
"""
from typing import List, Optional
import json
from supabase import Client
import anthropic
from src.modules.module_manager.schema import ModuleCreate, ModuleUpdate
from src.modules.module_manager.model import Module
from src.modules.module_manager.utils import create_module_generation_prompt
from src.core.config import get_settings

settings = get_settings()


class ModuleService:
    def __init__(self, db: Client, claude: anthropic.Anthropic):
        self.db = db
        self.claude = claude
    
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
        documentation: str
    ) -> List[dict]:
        """Generate modules using Claude AI based on project documentation"""
        
        # Create prompt
        prompt = create_module_generation_prompt(documentation)
        
        # Call Claude API
        message = self.claude.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Parse response
        response_text = message.content[0].text
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        modules_data = json.loads(response_text)
        
        # Store modules in database
        created_modules = []
        for module_data in modules_data:
            data = {
                "project_id": project_id,
                "name": module_data.get("name"),
                "description": module_data.get("description"),
                "scope": module_data.get("scope"),
                "dependencies": module_data.get("dependencies"),
                "features": module_data.get("features"),
                "requirements": module_data.get("requirements"),
                "technical_specs": module_data.get("technical_specs"),
                "generated_by_ai": True,
                "generation_metadata": {
                    "model": settings.CLAUDE_MODEL,
                    "prompt_version": "1.0"
                }
            }
            
            response = self.db.table(Module.table_name).insert(data).execute()
            created_modules.append(Module.to_dict(response.data[0]))
        
        return created_modules
