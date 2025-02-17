from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from .task import TaskStatus

class ScrapeResponse(BaseModel):
    task_id: str
    status: str = "queued"
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ScrapingResult(BaseModel):
    title: str
    content: str
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    language: Optional[str] = None
    categories: list = Field(default_factory=list)
    media_files: Dict[str, list] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    url: str
    result: Optional[ScrapingResult] = None
    error: Optional[str] = None
    retry_count: int = 0
    schema_regenerated: bool = False