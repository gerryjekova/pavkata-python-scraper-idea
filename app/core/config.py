from pydantic import BaseSettings

class Config(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    CRAWL4AI_API_KEY: str
    RULES_DIR: str = "configs/rules"
    
    # Task settings
    TASK_TIMEOUT: int = 3600  # 1 hour
    DEFAULT_TIMEOUT: int = 30  # 30 seconds
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 60  # 60 seconds
    
    class Config:
        env_file = ".env"

config = Config()