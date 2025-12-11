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
        
        # Call Claude API with maximum output tokens
        # Lower temperature (0.3) to enforce strict JSON formatting compliance
        message = self.claude.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=8192,  # Maximum for Claude Sonnet 3.5
            temperature=0.3,  # Low temp for strict rule-following
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Parse response
        response_text = message.content[0].text
        
        # Debug: Print the raw response
        print("=" * 80)
        print("Claude AI Task Generation Response:")
        print(f"Response length: {len(response_text)} chars")
        print(response_text[:1000])  # First 1000 chars
        print("=" * 80)
        
        # Extract JSON from response (handle markdown code blocks)
        original_text = response_text
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
            print("✓ Extracted JSON from ```json block")
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
            print("✓ Extracted JSON from ``` block")
        
        # Clean up response text - fix common JSON formatting issues
        response_text = response_text.strip()
        
        # CRITICAL FIX: Replace literal newlines in JSON strings with escaped \n
        # This handles Claude's inconsistent newline escaping
        # Strategy: Parse as lenient JSON-like text, fix strings, re-serialize
        try:
            # First attempt: Try parsing as-is (in case Claude got it right)
            tasks_data = json.loads(response_text)
            print(f"✅ Successfully parsed {len(tasks_data)} tasks from JSON (no fixes needed)")
        except json.JSONDecodeError as initial_error:
            print(f"⚠️ Initial parse failed: {initial_error}")
            print("🔧 Attempting to fix literal newlines in JSON strings...")
            
            # Fix strategy: Use regex to find strings with literal newlines and escape them
            # This is a heuristic but works for our structured format
            import re
            
            # Pattern: "description": "..." with potential literal newlines inside
            # Replace literal \n (newline char) with \\n (escaped string) in JSON string values
            def escape_newlines_in_json_strings(text):
                # Find all JSON string values (between quotes, not keys)
                # This regex finds: "key": "value with\npotential\nnewlines"
                def replace_in_match(match):
                    original = match.group(0)
                    # If this is a value (has : before it), escape newlines
                    if ':' in text[max(0, match.start()-20):match.start()]:
                        fixed = original.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                        return fixed
                    return original
                
                # Match quoted strings
                pattern = r'"[^"]*"'
                result = re.sub(pattern, replace_in_match, text, flags=re.DOTALL)
                return result
            
            fixed_text = escape_newlines_in_json_strings(response_text)
            
            # Count how many newlines were fixed
            original_literal = response_text.count('\n')
            fixed_literal = fixed_text.count('\n')
            print(f"   Fixed {original_literal - fixed_literal} literal newlines")
            
            # Try parsing the fixed version
            try:
                tasks_data = json.loads(fixed_text)
                print(f"✅ Successfully parsed {len(tasks_data)} tasks after auto-fix")
            except json.JSONDecodeError as e:
                # Still failed - give up and show detailed error
                print("❌ JSON Parse Error Details (even after auto-fix):")
                print(f"   Error: {e}")
                print(f"   Error position: line {e.lineno}, column {e.colno}")
                print(f"   Error character: {e.pos}")
                print("=" * 80)
                print("Problematic JSON (first 3000 chars):")
                print(fixed_text[:3000])
                print("=" * 80)
                print("Last 500 chars of JSON:")
                print(fixed_text[-500:])
                print("=" * 80)
                raise ValueError(f"Invalid JSON response from AI at line {e.lineno}, col {e.colno}: {str(e)}")
        
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
