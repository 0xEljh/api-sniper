class SniperError(Exception):
    """Base exception for all API Sniper errors."""
    pass

class AuthError(SniperError):
    """Raised when authentication fails."""
    pass

class RequestError(SniperError):
    """Raised when a request fails."""
    pass

class ResponseParseError(SniperError):
    """Raised when response parsing fails."""
    pass

class ConfigError(SniperError):
    """Raised when configuration is invalid."""
    pass
