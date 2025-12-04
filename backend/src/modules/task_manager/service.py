"""
Task manager service
"""
from typing import List, Optional
import json
from supabase import Client
import anthropic
from src.modules.task_manager.schema import TaskCreate, TaskUpdate
from src.modules.task_manager.model import Task
from src.modules.task_manager.utils import create_task_generation_prompt
from src.core.config import get_settings

settings = get_settings()


class TaskService:
    def __init__(self, db: Client, claude: anthropic.Anthropic):
        self.db = db
        self.claude = claude
    
    async def get_tasks_by_module(self, module_id: str) -> List[dict]:
        """Get all tasks for a module"""
        response = self.db.table(Task.table_name)\
            .select("*")\
            .eq("module_id", module_id)\
            .execute()
        
        return [Task.to_dict(row) for row in response.data]
    
    async def get_task_by_id(self, task_id: str) -> Optional[dict]:
        """Get task by ID"""
        response = self.db.table(Task.table_name)\
            .select("*")\
            .eq("id", task_id)\
            .execute()
        
        if response.data:
            return Task.to_dict(response.data[0])
        return None
    
    async def create_task(self, task: TaskCreate) -> dict:
        """Create new task"""
        data = {
            "module_id": task.module_id,
            "name": task.name,
            "description": task.description,
            "assignee": task.assignee,
            "status": task.status,
            "priority": task.priority,
            "difficulty": task.difficulty,
            "time_estimate": task.time_estimate,
            "quality_score": task.quality_score,
            "autonomy": task.autonomy,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "generated_by_ai": False,
        }
        
        response = self.db.table(Task.table_name).insert(data).execute()
        return Task.to_dict(response.data[0])
    
    async def update_task(self, task_id: str, task: TaskUpdate) -> Optional[dict]:
        """Update task"""
        update_data = {}
        
        for field in ['name', 'description', 'assignee', 'status', 'priority', 
                      'difficulty', 'time_estimate', 'actual_time', 'quality_score', 
                      'autonomy', 'due_date']:
            value = getattr(task, field, None)
            if value is not None:
                # Convert date to ISO string for JSON serialization
                if field == 'due_date' and value is not None:
                    update_data[field] = value.isoformat() if hasattr(value, 'isoformat') else value
                else:
                    update_data[field] = value
        
        if not update_data:
            return await self.get_task_by_id(task_id)
        
        response = self.db.table(Task.table_name)\
            .update(update_data)\
            .eq("id", task_id)\
            .execute()
        
        if response.data:
            return Task.to_dict(response.data[0])
        return None
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        response = self.db.table(Task.table_name)\
            .delete()\
            .eq("id", task_id)\
            .execute()
        
        return len(response.data) > 0
    
    async def generate_tasks_with_ai(
        self,
        module_id: str,
        module_data: dict
    ) -> List[dict]:
        """Generate tasks using Claude AI based on module information"""
        
        # Create prompt
        prompt = create_task_generation_prompt(module_data)
        
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
        
        tasks_data = json.loads(response_text)
        
        # Store tasks in database
        created_tasks = []
        for task_data in tasks_data:
            data = {
                "module_id": module_id,
                "name": task_data.get("name"),
                "description": task_data.get("description"),
                "assignee": task_data.get("assignee", ""),
                "status": "todo",
                "priority": task_data.get("priority", "medium"),
                "difficulty": task_data.get("difficulty", 2),
                "time_estimate": task_data.get("time_estimate", 0),
                "quality_score": task_data.get("quality_score", 3),
                "autonomy": task_data.get("autonomy", 2),
                "generated_by_ai": True,
                "generation_metadata": {
                    "model": settings.CLAUDE_MODEL,
                    "prompt_version": "1.0"
                }
            }
            
            response = self.db.table(Task.table_name).insert(data).execute()
            created_tasks.append(Task.to_dict(response.data[0]))
        
        return created_tasks
