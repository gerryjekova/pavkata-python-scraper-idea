from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Optional
import logging
from ..models.requests import ScrapeRequest
from ..models.responses import ScrapeResponse, TaskStatusResponse
from ..services.queue_service import QueueService
from ..services.validation import validate_url
from ..core.dependencies import get_queue_service

router = APIRouter(prefix="/scrape", tags=["scraping"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=ScrapeResponse, status_code=202)
async def create_scrape_task(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    queue_service: QueueService = Depends(get_queue_service)
):
    """
    Create a new scraping task
    
    Args:
        request: Scraping request parameters
        background_tasks: FastAPI background tasks
        queue_service: Queue service instance
    
    Returns:
        ScrapeResponse with task ID and initial status
    """
    try:
        # Validate URL format and accessibility
        await validate_url(request.url)
        
        # Create task
        task_id = await queue_service.create_task(
            url=str(request.url),
            headers=request.headers,
            options=request.options
        )
        
        # Add task to background processing
        background_tasks.add_task(
            queue_service.process_task,
            task_id=task_id
        )
        
        return ScrapeResponse(
            task_id=task_id,
            status="queued",
            message="Task created successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating scraping task: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create scraping task")

@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    queue_service: QueueService = Depends(get_queue_service)
):
    """
    Get the status and result of a scraping task
    
    Args:
        task_id: UUID of the task to check
        queue_service: Queue service instance
    
    Returns:
        TaskStatusResponse with current status and results if available
    """
    try:
        task = await queue_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch task status")