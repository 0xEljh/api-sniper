from typing import Any, Dict, Optional
import json
from requests import Response
from .exceptions import ResponseParseError

class ResponseProcessor:
    """Processes and validates HTTP responses."""
    
    @staticmethod
    def process_response(response: Response) -> Any:
        """Process response and return parsed data."""
        try:
            content_type = response.headers.get("content-type", "")
            
            if "application/json" in content_type:
                return response.json()
            elif "text/" in content_type:
                return response.text
            else:
                return response.content
        except json.JSONDecodeError as e:
            raise ResponseParseError(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            raise ResponseParseError(f"Failed to process response: {str(e)}")
    
    @staticmethod
    def validate_response(
        response: Response,
        expected_status: Optional[int] = None,
        required_fields: Optional[list] = None
    ) -> None:
        """Validate response status and content."""
        if expected_status and response.status_code != expected_status:
            raise ResponseParseError(
                f"Unexpected status code: {response.status_code}, expected: {expected_status}"
            )
            
        if required_fields:
            try:
                data = response.json()
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    raise ResponseParseError(
                        f"Response missing required fields: {', '.join(missing_fields)}"
                    )
            except json.JSONDecodeError:
                raise ResponseParseError("Response is not valid JSON")
