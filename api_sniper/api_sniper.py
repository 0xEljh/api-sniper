from typing import Optional, Dict, Any
import requests
from .config import SniperConfig
from .auth_manager import AuthManager
from .request_handler import RequestHandler
from .response_processor import ResponseProcessor
from .utils import rotate_user_agent

class APISniper:
    """Main class for making API requests that mimic browser behavior."""
    
    def __init__(self, config: SniperConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.headers)
        
        self.auth = AuthManager(config, self.session)
        self.request_handler = RequestHandler(config, self.session)
        self.response_processor = ResponseProcessor()
        
        if config.user_agent_rotation and config.user_agents:
            self._rotate_user_agent()
    
    def _rotate_user_agent(self) -> None:
        """Rotate the user agent if rotation is enabled."""
        if user_agent := rotate_user_agent(self.config.user_agents):
            self.session.headers["User-Agent"] = user_agent
    
    def login(self, username: str, password: str) -> None:
        """Authenticate with the API."""
        self.auth.login(username, password)
    
    def set_token(self, token: str, token_type: str = "Bearer") -> None:
        """Manually set an authentication token."""
        self.auth.set_token(token, token_type)
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Make a GET request."""
        response = self.request_handler.make_request(
            "GET", endpoint, params=params, headers=headers
        )
        return self.response_processor.process_response(response)
    
    def post(
        self,
        endpoint: str,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Make a POST request."""
        response = self.request_handler.make_request(
            "POST", endpoint, json=json, data=data, headers=headers
        )
        return self.response_processor.process_response(response)
    
    def put(
        self,
        endpoint: str,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Make a PUT request."""
        response = self.request_handler.make_request(
            "PUT", endpoint, json=json, data=data, headers=headers
        )
        return self.response_processor.process_response(response)
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Make a DELETE request."""
        response = self.request_handler.make_request(
            "DELETE", endpoint, params=params, headers=headers
        )
        return self.response_processor.process_response(response)
    
    def record_request_pattern(
        self,
        pattern_name: str,
        method: str,
        url: str,
        **kwargs
    ) -> None:
        """Record a request pattern for later replay."""
        self.request_handler.record_request_pattern(pattern_name, method, url, **kwargs)
    
    def replay_request(self, pattern_name: str) -> Any:
        """Replay a recorded request pattern."""
        response = self.request_handler.replay_request(pattern_name)
        return self.response_processor.process_response(response)
