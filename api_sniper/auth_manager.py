from typing import Optional, Dict
import requests
from .exceptions import AuthError
from .config import SniperConfig

class AuthManager:
    """Manages authentication state and credentials."""
    
    def __init__(self, config: SniperConfig, session: requests.Session):
        self.config = config
        self.session = session
        self._token: Optional[str] = None
        self._token_type: Optional[str] = None
    
    def login(self, username: str, password: str) -> None:
        """Authenticate with username and password."""
        if not self.config.auth_endpoint:
            raise AuthError("No auth endpoint configured")
            
        try:
            response = self.session.post(
                f"{self.config.base_url}{self.config.auth_endpoint}",
                json={"username": username, "password": password},
                timeout=self.config.timeout
            )
            response.raise_for_status()
            auth_data = response.json()
            
            # Handle common token response formats
            self._token = auth_data.get("access_token") or auth_data.get("token")
            self._token_type = auth_data.get("token_type", "Bearer")
            
            if self._token:
                self.session.headers["Authorization"] = f"{self._token_type} {self._token}"
        except Exception as e:
            raise AuthError(f"Login failed: {str(e)}")
    
    def set_token(self, token: str, token_type: str = "Bearer") -> None:
        """Manually set an authentication token."""
        self._token = token
        self._token_type = token_type
        self.session.headers["Authorization"] = f"{token_type} {token}"
    
    def clear_auth(self) -> None:
        """Clear authentication state."""
        self._token = None
        self._token_type = None
        self.session.headers.pop("Authorization", None)
    
    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return bool(self._token)
