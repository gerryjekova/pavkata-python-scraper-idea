import os
import json
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional, Dict
import logging
from crawl4ai import Crawler
from ..models.domain_config import DomainConfig, SelectorRules

logger = logging.getLogger(__name__)

class SchemaGenerator:
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        self.crawler = Crawler()
        os.makedirs(config_dir, exist_ok=True)
    
    def _get_domain_path(self, url: str) -> str:
        """Get the path for domain-specific configuration file"""
        domain = urlparse(url).netloc
        return os.path.join(self.config_dir, f"{domain}.json")
    
    async def generate_schema(self, url: str) -> DomainConfig:
        """Generate extraction schema using Crawl4AI's LLM capabilities"""
        try:
            domain = urlparse(url).netloc
            logger.info(f"Generating schema for domain: {domain}")
            
            # Use Crawl4AI to analyze the webpage and generate schema
            schema_data = await self.crawler.analyze_page(
                url=url,
                elements=[
                    "title",
                    "content",
                    "author",
                    "publish_date",
                    "language",
                    "categories",
                    "media"
                ]
            )
            
            # Create selector rules from schema
            selectors = SelectorRules(
                title=schema_data["selectors"]["title"],
                content=schema_data["selectors"]["content"],
                author=schema_data["selectors"].get("author"),
                publish_date=schema_data["selectors"].get("publish_date"),
                language=schema_data["selectors"].get("language"),
                categories=schema_data["selectors"].get("categories"),
                media={
                    "images": schema_data["selectors"].get("images", ""),
                    "videos": schema_data["selectors"].get("videos", ""),
                    "embeds": schema_data["selectors"].get("embeds", "")
                }
            )
            
            # Create domain configuration
            config = DomainConfig(
                domain=domain,
                selectors=selectors,
                use_headless=schema_data.get("requires_javascript", False),
                timeout=30
            )
            
            # Save the configuration
            self.save_config(config)
            
            return config
            
        except Exception as e:
            logger.error(f"Schema generation failed for {url}: {str(e)}")
            raise
    
    def save_config(self, config: DomainConfig) -> None:
        """Save domain configuration to file"""
        try:
            file_path = self._get_domain_path(f"https://{config.domain}")
            with open(file_path, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            logger.info(f"Saved configuration for domain: {config.domain}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            raise
    
    def load_config(self, url: str) -> Optional[DomainConfig]:
        """Load existing configuration for domain"""
        try:
            file_path = self._get_domain_path(url)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                return DomainConfig.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return None