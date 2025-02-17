import logging
from celery import Celery
from config import Config
from .models.task_response import TaskResponse, TaskStatus
from .scrapers.schema_generator import SchemaGenerator
from .scrapers.content_scraper import ContentScraper
from datetime import datetime
from crawl4ai import Crawler

logger = logging.getLogger(__name__)

celery_app = Celery('scraper', broker=Config.REDIS_URL)

class TaskManager:
    def __init__(self):
        self.crawler = Crawler(api_key=Config.CRAWL4AI_API_KEY)
        self.schema_generator = SchemaGenerator(Config.RULES_DIR, self.crawler)
        self.content_scraper = ContentScraper()
        self.tasks = {}
    
    @celery_app.task(bind=True, max_retries=3)
    def process_task(self, task_id: str, url: str, headers: dict = None, 
                    timeout: int = 30) -> None:
        """Process a scraping task with retries and failsafe mechanisms"""
        try:
            # Update task status
            self._update_task_status(task_id, TaskStatus.PROCESSING)
            
            # Get or generate config
            config = self.schema_generator.load_config(url)
            if not config:
                config = await self.schema_generator.generate_config(url)
            
            # Update config with request-specific settings
            if headers:
                config.user_agent = headers.get('User-Agent', config.user_agent)
            config.timeout = timeout
            
            # Attempt scraping
            try:
                result = self.content_scraper.scrape(url, config)
                self._update_task_success(task_id, result)
                
            except Exception as scrape_error:
                logger.error(f"Initial scraping failed: {str(scrape_error)}")
                
                # Regenerate config and retry
                config = await self.schema_generator.generate_config(url)
                result = self.content_scraper.scrape(url, config)
                self._update_task_success(task_id, result)
                
        except Exception as e:
            logger.error(f"Task processing failed: {str(e)}")
            self._update_task_failure(task_id, str(e))
            raise self.retry(countdown=60)
    
    def _update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Update task status"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
    
    def _update_task_success(self, task_id: str, result: dict) -> None:
        """Update task with successful result"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.tasks[task_id].completed_at = datetime.utcnow()
            self.tasks[task_id].result = result
    
    def _update_task_failure(self, task_id: str, error: str) -> None:
        """Update task with failure information"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.FAILED
            self.tasks[task_id].completed_at = datetime.utcnow()
            self.tasks[task_id].error = error