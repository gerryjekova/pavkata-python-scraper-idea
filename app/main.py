from fastapi import FastAPI
from .services.queue_manager import QueueManager
from .models.task_response import TaskResponse
from typing import Dict

app = FastAPI()
queue_manager = QueueManager()

@app.get("/")
async def root():
    return {"status": "running", "message": "Web Scraper API"}

@app.post("/scrape")
async def scrape_url(url: str, headers: Dict[str, str] = None) -> TaskResponse:
    task_id = queue_manager.create_task(url, headers)
    return queue_manager.get_task_status(task_id)

@app.get("/task/{task_id}")
async def get_task(task_id: str) -> TaskResponse:
    return queue_manager.get_task_status(task_id)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}