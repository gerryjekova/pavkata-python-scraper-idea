import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from celery import Celery
from redis import Redis
import json

from ..models.task_status import TaskStatus
from ..scrapers.content_scraper import ContentScraper
from ..scrapers.schema_generator import SchemaGenerator

logger = logging.getLogger(__name__)

class TaskManager:
    """Manages scraping tasks with Redis-backed persistence"""
    
    def __init__(self, redis_url: str, crawler_client=None):
        self.redis = Redis.from_url(redis_url)
        self.celery = Celery('scraper', broker=redis_url)
        self.scraper = ContentScraper()
        self.schema_generator = SchemaGenerator(crawler_client)
        
        # Configure Celery
        self.configure_celery()
    
    def configure_celery(self):
        """Configure Celery settings"""
        self.celery.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            task_track_started=True,
            task_time_limit=3600,  # 1 hour max
            task_soft_time_limit=1800,  # 30 minutes soft limit
            worker_max_tasks_per_child=200,
            worker_prefetch_multiplier=1  # One task at a time
        )
    
    def create_task(self, url: str, headers: Optional[Dict] = None) -> str:
        """
        Create a new scraping task and return its UUID
        """
        task_id = str(uuid.uuid4())
        
        # Store initial task data
        task_data = {
            'task_id': task_id,
            'url': url,
            'headers': headers,
            'status': TaskStatus.QUEUED.value,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'attempt': 0,
            'max_attempts': 3
        }
        
        # Save task data to Redis
        self.redis.hset(
            f'task:{task_id}',
            mapping=self._serialize_task_data(task_data)
        )
        
        # Queue the task
        self._process_task.delay(task_id)
        
        logger.info(f"Created task {task_id} for URL: {url}")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        Get task status and result
        """
        task_data = self.redis.hgetall(f'task:{task_id}')
        
        if not task_data:
            return None
        
        return self._deserialize_task_data(task_data)
    
    @staticmethod
    def _serialize_task_data(data: Dict) -> Dict[str, str]:
        """Serialize task data for Redis storage"""
        serialized = {}
        for key, value in data.items():
            if isinstance(value, dict):
                serialized[key] = json.dumps(value)
            else:
                serialized[key] = str(value)
        return serialized
    
    @staticmethod
    def _deserialize_task_data(data: Dict[bytes, bytes]) -> Dict[str, Any]:
        """Deserialize task data from Redis storage"""
        deserialized = {}
        for key, value in data.items():
            key = key.decode('utf-8')
            value = value.decode('utf-8')
            
            try:
                # Try to parse JSON fields
                deserialized[key] = json.loads(value)
            except json.JSONDecodeError:
                deserialized[key] = value
        
        return deserialized
    
    @celery.task(bind=True, max_retries=3)
    def _process_task(self, task_id: str):
        """
        Process a scraping task with retry capability
        """
        try:
            # Get task data
            task_data = self.get_task(task_id)
            if not task_data:
                logger.error(f"Task {task_id} not found")
                return
            
            # Update status to processing
            self._update_task_status(task_id, TaskStatus.PROCESSING)
            
            # Get or generate schema
            url = task_data['url']
            schema = self.schema_generator.load_config(url)
            if not schema:
                schema = self.schema_generator.generate_config(url)
            
            # Attempt scraping
            headers = task_data.get('headers')
            result = self.scraper.scrape(url, schema, headers)
            
            # Update task with success
            self._update_task_success(task_id, result)
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            
            # Get current attempt count
            task_data = self.get_task(task_id)
            attempt = int(task_data['attempt'])
            max_attempts = int(task_data['max_attempts'])
            
            if attempt < max_attempts:
                # Update attempt count and retry
                self._update_task_retry(task_id, attempt + 1)
                raise self._process_task.retry(
                    exc=e,
                    countdown=60 * (2 ** attempt)  # Exponential backoff
                )
            else:
                # Mark as failed
                self._update_task_failure(task_id, str(e))
    
    def _update_task_status(self, task_id: str, status: TaskStatus):
        """Update task status"""
        self.redis.hset(f'task:{task_id}', 'status', status.value)
        self.redis.hset(f'task:{task_id}', 'updated_at', datetime.utcnow().isoformat())
    
    def _update_task_retry(self, task_id: str, attempt: int):
        """Update task for retry"""
        self.redis.hmset(f'task:{task_id}', {
            'status': TaskStatus.QUEUED.value,
            'attempt': str(attempt),
            'updated_at': datetime.utcnow().isoformat()
        })
    
    def _update_task_success(self, task_id: str, result: Dict):
        """Update task with successful result"""
        self.redis.hmset(f'task:{task_id}', {
            'status': TaskStatus.COMPLETED.value,
            'result': json.dumps(result),
            'completed_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        })
    
    def _update_task_failure(self, task_id: str, error: str):
        """Update task with failure information"""
        self.redis.hmset(f'task:{task_id}', {
            'status': TaskStatus.FAILED.value,
            'error': error,
            'completed_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        })