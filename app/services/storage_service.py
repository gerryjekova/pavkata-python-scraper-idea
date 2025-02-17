from typing import Optional, Dict, Any
import json
import aioredis
import logging
from datetime import datetime, timedelta
from pathlib import Path
from ..models.task import TaskInfo, TaskStatus
from ..core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, storage_type: str = "memory", redis_url: Optional[str] = None):
        self.storage_type = storage_type
        self.redis_url = redis_url
        self.memory_storage: Dict[str, Dict] = {}
        self.redis = None
        
        if storage_type == "redis" and redis_url:
            self.redis = aioredis.from_url(redis_url)
    
    async def close(self):
        """Close connections"""
        if self.redis:
            await self.redis.close()
    
    async def save_task(self, task_id: str, task: TaskInfo):
        """Save task information"""
        try:
            if self.storage_type == "redis" and self.redis:
                await self.redis.hset(
                    f"task:{task_id}",
                    mapping=self._serialize_task(task)
                )
            else:
                self.memory_storage[task_id] = task.dict()
                
        except Exception as e:
            logger.error(f"Error saving task {task_id}: {str(e)}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get task information"""
        try:
            if self.storage_type == "redis" and self.redis:
                data = await self.redis.hgetall(f"task:{task_id}")
                if not data:
                    return None
                return self._deserialize_task(data)
            else:
                data = self.memory_storage.get(task_id)
                if not data:
                    return None
                return TaskInfo(**data)
                
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {str(e)}")
            return None
    
    async def cleanup_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            if self.storage_type == "redis" and self.redis:
                # Get all task keys
                keys = await self.redis.keys("task:*")
                for key in keys:
                    task_data = await self.redis.hgetall(key)
                    if task_data:
                        task = self._deserialize_task(task_data)
                        if self._should_cleanup_task(task, cutoff_time):
                            await self.redis.delete(key)
            else:
                # Cleanup memory storage
                self.memory_storage = {
                    task_id: task_data
                    for task_id, task_data in self.memory_storage.items()
                    if not self._should_cleanup_task(TaskInfo(**task_data), cutoff_time)
                }
                
        except Exception as e:
            logger.error(f"Error cleaning up tasks: {str(e)}")
    
    def _should_cleanup_task(self, task: TaskInfo, cutoff_time: datetime) -> bool:
        """Check if task should be cleaned up"""
        if not task.completed_at:
            return False
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return task.completed_at < cutoff_time
        
        return False
    
    def _serialize_task(self, task: TaskInfo) -> Dict[str, str]:
        """Serialize task for Redis storage"""
        task_dict = task.dict()
        return {
            key: json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            for key, value in task_dict.items()
        }
    
    def _deserialize_task(self, data: Dict[bytes, bytes]) -> TaskInfo:
        """Deserialize task from Redis storage"""
        decoded_data = {}
        for key, value in data.items():
            key = key.decode('utf-8')
            value = value.decode('utf-8')
            
            try:
                decoded_data[key] = json.loads(value)
            except json.JSONDecodeError:
                decoded_data[key] = value
        
        return TaskInfo(**decoded_data)