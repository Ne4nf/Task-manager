"""
Project service
"""
from typing import List, Optional
from supabase import Client
from src.modules.projects.schema import ProjectCreate, ProjectUpdate
from src.modules.projects.model import Project


class ProjectService:
    def __init__(self, db: Client):
        self.db = db
    
    async def get_all_projects(self, user_id: Optional[str] = None) -> List[dict]:
        """Get all projects"""
        query = self.db.table(Project.table_name).select("*")
        
        if user_id:
            query = query.eq("created_by", user_id)
        
        response = query.execute()
        return [Project.to_dict(row) for row in response.data]
    
    async def get_project_by_id(self, project_id: str) -> Optional[dict]:
        """Get project by ID"""
        response = self.db.table(Project.table_name).select("*").eq("id", project_id).execute()
        
        if response.data:
            return Project.to_dict(response.data[0])
        return None
    
    async def create_project(self, project: ProjectCreate, user_id: str) -> dict:
        """Create new project"""
        data = {
            "name": project.name,
            "description": project.description,
            "domain": project.domain,
            "created_by": user_id,
            "status": "active",
        }
        
        response = self.db.table(Project.table_name).insert(data).execute()
        return Project.to_dict(response.data[0])
    
    async def update_project(self, project_id: str, project: ProjectUpdate) -> Optional[dict]:
        """Update project"""
        update_data = {}
        
        if project.name is not None:
            update_data["name"] = project.name
        if project.description is not None:
            update_data["description"] = project.description
        if project.domain is not None:
            update_data["domain"] = project.domain
        if project.status is not None:
            update_data["status"] = project.status
        
        if not update_data:
            return await self.get_project_by_id(project_id)
        
        response = self.db.table(Project.table_name).update(update_data).eq("id", project_id).execute()
        
        if response.data:
            return Project.to_dict(response.data[0])
        return None
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        response = self.db.table(Project.table_name).delete().eq("id", project_id).execute()
        return len(response.data) > 0
