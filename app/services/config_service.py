from pathlib import Path
import json
import logging
from typing import Optional, Dict
from urllib.parse import urlparse
from ..models.domain_config import DomainConfig
from ..core.config import settings

logger = logging.getLogger(__name__)

class ConfigService:
    def __init__(self):
        self.config_dir = Path(settings.CONFIG_DIR)
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc
    
    def _get_config_path(self, domain: str) -> Path:
        """Get path for domain config file"""
        return self.config_dir / f"{domain}.json"
    
    async def get_config(self, url: str) -> Optional[DomainConfig]:
        """
        Get configuration for domain if it exists
        """
        try:
            domain = self._get_domain(url)
            config_path = self._get_config_path(domain)
            
            if config_path.exists():
                config_data = json.loads(config_path.read_text())
                return DomainConfig(**config_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading config for {url}: {str(e)}")
            return None
    
    async def save_config(self, url: str, config: DomainConfig):
        """
        Save configuration for domain
        """
        try:
            domain = self._get_domain(url)
            config_path = self._get_config_path(domain)
            
            # Save config
            config_path.write_text(json.dumps(config.dict(), indent=2))
            logger.info(f"Saved configuration for domain: {domain}")
            
        except Exception as e:
            logger.error(f"Error saving config for {url}: {str(e)}")
            raise
    
    async def list_domains(self) -> list:
        """
        List all domains with configurations
        """
        try:
            return [f.stem for f in self.config_dir.glob("*.json")]
        except Exception as e:
            logger.error(f"Error listing domains: {str(e)}")
            return []
    
    async def delete_config(self, domain: str) -> bool:
        """
        Delete configuration for domain
        """
        try:
            config_path = self._get_config_path(domain)
            if config_path.exists():
                config_path.unlink()
                logger.info(f"Deleted configuration for domain: {domain}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting config for {domain}: {str(e)}")
            return False