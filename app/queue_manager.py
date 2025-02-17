from celery import Celery
from config import Config
import uuid
from .schema_generator import SchemaGenerator
from .scraper import Scraper

celery_app = Celery('scraper', broker=Config.REDIS_URL)

class TaskManager:
    def __init__(self):
        self.schema_generator = SchemaGenerator()
        self.scraper = Scraper()
        self.results = {}  # In-memory storage (replace with Redis in production)
    
    def create_task(self, url):
        """Create a new scraping task"""
        task_id = str(uuid.uuid4())
        self.process_task.delay(task_id, url)
        return task_id
    
    def get_result(self, task_id):
        """Get the result of a task"""
        return self.results.get(task_id)
    
    @celery_app.task(bind=True, max_retries=Config.MAX_RETRIES)
    def process_task(self, task_id, url):
        """Process a scraping task"""
        try:
            # Try to load existing schema
            schema = self.schema_generator.load_schema(url)
            
            if not schema:
                # Generate new schema if none exists
                schema = self.schema_generator.generate_schema(url)
            
            # Attempt to scrape with the schema
            result = self.scraper.scrape(url, schema)
            
            # Store the result
            self.results[task_id] = {
                'status': 'completed',
                'data': result
            }
            
        except Exception as e:
            # If scraping fails, try regenerating schema
            try:
                schema = self.schema_generator.generate_schema(url)
                result = self.scraper.scrape(url, schema)
                self.results[task_id] = {
                    'status': 'completed',
                    'data': result
                }
            except Exception as retry_e:
                self.results[task_id] = {
                    'status': 'failed',
                    'error': str(retry_e)
                }
                raise self.retry(countdown=Config.RETRY_DELAY)