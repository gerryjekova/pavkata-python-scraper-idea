from dataclasses import dataclass
from typing import Dict, Optional, List, Any
from datetime import datetime

@dataclass
class SelectorRules:
    title: str  # XPath or CSS selector
    content: str
    author: Optional[str]
    publish_date: Optional[str]
    language: Optional[str]
    categories: Optional[str]
    media: Dict[str, str]  # Selectors for images, videos, embeds

@dataclass
class DomainConfig:
    domain: str
    selectors: SelectorRules
    use_headless: bool = False
    use_proxy: bool = False
    timeout: int = 30
    user_agent: Optional[str] = None
    proxy_config: Optional[Dict[str, Any]] = None
    last_updated: datetime = datetime.utcnow()
    success_rate: float = 1.0  # Track success rate for monitoring

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "selectors": {
                "title": self.selectors.title,
                "content": self.selectors.content,
                "author": self.selectors.author,
                "publish_date": self.selectors.publish_date,
                "language": self.selectors.language,
                "categories": self.selectors.categories,
                "media": self.selectors.media
            },
            "use_headless": self.use_headless,
            "use_proxy": self.use_proxy,
            "timeout": self.timeout,
            "user_agent": self.user_agent,
            "proxy_config": self.proxy_config,
            "last_updated": self.last_updated.isoformat(),
            "success_rate": self.success_rate
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DomainConfig':
        selectors = SelectorRules(**data["selectors"])
        return cls(
            domain=data["domain"],
            selectors=selectors,
            use_headless=data.get("use_headless", False),
            use_proxy=data.get("use_proxy", False),
            timeout=data.get("timeout", 30),
            user_agent=data.get("user_agent"),
            proxy_config=data.get("proxy_config"),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            success_rate=data.get("success_rate", 1.0)
        )