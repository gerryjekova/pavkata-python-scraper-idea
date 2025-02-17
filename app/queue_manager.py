from celery import Celery
from config import Config
from .models import TaskResponse, TaskStatus, ScrapedContent
from .schema_generator import SchemaGenerator
from .scraper import Scraper
from datetime import datetime
from typing import Optional, Dict, Any

celery_app = Celery('scraper', broker=Config.REDIS_URL)

class TaskManager:
    def __init__(self):
        self.schema_generator = SchemaGenerator()
        self.scraper = Scraper()
        self.tasks = {}  # In-memory storage (replace with Redis in production)
    
    def create_task(self, task_id: str, url: str, headers: Optional[Dict] = None, 
                   timeout: int = 30) -> None:
        """Create a new scraping task"""
        # Initialize task in storage
        self.tasks[task_id] = TaskResponse(
            task_id=task_id,
            status=TaskStatus.QUEUED,
            created_at=datetime.utcnow()
        )
        
        # Queue the task
        self.process_task.delay(task_id, url, headers, timeout)
    
    def get_result(self, task_id: str) -> Optional[TaskResponse]:
        """Get the result of a task"""
        return self.tasks.get(task_id)
    
    @celery_app.task(bind=True, max_retries=Config.MAX_RETRIES)
    def process_task(self, task_id: str, url: str, headers: Optional[Dict], 
                    timeout: int) -> None:
        """Process a scraping task"""
        try:
            # Update task status
            self.tasks[task_id].status = TaskStatus.PROCESSING
            
            # Try to load existing schema
            schema = self.schema_generator.load_schema(url)
            
            if not schema:
                schema = self.schema_generator.generate_schema(url)
            
            # Attempt to scrape with the schema
            result = self.scraper.scrape(url, schema, headers, timeout)
            
            # Update task with success result
            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.tasks[task_id].completed_at = datetime.utcnow()
            self.tasks[task_id].result = result
            
        except Exception as e:
            # If scraping fails, try regenerating schema
            try:
                schema = self.schema_generator.generate_schema(url)
                result = self.scraper.scrape(url, schema, headers, timeout)
                
                self.tasks[task_id].status = TaskStatus.COMPLETED
                self.tasks[task_id].completed_at = datetime.utcnow()
                self.tasks[task_id].result = result
                
            except Exception as retry_e:
                self.tasks[task_id].status = TaskStatus.FAILED
                self.tasks[task_id].error = str(retry_e)
                self.tasks[task_id].completed_at = datetime.utcnow()
                raise self.retry(countdown=Config.RETRY_DELAY)