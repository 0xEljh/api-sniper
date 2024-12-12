from dataclasses import dataclass, field
from typing import Dict, Optional, List
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class SniperConfig:
    """Configuration for the API Sniper."""
    base_url: str
    timeout: int = 30
    retry_attempts: int = 3
    retry_backoff: float = 1.0
    headers: Dict[str, str] = field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    auth_endpoint: Optional[str] = None
    token_refresh_endpoint: Optional[str] = None
    proxies: Optional[Dict[str, str]] = None
    verify_ssl: bool = True
    max_redirects: int = 5
    user_agent_rotation: bool = False
    user_agents: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return self.to_dict()
