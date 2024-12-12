from typing import Optional, Dict, Any
import time
import requests
from functools import wraps
from .exceptions import RequestError
from .config import SniperConfig

def retry_on_failure(max_attempts: int, backoff: float = 1.0):
    """Decorator for retrying failed requests."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except RequestError as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        time.sleep(backoff * (attempt + 1))
            raise last_error
        return wrapper
    return decorator

class RequestHandler:
    """Handles HTTP requests with retry logic and error handling."""
    
    def __init__(self, config: SniperConfig, session: requests.Session):
        self.config = config
        self.session = session
    
    @retry_on_failure(max_attempts=3)
    def make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """Make an HTTP request with retry logic."""
        try:
            url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                headers=headers,
                timeout=timeout or self.config.timeout,
                verify=self.config.verify_ssl,
                proxies=self.config.proxies,
                allow_redirects=True
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise RequestError(f"Request failed: {str(e)}")
    
    def record_request_pattern(
        self,
        pattern_name: str,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> None:
        """Record a request pattern for later replay."""
        self._patterns[pattern_name] = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "json": json,
            "data": data
        }
    
    def replay_request(self, pattern_name: str) -> Any:
        """Replay a recorded request pattern."""
        if pattern_name not in self._patterns:
            raise RequestError(f"No request pattern found with name: {pattern_name}")
            
        pattern = self._patterns[pattern_name]
        return self.make_request(
            method=pattern["method"],
            endpoint=pattern["url"],
            headers=pattern["headers"],
            params=pattern["params"],
            json=pattern["json"],
            data=pattern["data"]
        )
