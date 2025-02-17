from typing import AsyncGenerator
from fastapi import Depends
from .config import settings
from ..services.queue_service import QueueService
from ..services.scraper_service import ScraperService
from ..services.config_service import ConfigService
from ..services.storage_service import StorageService

async def get_storage_service() -> AsyncGenerator[StorageService, None]:
    service = StorageService(settings.STORAGE_TYPE, settings.REDIS_URL)
    try:
        yield service
    finally:
        await service.close()

async def get_config_service(
    storage: StorageService = Depends(get_storage_service)
) -> ConfigService:
    return ConfigService()

async def get_scraper_service(
    config: ConfigService = Depends(get_config_service)
) -> ScraperService:
    return ScraperService(config)

async def get_queue_service(
    storage: StorageService = Depends(get_storage_service),
    scraper: ScraperService = Depends(get_scraper_service)
) -> QueueService:
    return QueueService(storage, scraper)